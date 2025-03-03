import re
import json

from config.log import get_logger
from config.config import Config
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


def chat_response(query):

    config_obj = Config()
    company_json = config_obj.match_company(query)
    if company_json is None:
        return None, None

    if query_data(f"key is '{company_json['统一社会信用代码']}'") != {}:
        data = get_data(company_json['统一社会信用代码'])
    else:
        product_list = config_obj.product_config(match=False)
        rule_list = config_obj.rule_config()
        # context = personal_context(product_list, rule_list)
        # question = personal_question(company_json)
        # personal_prompt = sys_prompt(context, question)

        personal_prompt = whole_prompt(product_list, rule_list, company_json)
        logger.info(f'prompt: {personal_prompt}.')

        llm_chat = LLM(config_obj.config['BASE_URL'])
        result = llm_chat.chat(prompt=personal_prompt, model=config_obj.config['LLM_MODEL'])
        data = json.loads(result)['response']

    logger.info(f"response: {data['content']}.")
    # # 用于演示的示例数据
    # data = {'role': 'assistant', 
    #         'content': '<think>\n好，我现在需要帮用户推荐两笔贷款产品给xx公司。首先，我得看看公司的基本信息：成立时间是2019年，注册资本1000万，经营范围是软件开发，行业分类是信息技术，公司规模在100到500人之间，法人张三是企业家，背景是大学毕业生。\n\n接下来，我要分析每个贷款产品的条件和用途是否符合公司的需求。首先看“企业经营贷款”产品，它的担保方式是抵押，用途也是企业经营，适用条件是企业有稳定经营和还款能力，这些都符合xx公司的情况。参考利率5.9%看起来比较合理，但要注意金融风控政策。根据之前的回答，金融风控可能会影响利率，建议用户先咨询当地银行或政府，了解最新的利率调整情况。\n\n然后是“企业创新贷款”，担保方式也是抵押，用途同样是企业创新，条件同样符合公司的稳定经营和创新能力需求。参考利率3.9%~5%，也在合理范围内。但同样，金融风控方面，可能需要提前查看具体的政策，是否影响利率或申请流程。\n\n再看“企业扩张贷款”，担保是保证，用途也是企业扩张，适用条件符合公司的稳定性。参考利率5.9%，看起来有点高，但可能因为业务规模扩大而更高。注意事项里提到企业需提供真实有效的企业信息，这可能意味着需要核实相关资料，或者担心数据安全。\n\n最后是“企业经营贷款”，但这个产品好像有问题，它的担保方式是保证，用途也是企业经营，但参考利率只有3.56%。这比其他产品低很多，可能更适合资金有限的企业，但如果xx公司有充足的资金需求，可能不适用。不过，结合公司规模和注册资本100万，可能适合。\n\n综合考虑，推荐“企业创新贷款”和“企业扩张贷款”。因为这两个产品都有抵押担保，并且适用于企业的经营或创新需求，特别是对于初创公司的来说，创新贷款可能更合适。另外，“企业扩张贷款”的利率有点高，但如果公司规模扩大了，这个产品可能是更适合的选择。\n</think>\n\n根据你的查询和提供的贷款产品列表，结合你公司的信息：“xx公司”，我会推荐以下两笔适合的贷款产品：\n\n### 1. **企业创新贷款**\n   - **推荐理由**：该贷款产品的担保方式为抵押，并且用途是“企业创新”。这符合公司所从事的“软件开发”业务，特别是如果公司正在开拓新的业务领域或进行技术创新，则可能更适合。另外，贷款期限和参考利率也适合企业的成长需求。\n   - **金融风控注意事项**：建议在收到贷款申请后，提前咨询当地金融机构关于金融风控政策的具体信息，以了解可能的利率调整或申请限制情况。\n\n### 2. **企业扩张贷款**\n   - **推荐理由**：该贷款产品的担保方式为保证，并且用途是“企业扩张”。这适合公司规模较大的情况（100-500人），特别是如果公司需要扩大业务规模，以增加利润和提高现金流。另外，贷款期限和参考利率也较为合理。\n   - **金融风控注意事项**：建议在收到贷款申请后，提前查看当地金融局或银行关于“企业扩张”业务的最新政策信息，了解是否有额外的限制或调整。\n\n### 注意事项：\n- 请确保在推荐产品时关注公司的具体情况和市场环境，必要时应进行实地考察。\n- 如果你所在地区的金融政策有特别的规定，请务必及时了解，并在申请过程中做好充分准备。'}

    return company_json['统一社会信用代码'], data


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

    # 提取 content 信息
    content = chat_result['content']

    # 分割 <think> 内容和回答部分
    think_content = content.split('</think>')[0].replace('<think>', '').strip()
    response_content = content.split('</think>')[1].strip()

    # 去掉多余的标记（```json 和 ```）
    json_content = response_content.strip('```json\n').strip('```').strip()

    # 解析为 Python 对象（列表）
    parsed_data = json.loads(json_content)

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


# 使用示例
if __name__ == "__main__":
    company_id, chat_result = chat_response(query="xx公司")
    output_json = format_response(chat_result)
    print(output_json['recommended_products'])
