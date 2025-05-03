import customtkinter as ctk
from config import app_config as config, ConfigHandler

def setup_theme(config):
    # Configure global CustomTkinter theme
    theme_mode = config.get("theme_mode", "light")
    ctk.set_appearance_mode(theme_mode)
    ctk.set_default_color_theme("blue")
    
    # Configure custom colors
    if theme_mode in config["color_scheme"]:
        color_scheme = config["color_scheme"][theme_mode]
    else:
        # Fallback to light theme if the requested theme is not available
        color_scheme = config["color_scheme"]["light"]
    
    # Add derived colors if they don't exist
    if "primary_dark" not in color_scheme:
        if theme_mode == "dark":
            color_scheme["primary_dark"] = darken_color(color_scheme["primary"])
        else:
            color_scheme["primary_dark"] = darken_color(color_scheme["primary"])
    
    # Define custom button styles
    button_style = {
        "fg_color": color_scheme["primary"],
        "hover_color": color_scheme["primary_dark"],
        "text_color": "white" if theme_mode == "light" else color_scheme.get("text", "#FFFFFF"),
        "corner_radius": 10,
        "border_width": 0,
        "font": ("Inter", 18)
    }
    
    # Define text entry styles
    entry_style = {
        "fg_color": color_scheme["surface"],
        "border_color": color_scheme["secondary"],
        "text_color": color_scheme["text"],
        "corner_radius": 8,
        "border_width": 1,
        "font": ("Inter", 18)
    }
    
    # Define frame styles
    frame_style = {
        "fg_color": color_scheme["background"],
        "corner_radius": 10
    }
    
    # Define checkbox styles
    checkbox_style = {
        "fg_color": color_scheme["surface"],
        "border_color": color_scheme["secondary"],
        "text_color": color_scheme["text"],
        "hover_color": color_scheme["primary"],
        "checkmark_color": color_scheme["primary"],
        "corner_radius": 6
    }

    return {
        "button": button_style,
        "entry": entry_style,
        "frame": frame_style,
        "checkbox": checkbox_style,
        "text_color": color_scheme["text"]
    }


def darken_color(hex_color, factor=0.7):
    """Darken a hex color by a factor (0-1)"""
    # Remove the # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Darken
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    
    # Convert back to hex
    return f'#{r:02x}{g:02x}{b:02x}'

def apply_theme(theme, config):
    """Apply theme and save to configuration"""
    # Set appearance mode based on theme
    ctk.set_appearance_mode(theme)
    
    # Update config with the new theme mode
    config["theme_mode"] = theme
    ConfigHandler.save_config(config)
    
    # Get color scheme for the selected theme
    if theme in config["color_scheme"]:
        return config["color_scheme"][theme]
    else:
        # Fallback to light theme if the requested theme is not available
        ctk.set_appearance_mode("light")
        config["theme_mode"] = "light"
        ConfigHandler.save_config(config)
        return config["color_scheme"]["light"]

# Apply theme based on configuration
apply_theme(config.get("theme_mode", "light"), config)