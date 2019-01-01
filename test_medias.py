import nose
import unittest
import urllib
import httplib
import json
import subprocess
import threading
import time
import datetime
import requests
import test_base


class MediasTest(test_base.BaseTest):

    def setUp(self):
        test_base.BaseTest.setUp(self)
        self.thread_count = 1000

    def get_medias(self, token, timestamp, direction, page_size, page_index):
        params = urllib.urlencode(
            {'timestamp': timestamp, 'direction': direction,
             'page_size': page_size, 'page_index': page_index})
        headers = {"Token": token, "accept": "application/json",
                   "AuthHost": self.AuthHost}
        conn = httplib.HTTPConnection(self.SLB_ip, self.port)
        get_url = "/v1/medias/?"
        conn.request("GET", get_url, params, headers)
        response = conn.getresponse()
        data = response.read()
        response_get_medias = json.loads(data)
        conn.close()

        #print "\n%s" % response_get_medias

    def get_media_with_curl(self, token, timestamp, direction, page_size,
                            page_index):
        cmd = 'curl -X GET "http://%s:%s/v1/medias/?timestamp=%s&direction=%s&page_size=%s&page_index=%s" -H "accept: application/json" -H "AuthHost: api.cloudstorage.com" -H "Token: %s "' % (
        self.SLB_ip, self.port, timestamp, direction, page_size, page_index, token)

        start_time = time.time()
        child = subprocess.call(cmd, shell=True)
        time_spend = time.time() - start_time

        self.get_media_spend_list.append(time_spend)

    def get_medias_request(self, token, timestamp, direction, page_size, page_index):
        url = 'http://' + self.SLB_ip + ':' + str(self.port) + '/v1/medias/'
        headers = {"Token": token, "accept": "application/json",
                   "AuthHost": self.AuthHost}
        data = {'timestamp': timestamp, 'page_size': page_size,
                'page_index': page_index, 'direction': direction}
        start_time = time.time()
        response = requests.get(url, params=data, headers=headers, verify=True)
        time_spend = time.time() - start_time
        data = response.text
        print data
        self.get_media_spend_list.append(time_spend)
        response = response.json()
        try:
            return_code = response[u'code']
        except KeyError as e:
            print("Request-%s: Exception: %s" % (e, id))
            self.response.append("Except")
            return
        if return_code != 200:
            self.response.append("Failed")
            print(
            "Request-%s: Failed to get computes request: %s" % (id, response))
            return
        print("Request-%s: Successfully to get computes request" % id)
        self.response.append("OK")
        return

    def add_media_interface_with_curl(self, token, fingerprint, url, size, image_type, data_taken, height, width, img_rotate):
        cmd = 'curl -X PUT "http://%s:%s/v1/medias/" -H  "accept: application/json" -H  "AuthHost: api.cloudstorage.com" -H  "Token: %s" -H  "content-type: application/x-www-form-urlencoded" -d "fingerprint=%s&url=%s&size=%s&type=%s&data_taken=%s&img_height=%s&img_width=%s&img_rotate=%s"' % \
              (self.SLB_ip, self.port, token, fingerprint, url, size, image_type, data_taken, height, width, img_rotate)
        print cmd
        start_time = time.time()
        child = subprocess.call(cmd, shell=True)
        time_spend = time.time() - start_time

        self.add_media_interface_spend_list.append(time_spend)

    def add_media_interface(self, token, fingerprint, url, size, image_type, data_taken, height, width, img_rotate):
        request_url = 'http://' + self.SLB_ip + ':' + str(self.port) + '/v1/medias/'
        headers = {"Token": token, "accept": "application/json",
                   "AuthHost": self.AuthHost}
        data = {'fingerprint': fingerprint, 'url': url,
                'size': size, 'type': image_type,
                'data_taken': data_taken, 'img_height': height,
                'img_width': width, 'img_rotate': img_rotate}
        start_time = time.time()
        r = requests.put(request_url, data, headers=headers, verify=True)
        time_spend = time.time() - start_time
        data = r.text
        print data
        response = r.json()
        self.add_media_interface_spend_list.append(time_spend)
        try:
            return_code = response[u'code']
        except KeyError as e:
            print("Request-%s: Exception: %s" % (e, id))
            self.response.append("Except")
            return
        if return_code != 200:
            self.response.append("Failed")
            print("Request-%s: Failed to get computes request: %s" % (id, response))
            return
        print("Request-%s: Successfully to get computes request" % id)
        self.response.append("OK")
        return

    def multi_thread_users_get_medias(self, token_file_path, count):
        page_size = 30
        page_index = 1
        timestamp = '1512012900'
        direction = 'BEHIND'
        threads = []
        i = 0
        with open(token_file_path) as f:
            for line in f.readlines():
                if i > count - 1:
                    break
                token = line.strip()
                #print token
                t = threading.Thread(target=self.get_medias_request,
                                     args=(token, timestamp, direction, page_size, page_index))
                threads.append(t)
                i += 1

            for t in threads:
                t.setDaemon(True)
                t.start()

            for i in range(0, len(threads)):
                threads[i].join(600)

    def multi_thread_usrs_add_media_interface(self, token_file_path, url_file_path, count):
        img_type = 'PIC'
        size = 253730
        data_taken = '1512012900'
        img_height = 5
        img_width = 2
        img_rotate = 1

        url_count = 0
        token_count = 0
        threads = []
        i = 0
        with open(url_file_path) as f_url:
            with open(token_file_path) as f_token:
                token_lines = f_token.readlines()
                for line_url in f_url.readlines():
                    if i > count*2 - 1:
                        break

                    if not url_count % 2 and url_count != 0:
                        token_count = token_count + 1

                    token = token_lines[token_count].strip()

                    if not url_count % 2:
                        line_url = line_url.strip()
                        finger_print = line_url.split("/")[-1][:-4]

                        t = threading.Thread(target=self.add_media_interface,
                                             args=(
                                                 token, finger_print, line_url,
                                                 size, img_type, data_taken,
                                                 img_height,
                                                 img_width, img_rotate))
                        threads.append(t)
                    url_count = url_count + 1

                    i += 1

                for t in threads:
                    t.setDaemon(True)
                    t.start()

                for i in range(0, len(threads)):
                    threads[i].join(60)

    def test_get_media(self):
        self.thread_count = 1
        token_file_path = "data/token.txt"

        self.start_time = datetime.datetime.now()
        self.multi_thread_users_get_medias(token_file_path, self.thread_count)
        self.end_time = datetime.datetime.now()

        self.out_log_pk(self.thread_count, "data/spendtime_get_media_%s.log" %
                        self.thread_count,  self.get_media_spend_list)

    def test_add_media_interface(self):
        self.thread_count = 600
        token_file_path = "data/token.txt"
        url_file_path = "data/photo_storage_url.txt"

        self.start_time = datetime.datetime.now()
        self.multi_thread_usrs_add_media_interface(token_file_path, url_file_path, self.thread_count)
        self.end_time = datetime.datetime.now()

        self.out_log_pk(self.thread_count,
                        "data/spendtime_add_media_%s.log" % self.thread_count,
                        self.add_media_interface_spend_list)


