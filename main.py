# import pprint

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import requests

with open('apikey_and_token.txt', 'r') as apikey_and_token:
    APIKEY = apikey_and_token.readline().rstrip('\n')
    BOT_TOKEN = apikey_and_token.readline().rstrip('\n')

default_city = "Москва"


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
        "apikey": APIKEY,
        "text": update.message.text,
        "lang": "ru_RU",
        "results": "50"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()

    try:
        city = context.user_data['default_city']

    except KeyError:
        city = default_city

    """Поиск по организациям или поиск адреса"""

    try:

        choosing_from_ten = ''

        count = 0

        for i in range(len(json_response['features'])):
            if json_response["features"][i]["properties"]["CompanyMetaData"]["address"].split(', ')[0] == city:

                context.user_data['list_of_some'][str(count + 1)] = json_response["features"][count]

                choosing_from_ten += f'{count + 1}:\n' \
                                     f'    Название: {context.user_data["list_of_some"][str(count + 1)]["properties"]["CompanyMetaData"]["name"]}\n' \
                                     f'    Адрес: {context.user_data["list_of_some"][str(count + 1)]["properties"]["CompanyMetaData"]["address"]}\n' \
                                     f'    \n'

                count += 1

        await update.message.reply_html(choosing_from_ten)

        select_kb_reply = ReplyKeyboardMarkup([[str(i + 1)] for i in range(len(context.user_data["list_of_some"]))],
                                              one_time_keyboard=True)

        await update.message.reply_html(
            'Выберите подходящее место и отправьте число его номер,'
            ' чтобы получить точную информацию об этом месте',
            reply_markup=select_kb_reply
        )

        return 2

    except KeyError:

        choosing_from_ten = ''

        count = 0

        for i in range(len(json_response['features'])):
            if json_response["features"][i]["properties"]["GeocoderMetaData"]["text"].split(', ')[1] == city:

                context.user_data['list_of_some'][str(count + 1)] = json_response["features"][count]

                choosing_from_ten += f'{i + 1}:\n' \
                                     f'    Тип: {context.user_data["list_of_some"][str(count + 1)]["properties"]["GeocoderMetaData"]["kind"]}\n' \
                                     f'    Адрес: {context.user_data["list_of_some"][str(count + 1)]["properties"]["name"]}, ' \
                                     f'{context.user_data["list_of_some"][str(count + 1)]["properties"]["GeocoderMetaData"]["text"]}\n'

                count += 1

            else:
                pass

        await update.message.reply_html(choosing_from_ten)

        select_kb_reply = ReplyKeyboardMarkup([[str(i + 1)] for i in range(len(context.user_data["list_of_some"]))],
                                              one_time_keyboard=True)

        await update.message.reply_html(
            'Выберите подходящее место и отправьте число его номер,'
            ' чтобы получить точную информацию об этом месте',
            reply_markup=select_kb_reply
        )

        return 3


async def get_address_information(update, context):
    """Функция вывода информации об адресе"""

    select = str(int(update.message.text))
    organization = context.user_data['list_of_some'][select]

    context.user_data['list_of_some'] = {}

    kind = organization["properties"]["GeocoderMetaData"]["kind"]
    street = organization["properties"]["name"]
    city = organization["properties"]["description"]
    org_coordinates = organization["geometry"]["coordinates"]

    org_map = f'https://static-maps.yandex.ru/1.x/?ll=' \
              f'{str(organization["geometry"]["coordinates"][0])},{str(organization["geometry"]["coordinates"][1])}' \
              f'&spn=0.005,0.005&l=map&pt={str(organization["geometry"]["coordinates"][0])},' \
              f'{str(organization["geometry"]["coordinates"][1])},pm2bll'

    """Создание сообщения о выбранном адресе"""

    answer = f'''
    Тип: {kind}
    Адрес: {city}, {street}
    Точные координаты: {str(org_coordinates).rstrip("]").lstrip("[")}'''

    await update.message.reply_photo(org_map, caption=answer)

    return ConversationHandler.END


async def get_name_information(update, context):
    """Функция вывода информации об организации"""

    select = str(int(update.message.text))
    organization = context.user_data['list_of_some'][select]

    context.user_data['list_of_some'] = {}

    url = '---'

    name = organization["properties"]["CompanyMetaData"]["name"]
    address = organization["properties"]["CompanyMetaData"]["address"]
    coordinates = organization["geometry"]["coordinates"]
    phone = organization["properties"]["CompanyMetaData"]["Phones"][0]["formatted"]
    hours = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
    map_map = f'https://static-maps.yandex.ru/1.x/?ll=' \
              f'{str(organization["geometry"]["coordinates"][0])},{str(organization["geometry"]["coordinates"][1])}' \
              f'&spn=0.005,0.005&l=map&pt={str(organization["geometry"]["coordinates"][0])},' \
              f'{str(organization["geometry"]["coordinates"][1])},pm2rdl'

    try:
        url = organization["properties"]["CompanyMetaData"]["url"]
    except KeyError:
        pass

    """Создание сообщения о выбранной организации"""

    answer = f'''
    Название: {name}
    Адрес: {address}
    Точные координаты: {str(coordinates).rstrip("]").lstrip("[")}
    URL: {url}
    Телефон: {phone}
    Часы работы: {hours}'''

    await update.message.reply_photo(map_map, caption=answer)

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


async def geolocation(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"

    search_params = {
        "apikey": APIKEY,
        "text": f"{update.message.location.latitude},{update.message.location.longitude}",
        "lang": "ru_RU",
        "results": "50"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()

    context.user_data["default_city"] = json_response["features"][0]["properties"]["GeocoderMetaData"]["text"].split(', ')[1]

    await update.message.reply_text('Геолокация обновлена')


async def stop(update, context):
    await update.message.reply_text("Диалог остановлен")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    the_one_who_controls = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_or_address)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_information)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address_information)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(the_one_who_controls)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.LOCATION, geolocation))

    application.run_polling()


if __name__ == '__main__':
    main()
