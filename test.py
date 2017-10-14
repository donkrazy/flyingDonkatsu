import urllib.request
import urllib.error
import urllib.parse
import json
import requests


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
    # TODO: get toekn from body
    except urllib.error.HTTPError:
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
    response = urllib.request.urlopen(request)
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
    response = urllib.request.urlopen(request)
    features = json.loads(response.read().decode('utf-8'))['features']

    # post or delete features
    url = 'http://api.welcome.kakao.com/image/feature'
    headers = {"X-Auth-Token": token}
    if method == 'POST':
        requests.post(url, data=json.dumps({'data': features}), headers=headers)
    elif method == 'DELETE':
        requests.delete(url, data=json.dumps({'data': features}), headers=headers)

    return len(features)


def crawl(seed_list, token):
    while True:
        for i in range(len(seed_list)):
            seed = seed_list[i]
            document = get_document(seed, token)
            images = document['images']
            result = manage_image(images, token)
            print('got document from {}, {} images, {}/{}(post/delete) features'.format(seed, len(images), result[0], result[1]))
            next_url = document['next_url']
            seed_list[i] = next_url


if __name__ == '__main__':
    token = get_token()
    seed_list = get_seed(token)
    crawl(seed_list, token)

















