from requests import Session as req_session
from bs4 import BeautifulSoup
from auth_params import *
from re import compile as re_comp


def auth_lk():
    # функция прохождения авторизации на портале. Если возвращает истину, то авторизация прошла успешно
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
    # просто загружаем страницу авторизации, чтоб открыть сессию на сервере. ХЗ зачем, но без этого
    # не работает
    session.get(url_lk)
    # авторизируемся. Если в ответ получим 1, то значит все хорошо
    response =  session.post(url_auth, data=data)
    soup = BeautifulSoup(response.text, 'lxml')
    # еще раз просто загрузаем страницу ЛК, иначе в дельнейшем у нас не будут грузится страницы для
    # парсинга. Она нам не нужна, но без ее загрузки ничего не работает. ХЗ почему, это ведь бонч.
    session.get(url_lk)
    return soup.p.text == '1'

def files_count_range():
    # функция подсчета количества страниц с файлами группам. Возвращает число страниц.
    url_forms_gr = 'https://lk.sut.ru/project/cabinet/forms/files_group_pr.php'
    response =  session.get(url_forms_gr)
    soup = BeautifulSoup(response.text, 'lxml')
    soup = soup.find("span", id="table_mes")
    # номер последней страницы содержится в четвертом теге <a> внутри span. Перебираем все теги <a> до
    # четвергого и прерываем цикл.
    num_span_a=0
    for child_span_a in soup.find_all("a"):
        if num_span_a == 3 :
            #Нужное значение находится в строке в параметре onclick
            child_span_a=child_span_a.get("onclick")
            break
        num_span_a+=1
    # Перед тем как вернуть, преобразуем значение в число
    return int(child_span_a[-4:-2])

def get_all_files_group():
    # функция парсинга файлов группы. Возвращает list с полученными занчениями
    url_forms_gr = 'https://lk.sut.ru/project/cabinet/forms/files_group_pr.php'
    # объявлям list, в котором будут все записи
    files_group=[]
    for page in range(1, files_count_range()+1):
        response =  session.get(url_forms_gr + '?page=' + str(page))
        soup = BeautifulSoup(response.text, 'lxml')
        # переходиим в таблицу с данными
        soup = soup.find("table", id="mytable")
        soup = soup.tbody
        # Цикл для всех строк (записей) в таблице. Строки обособлены тегом <tr>, а у нужным нам строк
        # id начинается на tr. Находим таки строки с помощью регулярного выражения
        for child_tr in soup.find_all("tr", id=re_comp("^tr")):
            # объявляем list, в котором будут все значения одной записи
            files_params=[]
            # каждое значение (ячейка столбца) внутри строки обособлена тегом <td>. Находим такие значения
            num_td=0
            for child_td in child_tr.find_all("td"):
                # из столбцов 1-5 просто берем текстовые значения
                if num_td < 5:
                    files_params.append(child_td.text)
                    num_td+=1
                # в шестом столбце может хранится несколько ссылок на файлы, поэтому его обрабатываем отдельно
                else:
                    # обявляем list для всех ссылок текущей записи
                    files_links=[]
                    # каждая ссылка находится в параметре href тега <a>. Находим такие теги и берем из
                    # них значение параметра.
                    for child_a in child_td.find_all("a"):
                            files_links.append(child_a.get("href"))
                    files_params.append(files_links)
                    break
            files_group.append(files_params)
    return files_group

session = req_session()
if auth_lk():
    print(get_all_files_group()[0][5][1])
else:
    print('Авторизация неуспешна, проверьте параметры авторизации.')