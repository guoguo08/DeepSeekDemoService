import json
from datetime import datetime
import pandas as pd

from config.log import get_logger
from config.config import Config
from db.db_orm import read_table_to_dataframe, update_table_from_dataframe
from db.db_orm import get_table_structure
from db.db import get_data, query_data, save_data
from llm.llm import LLM
from db.db_orm import execute_sql_query


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


def calculate_age_score(establishment_date):
    if pd.isna(establishment_date):
        return 0  # 处理空值情况
    
    # 计算年限（转换为年数）
    delta = datetime.now() - establishment_date
    years = delta.days / 365.25
    
    # 根据年限返回对应分值
    if years > 5:
        return 100
    elif 3 < years <= 5:
        return 80
    elif 1 < years <= 3:
        return 60
    else:
        return 40


def modeling():
    """模型设计"""
    # 这里可以添加模型设计的逻辑

    company_basic = 'company_basic_info'
    company_basic_df = read_table_to_dataframe(company_basic)


    # 企业基本信息表(company_basic_info)评分模型（20%）
    company_basic_df['basic_score'] = company_basic_df['company_status'].apply(
        lambda x: 100 if x in ['运营中', '存续'] else 0
    ) * 0.3
    company_basic_df['basic_score'] += company_basic_df['establishment_date'].apply(calculate_age_score) * 0.2
    company_basic_df['basic_score'] += company_basic_df['registered_capital'].apply(
        lambda x: 100 if x > 10000 else (80 if x > 1000 else (60 if x > 100 else 40))
    ) * 0.15
    company_basic_df['basic_score'] += company_basic_df['employee_count'].apply(
        lambda x: 100 if x > 1000 else (80 if x > 500 else (60 if x > 100 else 40))
    ) * 0.1
    company_basic_df['basic_score'] += company_basic_df['total_financing_amount'].apply(
        lambda x: 100 if x > 10000 else (80 if x > 5000 else (60 if x > 1000 else 40))
    ) * 0.1
    company_basic_df['basic_score'] += company_basic_df['shareholder_count'].apply(
        lambda x: 100 if x > 10 else (80 if x > 5 else (60 if x > 2 else 40))
    ) * 0.1
    company_basic_df['basic_score'] += company_basic_df['industry'].apply(
        lambda x: 100  if x is not None else 40
    ) * 0.05


    # 企业中标信息表(company_bidding_info)评分模型（20%）
    # 评分维度：
    # 中标金额(40%)：按金额分级评分
    # 中标频率(30%)：中标次数分级评分
    # 负面信息(30%)：无负面=100，有负面=0
    # 政采贷情况(0%)：政采贷金额和次数综合评分

    company_bidding = 'company_bidding_info'
    company_bidding_df = read_table_to_dataframe(company_bidding)
    # 将多次中标企业去重
    company_bidding_df_uniq = company_bidding_df[['unified_social_credit_code']].drop_duplicates(
        subset=['unified_social_credit_code']).reset_index()[['unified_social_credit_code']]
    # 根据累计中标金额(分组求和)计算评分
    company_bidding_df_uniq['bidding_score'] = 0
    bidding__amount = company_bidding_df.groupby('unified_social_credit_code')['winning_amount'].sum().reset_index()
    company_bidding_df_uniq = company_bidding_df_uniq.merge(
        bidding__amount,
        on='unified_social_credit_code',
        how='left'
    )
    company_bidding_df_uniq['bidding_score'] += company_bidding_df_uniq['winning_amount'].apply(
        lambda x: 100 if x > 10000 else (80 if x > 5000 else (60 if x > 1000 else 40))
    ) * 0.4

    company_bidding_count = company_bidding_df.groupby('unified_social_credit_code').size().reset_index(name='bid_count')
    company_bidding_df_uniq = company_bidding_df_uniq.merge(
        company_bidding_count,
        on='unified_social_credit_code',
        how='left'
    )

    company_bidding_df_uniq['bidding_score'] += company_bidding_df_uniq['bid_count'].apply(
        lambda x: 100 if x > 10 else (80 if x > 5 else (60 if x >= 2 else 40))
    ) * 0.3

    company_information = (
        company_bidding_df
        .sort_values('winning_date',ascending=False)
        .groupby('unified_social_credit_code')
        .head(1))

    company_bidding_df_uniq = company_bidding_df_uniq.merge(
        company_information,
        on='unified_social_credit_code',
        how='left'
    )
    company_bidding_df_uniq['bidding_score'] += company_bidding_df_uniq['negative_information'].apply(
        lambda x: 100 if x == "无" else 0
    ) * 0.3

    # 企业财务信息表(company_financial_data)
    # 评分模型
    # 权重：25 %
    #
    # 评分维度：
    # 盈利能力(30 %)：净利润率评分
    # 偿债能力(25 %)：资产负债率评分
    # 运营效率(20 %)：营业成本占比评分
    # 税收缴纳(15 %)：纳税总额评分
    # 社保缴纳(10 %)：社保参保人数评分

    # 读表数据成dataframe
    company_financial = 'company_financial_data'
    company_finacial_df = read_table_to_dataframe(company_financial)

    company_finacial_df = company_finacial_df.sort_values('create_time').groupby('unified_social_credit_code').apply(
        lambda x: x.assign(
            profit_margin=x['total_profit'] / x['operating_income']
        )
    ).reset_index(drop=True)

    company_finacial_unique = company_finacial_df.drop_duplicates(
        subset=['unified_social_credit_code'],
        keep='last'
    )

    company_finacial_unique['financial_score'] = 0
    company_finacial_unique['financial_score'] += company_finacial_unique['profit_margin'].apply(
        lambda x: 100 if x > 0.4 else (90 if x > 0.3 else (80 if x > 0.2 else (60 if x > 0.1 else 40)))
    )  * 0.3

    company_finacial_unique['asset_liability_ratio'] = (company_finacial_unique['total_liabilities']
                                                        / company_finacial_unique['total_assets'])
    company_finacial_unique['financial_score'] += company_finacial_unique['asset_liability_ratio'].apply(
        lambda x: 100 if x < 0.2 else (90 if x<0.4 else (80 if x < 0.6 else (60 if x < 0.8 else 40)))
    ) * 0.25

    company_finacial_unique['proportion_operating_costs'] = (company_finacial_unique['total_operating_costs']
                                                             / company_finacial_unique['operating_income'])
    company_finacial_unique['financial_score'] += company_finacial_unique['proportion_operating_costs'].apply(
        lambda x: 40 if x > 0.9 else (60 if x > 0.7 else (80 if x > 0.5 else (90 if x > 0.4 else 100)))
    ) * 0.2

    company_finacial_unique['financial_score'] += company_finacial_unique['total_tax_payment'].apply(
        lambda x: 100 if x > 10000 else (80 if x > 5000 else (60 if x > 1000 else 40))
    ) * 0.15

    company_finacial_unique['financial_score'] += company_finacial_unique['endowment_insurance_count'].apply(
        lambda x: 100 if x > 1000 else (80 if x > 500 else (70 if x > 100 else (60 if x > 50 else 40 )))
    ) * 0.1


    # 1.4 企业税务信息表(company_tax_info)评分模型
    # 权重：20%
    # 评分维度：
    # 纳税信用等级(40%)：A=100，B=80，C=60，D=0
    # 欠税情况(30%)：欠税金额和期数评分
    # 税收增长率(20%)：本年累计同比评分
    # 申报及时性(10%)：申报期限遵守情况评分

    company_tax = 'company_tax_info'
    company_tax_df = read_table_to_dataframe(company_tax)

    company_tax_df_uniq = company_tax_df.sort_values('declaration_date' , ascending=False).drop_duplicates(
        subset=['unified_social_credit_code'],
        keep='first'
    )

    company_tax_df_uniq['tax_score'] = 0
    company_tax_df_uniq['tax_score'] += company_tax_df_uniq['tax_credit_rating'].apply(
        lambda x: 100 if x == "A级" else (80 if x == "B级" else (60 if x == "C级" else 0))
    ) * 0.4

    company_tax_df_uniq['tax_score'] += company_tax_df_uniq['tax_arrears_balance'].apply(
        lambda x: 100 if x == 0 else (80 if x < 1000 else (60 if x < 5000 else(40 if x < 10000 else 0)))
    ) * 0.3

    company_tax_df_uniq['tax_score'] += company_tax_df_uniq['year_to_date_amount'].apply(
        lambda x: 100 if x > 50000000 else (90 if x > 30000000 else (80 if x > 10000000 else (70 if x > 5000000 else 60)))
    ) * 0.2

    company_tax_df_uniq['tax_score'] += company_tax_df_uniq['rating_score'].apply(
        lambda x: 100 if x > 90 else (90 if x > 80 else (80 if x > 70 else 60 if x > 60 else 40))
    ) * 0.1

    # 1.5 企业电力使用信息表(company_electricity_usage)评分模型
    # 权重：10%
    # 评分维度：
    # 用电趋势(40%)：上升=100，平稳=80，下降=60
    # 用电规模(30%)：电容量和电量等级评分
    # 欠费情况(20%)：欠费期数评分
    # 违章用电(10%)：无违章=100，有违章=0
    company_electricity = 'company_electricity_usage'
    company_electricity_df = read_table_to_dataframe(company_electricity)

    company_electricity_df_uniq = company_electricity_df.sort_values('record_time', ascending=False).drop_duplicates(
        subset=['unified_social_credit_code'],
        keep='first'
    )
    company_electricity_df_uniq['electricity_score'] = 0

    company_electricity_df_uniq['electricity_score'] += company_electricity_df_uniq['electricity_trend'].apply(
        lambda x: 100 if x == "上升" else (80 if x == "平稳" else 60)
    ) * 0.4

    company_electricity_df_uniq['electricity_score'] += company_electricity_df_uniq['user_capacity'].apply(
        lambda x: 100 if x > 10000 else (80 if x > 5000 else (60 if x > 1000 else 40))
    ) * 0.3

    company_electricity_df_uniq['electricity_score'] += company_electricity_df_uniq['arrears_periods'].apply(
        lambda x: 100 if x == 0 else (80 if x <= 3  else (60 if x <= 6 else 40))
    ) * 0.2

    company_electricity_df_uniq['electricity_score'] += company_electricity_df_uniq['is_illegal_usage'].apply(
        lambda x: 100 if x == 0 else 0
    ) * 0.1

    # 1.6 商户流水信息表(merchant_transaction)评分模型
    # 权重：10%
    # 评分维度：
    # 交易金额(60%)：近90天和365天金额评分
    # 交易用户数(40%)：近90天和365天用户数评分

    company_transaction = 'merchant_transaction'
    company_transaction_df = read_table_to_dataframe(company_transaction)

    company_transaction_df_uniq = company_transaction_df.sort_values('create_time', ascending=False).drop_duplicates(
        subset=['unified_social_credit_code'],
        keep='first'
    )
    company_transaction_df_uniq['transaction_score'] = 0
    company_transaction_df_uniq['transaction_score'] += company_transaction_df_uniq['amount_last_90d'].apply(
        lambda x: 100 if x > 10000000 else (90 if x > 8000000 else (80 if x > 5000000 else (60 if x > 1000000 else 40) ))
    ) * 0.3
    company_transaction_df_uniq['transaction_score'] += company_transaction_df_uniq['amount_last_365d'].apply(
        lambda x: 100 if x > 100000000 else (90 if x > 80000000 else (80 if x > 50000000 else (60 if x > 10000000 else 40)))
    ) * 0.3
    company_transaction_df_uniq['transaction_score'] += company_transaction_df_uniq['users_last_90d'].apply(
        lambda x: 100 if x > 500 else (90 if x > 400 else (80 if x > 300 else (60 if x > 200 else 40)))
    ) * 0.2
    company_transaction_df_uniq['transaction_score'] += company_transaction_df_uniq['users_last_365d'].apply(
        lambda x: 100 if x > 5000 else (80 if x > 3000 else (60 if x > 1000 else 40))
    ) * 0.2

    # 企业画像表
    company_portrait = company_basic_df[['company_name', 'unified_social_credit_code']]
    company_portrait['basic_score'] = pd.merge(
        company_portrait, company_basic_df, on='unified_social_credit_code', how='left'
    )['basic_score']
    company_portrait['bidding_score'] = pd.merge(
        company_portrait, company_bidding_df_uniq, on='unified_social_credit_code', how='left'
    )['bidding_score'].fillna(0)
    company_portrait['financial_score'] = pd.merge(
        company_portrait, company_finacial_unique, on='unified_social_credit_code', how='left'
    )['financial_score'].fillna(0)
    company_portrait['tax_score'] = pd.merge(
        company_portrait, company_tax_df_uniq, on='unified_social_credit_code', how='left'
    )['tax_score'].fillna(0)
    company_portrait['electricity_score'] = pd.merge(
        company_portrait, company_electricity_df_uniq, on='unified_social_credit_code', how='left'
    )['electricity_score'].fillna(0)
    company_portrait['transaction_score'] = pd.merge(
        company_portrait, company_transaction_df_uniq, on='unified_social_credit_code', how='left'
    )['transaction_score'].fillna(0)
    company_portrait['total_score'] = (company_portrait['basic_score'] * 0.2
                                       + company_portrait['bidding_score'] * 0.15
                                       + company_portrait['financial_score'] * 0.25
                                       + company_portrait['tax_score'] * 0.2
                                       + company_portrait['electricity_score'] * 0.1
                                       + company_portrait['transaction_score'] * 0.1)

    company_portrait['credit_level'] = company_portrait['total_score'].apply(
        lambda x: "AAA" if x >= 95 else (
            "AA" if x>= 90 else (
                "A" if x >=85 else (
                    "BBB" if x >= 80 else (
                        "BB" if x >= 75 else (
                            "B" if x >= 70 else (
                                "CCC" if x >= 65 else (
                                    "CC" if x >= 60 else (
                                       'C' if x >= 0 else "NaN")
                                )
                            )
                        )
                    )
                )
            )
        )
    )

    bidding_amount_new = company_bidding_df.sort_values('winning_date',ascending=False)\
                                        .groupby('unified_social_credit_code')\
                                        .head(1)\
                                        .reset_index(drop=True)[['unified_social_credit_code','winning_amount']]

    company_portrait = company_portrait.merge(
        bidding_amount_new,
        on='unified_social_credit_code',
        how='left'
    )

    company_portrait['recommended_limit'] = company_portrait['winning_amount'] * company_portrait['total_score'] / 100
    company_portrait['recommended_limit'] = company_portrait['recommended_limit'].fillna(0)

    update_credit_limit(company_portrait)

    logger.info(f"模型设计结果: {company_portrait}")

    # model_result = ...
    # logger.info(f"模型设计结果: {model_result}")
    # return model_result




