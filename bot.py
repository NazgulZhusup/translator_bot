from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Глобальные переменные
user_languages = {}  # Словарь для хранения языка каждого пользователя
chats = {}  # Словарь для хранения информации о чатах

# Доступные языки
LANGUAGES = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Korean": "ko",
    "Russian": "ru",
    "Kyrgyz": "ky",
}

# Тексты на разных языках
# Тексты на разных языках
TEXTS = {
    "en": {
        "start": "Welcome! Please select your language:",
        "language_set": "Your language has been set to {}. Now send a message, and I will translate it for your partner.",
        "choose_language": "Please select a language from the list.",
        "not_set": "Please select your language first using the /start command.",
        "translation": "Translation:",
        "error": "An error occurred while translating. Please try again.",
        "exit_chat": "You have successfully exited the chat.",
        "no_chat": "You are not currently in any chat.",
    },
    "fr": {
        "start": "Bienvenue! Veuillez sélectionner votre langue :",
        "language_set": "Votre langue a été définie sur {}. Envoyez un message, et je le traduirai pour votre partenaire.",
        "choose_language": "Veuillez sélectionner une langue dans la liste.",
        "not_set": "Veuillez d'abord sélectionner votre langue avec la commande /start.",
        "translation": "Traduction :",
        "error": "Une erreur s'est produite lors de la traduction. Veuillez réessayer.",
        "exit_chat": "Vous avez quitté le chat avec succès.",
        "no_chat": "Vous n'êtes actuellement dans aucun chat.",
    },
    "es": {
        "start": "¡Bienvenido! Por favor seleccione su idioma:",
        "language_set": "Su idioma ha sido configurado como {}. Ahora envíe un mensaje y lo traduciré para su compañero.",
        "choose_language": "Por favor seleccione un idioma de la lista.",
        "not_set": "Por favor seleccione su idioma primero usando el comando /start.",
        "translation": "Traducción:",
        "error": "Ocurrió un error al traducir. Por favor intente de nuevo.",
        "exit_chat": "Has salido del chat con éxito.",
        "no_chat": "Actualmente no estás en ningún chat.",
    },
    "de": {
        "start": "Willkommen! Bitte wählen Sie Ihre Sprache aus:",
        "language_set": "Ihre Sprache wurde auf {} eingestellt. Senden Sie jetzt eine Nachricht, und ich werde sie für Ihren Partner übersetzen.",
        "choose_language": "Bitte wählen Sie eine Sprache aus der Liste.",
        "not_set": "Bitte wählen Sie zuerst Ihre Sprache mit dem Befehl /start.",
        "translation": "Übersetzung:",
        "error": "Beim Übersetzen ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
        "exit_chat": "Sie haben den Chat erfolgreich verlassen.",
        "no_chat": "Sie sind derzeit in keinem Chat.",
    },
    "ko": {
        "start": "환영합니다! 언어를 선택하세요:",
        "language_set": "언어가 {}로 설정되었습니다. 이제 메시지를 보내면 번역해 드리겠습니다.",
        "choose_language": "목록에서 언어를 선택하세요.",
        "not_set": "/start 명령어를 사용하여 먼저 언어를 선택하세요.",
        "translation": "번역:",
        "error": "번역 중 오류가 발생했습니다. 다시 시도하세요.",
        "exit_chat": "채팅을 성공적으로 종료했습니다.",
        "no_chat": "현재 채팅방에 없습니다.",
    },
    "ru": {
        "start": "Добро пожаловать! Пожалуйста, выберите язык:",
        "language_set": "Ваш язык установлен на {}. Теперь отправьте сообщение, и я переведу его для вашего собеседника.",
        "choose_language": "Пожалуйста, выберите язык из списка.",
        "not_set": "Пожалуйста, выберите язык с помощью команды /start.",
        "translation": "Перевод:",
        "error": "Произошла ошибка при переводе. Пожалуйста, попробуйте снова.",
        "exit_chat": "Вы успешно вышли из чата.",
        "no_chat": "Вы не находитесь в текущем чате.",
    },
    "ky": {
        "start": "Кош келиңиздер! Тилди тандаңыз:",
        "language_set": "Сиздин тилиңиз {} болуп орнотулду. Эми билдирүү жөнөтүңүз, мен аны өнөктөшүңүз үчүн которуп берем.",
        "choose_language": "Тизмеден тилди тандаңыз.",
        "not_set": "Биринчи тилди /start буйругу менен тандаңыз.",
        "translation": "Которуу:",
        "error": "Которууда ката кетти. Кайра аракет кылыңыз.",
        "exit_chat": "Сиз чаттан ийгиликтүү чыктыңыз.",
        "no_chat": "Сиз учурда эч кандай чатта жоксуз.",
    },
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    user_languages[user_id] = None  # Сбрасываем язык при запуске

    # Клавиатура выбора языков
    keyboard = [[lang] for lang in LANGUAGES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(TEXTS["en"]["start"], reply_markup=reply_markup)

# Установка языка
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    chosen_language = update.message.text

    if chosen_language in LANGUAGES:
        user_languages[user_id] = LANGUAGES[chosen_language]
        language_code = LANGUAGES[chosen_language]
        await update.message.reply_text(TEXTS[language_code]["language_set"].format(chosen_language))
    else:
        await update.message.reply_text(TEXTS["en"]["choose_language"])

# Перевод и передача сообщений
async def handle_message(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    if context.user_data.get("waiting_for_chat_code"):
        chat_code = text
        if chat_code in chats:
            if chats[chat_code]["user_b"] is None:
                chats[chat_code]["user_b"] = user_id
                await update.message.reply_text("You have successfully joined the chat!")
                user_a_id = chats[chat_code]["user_a"]
                await context.bot.send_message(chat_id=user_a_id, text="Your partner has joined the chat!")
            else:
                await update.message.reply_text("This chat already has two participants.")
        else:
            await update.message.reply_text("Invalid chat code.")
        context.user_data["waiting_for_chat_code"] = False
    else:
        # Обработка обычных сообщений
        if user_id not in user_languages or user_languages[user_id] is None:
            await update.message.reply_text(TEXTS["en"]["not_set"])
            return

        user_language = user_languages[user_id]
        target_language = "en" if user_language != "en" else "ru"

        # Найти собеседника в чате
        target_user_id = None
        for chat_id, chat in chats.items():
            if chat["user_a"] == user_id:
                target_user_id = chat["user_b"]
                break
            elif chat["user_b"] == user_id:
                target_user_id = chat["user_a"]
                break

        if target_user_id is None:
            await update.message.reply_text("You are not connected to any chat. Use /start_chat to begin.")
            return

        try:
            translated_text = GoogleTranslator(source=user_language, target=target_language).translate(text)
            await context.bot.send_message(chat_id=target_user_id, text=translated_text)
        except Exception as e:
            logging.error(f"Translation error: {e}")
            await update.message.reply_text(TEXTS[user_language]["error"])

# Создание чата
async def start_chat(update, context):
    user_id = update.message.chat_id
    if any(user_id in (chat["user_a"], chat["user_b"]) for chat in chats.values()):
        await update.message.reply_text("You have already started a chat.")
        return

    chat_id = f"CHAT{len(chats) + 1}"
    chats[chat_id] = {"user_a": user_id, "user_b": None}

    # Создаем клавиатуру с кнопкой для ввода кода чата
    keyboard = [
        [InlineKeyboardButton("Enter Chat Code", callback_data="enter_chat_code")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"Your chat code: {chat_id}. Share it with your partner.", reply_markup=reply_markup)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "enter_chat_code":
        await query.message.reply_text("Chat code:")
        context.user_data["waiting_for_chat_code"] = True

# Помощь
async def help_command(update, context):
    await update.message.reply_text(
        "Welcome to the chat bot! Here's how you can use it:\n"
        "/start - Set your language\n"
        "/start_chat - Create a new chat\n"
        "/exit_chat - Exit the current chat\n"
        "Simply type a message to start chatting with your partner!\n\n"
        "Example: /start_chat"
    )
async def exit_chat(update, context):
    user_id = update.message.chat_id
    chat_to_remove = None

    for chat_id, chat in chats.items():
        if chat["user_a"] == user_id or chat["user_b"] == user_id:
            chat_to_remove = chat_id
            break

    if chat_to_remove:
        del chats[chat_to_remove]
        await update.message.reply_text(TEXTS["en"]["exit_chat"])
    else:
        await update.message.reply_text(TEXTS["en"]["no_chat"])
# Основная функция
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(LANGUAGES.keys())})$"), set_language))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("start_chat", start_chat))
    application.add_handler(CommandHandler("exit_chat", exit_chat))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("help", help_command))

    # Запуск вебхуков
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="webhook",
        webhook_url="https://translator-bot-kxxv.onrender.com/webhook"
    )

if __name__ == "__main__":
    main()