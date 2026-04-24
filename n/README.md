# IKB Smart Meter – Home Assistant Integration

[![GitHub Release](https://img.shields.io/github/release/luderas/ikb_smartmeter_hass.svg)](https://github.com/luderas/ikb_smartmeter_hass/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Eine **lokale** Home Assistant Integration für den **Kaifa MA309** Smartmeter (IKB / Innsbrucker Kommunalbetriebe), der über einen M-Bus-zu-USB-Adapter ausgelesen wird.

Die Entschlüsselung erfolgt vollständig lokal mit **AES-128-CTR** – es werden keine Cloud-Dienste benötigt.

---

## Unterstützte Geräte

| Gerät | Netz | Protokoll |
|---|---|---|
| Kaifa MA309 | IKB (Innsbruck) | M-Bus Long Frame, AES-128-CTR |

---

## Voraussetzungen

- Home Assistant ≥ 2025.1.4
- M-Bus slave-zu-USB-Adapter
- AES-128 Schlüssel (16 Byte / 32 Hex-Zeichen) – bei IKB-direct(NETZ) anzufragen

---

## Installation via HACS

1. HACS öffnen → **Integrationen** → ⋮ → *Benutzerdefiniertes Repository hinzufügen*
2. URL: `https://github.com/luderas/ikb_smartmeter_hass` · Kategorie: *Integration*
3. Integration `IKB Smart Meter` suchen und installieren
4. Home Assistant neu starten
5. **Einstellungen → Geräte & Dienste → Integration hinzufügen → IKB Smart Meter**

### Manuelle Installation

```bash
cp -r custom_components/ikb_smartmeter_hass \
      <config>/custom_components/ikb_smartmeter_hass
```
Home Assistant neu starten und die Integration wie oben einrichten.

---

## Konfiguration

### Schritt 1 – Port-Typ wählen

| Option | Beschreibung |
|---|---|
| `by-id` | `/dev/serial/by-id/...` – stabiler Symlink, empfohlen |
| `ttyUSB/ttyACM` | `/dev/ttyUSB0`, `/dev/ttyACM0`, … |

### Schritt 2 – Port & Schlüssel

| Feld      | Beispiel                    | Beschreibung                              |
|           |                             |                                           |
| USB-Port  | `/dev/serial/by-id/usb-...` | Serieller Port des Adapters               |
| Schlüssel | `0123456789ABCDEF0123456789ABCDEF` | AES-128-Schlüssel (32 Hex-Zeichen) |

### Optionen (nach der Einrichtung)

| Option           | Standard | Bereich  | Beschreibung                      |

| Update-Intervall | 30 s     | 5–3600 s | Wie oft das Plugin abgefragt wird |

---

## Verfügbare Sensoren

### Standardmäßig aktiviert

| Sensor | Einheit | Beschreibung |
|---|---|---|
| Voltage L1 / L2 / L3 | V | Spannung je Phase |
| Current L1 / L2 / L3 | A | Strom je Phase |
| Real power in | W | Bezogene Wirkleistung (gesamt) |
| Real power out | W | Eingespeiste Wirkleistung (gesamt) |
| Real power delta | W | Differenz (Bezug − Einspeisung) |
| Real energy in | Wh | Zählerwert Bezug |
| Real energy out | Wh | Zählerwert Einspeisung |
| Reactive energy in / out | varh | Blindenergie Bezug / Einspeisung |

---

## Hardware-Anschluss

```
[Kaifa MA309]
  M-Bus RJ12  ──►  [M-Bus slave-zu-USB-Adapter]  ──►  USB des HA-Hosts
```

> **Hinweis für Docker / HA OS VM:** Den USB-Adapter als Gerät in den Container durchreichen:
> `--device=/dev/ttyUSB0`.

---

## Fehlerbehebung

### Debug-Logging aktivieren

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.ikb_smartmeter_hass: debug
```

### Häufige Fehler

| Fehler | Ursache | Lösung |
|---|---|---|
| `cannot_connect` | Falscher Port oder Kabel | Port und Verkabelung prüfen |
| `no_serial_ports` | Adapter nicht erkannt | USB-Adapter neu einstecken, `lsusb` prüfen |
| Timeout nach 15 s | Falscher Adapter oder Baudrate | Kaifa MA309 sendet bei 2400 Baud |
| Falsche Werte | Falscher Schlüssel | AES-128-Schlüssel erneut bei IKB anfragen |

---

## Lizenz

[MIT](LICENSE) © 2026 Luderas (Lukas Kritsotakis)
