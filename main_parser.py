import requests
from bs4 import BeautifulSoup
from auth_params import *

def auth_lk():
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
    session.headers.update(headers)
    response =  session.get(url_lk)
    response =  session.post(url_auth, data=data)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.p.text == '1'

url_forms = 'https://lk.sut.ru/?login=yes'
session = requests.Session()
if auth_lk():
    response =  session.get(url_forms)
    soup = BeautifulSoup(response.text, 'lxml')
    print(soup)
else:
    print('Авторизация неуспешна, проверьте параметры авторизации.')