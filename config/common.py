TRANSLATION_DICT = {
    "ID": "产品编号",
    "ORG_CODE": "银行代码",
    "ORG_NAME": "银行名称",
    "PRODUCT_NAME": "产品名称",
    "PRODUCT_CODE": "产品代码",
    "PRODUCT_TYPE": "产品类型",
    "PRODUCT_SUB_TYPE": "产品子类型",
    "PRODUCT_LEVEL": "产品等级",
    "MIN_RATE": "最低利率",
    "MAX_RATE": "最高利率",
    "SHOW_RATE": "显示利率",
    "MIN_AMOUNT": "最低额度",
    "MAX_AMOUNT": "最高额度",
    "SHOW_AMOUNT": "显示额度",
    "MIN_TERM": "最短周期",
    "MAX_TERM": "最长周期",
    "SHOW_TERM": "显示周期",
    "PRODUCT_REMARK": "产品描述",
    "USE_AREA": "使用地区",
    "APPLY_CUST": "适用主体/适用客户",
    "PRODUCT_FEATURE_TAG": "产品特征标签",
    "PRODUCT_FEATURE": "产品特征",
    "GUARANT_TYPE": "担保方式",
    "LOAN_USAGE": "贷款用途",
    "COMMIT_STUFF_TAG": "提交材料标签",
    "COMMIT_STUFF": "提交材料",
    "APPLY_CONDITION": "申请条件",
    "PRODUCT_STAR": "产品星级",
    "PRODUCT_TAG": "产品标签",
    "RATE_TYPE_CODE": "利率类型代码",
    "PRODUCT_OBJECT": "产品对象",
    "PARENT_ID": "总行编号",
    "AREA": "地区",
    "AREA_CODE": "地区代码",
    "STATUS": "状态",
    "COUNTER_GUARANT_TYPE": "反担保类型",
    "PRODUCT_URL": "产品链接",
    "PC_PIC_URL": "银行图标链接",
    "APP_PIC_URL": "银行APP图标链接",
    "APPLY_REF_TYPE": "申请参考类型",
    "RATE_TYPE_NAME": "利率类型名称",
    "PHONE": "电话",
    "PRODUCT_QR_CODE": "产品二维码",
    "CREATE_TIME": "创建时间",
    "CREATE_BY": "创建人",
    "UPDATE_TIME": "更新时间",
    "UPDATE_BY": "更新人",
    "SFTJ": "SFTJ",
    "CREATE_ID": "创建编号",
    "CPLY": "CPLY",
    "RECOMMEND_REASON": "推荐理由",
    "FINANCIAL_RISK_NOTES": "金融风控注意事项",
    "产品编号": "ID",
    "银行代码": "ORG_CODE",
    "银行名称": "ORG_NAME",
    "产品名称": "PRODUCT_NAME",
    "产品代码": "PRODUCT_CODE",
    "产品类型": "PRODUCT_TYPE",
    "产品子类型": "PRODUCT_SUB_TYPE",
    "产品等级": "PRODUCT_LEVEL",
    "最低利率": "MIN_RATE",
    "最高利率": "MAX_RATE",
    "显示利率": "SHOW_RATE",
    "最低额度": "MIN_AMOUNT",
    "最高额度": "MAX_AMOUNT",
    "显示额度": "SHOW_AMOUNT",
    "最短周期": "MIN_TERM",
    "最长周期": "MAX_TERM",
    "显示周期": "SHOW_TERM",
    "产品描述": "PRODUCT_REMARK",
    "使用地区": "USE_AREA",
    "适用主体/适用客户": "APPLY_CUST",
    "产品特征标签": "PRODUCT_FEATURE_TAG",
    "产品特征": "PRODUCT_FEATURE",
    "担保方式": "GUARANT_TYPE",
    "贷款用途": "LOAN_USAGE",
    "提交材料标签": "COMMIT_STUFF_TAG",
    "提交材料": "COMMIT_STUFF",
    "申请条件": "APPLY_CONDITION",
    "产品星级": "PRODUCT_STAR",
    "产品标签": "PRODUCT_TAG",
    "利率类型代码": "RATE_TYPE_CODE",
    "产品对象": "PRODUCT_OBJECT",
    "总行编号": "PARENT_ID",
    "地区": "AREA",
    "地区代码": "AREA_CODE",
    "状态": "STATUS",
    "反担保类型": "COUNTER_GUARANT_TYPE",
    "产品链接": "PRODUCT_URL",
    "银行图标链接": "PC_PIC_URL",
    "银行APP图标链接": "APP_PIC_URL",
    "申请参考类型": "APPLY_REF_TYPE",
    "利率类型名称": "RATE_TYPE_NAME",
    "电话": "PHONE",
    "产品二维码": "PRODUCT_QR_CODE",
    "创建时间": "CREATE_TIME",
    "创建人": "CREATE_BY",
    "更新时间": "UPDATE_TIME",
    "更新人": "UPDATE_BY",
    "创建编号": "CREATE_ID",
    "推荐理由": "RECOMMEND_REASON",
    "金融风控注意事项": "FINANCIAL_RISK_NOTES",
}


