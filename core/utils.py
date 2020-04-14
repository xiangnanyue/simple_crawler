import psycopg2
import requests
import logging
import random

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
    conn = psycopg2.connect(dbname='crawler', user="postgres", password="123456", host='localhost')
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


def check_ip_bac(proxy_type, ip, port, test_url='http://www.sina.cn', timeout=30):
    proxies = {proxy_type: '{}:{}'.format(ip, port)}
    try:
        r = get_page(test_url, proxies=proxies, timeout=timeout)
        return True
    except Exception as e:
        logger.info(str(e))
        return False


# 返回一个随机的请求头 headers
def getheaders():
    user_agent_list = [ \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    UserAgent=random.choice(user_agent_list)
    headers = {'User-Agent': UserAgent}
    return headers


def check_ip(proxy_type,
             ip,
             port,
             test_url=('http://money.finance.sina.com.cn/corp/go.php/'
                       'vDOWN_BalanceSheet/displaytype/4/stockid/'
                       '600343/ctrl/all.phtml'),
             timeout=10):
    # proxies = {proxy_type: '{}:{}'.format(ip, port)}
    proxies = {"http": "http://"+'{}:{}'.format(ip, port),
               "https": "http://"+'{}:{}'.format(ip, port)}
    headers = getheaders()
    try:
        response = requests.get(url=test_url,
                                proxies=proxies,
                                headers=headers,
                                timeout=8)
        print(response.status_code)
        if response.status_code == 200:
            try:
                with open("./ips.csv", "a") as f:
                    f.write(",".join([proxy_type, ip, port, str(datetime.now())]))
                    f.write("\n")
                # content is of form bytes
                text = response.content
                text = text.decode('GBK')
                text = text.replace('\t\n', '\r\n')
                text = text.replace('\t', ',')
                print(text[:10])
            except Exception as e:
                logger.info(str(e))
            return True
        else:
            return False
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
        '''select * from ippool 
        where status = 0 
        order by failures, update_time desc for update skip locked limit 1''')
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
    data = []
    # todo: debug at create_ippool
    if isinstance(proxy_type, tuple):
        data.append(proxy_type)
        data.append(ip)
        data.append(port)
    else:
        data.append((proxy_type, ip, port))
    for dt in data:
        proxy_type_, ip_, port_ = dt
        logger.info("new ip added {}:{}".format(ip_, port_))
        cur = conn.cursor()
        cur.execute(
            '''insert into ippool(proxy_type, ip, port) values (%s, %s, %s) 
            on conflict (ip) do update set update_time = %s''' % (
                proxy_type_, ip_, str(port_), datetime.now())
        )
        conn.commit()


if __name__ == "__main__":
    conn = connect_db()
    ip = get_ip(conn, 10)
    print(ip)
