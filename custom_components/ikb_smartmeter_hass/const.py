"""Konstanten für die IKB Smart Meter Integration (Kaifa MA309)."""

from homeassistant.const import Platform

# ---------------------------------------------------------------------------
# Integration-Identifikation
# ---------------------------------------------------------------------------

DOMAIN = "ikb_smartmeter_hass"
NAME   = "IKB Smart Meter"

# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------

ISSUE_URL = "https://github.com/luderas/ikb_smartmeter_hass/issues"
DOCS_URL  = "https://github.com/luderas/ikb_smartmeter_hass"

# ---------------------------------------------------------------------------
# Config-Entry-Schlüssel  (werden in config_entries.data gespeichert)
# ---------------------------------------------------------------------------

CONF_COM_PORT  = "com_port"    # Serieller Port, z. B. /dev/ttyUSB0
CONF_KEY_HEX   = "key_hex"     # AES-128-Schlüssel als 32-stelliger Hex-String
CONF_SERIAL_NO = "serial_no"   # Geräteseriennummer (wird als unique_id verwendet)

# ---------------------------------------------------------------------------
# Port-Typ-Auswahl (Config-Flow Schritt 1)
# ---------------------------------------------------------------------------

CONF_PORT_TYPE  = "port_type"
PORT_TYPE_BY_ID = "by-id"          # /dev/serial/by-id/... (stabiler Symlink)
PORT_TYPE_TTY   = "ttyUSB/ttyACM"  # /dev/ttyUSB0, /dev/ttyACM0, …

# ---------------------------------------------------------------------------
# Options-Schlüssel  (werden in config_entries.options gespeichert)
# ---------------------------------------------------------------------------

OPT_DATA_INTERVAL: str = "data_interval"  # Update-Intervall in Sekunden
OPT_DATA_INTERVAL_DEFAULT: int = 30       # Standardwert
OPT_DATA_INTERVAL_MIN: int = 5            # Minimum
OPT_DATA_INTERVAL_MAX: int = 3600         # Maximum


# ---------------------------------------------------------------------------
# Version & Startmeldung
# ---------------------------------------------------------------------------

VERSION = "0.0.1"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}  
Version: {VERSION}
Kaifa MA309 / IKB – lokale AES-128-CTR M-Bus Dekodierung
Probleme melden: {ISSUE_URL}
-------------------------------------------------------------------
"""
