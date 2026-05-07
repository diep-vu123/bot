import os
import pandas as pd
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler


# =================================
# TOKEN
# =================================
TOKEN = os.getenv("TOKEN")


# =================================
# DOC FILE EXCEL
# =================================
def load_excel_data(file_path):

    data = {}

    try:
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():

            product_code = str(row["MA_SP"]).strip().upper()

            data[product_code] = {
                "name": str(row["TEN_SP"]).strip(),
                "note": str(row["GHI_CHU"]).strip(),
                "price": str(row["GIA_BAN"]).strip()
            }

        print(f"Da tai {len(data)} san pham.")

    except Exception as e:
        print("Loi doc Excel:", e)

    return data


# =================================
# LOAD SAN PHAM
# =================================
product_data = load_excel_data("products.xlsx")


# =================================
# START
# =================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Bot tra gia san pham\n\n"
        "Co the tim:\n"
        "- Ma san pham\n"
        "- Ten san pham\n\n"
        "Vi du:\n"
        "D1-107X1.2\n"
        "Da cat"
    )


# =================================
# TIM SAN PHAM
# =================================
async def search_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    product_code = query.data

    if product_code in product_data:

        product = product_data[product_code]

        response = (
            f"Ma SP: {product_code}\n"
            f"Ten SP: {product['name']}\n"
            f"Ghi chu: {product['note']}\n"
            f"Gia ban: {product['price']}"
        )

        await query.message.reply_text(response)

    query = update.message.text.strip().upper()

    # =================================
    # TIM CHINH XAC MA SP
    # =================================
    if query in product_data:

        product = product_data[query]

        response = (
            f"Ma SP: {query}\n"
            f"Ten SP: {product['name']}\n"
            f"Ghi chu: {product['note']}\n"
            f"Gia ban: {product['price']}"
        )

        await update.message.reply_text(response)
        return

    # =================================
    # TIM THEO TEN SAN PHAM
    # =================================
    matched_products = []

    for code, product in product_data.items():

        product_name = product["name"].upper()

        if query in product_name:

            matched_products.append(
                f"Ma SP: {code}\n"
                f"Ten: {product['name']}\n"
                f"Ghi chu: {product['note']}\n"
                f"Gia: {product['price']}"
            )

    # =================================
    # NEU TIM THAY TEN
    # =================================
    if matched_products:

        result = "\n\n".join(matched_products[:10])

        await update.message.reply_text(
            f"Tim thay san pham:\n\n{result}"
        )

        return

    # =================================
    # TIM GAN DUNG MA SP
    # =================================
    similar_products = []

    for code in product_data.keys():

        if query in code:
            similar_products.append(code)

    if similar_products:

        keyboard = []

        for code in similar_products[:10]:

            keyboard.append(
                [
                    InlineKeyboardButton(
                        code,
                        callback_data=code
                    )
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Khong tim thay ma chinh xac.\n\nBan co muon tim:",
            reply_markup=reply_markup
        )

    else:

        await update.message.reply_text(
            "Khong tim thay san pham."
        )

# =================================
# MAIN
# =================================
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_product
        )
    )
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot dang chay...")

    app.run_polling()


# =================================
# RUN BOT
# =================================
if __name__ == "__main__":
    main()