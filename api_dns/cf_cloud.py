import logging,time,json,whois,requests
import dns.resolver
from datetime import datetime
from cloudflare import Cloudflare
from api_dns.interface import DNSInterface
from config import Config

logger = logging.getLogger(__name__)

class CloudflareDNS(DNSInterface):
    def __init__(self, **kwargs):
        """
        Initialize Cloudflare DNS client
        Args:
            **kwargs: Must contain:
                api_token (str): Cloudflare API Token for authentication
        """
        #验证 api_token 参数
        api_token = kwargs.get('api_token')
        if not api_token:
            raise ValueError("API token is required")
        if not isinstance(api_token, str):
            raise TypeError("API token must be a string")
        
        try:
            self.client = Cloudflare(api_token=api_token)
            logger.info("Cloudflare DNS client initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudflare client: {str(e)}")
            raise
    
    def get_detail_domain(self, **kwargs):
        pass
    
    def list_dns(self, max_retries=3):
        """List all DNS zones"""
        try:
            all_data = []
            page = 1
            per_page = 50
            retry_count = 0

            while True:
                try:
                    response = self.client.zones.list(page=page, per_page=per_page)
                    retry_count = 0
                    current_data = response.result
                    current_page_info = response.result_info
                    for zone in current_data:
                        zone_info = {
                            "id": zone.id,
                            "name": zone.name,
                            "status": zone.status,
                            "paused": zone.paused,
                            "type": zone.type,
                            "development_mode": zone.development_mode,
                            "name_servers": zone.name_servers,
                            "original_name_servers": zone.original_name_servers,
                            "created_on": str(zone.created_on),
                            "modified_on": str(zone.modified_on)
                        }
                        all_data.append(zone_info)

                    if page >= current_page_info.total_pages:
                        break

                    page += 1

                except Exception as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        raise Exception(f"Max retries exceeded: {str(e)}")
                        
                    logger.warning(f"Retry {retry_count} for page {page}")
                    sleep_time = 2 ** retry_count
                    time.sleep(sleep_time)
       
            return {
                "code": 200,
                "message": "Zones retrieved successfully",
                "total": len(all_data),
                "data": all_data
            }
        except Exception as e:
            logger.error(f"Failed to list zones: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def list_dns_record(self, **kwargs):
        """List all DNS record"""
        try:
            all_data = []
            page = 1
            per_page = 50
            retry_count = 0
            max_retries=3

            while True:
                try:
                    logger.info(f"Requesting page {page}")
                    response = self.client.dns.records.list(page=page, per_page=per_page, **kwargs)
                    retry_count = 0
                    current_data = response.result
                    current_page_info = response.result_info

                    for record in current_data:
                        record_info = {
                            "id": record.id,
                            "name": record.name,
                            "type": record.type,
                            "content": record.content,
                            "proxiable": record.proxiable,
                            "proxied": record.proxied,
                            "ttl": record.ttl,
                            "created_on": str(record.created_on),
                            "modified_on": str(record.modified_on)
                        }
                        all_data.append(record_info)

                    if page >= current_page_info.total_pages:
                        break

                    page += 1
                
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Retry {retry_count} for page {page} due to error: {str(e)}")
                    if retry_count > max_retries:
                        logger.error(f"Max retries exceeded for page {page}")
                        raise Exception(f"Max retries exceeded: {str(e)}")
                        
                    time.sleep(1)
            
            return {
                'code': 200,
                'message': 'Success',
                'total': len(all_data),
                'data': all_data
            }
        
        except Exception as e:
            logger.error(f"Failed to get data: {str(e)}")
            return {
                'code': 500,
                'message': str(e),
                'data': None
            }

    def create_dns_record(self, zone_id, **kwargs):
        """Create a new DNS Record"""
        # zone_id = "ed7672f96562b6f993928d3be2b63ffc"
        if not zone_id:
            raise ValueError("zone_id is required")
        if not isinstance(zone_id, str):
            raise TypeError("zone_id must be a string")
        isBindNginx = kwargs.get('isBindNginx')
        print(isBindNginx)
        print(type(isBindNginx))
        if isBindNginx:
            bind_args = kwargs.get('bind_args')
            headers = {"Content-Type": "application/json"}
            url = Config.BIND_NGINX_API
            try:
                response = requests.post(url, data=json.dumps(bind_args), headers=headers, timeout=5)
                logger.info(f"请求成功: {response}")
                # payload = {
                #     "businessId": bind_args.get('businessId'),
                #     "env": bind_args.get('env'),
                #     "domain": bind_args.get('domain'),
                #     "sourceUrl": bind_args.get('sourceUrl'),
                #     "type": bind_args.get('type')
                # }
            except requests.exceptions.Timeout:
                logger.error("请求超时！")
        required_params = ['type', 'name', 'content']
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"{param} is required")

        try:
            keys_to_remove = ["isBindNginx", "bind_args"]
            for key in keys_to_remove:
                kwargs.pop(key, None)
            response = self.client.dns.records.create(
                zone_id=zone_id,
                **kwargs
            )
            record_info = {
                "id": response.id,
                "name": response.name,
                "type": response.type,
                "content": response.content,
                "proxiable": response.proxiable,
                "proxied": response.proxied,
                "ttl": response.ttl,
                "created_on": str(response.created_on),
                "modified_on": str(response.modified_on)
            }
            return {
                "code": 200,
                "message": "Zone created successfully",
                "data": record_info
            }
        except Exception as e:
            logger.error(f"Failed to create zone: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def del_dns(self, **kwargs):
        """Delete a DNS Record"""
        try:
            self.client.dns.records.delete(**kwargs)
            return {
                "code": 200,
                "message": "Zone deleted successfully",
                "data": None
            }
        except Exception as e:
            logger.error(f"Failed to delete zone: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def list_nsserver(self, **kwargs):
        """List nameservers for a zone"""
        zone_id = kwargs.get('zone_id')
        if not zone_id:
            raise ValueError("zone_id is required")
        if not isinstance(zone_id, str):
            raise TypeError("zone_id must be a string")
   
        try:
            zone = self.client.zones.get(zone_id=zone_id)
            return {
                "code": 200,
                "message": "Nameservers retrieved successfully",
                "data": {
                    "nameservers": zone.name_servers
                }
            }
        except Exception as e:
            logger.error(f"Failed to get nameservers: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def ns_check(self, **kwargs):
        """Check nameservers for a zone"""
        zone_id = kwargs.get('zone_id')
        if not zone_id:
            raise ValueError("zone_id is required")
        if not isinstance(zone_id, str):
            raise TypeError("zone_id must be a string")
        
        domain_info = self._get_zone_details(**kwargs)
        domain_name = domain_info["name"]
        domain_ns = domain_info["name_servers"]
        myResolver = dns.resolver.Resolver()
        myResolver.nameservers = ['8.8.8.8','8.8.4.4']
        myAnswers = myResolver.resolve(domain_name, "NS")
        nameservers = [str(answer) for answer in myAnswers]
        # print(s.rstrip('.') for s in nameservers)
        if sorted(domain_ns) == sorted(s.rstrip('.') for s in nameservers):
            result = True
            result_info = {
                "name": domain_name,
                "name_servers": domain_ns,
                "vanity_name_servers": nameservers,
                "status": result
            }
            return {
                "code": 200,
                "message": "The domain NS is completed",
                "data": result_info
            }
        else:
            return {
                "code": 500,
                "messsage": "The domain NS is not yet",
                "data": None
            }

    def update_dns_record(self, **kwargs):
        """Update a new DNS Record"""
        try:
            self.client.dns.records.edit(**kwargs)

            return {
                "code": 200,
                "message": "Zone Update successfully",
                "data": None
            }
        except Exception as e:
            logger.error(f"Failed to update zone: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def manage_dns(self, domain_name, action, record_type, record_value, ttl=300):
        """Manage DNS records"""
        try:
            zone_id = self._get_zone_id(domain_name)
            if action == 'create':
                response = self.client.zones.dns_records.post(zone_id, data={
                    'type': record_type,
                    'name': domain_name,
                    'content': record_value,
                    'ttl': ttl
                })
            elif action == 'update':
                # 获取记录ID并更新
                records = self.client.zones.dns_records.get(zone_id)
                for record in records:
                    if record['name'] == domain_name and record['type'] == record_type:
                        response = self.client.zones.dns_records.put(zone_id, record['id'], data={
                            'type': record_type,
                            'name': domain_name,
                            'content': record_value,
                            'ttl': ttl
                        })
                        break
            return {
                "code": 200,
                "message": f"DNS record {action}d successfully",
                "data": response
            }
        except Exception as e:
            logger.error(f"Failed to {action} DNS record: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def create_zone(self, **kwargs):
        """create a new zone"""
        try:
            zone = self.client.zones.create(**kwargs)
            record_info = {
                "id": zone.id,
                "name": zone.name,
                "type": zone.type,
                "status": zone.status,
                "paused": zone.paused,
                "name_servers": zone.name_servers,
                "original_name_servers": zone.original_name_servers,
                "account": {
                    "id": zone.account.id,
                    "name": zone.account.name
                },
                "plan": zone.plan,
                "created_on": str(zone.created_on),
                "modified_on": str(zone.modified_on)
            }
            return {
                "code": 200,
                "message": "Zone created successfully",
                "data": record_info
            }
        except Exception as e:
            logger.error(f"Failed to create zone: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def del_zone(self, **kwargs):
        try:
            zone = self.client.zones.delete(**kwargs)
            record_info = {
                "id": zone.id
            }
            return {
                "code": 200,
                "message": "Zone created successfully",
                "data": record_info
            }
        except Exception as e:
            logger.error(f"Failed to create zone: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": False
            }

    def record_check(self, **kwargs):
        """Check DNS record for a zone"""
        record_type = kwargs.get('type')
        record_content = kwargs.get('content')
        record_name = kwargs.get('name')
        proxied = kwargs.get('proxied')
        if not all([record_type,record_content,record_name]):
            raise ValueError("type and content is required")
        if not isinstance(record_type, str):
            raise TypeError("type must be a string")
        
        try:
            if proxied:
                def is_cloudflare_proxied(url):
                    try:
                        # 确保 URL 以 https:// 开头
                        if not url.startswith("https://") and not url.startswith("http://"):
                            url = "https://" + url
                        elif url.startswith("http://"):
                            # 如果是 http:// 开头，尝试替换为 https://，更安全
                            url = url.replace("http://", "https://", 1) # 只替换一次，避免替换掉 url 中间部分的 "http://"
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                        response = requests.get(url, headers=headers, timeout=5)
                        response.raise_for_status()

                        # 检查 Cloudflare 特有的 HTTP 头部
                        if 'server' in response.headers and response.headers['server'] == 'cloudflare':
                            return True
                        elif 'cf-ray' in response.headers:
                            return True
                        elif 'cf-cache-status' in response.headers:  # 检查 CF-Cache-Status 头部
                            return True
                        else:
                            return False
                    except requests.exceptions.RequestException as e:
                        print(f"请求失败: {e}")
                        return False
                
                result = is_cloudflare_proxied(record_name)
                return {
                    "code": 200,
                    "message": "Zone active check successfully",
                    "data": result
                }
            else:   
                result = dns.resolver.resolve(record_name, record_type)
                print(result)
                for record in result:
                    logger.info(f"CNAME Record: {record_name} -> {record.target}")
                    record_cname = str(record.target)
                    content_new = record_cname

                if record_content in content_new:
                    return {
                        "code": 200,
                        "message": "Zone active check successfully",
                        "data": True
                    }
                else:
                    return {
                        "code": 200,
                        "message": f"{record_content} is not {content_new}",
                        "data": False
                    }
        except Exception as e:
            return {
                "code": 200,
                "message": f"Zone active check false: str{e}",
                "data": False
            }

    def active_status(self, **kwargs):
        try:
            response = self.client.zones.get(**kwargs)
            return {
                "code": 200,
                "message": "Zone active check successfully",
                "data": response.status
            }
        except Exception as e:
            logger.error(f"Failed to check zone: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def verify_record(self, **kwargs):
        """Verify DNS record for a zone"""
        zone_id = kwargs.get('zone_id')
        dns_record_id = kwargs.get('dns_record_id')
        content = kwargs.get('content')
        if not all([zone_id, dns_record_id, content]):
            raise ValueError("zone_id and dns_record_id and content is required")
        if not isinstance(zone_id, str):
            raise TypeError("zone_id must be a string")
        
        if "content" in kwargs:
            try:
                del kwargs["content"]
                record_info = self._get_record_details(**kwargs)
                if record_info["content"] == content:
                    return {
                        "code": "200",
                        "message": "Record is successfully",
                        "data": True
                    }
                else:
                    return {
                        "code": "200",
                        "message": "Record is not ready",
                        "data": False
                    }
            except Exception as e:
                logger.error(f"Failed to verify zone: {str(e)}")
                return {
                    "code": 500,
                    "message": str(e),
                    "data": None
                }

    def get_domain_expiry(self, **kwargs):
        """Get domain expiration date"""
        domain_name = kwargs.get('name')
        if not domain_name:
            raise ValueError("name is required")
        if not isinstance(domain_name, str):
            raise TypeError("name must be a string")

        try:
            domain_info = whois.whois(domain_name)
            expiry_date = domain_info.expiration_date
            if isinstance(expiry_date, list):
                expiry_date = expiry_date[0]
                
            return {
                "code": 200,
                "message": "Domain expiration date get successfully",
                "data": expiry_date
            }
        except Exception as e:
            logger.error(f"Failed to get domain: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": False
            }

    def cache_purge(self, **kwargs):
        """Get params"""
        zone_id = kwargs.get('zone_id')
        type = kwargs.get('type')
        if type not in kwargs:
            raise ValueError(f"{type} is required")
        if not zone_id:
            raise ValueError("zone_id is required")
        if not isinstance(zone_id, str):
            raise TypeError("zone_id must be a string")
        
        try:
            del kwargs["type"]
            response = self.client.cache.purge(**kwargs)
            result_info = {
                "id": response.id,
                "result": "success"
            }
            return {
                "code": 200,
                "message": "Domain expiration date get successfully",
                "data": result_info
            }
        except Exception as e:
            logger.error(f"Failed to purge cache: {str(e)}")
            return {
                "code": 500,
                "message": str(e),
                "data": None
            }

    def _get_zone_details(self, **kwargs):
        """Helper method to get zone ID from domain name"""
        try:
            response = self.client.zones.get(**kwargs)
            zone_info = {
                "id": response.id,
                "name": response.name,
                "status": response.status,
                "paused": response.paused,
                "type": response.type,
                "name_servers": response.name_servers
            }
            return zone_info
        except Exception as e:
            logger.error(f"Failed to get zone info: {str(e)}")
            return str(e)

    def _get_record_details(self, **kwargs):
        """Helper method to get record ID from domain name"""
        try:
            response = self.client.dns.records.get(**kwargs)
            record_info = {
                "id": response.id,
                "name": response.name,
                "type": response.type,
                "content": response.content
            }
            return record_info
        except Exception as e:
            logger.error(f"Failed to get record info: {str(e)}")
            return str(e)
