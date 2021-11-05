import asyncio
import time

from requests.sessions import Session
from auth_params import *
from aiohttp import ClientSession, ClientResponseError
from bs4 import BeautifulSoup

async def auth_lk(session):
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
    #session.headers.update(headers)
    # просто загружаем страницу авторизации, чтоб открыть сессию на сервере. ХЗ зачем, но без этого
    # не работает
    await session.get(url_lk, headers=headers)
    # авторизируемся. Если в ответ получим 1, то значит все хорошо
    response = await session.post(url_auth, data=data)
    resp_t = await response.text()
    soup = BeautifulSoup(resp_t, 'lxml')
    # еще раз просто загрузаем страницу ЛК, иначе в дельнейшем у нас не будут грузится страницы для
    # парсинга. Она нам не нужна, но без ее загрузки ничего не работает. ХЗ почему, это ведь бонч.
    await session.get(url_lk)
    return soup.p.text == '1'

async def fetch_url_data(session, url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }
    async with session.get(url, headers=headers, timeout=30) as response:
        resp = await response.text()
    resp2 = BeautifulSoup(resp, 'lxml')
    #print(resp2)
    #print(session)
    return resp2


async def fetch_async(loop, r):
    url = "https://lk.sut.ru/project/cabinet/forms/files_group_pr.php"
    tasks = []
    async with ClientSession() as session:
        #print(session)
        await auth_lk(session)
        for i in range(r):
            task = asyncio.ensure_future(fetch_url_data(session, url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses


if __name__ == '__main__':
    for ntimes in [15]:
        start_time = time.time()
        data=[]
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_async(loop, ntimes))
        # будет выполняться до тех пор, пока не завершится или не возникнет ошибка
        loop.run_until_complete(future)
        responses = future.result()
        #print(responses)
        print(f'Получено {ntimes} результатов запроса за {time.time() - start_time} секунд')