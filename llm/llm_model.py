import json
import pandas as pd

from config.log import get_logger
from config.config import Config
from db.db_orm import read_table_to_dataframe, update_table_from_dataframe
from db.db_orm import get_table_structure
from db.db import get_data, query_data, save_data
from llm.llm import LLM


logger = get_logger()
config_obj = Config()


def get_table_prompt():

    table_list = ['company_basic_info', 'company_bidding_info', 
                  'company_financial_data', 'company_tax_info', 
                  'company_electricity_usage', 'merchant_transaction']
    
    # 初始化表结构的提示信息
    prompt = (f"你是一个专业的金融风险建模师，负责为企业构建风险评估模型，"
                "请根据我提供的数据回答问题。遵循以下规则：\n"
                "1. 先读取6个表的字段和描述信息\n"
                "2. 设计一个模型，将每个表的字段信息视为1个维度，计算该维度的评分（评分范围为0~100）\n"
                "3. 将6个表的评分进行加权求和，权重依据表的内容确定，计算出加权后的综合评分（范围为0~100）\n"
                "4. 在回答中给出每个表对应的评分模型，和综合评分模型\n\n")

    for table_name in table_list:
        # 获取表结构
        table_structure = get_table_structure(table_name)
        prompt += f"{table_structure}\n"
        
    # print(prompt)
    # 打印或保存提示信息
    logger.info(prompt)

    return prompt


def chat_model_response():
    '''
    企业风险评估模型设计
    基于提供的6个表，我将为每个表设计评分模型，然后构建综合评分模型。

    1. 各表评分模型
    1.1 企业基本信息表(company_basic_info)评分模型
    权重：20%

    评分维度：
    企业状态(30%)：正常运营=100，注销/吊销=0
    成立年限(20%)：5年以上=100，3-5年=80，1-3年=60，1年以下=40
    注册资本(15%)：按规模分级评分
    员工人数(10%)：按规模分级评分
    融资情况(10%)：融资轮次和金额综合评分
    股东结构(10%)：股东数量和控制人稳定性评分
    行业风险(5%)：行业分类风险评级

    1.2 企业中标信息表(company_bidding_info)评分模型
    权重：15%

    评分维度：

    中标金额(40%)：按金额分级评分
    中标频率(30%)：中标次数分级评分
    负面信息(20%)：无负面=100，有负面=0
    政采贷情况(10%)：政采贷金额和次数综合评分

    1.3 企业财务信息表(company_financial_data)评分模型
    权重：25%

    评分维度：
    盈利能力(30%)：净利润率评分
    偿债能力(25%)：资产负债率评分
    运营效率(20%)：营业成本占比评分
    税收缴纳(15%)：纳税总额评分
    社保缴纳(10%)：社保参保人数评分

    1.4 企业税务信息表(company_tax_info)评分模型
    权重：20%

    评分维度：
    纳税信用等级(40%)：A=100，B=80，C=60，D=0
    欠税情况(30%)：欠税金额和期数评分
    税收增长率(20%)：本年累计同比评分
    申报及时性(10%)：申报期限遵守情况评分

    1.5 企业电力使用信息表(company_electricity_usage)评分模型
    权重：10%

    评分维度：

    用电趋势(40%)：上升=100，平稳=80，下降=60
    用电规模(30%)：电容量和电量等级评分
    欠费情况(20%)：欠费期数评分
    违章用电(10%)：无违章=100，有违章=0

    1.6 商户流水信息表(merchant_transaction)评分模型
    权重：10%

    评分维度：

    交易金额(60%)：近90天和365天金额评分
    交易用户数(40%)：近90天和365天用户数评分

    2. 综合评分模型
    综合评分 =
    (company_basic_info评分 × 20%) +
    (company_bidding_info评分 × 15%) +
    (company_financial_data评分 × 25%) +
    (company_tax_info评分 × 20%) +
    (company_electricity_usage评分 × 10%) +
    (merchant_transaction评分 × 10%)

    3. 风险等级划分
    90-100分：极低风险
    80-89分：低风险
    70-79分：中等风险
    60-69分：较高风险
    0-59分：高风险

    这个模型综合考虑了企业的基础信息、经营能力、财务健康度、税务合规性、用电情况和交易活跃度等多个维度，能够较全面地评估企业风险状况。各表权重可根据具体行业特点进行调整。
    '''
    model_prompt = get_table_prompt()
    llm_chat = LLM(config_obj.config['BASE_URL'])
    result = llm_chat.chat(model_prompt, config_obj.config['LLM_MODEL'])
    data = json.loads(result)['response']
    logger.info(f"response: {data['content']}.")
    return data


