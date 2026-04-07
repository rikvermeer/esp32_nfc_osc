import json

DEFAULT_CONFIG = {
    "wifi_ssid": "network",
    "wifi_password": "password",
    "osc_server_ip": "192.168.1.3",
    "osc_server_port": 11000,
    "ap_ssid": "NFC-SETUP",
    "ap_password": "12345678"
}

def config_exists():
    """Check if config file exists"""
    try:
        with open('/config.json', 'r') as f:
            return True
    except OSError:
        return False

def load_config():
    """Load configuration from file or return defaults"""
    try:
        with open('/config.json', 'r') as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            result = DEFAULT_CONFIG.copy()
            result.update(config)
            return result
    except OSError:
        print("Config file not found, using defaults")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    try:
        with open('/config.json', 'w') as f:
            json.dump(config, f)
        print("Config saved successfully")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
