import random
import re
import requests
from bs4 import BeautifulSoup

# 热门榜地址
url = 'https://www.taptap.cn/top/download'
# 热玩榜地址
played_url = 'https://www.taptap.cn/top/played'
urls = [url, played_url]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 '
                  'Safari/537.36 Edg/126.0.0.0'
}

# 服务器地址
server_url = 'http://127.0.0.1:8080'


def get_game_id_db_by_game_name(game_name):
    response = requests.get(f'{server_url}/public/game/id', params={'name': game_name})
    if response.status_code == 200:
        return response.json().get('data')


def get_game_info_list(url, page) -> list[dict]:
    # 游戏榜单游戏id
    response = requests.get(f"{url}?page={page}", headers=headers)
    response.encoding = 'utf-8'
    html_content = response.text
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    game_list = soup.find('div', class_='list-content')
    game_info_list: list[dict] = list()
    for game in game_list.find_all('div', class_='list-item', attrs={'data-page': page}):
        try:
            game_center = game.find('div', class_='game-center')
            game_name = game_center.find('meta', itemprop='name')['content']
            # 如果数据库不存在此游戏，则不加入id
            game_id_db = get_game_id_db_by_game_name(game_name)
            if game_id_db is None:
                print('不存在游戏：', game_name)
                continue
            game_id_str = re.search(r'/app/(\d+)', game.find('a', class_='game-cell__icon')['href']).group(1)
            game_info_list.append({'game_id_str': game_id_str, 'game_name': game_name, 'game_id_db': game_id_db})
        except:
            continue
    print(f'第{page}页：{game_info_list}')
    return game_info_list


class Comment:
    def __init__(self, game_id_db, avatar, nickname, content, images, rating):
        self.game_id_db: int = game_id_db
        self.avatar: str = avatar
        self.nickname: str = nickname
        self.content: str = content
        self.images: list[str] = images
        self.rating: int = rating

    def __str__(self):
        return f'avatar:{self.avatar}, nickname:{self.nickname}, content:{self.content}, images:{self.images}, rating:{self.rating}'


def build_comments(game_info: dict) -> list[Comment]:
    game_id_str = game_info.get('game_id_str')
    url = f'https://www.taptap.cn/app/{game_id_str}/review'
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    html_content = response.text

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    # 获取游戏名称
    game_name = game_info.get('game_name')
    print(f'爬取评价：{game_name}')
    # 获取评价列表
    comment_list = soup.find_all('div', class_='review-item')
    comment_obj_list: list[Comment] = list()
    game_id_db = game_info.get('game_id_db')
    for comment_item in comment_list:
        try:
            comment_obj = build_comment(game_id_db, comment_item)
            comment_obj_list.append(comment_obj)
        except:
            continue
    return comment_obj_list


def build_comment(game_id_db: int, comment_item):
    # 昵称
    avatar = comment_item.find('a', class_='review-item__header-avatar').find('img')['src']
    # 昵称
    nickname = comment_item.find('a', class_='user-name__text')['title']
    # 评价文本内容
    content = comment_item.find('div', class_='review-item__contents').find_all('div')[0].find('a').get_text(separator='\n')
    # 评价的图片（不一定有）
    images = []
    image_list = comment_item.find_all('div', class_='review-image-list__item')
    if image_list:
        for image_item in image_list:
            img = image_item.find('img')['src']
            images.append(img)
    return Comment(game_id_db, avatar, nickname, content, images, random.randint(3, 5))


def generate_random_phone_number():
    return '1' + ''.join(random.choices('0123456789', k=10))


def insert_comment(comment_obj: Comment):
    # 1. 注册账号，手机号随机11位数字，密码默认为123456
    phone = generate_random_phone_number()
    password = '123456'
    register_data = {
        'phone': phone,
        'password': password,
        'nickname': comment_obj.nickname,
    }
    response = requests.post(f'{server_url}/public/user/register', json=register_data)
    # 注册成功说明是新用户，不成功则说明手机号重复，用户已经存在
    # 2. 登录账号，获取token
    login_data = {
        'phone': phone,
        'password': password,
    }
    response = requests.post(f'{server_url}/public/user/login', json=login_data)
    token: str = response.json().get('data')
    headers = {
        'Authorization': token
    }
    # 3. 更换头像
    avatar_data = {
        'avatar': comment_obj.avatar
    }
    requests.put(f'{server_url}/protected/user/avatar/url', json=avatar_data, headers=headers)
    # 4. 插入评价
    comment_data = {
        'gameId': comment_obj.game_id_db,
        'content': comment_obj.content,
        'images': comment_obj.images,
        'rating': comment_obj.rating
    }
    requests.post(f'{server_url}/protected/comment', headers=headers, json=comment_data)
    # 5. 关注游戏
    requests.put(f'{server_url}/protected/game/follow/{comment_obj.game_id_db}', headers=headers)


for url in urls:
    print(f'爬取游戏ID：{url}')
    for i in range(1, 16):
        game_info_list = get_game_info_list(url, i)
        for game_info in game_info_list:
            comments = build_comments(game_info)
            for comment in comments:
                try:
                    insert_comment(comment)
                    print(f'插入成功：{comment.game_id_db},{comment.nickname},{comment.avatar}')
                except:
                    continue
