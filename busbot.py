import telebot
from background import keep_alive #импорт функции для поддержки работоспособности
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from telebot import types

token = '6210753848:AAE2pPorX3pn2pKSR0zUU3Mi2oCHon9MHIs'
bot = telebot.TeleBot(token)

bus_list = ['180', '86', '123', '80', '328']
favorites = {'180': ['Хошимина (Композиторов)', 'Стародеревенская улицa (Улицa Ильюшина)']}
bus_end_station, stations_list_1, stations_list_2 = [], [], []
dict_to_1, dict_to_2 = {}, {}
prev_menu = False
time_next_2, cur_bus, cur_station, cur_direct ='', '', '', ''


@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, <b>{message.from_user.first_name}</b>!'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    bot.send_message(message.chat.id, 'Жми <b>/norHaJlu</b> и мы стааартуем', parse_mode='html')


@bot.message_handler(commands=['norHaJlu'])
def pognali_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for bus in bus_list:
        item1 = types.KeyboardButton(bus)
        markup.add(item1)
    bot.send_message(message.chat.id, 'Выберите номер басика', reply_markup=markup)


def get_bus_info(bus_num):
    global dict_to_1
    global dict_to_2
    global time_next_2
    global cur_bus

    bus_end_station.clear()
    stations_list_1.clear()
    stations_list_2.clear()
    dict_to_1.clear()
    dict_to_2.clear()
    cur_bus = bus_num

    headers = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                       Chrome/112.0.0.0 Safari/537.36'
    }

    url = f'https://ru.busti.me/spb/bus-{bus_num}/'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    bus_stop_1 = soup.find('table', {'class': 'ui compact unstackable table',
                                     'id': 'd0'}).find('b').text
    bus_stop_2 = soup.find('table', {'class': 'ui compact unstackable table',
                                     'id': 'd1'}).find('b').text
    bus_times_1 = soup.find('table', {'class': 'ui compact unstackable table',
                                      'id': 'd0'}).find_all('div', class_='ft')
    times_1 = [(time.text + ':00') for time in bus_times_1]
    bus_times_2 = soup.find('table', {'class': 'ui compact unstackable table',
                                      'id': 'd1'}).find_all('tr')
    busti_2 = [ti.find_next('td').text.replace('\n', '') for ti in bus_times_2]
    times_2 = [(time + ':00') for time in busti_2]

    bus_stops_list_1 = soup.find('table', {'class': 'ui compact unstackable table',
                                           'id': 'd0'}).find_all('tr')
    bus_stops_list_2 = soup.find('table', {'class': 'ui compact unstackable table',
                                           'id': 'd1'}).find_all('tr')
    bus_end_station.append(bus_stop_1)
    bus_end_station.append(bus_stop_2)
    stop_list_1 = [stop.find_previous('td').text.replace('\n', '') for stop in bus_stops_list_1]
    stop_list_2 = [stop.find_previous('td').text.replace('\n', '') for stop in bus_stops_list_2]

    for stop in stop_list_1[1:]:
        if bus_stop_1 in stop:
            stations_list_1.append(bus_stop_1)
        else:
            stations_list_1.append(stop.strip())
    stations_list_1.append(bus_stop_2)

    for stop in stop_list_2[1:]:
        if bus_stop_2 in stop:
            stations_list_2.append(bus_stop_2)
        else:
            stations_list_2.append(stop.strip())
    stations_list_2.append(bus_stop_1)

    dict_to_1 = dict(zip(stations_list_1, times_1))
    dict_to_2 = dict(zip(stations_list_2, times_2))

    return bus_stop_1, bus_stop_2


