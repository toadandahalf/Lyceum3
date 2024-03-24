from telegram.ext import Application, MessageHandler, filters, CommandHandler

BOT_TOKEN = '7166801459:AAFqB5svbsnPg2ASubf11ZKJr-SFip4J5yw'


async def basic_response(update, context):
    await update.message.reply_text('Пока не готово...')


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}!) Я бот, который поможет тебе сохранить место, которое тебе понравилось, и"
        rf" узнать о нём нужную тебе информацию. Сперва сообщением отправь мне название места, и я дам тебе список мест"
        rf", которые мне удалось для тебя найти. Затем выбери из списка мест то, которое тебе нужно, и я пришлю тебе "
        rf"информацию о нём. Все очень легко, правда?) А как удобно! Приятного пользования!)"
    )


async def help(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"Я бот, который поможет тебе сохранить место, которое тебе понравилось, и"
        rf" узнать о нём нужную тебе информацию. Сперва сообщением отправь мне название места, и я дам тебе список мест"
        rf", которые мне удалось для тебя найти. Затем выбери из списка мест то, которое тебе нужно, и я пришлю тебе "
        rf"информацию о нём. Все очень легко, правда?) А как удобно! Приятного пользования!)"
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(MessageHandler(filters.TEXT, basic_response))

    application.run_polling()


if __name__ == '__main__':
    main()
