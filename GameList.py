import requests
from bs4 import BeautifulSoup

# 目标URL
url = 'https://www.taptap.cn/'

response = requests.get(url)
response.encoding = 'utf-8'

html_content = response.text

# 使用BeautifulSoup解析HTML内容
soup = BeautifulSoup(html_content, 'html.parser')
print(soup.title)
