#!/usr/bin/env python3
import json
import logging
import subprocess
import random
import os

# Setup
logging.basicConfig(level=logging.INFO)
SCRIPT_PATH = "/home/tinyint/Bots/tc/tipo_cambio.py"
JSON_PATH = "/home/tinyint/Bots/tc/tipo_cambio.json"
PREVIOUS_JSON_PATH = "/home/tinyint/Bots/tc/tipo_cambio_prev.json"
WHATSAPP_GROUP = "50660429860-1446684378@g.us"
OPENCLAW_BIN = "/home/tinyint/.npm-global/bin/openclaw"

def load_json(path):
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except:
        pass
    return None

def save_previous(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving previous: {e}")

def send_whatsapp(text):
    try:
        result = subprocess.run(
            [
                OPENCLAW_BIN,
                "message",
                "send",
                "--channel",
                "whatsapp",
                "--target",
                WHATSAPP_GROUP,
                "--message",
                text,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        logging.info(f"WhatsApp sent: {result.stdout.strip()}")
    except Exception as e:
        logging.error(f"Error sending WhatsApp: {e}")

def format_rate(rate):
    if float(rate).is_integer():
        return f"₡{int(rate)}"
    return f"₡{rate:.2f}"

def build_vacilona(compra_prev, venta_prev, compra_new, venta_new):
    delta = round(venta_new - venta_prev, 2)
    if delta == 0:
        return None
    
    abs_delta = abs(delta)
    compra_text = format_rate(compra_new)
    venta_text = format_rate(venta_new)
    delta_text = f"{delta:+.2f}" if not abs_delta.is_integer() else f"{int(delta):+d}"
    
    if delta > 0:
        if abs_delta < 2:
            options = [
                f"🔥💸⚔️ ¡FIRST BLOOD! El dólar asoma los colmillos. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"💸🔥 ¡Se prendió esta vara! FIRST BLOOD. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"⚔️🔥💸 Primer sangre para la devaluación. {delta_text} CRC arriba. Compra: {compra_text} | Venta: {venta_text}",
            ]
        elif abs_delta < 3:
            options = [
                f"🔥⚔️💸 ¡DOUBLE KILL! ¡RAMPAGE! El Colón va jalando. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"💸🔥⚔️ ¡Dominando la partida! DOUBLE KILL financiero. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"⚔️💸🔥 RAMPAGE del dólar. El colón pidió incapacidad. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
            ]
        else:
            options = [
                f"🔥💸⚔️ ¡M-M-M-MONSTER KILL! ¡GODLIKE! APOCALIPSIS FINANCIERO. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"⚔️🔥💸 ¡GODLIKE! El colón se fue AFK. {delta_text} CRC arriba. Compra: {compra_text} | Venta: {venta_text}",
                f"💸🔥⚔️ MONSTER KILL bursátil. Arde la economía y se celebra. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
            ]
    else:
        if abs_delta < 3:
            options = [
                f"🥀💸⚰️ ¡DERROTA! F en el chat. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"⚰️💸🥀 Cayó el dólar. El sistema ha fallado. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"💸🥀 F. Nos estamos haciendo pobres. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
            ]
        else:
            options = [
                f"☠️🥀💸 ¡GAME OVER! Desinstalen la vida. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"💀⚰️💸 Fin de una era. El Colón ganó esta batalla. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
                f"🥀☠️ GAME OVER financiero. Qué tragedia nacional. {delta_text} CRC. Compra: {compra_text} | Venta: {venta_text}",
            ]
    
    return random.choice(options)

def main():
    # Ejecutar el script principal
    logging.info("Ejecutando tipo_cambio.py...")
    result = subprocess.run(
        ["python3", SCRIPT_PATH],
        capture_output=True,
        text=True,
    )
    logging.info(f"Script salió con código: {result.returncode}")
    
    # Cargar valores actuales
    current = load_json(JSON_PATH)
    previous = load_json(PREVIOUS_JSON_PATH)
    
    if not current:
        logging.warning("No se pudo cargar JSON actual")
        return
    
    # Si hay cambio, enviar a WhatsApp
    if previous and current.get("venta") != previous.get("venta"):
        compra_prev = float(previous["compra"])
        venta_prev = float(previous["venta"])
        compra_new = float(current["compra"])
        venta_new = float(current["venta"])
        message = build_vacilona(compra_prev, venta_prev, compra_new, venta_new)
        if message:
            logging.info(f"Detectado cambio: {venta_prev} → {venta_new}")
            send_whatsapp(message)
    
    # Guardar como previous para próxima ejecución
    save_previous(PREVIOUS_JSON_PATH, current)

if __name__ == "__main__":
    main()
