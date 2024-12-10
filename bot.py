from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import random
import os
import logging

load_dotenv()

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
        "chat_created": "Your chat code: {}. Share it with your partner.",
        "enter_chat_code": "Please enter the chat code:",
        "chat_joined": "You have successfully joined the chat!",
        "chat_already_full": "This chat already has two participants.",
        "invalid_chat_code": "Invalid chat code.",
        "already_in_chat": "You are already in a chat. Use /exit_chat to leave the current chat.",
        "chat_not_found": "Chat not found. Please check the chat code and try again.",
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
        "chat_created": "Votre code de chat: {}. Partagez-le avec votre partenaire.",
        "enter_chat_code": "Veuillez entrer le code de chat:",
        "chat_joined": "Vous avez rejoint le chat avec succès!",
        "chat_already_full": "Ce chat a déjà deux participants.",
        "invalid_chat_code": "Code de chat invalide.",
        "already_in_chat": "Vous êtes déjà dans un chat. Utilisez /exit_chat pour quitter le chat actuel.",
        "chat_not_found": "Chat introuvable. Veuillez vérifier le code de chat et réessayer.",
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
        "chat_created": "Tu código de chat: {}. Compártelo con tu compañero.",
        "enter_chat_code": "Por favor ingrese el código de chat:",
        "chat_joined": "¡Has unido el chat con éxito!",
        "chat_already_full": "Este chat ya tiene dos participantes.",
        "invalid_chat_code": "Código de chat inválido.",
        "already_in_chat": "Ya estás en un chat. Usa /exit_chat para salir del chat actual.",
        "chat_not_found": "Chat no encontrado. Por favor verifique el código de chat y vuelva a intentarlo.",
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
        "chat_created": "Ihr Chat-Code: {}. Teilen Sie ihn mit Ihrem Partner.",
        "enter_chat_code": "Bitte geben Sie den Chat-Code ein:",
        "chat_joined": "Sie haben den Chat erfolgreich beigetreten!",
        "chat_already_full": "Dieser Chat hat bereits zwei Teilnehmer.",
        "invalid_chat_code": "Ungültiger Chat-Code.",
        "already_in_chat": "Sie sind bereits in einem Chat. Verwenden Sie /exit_chat, um den aktuellen Chat zu verlassen.",
        "chat_not_found": "Chat nicht gefunden. Bitte überprüfen Sie den Chat-Code und versuchen Sie es erneut.",
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
        "chat_created": "채팅 코드: {}. 파트너와 공유하세요.",
        "enter_chat_code": "채팅 코드를 입력하세요:",
        "chat_joined": "채팅에 성공적으로 참여했습니다!",
        "chat_already_full": "이 채팅에는 이미 두 명의 참가자가 있습니다.",
        "invalid_chat_code": "유효하지 않은 채팅 코드입니다.",
        "already_in_chat": "이미 채팅방에 있습니다. 현재 채팅방을 나가려면 /exit_chat을 사용하세요.",
        "chat_not_found": "채팅을 찾을 수 없습니다. 채팅 코드를 확인하고 다시 시도하세요.",
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
        "chat_created": "Ваш код чата: {}. Поделитесь им с вашим партнером.",
        "enter_chat_code": "Пожалуйста, введите код чата:",
        "chat_joined": "Вы успешно присоединились к чату!",
        "chat_already_full": "В этом чате уже есть два участника.",
        "invalid_chat_code": "Неверный код чата.",
        "already_in_chat": "Вы уже находитесь в чате. Используйте /exit_chat, чтобы покинуть текущий чат.",
        "chat_not_found": "Чат не найден. Пожалуйста, проверьте код чата и попробуйте снова.",
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
        "chat_created": "Сиздин чат коду: {}. Аны өнөктөшүңүз менен бөлүшүңүз.",
        "enter_chat_code": "Чат кодун киргизиңиз:",
        "chat_joined": "Сиз чатка ийгиликтүү кошулдуңуз!",
        "chat_already_full": "Бул чатта эки өнөктөш бар.",
        "invalid_chat_code": "Жараксыз чат коду.",
        "already_in_chat": "Сиз азырча чатта жоксуз. Азыркы чаттан чыгуу үчүн /exit_chat колдонуңуз.",
        "chat_not_found": "Чат табылган жок. Чат кодун текшерип, кайра аракет кылыңыз.",
    },
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    context.user_data["language"] = None  # Сбрасываем язык при запуске

    # Клавиатура выбора языков
    keyboard = [[lang] for lang in LANGUAGES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    try:
        await update.message.reply_text(TEXTS["en"]["start"], reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# Установка языка
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    chosen_language = update.message.text

    if chosen_language in LANGUAGES:
        context.user_data["language"] = LANGUAGES[chosen_language]
        language_code = LANGUAGES[chosen_language]
        await update.message.reply_text(TEXTS[language_code]["language_set"].format(chosen_language))
    else:
        await update.message.reply_text(TEXTS["en"]["choose_language"])
    await start(update, context)

async def handle_message(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    if context.user_data.get("waiting_for_chat_code"):
        await handle_chat_code_input(update, context)
        return

    user_language = context.user_data.get("language")
    if user_language is None:
        await update.message.reply_text(TEXTS["en"]["not_set"])
        return

    chat_data = next((chat for chat in context.bot_data.get("chats", {}).values()
                      if chat["user_a"] == user_id or chat["user_b"] == user_id), None)

    if not chat_data:
        await update.message.reply_text(TEXTS[user_language]["no_chat"])
        return

    if chat_data["user_a"] == user_id:
        target_user_id = chat_data["user_b"]
        target_language = chat_data.get("user_b_language", "en")
    else:
        target_user_id = chat_data["user_a"]
        target_language = chat_data.get("user_a_language", "en")

    logging.info(f"User Language: {user_language}, Target Language: {target_language}, Target User ID: {target_user_id}")

    if target_user_id is None:
        await update.message.reply_text(TEXTS[user_language]["no_chat"])
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
    if any(user_id in (chat["user_a"], chat["user_b"]) for chat in context.bot_data.get("chats", {}).values()):
        await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["already_in_chat"])
        return

    chat_code = f"{random.randint(0, 9999):04d}"  # Генерация 4-значного кода

    if "chats" not in context.bot_data:
        context.bot_data["chats"] = {}
    context.bot_data["chats"][chat_code] = {
        "user_a": user_id,
        "user_b": None,
        "user_a_language": context.user_data.get("language", "en")
    }

    await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["chat_created"].format(chat_code))

async def join_chat(update, context):
    user_id = update.message.chat_id
    if any(user_id in (chat["user_a"], chat["user_b"]) for chat in context.bot_data.get("chats", {}).values()):
        await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["already_in_chat"])
        return

    await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["enter_chat_code"])
    context.user_data["waiting_for_chat_code"] = True

