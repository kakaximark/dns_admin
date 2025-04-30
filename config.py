#
# SECRET_KEY = 'your_secret_key'
# DATABASE_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'admin9877',
#     'database': 'devops_manager'
# }


class Config:
    WAF_PATH = 'api_waf'
    WAF_PACKAGE = 'api_waf'
    CDNS_PATH = 'cdns'  # CDN 实现类所在文件夹路径
    CDNS_PACKAGE = 'cdns'  # CDN 实现类所在包
    DNS_PATH = 'api_dns'
    DNS_PACKAGE = 'api_dns'
    client_param = {
        "api_token": "cloudflare_api_token"
    }
    BIND_NGINX_API = 'http://172.20.0.183:8080/subAgent'
    # BIND_NGINX_API = 'http://127.0.0.1:8888/subAgent'