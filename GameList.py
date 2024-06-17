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

results = list()


def getDataPage(page):
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
        result_game_item = GameItem(game_rank, game_name, game_rating, game_icon_url, game_id)
        results.append(result_game_item)




print('开始爬取数据...')
for i in range(1, 2):
    getDataPage(i)
for result in results:
    print(result)
print('爬取数据结束！')
