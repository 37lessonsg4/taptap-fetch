import re

import requests
from bs4 import BeautifulSoup


class GameItem:
    def __init__(self, rank, name, rating, icon_url):
        self.rank = rank
        self.name = name
        self.rating = rating
        self.icon_url = icon_url

    def __str__(self):
        return f'Rank: {self.rank}, Name: {self.name}, Rating: {self.rating}, Icon URL: {self.icon_url}'


# 目标URL
url = 'https://www.taptap.cn/top/download/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 '
                  'Safari/537.36 Edg/126.0.0.0'
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

html_content = response.text

# 使用BeautifulSoup解析HTML内容
soup = BeautifulSoup(html_content, 'html.parser')
print(soup.title)

results = list()
game_list = soup.find('div', class_='list-content')
for game in game_list.find_all('div', class_='list-item'):
    game_center = game.find('div', class_='game-center')
    game_rank = game.find(class_='rank-index').text
    game_icon_url = game.find('img', alt=re.compile('.*icon$'))['src']
    game_rating = game.find(class_='tap-rating__number').text
    game_name = game_center.find('meta', itemprop='name')['content']
    result = GameItem(game_rank, game_name, game_rating, game_icon_url)
    results.append(result)

for result in results:
    print(result)
