import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

ANSWER = range(1)

# Вопросы и варианты ответов
quiz = [
    {
        "q": "1. Что ты чувствуешь после пробуждения?\n"
             "1️⃣ ☀️ Спокойствие и радость от нового дня\n"
             "2️⃣ 😐 Ничего, просто начинаю дела\n"
             "3️⃣ 😣 Хочется ещё лежать и ничего не делать",
    },
    {
        "q": "2. Вспомни прошедшую неделю, как бы ты охарактеризовал(а) своё настроение?\n"
             "1️⃣ 😊 Ровное или приподнятое\n"
             "2️⃣ 😕 Небольшие перепады\n"
             "3️⃣ 😫 Чаще тяжёлое, чем лёгкое",
    },
    {
        "q": "3. Представь что у тебя появились свободные 30 минут. На что ты их потратишь?\n"
             "1️⃣ 📖 Отдохну так, как хочу (книга, музыка, прогулка)\n"
             "2️⃣ 📱 Буду листать соцсети без особого интереса\n"
             "3️⃣ 🫠 Отложу все дела и буду лежать без сил",
    },
    {
        "q": "4. Как ты реагируешь на неожиданные мелкие трудности?\n"
             "1️⃣ 🙂 Сохраняю спокойствие, решаю вопрос\n"
             "2️⃣ 😐 Немного напрягает, но справляюсь\n"
             "3️⃣ 😤 Очень раздражает или выбивает из колеи",
    },
    {
        "q": "5. Насколько часто тебе хотелось что-то срочно поменять в своей жизни?\n"
             "1️⃣ 🌿 Редко, меня в целом всё устраивает\n"
             "2️⃣ 🤔 Иногда появляются такие мысли\n"
             "3️⃣ 🔄 Очень часто хочется всё бросить или поменять",
    },
    {
        "q": "6. Как у тебя с привычными делами (учёба, работа, домашние обязанности)?\n"
             "1️⃣ 📝 Выполняю их нормально, в привычном ритме\n"
             "2️⃣ 😐 Иногда приходится заставлять себя\n"
             "3️⃣ 😫 Почти всегда тяжело даже начать",
    },
    {
        "q": "7. Что ты чаще всего чувствуешь при общении с другими людьми?\n"
             "1️⃣ 🫂 Интерес и тепло\n"
             "2️⃣ 😶 Просто общение «по необходимости»\n"
             "3️⃣ 🚪 Хочется быстрее закончить разговор",
    },
    {
        "q": "8. Если сравнить твою энергию с «батарейкой», каким бы сейчас был её заряд?\n"
             "1️⃣ 🔋 Почти полная (70–100%)\n"
             "2️⃣ 🔋 Наполовину (40–70%)\n"
             "3️⃣ 🔋 Почти разряжена (0–40%)",
    },
    {
        "q": "9. Что первым приходит в голову при мысли о ближайшей неделе?\n"
             "1️⃣ ✨ Любопытство, ожидание\n"
             "2️⃣ 😐 Всё равно, «как пойдёт»\n"
             "3️⃣ 😣 Тяжесть и нежелание",
    },
    {
        "q": "10. Что ты чаще всего ощущаешь перед сном?\n"
             "1️⃣ 🛏 Спокойствие, расслабленность\n"
             "2️⃣ 😕 Суета в мыслях, но удаётся уснуть\n"
             "3️⃣ 😫 Напряжение, тяжёлые мысли, долго ворочаюсь",
    },
]

# Для хранения состояния
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {"score": 0, "current_q": 0}

    await update.message.reply_text(
        "👋 Привет! Давай проверим твой уровень стресса!\n\n"
        "Отвечай цифрой (1, 2 или 3)."
    )

    return await ask_question(update, context)


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = user_data[chat_id]
    q_num = data["current_q"]

    if q_num < len(quiz):
        await update.message.reply_text(quiz[q_num]["q"])
        return ANSWER
    else:
        return await finish(update, context)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = user_data[chat_id]
    q_num = data["current_q"]

    text = update.message.text.strip()
    if text not in ["1", "2", "3"]:
        await update.message.reply_text("❗️Пожалуйста, ответь цифрой: 1, 2 или 3.")
        return ANSWER

    score = int(text)
    data["score"] += score
    data["current_q"] += 1
    user_data[chat_id] = data

    if data["current_q"] < len(quiz):
        return await ask_question(update, context)
    else:
        return await finish(update, context)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    score = user_data[chat_id]["score"]

    if 10 <= score <= 16:
        result = "🌿 Низкий уровень стресса: Отлично! Продолжай заботиться о себе 🫂"
    elif 17 <= score <= 23:
        result = "🌥 Средний уровень стресса: Уделяй больше внимания отдыху! 🫂"
    else:
        result = "🚨 Высокий уровень стресса: Обрати внимание на своё состояние, поговори с близкими или специалистом 🫂"

    await update.message.reply_text(
        f"✅ Тест завершён!\nТвои баллы: {score}\n\n{result}"
    )

    return ConversationHandler.END


def main():
    import os

    TOKEN = "8331858917:AAF8HRI3UDe7bN050PNHI215LnhH939Dk44"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]},
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    print("Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
