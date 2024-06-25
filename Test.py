import requests

server_url = "http://127.0.0.1:8080"

params = {
    'name': '不存在的游戏'
}

response = requests.get(f'{server_url}/game/id', params=params)
print(response.json())
if response.status_code == 200:
    if response.json().get('data') is None:
        print('不存在')

data = {
    'phone': '13188884444',
    'password': '123456'
}

response = requests.post(f'{server_url}/user/login', json=data)
print(response.json())
