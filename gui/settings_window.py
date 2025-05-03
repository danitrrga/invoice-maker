import customtkinter as ctk
from tkinter import filedialog, colorchooser, messagebox
from config import app_config, ConfigHandler
from .theme import setup_theme

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Application Settings")
        self.config = app_config.copy()
        self.theme = setup_theme(app_config)
        # Make window stay on top
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        self.attributes("-topmost", True)
        
        # Set window size and position
        window_width = 600
        window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.minsize(500, 400)  # Set minimum size
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, **self.theme["frame"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create a scrollable frame container
        self.scrollable_frame = ctk.CTkScrollableFrame(main_frame, **self.theme["frame"])
        self.scrollable_frame.pack(fill="both", expand=True)

        self.tab_view = ctk.CTkTabview(self.scrollable_frame, **self.theme["frame"])
        self.tab_view.pack(fill="both", expand=True)

        general_tab = self.tab_view.add("General")
        self.create_path_settings(general_tab)
        
        biz_tab = self.tab_view.add("Business")
        self.create_business_settings(biz_tab)
        
        appearance_tab = self.tab_view.add("Appearance")
        self.create_appearance_settings(appearance_tab)
        
        # Add reset button for color schemes
        reset_frame = ctk.CTkFrame(appearance_tab, **self.theme["frame"])
        reset_frame.pack(fill="x", pady=10, padx=5)
        ctk.CTkButton(reset_frame, 
                      text="Reset to Default Colors", 
                      command=self.reset_color_schemes,
                      **self.theme["button"]).pack(pady=5)

        btn_frame = ctk.CTkFrame(main_frame, **self.theme["frame"])
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Save", command=self.save_settings, **self.theme["button"]).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, **self.theme["button"]).pack(side="right")

    def create_path_settings(self, parent):
        frame = ctk.CTkFrame(parent, **self.theme["frame"])
        frame.pack(fill="both", pady=5, padx=5)
        ctk.CTkLabel(frame, text="File Paths", font=("Inter", 18, "bold")).pack(pady=5)
        self.create_path_row(frame, "Template Path:", "template_path", 0)
        self.create_path_row(frame, "Clients DB:", "clients_db", 1)
        self.create_path_row(frame, "Invoices DB:", "invoices_db", 2)

    def create_business_settings(self, parent):
        frame = ctk.CTkFrame(parent, **self.theme["frame"])
        frame.pack(fill="both", pady=5, padx=5)
        ctk.CTkLabel(frame, text="Business Information", font=("Inter", 18, "bold")).pack(pady=5)
        biz_fields = [
            ("Name:", "business_info", "name"),
            ("Email:", "business_info", "email"),
            ("Phone:", "business_info", "phone"),
            ("Address:", "business_info", "address")
        ]
        for i, (label, section, key) in enumerate(biz_fields):
            self.create_entry_row(frame, label, section, key, i)

    def create_appearance_settings(self, parent):
        frame = ctk.CTkFrame(parent, **self.theme["frame"])
        frame.pack(fill="both", pady=5, padx=5)
        
        # Theme mode selection
        theme_frame = ctk.CTkFrame(frame, **self.theme["frame"])
        theme_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(theme_frame, text="Theme Mode:", width=100).pack(side="left")
        theme_var = ctk.StringVar(value=self.config["theme_mode"])
        theme_menu = ctk.CTkOptionMenu(theme_frame, variable=theme_var, values=["light", "dark"])
        theme_menu.pack(side="left", padx=5)
        setattr(self, "theme_mode_var", theme_var)
        
        # Color scheme settings
        ctk.CTkLabel(frame, text="Color Scheme", font=("Inter", 18, "bold")).pack(pady=5)
        color_fields = [
            ("Background:", "background"),
            ("Surface:", "surface"),
            ("Primary:", "primary"),
            ("Secondary:", "secondary"),
            ("Text:", "text"),
            ("Highlight:", "highlight")
        ]
        
        # Create color settings for both light and dark themes
        for theme in ["light", "dark"]:
            ctk.CTkLabel(frame, text=f"{theme.capitalize()} Theme", font=("Inter", 14, "bold")).pack(pady=(10, 5))
            for i, (label, key) in enumerate(color_fields):
                self.create_color_row(frame, label, "color_scheme", theme, key, i)

    def create_path_row(self, parent, label, key, row):
        frame = ctk.CTkFrame(parent, **self.theme["frame"])
        frame.pack(fill="x", pady=4)
        ctk.CTkLabel(frame, text=label, width=100).pack(side="left")
        entry = ctk.CTkEntry(frame, **self.theme["entry"])
        entry.insert(0, self.config[key])
        entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(frame, text="Browse...", 
                    command=lambda k=key, e=entry: self.browse_file(k, e),
                    **self.theme["button"]).pack(side="left")
        setattr(self, f"{key}_entry", entry)

    def create_entry_row(self, parent, label, section, key, row):
        frame = ctk.CTkFrame(parent, **self.theme["frame"])
        frame.pack(fill="x", pady=4)
        ctk.CTkLabel(frame, text=label, width=100).pack(side="left")
        entry = ctk.CTkEntry(frame, **self.theme["entry"])
        entry.insert(0, self.config[section][key])
        entry.pack(side="left", fill="x", expand=True, padx=5)
        setattr(self, f"{section}_{key}_entry", entry)

    def create_color_row(self, parent, label, section, theme, key, row):
        frame = ctk.CTkFrame(parent, **self.theme["frame"])
        frame.pack(fill="x", pady=4)
        ctk.CTkLabel(frame, text=label, width=100).pack(side="left")
        entry = ctk.CTkEntry(frame, width=100, **self.theme["entry"])
        entry.insert(0, self.config[section][theme][key])
        entry.pack(side="left", padx=5)
        ctk.CTkButton(frame, text="Pick", 
                    command=lambda e=entry: self.pick_color(e),
                    **self.theme["button"]).pack(side="left")
        setattr(self, f"{section}_{theme}_{key}_entry", entry)

    def browse_file(self, key, entry):
        if key == "template_path":
            path = filedialog.askopenfilename(filetypes=[("Word Templates", "*.docx")])
        else:
            path = filedialog.asksaveasfilename()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def pick_color(self, entry):
        color = colorchooser.askcolor(title="Choose color", initialcolor=entry.get())
        if color[1]:
            entry.delete(0, tk.END)
            entry.insert(0, color[1])

    def reset_color_schemes(self):
        if messagebox.askyesno("Reset Colors", "Are you sure you want to reset all color schemes to default?"):
            # Reset both light and dark theme colors to default
            self.config["color_scheme"] = {
                "light": {
                    "background": "#ffffff",
                    "surface": "#f0f0f0",
                    "primary": "#1f538d",
                    "secondary": "#8D99AE",
                    "text": "#000000",
                    "highlight": "#14375e"
                },
                "dark": {
                    "background": "#2b2b2b",
                    "surface": "#1e1e1e",
                    "primary": "#3B82F6",
                    "secondary": "#64748B",
                    "text": "#ffffff",
                    "highlight": "#60A5FA"
                }
            }
            
            # Update all color entry fields
            for theme in ["light", "dark"]:
                for key in ["background", "surface", "primary", "secondary", "text", "highlight"]:
                    entry = getattr(self, f"color_scheme_{theme}_{key}_entry")
                    entry.delete(0, "end")
                    entry.insert(0, self.config["color_scheme"][theme][key])
            
            messagebox.showinfo("Colors Reset", "Color schemes have been reset to default values.")
    
    def save_settings(self):
        self.config["template_path"] = self.template_path_entry.get()
        self.config["clients_db"] = self.clients_db_entry.get()
        self.config["invoices_db"] = self.invoices_db_entry.get()

        biz_keys = ["name", "email", "phone", "address"]
        for key in biz_keys:
            self.config["business_info"][key] = getattr(self, f"business_info_{key}_entry").get()

        # Save theme mode and apply it immediately
        new_theme = self.theme_mode_var.get()
        self.config["theme_mode"] = new_theme
        
        # Apply the new theme immediately
        ctk.set_appearance_mode(new_theme)
        self.master.apply_theme(new_theme)

        # Save color scheme for both themes
        color_keys = ["background", "surface", "primary", "secondary", "text", "highlight"]
        for theme in ["light", "dark"]:
            for key in color_keys:
                self.config["color_scheme"][theme][key] = getattr(self, f"color_scheme_{theme}_{key}_entry").get()

        ConfigHandler.save_config(self.config)
        messagebox.showinfo("Settings Saved", 
                          "Some changes may require application restart to take effect")
        self.destroy()