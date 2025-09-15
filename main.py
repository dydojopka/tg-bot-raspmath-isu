from dotenv import load_dotenv
import os
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from datetime import date, datetime, timedelta
import telebot
from telebot import types
import sqlite3
import threading
import time
import requests

load_dotenv()

# API-ключ
API_TOKEN = os.getenv("RASPMATH_API_KEY", "")
if not API_TOKEN:
    raise ValueError("RASPMATH_API_KEY не найден в .env")

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения.")
bot = telebot.TeleBot(TOKEN)


# # Инициализация драйвера Chrome
# ChromeDriverManager().install()
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# driver = webdriver.Chrome(options=chrome_options)

# # Блокировка для безопасной работы с драйвером в потоках
# driver_lock = threading.Lock()

# Словарь для кратких номеров групп: {краткий_номер: (полное_название, url_num)}
short_group_map = {
    # Курс 1
    "2121": ("02121-ДБ", 1),
    "2122": ("02122-ДБ", 2),
    "2123": ("02123-ДБ", 3),
    "2141": ("02141-ДБ", 4),
    "2161": ("02161-ДБ", 5),
    "2162": ("02162-ДБ", 6),
    "2171": ("02171-ДБ", 7),
    "2172": ("02172-ДБ", 8),
    "2181": ("02181-ДБ", 9),
    # Курс 2
    "2221": ("02221-ДБ", 10),
    "2222": ("02222-ДБ", 11),
    "2223": ("02223-ДБ", 12),
    "2241": ("02241-ДБ", 13),
    "2261": ("02261-ДБ", 14),
    "2262": ("02262-ДБ", 15),
    "2271": ("02271-ДБ", 16),
    "2272": ("02272-ДБ", 17),
    "2281": ("02281-ДБ", 18),
    # Курс 3
    "2321": ("02321-ДБ", 19),
    "2322": ("02322-ДБ", 20),
    "2323": ("02323-ДБ", 21),
    "2341": ("02341-ДБ", 22),
    "2361": ("02361-ДБ", 23),
    "2362": ("02362-ДБ", 24),
    "2371": ("02371-ДБ", 25),
    "2381": ("02381-ДБ", 26),
    # Курс 4
    "2421": ("02421-ДБ", 27),
    "2422": ("02422-ДБ", 28),
    "2441": ("02441-ДБ", 29),
    "2461": ("02461-ДБ", 30),
    "2471": ("02471-ДБ", 31),
    "2481": ("02481-ДБ", 50),
}

