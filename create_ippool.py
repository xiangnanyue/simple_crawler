from core.utils import create_ippool_table, connect_db, add_new_ip
from ip_proxy import ProxyFactory, SAMPLE_HEADERS
from selenium import webdriver
import logging

if __name__ == '__main__':
    conn = connect_db()
    create_ippool_table(conn)
    path = 'phantomjs'
    driver = webdriver.PhantomJS(executable_path=path)
    proxy_engine = ProxyFactory(driver, SAMPLE_HEADERS)
    while 1:
        try:
            for proxy_type, ip, port in proxy_engine.get_proxy():
                add_new_ip(conn, proxy_type, ip, port)
        except Exception as e:
            logging.error(str(e))