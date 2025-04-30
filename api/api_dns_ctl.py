import importlib
import pkgutil
from flask import jsonify, request
from api_dns.interface import DNSInterface
from config import Config

def load_dns_classes():
    """
    动态加载所有实现了 DNSInterface 的类
    """
    dns_classes = {}
    for _, module_name, _ in pkgutil.iter_modules([Config.DNS_PATH]):
        module = importlib.import_module(f'{Config.DNS_PACKAGE}.{module_name}')
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, DNSInterface) and attr is not DNSInterface:
                dns_classes[module_name] = attr
    return dns_classes

def register_dns_routes(app):
    """
    根据 DNS 实现动态生成路由
    """
    dns_classes = load_dns_classes()
    # 新增: 获取所有DNS提供商列表的路由
    @app.route('/dns/providers', methods=['GET'])
    def get_dns_providers():
        providers = []
        for provider, dns_class in dns_classes.items():
            # 获取类中的可用方法
            methods = []
            for method_name in dir(DNSInterface):
                method = getattr(DNSInterface, method_name, None)
                if callable(method) and getattr(method, "__isabstractmethod__", False):
                    methods.append(method_name)
            
            providers.append({
                'name': provider,
                'class': dns_class.__name__,
                'methods': methods
            })
        return jsonify({
            'code': 200,
            'message': 'DNS providers retrieved successfully',
            'data': providers
        })

    for provider, dns_class in dns_classes.items():
        for method_name in dir(DNSInterface):
            method = getattr(DNSInterface, method_name, None)
            if callable(method) and getattr(method, "__isabstractmethod__", False):
                route_path = f"/dns/{provider}/{method_name}"

                def create_api_handler(provider_name, dns_class, method_name):
                    def api_handler():
                        # 获取客户端初始化参数
                        # client_param = request.json.get("client_param", {})
                        # print(client_param)
                        # if not client_param:
                        #     return jsonify({"error": "Missing 'client_param' for DNS client initialization"}), 400
                        client_param = Config.client_param
                        # print(client_param)
                        
                        # 验证必要参数
                        if "api_token" not in client_param:
                            return jsonify({"error": "Missing required parameter 'api_token'"}), 400
                        
                        # 初始化 DNS 客户端
                        try:
                            client = dns_class(**client_param)
                            # client = dns_class()
                        except Exception as e:
                            return jsonify({"error": f"Failed to initialize DNS client: {str(e)}"}), 400

                        # 获取方法参数
                        try:
                            method_args = request.json.get("method_args", {})
                            # print(f"method_args: {method_args}")
                            method = getattr(client, method_name)
                        except Exception as e:
                            return jsonify({"error": "Missing required parameter 'method_args'"}), 400
                        # print(f"method_args: {method_args},method: {method}")

                        try:
                            # 调用方法
                            # print(f"方法是: {method}---{method_name}")
                            result = method(**method_args)
                            return jsonify({"result": result})
                        except Exception as e:
                            return jsonify({"error": str(e)}), 500

                    return api_handler

                # 动态注册路由
                app.route(route_path, methods=["POST"], endpoint=f"{provider}_{method_name}")(
                    create_api_handler(provider, dns_class, method_name)
                )
