import nose
import unittest
import urllib
import httplib
import json
import subprocess
import threading
import time


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.SLB_ip = "47.95.167.246"
        self.port = 8081
        self.AuthHost = "api.cloudstorage.com"
        self.thread_count = 500

        self.get_media_spend_list = []
        self.get_compute_spend_list = []
        self.submit_compute_spend_list = []
        self.add_media_interface_spend_list = []

        self.response = []

        self.start_time = ""
        self.end_time = ""

    def out_log(self, out_path, out_list):
        with open(out_path, 'w') as out:
            out.write('concurrency: %s, max: %s, min: %s, avarage: %s\n' %
                      (self.thread_count, max(out_list), min(out_list), float(sum(out_list)/len(out_list))))

    def out_log_pk(self, thread_count, out_path, out_list):
        count_fail = 0
        # print("out_list:%s" % out_list)
        with open(out_path, 'w') as out:
            total = len(self.response)
            for i in range(total):
                if not self.response[i] in "OK":
                    count_fail += 1
            if out_list:
                out.write('concurrency: %s, failure rate: %s%%, max: %s, min: %s, avarage: %s, start time: %s, end time: %s\n' %
                          (thread_count, (count_fail * 100 / total), max(out_list), min(out_list),
                           float(sum(out_list) / len(out_list)), self.start_time, self.end_time))
            else:
                out.write('concurrency: %s, failure rate: %s%%, max: --, min: --, avarage: --, start time: %s, end time: %s\n' %
                          (thread_count, (count_fail * 100 / total), self.start_time, self.end_time))


