import logging
import random
import re

from core.utils import check_ip

logger = logging.getLogger('crawler')

SAMPLE_HEADERS = {'Connection': 'keep-alive',
                  'Cache-Control': 'max-age=0',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Encoding': 'gzip, deflate, sdch',
                  'Accept-Language': 'zh-CN,zh;q=0.8',
                  }


class GetFreeProxy(object):
    """
    proxy getter
    """

    def __init__(self, driver, headers):
        self.driver = driver
        self.headers = headers

    def get_proxy(self):
        raise NotImplementedError

    def check_free_proxy(self, proxy_type, ip, port):
        return check_ip(proxy_type, ip, port)


class IP3366(GetFreeProxy):
    def __init__(self, driver, headers):
        super(IP3366, self).__init__(driver, headers)

    def get_proxy(self):
        self.driver.get('http://www.ip3366.net/free/?stype=1&page={}'.format(random.randint(1, 8)))
        # print('http://www.ip3366.net/free/?stype=1&page={}'.format(i))
        rows = self.driver.find_elements_by_tag_name('tr')
        rows = [row.text for row in rows]
        for row in rows:
            matched = re.findall('(\d+\.\d+\.\d+\.\d+)\s+(\d+)', row)
            if not matched:
                continue
            ip, port = matched[0]
            proxy_type = 'https' if 'https' in row.lower() else 'http'
            if self.check_free_proxy(proxy_type, ip, port):
                yield proxy_type, ip, port


class Jiangxianli(GetFreeProxy):
    def __init__(self, driver, headers):
        super(Jiangxianli, self).__init__(driver, headers)

    def get_proxy(self):
        self.driver.get('http://ip.jiangxianli.com/?page={}'.format(random.randint(1, 3)))
        rows = self.driver.find_elements_by_tag_name('tr')
        rows = [row.text for row in rows]
        for row in rows:
            matched = re.findall('(\d+\.\d+\.\d+\.\d+)\s+(\d+)', row)
            if not matched:
                continue
            ip, port = matched[0]
            proxy_type = 'https' if 'https' in row.lower() else 'http'
            if self.check_free_proxy(proxy_type, ip, port):
                yield proxy_type, ip, port


class Kuaidaili(GetFreeProxy):
    def __init__(self, driver, headers):
        super(Kuaidaili, self).__init__(driver, headers)

    def get_proxy(self):
        self.driver.get('https://www.kuaidaili.com/free/inha/{}'.format(random.randint(1, 10)))
        rows = self.driver.find_elements_by_tag_name('tr')
        rows = [row.text for row in rows]
        for row in rows:
            matched = re.findall('(\d+\.\d+\.\d+\.\d+)\s+(\d+)', row)
            if not matched:
                continue
            ip, port = matched[0]
            proxy_type = 'https' if 'https' in row.lower() else 'http'
            if self.check_free_proxy(proxy_type, ip, port):
                yield proxy_type, ip, port


class ProxyFactory(object):
    def __init__(self, driver, headers):
        self.factory = [Kuaidaili(driver, headers), Jiangxianli(driver, headers), IP3366(driver, headers)]

    def get_proxy(self):
        while 1:
            manager = random.choice(self.factory)
            yield manager.get_proxy()
