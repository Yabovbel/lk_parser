import requests
from bs4 import BeautifulSoup

url = 'https://lk.sut.ru/'
# представляемся сайту обычным браузером для того, чтоб пройти проверку на робота. Для этого прописываем
# рандомный браузер в user-agent
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
      }
response = requests.get(url, headers = headers)
soup = BeautifulSoup(response.text, 'lxml')

print(soup)