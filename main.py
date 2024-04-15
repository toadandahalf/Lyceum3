from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import requests

import pprint

BOT_TOKEN = '7166801459:AAFqB5svbsnPg2ASubf11ZKJr-SFip4J5yw'
apikey = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"


async def start_address(update, context):
    await update.message.reply_text('Введите адрес места.')
    return 1


async def start_name(update, context):
    await update.message.reply_text('Введите название места')
    return 1


async def start(update, context):
    user = update.effective_user
    context.user_data['list_of_some'] = {}

    reply_keyboard = [['/start_name - поиск по имени'], ['/start_address - поиск по адресу']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я бот,\n"
        f"который поможет тебе сохранить место,\n"
        f"которое тебе понравилось, и сохранить\n"
        f"о нём нужную тебе информацию.\n"
        f"\n"
        f"Сперва сообщением отправь мне название\n"
        f"места, и я дам тебе список мест,\n"
        f"которые мне удалось для тебя найти.\n"
        f"Затем выбери из списка мест то, которое\n"
        f"тебе нужно, и я пришлю тебе\n"
        f"информацию о нём.\n"
        f"\n"
        f"Все очень легко, правда? А как удобно!\n"
        f"Приятного пользования!\n",
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
    else:
        print('Aboba')


async def get_name(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"

    search_params = {
        "apikey": apikey,
        "text": update.message.text,
        "lang": "ru_RU",
        "type": "biz",
        "bbox": "54.331086, 34.372653~57.893077, 41.036901",
        "results": "50"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()

    pprint.pprint(json_response)

    choosing_from_ten = ''

    try:
        for i in range(len(json_response['features'])):
            context.user_data['list_of_some'][str(i)] = json_response["features"][i]

            choosing_from_ten += f'{i + 1}:\n' \
                                 f'    Название: {context.user_data["list_of_some"][str(i)]["properties"]["CompanyMetaData"]["name"]}\n' \
                                 f'    Адрес: {context.user_data["list_of_some"][str(i)]["properties"]["CompanyMetaData"]["address"]}\n' \
                                 f'    \n'

        await update.message.reply_html(choosing_from_ten)

    except IndexError:
        await update.message.reply_html('Ошибка!')
        return 1

    select_kb_reply = ReplyKeyboardMarkup([[str(i + 1)] for i in range(len(context.user_data["list_of_some"]))],
                                          one_time_keyboard=True)

    await update.message.reply_html(
        'Выберите подходящее место и отправьте число от 1 до 10, чтобы получить точную ифнормацию об этом месте',
        reply_markup=select_kb_reply
    )

    return 2


async def get_name_information(update, context):
    select = str(int(update.message.text) - 1)
    organization = context.user_data['list_of_some'][select]

    context.user_data['list_of_some'] = {}

    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    org_coordinates = organization["geometry"]["coordinates"]
    org_map = f'https://static-maps.yandex.ru/1.x/?ll=' \
              f'{str(organization["geometry"]["coordinates"][0])},{str(organization["geometry"]["coordinates"][1])}' \
              f'&spn=0.005,0.005&l=map&pt={str(organization["geometry"]["coordinates"][0])},' \
              f'{str(organization["geometry"]["coordinates"][1])},pm2rdl'

    answer = f'''
    {org_name}
    Адрес: {org_address}
    Точные координаты: {str(org_coordinates).rstrip("]").lstrip("[")}'''

    await update.message.reply_photo(org_map, caption=answer)

    return ConversationHandler.END


async def help_command(update, context):
    await update.message.reply_text(
        f" Коротко о себе: Я бот,\n"
        f" который поможет тебе сохранить место,\n"
        f" которое тебе понравилось, и сохранить\n"
        f" о нём нужную тебе информацию.\n"
        f" \n"
        f" Сперва сообщением отправь мне название\n"
        f" места, и я дам тебе список мест,\n"
        f" которые мне удалось для тебя найти.\n"
        f" Затем выбери из списка мест то, которое\n"
        f" тебе нужно, и я пришлю тебе\n"
        f" информацию о нём.\n"
        f" \n"
        f" Все очень легко, правда? А как удобно!\n"
        f" Приятного пользования!\n"
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

# https://docs.python-telegram-bot.org/en/stable/telegram.bot.html#telegram.Bot.send_photo
# https://qna.habr.com/q/331636