def update_credit_limit(calculated_df):
    """更新商户信用额度"""
    table_name = 'merchant_credit_limit'
    db_df = read_table_to_dataframe(table_name)

    if db_df is None:
        print("无法从数据库读取商户信用额度表")
        return

    if calculated_df is None or calculated_df.empty:
        print("没有需要更新的计算结果")
        return

    # 只保留需要更新的字段
    update_df = calculated_df[['unified_social_credit_code', 'credit_level', 'recommended_limit']]

    # 合并数据，找出需要更新的记录
    merged_df = pd.merge(db_df, update_df,
                         on='unified_social_credit_code',
                         how='inner',
                         suffixes=('_db', '_new'))

    # 筛选出需要更新的记录（信用等级或额度有变化的）
    needs_update = merged_df[
        (merged_df['credit_level_db'] != merged_df['credit_level_new']) |
        (merged_df['recommended_limit_db'] != merged_df['recommended_limit_new'])
        ]

    if needs_update.empty:
        print("没有需要更新的记录")
        return

    # 准备更新用的DataFrame，添加update_time字段
    final_update_df = needs_update[['unified_social_credit_code']].copy()
    final_update_df['credit_level'] = needs_update['credit_level_new']
    final_update_df['recommended_limit'] = needs_update['recommended_limit_new']
    final_update_df['update_time'] = pd.Timestamp.now()  # 添加更新时间

    # 执行更新
    update_table_from_dataframe(final_update_df, table_name,
                                id_column='unified_social_credit_code')
    print(f"成功更新了 {len(final_update_df)} 条记录")
    logger.info(f"成功更新了 {len(final_update_df)} 条记录")




