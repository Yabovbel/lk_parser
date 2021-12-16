from bs4 import BeautifulSoup
from requests.sessions import session
from auth_params import *
from re import compile as re_comp, search as re_search, split as re_split
import asyncio
import time
from aiohttp import ClientSession, TCPConnector, ClientTimeout

async def auth_lk(session):
    # функция прохождения авторизации на портале. Если возвращает истину, то авторизация прошла успешно
    url_lk = 'https://lk.sut.ru/?login=yes'
    url_auth = 'https://lk.sut.ru/cabinet/lib/autentificationok.php'
    # представляемся сайту обычным браузером для того, чтоб пройти проверку на робота. Для этого прописываем
    # рандомный браузер в user-agent
    data = {
        'users': LOGIN,
        'parole': PASSWORD,
    }
    #session.headers==headers
    # просто загружаем страницу авторизации, чтоб открыть сессию на сервере. ХЗ зачем, но без этого
    # не работает
    await session.get(url_lk)
    # авторизируемся. Если в ответ получим 1, то значит все хорошо
    response = await session.post(url_auth, data=data)
    resp_t = await response.text()
    soup = BeautifulSoup(resp_t, 'lxml')
    # еще раз просто загрузаем страницу ЛК, иначе в дельнейшем у нас не будут грузится страницы для
    # парсинга. Она нам не нужна, но без ее загрузки ничего не работает. ХЗ почему, это ведь бонч.
    await session.get(url_lk)
    return soup.p.text == '1'

async def files_count_range(session):
    # функция подсчета количества страниц с файлами группам. Возвращает число страниц.
    url_forms_gr = 'https://lk.sut.ru/project/cabinet/forms/files_group_pr.php'
    response = await session.get(url_forms_gr)
    response_text = await response.text()
    soup = BeautifulSoup(response_text, 'lxml')
    soup = soup.find("span", id="table_mes")
    # номер последней страницы содержится внутри span в теге <a>, где строка " >> "
    child_span_a=soup.find("a", string=" >> ")
    # Нужное значение находится в строке в параметре onclick
    child_span_a=child_span_a.get("onclick")
    # Перед тем как вернуть, преобразуем значение в число
    files_count_range_result=int(child_span_a[-4:-2])
    return files_count_range_result

async def fetch_url_data(session, url_list_files_gr):
    async with session.get(url_list_files_gr, timeout=60) as response:
        resp = await response.text()
        soup = BeautifulSoup(resp, 'lxml')
        # переходиим в таблицу с данными
        soup = soup.find("table", id="mytable")
        soup = soup.tbody
        files_group=[]
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

async def fetch_async(loop):
    url_forms_gr = "https://lk.sut.ru/project/cabinet/forms/files_group_pr.php"
    tasks = []
    header_new = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }
    conn = TCPConnector(limit=5)
    timeout = ClientTimeout(total=60)
    async with ClientSession(headers=header_new, timeout=timeout, connector=conn) as session:
        auth_lk_result = await auth_lk(session)
        if auth_lk_result:
            async_files_count_range = await files_count_range(session)+1
            for page in range(1, async_files_count_range):
                task = asyncio.ensure_future(fetch_url_data(session, url_forms_gr + '?page=' + str(page)))
                tasks.append(task)
            responses = await asyncio.gather(*tasks)
            return [1, responses]
        else:
            return [0, 0]
    
def get_all_files_group():
    # функция парсинга файлов группы. Возвращает list с полученными занчениями
    # объявлям list, в котором будут все записи
    # files_group=[]
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_async(loop))
    # будет выполняться до тех пор, пока не завершится или не возникнет ошибка
    loop.run_until_complete(future)
    responses = future.result()
    if responses[0] == 1:
        new_mass=[]
        for get_all_tt_list in responses[1]:
            for get_all_tt_list_in in get_all_tt_list:
                new_mass.append(get_all_tt_list_in)
        responses[1]=new_mass
    return responses

async def async_get_week(session, week_pool, week_num):
    url_forms_tt = 'https://lk.sut.ru/project/cabinet/forms/raspisanie.php'
    week_search = week_num+week_pool*12+17
    print(222)
    async with session.get(url_forms_tt + '?week=' + str(week_search), timeout=60) as response:
        resp_t_nwn = await response.text()
        soup = BeautifulSoup(resp_t_nwn, 'lxml')
        # перебираем недели до тех пор, пока не найдет неделю, в заголовке которой сочетание "№0 "
        if re_search("№0 ", soup.h3.text):
            return week_search
    return 

