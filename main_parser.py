from requests import Session as req_session
from bs4 import BeautifulSoup
from auth_params import *
from re import compile as re_comp, search as re_search, split as re_split


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
    # номер последней страницы содержится внутри span в теге <a>, где строка " >> "
    child_span_a=soup.find("a", string=" >> ")
    # Нужное значение находится в строке в параметре onclick
    child_span_a=child_span_a.get("onclick")
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

def number_week_null():
    # функция определения номера нулевой недели. Возвращает номер недели.
    url_forms_tt = 'https://lk.sut.ru/project/cabinet/forms/raspisanie.php'
    # Минимально в семестре 17 недель, поэтому для оптимизации, недели раньше 17ой не просматриваются.
    # Будем считать, что семестр не может блится больше 52 недель. Если функция возвращает значение 53,
    # значит произошла ошибка
    for week_search in range (17, 54):
        response =  session.get(url_forms_tt + '?week=' + str(week_search))
        soup = BeautifulSoup(response.text, 'lxml')
        if re_search("№0 ", soup.h3.text):
            break
    return week_search

def get_all_timetable():
    url_forms_tt = 'https://lk.sut.ru/project/cabinet/forms/raspisanie.php'
    # объявлям list, в котором будут все записи
    tt_all=[]
    max_week = number_week_null()
    if max_week != 53:
        for week in range(1, max_week):
            response =  session.get(url_forms_tt + '?week=' + str(week))
            soup = BeautifulSoup(response.text, 'lxml')
            tt_week = [week, soup.h3.text[-27:-16], soup.h3.text[-13:-3]]
            # переходиим в таблицу с данными
            if soup.find("div", {"class": "alert alert-info"}, string="Занятий не найдено") == None:
                soup = soup.table
                soup = soup.tbody
                # Цикл для всех строк (записей) в таблице. Строки обособлены тегом <tr>, а у нужным нам строк
                # id начинается на tr. Находим таки строки с помощью регулярного выражения
                tt_day=[]
                day_number=-1
                for child_tr in soup.find_all("tr"):
                    if child_tr.get("style") != None:
                        day_number+=1
                        tt_day.append([child_tr.b.text, child_tr.small.text,[]])
                    else:
                        one_day=[]
                        num_td=0
                        for child_td in child_tr.find_all("td"):
                            if num_td == 1:
                                one_day.append(child_td.b.text)
                                # Костыль, как убрать не придумал
                                type_lesson=str(child_td.small)[7:-8]
                                one_day.append(type_lesson.split("<br/>")[0])
                            else:
                                one_day.append(child_td.text)
                            num_td+=1
                        tt_day[day_number][2].append(one_day)
                tt_week.append(tt_day)
            else:
                tt_week.append(None)
            tt_all.append(tt_week)
    else:
        tt_all=False
    return tt_all

session = req_session()
if auth_lk():
    #print(get_all_files_group()[0][5][1])
    timetable = get_all_timetable()
    if timetable:
        print(timetable[17])
    else:
        print('Произошла ошибка при парсинге расписания')
else:
    print('Авторизация неуспешна, проверьте параметры авторизации.')