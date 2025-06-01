from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date, datetime, timezone
import telebot
from telebot import types
import sqlite3
import threading
import time

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения.")
bot = telebot.TeleBot(TOKEN)

# Инициализация драйвера Chrome
ChromeDriverManager().install()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# Блокировка для безопасной работы с драйвером в потоках
driver_lock = threading.Lock()

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

# Получение локального времени
local_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# -------- Работа с бд расписания --------

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
        for day in range(6):  # Пн-Сб
            for lesson_num in range(7):  # 7 пар в день
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


# Функция парсинга с сохранением в базу данных
def parse_and_save_schedule(url_num, group_name):
    print(f"{datetime.now().time()} - Парсинг для: {group_name}")
    
    data = {
        'subject': [],
        'teacher': [],
        'clr': [],
    }
    top_week = True

    try:
        with driver_lock:
            driver.get(f"https://raspmath.isu.ru/schedule/{url_num}")
            soup = BeautifulSoup(driver.page_source, 'lxml')

        # Определение текущей недели
        active_li = soup.find('li', class_='active mr-3')
        if active_li and active_li.find('a', class_="btn btn-primary2 top-week active"):
            top_week = True
            week_type = 'top'
        else:
            top_week = False
            week_type = 'bottom'

        tbody = soup.find('tbody')
        if not tbody:
            print(f"Не найдено расписание для группы: {group_name}")
            return None

        if top_week:
            td_list = tbody.find_all('td', class_='td1')
        else:
            td_list = tbody.find_all('td', class_='td2')

        for td in td_list:
            if len(td) == 0:
                data['subject'].append('-----')
                data['teacher'].append('-----')
                data['clr'].append('-----')
            else:
                if td.find('p', class_='nameHoliday h5 text-center'): 
                    data['subject'].append('-----')
                    data['teacher'].append('-----')
                    data['clr'].append('-----')
                else:
                    subject_el = td.find('div', class_='nameSubject')
                    subject = subject_el.text.strip() if subject_el else '-----'
                    data['subject'].append(subject)
                    
                    teacher_el = td.find('div', class_='teacher sch-mt-1')
                    teacher = teacher_el.text.strip() if teacher_el else '-----'
                    data['teacher'].append(teacher)
                    
                    clr_el = td.find('div', class_='classroom sch-mt-1')
                    classroom = clr_el.text.strip() if clr_el else '-----'
                    data['clr'].append(classroom)

        # Сохраняем в базу данных
        save_schedule_to_db(group_name, week_type, data)
        return data
    except Exception as e:
        print(f"Ошибка при парсинге для {group_name}: {e.msg}")
        return None
    
# Функция для получения расписания (из базы или парсинга)
def get_schedule(group_name, url_num):
    day = date.today().weekday()
    if day == 6:
        return {'subject': [], 'teacher': [], 'clr': [], 'timestamp': []}  # пустое расписание для воскресенья

    schedule_data = get_schedule_from_db(group_name, day)
    if not schedule_data:
        schedule_data = parse_and_save_schedule(url_num, group_name)

    return schedule_data

# Функция для фонового обновления базы данных
def update_database():
    while True:
        print(f"{datetime.now()} - Начало обновления базы данных")
        for group_short, (group_name, url_num) in short_group_map.items():
            try:
                print(f"Обновление для группы: {group_name}")
                parse_and_save_schedule(url_num, group_name)
                time.sleep(2)  # Пауза между запросами
            except Exception as e:
                print(f"Ошибка при обновлении группы {group_name}: {str(e)}")
        
        print(f"{datetime.now()} - Обновление завершено")
        time.sleep(3600)  # 10 минут

# Запуск фонового потока для обновления базы
update_thread = threading.Thread(target=update_database, daemon=True)
update_thread.start()

# -------- Работа с бд настроек пользователей --------