def modeling():
    """模型设计"""
    # 这里可以添加模型设计的逻辑
    model_result = ...
    logger.info(f"模型设计结果: {model_result}")
    return model_result


def update_credit_limit():
    """更新商户信用额度"""
    table_name = 'merchant_credit_limit'
    df = read_table_to_dataframe(table_name)
    
    if df is not None:
        # 示例：将所有等级为'CCC'的额度降低10%
        mask = df['credit_level'] == 'CCC'
        df.loc[mask, 'recommended_limit'] = (df.loc[mask, 'recommended_limit'] * 0.9).astype('int')
        
        # 将更新记录写回数据库
        update_table_from_dataframe(df[mask], table_name, 
                                    id_column='unified_social_credit_code')


def get_relevant_data(question):

    table_list = ['company_basic_info', 'company_bidding_info', 
                  'company_financial_data', 'company_tax_info', 
                  'company_electricity_usage', 'merchant_transaction']
    
    table_list_dict = {
        'company_basic_info': ['基本信息', '注册', '法人', '信用代码', '企业名', '公司名'],
        'company_bidding_info': ['中标', '政采贷'],
        'company_financial_data': ['财务', '营业收入', '营收', '利润', '纳税', '收益', '负债', '主营业务', '年报'],
        'company_tax_info': ['税务', '纳税信用等级', '税额', '计税', '欠税', '税率'],
        'company_electricity_usage': ['电力', '用电', '电量', '电费', '电压', '欠费'],
        'merchant_transaction': ['流水', '交易']}

    relevant_table_list = []
    for table_name in table_list:
        if query_data(f"key is '{table_name}'") != {}:
            table_structure = pd.read_json(get_data(table_name), orient='records')
        else:
            table_structure = get_table_structure(table_name, is_str=False)
            save_data(table_name, table_structure.to_json(orient='records'))

        for column in table_structure['字段描述']:
            if column in question:
                relevant_table_list.append(table_name)
                break

        for key_word in table_list_dict[table_name]:
            if key_word in question:
                relevant_table_list.append(table_name)
                break

    table_name = 'company_bidding_info'
    relevant_data = ''
    for table_name in relevant_table_list:
        relevant_data += (get_table_structure(table_name) + '\n')

    return relevant_data


def get_analysis_prompt(question, relevant_data):
    
    # 初始化表结构的提示信息
    prompt = (f"你是一个专业的数据分析师，负责根据问题和数据表内容，生成对应的SQL语句，"
                "请根据我提供的数据回答问题。遵循以下规则：\n"
                "1. 先读取用户需要分析的问题\n"
                "2. 再读取数据表的表明和字段名\n"
                "3. 按照问题要求给出SQL语句实现用户分析的需求\n"
                "4. 在回答中仅需要给出SQL语句即可\n\n")

    # prompt += f"{question}\n\n" + f'数据库名为：ws_zcd\n' + f"{relevant_data}\n"
    prompt += f"{question}\n\n" + f"{relevant_data}\n"
    
    # print(prompt)
    # 打印或保存提示信息
    logger.info(prompt)

    return prompt


def parsed_chat(content):
    # 分割 <think> 内容和回答部分
    think_content = content.split('</think>')[0].replace('<think>', '').strip()
    response_content = content.split('</think>')[1].strip()

    # 去掉多余的标记（```sql 和 ```）
    sql_data = response_content.strip('```sql\n').strip('```').strip()

    return think_content, response_content, sql_data


def format_sql_response(res_content):
    think_content, response_content, sql_data = parsed_chat(res_content)
    return sql_data


def chat_analysis_response(question):
    '''
    USE ws_zcd;

    SELECT COUNT(DISTINCT unified_social_credit_code) AS winning_companies_count
    FROM company_bidding_info
    WHERE EXTRACT(YEAR FROM winning_date) = 2025;

    SELECT COUNT(DISTINCT unified_social_credit_code)
    FROM company_bidding_info
    WHERE winning_date BETWEEN '2025-01-01' AND '2025-12-31';
    '''
    relevant_data = get_relevant_data(question)
    analysis_prompt = get_analysis_prompt(question, relevant_data)
    llm_chat = LLM(config_obj.config['BASE_URL'])
    result = llm_chat.chat(analysis_prompt, config_obj.config['LLM_MODEL'])
    data = json.loads(result)['response']
    data['content'] = format_sql_response(data['content'])
    logger.info(f"response: {data}.")

    return data


if __name__=="__main__":
    question = '2025年中标企业有多少家？'

