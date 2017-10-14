import urllib.request
import urllib.error
import urllib.parse
import json
import requests
import threading
import time
import sys


class Crawler(threading.Thread):
    num_post = 0
    num_delete = 0

    def __init__(self, name, seed, token):
        super(Crawler, self).__init__()
        self.name = name
        self.next_url = seed
        self.token = token

    def get_document(self, url):
        url = 'http://api.welcome.kakao.com{}'.format(url)
        request = urllib.request.Request(url)
        request.add_header("X-Auth-Token", self.token)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print(e.code, '10 minutes..')
            # TODO 2: 왜안꺼져!
            self.join()
            self.exit()
            sys.exit()
        document = json.loads(response.read().decode('utf-8'))
        return document

    def manage_image(self, images):
        image_dict = {}
        # TODO 6: 중복 image 관리
        for img in images:
            if img['type'] == 'add':
                image_dict[img['id']] = 'add'
            else:
                image_dict[img['id']] = 'del'

        to_save = []
        to_delete = []
        for img_id in image_dict:
            if image_dict[img_id] == 'add':
                to_save.append(img_id)
            else:
                to_delete.append(img_id)

        num_post = self.manage_feature(to_save, 'POST')
        num_delete = self.manage_feature(to_delete, 'DELETE')
        return (num_post, num_delete)

    '''Get features from images, Add/Delete features'''
    def manage_feature(self, images, method):
        # slice images if 50^ images
        if len(images) > 50:
            num_feature = self.manage_feature(images[:50], method)
            num_feature += self.manage_feature(images[50:], method)
            return num_feature

        # get features
        url = 'http://api.welcome.kakao.com/image/feature?id={}'.format(','.join(images))
        request = urllib.request.Request(url)
        request.add_header("X-Auth-Token", self.token)

        # 들어올 때는 마음대로지만 나갈 때는 아니란다.
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:  # 503
            print(e)
            time.sleep(1)
            return self.manage_features(images, method)
        except ConnectionResetError as e:  # API 초당 50 제한
            print(e)
            time.sleep(1)
            return self.manage_features(images, method)
        features = json.loads(response.read().decode('utf-8'))['features']

        # post or delete features
        url = 'http://api.welcome.kakao.com/image/feature'
        headers = {"X-Auth-Token": self.token}
        # slice features if 50^, 50개 미만일 시 data=null값으로 오류 발생 ㄴ(?)
        if method == 'POST':
            requests.post(url, data=json.dumps({'data': features[:50]}), headers=headers)
            requests.post(url, data=json.dumps({'data': features[50:]}), headers=headers)
        elif method == 'DELETE':
            requests.delete(url, data=json.dumps({'data': features[:50]}), headers=headers)
            requests.delete(url, data=json.dumps({'data': features[50:]}), headers=headers)
        return len(features)

    def run(self):
        while True:
            url = self.next_url
            document = self.get_document(url)
            next_url = document['next_url']
            self.next_url = next_url
            # 같은 document일 경우 리젠될때까지 기다림(url, next_url 비교)
            # TODO 4: 리젠 주기 파악
            if url == next_url:
                time.sleep(1)
                continue
            images = document['images']
            result = self.manage_image(images)
            self.num_post += result[0]
            self.num_delete += result[1]
