import requests
import asyncio
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8290397833:AAHeJJrFHZy78do2RhpLYkc17uVK3Ssq35w"

alerts = []

# Ambil data market dari Gate.io
def get_market_data():
    url = "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=CC_USDT"
    r = requests.get(url).json()

    price = float(r[0]["last"])
    change = float(r[0]["change_percentage"])

    return price, change

# Ambil kurs USD ke IDR
def get_usd_idr():
    url = "https://open.er-api.com/v6/latest/USD"
    r = requests.get(url).json()
    return float(r["rates"]["IDR"])

# Command /price
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price_value, change = get_market_data()
        emoji = "📈" if change >= 0 else "📉"

        text = (
            "Canton Coin (CC)\n"
            f"Harga: ${price_value:.6f}\n"
            f"24h: {emoji} {change:.2f}%\n"
            "Market: Gate.io"
        )

        await update.message.reply_text(text)

    except:
        await update.message.reply_text("Gagal mengambil data harga.")

# Command /idr
async def idr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Contoh: /idr 300")
        return

    try:
        amount = float(context.args[0])

        price_usd, _ = get_market_data()
        rate = get_usd_idr()

        total_usd = amount * price_usd
        total_idr = total_usd * rate

        text = (
            "Canton Coin (CC)\n"
            f"{amount:.0f} CC =\n"
            f"${total_usd:.2f}\n"
            f"Rp {total_idr:,.0f}"
        )

        await update.message.reply_text(text)

    except:
        await update.message.reply_text("Format salah. Contoh: /idr 300")

# Command /value
async def value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Contoh: /value 300")
        return

    try:
        amount = float(context.args[0])

        price_usd, change = get_market_data()
        rate = get_usd_idr()

        total_usd = amount * price_usd
        total_idr = total_usd * rate

        emoji = "📈" if change >= 0 else "📉"

        text = (
            "Canton Coin (CC)\n"
            f"Harga: ${price_usd:.6f}\n"
            f"24h: {emoji} {change:.2f}%\n\n"
            f"{amount:.0f} CC =\n"
            f"${total_usd:.2f}\n"
            f"Rp {total_idr:,.0f}"
        )

        await update.message.reply_text(text)

    except:
        await update.message.reply_text("Format salah. Contoh: /value 300")

# Membaca pesan seperti "300 cc", "300cc", "1k cc"
async def convert_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    match = re.match(r"(\d+(\.\d+)?)(k?)\s*cc", text)
    if not match:
        return

    number = float(match.group(1))
    is_k = match.group(3)

    amount = number * 1000 if is_k == "k" else number

    try:
        price_usd, change = get_market_data()
        rate = get_usd_idr()

        total_usd = amount * price_usd
        total_idr = total_usd * rate

        emoji = "📈" if change >= 0 else "📉"

        reply = (
            "Canton Coin (CC)\n\n"
            f"Harga : ${price_usd:.6f}\n"
            f"24h   : {emoji} {change:.2f}%\n"
            "_Source: Gate.io_\n\n"
            f"{amount:,.0f} CC =\n"
            f"${total_usd:.2f}\n"
            f"Rp {total_idr:,.0f}"
        )

        await update.message.reply_text(reply, parse_mode="Markdown")

    except:
        await update.message.reply_text("Gagal mengambil data harga.")

# Command /alert
async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Contoh: /alert 0.15")
        return

    target = float(context.args[0])
    chat_id = update.effective_chat.id

    alerts.append({
        "target": target,
        "chat_id": chat_id
    })

    await update.message.reply_text(f"Alert diset: CC ≤ {target}")

# Loop alert
async def check_alerts(app):
    while True:
        for alert in alerts[:]:
            try:
                price, _ = get_market_data()
                if price <= alert["target"]:
                    await app.bot.send_message(
                        chat_id=alert["chat_id"],
                        text=f"Alert!\nHarga CC sekarang ${price:.6f}"
                    )
                    alerts.remove(alert)
            except:
                pass

        await asyncio.sleep(30)

async def post_init(app):
    asyncio.create_task(check_alerts(app))

print("Bot berjalan...")

app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("idr", idr))
app.add_handler(CommandHandler("value", value))
app.add_handler(CommandHandler("alert", alert_command))

# handler membaca "300 cc"
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_cc))

app.run_polling()
