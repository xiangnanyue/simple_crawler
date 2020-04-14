from core.utils import create_ippool_table, connect_db, add_new_ip
from ip_proxy import ProxyFactory, SAMPLE_HEADERS
from selenium import webdriver
import logging
import os

if __name__ == '__main__':
    conn = connect_db()
    create_ippool_table(conn)
    print(os.path.dirname(__file__))
    path = '/home/xiangnanyue/Downloads/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
    driver = webdriver.PhantomJS(executable_path=path)
    proxy_engine = ProxyFactory(driver, SAMPLE_HEADERS)
    while 1:
        try:
            for tup in proxy_engine.get_proxy():
                proxy_type, ip, port = tup
                add_new_ip(conn, proxy_type, ip, port)
        except Exception as e:
            logging.error(str(e))
