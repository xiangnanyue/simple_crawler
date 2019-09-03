import psycopg2
import requests
import logging
from datetime import datetime
from collections import namedtuple

IP = namedtuple("IP", "id failures update_time ip port proxy_type")


def create_logger(logger_name):
    # create logger with 'crawler'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('crawler.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    logger.addHandler(consoleHandler)
    return logger


logger = create_logger('crawler')


def connect_db():
    logger.info('create connection pool')
    conn = psycopg2.connect(dbname='crawler', host='localhost')
    return conn


def create_ippool_table(conn):
    logger.info('create ippool table')
    cur = conn.cursor()
    cur.execute(
        '''create table if not exists ippool (
        id serial primary key ,
        ip text unique, 
        port text,
        proxy_type text,
        failures int default 0,
        update_time timestamp default now(),
        status int default 0)''')
    conn.commit()


def check_ip(proxy_type, ip, port, test_url='http://www.sina.cn', timeout=30):
    proxies = {proxy_type: '{}:{}'.format(ip, port)}
    try:
        r = get_page(test_url, proxies=proxies, timeout=timeout)
        return True
    except Exception as e:
        logger.info(str(e))
        return False


def get_page(url, proxies=None, params=None, timeout=30, headers=None):
    page = requests.request(method='get', url=url, proxies=proxies, params=params, timeout=timeout, headers=headers)
    return page.content.decode('utf8')


def str2header(s):
    d = {}
    for line in s.strip().split('\n'):
        k, v = line.strip().split(':', 1)
        d[k] = v.strip()
    return d


def get_ip(conn, timeout=30):
    cur = conn.cursor()
    cur.execute(
        '''select * from ippool where status = 0 order by failures, update_time desc for update skip locked limit 1''')
    id, ip, port, proxy_type, failures, update_time, status = cur.fetchone()
    Ip = IP(id, failures, update_time, ip, port, proxy_type)
    if check_ip(proxy_type, ip, port, timeout=timeout):
        cur.execute('''update ippool set status=1 where id = %s''', (id,))
        conn.commit()
        return Ip
    else:
        put_ip(conn, Ip)
        return get_ip(conn, timeout)


def put_ip(conn, ip):
    cur = conn.cursor()
    cur.execute('''update ippool set status=0, failures = %s where id = %s''', (ip.failures + 1, ip.id))
    conn.commit()


def switch_ip(conn, ip, timeout=30):
    put_ip(conn, ip)
    return get_ip(conn, timeout)


def add_new_ip(conn, proxy_type, ip, port):
    logger.info("new ip added {}:{}".format(ip, port))
    cur = conn.cursor()
    cur.execute(
        '''insert into ippool(proxy_type, ip, port) values (%s, %s,%s) on conflict (ip) do update set update_time = %s''',
        (proxy_type, ip, port, datetime.now()))
    conn.commit()
