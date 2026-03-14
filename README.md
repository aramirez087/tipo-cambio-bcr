# Tipo de Cambio BCR

Script automático para monitorear el tipo de cambio desde el Banco Central de Costa Rica y notificar cambios a Telegram.

## Descripción

Este proyecto contiene dos scripts Python:

1. **`tipo_cambio.py`** - Script principal que:
   - Obtiene el tipo de cambio del sitio del Banco Central
   - Detecta cambios comparando con un JSON previo
   - Envía notificaciones a Telegram cuando hay cambios

2. **`tipo_cambio_con_whatsapp.py`** - Wrapper que:
   - Ejecuta el script principal
   - Además envía notificaciones "vacilonas" (en estilo gaming) a un grupo de WhatsApp
   - No interfiere con el funcionamiento original del script

## Requisitos

### Dependencias Python
```bash
pip install requests python-telegram-bot beautifulsoup4 schedule
```

### Variables de entorno (opcionales)

Para `tipo_cambio_con_whatsapp.py`:
```bash
export TIPO_CAMBIO_WHATSAPP_GROUP="50660429860-1446684378@g.us"  # JID del grupo de WhatsApp
export OPENCLAW_BIN="/home/tinyint/.npm-global/bin/openclaw"    # Ruta al binario de OpenClaw
```

### Configuración de Telegram
El script envía a un canal de Telegram. Las credenciales están hardcodeadas en el script original (actualizar antes de usar en producción).

### Configuración de WhatsApp
El wrapper usa OpenClaw CLI para enviar mensajes. Asegúrate de tener:
- OpenClaw instalado y funcionando
- WhatsApp Web vinculado
- El grupo correcto en la variable de entorno

## Uso

### Ejecución manual
```bash
python3 tipo_cambio.py              # Script principal
python3 tipo_cambio_con_whatsapp.py # Con notificación a WhatsApp
```

### Con systemd timer
Instalar como servicio:
```bash
sudo cp tipo_cambio.timer /etc/systemd/system/
sudo cp tipo_cambio.service /etc/systemd/system/
# Editar tipo_cambio.service para apuntar a tipo_cambio_con_whatsapp.py
sudo systemctl daemon-reload
sudo systemctl enable tipo_cambio.timer
sudo systemctl start tipo_cambio.timer
```

## Archivos

- `tipo_cambio.py` - Script principal (Telegram)
- `tipo_cambio_con_whatsapp.py` - Wrapper con notificaciones adicionales a WhatsApp
- `tipo_cambio.py.original` - Backup del script original
- `tipo_cambio.json` - Estado actual (compra/venta guardado)
- `tipo_cambio_prev.json` - Estado anterior (usado por el wrapper)

## Flujo

1. Script obtiene datos del BCR (tabla HTML con tipo de cambio)
2. Parsea la fila del banco configurado (ej: Banco BAC San José)
3. Compara con JSON previo guardado
4. Si hay cambio:
   - Envía notificación a Telegram (script principal)
   - Envía notificación "vacilona" a WhatsApp (wrapper)
   - Actualiza el JSON con nuevos valores

## Mensajes de WhatsApp

El wrapper genera mensajes estilo gaming basados en el delta del cambio:

- **FIRST BLOOD** (delta < 2): Pequeños cambios
- **DOUBLE KILL** (delta 2-3): Cambios moderados
- **MONSTER KILL** (delta > 3): Cambios grandes
- **DERROTA/GAME OVER** (delta negativo): El colón se fortalece

Ejemplo:
```
🔥⚔️💸 ¡DOUBLE KILL! ¡RAMPAGE! El Colón va jalando. +2.50 CRC. Compra: ₡462 | Venta: ₡479
```

## Debugging

Ver logs en tiempo real:
```bash
journalctl -u tipo_cambio.service -f
```

Pausar ejecuciones (sin eliminar timer):
```bash
touch /home/tinyint/Bots/tc/PAUSED
```

Reanudar:
```bash
rm /home/tinyint/Bots/tc/PAUSED
```

## Licencia

MIT