def get_minutes(time_arrive):
    cur_time = datetime.now()
    bus_day = str(datetime.now().date()) + ' ' + time_arrive
    bus_time = datetime.strptime(bus_day, "%Y-%m-%d %H:%M:%S")
    delta = bus_time - cur_time
    return int(((delta.total_seconds() // 60) - 179))


@bot.message_handler(content_types='text')
def message_num_bus(message):
    global prev_menu
    global cur_bus
    global cur_direct
    global cur_station
    global dict_to_1
    global dict_to_2

    if message.text in bus_list:
        stop_1, stop_2 = get_bus_info(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(stop_1)
        markup.add(item1)
        item1 = types.KeyboardButton(stop_2)
        markup.add(item1)
        item1 = types.KeyboardButton('Назад')
        markup.add(item1)
        bot.send_message(message.chat.id, 'В сторону какой остановки поедем (конечная, как в метро)', reply_markup=markup)

    elif message.text == 'Назад':
        pognali_message(message)

    elif message.text == 'Выбрать все остановки':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if dict_to_1:
            for stop in stations_list_1:
                item1 = types.KeyboardButton(stop)
                markup.add(item1)
        elif dict_to_2:
            for stop in stations_list_2:
                item1 = types.KeyboardButton(stop)
                markup.add(item1)
        item1 = types.KeyboardButton('Назад')
        markup.add(item1)
        bot.send_message(message.chat.id, 'Откуда едем?', reply_markup=markup)

    elif message.text == 'Выбрать остановки фавориты':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if cur_bus in favorites.keys():
            for i in favorites[cur_bus]:
                item1 = types.KeyboardButton(i)
                markup.add(item1)
            item1 = types.KeyboardButton('Назад')
            markup.add(item1)
            bot.send_message(message.chat.id, 'Откуда едем?', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f'Для автобуса {cur_bus} не заведены фавориты. Попросите об этом \
                                                разработчика либо ждите следюущих обновлений', reply_markup=markup)

    elif message.text in bus_end_station and prev_menu == False:
        prev_menu = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if message.text == bus_end_station[1]:
            dict_to_2.clear()
            cur_direct = '1'
        else:
            dict_to_1.clear()
            cur_direct = '2'
        item1 = types.KeyboardButton('Выбрать остановки фавориты')
        markup.add(item1)
        item1 = types.KeyboardButton('Выбрать все остановки')
        markup.add(item1)
        item1 = types.KeyboardButton('Назад')
        markup.add(item1)
        bot.send_message(message.chat.id, f'Едем в сторону {message.text}', reply_markup=markup)

    elif (message.text in stations_list_1 or message.text in stations_list_2) and prev_menu == True:
        prev_menu = False
        cur_station = message.text
        bot.send_message(message.chat.id, f'Мы на остановке {message.text}')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Обновить информацию')
        markup.add(item1)
        item1 = types.KeyboardButton('Назад')
        markup.add(item1)
        if dict_to_1:
            if dict_to_1[message.text] != ':00':
                minutes = get_minutes(dict_to_1[message.text])
                if minutes > 0:
                    bot.send_message(message.chat.id, f'Ближайший автобус приедет через {str(minutes) + " мин."}',
                                     reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, f'Автобус прибывает прямо сейчас!', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Пока нет басика на маршруте')
                bot.send_message(message.chat.id,
                                 f'Следующий автобус стартует со станции {bus_end_station[0]} в \
                                 {dict_to_1[bus_end_station[0]]}', reply_markup=markup)
        elif dict_to_2:
            if dict_to_2[message.text] != ':00':
                minutes = get_minutes(dict_to_2[message.text])
                if minutes > 0:
                    bot.send_message(message.chat.id, f'Ближайший автобус приедет через {str(minutes) + " мин."}',
                                     reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, f'Автобус прибывает прямо сейчас!', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Пока нет басика на маршруте', reply_markup=markup)
                bot.send_message(message.chat.id, f'Следующий автобус стартует со станции {bus_end_station[1]} в \
                                                    {time_next_2+":00"}', reply_markup=markup)
        
    elif message.text == 'Обновить информацию':
        bot.send_message(message.chat.id, f'Мы на остановке {cur_station}')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Обновить информацию')
        markup.add(item1)
        item1 = types.KeyboardButton('Назад')
        markup.add(item1)
        get_bus_info(cur_bus)
        if cur_direct == '1' and dict_to_1[cur_station] != ':00':
            minutes = get_minutes(dict_to_1[cur_station])
        elif cur_direct == '2' and dict_to_2[cur_station] != ':00':
            minutes = get_minutes(dict_to_2[cur_station])
        else:
            bot.send_message(message.chat.id, 'Пока нет басика на маршруте', reply_markup=markup)
            return 
        if minutes > 0:
            bot.send_message(message.chat.id, f'Ближайший автобус приедет через {str(minutes) + " мин."}',
                                 reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f'Автобус прибывает прямо сейчас!', reply_markup=markup)


keep_alive()
bot.polling(none_stop=True)
