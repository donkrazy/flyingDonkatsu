import urllib.request
import urllib.error
import urllib.parse
import time
from Crawler import Crawler


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
    # TODO 1: get token from response body
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


def crawl(seed_list, token):
    # Make 5 threads(number of seeds)
    crawler_list = []
    for seed in seed_list:
        name = seed.split('/')[2]
        crawler = Crawler(name, seed, token)
        crawler.start()
        crawler_list.append(crawler)

    # simple work checker
    while True:
        time.sleep(10)
        print('#######{}########'.format(time.ctime()))
        for crawler in crawler_list:
            print('{}: {}/{}'.format(crawler.name, crawler.num_post, crawler.num_delete))


if __name__ == '__main__':
    token = get_token()
    seed_list = get_seed(token)  # category별 seed
    crawl(seed_list, token)
