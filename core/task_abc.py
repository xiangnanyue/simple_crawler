from .utils import switch_ip, get_ip
import time
import json
import random


class Task(object):
    def __init__(self, conn, task_name, use_proxy, logger, sleep=1):
        self._conn = conn
        self._cur = conn.cursor()
        self._task_name = task_name
        self._use_proxy = use_proxy
        self._ip = get_ip(conn) if use_proxy else None
        self._proxy = {self._ip.proxy_type: '{}:{}'.format(self._ip.ip, self._ip.port)}
        print(self._proxy)
        self._logger = logger
        self._sleep = sleep
        self._logger.info('using proxy: {}'.format(json.dumps(self._proxy)))

    def get_task_id(self):
        raise NotImplementedError

    def task_finished(self, task_id):
        raise NotImplementedError

    def task_failed(self, task_id):
        raise NotImplementedError

    def process_task(self, task_id):
        raise NotImplementedError

    def start(self):
        task_id = self.get_task_id()
        while task_id is not None:
            try:
                self.process_task(task_id)
                self.task_finished(task_id)
            except Exception as e:
                self._logger.error(str(e))
                self.task_failed(task_id)
                if self._use_proxy:
                    old_proxy = {'http': '{}:{}'.format(self._ip.ip, self._ip.port)}
                    self._ip = switch_ip(self._conn, self._ip)
                    new_proxy = {'http': '{}:{}'.format(self._ip.ip, self._ip.port)}
                    self._proxy = new_proxy
                    self._logger.info("switching proxy from {} to {}".format(old_proxy, new_proxy))
            task_id = self.get_task_id()
            time.sleep(self._sleep + random.random() * self._sleep/5)
        self._logger.info(self._task_name + " is finished!")
