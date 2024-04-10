from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import requests

BOT_TOKEN = '7166801459:AAFqB5svbsnPg2ASubf11ZKJr-SFip4J5yw'
apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
organizations = {}


async def start_address(update, context):
    await update.message.reply_text('Введите адрес места.')
    return 1


async def start_name(update, context):
    await update.message.reply_text('Введите название места')
    return 1


async def start(update, context):
    user = update.effective_user
    reply_keyboard = [['/start_name - поиск по имени'], ['/start_address - поиск по адресу']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}!) Я бот, который поможет тебе сохранить место, которое тебе понравилось, и"
        rf" узнать о нём нужную тебе информацию. Сперва сообщением отправь мне название места, и я дам тебе список мест"
        rf", которые мне удалось для тебя найти. Затем выбери из списка мест то, которое тебе нужно, и я пришлю тебе "
        rf"информацию о нём. Все очень легко, правда?) А как удобно! Приятного пользования!)",
        reply_markup=markup
    )


async def get_address(update, context):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={apikey}" \
                       f"&geocode={update.message.text}&kind=metro&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()

    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]['formatted']


async def get_name(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"

    search_params = {
        "apikey": apikey,
        "text": update.message.text,
        "lang": "ru_RU",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()

    for i in range(10):
        organizations[str(i)] = json_response["features"][i]
    # select_kb = InlineKeyboardMarkup()

    for i in range(10):
        await update.message.reply_html(
            f'Название: {organizations[str(i)]["properties"]["CompanyMetaData"]["name"]}'
            f'Адрес: {organizations[str(i)]["properties"]["CompanyMetaData"]["address"]}'
        )
    await update.message.reply_html(
        r'Выберите подходящее место и отправьте число от 1 до 10, чтобы получить точную ифнормацию об этом месте'
    )
    return 2


async def get_name_information(update, context):
    select = update.message.text
    organization = organizations[select]

    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    org_coordinates = organization["geometry"]["coordinates"]
    org_map = f'https://static-maps.yandex.ru/1.x/?ll={organization["geometry"]["coordinates"]}&spn=0.005,0.005&l=map'


async def help_command(update, context):
    await update.message.reply_text(
        rf"Я бот, который поможет тебе сохранить место, которое тебе понравилось, и"
        rf" узнать о нём нужную тебе информацию. Сперва сообщением отправь мне название места, и я дам тебе список мест"
        rf", которые мне удалось для тебя найти. Затем выбери из списка мест то, которое тебе нужно, и я пришлю тебе "
        rf"информацию о нём. Все очень легко, правда?) А как удобно! Приятного пользования!)"
    )


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Хорошо, я могу закрыть панель",
        reply_markup=ReplyKeyboardRemove()
    )


async def stop(update, context):
    await update.message.reply_text("Диалог остановлен.")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    with_address = ConversationHandler(
        entry_points=[CommandHandler('start_address', start_address)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    with_name = ConversationHandler(
        entry_points=[CommandHandler('start_name', start_name)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_information)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(with_address)
    application.add_handler(with_name)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("close", close_keyboard))
    application.add_handler(CommandHandler("start_address", start_address))
    application.add_handler(CommandHandler("start_name", start_name))
    application.add_handler(CommandHandler("stop", stop))

    application.run_polling()


if __name__ == '__main__':
    main()
