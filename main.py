from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import requests
import pprint

BOT_TOKEN = '7166801459:AAFqB5svbsnPg2ASubf11ZKJr-SFip4J5yw'
apikey = "40d1649f-0493-4b70-98ba-98533de7710b"


async def start_dialog(update, context):
    await update.message.reply_text('Введите адрес места.')
    return 1


async def start(update, context):
    user = update.effective_user
    reply_keyboard = [['/help - 123'], ['/close'], ['/start_dialog']]
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

        # toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        real_toponym = json_response["response"]["GeoObjectCollection"]["featureMember"]
        # address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]['formatted']

        # pprint.pprint(check1)
        # print('---')
        # print(address)

        ten = []

        for address in real_toponym:
            ten.append([address["GeoObject"]["metaDataProperty"]
                        ["GeocoderMetaData"]["Address"]['formatted']])

        context.user_data['ten_addresses'] = ten

        return 2


async def choosing_from_ten(update, context):
    user = update.effective_user
    reply_keyboard = []
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    for address in context.user_data['ten_addresses']:
        reply_keyboard.append(f'/create - {address}')

    await update.message.reply_html(text='', reply_markup=markup)


async def create(update, context):
    pass


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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start_dialog', start_dialog)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            2: [MessageHandler(filters.TEXT, choosing_from_ten)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("close", close_keyboard))
    application.add_handler(CommandHandler("choosing_from_ten", choosing_from_ten))
    application.add_handler(CommandHandler("create", create))

    application.run_polling()


if __name__ == '__main__':
    main()
