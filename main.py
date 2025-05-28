from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import datetime
import telebot
from telebot import types

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

ChromeDriverManager().install()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

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
    bot.send_message(message.chat.id, 'Выбери курс\nЧтобы вернуться к выбору курса отправь /start', reply_markup=markup)

def parsing(message, url_num):
    print(f"{datetime.datetime.now().time()} - Запрос от: {message.from_user.username}")

    subject = []
    teacher = []
    clr = []
    top_week = True

    driver.get(f"https://raspmath.isu.ru/schedule/{url_num}") 
    soup = BeautifulSoup(driver.page_source, 'lxml')

    group = soup.find('span', {'class': 'select2-selection__rendered'}).text[1:]

    if  soup.find('a', class_="btn btn-primary2 top-week active") in soup.find('li', class_='active mr-3'):
        top_week = True
    else:
        top_week = False

    tbody = soup.find('tbody')

    if top_week == True:
        td_list = tbody.find_all('td', class_='td1')
    else:
        td_list = tbody.find_all('td', class_='td2')

    for td in td_list:
        if len(td) == 0:
            subject.append('-----')
            teacher.append('-----')
            clr.append('-----')
        else:
            if td.find('p', class_='nameHoliday h5 text-center'): 
                subject.append('-----')
                teacher.append('-----')
                clr.append('-----')
            else:
                subject_el = td.find('div', class_ = 'nameSubject').text
                subject.append(subject_el)
                teacher_el = td.find('div', class_ = 'teacher sch-mt-1').text
                teacher.append(teacher_el)
                clr_el = td.find('div', class_ = 'classroom sch-mt-1').text
                clr.append(clr_el)

    tday = date.today().weekday()
    day = soup.find('th', class_ = tday+1).text
    if tday == 6:
        bot.send_message(message.chat.id, "Сегодня воскресенье")
    elif tday == 0:
        bot.send_message(message.chat.id, f"🗓️{day} - {group}\n⌚08.30-10.00:\n    ⌊📖{subject[0]}\n    ⌊👤{teacher[0]}\n    ⌊🚪{clr[0]}\n⌚10.10-11.40:\n    ⌊📖{subject[6]}\n    ⌊👤{teacher[6]}\n    ⌊🚪{clr[6]}\n⌚11.50-13.20:\n    ⌊📖{subject[12]}\n    ⌊👤{teacher[12]}\n    ⌊🚪{clr[12]}\n⌚13.50-15.20:\n    ⌊📖{subject[18]}\n    ⌊👤{teacher[18]}\n    ⌊🚪{clr[18]}\n⌚15.30-17.00:\n    ⌊📖{subject[24]}\n    ⌊👤{teacher[24]}\n    ⌊🚪{clr[24]}\n⌚17.10-18.40:\n    ⌊📖{subject[30]}\n    ⌊👤{teacher[30]}\n    ⌊🚪{clr[30]}\n⌚18.50-20.20:\n    ⌊📖{subject[36]}\n    ⌊👤{teacher[36]}\n    ⌊🚪{clr[36]}")
    elif tday == 1:
        bot.send_message(message.chat.id, f"🗓️{day} - {group}\n⌚08.30-10.00:\n    ⌊📖{subject[1]}\n    ⌊👤{teacher[1]}\n    ⌊🚪{clr[1]}\n⌚10.10-11.40:\n    ⌊📖{subject[7]}\n    ⌊👤{teacher[7]}\n    ⌊🚪{clr[7]}\n⌚11.50-13.20:\n    ⌊📖{subject[13]}\n    ⌊👤{teacher[13]}\n    ⌊🚪{clr[13]}\n⌚13.50-15.20:\n    ⌊📖{subject[19]}\n    ⌊👤{teacher[19]}\n    ⌊🚪{clr[19]}\n⌚15.30-17.00:\n    ⌊📖{subject[25]}\n    ⌊👤{teacher[25]}\n    ⌊🚪{clr[25]}\n⌚17.10-18.40:\n    ⌊📖{subject[31]}\n    ⌊👤{teacher[31]}\n    ⌊🚪{clr[31]}\n⌚18.50-20.20:\n    ⌊📖{subject[37]}\n    ⌊👤{teacher[37]}\n    ⌊🚪{clr[37]}")
    elif tday == 2:
        bot.send_message(message.chat.id, f"🗓️{day} - {group}\n⌚08.30-10.00:\n    ⌊📖{subject[2]}\n    ⌊👤{teacher[2]}\n    ⌊🚪{clr[2]}\n⌚10.10-11.40:\n    ⌊📖{subject[8]}\n    ⌊👤{teacher[8]}\n    ⌊🚪{clr[8]}\n⌚11.50-13.20:\n    ⌊📖{subject[14]}\n    ⌊👤{teacher[14]}\n    ⌊🚪{clr[14]}\n⌚13.50-15.20:\n    ⌊📖{subject[20]}\n    ⌊👤{teacher[20]}\n    ⌊🚪{clr[20]}\n⌚15.30-17.00:\n    ⌊📖{subject[26]}\n    ⌊👤{teacher[26]}\n    ⌊🚪{clr[26]}\n⌚17.10-18.40:\n    ⌊📖{subject[32]}\n    ⌊👤{teacher[32]}\n    ⌊🚪{clr[32]}\n⌚18.50-20.20:\n    ⌊📖{subject[38]}\n    ⌊👤{teacher[38]}\n    ⌊🚪{clr[38]}")
    elif tday == 3:
        bot.send_message(message.chat.id, f"🗓️{day} - {group}\n⌚08.30-10.00:\n    ⌊📖{subject[3]}\n    ⌊👤{teacher[3]}\n    ⌊🚪{clr[3]}\n⌚10.10-11.40:\n    ⌊📖{subject[9]}\n    ⌊👤{teacher[9]}\n    ⌊🚪{clr[9]}\n⌚11.50-13.20:\n    ⌊📖{subject[15]}\n    ⌊👤{teacher[15]}\n    ⌊🚪{clr[15]}\n⌚13.50-15.20:\n    ⌊📖{subject[21]}\n    ⌊👤{teacher[21]}\n    ⌊🚪{clr[21]}\n⌚15.30-17.00:\n    ⌊📖{subject[27]}\n    ⌊👤{teacher[27]}\n    ⌊🚪{clr[27]}\n⌚17.10-18.40:\n    ⌊📖{subject[33]}\n    ⌊👤{teacher[33]}\n    ⌊🚪{clr[33]}\n⌚18.50-20.20:\n    ⌊📖{subject[39]}\n    ⌊👤{teacher[39]}\n    ⌊🚪{clr[39]}")
    elif tday == 4:
        bot.send_message(message.chat.id, f"🗓️{day} - {group}\n⌚08.30-10.00:\n    ⌊📖{subject[4]}\n    ⌊👤{teacher[4]}\n    ⌊🚪{clr[4]}\n⌚10.10-11.40:\n    ⌊📖{subject[10]}\n    ⌊👤{teacher[10]}\n    ⌊🚪{clr[10]}\n⌚11.50-13.20:\n    ⌊📖{subject[16]}\n    ⌊👤{teacher[16]}\n    ⌊🚪{clr[16]}\n⌚13.50-15.20:\n    ⌊📖{subject[22]}\n    ⌊👤{teacher[22]}\n    ⌊🚪{clr[22]}\n⌚15.30-17.00:\n    ⌊📖{subject[28]}\n    ⌊👤{teacher[28]}\n    ⌊🚪{clr[28]}\n⌚17.10-18.40:\n    ⌊📖{subject[34]}\n    ⌊👤{teacher[34]}\n    ⌊🚪{clr[34]}\n⌚18.50-20.20:\n    ⌊📖{subject[40]}\n    ⌊👤{teacher[40]}\n    ⌊🚪{clr[40]}")
    elif tday == 5:
        bot.send_message(message.chat.id, f"🗓️{day} - {group}\n⌚08.30-10.00:\n    ⌊📖{subject[5]}\n    ⌊👤{teacher[5]}\n    ⌊🚪{clr[5]}\n⌚10.10-11.40:\n    ⌊📖{subject[11]}\n    ⌊👤{teacher[11]}\n    ⌊🚪{clr[11]}\n⌚11.50-13.20:\n    ⌊📖{subject[17]}\n    ⌊👤{teacher[17]}\n    ⌊🚪{clr[17]}\n⌚13.50-15.20:\n    ⌊📖{subject[23]}\n    ⌊👤{teacher[23]}\n    ⌊🚪{clr[23]}\n⌚15.30-17.00:\n    ⌊📖{subject[29]}\n    ⌊👤{teacher[29]}\n    ⌊🚪{clr[29]}\n⌚17.10-18.40:\n    ⌊📖{subject[35]}\n    ⌊👤{teacher[35]}\n    ⌊🚪{clr[35]}\n⌚18.50-20.20:\n    ⌊📖{subject[41]}\n    ⌊👤{teacher[41]}\n    ⌊🚪{clr[41]}")

