import logging
from telegram import Update, ReplyKeyboardMarkup
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

# Этапы диалога
ANSWER = range(1)

# Вопросы и варианты ответов
quiz = [
    {
        "q": "1. Что ты чувствуешь после пробуждения?",
        "options": [
            ("☀️ Спокойствие и радость от нового дня", 1),
            ("😐 Ничего, просто начинаю дела", 2),
            ("😣 Хочется ещё лежать и ничего не делать", 3),
        ],
    },
    {
        "q": "2. Вспомни прошедшую неделю, как бы ты охарактеризовал(а) своё настроение?",
        "options": [
            ("😊 Ровное или приподнятое", 1),
            ("😕 Небольшие перепады", 2),
            ("😫 Чаще тяжёлое, чем лёгкое", 3),
        ],
    },
    {
        "q": "3. Представь что у тебя появились свободные 30 минут. На что ты их потратишь?",
        "options": [
            ("📖 Отдохну так, как хочу (книга, музыка, прогулка)", 1),
            ("📱 Буду листать соцсети без особого интереса", 2),
            ("🫠 Отложу все дела и буду лежать без сил", 3),
        ],
    },
    {
        "q": "4. Как ты реагируешь на неожиданные мелкие трудности?",
        "options": [
            ("🙂 Сохраняю спокойствие, решаю вопрос", 1),
            ("😐 Немного напрягает, но справляюсь", 2),
            ("😤 Очень раздражает или выбивает из колеи", 3),
        ],
    },
    {
        "q": "5. Насколько часто тебе хотелось что-то срочно поменять в своей жизни?",
        "options": [
            ("🌿 Редко, меня в целом всё устраивает", 1),
            ("🤔 Иногда появляются такие мысли", 2),
            ("🔄 Очень часто хочется всё бросить или поменять", 3),
        ],
    },
    {
        "q": "6. Как у тебя с привычными делами (учёба, работа, домашние обязанности)?",
        "options": [
            ("📝 Выполняю их нормально, в привычном ритме", 1),
            ("😐 Иногда приходится заставлять себя", 2),
            ("😫 Почти всегда тяжело даже начать", 3),
        ],
    },
    {
        "q": "7. Что ты чаще всего чувствуешь при общении с другими людьми?",
        "options": [
            ("🫂 Интерес и тепло", 1),
            ("😶 Просто общение «по необходимости»", 2),
            ("🚪 Хочется быстрее закончить разговор", 3),
        ],
    },
    {
        "q": "8. Если сравнить твою энергию с «батарейкой», каким бы сейчас был её заряд?",
        "options": [
            ("🔋 Почти полная (70–100%)", 1),
            ("🔋 Наполовину (40–70%)", 2),
            ("🔋 Почти разряжена (0–40%)", 3),
        ],
    },
    {
        "q": "9. Что первым приходит в голову при мысли о ближайшей неделе?",
        "options": [
            ("✨ Любопытство, ожидание", 1),
            ("😐 Всё равно, «как пойдёт»", 2),
            ("😣 Тяжесть и нежелание", 3),
        ],
    },
    {
        "q": "10. Что ты чаще всего ощущаешь перед сном?",
        "options": [
            ("🛏 Спокойствие, расслабленность", 1),
            ("😕 Суета в мыслях, но удаётся уснуть", 2),
            ("😫 Напряжение, тяжёлые мысли, долго ворочаюсь", 3),
        ],
    },
]

# Для хранения состояния
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {"score": 0, "current_q": 0}

    await update.message.reply_text(
        "👋 Привет! Давай проверим твой уровень стресса!\n\n"
        "Отвечай на вопросы, выбирая подходящий вариант."
    )

    return await ask_question(update, context)


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = user_data[chat_id]
    q_num = data["current_q"]

    if q_num < len(quiz):
        q_data = quiz[q_num]
        options = [o[0] for o in q_data["options"]]

        reply_markup = ReplyKeyboardMarkup(
            [options], resize_keyboard=True, one_time_keyboard=True
        )

        await update.message.reply_text(q_data["q"], reply_markup=reply_markup)
        return ANSWER
    else:
        return await finish(update, context)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = user_data[chat_id]
    q_num = data["current_q"]

    chosen = update.message.text
    score = 0

    # ищем выбранный вариант
    for opt_text, opt_score in quiz[q_num]["options"]:
        if chosen == opt_text:
            score = opt_score

    if score == 0:  # если ввели что-то не то
        await update.message.reply_text("Пожалуйста, выбери вариант с кнопки.")
        return ANSWER

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

    TOKEN ="8331858917:AAF8HRI3UDe7bN050PNHI215LnhH939Dk44"
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
