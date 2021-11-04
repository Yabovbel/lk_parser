# lk_parser
SPbSUT personal account parser

-----
Необходимо установить библиотеки requests, bs4, lxml. Для этого нужно выполнить команду:
pip install (requests,) bs4, lxml, aiohttp

-----
Необходимо создать файл auth_params.py, где присвоить переменным LOGIN, PASSWORD действительные значения для авторизации. Пример данного файла:
LOGIN = 'test@yandex.ru'
PASSWORD = 'testTEST123'

-----
Парсинг файлов группы вызывается функцией get_all_files_group() и возвращает список, вида
get_all_files_group()[263][5][1], где
[263=номер записи, начиная с 0. Поэтому он будет на 1 меньше, чем реальный][5=номер столбца][1=номер ссылки начиная с 0. Параметр актуален, только если номер стобца равен 5]

Номера столбцов (нумерация начинается с 0):
    0-номер записи
    1-ФИО отправителя
    2-дата и время отправки
    3-дисциплина
    4-сообщение
    5-ссылка (в форме list)

get_all_files_group()-вернет полностью list со всеми записями

Примеры:
print(get_all_files_group()[0])
['1', 'Иванов Иван Иванович', '29-09-2021 14:01:02', 'Электротехника', '-', ['https://lk.sut.ru/cabinet/ini/subconto/sendto/101/9998877/document1.docx', 'https://lk.sut.ru/cabinet/ini/subconto/sendto/101/9998877/presentation2.ppt']]

print(get_all_files_group()[264][1])
Воронцов Артем Петрович

print(get_all_files_group()[0][5])
['https://lk.sut.ru/cabinet/ini/subconto/sendto/101/9998877/document1.docx', 'https://lk.sut.ru/cabinet/ini/subconto/sendto/101/9998877/presentation2.ppt']

print(get_all_files_group()[0][5][1])
https://lk.sut.ru/cabinet/ini/subconto/sendto/101/9998877/presentation2.ppt