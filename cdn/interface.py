from abc import ABC, abstractmethod

class CDNInterface(ABC):
    """
    CDN 接口定义
    """

    @abstractmethod
    def verify_owner(self, domain_name):
        pass

    @abstractmethod
    def get_verifies(self, domain_name):
        pass

    @abstractmethod
    def create_domain(self, domain_name, business_type, sources, service_area):
        pass

    @abstractmethod
    def refresh_cache(self, urls):
        pass

    @abstractmethod
    def get_domain_status(self, domain_name):
        pass