@bot.message_handler(content_types='text')
def message_reply(message):
    user_input = message.text.strip().lower()
    group_input = message.text.strip()
    
    # Обработка кнопок курсов (регистронезависимая)
    if user_input in ["курс 1", "курс1"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        g1 = types.KeyboardButton("02121-ДБ")
        g2 = types.KeyboardButton("02122-ДБ")
        g3 = types.KeyboardButton("02123-ДБ")
        g4 = types.KeyboardButton("02141-ДБ")
        g5 = types.KeyboardButton("02161-ДБ")
        g6 = types.KeyboardButton("02162-ДБ")
        g7 = types.KeyboardButton("02171-ДБ")
        g8 = types.KeyboardButton("02172-ДБ")
        g9 = types.KeyboardButton("02181-ДБ")
        markup.add(g1, g2, g3, g4, g5, g6, g7, g8, g9)
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
        
    elif user_input in ["курс 2", "курс2"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        g1 = types.KeyboardButton("02221-ДБ")
        g2 = types.KeyboardButton("02222-ДБ")
        g3 = types.KeyboardButton("02223-ДБ")
        g4 = types.KeyboardButton("02241-ДБ")
        g5 = types.KeyboardButton("02261-ДБ")
        g6 = types.KeyboardButton("02262-ДБ")
        g7 = types.KeyboardButton("02271-ДБ")
        g8 = types.KeyboardButton("02272-ДБ")
        g9 = types.KeyboardButton("02281-ДБ")
        markup.add(g1, g2, g3, g4, g5, g6, g7, g8, g9)
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
        
    elif user_input in ["курс 3", "курс3"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        g1 = types.KeyboardButton("02321-ДБ")
        g2 = types.KeyboardButton("02322-ДБ")
        g3 = types.KeyboardButton("02323-ДБ")
        g4 = types.KeyboardButton("02341-ДБ")
        g5 = types.KeyboardButton("02361-ДБ")
        g6 = types.KeyboardButton("02362-ДБ")
        g7 = types.KeyboardButton("02371-ДБ")
        g8 = types.KeyboardButton("02381-ДБ")
        markup.add(g1, g2, g3, g4, g5, g6, g7, g8)
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
        
    elif user_input in ["курс 4", "курс4"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        g1 = types.KeyboardButton("02421-ДБ")
        g2 = types.KeyboardButton("02422-ДБ")
        g3 = types.KeyboardButton("02441-ДБ")
        g4 = types.KeyboardButton("02461-ДБ")
        g5 = types.KeyboardButton("02471-ДБ")
        g5 = types.KeyboardButton("02481-ДБ")
        markup.add(g1, g2, g3, g4, g5)
        bot.send_message(message.chat.id, 'Выбери группу', reply_markup=markup)
    
    # Обработка групп по кнопкам или краткому номеру
    elif group_input in short_group_map:
        full_name, url_num = short_group_map[group_input]
        parsing(message, url_num)
    
    # Обработка полных названий групп (регистронезависимая)
    else:
        input_upper = group_input.upper()
        found = False
        for short, (full, url) in short_group_map.items():
            if input_upper == full.upper():
                parsing(message, url)
                found = True
                break
        
        if not found:
            bot.send_message(message.chat.id, "Группа не найдена. Попробуйте ещё раз или выберите курс.")

bot.infinity_polling()