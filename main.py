from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from googleapiclient.discovery import build

TELEGRAM_TOKEN = '7364785286:AAFkoqysMBeQK3z2I-SORzaf5i6Bmm12Syg'
YOUTUBE_API_KEY = 'AIzaSyBsUZ2EFq1E2gBKuxNhBxIzHKozdY_ChWY'

user_languages = {}

# Тексты на разных языках
TEXTS = {
    'en': {
        'start': "👋 Hello! Send me any word (e.g., Messi, Barcelona) and I'll find you edits! To change language, use /language.",
        'choose_lang': "🌐 Choose your language:",
        'lang_set': "✅ Language set to English!",
        'searching': "🔍 Searching for: *{}*",
        'not_found': "❗ Nothing found. Try another word.",
        'error': "❌ Error: {}"
    },
    'ru': {
        'start': "👋 Привет! Напиши любое слово (например: Месси, Барселона), и я найду тебе эдиты! Чтобы сменить язык, используй /language.",
        'choose_lang': "🌐 Выбери язык:",
        'lang_set': "✅ Язык изменён на Русский!",
        'searching': "🔍 Ищу эдиты по запросу: *{}*",
        'not_found': "❗ Ничего не найдено. Попробуй другое слово.",
        'error': "❌ Ошибка: {}"
    },
    'uz': {
        'start': "👋 Salom! Istalgan so‘zni yozing (masalan: Messi, Barcelona), men sizga videolar topib beraman! Tilni o‘zgartirish uchun /language buyrug‘idan foydalaning.",
        'choose_lang': "🌐 Tilni tanlang:",
        'lang_set': "✅ Til o‘zgartirildi: O‘zbekcha!",
        'searching': "🔍 Qidirilmoqda: *{}*",
        'not_found': "❗ Hech narsa topilmadi. Boshqa so‘zni sinab ko‘ring.",
        'error': "❌ Xatolik: {}"
    }
}

def search_youtube(query, max_results=5):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results
    )
    response = request.execute()

    video_links = []
    for item in response['items']:
        video_id = item['id']['videoId']
        video_links.append(f"https://www.youtube.com/shorts/{video_id}")
    return video_links

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, 'en')
    await update.message.reply_text(TEXTS[lang]['start'])

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
        [InlineKeyboardButton("🇺🇿 Oʻzbekcha", callback_data='lang_uz')]
    ]
    await update.message.reply_text("🌐 Tilni tanlang / Choose language:", reply_markup=InlineKeyboardMarkup(keyboard))

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = query.data.split('_')[1]  # ru, en, uz
    user_id = query.from_user.id
    user_languages[user_id] = lang_code

    await query.edit_message_text(TEXTS[lang_code]['lang_set'])

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, 'en')
    query_text = update.message.text.strip()

    if not query_text:
        await update.message.reply_text(TEXTS[lang]['not_found'])
        return

    await update.message.reply_text(TEXTS[lang]['searching'].format(query_text), parse_mode='Markdown')

    try:
        links = search_youtube(query_text)
        if not links:
            await update.message.reply_text(TEXTS[lang]['not_found'])
            return

        await update.message.reply_text("\n".join(links))

    except Exception as e:
        await update.message.reply_text(TEXTS[lang]['error'].format(e))

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("language", language))
app.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_command))

app.run_polling()





