# Обработчик ввода кода чата
async def handle_chat_code_input(update, context):
    if not context.user_data.get("waiting_for_chat_code"):
        return

    chat_code = update.message.text

    # Проверка, что чат-код состоит только из цифр и имеет длину 4 символа
    if not chat_code.isdigit() or len(chat_code) != 4:
        await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["invalid_chat_code"])
        return

    if chat_code in context.bot_data.get("chats", {}):
        chat = context.bot_data["chats"][chat_code]
        if chat["user_b"] is None:
            chat["user_b"] = update.message.chat_id
            chat["user_b_language"] = context.user_data.get("language", "en")
            await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["chat_joined"])
            await context.bot.send_message(chat_id=chat["user_a"], text=TEXTS[chat["user_a_language"]]["partner_joined"])
        else:
            await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["chat_already_full"])
    else:
        await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["invalid_chat_code"])

    context.user_data["waiting_for_chat_code"] = False
# Команда /exit_chat
async def exit_chat(update, context):
    user_id = update.message.chat_id
    chat_to_remove = None
    for chat_id, chat in context.bot_data.get("chats", {}).items():
        if chat["user_a"] == user_id or chat["user_b"] == user_id:
            chat_to_remove = chat_id
            break
    if chat_to_remove:
        del context.bot_data["chats"][chat_to_remove]
        await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["exit_chat"])
    else:
        await update.message.reply_text(TEXTS[context.user_data.get("language", "en")]["no_chat"])

async def help_command(update, context):
    await update.message.reply_text(
        "Welcome to the chat bot! Here's how you can use it:\n"
        "/start - Set your language\n"
        "/start_chat - Create a new chat\n"
        "/join_chat - Enter a chat code to join an existing chat\n"
        "/exit_chat - Exit the current chat\n"
        "Simply type a message to start chatting with your partner!\n\n"
        "Example: /start_chat"
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
    application.add_handler(CommandHandler("join_chat", join_chat))
    application.add_handler(CommandHandler("exit_chat", exit_chat))
    application.add_handler(CommandHandler("help", help_command))

    # Запуск вебхуков
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="webhook",
        webhook_url="https://translator-bot-kxxv.onrender.com"
    )

if __name__ == "__main__":
    main()