def init_user_settings_db():
    conn = sqlite3.connect('user_settings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            mode TEXT CHECK(mode IN ('full', 'short')) NOT NULL DEFAULT 'full'
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


# Команда /start
@bot.message_handler(commands=['start'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    c1 = types.KeyboardButton("Курс 1")
    c2 = types.KeyboardButton("Курс 2")
    c3 = types.KeyboardButton("Курс 3")
    c4 = types.KeyboardButton("Курс 4")
    markup.add(c1)
    markup.add(c2)
    markup.add(c3)
    markup.add(c4)
    bot.send_message(message.chat.id, 'Выбери курс\nЧтобы вернуться на главную - отправь /start', reply_markup=markup)

# Формаирование сообщения
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
                    msg += f"⌚*{lesson_times[i]}:*\n    ⌊📖{subject}\n    ⌊👤{teacher}\n    ⌊🚪{classroom}\n"
        
        # Если режим 'short' — показываем только непустые пары
        elif mode == 'short':
            for i in range(7):
                if i < len(schedule_data['subject']) and schedule_data['subject'][i] != '-----':
                    subject = schedule_data['subject'][i]
                    teacher = schedule_data['teacher'][i]
                    classroom = schedule_data['clr'][i]
                    msg += f"⌚*{lesson_times[i]}:*\n    ⌊📖{subject}\n    ⌊👤{teacher}\n    ⌊🚪{classroom}\n"

        if schedule_data.get('timestamp'):
            last_updated = max(schedule_data['timestamp'])
            msg += f"\n ⚠️`Последнее обновление:{last_updated}`"

    # Кнопки
    keyboard = types.InlineKeyboardMarkup()

    # Кнопка переключения режима
    switch_label = f"🔄 Отображение: {'Полное' if mode == 'full' else 'Краткое'}"
    keyboard.add(types.InlineKeyboardButton(switch_label, callback_data=f"toggle_mode:{group_name}:{tday}"))

    # Кнопки навигации по дням
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
           print(f"Ошибка редактирования сообщения: {e}")
    else:
        bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode='Markdown')


# Обработать нажатия на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith("day:"))
def handle_day_navigation(call):
    # Кнопки перелистывания дня
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
        print(f"Ошибка в handle_day_navigation: {e}")
        bot.answer_callback_query(call.id, "Ошибка обработки")


# Обработка режима вывода рассписания
@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_mode:"))
def handle_mode_toggle(call):
    try:
        _, group_name, day_str = call.data.split(":")
        day = int(day_str)
        username = call.from_user.username or str(call.message.chat.id)
        new_mode = toggle_user_mode(username)

        # Получаем расписание для указанного дня
        schedule_data = get_schedule_from_db(group_name, day)

        # Редактируем сообщение только в случае, если режим был изменён
        send_schedule(call.message, schedule_data, group_name, day=day, edit=True, message_id=call.message.message_id, force_mode=new_mode)

        bot.answer_callback_query(call.id, f"Режим переключен на: {new_mode}")
    except Exception as e:
        print(f"Ошибка в handle_mode_toggle: {e}")
        bot.answer_callback_query(call.id, "Не удалось переключить режим")
        

# Обработка сообщений
@bot.message_handler(content_types='text')
def message_reply(message):
    user_input = message.text.strip().lower()

    # Если сообщение "вернуться на главную", вызываем тот же обработчик, что и для команды /start
    if user_input == "вернуться на главную":
        button_message(message)
    else:

        group_input = message.text.strip()

        username = message.from_user.username or str(message.chat.id)
        mode = get_user_mode(username)
        day = date.today().weekday()

        # Обработка кнопок курсов
        if user_input in ["курс 1", "курс1"]:
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

        elif user_input in ["курс 2", "курс2"]:
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

        elif user_input in ["курс 3", "курс3"]:
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

        elif user_input in ["курс 4", "курс4"]:
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

        # Обработка ввода по краткому номеру группы
        elif group_input in short_group_map:
            full_name, url_num = short_group_map[group_input]
            schedule_data = get_schedule(full_name, url_num)
            send_schedule(message, schedule_data or {'subject': [], 'teacher': [], 'clr': [], 'timestamp': []},
                          full_name, day=day, force_mode=mode)

        # Обработка ввода по полному названию группы
        else:
            input_upper = group_input.strip().upper()
            found = False
            for short, (full, url) in short_group_map.items():
                if input_upper == full.upper():
                    schedule_data = get_schedule(full, url)
                    send_schedule(message, schedule_data or {'subject': [], 'teacher': [], 'clr': [], 'timestamp': []},
                                  full, day=day, force_mode=mode)
                    found = True
                    break

            if not found:
                bot.send_message(message.chat.id, "Группа не найдена. Попробуйте ещё раз или выберите курс.")

        print(f"{datetime.now().time()} - Запрос от: {message.from_user.username}")
    
        pass


init_user_settings_db()
init_db()
bot.infinity_polling()