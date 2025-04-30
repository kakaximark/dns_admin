from flask import Flask, jsonify, request
from api.api_cdn_ctl import register_cdn_routes
from api.api_dns_ctl import register_dns_routes
from api.api_waf_ctl import register_waf_routes
import logging
import time

app = Flask(__name__)

# 注册所有 CDN 路由
register_cdn_routes(app)
# 注册所有 DNS 路由
register_dns_routes(app)
# 注册所有 WAF 路由
register_waf_routes(app)

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,  # 日志级别
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # 日志输出到文件
        logging.StreamHandler()  # 日志输出到控制台
    ]
)

logger = logging.getLogger(__name__)

# 打印所有请求的日志
@app.before_request
def log_request_info():
    request.start_time = time.time()
    logger.info(f"Request: {request.method} {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Body: {request.get_data(as_text=True)}")

@app.after_request
def log_response_info(response):
    duration = time.time() - request.start_time
    logger.info(f"Response: {response.status_code} {response.get_data(as_text=True)}")
    logger.info(f"Duration: {duration:.3f}s")
    return response

# 全局异常处理器
@app.errorhandler(Exception)
def handle_global_exception(e):
    # 返回 JSON 格式的错误信息
    logger.error(f"Exception: {str(e)}", exc_info=True)
    return jsonify({
        "error": str(e),
        "type": type(e).__name__
    }), 500

if __name__ == "__main__":
    app.config["PROPAGATE_EXCEPTIONS"] = True  # 确保异常传播到全局处理器
    app.run(debug=True, host='0.0.0.0', port=8080)
    # app.run(host='0.0.0.0', port=8080)
