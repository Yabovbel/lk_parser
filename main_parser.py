import requests
from bs4 import BeautifulSoup
from auth_params import *

url_lk = 'https://lk.sut.ru/?login=yes'
url_auth = 'https://lk.sut.ru/cabinet/lib/autentificationok.php'
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
response =  session.get(url_lk)
response =  session.post(url_auth, data=data)
soup = BeautifulSoup(response.text, 'lxml')
if soup.p.text != '1':
    print('Авторизация неуспешна, проверьте параметры авторизации.')
else:
    response =  session.get(url_lk)
    soup = BeautifulSoup(response.text, 'lxml')
    print(soup)