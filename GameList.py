import logging
import re

import requests
from bs4 import BeautifulSoup


class GameItem:
    def __init__(self, rank, name, rating, icon_url, id):
        self.rank = rank
        self.name = name
        self.rating = rating
        self.icon_url = icon_url
        self.id = id

    def __str__(self):
        return f'Rank: {self.rank}, Name: {self.name}, Rating: {self.rating}, Icon URL: {self.icon_url}, ID: {self.id}'


# 目标URL
url = 'https://www.taptap.cn/top/download'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 '
                  'Safari/537.36 Edg/126.0.0.0'
}

rank_results = list()


def get_rank_list(page):
    response = requests.get(url + f"?page={page}", headers=headers)
    response.encoding = 'utf-8'

    html_content = response.text

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup.title)

    game_list = soup.find('div', class_='list-content')
    for game in game_list.find_all('div', class_='list-item', attrs={'data-page': page}):
        game_center = game.find('div', class_='game-center')
        game_rank = game.find(class_='rank-index').text
        game_icon_url = game.find('img', alt=re.compile('.*icon$'))['src']
        game_rating = game.find(class_='tap-rating__number').text
        game_name = game_center.find('meta', itemprop='name')['content']
        game_id = re.search(r'/app/(\d+)', game.find('a', class_='game-cell__icon')['href']).group(1)
        result_rank_item = GameItem(game_rank, game_name, game_rating, game_icon_url, game_id)
        rank_results.append(result_rank_item)

def get_game_detail(game_id):
    response = requests.get(f'https://www.taptap.cn/app/{game_id}', headers=headers)
    response.encoding = 'utf-8'
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    game_name = soup.find('h1', class_='text-default--size').text
    basic_info = soup.find('div', class_='app-basic-info').find_all('div', class_='single-info__content')

    # 初始化字典以存储信息
    game_info = {
        'name': game_name,
        'downloads': None,
        'follow': None,
        'size': None,
        'developer': None,
        'heat': None
    }

    game_info_list = list()

    # 遍历基本信息
    for info in basic_info:
        label = info.find('span', class_='caption-m12-w12 gray-06')
        value = info.find('div',
                          class_='tap-text tap-text__one-line single-info__content__value gray-07 overflow-single')

        if label and value:
            label_text = label.text.strip()
            value_text = value.text.strip()

            if label_text == '下载':
                game_info['downloads'] = value_text
            elif label_text == '关注':
                game_info['followers'] = value_text
            elif label_text == '游戏大小':
                game_info['size'] = value_text
            elif label_text == '开发' or label_text == '厂商':
                game_info['developer'] = value_text

        # for key, value in game_info.items():
        #     if value is None:
        #         print(info.prettify())

    return game_info







print('开始爬取数据...')
for i in range(1, 2):
    get_rank_list(i)
for result in rank_results:
    # print(result)
    print(get_game_detail(result.id))
print('爬取数据结束！')
