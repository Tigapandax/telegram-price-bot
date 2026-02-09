import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8290397833:AAGuJOm2LPZBYNXMUafNL_IFG56P1216x8g"
SYMBOL = "CCUSDT"

alerts = []

def get_price():
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={SYMBOL}"
    r = requests.get(url).json()
    return float(r["result"]["list"][0]["lastPrice"])

# Command /price
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price_value = get_price()
        text = (
            "Canton Coin (CC)\n"
            f"Harga: {price_value} USDT\n"
            "Source: Bybit"
        )
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("Gagal mengambil data harga.")

# Command /alert
async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Contoh penggunaan:\n/alert 0.15")
        r
