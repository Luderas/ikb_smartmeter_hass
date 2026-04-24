"""Constants for the Smartmeter Austria (IKB / Kaifa MA309) integration."""
from homeassistant.const import Platform

DOMAIN = "smartmeter_austria"

# Base component constants
NAME        = "Smart Meter Austria Integration"
ISSUE_URL   = "https://github.com/NECH2004/smartmeter_austria/issues"

# Config entries
CONF_COM_PORT  = "com_port"
CONF_KEY_HEX   = "key_hex"
CONF_SERIAL_NO = "smartmeter_aut_serial_number"

# Port-type selector (config flow step 1)
CONF_PORT_TYPE        = "port_type"
PORT_TYPE_BY_ID       = "by-id"
PORT_TYPE_TTY         = "ttyUSB/ttyACM"

OPT_DATA_INTERVAL       = "smartmeter_aut_data_interval"
OPT_DATA_INTERVAL_VALUE: int = 30

"""List of platforms that are supported."""
PLATFORMS = [Platform.SENSOR]

# Version
VERSION = "1.4.11"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
Kaifa MA309 / IKB – AES-128-CTR M-Bus decoder (local, no pip dependency)
If you have any issues with this integration, please open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