def get_relevant_data(question):

    table_list = ['company_basic_info', 'company_bidding_info', 
                  'company_financial_data', 'company_tax_info', 
                  'company_electricity_usage', 'merchant_transaction']
    
    table_list_dict = {
        'company_basic_info': ['基本信息', '注册', '法人', '信用代码', '企业名', '公司名'],
        'company_bidding_info': ['中标', '政采贷'],
        'company_financial_data': ['财务', '营业收入', '营收', '利润', '纳税', '收益', '负债', '主营业务', '年报'],
        'company_tax_info': ['税务', '纳税', '纳税信用等级', '税额', '计税', '欠税', '税率'],
        'company_electricity_usage': ['电力', '用电', '电量', '电费', '电压', '欠费'],
        'merchant_transaction': ['流水', '交易']}

    relevant_table_list = []
    for table_name in table_list:
        if query_data(f"key is '{table_name}'") != {}:
            table_structure = pd.read_json(get_data(table_name), orient='records')
        else:
            table_structure = get_table_structure(table_name, is_str=False)
            save_data(table_name, table_structure.to_json(orient='records'))

        # for column in table_structure['字段描述']:
        #     if column in question:
        #         relevant_table_list.append(table_name)
        #         break

        for key_word in table_list_dict[table_name]:
            if key_word in question:
                relevant_table_list.append(table_name)
                break

    # 去重
    relevant_table_list = list(set(relevant_table_list))
    
    relevant_data = ''
    for table_name in relevant_table_list:
        relevant_data += (get_table_structure(table_name) + '\n')

    return relevant_data ,relevant_table_list


