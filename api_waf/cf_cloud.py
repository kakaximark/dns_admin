import logging,time,json
from datetime import datetime
from cloudflare import Cloudflare
from api_waf.interface import WAFInterface

logger = logging.getLogger(__name__)

class Cloudflarewaf(WAFInterface):
    def __init__(self, **kwargs):
        """
        Initialize Cloudflare waf client
        Args:
            **kwargs: Must contain:
                api_token (str): Cloudflare API Token for authentication
        """
        api_token = kwargs.get('api_token')
        if not api_token:
            raise ValueError("API token is required")
        if not isinstance(api_token, str):
            raise TypeError("API token must be a string")
        
        try:
            self.client = Cloudflare(api_token=api_token)
            logger.info("Cloudflare waf client initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudflare client: {str(e)}")
            raise

    def manage_waf(self, **kwargs):
        pass
            
    def create_rules(self, **kwargs):
        """List rulesets phases"""
        zone_id = kwargs.get("zone_id")
        ruleset_id = kwargs.get("ruleset_id")
        if not all([zone_id,ruleset_id]):
            raise ValueError("zone_id and ruleset_id is required")
        if not isinstance(zone_id, str):
            raise TypeError("zone_id must be a string")
        
        result_info = self._if_rules_exist(zone_id=zone_id, ruleset_phase="http_request_firewall_custom")
        if not result_info["data"]:
            try:
                self.client.rulesets.rules.create(**kwargs)
                return  {
                    "code": 200,
                    "massage": "Rules created successfully",
                    "data": True
                }
            except Exception as e:
                logger.error(f"Failed to create rulesets rules: {str(e)}")
                return  {
                    "code": 500,
                    "massage": f"Failed to create rules: {str(e)}",
                    "data": False
                }

        return result_info

    def _if_rules_exist(self, **kwargs):
        """Check rulesets phases"""
        zone_id = kwargs.get("zone_id")
        if not all([zone_id]):
            raise ValueError("zone_id is required")
        if not isinstance(zone_id, str):
            raise TypeError("zone_id must be a string")
        
        try:
            response = self.client.rulesets.phases.get(**kwargs)
            if response and hasattr(response, 'rules') and response.rules:
                rule_name = response.rules[0].description
                if rule_name == "BlackList":
                    return {
                        "code": 200,
                        "massage": "Blacklist is already exist!",
                        "data": True
                    }
                else:
                    return {
                        "code": 404,
                        "massage": "Blacklist is not exist, please create rules first!",
                        "data": False
                    }
            return {
                "code": 404,
                "massage": "No rules found",
                "data": False
            }
        except Exception as e:
            logger.error(f"Failed to list rulesets phases: {str(e)}")
            return {
                "code": 500,
                "message": "Error checking rules existence",
                "data": False
            }

    def rules_lists(self, **kwargs):
        try:
            response = self.client.rules.lists.list(**kwargs)
        except Exception as e:
            logger.error(f"Failed to list rules lists: {str(e)}")
            return {
                "code": 500,
                "message": f"Error checking rules lists: {str(e)}",
                "data": False
            }

    def _create_lists(self, **kwargs):
        """Create lists"""
        account_id = kwargs.get("account_id")
        name = kwargs.get("name")
        if not all([account_id,name]):
            raise ValueError("account_id and name is required")
        if not isinstance(account_id, str):
            raise TypeError("account_id must be a string")

        keys_to_remove = ["zone_id","body"]
        for key in keys_to_remove:
            kwargs.pop(key, None)

        try:
            print(kwargs)
            response = self.client.rules.lists.create(**kwargs)
            logger.info(f"{name} list created successfully")
            return  {
                "code": 200,
                "massage": f"{name} List created successfully!",
                "data": response.id
            }        
        except Exception as e:
            logger.error(f"Failed to create {name} list rules: {str(e)}")
            return  {
                "code": 500,
                "massage": f"{name} Failed to create rules: {str(e)}",
                "data": False
            }

    def _get_list_id(self, **kwargs):
        account_id = kwargs.get("account_id")
        name = kwargs.get("name")
        if not all([account_id,name]):
            raise ValueError("account_id and name is required")
        if not isinstance(account_id, str):
            raise TypeError("account_id must be a string")
        
        try:
            response = self.client.rules.lists.list(account_id=account_id)
            result = (item.id for item in response.result if item.name == name)
            for i in result:
                list_id = i
                
            return list_id
        except Exception as e:
            return str(e)

    def create_items(self, **kwargs):
        '''
        1.判断lists是否存在,不存在则创建
        2.添加items
        '''
        """Create lists"""
        account_id = kwargs.get("account_id")
        kind = kwargs.get("kind")
        info = kwargs.get("info")
        body = kwargs.get("body")
        del kwargs["info"]
        if not all([account_id,kind,info,body]):
            raise ValueError("account_id and kind and info and body is required")
        if not isinstance(account_id, str):
            raise TypeError("account_id must be a string")

        results = []
        for items in info:
            new_name = items["name"].replace('.','_').replace('-','_') + "_block"
            zone_id = items["zone_id"]
            kwargs["name"] = new_name
            kwargs["zone_id"] = zone_id
            create_result = self._create_lists(**kwargs)
            print(create_result)

        for items in info:
            new_name = items["name"].replace('.','_').replace('-','_') + "_block"
            zone_id = items["zone_id"]
            kwargs["name"] = new_name
            kwargs["zone_id"] = zone_id
            list_id = self._get_list_id(**kwargs)
            keys_to_remove = ["zone_id","name","kind"]
            for key in keys_to_remove:
                kwargs.pop(key, None)
                
            kwargs["list_id"] = list_id
            print(kwargs)
            try:
                response = self.client.rules.lists.items.create(**kwargs)
                print(response)
                results.append({
                    "code": 200,
                    "massage": "items created successfully",
                    "data": True
                })
            except Exception as e:
                logger.error(f"Failed to create items rules: {str(e)}")
                results.append({
                    "code": 500,
                    "massage": f"Failed to create items: {str(e)}",
                    "data": False
                })
        
        return {
            "code": 200,
            "massage": "All items processed",
            "data": results
        }

    def list_items(self, **kwargs):
        account_id = kwargs.get("account_id")
        name = kwargs.get("name")
        new_name = name.replace('.','_') + "_block"
        kwargs['name'] = new_name
        if not all([account_id,name]):
            raise ValueError("account_id and name is required")
        if not isinstance(account_id, str):
            raise TypeError("account_id must be a string")

        create_result = self._create_lists(**kwargs)
        if create_result["code"] == 200:
            list_id = create_result["data"]
        else:
            list_id = self._get_list_id(**kwargs)

        try:
            all_data = []
            response = self.client.rules.lists.items.list(account_id=account_id,list_id=list_id)
            current_data = response.result
            for data in current_data:
                data_info = {
                    "id": data.id,
                    "ip": data.ip
                }
                all_data.append(data_info)
            
            return {
                "code": 200,
                "message": "Operation successful",
                "data": all_data
            }
                
        except Exception as e:
            logger.error(f"Failed to list items: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": False
            }