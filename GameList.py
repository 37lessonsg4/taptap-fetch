import requests
from bs4 import BeautifulSoup

# 目标URL
url = 'https://www.taptap.cn/'

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
