import os

# Icons configuration
ICONS = {
    'main': 'icon.ico',
    'database': 'database.ico',
    'client': 'client.ico',
    'settings': 'settings.ico'
}

def get_icon_path(icon_name):
    """Get the absolute path for an icon"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    icon_dir = os.path.join(base_dir, 'icons')
    icon_path = os.path.join(icon_dir, ICONS.get(icon_name, ICONS['main']))
    return icon_path if os.path.exists(icon_path) else os.path.join(base_dir, ICONS['main'])