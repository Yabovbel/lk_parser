import requests
from bs4 import BeautifulSoup
from auth_params import *

url = 'https://lk.sut.ru/?login=yes'
# представляемся сайту обычным браузером для того, чтоб пройти проверку на робота. Для этого прописываем
# рандомный браузер в user-agent
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
}
data = {
    'users': LOGIN,
    'parole': PASSWORD,
}
session = requests.Session()
session.headers.update(headers)
response =  session.post(url, data=data)
#response = requests.get(url, headers = headers)
soup = BeautifulSoup(response.text, 'lxml')

print(soup)