teacher_map = {
    "Айсанова Александра Андреевна",
    "Александрович Ольга Юрьевна",
    "Амбросов Николай Владимирович",
    "Антипина Екатерина Дмитриевна",
    "Антоник Владимир Георгиевич",
    "Аргучинцев Александр Валерьевич",
    "Балагура Анна Александровна",
    "Балашов Александр Викторович",
    "Болотов Андрей Валентинович",
    "Брагин Александр Евгеньевич",
    "Бринько Игорь Иванович",
    "Винокуров Сергей Федорович",
    "Вшивков Юрий Фёдорович",
    "Вырупаева Татьяна Владимировна", # их две: №99 и №112
    "Гаврилин Денис Николаевич",
    "Гаврилина Дарья Эдуардовна",
    "Гаер Максим Александрович",
    "Глебец Иван Владимирович",
    "Головко Елена Анатольевна",
    "Гончакук Даниил Евгеньевич", # их двое: №108 и №3
    "Гражданцева Елена Юрьевна",
    "Григорьев Станислав Валентинович",
    "Грицких Надежда Викторовна",
    "Грошева Надежда Борисовна",
    "Гуренков Андрей Александрович",
    "Деденко Михаил Михайлович",
    "Евдокимов Дмитрий Максимович",
    "Ермолаева Екатерина Валерьевна",
    "Захарова Ирина Валентиновна",
    "Захарченко Варвара Сергеевна",
    "Зинченко Анна Сергеевна",
    "Зубков Олег Владимирович",
    "Иванова Ана Леонидовна",
    "Ильин Борис Петрович",
    "Иов Роман Вадимович",
    "Казимиров Алексей Сергеевич",
    "Калинина Нина Викторовна",
    "Каратуева Нина Анатольевна", # их две: №98 и №109
    "Карелин Александр Геннадьевич",
    "Кедрин Виктор Сергеевич",
    "Кензин Максим Юрьевич",
    "Кириченко Константин Дмитриевич",
    "Колокольникова Наталья Арсеньевна",
    "Колпакиди Наталия Леонидовна",
    "Колпакиди Дмитрий Викторович",
    "Комаров Алексей Владимирович",
    "Копылова Наталья Юрьевна",
    "Косогова Анастасия Самсоновна",
    "Кривель Сергей Михайлович",
    "Кузьмин Олег Викторович",
    "Кузьмина Елена Юрьевна",
    "Курзыбова Яна Владимировна",
    "Лавлинский Максим Викторович",
    "Лашина Елена Борисовна",
    "Леонтьев Роман Юрьевич",
    "Ли-Дэ Даниил Игоревич",
    "Лохов Сергей Николаевич",
    "ЛЭТИ",
    "Малышева Мария Андреевна",
    "Мальчукова Нина Валерьевна",
    "Манцивода Андрей Валерьевич",
    "Мартьянов Владимир Иванович",
    "Массель Алексей Геннадьевич",
    "Метёлкина Лариса Николаевна",
    "Михайлов Андрей Анатольевич",
    "Московская Татьяна Эдуардовна,",
    "Мутовин Павел Николаевич",
    "Муценек Витус Евгеньевич",
    "Осипенко Лариса Анатольевна",
    "Пантелеев Владимир Иннокентьевич",
    "Парамонов Вячеслав Владимирович",
    "Пахомов Дмитрий Вячеславович",
    "Перязев Николай Алексеевич",
    "Петренко Павел Сергеевич",
    "Петрова Наталья Васильевна",
    "Петрушин Иван Сергеевич",
    "Плотникова Ирина Ивановна",
    "Поплевко Василиса Павловна",
    "Попова Виктория Алексеевна",
    "Рейнгольд Михаил Григорьевич",
    "Рябец Леонид Владимирович",
    "Салимов Борис Гудратович",
    "Салтыков Александр Сергеевич",
    "Самсонюк Ольга Николаевна",
    "Семенов Андрей Леонидович",
    "Серебренников Денис Александрович",
    "Серёдкина Александра Сергеевна",
    "Сидоров Денис Николаевич",
    "Слободняк Илья Анатольевич",
    "Сокольская Мария Александровна",
    "Солодуша Светлана Витальевна",
    "Сорокин Степан Павлович",
    "Срочко Владимир Андреевич",
    "Тагласов Эдуард Станиславович",
    "Тарасенко Василий Анатольевич",
    "Тобола Кирилл Владимирович",
    "Толстихин Антон Артемович",
    "Тюрнева Татьяна Геннадьевна",
    "Уланов Илья Викторович",
    "Фалалеев Михаил Валентинович",
    "Федоров Роман Константинович",
    "Фереферов Евгений Сергеевич",
    "Физическая культура и спорт",
    "Хамисов Олег Валерьевич",
    "Хара Алина",
    "Харахинов Владимир Александрович",
    "Черкашин Евгений Александрович", # их двое: №54 и №128
    "Шахова Ирина Савельевна",
    "Шеломенцева Наталья Николаевна",
    "Шеметова Людмила Николаевна",
    "Шигаров Алексей Олегович",
    "Шипилова Ольга Ивановна",
    "Шмелев Валерий Юрьевич",
    "Щербаков Алексей Борисович",
    "Элективные курсы по физической культуре и спорту",
    "Ямушева Ирина Валерьевна,",
}

# Получение локального времени
local_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ====== Работа с бд расписания ======

# Инициализация базы данных расписания
def init_db():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY,
            group_name TEXT NOT NULL,
            week_type TEXT NOT NULL,
            day INTEGER NOT NULL,
            lesson_number INTEGER NOT NULL,
            subject TEXT,
            teacher TEXT,
            classroom TEXT,
            timestamp DATETIME,
            UNIQUE(group_name, week_type, day, lesson_number)
        )
    ''')
    conn.commit()
    conn.close()

# Функция для сохранения расписания в базу данных
def save_schedule_to_db(group_name, week_type, schedule_data):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    try:
        # Удаляем старые записи для этой группы и недели
        cursor.execute("DELETE FROM schedule WHERE group_name = ? AND week_type = ?", 
                      (group_name, week_type))
        
        # Вставляем новые данные
        for day in range(6): # Пн-Сб
            for lesson_num in range(7): # 7 пар в день
                idx = lesson_num * 6 + day
                if idx < len(schedule_data['subject']):
                    subject = schedule_data['subject'][idx]
                    teacher = schedule_data['teacher'][idx]
                    classroom = schedule_data['clr'][idx]
                    
                    # Преобразуем "-----" в None для базы данных
                    subject = None if subject == '-----' else subject
                    teacher = None if teacher == '-----' else teacher
                    classroom = None if classroom == '-----' else classroom
                    
                    cursor.execute('''
                        INSERT INTO schedule 
                        (group_name, week_type, day, lesson_number, subject, teacher, classroom, timestamp) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (group_name, week_type, day, lesson_num, subject, teacher, classroom, local_timestamp))
        conn.commit()
    finally:
        conn.close()

