import csv
import json
import yaml


class Config:
    def __init__(self, debug=False):
        self.debug = debug
        # 读取YAML配置文件
        with open('application.yml', 'r') as file:
            self.config = yaml.safe_load(file)

    def match_company(self, query_name):

        company_json = self.company_config()
        
        # 遍历JSON数据，查找匹配的公司信息
        matched_company = None
        for company in company_json:
            if company["企业名称"] == query_name or company["统一社会信用代码"] == query_name:
                matched_company = company
                break  # 如果只需要找到第一个匹配项，就使用break退出循环
        
        # 输出匹配的公司信息
        if matched_company:
            return matched_company
        else:
            return None

    def match_product(self, product_name):

        product_json = self.product_config()
        
        # 遍历JSON数据，查找匹配的产品信息
        matched_product = None
        for product in product_json:
            if product["产品名称"] == product_name or \
                product["产品名称"] in product_name or \
                    product_name in product["产品名称"]:
                matched_product = product
                break  # 如果只需要找到第一个匹配项，就使用break退出循环
        
        # 输出匹配的公司信息
        if matched_product:
            return matched_product
        else:
            return None

    def company_config(self):
        """
        企业列表
        """
        # 定义CSV文件的路径
        csv_file_path = self.config['company_path']

        # 读取CSV文件并转换为JSON格式
        data = []
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            # 使用csv.DictReader读取CSV文件，自动将第一行作为表头
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                # 将每行数据添加到列表中
                data.append(row)
        
        return data

    def product_config(self, match=True):
        """
        产品信息
        """
        # 定义CSV文件的路径
        if match:
            csv_file_path = self.config['product_path']
        else:
            csv_file_path = self.config['product1_path']

        # 读取CSV文件并转换为JSON格式
        data = []
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            # 使用csv.DictReader读取CSV文件，自动将第一行作为表头
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                # 将每行数据添加到列表中
                data.append(row)

        return data

    def rule_config(self):
        """
        推荐规则信息
        """
        # 定义CSV文件的路径
        csv_file_path = self.config['rule_path']

        # 读取CSV文件并转换为JSON格式
        data = []
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            for line in csvfile:
                # 将每行数据添加到列表中
                data.append(line)

        return data


# 示例用法
if __name__ == "__main__":
    # 从环境变量加载配置
    config = Config()
    
    company_json = config.company_config()
    print(company_json)
    product_json = config.product_config()
    print(product_json)
    rule_list = config.rule_config()
    print(rule_list)

    print(config.match_company('xx公司'))
    print(config.match_company('91310100MA1G0QJX4C'))

    print(config.match_product('481bdab643084e7f9a89bebeae3fc0a5'))
