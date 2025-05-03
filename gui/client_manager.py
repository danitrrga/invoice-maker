import customtkinter as ctk
from tkinter import messagebox
from config import app_config
from gui.theme import setup_theme

class ClientManager(ctk.CTkToplevel):
    def __init__(self, parent, client_data=None):
        super().__init__(parent)
        self.title("Manage Client" if client_data else "New Client")
        self.client_data = client_data or {}
        self.result = None
        self.theme = setup_theme(app_config)
        # Make window transient and set custom icon
        self.transient(parent)
        self.grab_set()
        from .icons import get_icon_path
        icon_path = get_icon_path('client')
        try:
            self.iconbitmap(icon_path)
        except:
            pass  # Fallback to default icon if SVG conversion fails
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, **self.theme["frame"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        fields = [
            ("Name:", "name"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Address:", "address")
        ]

        for i, (label, field) in enumerate(fields):
            row_frame = ctk.CTkFrame(main_frame, **self.theme["frame"])
            row_frame.pack(fill="x", pady=4)
            ctk.CTkLabel(row_frame, text=label, width=100, anchor="e").pack(side="left")
            entry = ctk.CTkEntry(row_frame, **self.theme["entry"])
            entry.pack(side="left", fill="x", expand=True, padx=5)
            if self.client_data:
                entry.insert(0, self.client_data.get(field, ""))
            setattr(self, f"{field}_entry", entry)

        btn_frame = ctk.CTkFrame(main_frame, **self.theme["frame"])
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Save", command=self.save, **self.theme["button"]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, **self.theme["button"]).pack(side="left")

    def save(self):
        data = {
            "name": self.name_entry.get(),
            "email": self.email_entry.get(),
            "phone": self.phone_entry.get(),
            "address": self.address_entry.get()
        }
        if not data["name"]:
            messagebox.showerror("Error", "Name is required")
            return
        self.result = data
        self.destroy()