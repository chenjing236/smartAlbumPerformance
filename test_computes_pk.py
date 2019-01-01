import nose
import unittest
import urllib
import httplib
import json
import subprocess
import threading
import time
import test_base
import requests


class ComputesTest(test_base.BaseTest):

    def setUp(self):
        test_base.BaseTest.setUp(self)

    def get_computes(self, token, page_size, page_index):
        params = urllib.urlencode(
            {'page_size': page_size, 'page_index': page_index})
        headers = {"Token": token, "accept": "application/json",
                   "AuthHost": self.AuthHost}
        conn = httplib.HTTPConnection(self.SLB_ip, self.port)
        get_url = "/v1/computes/?"
        conn.request("GET", get_url, params, headers)
        response = conn.getresponse()
        data = response.read()
        response_get_computes = json.loads(data)
        conn.close()

        print "\n %s" % response_get_computes

    def get_computes_with_curl(self, token, page_size, page_index):
        cmd = 'curl -X GET "http://%s:%s/v1/computes/?page_size=%s&page_index=%s" -H "accept: application/json" -H "AuthHost: api.cloudstorage.com" -H "Token: %s" -s' % (
        self.SLB_ip, self.port, page_size, page_index, token)
        print cmd
        start_time = time.time()
        child = subprocess.call(cmd, shell=True)
        time_spend = time.time() - start_time
        self.get_compute_spend_list.append(time_spend)

    def get_computes_request(self, token, page_size, page_index, id):
        url = 'http://' + self.SLB_ip + ':' + str(self.port) + '/v1/computes/?page_size=%s&page_index=%s' % (page_size, page_index)
        headers = {"Token": token, "accept": "application/json",
                   "AuthHost": self.AuthHost}
        start_time = time.time()
        r = requests.get(url, headers=headers, verify=True) # Works well
        #r = requests.post(url, headers=headers, verify=True) # Just make failure
        time_spend = time.time() - start_time
        response = r.json()
        #print('Result : %s' % response)
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
        self.get_compute_spend_list.append(time_spend)
        self.response.append("OK")
        return 

    def submit_computes_tasks(self, token, fingerprint, url):
        params = urllib.urlencode({'fingerprint': fingerprint, 'url': url})
        headers = {"Token": token, "accept": "application/json",
                   "AuthHost": self.AuthHost}
        conn = httplib.HTTPConnection(self.SLB_ip, self.port)
        url = "/v1/computes/"
        conn.request("POST", url, params, headers)
        response = conn.getresponse()
        # response status is not OK
        if response.status != 200:
            print("Fail")
            return False
        # when response status is OK, get token from response data
        data = response.read()
        response_data = json.loads(data)
        conn.close()

        print response_data

    def submit_computes_with_url(self, token, fingerprint, url):
        cmd = 'curl -X POST "http://%s:%s/v1/computes/" -H "accept: application/json" -H "AuthHost: api.cloudstorage.com" -H "Token: %s" -d "fingerprint=%s&url=%s"' % \
              (self.SLB_ip, self.port, token, fingerprint, url)
        start_time = time.time()
        print("cmd:%s" % cmd)
        child = subprocess.call(cmd, shell=True)
        time_spend = time.time() - start_time
        self.submit_compute_spend_list.append(time_spend)

    def submit_computes_request(self, token, fingerprint, url, id):
        url = 'http://' + self.SLB_ip + ':' + str(self.port) + '/v1/computes/'
        headers = {"Token": token, "accept": "application/json",
                   "AuthHost": self.AuthHost}
        data = {'fingerprint': fingerprint, 'url': url }
        start_time = time.time()
        r = requests.post(url, data=data, headers=headers, verify=True) # Works well
        #r = requests.post(url, data=json.dumps(data), headers=headers, verify=True) # Just make failure
        time_spend = time.time() - start_time
        response = r.json()
        #print('Result : %s' % response)
        try:
            return_code = response[u'code']
        except KeyError as e:
            print("Request-%s: Exception: %s" % (e, id))
            self.response.append("Except")
            return 
        if return_code != 200:
            self.response.append("Failed")
            print("Request-%s: Failed to submit computes request: %s" % (id, response))
            return 
        print("Request-%s: Successfully to submit computes request" % id)
        self.submit_compute_spend_list.append(time_spend)
        self.response.append("OK")
        return 

    def multi_thread_users_get_computes(self, token_file_path, count):
        page_size = 10
        page_index = 1
        threads = []
        i = 0
        with open(token_file_path) as f:
            for line in f.readlines():
                if i > count - 1:
                    break
                token = line.strip()
                t = threading.Thread(target=self.get_computes_request,
                #t = threading.Thread(target=self.get_computes_with_curl,
                                     args=(token, page_size, page_index, i+1))
                threads.append(t)
                i += 1

            for t in threads:
                t.setDaemon(True)
                t.start()

            for i in range(0, len(threads)):
                threads[i].join(600)

#    '''def multi_thread_usrs_submit_compute_tasks(self, token_file_path, url_file_path, count):
#        url_count = 0
#        token_count = 0
#        threads = []
#        i = 0
#        with open(url_file_path) as f_url:
#            with open(token_file_path) as f_token:
#                token_lines = f_token.readlines()
#                for line_url in f_url.readlines():
#                    if i > count - 1:
#                        break
#                    line_url = line_url.strip()
#                    if not url_count % 2 and url_count != 0:
#                        token_count = token_count + 1
#                    token = token_lines[token_count]
#                    url_count = url_count + 1
#                    finger_print = line_url.split("/")[-1][:-4]
#
#                    t = threading.Thread(target=self.submit_computes_with_url,
#                                         args=(token.strip(), finger_print, line_url))
#                    threads.append(t)
#                    i += 1
#
#                for t in threads:
#                    t.setDaemon(True)
#                    t.start()
#
#                for i in range(0, len(threads)):
#                    threads[i].join(600)'''

    def multi_thread_usrs_submit_compute_tasks(self, token_file_path, url_file_path, count):
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
                    token = token_lines[token_count]
                    url_count = url_count + 1

                    if not url_count % 2:
                        line_url = line_url.strip()
                        finger_print = line_url.split("/")[-1][:-4]
                        #t = threading.Thread(target=self.submit_computes_with_url,
                        t = threading.Thread(target=self.submit_computes_request,
                                             args=(token.strip(), finger_print, line_url, token_count+1))
                        threads.append(t)
                    i += 1

                for t in threads:
                    t.setDaemon(True)
                    t.start()

                for i in range(0, len(threads)):
                    threads[i].join(60)


    def test_get_computes(self):
        token_file_path = "data/token.txt"
        thread_count = 3

        self.multi_thread_users_get_computes(token_file_path, thread_count)
        self.out_log(thread_count, "data/spendtime_%s.log" % thread_count, self.get_compute_spend_list)

    def test_submit_computes_tasks(self):
        token_file_path = "data/token.txt"
        url_file_path = "data/photo_url.txt"
        thread_count = 500

        self.multi_thread_usrs_submit_compute_tasks(token_file_path, url_file_path, thread_count)
        self.out_log(thread_count, "data/spendtime_%s.log" % thread_count, self.submit_compute_spend_list)



if  __name__ == "__main__":
    compute_utils = ComputesTest()
    compute_utils.test_get_computes()
