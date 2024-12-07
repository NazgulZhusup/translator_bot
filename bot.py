from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
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
}

# Тексты на разных языках
TEXTS = {
    "en": {
        "start": "Welcome! Please select your language:",
        "language_set": "Your language has been set to {}. Now send a message, and I will translate it for your partner.",
        "choose_language": "Please select a language from the list.",
        "not_set": "Please select your language first using the /start command.",
        "translation": "Translation:",
        "error": "An error occurred while translating. Please try again.",
    },
    "fr": {
        "start": "Bienvenue! Veuillez sélectionner votre langue :",
        "language_set": "Votre langue a été définie sur {}. Envoyez un message, et je le traduirai pour votre partenaire.",
        "choose_language": "Veuillez sélectionner une langue dans la liste.",
        "not_set": "Veuillez d'abord sélectionner votre langue avec la commande /start.",
        "translation": "Traduction :",
        "error": "Une erreur s'est produite lors de la traduction. Veuillez réessayer.",
    },
    "es": {
        "start": "¡Bienvenido! Por favor seleccione su idioma:",
        "language_set": "Su idioma ha sido configurado como {}. Ahora envíe un mensaje y lo traduciré para su compañero.",
        "choose_language": "Por favor seleccione un idioma de la lista.",
        "not_set": "Por favor seleccione su idioma primero usando el comando /start.",
        "translation": "Traducción:",
        "error": "Ocurrió un error al traducir. Por favor intente de nuevo.",
    },
    "de": {
        "start": "Willkommen! Bitte wählen Sie Ihre Sprache aus:",
        "language_set": "Ihre Sprache wurde auf {} eingestellt. Senden Sie jetzt eine Nachricht, und ich werde sie für Ihren Partner übersetzen.",
        "choose_language": "Bitte wählen Sie eine Sprache aus der Liste.",
        "not_set": "Bitte wählen Sie zuerst Ihre Sprache mit dem Befehl /start.",
        "translation": "Übersetzung:",
        "error": "Beim Übersetzen ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
    },
    "ko": {
        "start": "환영합니다! 언어를 선택하세요:",
        "language_set": "언어가 {}로 설정되었습니다. 이제 메시지를 보내면 번역해 드리겠습니다.",
        "choose_language": "목록에서 언어를 선택하세요.",
        "not_set": "/start 명령어를 사용하여 먼저 언어를 선택하세요.",
        "translation": "번역:",
        "error": "번역 중 오류가 발생했습니다. 다시 시도하세요.",
    },
    "ru": {
        "start": "Добро пожаловать! Пожалуйста, выберите язык:",
        "language_set": "Ваш язык установлен на {}. Теперь отправьте сообщение, и я переведу его для вашего собеседника.",
        "choose_language": "Пожалуйста, выберите язык из списка.",
        "not_set": "Пожалуйста, выберите язык с помощью команды /start.",
        "translation": "Перевод:",
        "error": "Произошла ошибка при переводе. Пожалуйста, попробуйте снова.",
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
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    text = update.message.text

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
        await update.message.reply_text("You are not connected to any chat. Use /start_chat or /connect to begin.")
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
    await update.message.reply_text(f"Your chat code: {chat_id}. Share it with your partner.")

# Подключение к чату
async def connect(update, context):
    user_id = update.message.chat_id
    if not context.args:
        await update.message.reply_text("Please provide a chat code. Example: /connect CHAT123")
        return

    chat_id = context.args[0]
    if chat_id not in chats:
        await update.message.reply_text("Invalid chat code.")
        return

    if chats[chat_id]["user_b"] is not None:
        await update.message.reply_text("This chat already has two participants.")
        return

    chats[chat_id]["user_b"] = user_id
    await update.message.reply_text("You have successfully joined the chat!")
    user_a_id = chats[chat_id]["user_a"]
    await context.bot.send_message(chat_id=user_a_id, text="Your partner has joined the chat!")

# Помощь
async def help_command(update, context):
    await update.message.reply_text(
        "Welcome to the chat bot! Here's how you can use it:\n"
        "/start - Set your language\n"
        "/start_chat - Create a new chat\n"
        "/connect <code> - Join an existing chat with a code\n"
        "Simply type a message to start chatting with your partner!"
    )

# Основная функция
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(LANGUAGES.keys())})$"), set_language))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("start_chat", start_chat))
    application.add_handler(CommandHandler("connect", connect))
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