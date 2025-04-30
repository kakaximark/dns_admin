from abc import ABC, abstractmethod

class DNSInterface(ABC):
    """
    DNS 接口定义
    """

    @abstractmethod
    def manage_dns(self, domain_name, action, record_type, record_value, ttl=300):
        """
        管理 DNS 记录 (创建或更新)
        :param domain_name: 域名
        :param action: 操作类型 ('create', 'update')
        :param record_type: 记录类型 (如 'A', 'CNAME', 'TXT')
        :param record_value: 记录值
        :param ttl: DNS 生存时间
        """
        pass

    @abstractmethod
    def list_dns(self, domain_name):
        """
        列出 DNS 记录
        :param domain_name: 域名
        :return: 包含记录的列表
        """
        pass

    @abstractmethod
    def list_dns_record(self, domain_name):
        """
        列出域名 DNS 记录
        :param domain_name: 域名
        :return: 包含记录的列表
        """
        pass

    @abstractmethod
    def update_dns_record(self, domain_name):
        """
        更新域名 DNS 记录
        :param dns_record_id: dns_record_id
        :param zone_id: zone_id
        :return: 包含记录的列表
        """
        pass

    @abstractmethod
    def create_dns_record(self, domain_name):
        """
        创建域名
        :param domain_name: 要创建的域名
        :param content: 解析记录
        :param type: 解析类型
        :return: 创建结果
        """
        pass

    @abstractmethod
    def list_nsserver(self, zone_id):
        """
        删除 DNS 记录
        :param zone_id: 要删除的记录 ID
        """
        pass

    @abstractmethod
    def del_dns(self, domain_name):
        """
        删除 DNS 记录
        :param zone_id: 要删除的记录 ID
        """
        pass

    @abstractmethod
    def create_zone(self, domain_name):
        """
        添加 域名
        :param zone_id: 要删除的记录 ID
        """
        pass

    @abstractmethod
    def del_zone(self, domain_name):
        """
        添加 域名
        :param zone_id: 要删除的记录 ID
        """
        pass

    @abstractmethod
    def record_check(self, domain_name):
        """
        检查 DNS 记录
        :param zone_id: 要检查的记录 ID
        """
        pass
    
    @abstractmethod
    def ns_check(self, domain_name):
        """
        检查 NS 记录
        :param zone_id: 要检查的记录 ID
        """
        pass

    @abstractmethod
    def active_status(self, domain_name):
        """
        检查 NS 记录
        :param zone_id: 要检查的记录 ID
        """
        pass
    
    @abstractmethod
    def verify_record(self, domain_name):
        """
        检查 NS 记录
        :param zone_id: 要检查的记录 ID
        """
        pass

    @abstractmethod
    def get_domain_expiry(self, domain_name):
        """
        检查 NS 记录
        :param zone_id: 要检查的记录 ID
        """
        pass

    @abstractmethod
    def cache_purge(self, domain_name):
        """
        检查 NS 记录
        :param zone_id: 要检查的记录 ID
        """
        pass
    
    @abstractmethod
    def get_detail_domain(self, domain_name):
        """
        检查 NS 记录
        :param zone_id: 要检查的记录 ID
        """
        pass