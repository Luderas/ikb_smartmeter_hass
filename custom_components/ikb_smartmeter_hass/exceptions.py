"""Ausnahmen für die IKB Smart Meter Integration."""


class SmartmeterException(Exception):
    """Basisausnahme für alle Smartmeter-Fehler.
    
    Wird ausgelöst, wenn der empfangene Bytestrom nicht dem erwarteten
    M-Bus-Frame-Format entspricht oder die AES-Entschlüsselung fehlschlägt.
    """


class SmartmeterSerialException(SmartmeterException):
    """Serieller Port nicht verfügbar oder kann nicht geöffnet werden.
    
    Mögliche Ursachen:
    - Port-Pfad ungültig oder nicht vorhanden
    - Port bereits von einem anderen Prozess belegt
    - Falsches USB-Gerät angeschlossen
    """


class SmartmeterTimeoutException(SmartmeterException):
    """Kein gültiger M-Bus-Frame innerhalb des Zeitlimits empfangen.
    
    Mögliche Ursachen:
    - Smartmeter nicht erreichbar oder ausgeschaltet
    - Falsches USB-Gerät / falsche Baudrate
    - M-Bus-Verbindung unterbrochen
    """
