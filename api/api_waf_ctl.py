import importlib
import pkgutil
from flask import jsonify, request
from api_waf.interface import WAFInterface
from config import Config

def load_waf_classes():
    """
    动态加载所有实现了 wafInterface 的类
    """
    waf_classes = {}
    for _, module_name, _ in pkgutil.iter_modules([Config.WAF_PATH]):
        module = importlib.import_module(f'{Config.WAF_PACKAGE}.{module_name}')
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, WAFInterface) and attr is not WAFInterface:
                waf_classes[module_name] = attr
    return waf_classes

def register_waf_routes(app):
    """
    根据 waf 实现动态生成路由
    """
    waf_classes = load_waf_classes()
    # 新增: 获取所有waf提供商列表的路由
    @app.route('/waf/providers', methods=['GET'])
    def get_waf_providers():
        providers = []
        for provider, waf_class in waf_classes.items():
            # 获取类中的可用方法
            methods = []
            for method_name in dir(WAFInterface):
                method = getattr(WAFInterface, method_name, None)
                if callable(method) and getattr(method, "__isabstractmethod__", False):
                    methods.append(method_name)
            
            providers.append({
                'name': provider,
                'class': waf_class.__name__,
                'methods': methods
            })
        return jsonify({
            'code': 200,
            'message': 'waf providers retrieved successfully',
            'data': providers
        })

    for provider, waf_class in waf_classes.items():
        for method_name in dir(WAFInterface):
            method = getattr(WAFInterface, method_name, None)
            if callable(method) and getattr(method, "__isabstractmethod__", False):
                route_path = f"/waf/{provider}/{method_name}"

                def create_api_handler(provider_name, waf_class, method_name):
                    def api_handler():
                        # 获取客户端初始化参数
                        # client_param = request.json.get("client_param", {})
                        # print(client_param)
                        client_param = Config.client_param
                        if not client_param:
                            return jsonify({"error": "Missing 'client_param' for waf client initialization"}), 400
                        
                        # 验证必要参数
                        if "api_token" not in client_param:
                            return jsonify({"error": "Missing required parameter 'api_token'"}), 400
                        
                        # 初始化 waf 客户端
                        try:
                            client = waf_class(**client_param)
                            # client = waf_class()
                        except Exception as e:
                            return jsonify({"error": f"Failed to initialize waf client: {str(e)}"}), 400

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
                    create_api_handler(provider, waf_class, method_name)
                )
