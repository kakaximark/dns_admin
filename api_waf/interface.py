from abc import ABC, abstractmethod

class WAFInterface(ABC):
    """
    WAF 接口定义
    """
    @abstractmethod
    def manage_waf(self, domain_name, action, record_type, record_value, ttl=300):
        """
        管理 WAF 记录 (创建或更新)
        """
        pass

    @abstractmethod
    def create_rules(self, zone_id):
        """
        列出 WAF 记录
        """
        pass
  
    @abstractmethod
    def rules_lists(self, zone_id):
        """
        列出 WAF 记录
        """
        pass
    
    @abstractmethod
    def list_items(self, zone_id):
        """
        列出 WAF 记录
        """
        pass
    
    @abstractmethod
    def create_items(self, zone_id):
        """
        列出 WAF 记录
        """
        pass
