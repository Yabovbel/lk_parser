from requests import Session as req_session
from bs4 import BeautifulSoup
from auth_params import *
from re import compile as re_comp


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
    session.get(url_lk)
    response =  session.post(url_auth, data=data)
    soup = BeautifulSoup(response.text, 'lxml')
    session.get(url_lk)
    return soup.p.text == '1'

def files_count_range():
    url_forms = 'https://lk.sut.ru/project/cabinet/forms/'
    response =  session.get(url_forms + 'files_group_pr.php')
    soup = BeautifulSoup(response.text, 'lxml')
    soup = soup.find("span", id="table_mes")
    num_span_a=0
    for child_span_a in soup.find_all("a"):
        if num_span_a == 3 :
            child_span_a=child_span_a.get("onclick")
            int(child_span_a[-4:-2])
            break
        num_span_a+=1
    return int(child_span_a[-4:-2])

def get_all_files_group():
    url_forms = 'https://lk.sut.ru/project/cabinet/forms/'
    files_group=[]
    for page in range(1, files_count_range()):
        response =  session.get(url_forms + 'files_group_pr.php?page=' + str(page))
        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find("table", id="mytable")
        soup = soup.tbody
        for child_tr in soup.find_all("tr", id=re_comp("^tr")):
                files_params=[]
                num_td=0
                for child_td in child_tr.find_all("td"):
                        if num_td < 5:
                            files_params.append(child_td.text)
                            num_td+=1
                        else:
                            files_links=[]
                            for child_a in child_td.find_all("a"):
                                    files_links.append(child_a.get("href"))
                            files_params.append(files_links)
                            break
                files_group.append(files_params)
    return files_group

session = req_session()
if auth_lk():
    print(get_all_files_group()[252])
else:
    print('Авторизация неуспешна, проверьте параметры авторизации.')