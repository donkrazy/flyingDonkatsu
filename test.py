import urllib.request
import urllib.error
import urllib.parse
import json
import requests
import threading
import time
import sys


def get_token():
    token_login = 'Ujme8WK325GqrHRzNBE3Bpj7MHk83-gNRDdp8A3VrmM'
    url = 'http://api.welcome.kakao.com/token/{}'.format(token_login)
    # get new token
    try:
        response = urllib.request.urlopen(url)
        with open('token', 'w') as f:
            token_submit = response.read().decode('utf-8')
            f.write(token_submit)
    # 403 error: read token from file
    # TODO: get token from body
    except urllib.error.HTTPError as e:
        print(e)
        with open('token') as f:
            token_submit = f.read()
    return token_submit


def get_seed(token):
    url = 'http://api.welcome.kakao.com/seed'
    request = urllib.request.Request(url)
    request.add_header("X-Auth-Token", token)
    response = urllib.request.urlopen(request)
    seed_list = response.read().decode('utf-8').strip().split('\n')
    return seed_list


def get_document(seed, token):
    url = 'http://api.welcome.kakao.com{}'.format(seed)
    request = urllib.request.Request(url)
    request.add_header("X-Auth-Token", token)
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        print(e.code, '10 minutes..')
        sys.exit()
    document = json.loads(response.read().decode('utf-8'))
    return document


def manage_image(images, token):
    image_dict = {}
    # TODO: duplicate?
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

    num_post = manage_features(to_save, token, 'POST')
    num_delete = manage_features(to_delete, token, 'DELETE')
    return (num_post, num_delete)


def manage_features(images, token, method):
    # slice images if 50^ images
    if len(images) > 50:
        num_feature = manage_features(images[:50], token, method)
        num_feature += manage_features(images[50:], token, method)
        return num_feature

    # get features
    url = 'http://api.welcome.kakao.com/image/feature?id={}'.format(','.join(images))
    request = urllib.request.Request(url)
    request.add_header("X-Auth-Token", token)

    # 들어올 때는 마음대로지만 나갈 때는 아니란다.
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:  # 503
        print(e)
        time.sleep(1)
        return manage_features(images, token, method)
    except ConnectionResetError as e:
        print(e)
        time.sleep(1)
        return manage_features(images, token, method)

    features = json.loads(response.read().decode('utf-8'))['features']

    # post or delete features
    url = 'http://api.welcome.kakao.com/image/feature'
    headers = {"X-Auth-Token": token}
    if method == 'POST':
        requests.post(url, data=json.dumps({'data': features}), headers=headers)
    elif method == 'DELETE':
        requests.delete(url, data=json.dumps({'data': features}), headers=headers)

    return len(features)


class Crawler(threading.Thread):
    num_post = 0
    num_delete = 0

    def __init__(self, name, seed, token):
        super(Crawler, self).__init__()
        self.name = name
        self.seed = seed
        self.next_url = seed
        self.token = token

    def run(self):
        while True:
            url = self.next_url
            document = get_document(url, token)
            next_url = document['next_url']
            self.next_url = next_url
            # 리젠될때까지 기다림
            # 리젠 주기 파악
            if url == next_url:
                time.sleep(1)
                continue
            images = document['images']
            result = manage_image(images, token)
            self.num_post += result[0]
            self.num_delete += result[1]


def crawl(seed_list, token):
    crawler_list = []
    for seed in seed_list:
        name = seed.split('/')[2]
        crawler = Crawler(name, seed, token)
        crawler.start()
        crawler_list.append(crawler)

    # simple timer
    while True:
        time.sleep(10)
        print('#######{}########'.format(time.ctime()))
        for crawler in crawler_list:
            print('{}: {}/{}'.format(crawler.name, crawler.num_post, crawler.num_delete))


if __name__ == '__main__':
    token = get_token()
    seed_list = get_seed(token)
    crawl(seed_list, token)