# Функция для получения расписания из базы данных
def get_schedule_from_db(group_name, day):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT subject, teacher, classroom, MAX(timestamp)
            FROM schedule 
            WHERE group_name = ? AND day = ?
            GROUP BY lesson_number
            ORDER BY lesson_number
        ''', (group_name, day))

        results = cursor.fetchall()
        if results:
            subject, teacher, classroom, timestamp = [], [], [], []
            for subj, teach, clrm, ts in results:
                subject.append(subj if subj is not None else '-----')
                teacher.append(teach if teach is not None else '-----')
                classroom.append(clrm if clrm is not None else '-----')
                timestamp.append(ts)
            return {'subject': subject, 'teacher': teacher, 'clr': classroom, 'timestamp': timestamp}
        return None
    finally:
        conn.close()

# # Функция парсинга с сохранением в базу данных
# def parse_and_save_schedule(url_num, group_name):
#     data = {
#         'subject': [],
#         'teacher': [],
#         'clr': [],
#     }
#     top_week = True

#     try:
#         with driver_lock:
#             driver.get(f"https://raspmath.isu.ru/schedule/{url_num}")
#             soup = BeautifulSoup(driver.page_source, 'lxml')

#         # Определение текущей недели
#         active_li = soup.find('li', class_='active mr-3')
#         if active_li and active_li.find('a', class_="btn btn-primary2 top-week active"):
#             top_week = True
#             week_type = 'top'
#         else:
#             top_week = False
#             week_type = 'bottom'

#         tbody = soup.find('tbody')
#         if not tbody:
#             print(f"Не найдено расписание для группы: {group_name}")
#             return None

#         if top_week:
#             td_list = tbody.find_all('td', class_='td1')
#         else:
#             td_list = tbody.find_all('td', class_='td2')

#         for td in td_list:
#             if len(td) == 0:
#                 data['subject'].append('-----')
#                 data['teacher'].append('-----')
#                 data['clr'].append('-----')
#             else:
#                 if td.find('p', class_='nameHoliday h5 text-center'): 
#                     data['subject'].append('-----')
#                     data['teacher'].append('-----')
#                     data['clr'].append('-----')
#                 else:
#                     subject_el = td.find('div', class_='nameSubject')
#                     subject = subject_el.text.strip() if subject_el else '-----'
#                     data['subject'].append(subject)
                    
#                     teacher_el = td.find('div', class_='teacher sch-mt-1')
#                     teacher = teacher_el.text.strip() if teacher_el else '-----'
#                     data['teacher'].append(teacher)
                    
#                     clr_el = td.find('div', class_='classroom sch-mt-1')
#                     classroom = clr_el.text.strip() if clr_el else '-----'
#                     data['clr'].append(classroom)

#         # Сохраняем в базу данных
#         save_schedule_to_db(group_name, week_type, data)
#         return data
#     except Exception as e:
#         print(f"[!] Ошибка при парсинге для {group_name}: {e.msg}")
#         return None
    
# Функция для получения расписания (из базы или парсинга)
def get_schedule(group_name, url_num):
    day = date.today().weekday()
    if day == 6:
        return {'subject': [], 'teacher': [], 'clr': [], 'timestamp': []} # пустое расписание для воскресенья

    schedule_data = get_schedule_from_db(group_name, day)
    if not schedule_data:
        week_dates = get_week_date_range()
        fetch_and_save_group_schedule(group_name, week_dates)
        schedule_data = get_schedule_from_db(group_name, day)

    return schedule_data


# ====== Работа с бд настроек пользователей ======

# Инициализация базы данных настроек пользователей
def init_user_settings_db():
    conn = sqlite3.connect('user_settings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            mode TEXT CHECK(mode IN ('full', 'short')) NOT NULL DEFAULT 'full',
            search_mode TEXT CHECK(search_mode IN ('group', 'teacher')) NOT NULL DEFAULT 'group'
        )
    ''')
    conn.commit()
    conn.close()


