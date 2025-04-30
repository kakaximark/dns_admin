import importlib
import pkgutil
from flask import jsonify, request
from cdns.interface import CDNInterface
from config import Config

def load_cdn_classes():
    """
    动态加载所有实现了 CDNInterface 的类
    """
    cdn_classes = {}
    for _, module_name, _ in pkgutil.iter_modules([Config.CDNS_PATH]):
        module = importlib.import_module(f'{Config.CDNS_PACKAGE}.{module_name}')
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, CDNInterface) and attr is not CDNInterface:
                cdn_classes[module_name] = attr
    return cdn_classes

def register_cdn_routes(app):
    """
    根据 CDN 实现动态生成路由
    """
    cdn_classes = load_cdn_classes()

    for provider, cdn_class in cdn_classes.items():
        for method_name in dir(CDNInterface):
            method = getattr(CDNInterface, method_name, None)
            if callable(method) and getattr(method, "__isabstractmethod__", False):
                route_path = f"/cdn/{provider}/{method_name}"

                def create_api_handler(provider_name, cdn_class, method_name):
                    def api_handler():
                        # 获取客户端初始化参数
                        client_param = request.json.get("client_param", {})
                        if not client_param:
                            return jsonify({"error": "Missing 'client_param' for CDN client initialization"}), 400

                        # 初始化 CDN 客户端
                        try:
                            client = cdn_class(**client_param)
                        except TypeError as e:
                            return jsonify({"error": f"Invalid 'client_param': {str(e)}"}), 400

                        # 获取方法参数
                        method_args = request.json.get("method_args", {})
                        method = getattr(client, method_name)

                        try:
                            # 调用方法
                            result = method(**method_args)
                            return jsonify({"result": result})
                        except Exception as e:
                            return jsonify({"error": str(e)}), 500

                    return api_handler

                # 动态注册路由
                app.route(route_path, methods=["POST"], endpoint=f"{provider}_{method_name}")(
                    create_api_handler(provider, cdn_class, method_name)
                )
