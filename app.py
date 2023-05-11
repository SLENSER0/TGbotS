# https://pastebin.com/0xZJiU1u
import calendar

import psycopg2
import telebot
from constants import API_TOKEN, PASSWORD
import datetime as dt


def get_week_number():  # возвращает номер дня двух недель. т.е. если сегодня понедельник нечеиерй недели, то вернет 1
                        # если сегодня понедельник четной недели, то вернет 8
    return 7 * (1 - dt.date.today().isocalendar().week % 2) + (dt.date.weekday(dt.date.today()) + 1)


def get_weekday(number):
    weekdays = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье'
    }
    return weekdays[number - 7 * (number > 7)]


def print_day(day):
    cur = conn.cursor()
    cur.execute(f"""
     SELECT timetable.id, timetable.DAY, subject.NAME, timetable.room_numb, timetable.start_time, teacher.full_name
     FROM timetable
     JOIN teacher ON timetable.teacher_id = teacher.id
     JOIN subject ON timetable.subject = subject.NAME
     WHERE day = {day};
     """)
    res = cur.fetchall()
    cur.close()
    timetable = {}
    for lesson in res:
        lesson_time = str(lesson[4])[:5]
        if lesson_time not in timetable:
            timetable[lesson_time] = []
        timetable[lesson_time].append({
            "name": lesson[2],
            "place": lesson[3],
            "teacher": lesson[5],
        })

    times = [
        "09:30",
        "11:20",
        "13:10",
        "15:25",
        "17:15"
    ]
    s = get_weekday(day) + '\n\n'
    for i, time in enumerate(times, start=1):
        s += f"{i}. {time} - {(dt.datetime.strptime(time, '%H:%M') + dt.timedelta(minutes=95)).strftime('%H:%M')}\n"
        if time in timetable:
            for lesson in timetable[time]:
                if lesson["name"] is not None and lesson["place"] is not None and lesson["teacher"] is not None:
                    s += f"{lesson['name']} \n{lesson['teacher']} \n{lesson['place']}"
                else:
                    s += "<Нет пары>"
        else:
            s += "<Нет пары>"

        s += '\n\n'
    return s


def print_week(num: int):  # num = 0 - нечетная неделя, num = 1 - четная неделя
    if num == 0:
        s = 'Нечетная неделя' + '\n\n'
        for i in range(1, 8):
            s += print_day(i) + '\n'
        return s
    elif num == 1:
        s = 'Четная неделя' + '\n\n'
        for i in range(8, 15):
            s += print_day(i) + '\n'
        return s


conn = psycopg2.connect(database="Schedule",
                        user="dummy",
                        password=PASSWORD,
                        host="localhost",
                        port="5432")

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Бот с расписанием для группы БВТ2203")


@bot.message_handler(commands=['mtuci'])
def send_url(message):
    bot.reply_to(message, "https://mtuci.ru/")


@bot.message_handler(commands=['monday'])
def get_schedule_for_this_monday(message):
    bot.reply_to(message, print_day(1 if get_week_number() <= 7 else 8))


@bot.message_handler(commands=['tuesday'])
def get_schedule_for_this_monday(message):
    bot.reply_to(message, print_day(2 if get_week_number() <= 7 else 9))


@bot.message_handler(commands=['wednesday'])
def get_schedule_for_this_monday(message):
    bot.reply_to(message, print_day(3 if get_week_number() <= 7 else 9))


@bot.message_handler(commands=['thursday'])
def get_schedule_for_this_monday(message):
    bot.reply_to(message, print_day(4 if get_week_number() <= 7 else 10))


@bot.message_handler(commands=['friday'])
def get_schedule_for_this_monday(message):
    bot.reply_to(message, print_day(5 if get_week_number() <= 7 else 11))


@bot.message_handler(commands=['tomorrow'])
def get_schedule_for_tommorow(message):
    bot.reply_to(message, print_day(get_week_number() + 1))


@bot.message_handler(commands=['today'])
def get_schedule_for_this_today(message):
    bot.reply_to(message, print_day(get_week_number()))


@bot.message_handler(commands=['this_week'])
def get_schedule_for_this_monday(message):
    bot.reply_to(message, print_week(0 if get_week_number() <= 7 else 1))


@bot.message_handler(commands=['next_week'])
def get_schedule_for_this_monday(message):
    bot.reply_to(message, print_week(1 if get_week_number() <= 7 else 0))


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = """
Я - бот с расписанием для группы БВТ2203.

Список команд:
/start - приветственное сообщение
/mtuci - ссылка на сайт МТУСИ
/monday - расписание на понедельник
/tuesday - расписание на вторник
/wednesday - расписание на среду
/thursday - расписание на четверг
/friday - расписание на пятницу
/today - расписание на сегодня
/tomorrow - расписание на завтра
/this_week - расписание на текущую неделю
/next_week - расписание на следующую неделю
/help - список команд с описанием

"""
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, 'Извините, я Вас не понял.')


bot.infinity_polling()
