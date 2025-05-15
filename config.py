import json

# ============= DEFAULT CONFIGURATION =============
DEFAULT_CONFIG = {
    "template_path": "invoice_template.docx",
    "clients_db": "clients.json",
    "invoices_db": "invoices.db",
    "business_info": {
        "name": "Your Business Name",
        "email": "business@example.com",
        "phone": "+123 456 7890",
        "address": "123 Business St, City, Country",
    },
    "color_scheme": {
        "light": {
            "background": "#F8F9FA",
            "surface": "#FFFFFF",
            "primary": "#2B2D42",
            "primary_dark": "#1E1F2E",
            "secondary": "#8D99AE",
            "text": "#2B2D42",
            "highlight": "#EF233C",
        },
        "dark": {
            "background": "#121212",
            "surface": "#1E1E1E",
            "primary": "#BB86FC",
            "primary_dark": "#8359B0",
            "secondary": "#03DAC6",
            "text": "#FFFFFF",
            "highlight": "#CF6679",
        },
    },
}

CONFIG_FILE = "app_config.json"


class ConfigHandler:
    @staticmethod
    def load_config():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            return DEFAULT_CONFIG

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)


# Load configuration and ensure theme_mode is set
app_config = ConfigHandler.load_config()

# Set default theme_mode if not present
if "theme_mode" not in app_config:
    app_config["theme_mode"] = "light"
    ConfigHandler.save_config(app_config)
