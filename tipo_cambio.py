import uuid
import logging
import json
import requests
import telegram
import os
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
import schedule
import time

# Constants
BCR_TC_URL = "https://gee.bccr.fi.cr/IndicadoresEconomicos/Cuadros/frmConsultaTCVentanilla.aspx"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TC_CHANNEL = os.getenv("TELEGRAM_CHANNEL_ID", "")
BANCO = "Banco BAC San José S.A."
BLOB_FILE_PATH = "tipo_cambio.json"
HTML_PARSER = "html.parser"
TABLE_ID = "Table2"
MAX_BANCO_LENGTH = 70

# Logging setup
logging.basicConfig(level=logging.INFO)

def get_html():
    """Do the request to the BCR bank"""
    url = BCR_TC_URL
    try:
        response = requests.get(url)
        logging.info(f"Request to {url} completed with status code {response.status_code}")
        return response.text
    except Exception as e:
        logging.error(f"Error during request to {url}: {str(e)}")
        return None

async def send_notification(compra, venta):
    # telegram
    bot_token = BOT_TOKEN
    channel_id = TC_CHANNEL
    bot = telegram.Bot(token=bot_token)
    msg = "Compra: " + str(compra) + "  |  Venta: " + str(venta)
    try:
        await bot.send_message(chat_id=channel_id, text=msg)
        logging.info("Notification sent successfully.")
    except Exception as e:
        logging.error(f"Error sending notification: {str(e)}")

def save_tipo_cambio(blob_path, compra, venta):
    tc = {"compra": compra, "venta": venta}
    try:
        with open(blob_path, "w") as outputblob:
            json.dump(tc, outputblob, indent=4)
        logging.info("Tipo de cambio saved successfully.")
    except Exception as e:
        logging.error(f"Error saving tipo de cambio: {str(e)}")

def get_tipo_cambio():
    compra, venta = 0, 0
    html_content = get_html()
    if html_content:
        try:
            table = BeautifulSoup(html_content, features=HTML_PARSER).find("table", {"id": TABLE_ID})
            bank_tag = BANCO
            insert_spaces = " " * (MAX_BANCO_LENGTH - len(bank_tag))
            tag = bank_tag + insert_spaces
            td_tag = table.find("td", text=tag)

            if (td_tag and td_tag.findNext("td").text and td_tag.findNext("td").findNext("td").text):
                compra = float(td_tag.findNext("td").text.strip().replace(',', '.'))
                venta = float(td_tag.findNext("td").findNext("td").text.strip().replace(',', '.'))
                logging.info(f"Tipo de cambio obtained: Compra - {compra}, Venta - {venta}")
            else:
                logging.warning("TD tag not found in the table.")
        except Exception as e:
            logging.error(f"Error parsing HTML content: {str(e)}")
    else:
        logging.error("Received no HTML content to parse.")
    return compra, venta

def any_changes(blob_path, compra, venta):
    try:
        if not os.path.exists(blob_path) or os.path.getsize(blob_path) == 0:
            return True
        with open(blob_path, "r") as inputblob:
            tipo_cambio_anterior = json.load(inputblob)
            compra_anterior = float(tipo_cambio_anterior["compra"])
            venta_anterior = float(tipo_cambio_anterior["venta"])
            return compra_anterior != compra or venta_anterior != venta
    except Exception as e:
        logging.error(f"Error checking for changes: {str(e)}")
        return True

async def main():
    compra, venta = get_tipo_cambio()

    if compra and venta and any_changes(BLOB_FILE_PATH, compra, venta):
        await send_notification(compra, venta)
        save_tipo_cambio(BLOB_FILE_PATH, compra, venta)
    else:
        logging.info("No changes detected or unable to obtain tipo de cambio.")

    logging.info("Function execution completed.")

if __name__ == "__main__":
    asyncio.run(main())
    