async def async_get_all_timetable(session, week):
    # функция парсинга всего распиания. Возвращает list с полученными значениями
    url_forms_tt = 'https://lk.sut.ru/project/cabinet/forms/raspisanie.php'
    try:
        async with session.get(url_forms_tt + '?week=' + str(week), timeout=30) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'lxml')
            # объявляем и начинаем заполнять list, в котором будут данные одной недели. Указываем номер
            # недели, парсим начальную и конечную дату недели
            tt_week = [week, soup.h3.text[-27:-16], soup.h3.text[-13:-3]]
            # проверяем наличие занятий на неделе
            if soup.find("div", {"class": "alert alert-info"}, string="Занятий не найдено") == None:
                soup = soup.table
                soup = soup.tbody
                # объявляем list, котором будет инфа о всех днях
                tt_day=[]
                # считает номер текущего дня в неделе, для заполнения list
                day_number=-1
                # Цикл для всех строк в таблице. Строки обособлены тегом <tr>.
                for child_tr in soup.find_all("tr"):
                    # строки (в которых указана дата, а не занятие), которые начинают день имеют параметр
                    # style. По наличию его, мы их и различаем
                    if child_tr.get("style") != None:
                        day_number += 1
                        # добавляем новый день в list всех дней. Укзаываем название дня недели, дату и
                        # оставляем пустой list для заполнения занятиями
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
    except Exception as e:
        print(e)
    return tt_week

async def async_number_week_num(loop):
    tasks = []
    header_new = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }
    #timeout_cl = ClientTimeout(total=600)
    conn = TCPConnector(limit=5)
    timeout = ClientTimeout(total=60)
    async with ClientSession(headers=header_new, timeout=timeout, connector=conn) as session:
    # async with ClientSession(headers=header_new, timeout=60) as session:
        auth_lk_result = await auth_lk(session)
        if auth_lk_result:
            for week_search_pool in range (3):
                for week_search in range (12):
                    task = asyncio.ensure_future(async_get_week(session, week_search_pool, week_search))
                    tasks.append(task)
                responses = await asyncio.gather(*tasks)
                tasks=[]
                if not(all([x is None for x in responses])):
                    break
            for num_week in responses:
                if num_week != None:
                    break
            else:
                return [0, 1]
    return [1, num_week, session]

async def async_number_week_num_faza_two(loop, num_week, session):
    tasks = []
    # header_new = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    # }
    # #timeout_cl = ClientTimeout(total=600)
    # conn = TCPConnector(limit=5)
    # timeout = ClientTimeout(total=60)
    # async with ClientSession(headers=header_new, timeout=timeout, connector=conn) as session:
    # # async with ClientSession(headers=header_new, timeout=60) as session:
    #     auth_lk_result = await auth_lk(session)
    #     if auth_lk_result:
    for week in range(1, num_week):
        task = asyncio.ensure_future(async_get_all_timetable(session, week))
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses

def get_all_timetable():
    # функция определения номера нулевой недели. Возвращает номер недели.
    url_forms_tt = 'https://lk.sut.ru/project/cabinet/forms/raspisanie.php'
    # Минимально в семестре 17 недель, поэтому для оптимизации, недели раньше 17ой не просматриваются.
    # Будем считать, что семестр не может блится больше 52 недель. Если функция возвращает значение 53,
    # значит произошла ошибка
    # for week_search in range (17, 54):
    # for week_search_pool in range (3):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(async_number_week_num(loop))
    # будет выполняться до тех пор, пока не завершится или не возникнет ошибка
    loop.run_until_complete(future)
    responses = future.result()
    if responses[0]==1:
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(async_number_week_num_faza_two(loop, responses[1], responses[2]))
        # будет выполняться до тех пор, пока не завершится или не возникнет ошибка
        loop.run_until_complete(future)
    return responses

def print_get_tt():
    get_tt_res = get_all_timetable()
    come_time=time.time()
    if get_tt_res[0] == 1:
        get_tt_res=get_tt_res[1]
        print(get_tt_res)
    else:
        if get_tt_res[1] == 0:
            print('Error 0: Авторизация неуспешна, проверьте параметры авторизации.')
        elif get_tt_res[1] == 1:
            print('Error 1: Ошибка запроса количества учебных недель.')
    return come_time

def print_get_fg():
    get_fg_res = get_all_files_group()
    come_time=time.time()
    if get_fg_res[0] == 1:
        get_fg_res=get_fg_res[1]
        print(get_fg_res)
    else:
        if get_fg_res[1] == 0:
            print('Error 0: Авторизация неуспешна, проверьте параметры авторизации.')
    return come_time

#start_time=time.time()
#come_time=print_get_tt()
#come_time=print_get_tt()

print(get_all_timetable())

#print('Время выполнения запроса:', int((come_time-start_time)*1000), 'ms')
#print('Полное время обработки запроса:', int((time.time()-start_time)*1000), 'ms')