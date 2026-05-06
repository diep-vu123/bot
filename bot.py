import os
import pdfplumber
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)


# ==================================
# TOKEN BOT TELEGRAM
# ==================================
TOKEN = os.getenv("TOKEN")


# ==================================
# DOC DU LIEU TU PDF
# ==================================
def load_pdf_data(file_path):
    data = {}

    try:
        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                # Thu doc bang truoc
                tables = page.extract_tables()

                if tables:
                    for table in tables:

                        # Bo qua dong tieu de
                        for row in table[1:]:

                            if not row or len(row) < 5:
                                continue

                            try:
                                # Cot du kien:
                                # STT | TEN SP | MA SP | SIZE | GIA BAN
                                product_name = str(row[1]).strip()
                                product_code = str(row[2]).strip().upper()
                                product_size = str(row[3]).strip()
                                product_price = str(row[4]).strip()

                                if product_code and product_price:
                                    data[product_code] = {
                                        "name": product_name,
                                        "size": product_size,
                                        "price": product_price
                                    }

                            except Exception:
                                continue

                else:
                    # Neu khong doc duoc bang thi doc text
                    text = page.extract_text()

                    if text:
                        lines = text.split("\n")

                        for line in lines:
                            parts = line.split()

                            # Co gang loc dong hop le
                            if len(parts) >= 5:
                                try:
                                    product_code = parts[0].strip().upper()
                                    product_price = parts[-1].strip()
                                    product_size = parts[-2].strip()
                                    product_name = " ".join(parts[1:-2])

                                    if product_code:
                                        data[product_code] = {
                                            "name": product_name,
                                            "size": product_size,
                                            "price": product_price
                                        }

                                except Exception:
                                    continue

    except FileNotFoundError:
        print("Khong tim thay file products.pdf")
    except Exception as e:
        print("Loi doc PDF:", e)

    return data


# ==================================
# LOAD SAN PHAM
# ==================================
product_data = load_pdf_data("products.pdf")

print(f"Da tai {len(product_data)} san pham.")


# ==================================
# LENH /start
# ==================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chao ban!\n"
        "Gui ma san pham de tra gia.\n"
        "Vi du: D1-107X1.2"
    )


# ==================================
# TRA GIA SAN PHAM
# ==================================
async def search_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()

    if code in product_data:
        product = product_data[code]

        response = (
            f"Ma SP: {code}\n"
            f"Ten SP: {product['name']}\n"
            f"Size: {product['size']}\n"
            f"Gia ban: {product['price']}"
        )

        await update.message.reply_text(response)

    else:
        # Tim gan dung
        similar_products = [
            key for key in product_data.keys()
            if code in key
        ]

        if similar_products:
            suggestion = "\n".join(similar_products[:10])

            await update.message.reply_text(
                f"Khong tim thay ma chinh xac.\n"
                f"Ban co muon tim:\n{suggestion}"
            )
        else:
            await update.message.reply_text(
                "Khong tim thay ma san pham."
            )


# ==================================
# MAIN
# ==================================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Start
    app.add_handler(CommandHandler("start", start))

    # Tim ma san pham
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_product
        )
    )

    print("Bot dang chay...")
    app.run_polling()


# ==================================
# CHAY BOT
# ==================================
if __name__ == "__main__":
    main()