class Product:
    def __init__(self, 
                 ID=None, 
                 ORG_CODE=None, 
                 ORG_NAME=None, 
                 PRODUCT_NAME=None, 
                 PRODUCT_CODE=None, 
                 PRODUCT_TYPE=None, 
                 PRODUCT_SUB_TYPE=None, 
                 PRODUCT_LEVEL=None, 
                 MIN_RATE=None, 
                 MAX_RATE=None, 
                 SHOW_RATE=None, 
                 MIN_AMOUNT=None, 
                 MAX_AMOUNT=None, 
                 SHOW_AMOUNT=None, 
                 MIN_TERM=None, 
                 MAX_TERM=None, 
                 SHOW_TERM=None, 
                 PRODUCT_REMARK=None, 
                 USE_AREA=None, 
                 APPLY_CUST=None, 
                 PRODUCT_FEATURE_TAG=None, 
                 PRODUCT_FEATURE=None, 
                 GUARANT_TYPE=None, 
                 LOAN_USAGE=None, 
                 COMMIT_STUFF_TAG=None, 
                 COMMIT_STUFF=None, 
                 APPLY_CONDITION=None, 
                 PRODUCT_STAR=None, 
                 PRODUCT_TAG=None, 
                 RATE_TYPE_CODE=None, 
                 PRODUCT_OBJECT=None, 
                 PARENT_ID=None, 
                 AREA=None, 
                 AREA_CODE=None, 
                 STATUS=None, 
                 COUNTER_GUARANT_TYPE=None, 
                 PRODUCT_URL=None, 
                 PC_PIC_URL=None, 
                 APP_PIC_URL=None, 
                 APPLY_REF_TYPE=None, 
                 RATE_TYPE_NAME=None, 
                 PHONE=None, 
                 PRODUCT_QR_CODE=None, 
                 CREATE_TIME=None, 
                 CREATE_BY=None, 
                 CREATE_ID=None, 
                 UPDATE_TIME=None, 
                 UPDATE_BY=None, 
                 SFTJ=None, 
                 GUARANT_TYPE_NAME=None, 
                 PRODUCT_TYPE_NAME=None, 
                 PRODUCT_FEATURE_NAME=None, 
                 LOAN_USAGE_NAME=None, 
                 APPLY_CUST_NAME=None, 
                 USE_AREA_NAME=None, 
                 SFYSC=None, 
                 RMCPSQL=None, 
                 SLJE=None, 
                 CPLY=None, 
                 CPLY_NAME=None,
                 RECOMMEND_REASON=None,
                 FINANCIAL_RISK_NOTES=None
                 ):
        self.ID = ID
        self.ORG_CODE = ORG_CODE
        self.ORG_NAME = ORG_NAME
        self.PRODUCT_NAME = PRODUCT_NAME
        self.PRODUCT_CODE = PRODUCT_CODE
        self.PRODUCT_TYPE = PRODUCT_TYPE
        self.PRODUCT_SUB_TYPE = PRODUCT_SUB_TYPE
        self.PRODUCT_LEVEL = PRODUCT_LEVEL
        self.MIN_RATE = MIN_RATE
        self.MAX_RATE = MAX_RATE
        self.SHOW_RATE = SHOW_RATE
        self.MIN_AMOUNT = MIN_AMOUNT
        self.MAX_AMOUNT = MAX_AMOUNT
        self.SHOW_AMOUNT = SHOW_AMOUNT
        self.MIN_TERM = MIN_TERM
        self.MAX_TERM = MAX_TERM
        self.SHOW_TERM = SHOW_TERM
        self.PRODUCT_REMARK = PRODUCT_REMARK
        self.USE_AREA = USE_AREA
        self.APPLY_CUST = APPLY_CUST
        self.PRODUCT_FEATURE_TAG = PRODUCT_FEATURE_TAG
        self.PRODUCT_FEATURE = PRODUCT_FEATURE
        self.GUARANT_TYPE = GUARANT_TYPE
        self.LOAN_USAGE = LOAN_USAGE
        self.COMMIT_STUFF_TAG = COMMIT_STUFF_TAG
        self.COMMIT_STUFF = COMMIT_STUFF
        self.APPLY_CONDITION = APPLY_CONDITION
        self.PRODUCT_STAR = PRODUCT_STAR
        self.PRODUCT_TAG = PRODUCT_TAG
        self.RATE_TYPE_CODE = RATE_TYPE_CODE
        self.PRODUCT_OBJECT = PRODUCT_OBJECT
        self.PARENT_ID = PARENT_ID
        self.AREA = AREA
        self.AREA_CODE = AREA_CODE
        self.STATUS = STATUS
        self.COUNTER_GUARANT_TYPE = COUNTER_GUARANT_TYPE
        self.PRODUCT_URL = PRODUCT_URL
        self.PC_PIC_URL = PC_PIC_URL
        self.APP_PIC_URL = APP_PIC_URL
        self.APPLY_REF_TYPE = APPLY_REF_TYPE
        self.RATE_TYPE_NAME = RATE_TYPE_NAME
        self.PHONE = PHONE
        self.PRODUCT_QR_CODE = PRODUCT_QR_CODE
        self.CREATE_TIME = CREATE_TIME
        self.CREATE_BY = CREATE_BY
        self.CREATE_ID = CREATE_ID
        self.UPDATE_TIME = UPDATE_TIME
        self.UPDATE_BY = UPDATE_BY
        self.SFTJ = SFTJ
        self.GUARANT_TYPE_NAME = GUARANT_TYPE_NAME
        self.PRODUCT_TYPE_NAME = PRODUCT_TYPE_NAME
        self.PRODUCT_FEATURE_NAME = PRODUCT_FEATURE_NAME
        self.LOAN_USAGE_NAME = LOAN_USAGE_NAME
        self.APPLY_CUST_NAME = APPLY_CUST_NAME
        self.USE_AREA_NAME = USE_AREA_NAME
        self.SFYSC = SFYSC
        self.RMCPSQL = RMCPSQL
        self.SLJE = SLJE
        self.CPLY = CPLY
        self.CPLY_NAME = CPLY_NAME
        self.RECOMMEND_REASON = RECOMMEND_REASON
        self.FINANCIAL_RISK_NOTES = FINANCIAL_RISK_NOTES

    def replace(self, replace_dict={}):
        for key, value in replace_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


if __name__=="__main__":
    product = Product()
    print(product.__dict__)
    product.replace({"ORG_NAME": "中国工商银行青海省分行"})
    print(product.__dict__)
