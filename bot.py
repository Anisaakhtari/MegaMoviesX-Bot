import logging
import sqlite3
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll, PollOption
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from gtts import gTTS
import os

# 🔹 Bot Token & API Keys
TOKEN = "7519970324:AAGA1BlzUv4gKQPAzLbH4D4ICJX-cq171Es"
OMDB_API_KEY = "1f4a9bd6"
WELCOME_GIF = "https://media.giphy.com/media/J4fNXbGgX2OjRPZhvM/giphy.gif"

# 🔹 Database Setup
DB_FILE = "users.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, referred_by INTEGER)")
conn.commit()
conn.close()

# 🔹 Logging Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Welcome Message
async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    welcome_text = (
        "🎆✨ *Welcome to MegaMoviesX!* ✨🎆\n\n"
        "🎬 *Unlimited Movies, Unlimited Fun!* 🍿\n"
        "💰 *Earn & Watch Together!* 💸\n\n"
        "🔥 *What You Get?*\n"
        "✅ Instant Movie Search 🎞️\n"
        "✅ Download in 1-Click ⏬\n"
        "✅ Invite & Earn ₹5 per Friend 💵\n"
        "✅ Minimum Withdraw ₹500 🏦\n\n"
        "🚀 *Start Exploring Now!* 👇"
    )

    keyboard = [
        [InlineKeyboardButton("🔥 Explore Movies", callback_data="explore")],
        [InlineKeyboardButton("💰 Earn Money", callback_data="refer")],
        [InlineKeyboardButton("🎥 Movie Discussions", callback_data="discuss")],
        [InlineKeyboardButton("📞 Help & Support", url="https://t.me/MegaMoviesX_Support")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_animation(chat_id=user_id, animation=WELCOME_GIF, caption=welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

# 🔹 Movie Search Function
async def search_movie(update: Update, context: CallbackContext):
    query = update.message.text.strip()
    if not query:
        await update.message.reply_text("❌ Please provide a movie name.")
        return

    url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
    response = httpx.get(url).json()

    if response.get("Response") == "True":
        poster_url = response.get("Poster", "https://via.placeholder.com/300x400?text=No+Image")
        movie_info = (
            f"🎬 *{response['Title']} ({response['Year']})*\n"
            f"⭐ IMDB: {response['imdbRating']}\n"
            f"📅 Release Date: {response['Released']}\n"
            f"🎭 Genre: {response['Genre']}\n"
            f"🎬 Director: {response['Director']}\n"
            f"📝 Plot: {response['Plot']}\n"
            "\n⏬ *Download Now:* [Click Here](https://t.me/MegaMoviesX_bot)"
        )
        await update.message.reply_photo(photo=poster_url, caption=movie_info, parse_mode="Markdown")
    else:
        await update.message.reply_text("🚧 *Coming Soon!* 🚧\n"
                                        "🎥 This movie is not available right now.\n"
                                        "🔔 Stay tuned, we’ll upload it soon!\n"
                                        "📢 *Join our channel:* @MegaMoviesX_bot",
                                        parse_mode="Markdown")

# 🔹 Movie Discussion Feature
async def discuss_movie(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🎥 *Discuss Movies with Friends!* 🎥\n"
        "💬 Share your thoughts, reviews, and ratings.\n"
        "📢 Join the discussion: @MegaMoviesX_Chat"
    )

# 🔹 Poll Feature for Movie Ratings
async def movie_poll(update: Update, context: CallbackContext):
    question = "How would you rate the last movie you watched?"
    options = ["⭐ 1 Star", "⭐⭐ 2 Stars", "⭐⭐⭐ 3 Stars", "⭐⭐⭐⭐ 4 Stars", "⭐⭐⭐⭐⭐ 5 Stars"]

    await update.message.reply_poll(
        question=question,
        options=options,
        is_anonymous=False
    )

# 🔹 Refer & Earn
async def refer(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(f"💰 Refer & Earn ₹5 per friend!\n🔗 Share this link: {referral_link}")

# 🔹 Withdraw Request
async def withdraw(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()[0]
    conn.close()

    if balance >= 500:
        await update.message.reply_text("✅ Withdrawal request sent. You'll receive ₹500 soon!")
    else:
        await update.message.reply_text("❌ Minimum ₹500 required to withdraw.")

# 🔹 Bot Setup
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search_movie))
app.add_handler(CommandHandler("refer", refer))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("discuss", discuss_movie))
app.add_handler(CommandHandler("poll", movie_poll))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

# 🔹 Run Bot
app.run_polling()