def get_analysis_prompt(question, relevant_data):
    
    # 初始化表结构的提示信息
    prompt = (f"你是一个专业的数据分析师，负责根据问题和数据表内容，生成对应的SQL语句，"
                "请根据我提供的数据回答问题。遵循以下规则：\n"
                "1. 先读取用户需要分析的问题\n"
                "2. 再读取数据表的表明和字段名\n"
                "3. 按照问题要求给出SQL语句实现用户分析的需求\n"
                "4. 在回答中仅需要给出SQL语句即可\n"
                "5. 在给出的SQL代码中不要有\\n符号。\n"
                "6. 必须将 SQL 代码包裹在 ```sql 和 ``` 之间。\n\n")

    # prompt += f"{question}\n\n" + f'数据库名为：ws_zcd\n' + f"{relevant_data}\n"
    prompt += f"{question}\n\n" + f"{relevant_data}\n"

    # print(prompt)
    # 打印或保存提示信息
    logger.info(prompt)

    return prompt

def get_conclusion_prompt(question,sql):
    """
    根据问题和SQL结果数据生成回答结论
    """
    prompt = (f"你是一个专业的数据分析师，负责查询结果的数据分析，"
                "请根据我提供的数据进行分析。：\n\n")

    sql_result = execute_sql_query(sql)
    prompt += f"问题：{question}\n\n" + f"数据：{sql_result}\n"

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

