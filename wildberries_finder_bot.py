import telebot
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = 'Телеграмм_токен' # Здесь нужно ввести ваш телеграмм токен
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для поиска места товара в выдаче Wildberries. Напишите /search для начала поиска.")


@bot.message_handler(commands=['search'])
def search_item(message):
    print("Запрос на поиск принят:", message.text)
    chat_id = message.chat.id
    query_and_id = message.text.split(' ', 2)  # список из команд (/search), товарного запроса и артикула товара
    if len(query_and_id) < 3:
        bot.send_message(chat_id, "Вы не ввели запрос и/или артикул товара.")
        return
    query, id = query_and_id[1:]
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(f'https://www.wildberries.ru/search?query={query}&page=1', headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    pages = soup.find_all('a', {'class': 'pagination-item'})
    try:
        last_page = int(pages[-1].text.strip())
    except IndexError:
        last_page = 1
    for i in range(1, last_page + 1):
        page = requests.get(f'https://www.wildberries.ru/search?query={query}&page={i}', headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        items = soup.find_all('div', {'class': 'dtList-inner'})
        for item in items:
            if id in item.get('data-popup-nm'):
                pos = items.index(item) + 1 + (i - 1) * len(items)
                # Отправляем гифку в чат
                f = open('cool_gif.gif', 'rb')
                bot.send_document(chat_id, f)
                f.close()
                # Отправляем сообщение с позицией товара на странице
                bot.send_message(chat_id, f'Товар с артикулом {id} находится на {pos} месте на странице {i}.')
                return
    bot.send_message(chat_id, f'Товар с артикулом {id} не найден.')


print("Бот запущен")
bot.polling()
