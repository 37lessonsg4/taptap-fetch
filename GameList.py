import csv
import re
import time

import requests
from bs4 import BeautifulSoup
from lxml import etree


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
url = 'https://www.taptap.cn/top'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 '
                  'Safari/537.36 Edg/126.0.0.0'
}

rank_results: list[GameItem] = list()


def get_rank_list(group, page):
    rank_results.clear()
    response = requests.get(url + f"{group}?page={page}", headers=headers)
    response.encoding = 'utf-8'

    html_content = response.text

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup.title)

    game_list = soup.find('div', class_='list-content')
    for game in game_list.find_all('div', class_='list-item', attrs={'data-page': page}):
        try:
            game_center = game.find('div', class_='game-center')
            game_rank = game.find(class_='rank-index').text
            game_icon_url = game.find('img', alt=re.compile('.*icon$'))['src']
            game_rating = game.find(class_='tap-rating__number').text
            game_name = game_center.find('meta', itemprop='name')['content']
            game_id = re.search(r'/app/(\d+)', game.find('a', class_='game-cell__icon')['href']).group(1)
            result_rank_item = GameItem(game_rank, game_name, game_rating, game_icon_url, game_id)
            rank_results.append(result_rank_item)
        except:
            continue


class GameInfo:
    def __init__(self, gameItem: GameItem):
        self.icon = gameItem.icon_url
        self.name = ''
        self.size = None
        self.manufacture = None
        self.description = ''
        self.devNote = ''
        self.album: list[str] = []
        self.tags: list[str] = []

    def comma_album(self):
        return ','.join(self.album)

    def comma_tags(self):
        return ','.join(self.tags)


def get_game_detail(gameItem: GameItem) -> GameInfo:
    game_info = GameInfo(gameItem)
    response = requests.get(f'https://www.taptap.cn/app/{gameItem.id}', headers=headers)
    response.encoding = 'utf-8'
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    game_name = soup.find('h1', class_='text-default--size').text
    basic_info = soup.find('div', class_='app-basic-info').find_all('div', class_='single-info')

    game_info.name = game_name

    for info in basic_info:
        label = info.find('span', class_='caption-m12-w12 gray-06')
        value = info.find('div', class_='single-info__content__value')

        if label and value:
            label_text = label.text.strip()
            value_text = value.text.strip()

            if label_text == '游戏大小':
                game_info.size = value_text

        dev_texts = info.find_all('div', {'class': 'tap-text tap-text__one-line'})
        if len(dev_texts) == 2 and ('开发' in dev_texts[0].text or '厂商' in dev_texts[0].text):
            game_info.manufacture = dev_texts[1].text

        follower_label = info.find('div', {'class': 'app-basic-info__follow-text'})
        follower_text = info.find('div', {'class': 'single-info__content__value'})
        if follower_label and follower_text and '关注' in follower_label.text:
            game_info.followers = follower_text.text

    # 将BeautifulSoup对象转换为lxml对象
    dom = etree.HTML(str(soup))

    developer_info_divs = dom.xpath(
        '//*[@id="__nuxt"]/div/main/div/div[1]/div[4]/div/div[4]/div[2]/div[3]/div/span[2]')

    if developer_info_divs:
        # 提取并打印每个找到的div的文本内容
        for i, div in enumerate(developer_info_divs, 1):
            developer_text = div.xpath('string(.)').strip()
            game_info.devNote = developer_text
    else:
        developer_info_divs = dom.xpath(
            '//*[@id="__nuxt"]/div/main/div/div[1]/div[4]/div/div[3]/div[2]/div[3]/div/span[2]')
        if developer_info_divs:
            # 提取并打印每个找到的div的文本内容
            for i, div in enumerate(developer_info_divs, 1):
                developer_text = div.xpath('string(.)').strip()
                game_info.devNote = developer_text
        else:
            print(game_info.name, 'has no dev note')

    game_info.description = get_game_description(gameItem.id)

    album_sliders = soup.find('div', class_='app-trailer-screenshot-header__wrap')
    for image in album_sliders.find_all('img'):
        try:
            game_info.album.append(image['data-src'])
        except KeyError:
            continue

    tags = soup.find('div', class_='app-intro__tag')
    for tag in tags.find_all('a'):
        try:
            game_info.tags.append(tag.text)
        except KeyError:
            print(game_info.name, 'has no tag')
            break
    # print(game_info.name, game_info.tags)
    return game_info


def get_game_description(game_id):
    response = requests.get(f'https://www.taptap.cn/app/{game_id}/all-info', headers=headers)
    response.encoding = 'utf-8'
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    description = soup.find('div', class_='app__intro__summary').find('span')
    if description:
        return description.text
    return ''


def save_to_csv(info_list, filename='game_details.csv'):
    keys = info_list[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(info_list)


def save_to_sql(info_list: list[GameInfo], filename='game_details.sql'):
    with open(filename, 'w', encoding='utf-8') as output_file:
        output_file.write(
            "INSERT INTO game(name, icon, size, manufacture, description,dev_note, album, tags) VALUES\n ")
        values = []
        for info in info_list:
            # 转义单引号
            name = info.name.replace("'", "''")
            icon = info.icon.replace("'", "''")
            size = info.size.replace("'", "''")
            manufacture = info.manufacture.replace("'", "''")
            description = info.description.replace("'", "''")
            dev_note = info.devNote.replace("'", "''")
            album = info.comma_album().replace("'", "''")
            tags = info.comma_tags().replace("'", "''")

            values.append(
                f"('{name}', '{icon}', '{size}', '{manufacture}', '{description}', '{dev_note}', '{album}', '{tags}')"
            )

        # 将所有 VALUES 子句连接在一起并以分号结尾
        output_file.write(",\n".join(values) + ";\n")


game_info_list = list()

fifty_groups = ['/download/action',
                '/download/strategy',
                '/download/idle',
                '/download/single',
                '/download/causal',
                '/download/sandbox_survival',
                '/download/management',
                '/download/unriddle',
                '/download/music',
                '/download/swordsman',
                '/download/otome',
                '/download/roguelike',
                '/download/new',
                '/sell']

hundred_groups = ['/download/action',
                  '/played',
                  '/download',
                  '/exclusive']

print('开始爬取数据...')
for i, group in enumerate(fifty_groups):
    game_info_list.clear()
    for j in range(1, 6):
        get_rank_list(group, j)
        for result in rank_results:
            try:
                game_detail = get_game_detail(result)
                game_info_list.append(game_detail)
            except:
                continue
    print(group, '爬取完成')
    time.sleep(5)
    save_to_sql(game_info_list, f'game_details-fifty-{i}.sql')

for i, group in enumerate(hundred_groups):
    game_info_list.clear()
    for j in range(1, 16):
        get_rank_list(group, j)
        for result in rank_results:
            try:
                game_detail = get_game_detail(result)
                game_info_list.append(game_detail)
            except:
                continue
    print(group, '爬取完成')
    save_to_sql(game_info_list, f'game_details-hundred-{i}.sql')

print('爬取数据结束！')