def format_result_response(res_content):
    think_content, response_content, sql_data = parsed_chat(res_content)
    return response_content

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
    relevant_data , relevant_table_list = get_relevant_data(question)
    analysis_prompt = get_analysis_prompt(question, relevant_data)
    llm_chat = LLM(config_obj.config['BASE_URL'])
    result = llm_chat.chat(analysis_prompt, config_obj.config['LLM_MODEL'])
    data = json.loads(result)['response']
    logger.info(f"response: {data}.")
    data['content'] = format_sql_response(data['content'])
    data['table_list'] = relevant_table_list
    # sql = "SELECT YEAR(winning_date) AS year, COUNT(DISTINCT unified_social_credit_code) AS company_count FROM company_bidding_info GROUP BY YEAR(winning_date) ORDER BY year;"
    # conclusion_prompt = get_conclusion_prompt(question, sql)
    conclusion_prompt = get_conclusion_prompt(question, data['content'])
    conclusion_result = llm_chat.chat(conclusion_prompt,config_obj.config['LLM_MODEL'])
    conc_result = json.loads(conclusion_result)['response']
    data['conclusion'] = format_result_response(conc_result['content'])
    logger.info(f"response: {data['conclusion']}.")
    logger.info("分析完成")
    data['content'] = data['content'].replace('\n', ' ')
    data['conclusion'] = data['conclusion'].replace('\n', ' ')
    logger.info("格式化完成")
    return data


if __name__=="__main__":
    question = '2025年中标企业有多少家？'

