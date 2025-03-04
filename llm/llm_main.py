import re
import json

from config.log import get_logger
from config.config import Config
from config.common import TRANSLATION_DICT
from db.db import get_data, query_data
from llm.llm import LLM


logger = get_logger()


def sys_prompt(context, question):
    return f"""You are a helpful AI assistant. Use the following pieces of
      context to answer the question at the end. If you don't know the answer, 
      just say you don't know. DO NOT try to make up an answer. If the question 
      is not related to the context, politely respond that you are tuned to only 
      answer questions that are related to the context.  {context}  
      Question: {question} Helpful answer:"""


def personal_context(product_list, rule_list=None):
    return f"""我有一批贷款产品列表，贷款产品信息如下json格式：{product_list}，
      后面所有需要推荐贷款产品的问题都是基于这批产品的。已经总结出了
      部分推荐规则，规则如下：{rule_list}."""


def personal_question(company_info, product_num=3):
    return f"""请根据企业信息和推荐规则，帮下述企业从我提供的json格式贷款产品中推荐最合适的
      {product_num}款贷款产品的产品编号，并给出每款产品的推荐理由和金融风控注意事项，
      回答中必须包含每款推荐产品的产品编号，推荐理由，金融风控注意事项3部分信息。
      企业信息json格式如下：{company_info}."""


def whole_prompt(product_list, rule_list, company_json, product_num=3):
    return f"""请帮我根据这家企业的信息：{company_json}，参考如下规则：
    {rule_list}，为这家企业从下面的{len(product_list)}款贷款产品列表：
    {product_list}中推荐最匹配的{product_num}款产品。回答中必须包含
    每款推荐产品的产品名称，推荐理由，金融风控注意事项3部分信息，
    以json格式回答。"""


def is_chinese_company_name_strict(input_str):
    # 正则表达式：匹配中文字符、英文字符、数字和特定符号
    pattern = re.compile(r'^[\u4e00-\u9fa5a-zA-Z0-9()（）·\-]{2,50}$')
    if not pattern.match(input_str):
        return False
    
    # 检查是否包含中文字符
    if not re.search(r'[\u4e00-\u9fa5]', input_str):
        return False
    
    # 检查英文字符和数字的比例
    non_chinese_count = len(re.findall(r'[a-zA-Z0-9]', input_str))
    total_length = len(input_str)
    if non_chinese_count / total_length > 0.5:  # 非中文字符比例超过 50%
        return False
    
    return True


def is_unified_social_credit_code(input_str):
    # 正则表达式：匹配 18 位的数字和大写字母
    pattern = re.compile(r'^[A-Z0-9]{18}$')
    return bool(pattern.match(input_str))


def chat_response(query):

    config_obj = Config()
    company_json = config_obj.match_company(query)
    if company_json is None:
        if is_chinese_company_name_strict(query):
            # 根据企业名称进行推荐
            company_json = {"统一社会信用代码": query, "企业名称": query}
        elif is_unified_social_credit_code(query):
            # 仅有统一社会信用代码，直接返回None
            company_json = {"统一社会信用代码": query}
            return company_json['统一社会信用代码'], None
        else:
            # 企业信息不存在，直接返回None
            return None, None

    if query_data(f"key is '{company_json['统一社会信用代码']}'") != {}:
        data = get_data(company_json['统一社会信用代码'])
    else:
        product_list = config_obj.product_config(match=False)
        rule_list = config_obj.rule_config()
        # context = personal_context(product_list, rule_list)
        # question = personal_question(company_json)
        # personal_prompt = sys_prompt(context, question)

        personal_prompt = whole_prompt(product_list, rule_list, 
                                       company_json, config_obj.config['PRODUCT_NUM'])
        logger.info(f'prompt: {personal_prompt}.')

        llm_chat = LLM(config_obj.config['BASE_URL'])
        result = llm_chat.chat(personal_prompt, config_obj.config['LLM_MODEL'])
        data = json.loads(result)['response']

    logger.info(f"response: {data['content']}.")
    return company_json['统一社会信用代码'], data


def parsed_chat(chat_result):
    # 提取 content 信息
    content = chat_result['content']

    # 分割 <think> 内容和回答部分
    think_content = content.split('</think>')[0].replace('<think>', '').strip()
    response_content = content.split('</think>')[1].strip()

    # 去掉多余的标记（```json 和 ```）
    json_content = response_content.strip('```json\n').strip('```').strip()

    # 解析为 Python 对象（列表）
    parsed_data = json.loads(json_content)

    return think_content, response_content, parsed_data


def format_product(product_name):

    config_obj = Config()

    product_info = config_obj.match_product(product_name)
    if product_info is not None:
        return {
            '产品名称': f'''{product_info['银行名称']} {product_info['产品名称']} ''' + \
            f'''{product_info['担保方式']}\n{product_info['显示额度']}万 ''' + \
            f'''{product_info['显示周期']}月 {product_info['显示利率']}%'''
            }
    else:
        return {'产品名称': product_name + '（未找到匹配产品信息）'}


def format_response(chat_result):

    think_content, response_content, parsed_data = parsed_chat(chat_result)

    # 提取回答中的几款产品信息
    products = []
    for product in parsed_data:
        # print(product)
        products.append(format_product(product[list(product.keys())[0]]))
        products[-1]['推荐理由'] = product[list(product.keys())[1]]
        products[-1]['金融风控注意事项'] = product[list(product.keys())[2]]

    # 将提取的信息存储为 JSON 格式
    output_json = {
        'think_content': think_content,
        'response_content': response_content,
        'recommended_products': products
    }

    # 打印或保存 JSON 结果
    # print(json.dumps(output_json, ensure_ascii=False, indent=4))
    return output_json


def format_query_product(product_name):

    config_obj = Config()

    product_info = config_obj.match_product(product_name)
    if product_info is not None:
        return product_info
    else:
        return {'产品名称': product_name + '（未找到匹配产品信息）'}


def format_query_response(chat_result):

    think_content, response_content, parsed_data = parsed_chat(chat_result)

    # 提取回答中的几款产品信息
    products = []
    for product in parsed_data:
        # print(product)
        products.append(format_query_product(product[list(product.keys())[0]]))
        products[-1]['推荐理由'] = product[list(product.keys())[1]]
        products[-1]['金融风控注意事项'] = product[list(product.keys())[2]]

    # 将中文key转为英文key
    products_eng = []
    for product in products:
        product_eng = {TRANSLATION_DICT[k]: v for k, v in product.items()}
        products_eng.append(product_eng)

    # 将提取的信息存储为 JSON 格式
    output_json = {
        'think_content': think_content,
        'response_content': response_content,
        'recommended_products': products_eng
    }

    return output_json


# 使用示例
if __name__ == "__main__":
    company_id, chat_result = chat_response(query="xx公司")
    output_json = format_response(chat_result)
    print(output_json['recommended_products'])

    output_json = format_query_response(chat_result)
    print(output_json['recommended_products'])
