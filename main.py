from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import requests

import pprint

BOT_TOKEN = '7166801459:AAFqB5svbsnPg2ASubf11ZKJr-SFip4J5yw'
apikey = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
kinds = {'house': 'дом', 'street': 'улица', 'metro': 'станция метро',
         'district': 'район города', 'locality': 'населенный пункт'}


async def start(update, context):
    user = update.effective_user
    context.user_data['list_of_some'] = {}

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
    )

    await update.message.reply_text('Введите название места:')

    return 1


async def get_name_or_address(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"

    search_params = {
        "apikey": apikey,
        "text": update.message.text,
        "lang": "ru_RU",
        "bbox": "54.331086, 34.372653~57.893077, 41.036901",
        "results": "50"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()

    pprint.pprint(json_response)
    print(json_response['features'][0]['properties'])
    try:
        choosing_from_ten = ''

        for i in range(len(json_response['features'])):
            context.user_data['list_of_some'][str(i)] = json_response["features"][i]

            choosing_from_ten += f'{i + 1}:\n' \
                                 f'    Название: {context.user_data["list_of_some"][str(i)]["properties"]["CompanyMetaData"]["name"]}\n' \
                                 f'    Адрес: {context.user_data["list_of_some"][str(i)]["properties"]["CompanyMetaData"]["address"]}\n' \
                                 f'    \n'

        await update.message.reply_html(choosing_from_ten)

        select_kb_reply = ReplyKeyboardMarkup([[str(i + 1)] for i in range(len(context.user_data["list_of_some"]))],
                                              one_time_keyboard=True)

        await update.message.reply_html(
            'Выберите подходящую организацию и отправьте число от 1 до 10,'
            ' чтобы получить точную информацию об этом месте',
            reply_markup=select_kb_reply
        )

        return 2

    except KeyError:

        choosing_from_ten = ''

        for i in range(len(json_response['features'])):
            context.user_data['list_of_some'][str(i)] = json_response["features"][i]

            choosing_from_ten += f'{i + 1}:\n' \
                                 f'    Тип: {kinds[context.user_data["list_of_some"][str(i)]["properties"]["GeocoderMetaData"]["kind"]]}\n' \
                                 f'    Адрес: {context.user_data["list_of_some"][str(i)]["properties"]["name"]}, ' \
                                 f'{context.user_data["list_of_some"][str(i)]["properties"]["description"]}\n'

        await update.message.reply_html(choosing_from_ten)

        select_kb_reply = ReplyKeyboardMarkup([[str(i + 1)] for i in range(len(context.user_data["list_of_some"]))],
                                              one_time_keyboard=True)

        await update.message.reply_html(
            'Выберите подходящее место и отправьте число от 1 до 10,'
            ' чтобы получить точную информацию об этом месте',
            reply_markup=select_kb_reply
        )

        return 3


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


async def get_address_information(update, context):
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


async def stop(update, context):
    await update.message.reply_text("Диалог остановлен.")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    with_name = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_or_address)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_information)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address_information)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(with_name)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stop", stop))

    application.run_polling()


if __name__ == '__main__':
    main()

# https://docs.python-telegram-bot.org/en/stable/telegram.bot.html#telegram.Bot.send_photo
# https://qna.habr.com/q/331636
# https://yandex.ru/blog/mapsapi/32690
