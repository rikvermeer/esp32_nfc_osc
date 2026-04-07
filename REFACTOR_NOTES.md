# Refactor Notities

## Uitgevoerde Wijzigingen

### Projectstructuur
Het project is opgesplitst in modulaire componenten:

```
esp32_nfc_controller/
├── src/
│   ├── main.py              # Orchestratie & boot flow
│   ├── config.py            # Config management (load/save)
│   ├── wifi_manager.py      # WiFi connectie & AP mode
│   ├── hardware.py          # I2C, NFC readers, displays
│   ├── osc_client.py        # OSC client wrapper
│   ├── setup_portal.py      # Web configuratie interface
│   ├── mapping.json         # NFC tag naar track mapping
│   └── lib/                 # MicroPython libraries
├── config.json.example      # Voorbeeld configuratie
└── README.md               # Documentatie
```

### Belangrijkste Verbeteringen

#### 1. **Geen Hardcoded Credentials** ✅
- WiFi SSID/password nu in `config.json`
- OSC server IP/port nu configureerbaar
- Defaults blijven beschikbaar als fallback

#### 2. **Setup Mode** ✅
- Activeer via boot button (GPIO 0)
- Automatische fallback bij WiFi fout
- Access Point: `NFC-SETUP` / `12345678`
- Web interface op `http://192.168.4.1`

#### 3. **Boot Flow** ✅
```
Start → Load Config → Check Setup Button
                    ↓
        Setup Mode ←──── WiFi Failed?
            ↓              ↓ No
        Web Portal    Normal Mode
            ↓              ↓
        Save Config   NFC/OSC Loop
            ↓
         Reboot
```

#### 4. **Geen Top-Level Side Effects** ✅
- Geen I2C init bij import
- Geen hardware scan bij import
- Geen OSC client init bij import
- Alle initialisatie in functies

#### 5. **Blocking/Sync Architecture** ✅
- Geen asyncio gebruikt
- Setup mode: blocking HTTP server
- Normal mode: blocking polling loop
- Twee aparte modi, geen mix

### Wat Werkt Nog Steeds

- ✅ NFC reader scanning via I2C multiplexer
- ✅ OLED display mapping
- ✅ Tag UID naar track mapping via `mapping.json`
- ✅ OSC berichten naar Ableton Live
- ✅ Display updates met status info
- ✅ Meerdere readers (6 tracks per reader)

### Testing Checklist

#### Test 1: Bestaande Functionaliteit
- [ ] Boot met geldige `config.json`
- [ ] WiFi verbindt
- [ ] NFC tags worden gelezen
- [ ] OSC berichten worden verstuurd
- [ ] Displays tonen correcte info

#### Test 2: Zonder Config
- [ ] Boot zonder `config.json`
- [ ] ESP32 gaat naar setup mode
- [ ] AP start: `NFC-SETUP`
- [ ] Web interface bereikbaar op 192.168.4.1

#### Test 3: Verkeerde WiFi
- [ ] Config met foute WiFi credentials
- [ ] Timeout na 15 seconden
- [ ] Fallback naar setup mode

#### Test 4: Web Configuratie
- [ ] Formulier velden tonen huidige waarden
- [ ] Ingevulde config wordt opgeslagen
- [ ] ESP32 reboot na save
- [ ] Nieuwe config wordt gebruikt

#### Test 5: Setup Button
- [ ] Boot button ingedrukt tijdens boot
- [ ] Setup mode wordt geforceerd
- [ ] Ook met geldige config

### Belangrijke Files

**`config.py`**
- `load_config()` - Laadt config of defaults
- `save_config(config)` - Slaat config op
- `config_exists()` - Check of config bestaat

**`wifi_manager.py`**
- `connect_wifi(ssid, password, timeout)` - WiFi connectie met timeout
- `start_access_point(essid, password)` - Start AP mode
- `is_wifi_connected(wlan)` - Check connectie status

**`hardware.py`**
- `init_i2c()` - Initialiseer I2C bus
- `scan_hardware()` - Scan NFC readers en displays
- `read_nfc_tag(reader)` - Lees NFC tag UID
- `print_lcd(display, text)` - Print naar OLED

**`osc_client.py`**
- `OSCClient(ip, port)` - OSC client klasse
- `.fire_clip(track, clip)` - Fire clip OSC bericht
- `.stop_track(track)` - Stop track OSC bericht
- `.stop_tracks(tracks)` - Stop meerdere tracks

**`setup_portal.py`**
- `run_setup_portal(ap)` - Blocking HTTP server
- HTML formulier voor configuratie
- POST handler met validatie
- Auto-reboot na save

### Upgrade Path

Voor bestaande installaties:
1. Backup huidige `main.py`
2. Upload nieuwe module bestanden
3. Delete oude `main.py`
4. Upload nieuwe `main.py`
5. ESP32 zal naar setup mode gaan
6. Configureer via web interface

### Technische Details

**WiFi Timeout**: 15 seconden (configureerbaar in `connect_wifi()`)

**Setup Button**: GPIO 0 (boot button op meeste ESP32 boards)

**AP IP**: 192.168.4.1 (standaard ESP32 AP gateway)

**Config Path**: `/config.json` (root van ESP32 filesystem)

**Mapping Path**: `/mapping.json` (root van ESP32 filesystem)

### Geen Breaking Changes

De NFC reader logica blijft identiek:
- Reader 0 → tracks 0-5
- Reader 1 → tracks 6-11
- Reader 2 → tracks 12-17
- Reader 3 → tracks 18-23

Display mapping: eerst gevonden display wordt gekoppeld aan eerst gevonden NFC reader.

Track assignment logica ongewijzigd.
