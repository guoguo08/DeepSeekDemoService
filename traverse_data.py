import datetime
import requests
from config.config import Config


def search_data(company):
    # 接口 URL
    url = "http://127.0.0.1:5810/search"  # 替换为实际的接口地址

    # 请求参数
    data = {
        "q": company
    }

    # 发送 POST 请求
    response = requests.request("POST", url, data=data)
    return response.json()


def traverse_data(parsed_data):
    for company in parsed_data:
        try:
            search_data(company)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  "完成 " + company + ' 推荐')
        except Exception as e:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  "Error " + company + ' 推荐')
            print(e)


if __name__=="__main__":
    config_obj = Config()
    company_json = config_obj.company_config()
    company_list = [company['企业名称'] for company in company_json]
    traverse_data(company_list)
