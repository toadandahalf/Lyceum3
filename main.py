from telegram.ext import Application, MessageHandler, filters, CommandHandler

BOTTOKEN = '7166801459:AAFqB5svbsnPg2ASubf11ZKJr-SFip4J5yw'


async def echo(update, context):
    await update.message.reply_text('Я получил сообщение ' + update.message.text)


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}!) Я бот, который поможет тебе сохранить место, которое тебе понравилось, и"
        rf" узнать о нём нужную тебе информацию. Сперва сообщением отправь мне название места, и я дам тебе список мест"
        rf", которые мне удалось для тебя найти. Затем выбери из списка мест то, которое тебе нужно, и я пришлю тебе "
        rf"информацию о нём. Все очень легко, правда?) А как удобно! Приятного пользования!)"
    )


def main():
    application = Application.builder().token(BOTTOKEN).build()

    application.add_handler(CommandHandler("start", start))

    text_handler = MessageHandler(filters.TEXT, echo)

    application.add_handler(text_handler)

    application.run_polling()


if __name__ == '__main__':
    main()