def get_user_mode(username):
    conn = sqlite3.connect('user_settings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT mode FROM user_settings WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 'full'

def toggle_user_mode(username):
    conn = sqlite3.connect('user_settings.db')
    cursor = conn.cursor()
    current = get_user_mode(username)
    new_mode = 'short' if current == 'full' else 'full'
    cursor.execute('REPLACE INTO user_settings (username, mode) VALUES (?, ?)', (username, new_mode))
    conn.commit()
    conn.close()
    return new_mode

def get_user_search_mode(username):
    conn = sqlite3.connect('user_settings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT search_mode FROM user_settings WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] in ['group', 'teacher'] else 'group'

def set_user_search_mode(username, search_mode):
    if search_mode not in ['group', 'teacher']:
        return
    conn = sqlite3.connect('user_settings.db')
    cursor = conn.cursor()
    # Проверка: есть ли уже запись?
    cursor.execute('SELECT username FROM user_settings WHERE username = ?', (username,))
    if cursor.fetchone():
        cursor.execute('UPDATE user_settings SET search_mode = ? WHERE username = ?', (search_mode, username))
    else:
        cursor.execute('INSERT INTO user_settings (username, mode, search_mode) VALUES (?, "full", ?)', (username, search_mode))
    conn.commit()
    conn.close()


# ====== Работа с бд преподователей ======

# Инициализация базы данных преподователей
def init_teacher_db():
    conn = sqlite3.connect('teacher_schedule.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher TEXT NOT NULL,
            group_name TEXT NOT NULL,
            date TEXT NOT NULL,
            weekday TEXT,
            pair_start_time TEXT,
            pair_end_time TEXT,
            subject_name TEXT,
            pair_type TEXT,
            classroom TEXT,
            week_type TEXT,
            last_updated TEXT,
            UNIQUE(teacher, group_name, date, pair_start_time)
        )
    ''')
    conn.commit()
    conn.close()

# Функция запроса и записи расписания групп
def fetch_and_save_group_schedule(group_name, target_dates):
    url = "https://raspmath.isu.ru/getScheduleForTest"
    headers = {"x-access-token": API_TOKEN}

    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()

    # Удаляем старые записи для группы
    cursor.execute("DELETE FROM schedule WHERE group_name = ?", (group_name,))
    conn.commit()

    for target_date in target_dates:
        payload = {
            "date": target_date,
            "group": group_name,
            "teacher": ""
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()

            for row in data:
                weekday = row.get("weekday")
                day = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота"].index(weekday) if weekday in ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота"] else None
                if day is None:
                    continue

                # Определяем номер пары
                lesson_number = {
                    "8.30": 0, "10.10": 1, "11.50": 2,
                    "13.50": 3, "15.30": 4, "17.10": 5, "18.50": 6
                }.get(row.get("pair_start_time"), None)

                cursor.execute('''
                    INSERT OR REPLACE INTO schedule
                    (group_name, week_type, day, lesson_number, subject, teacher, classroom, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get("group_name"),
                    row.get("week_type") or "",
                    day,
                    lesson_number if lesson_number is not None else -1,
                    row.get("subject_name"),
                    row.get("teacher"),
                    row.get("class_name"),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))

            conn.commit()
        except Exception as e:
            print(f"[!] Ошибка при запросе расписания для группы {group_name} на дату {target_date}: {str(e)}")

    conn.close()


# Функция запроса и записи расписания преподавателя
def fetch_and_save_teacher_schedule(teacher_name, target_dates):
    url = "https://raspmath.isu.ru/getScheduleForTest"
    headers = {"x-access-token": API_TOKEN}

    conn = sqlite3.connect("teacher_schedule.db")
    cursor = conn.cursor()

    # Удаляем все старые записи для данного преподавателя
    cursor.execute('''
        DELETE FROM teacher_schedule 
        WHERE teacher = ?
    ''', (teacher_name,))
    conn.commit()

    # --- Запрос и добавление новых записей ---
    for target_date in target_dates:
        payload = {
            "date": target_date,
            "teacher": teacher_name,
            "group": ""
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            for row in data:
                cursor.execute('''
                    INSERT OR REPLACE INTO teacher_schedule (
                        teacher, group_name, date, weekday, pair_start_time, pair_end_time,
                        subject_name, pair_type, classroom, week_type, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get("teacher"),
                    row.get("group_name"),
                    target_date,
                    row.get("weekday"),
                    row.get("pair_start_time"),
                    row.get("pair_end_time"),
                    row.get("subject_name"),
                    row.get("pair_type"),
                    row.get("class_name"),
                    row.get("week_type"),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))

            conn.commit()
        except Exception as e:
            print(f"[!] Ошибка при запросе расписания для преподавателя {teacher_name} на дату {target_date}: {str(e)}")

    conn.close()


# Функция для вычисления диапазона дат для текущей и следующей недели
def get_week_date_range():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=13)  # 2 недели
    
    dates = []
    current = start_of_week
    while current <= end_of_week:
        dates.append(current.isoformat())
        current += timedelta(days=1)
    
    return dates


# Функция для фонового обновления базы данных
def update_database():
    while True:
        print(f"{datetime.now()} - Начало обновления базы данных...")

        # --- Обновление расписания групп ---
        week_dates = get_week_date_range()
        for group_short, (group_name, _) in short_group_map.items():
            try:
                print(f"{datetime.now().time()} - Обновление для группы: {group_name}")
                fetch_and_save_group_schedule(group_name, week_dates)
                time.sleep(0.5)  # Пауза между запросами
            except Exception as e:
                print(f"[!] Ошибка при обновлении группы {group_name}: {str(e)}")
        print(f"{datetime.now()} - Обновление бд расписания групп завершено")

        # --- Обновление расписания преподавателей ---
        print(f"{datetime.now()} - Начало обновления расписания преподавателей...")

        # Получаем все даты для текущей и следующей недели
        week_dates = get_week_date_range()

        for teacher in teacher_map:
            try:
                print(f"{datetime.now().time()} - Обновление для преподавателя: {teacher}")
                fetch_and_save_teacher_schedule(teacher, week_dates)
                time.sleep(0.5)
            except Exception as e:
                print(f"[!] Ошибка при обновлении расписания для преподавателя {teacher}: {str(e)}")

        print(f"{datetime.now()} - Обновление бд расписания преподавателей завершено")

        time.sleep(21600)  # Раз в 6 часов


# Запуск фонового потока для обновления базы
update_thread = threading.Thread(target=update_database, daemon=True)
update_thread.start()


# Список с преподавателями в инлайн-кнопках
TEACHERS_PER_PAGE = 10
teacher_list = sorted(list(teacher_map))

def show_teacher_page(chat_id, page=0, message_id=None):
    total_pages = max(1, (len(teacher_list) - 1) // TEACHERS_PER_PAGE + 1)
    start = page * TEACHERS_PER_PAGE
    end = start + TEACHERS_PER_PAGE
    teachers_on_page = teacher_list[start:end]

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    for idx in range(start, min(end, len(teacher_list))):
        teacher_name = teacher_list[idx]
        keyboard.add(types.InlineKeyboardButton(teacher_name, callback_data=f"select_teacher:{idx}"))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"teacher_page:{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton("➡️ Далее", callback_data=f"teacher_page:{page + 1}"))
    
    if nav_buttons:
        keyboard.row(*nav_buttons)
    
    message_text = "Выберите преподавателя ниже:"
    
    # Редактируем существующее сообщение, если оно есть
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=message_text,
                                  reply_markup=keyboard)
        except Exception as e:
            print(f"[!] Ошибка редактирования: {e}")
            bot.send_message(chat_id, message_text, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, message_text, reply_markup=keyboard)


# Обработчик инлайн-кнопок для перелистывания
@bot.callback_query_handler(func=lambda call: call.data.startswith("teacher_page:"))
def handle_teacher_pagination(call):
    page = int(call.data.split(":")[1])
    # Передаем ID сообщения для редактирования
    show_teacher_page(call.message.chat.id, page, call.message.message_id)


# Формаирование сообщения расписания группы
def send_schedule(message, schedule_data, group_name, day=None, edit=False, message_id=None, force_mode=None):
    from datetime import date
    from telebot import types

    def get_username(msg):
        return msg.from_user.username or str(msg.chat.id)

    tday = day if day is not None else date.today().weekday()
    username = message.from_user.username or str(message.chat.id)
    mode = force_mode or get_user_mode(username)

    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    lesson_times = [
        "08.30-10.00", 
        "10.10-11.40", 
        "11.50-13.20",
        "13.50-15.20", 
        "15.30-17.00", 
        "17.10-18.40", 
        "18.50-20.20"
    ]
    day_name = days[tday] if tday < len(days) else f"День {tday}"

    if tday == 6:
        msg = f"🗓️ _{day_name} - {group_name}_\nСегодня воскресенье — пар нет.\n"
    else:
        msg = f"🗓️ _{day_name} - {group_name}_\n"
        
        # Если режим 'full' — показываем все пары
        if mode == 'full':
            for i in range(7):
                if i < len(schedule_data['subject']):
                    subject = schedule_data['subject'][i] or '-----'
                    teacher = schedule_data['teacher'][i] or '-----'
                    classroom = schedule_data['clr'][i] or '-----'
                    msg += f"⌚*{lesson_times[i]}:*\n    ⌊📖{subject}\n    ⌊🧑‍🏫{teacher}\n    ⌊🚪{classroom}\n"
        
        # Если режим 'short' — показываем только непустые пары
        elif mode == 'short':
            for i in range(7):
                if i < len(schedule_data['subject']) and schedule_data['subject'][i] != '-----':
                    subject = schedule_data['subject'][i]
                    teacher = schedule_data['teacher'][i]
                    classroom = schedule_data['clr'][i]
                    msg += f"⌚*{lesson_times[i]}:*\n    ⌊📖{subject}\n    ⌊🧑‍🏫{teacher}\n    ⌊🚪{classroom}\n"

        if schedule_data.get('timestamp'):
            last_updated = max(schedule_data['timestamp'])
            msg += f"\n ⚠️`Последнее обновление:{last_updated}`"

    # Кнопки
    keyboard = types.InlineKeyboardMarkup()

    # --- Кнопка переключения режима ---
    switch_label = f"🔄 Отображение: {'Полное' if mode == 'full' else 'Краткое'}"
    switch_label = f"🔄 Отображение: {'Полное' if mode == 'full' else 'Краткое'}"
    keyboard.add(types.InlineKeyboardButton(switch_label, callback_data=f"toggle_mode_g:{group_name}:{tday}"))

    # --- Кнопки навигации по дням ---
    if tday == 0:
        keyboard.add(types.InlineKeyboardButton("➡️ Завтра", callback_data=f"day:{group_name}:{tday + 1}"))
    elif tday == 6 or tday == 5:
        keyboard.add(types.InlineKeyboardButton("⬅️ Вчера", callback_data=f"day:{group_name}:{tday - 1}"))
    else:
        keyboard.add(
            types.InlineKeyboardButton("⬅️ Вчера", callback_data=f"day:{group_name}:{tday - 1}"),
            types.InlineKeyboardButton("➡️ Завтра", callback_data=f"day:{group_name}:{tday + 1}")
        )

    # Отправка
    if edit:
        try:
           # Только если текст отличается — редактировать
            if message.text != msg:
                bot.edit_message_text(chat_id=message.chat.id, message_id=message_id,
                                      text=msg, reply_markup=keyboard, parse_mode='Markdown')
        except Exception as e:
           print(f"[!] Ошибка редактирования сообщения: {e}")
    else:
        bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode='Markdown')


# Cловарь для преобразования имени преподавателя в индекс
teacher_to_index = {teacher: idx for idx, teacher in enumerate(teacher_list)}

# Формаирование сообщения расписания преподователя
def send_teacher_schedule(message, teacher_name, target_date=None, edit=False, message_id=None):
    from datetime import date, timedelta
    
    if target_date is None:
        target_date = date.today()
    else:
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
    
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=12)
    
    if target_date < start_of_week:
        target_date = start_of_week
    elif target_date > end_of_week:
        target_date = end_of_week
    
    if target_date.weekday() == 6:
        target_date += timedelta(days=1)
        if target_date > end_of_week:
            target_date = end_of_week
    
    day_of_week = target_date.weekday()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day_name = days[day_of_week]
    
    username = message.from_user.username or str(message.chat.id)
    mode = get_user_mode(username)
    date_str = target_date.isoformat()
    teacher_index = teacher_to_index.get(teacher_name, 0)

    conn = sqlite3.connect('teacher_schedule.db')
    cursor = conn.cursor()
    
    # Получаем данные о занятиях
    cursor.execute('''
        SELECT subject_name, group_name, pair_start_time, pair_end_time, classroom, pair_type
        FROM teacher_schedule
        WHERE teacher = ? AND date = ?
        ORDER BY pair_start_time
    ''', (teacher_name, date_str))
    results = cursor.fetchall()
    
    # Получаем время последнего обновления
    cursor.execute('''
        SELECT MAX(last_updated)
        FROM teacher_schedule
        WHERE teacher = ? AND date = ?
    ''', (teacher_name, date_str))
    max_update = cursor.fetchone()[0]
    
    conn.close()

    msg = f"🗓️ _{day_name} - {teacher_name}_\n📅 _{target_date.strftime('%d.%m.%Y')}\n_"
    
    if not results:
        msg += "Пар нет на этот день.\n"
    else:
        for row in results:
            subject_name, group_name, start_time, end_time, classroom, pair_type = row
            time_str = f"{start_time}-{end_time}" if start_time and end_time else "??:??-??:??"
            
            # Добавляем префикс типа занятия
            prefix = ""
            if pair_type == "практика":
                prefix = "пр. "
            elif pair_type == "лекция":
                prefix = "лек. "
            elif pair_type == "лабораторная":
                prefix = "лаб. "
            
            # Форматируем название предмета
            subject_display = f"{prefix}{subject_name}" if subject_name else "-----"
            
            if mode == 'full' or (mode == 'short' and subject_name and subject_name.strip() != '-----'):
                msg += f"⌚ *{time_str}:*\n"
                msg += f"    ⌊📖 {subject_display}\n"
                msg += f"    ⌊👥 {group_name}\n"
                msg += f"    ⌊🚪 {classroom}\n"
        
    if max_update:
        msg += f"\n⚠️`Последнее обновление:{max_update}`"

    # Остальной код без изменений...
    keyboard = types.InlineKeyboardMarkup()
    
    prev_date = target_date - timedelta(days=1)
    next_date = target_date + timedelta(days=1)
    
    if prev_date.weekday() == 6:
        prev_date -= timedelta(days=1)
    if next_date.weekday() == 6:
        next_date += timedelta(days=1)
    
    show_prev = prev_date >= start_of_week
    show_next = next_date <= end_of_week
    
    buttons = []
    if show_prev:
        buttons.append(types.InlineKeyboardButton("⬅️ Вчера", callback_data=f"t_day:{teacher_index}:{prev_date.isoformat()}"))
    if show_next:
        buttons.append(types.InlineKeyboardButton("Завтра ➡️", callback_data=f"t_day:{teacher_index}:{next_date.isoformat()}"))
    
    if buttons:
        keyboard.row(*buttons)

    if edit:
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=msg,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Ошибка редактирования: {e}")
    else:
        bot.send_message(
            message.chat.id,
            msg,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

# Обработчик выбора преподавателя
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_teacher:"))
def handle_teacher_select(call):
    index = int(call.data.split(":")[1])
    teacher_name = teacher_list[index]
    bot.answer_callback_query(call.id)
    
    send_teacher_schedule(
        message=call.message,
        teacher_name=teacher_name,
        edit=True,
        message_id=call.message.message_id
    )

# Обработчики для кнопок преподавателя
@bot.callback_query_handler(func=lambda call: call.data.startswith("t_day:"))
def handle_teacher_day_navigation(call):
    try:
        parts = call.data.split(":")
        teacher_index = int(parts[1])
        date_str = parts[2]
        teacher_name = teacher_list[teacher_index]
        send_teacher_schedule(
            message=call.message,
            teacher_name=teacher_name,
            target_date=date_str,
            edit=True,
            message_id=call.message.message_id
        )
    except Exception as e:
        print(f"[!] Ошибка навигации: {str(e)}")
        bot.answer_callback_query(call.id, "Ошибка обработки запроса")

# Обработать нажатия на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith("day:"))
def handle_day_navigation(call):
    # --- Кнопки перелистывания дня ---
    try:
        _, group_name, day_str = call.data.split(":")
        day = int(day_str)
        day = max(0, min(5, day))  # Ограничение Пн-Сб (0-5)

        # Найти short_group_map по полному названию
        url_num = None
        for short, (full, url) in short_group_map.items():
            if full == group_name:
                url_num = url
                break

        if url_num is None:
            bot.answer_callback_query(call.id, "Группа не найдена")
            return

        schedule_data = get_schedule_from_db(group_name, day)
        if schedule_data:
            username = call.from_user.username or str(call.message.chat.id)
            mode = get_user_mode(username)
            send_schedule(call.message, schedule_data, group_name, day=day, edit=True, message_id=call.message.message_id, force_mode=mode)
        else:
            bot.answer_callback_query(call.id, "Нет данных на выбранный день")
    except Exception as e:
        print(f"[!] Ошибка в handle_day_navigation: {e}")
        bot.answer_callback_query(call.id, "Ошибка обработки")


# Обработчик для групп
@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_mode_g:"))
def handle_group_mode_toggle(call):
    try:
        _, group_name, day_str = call.data.split(":")
        day = int(day_str)
        username = call.from_user.username or str(call.message.chat.id)
        new_mode = toggle_user_mode(username)

        schedule_data = get_schedule_from_db(group_name, day)
        send_schedule(call.message, schedule_data, group_name, day=day, 
                      edit=True, message_id=call.message.message_id, force_mode=new_mode)
        
        bot.answer_callback_query(call.id, f"Режим: {'Полный' if new_mode == 'full' else 'Краткий'}")
    except Exception as e:
        print(f"[!] Ошибка переключения режима группы: {e}")
        bot.answer_callback_query(call.id, "Ошибка переключения")

# Обработчик для преподавателей
@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_mode_t:"))
def handle_teacher_mode_toggle(call):
    try:
        parts = call.data.split(":")
        teacher_index = int(parts[1])
        date_str = parts[2]
        teacher_name = teacher_list[teacher_index]
        username = call.from_user.username or str(call.message.chat.id)
        new_mode = toggle_user_mode(username)
        
        send_teacher_schedule(
            message=call.message,
            teacher_name=teacher_name,
            target_date=date_str,
            edit=True,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id, f"Режим: {'Полный' if new_mode == 'full' else 'Краткий'}")
    except Exception as e:
        print(f"[!] Ошибка переключения режима преподавателя: {e}")
        bot.answer_callback_query(call.id, "Ошибка переключения")

# Обработчик выбора преподавателя по имени
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_teacher_by_name:"))
def handle_teacher_select_by_name(call):
    teacher_name = call.data.split(":", 1)[1]
    bot.answer_callback_query(call.id)
    
    send_teacher_schedule(
        message=call.message,
        teacher_name=teacher_name,
        edit=True,
        message_id=call.message.message_id
    )
    

# Команда /start
@bot.message_handler(commands=['start'])
def button_message(message):
    username = message.from_user.username or str(message.chat.id)
    set_user_search_mode(username, 'group')  # Сбрасываем режим поиска
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    c1 = types.KeyboardButton("Курс 1")
    c2 = types.KeyboardButton("Курс 2")
    c3 = types.KeyboardButton("Курс 3")
    c4 = types.KeyboardButton("Курс 4")
    t_search = types.KeyboardButton("Поиск по преподавателю")
    
    markup.add(c1, c2)
    markup.add(c3, c4)
    markup.add(t_search)
    bot.send_message(message.chat.id, 'Выбери курс\nЧтобы вернуться на главную - отправь /start', reply_markup=markup)

# Обработка сообщений
def set_user_mode(username, mode):
    conn = sqlite3.connect('user_settings.db')
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO user_settings (username, mode) VALUES (?, ?)', (username, mode))
    conn.commit()
    conn.close()

@bot.message_handler(content_types='text')
def message_reply(message):
    user_input = message.text.strip()
    user_input_lower = user_input.lower()
    username = message.from_user.username or str(message.chat.id)
    mode = get_user_mode(username)
    search_mode = get_user_search_mode(username)
    day = date.today().weekday()

    # --- Возврат на главную ---
    if user_input_lower == "вернуться на главную":
        set_user_search_mode(username, 'group')  # Переключаем на режим поиска по группам
        # Убираем текущую клавиатуру и показываем главное меню
        bot.send_message(message.chat.id, "Возвращаемся на главную...", reply_markup=types.ReplyKeyboardRemove())
        button_message(message)  # Показываем главное меню с исходной клавиатурой
        return

    # --- Переключение в режим поиска по преподавателям ---
    if user_input_lower == "поиск по преподавателю":
        set_user_search_mode(username, 'teacher')  # Переключаем на режим поиска преподавателей
        # Убираем текущую клавиатуру и устанавливаем клавиатуру для выбора преподавателей
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Вернуться на главную"))
        # Показываем список преподавателей
        show_teacher_page(message.chat.id, page=0)
        bot.send_message(message.chat.id, "Выберите преподавателя или введите ФИО вручную", reply_markup=markup)
        return

    # --- Режим преподавателя ---
    if search_mode == 'teacher':
        # Исправленный вызов без параметра day
        if user_input in teacher_map:
            send_teacher_schedule(message=message, teacher_name=user_input)
        else:
            # Добавим поиск по частичному совпадению
            found_teachers = [t for t in teacher_map if user_input.lower() in t.lower()]
            
            if len(found_teachers) == 1:
                send_teacher_schedule(message=message, teacher_name=found_teachers[0])
            elif len(found_teachers) > 1:
                # Предложим выбор из нескольких преподавателей
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                for teacher in found_teachers:
                    keyboard.add(types.InlineKeyboardButton(teacher, callback_data=f"select_teacher_by_name:{teacher}"))
                
                bot.send_message(
                    message.chat.id,
                    "Найдено несколько преподавателей. Выберите нужного:",
                    reply_markup=keyboard
                )
            else:
                bot.send_message(message.chat.id, "Преподаватель не найден. Попробуйте выбрать из списка или введите ФИО точно.")
        return

    # --- Режим поиска по группам ---
    group_input = user_input.strip()

    # --- Обработка курсов ---
    if user_input_lower in ["курс 1", "курс1"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(name) for name in [
            "02121-ДБ",
            "02122-ДБ",
            "02123-ДБ",
            "02141-ДБ",
            "02161-ДБ",
            "02162-ДБ",
            "02171-ДБ",
            "02172-ДБ",
            "02181-ДБ"
        ]])
        markup.add(types.KeyboardButton("Вернуться на главную"))
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
        return

    elif user_input_lower in ["курс 2", "курс2"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(name) for name in [
            "02221-ДБ",
            "02222-ДБ",
            "02223-ДБ",
            "02241-ДБ",
            "02261-ДБ",
            "02262-ДБ",
            "02271-ДБ",
            "02272-ДБ",
            "02281-ДБ"
        ]])
        markup.add(types.KeyboardButton("Вернуться на главную"))
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
        return

    elif user_input_lower in ["курс 3", "курс3"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(name) for name in [
            "02321-ДБ",
            "02322-ДБ",
            "02323-ДБ",
            "02341-ДБ",
            "02361-ДБ",
            "02362-ДБ",
            "02371-ДБ",
            "02381-ДБ"
        ]])
        markup.add(types.KeyboardButton("Вернуться на главную"))
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
        return

    elif user_input_lower in ["курс 4", "курс4"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(name) for name in [
            "02421-ДБ",
            "02422-ДБ",
            "02441-ДБ",
            "02461-ДБ",
            "02471-ДБ",
            "02481-ДБ"
        ]])
        markup.add(types.KeyboardButton("Вернуться на главную"))
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
        return

    # --- Поиск по краткому номеру группы ---
    if group_input in short_group_map:
        full_name, url_num = short_group_map[group_input]
        schedule_data = get_schedule(full_name, url_num)
        send_schedule(message, schedule_data or {'subject': [], 'teacher': [], 'clr': [], 'timestamp': []},
                      full_name, day=day, force_mode=mode)
        return

    # --- Поиск по полному названию группы ---
    input_upper = group_input.upper()
    for short, (full, url) in short_group_map.items():
        if input_upper == full.upper():
            schedule_data = get_schedule(full, url)
            send_schedule(message, schedule_data or {'subject': [], 'teacher': [], 'clr': [], 'timestamp': []},
                          full, day=day, force_mode=mode)
            return

    # --- Если ничего не найдено ---
    bot.send_message(message.chat.id, "Группа не найдена. Попробуйте ещё раз или выберите курс.")
    print(f"{datetime.now().time()} - Запрос от: {message.from_user.username}")



init_db()
init_user_settings_db()
init_teacher_db()

bot.infinity_polling()