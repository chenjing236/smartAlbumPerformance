import oss2
import os


ossAccessKeyID = "LTAITfD9Tq6qM5iQ"
ossAccessKeySecret = "bvHQv9G0MtDuoGbHmiY1jgpoBzVFC0"
endpoint = "http://oss-cn-beijing.aliyuncs.com/"
url_str = "http://albumstorage-test22.oss-cn-beijing.aliyuncs.com/"
bucket_name = "albumstorage-test22"

auth = oss2.Auth(ossAccessKeyID, ossAccessKeySecret)

def get_bucket():
    bucket = oss2.Bucket(auth, endpoint, "albumstorage-test22")
    result = bucket.get_bucket_location()
    print result.location

def put_object(uid, photo_name):
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    with open("/mnt/photos/25454/%s" % photo_name, "rb") as f:
        bucket.put_object("%s/%s" % (uid, photo_name), f)

def get_uid():
    with open("/home/smart_album/uid.txt", "r") as f:
        for line in f.readlines():
            uid = line.strip()

def list_files():
    path = "/mnt/photos/25454"
    files = os.listdir(path)
    for file_name in files:
        print file_name

def func():
    photo_path = "/mnt/photos/25454"
    uid_path = "/home/smart_album/uid.txt"
    files = os.listdir(photo_path)
    i = 0
    with open(uid_path, "r") as f:
        with open("data/photo_storage_url.txt", "wr") as _f:
            for line in f.readlines():
                uid = line.strip()
                if i > 10000:
                    break
                while True:
                    i = i + 1
                    file_name = files[i]
                    url = url_str + "%s/%s" % (uid, file_name)
                    _f.writelines("%s\n" % url)
                    put_object(uid, file_name)
                    if not i % 2:
                        break
if __name__ == "__main__":
    func()

