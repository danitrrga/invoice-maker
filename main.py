import os
import json
import random
import string
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from docx import Document
from docx2pdf import convert
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==================== CONFIGURATION ====================
TEMPLATE_PATH = "invoice_template.docx"
CLIENTS_DB = "clients.json"
GS_CREDENTIALS = "credentials.json"
GS_SHEET_NAME = "Invoices"

BUSINESS_INFO = {
    "name": "Your Business Name",
    "email": "business@example.com",
    "phone": "+123 456 7890",
    "address": "123 Business St, City, Country"
}

COLOR_SCHEME = {
    "background": "#F0F0F0",
    "primary": "#2C3E50",
    "secondary": "#3498DB",
    "text": "#FFFFFF"
}
# =======================================================

def generate_id(prefix="INV"):
    """Generate unique ID with prefix, date, and random characters"""
    date_str = datetime.now().strftime("%y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_str}-{random_str}"

class GoogleSheetsManager:
    """Handles Google Sheets integration for invoice tracking"""
    
    @staticmethod
    def save_invoice(invoice_data):
        """Save invoice metadata to Google Sheets"""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(GS_CREDENTIALS, scope)
            client = gspread.authorize(creds)
            sheet = client.open(GS_SHEET_NAME).sheet1
            
            row = [
                invoice_data["invoice_id"],
                invoice_data["date"],
                invoice_data["client_name"],
                invoice_data["client_email"],
                invoice_data["total_amount"],
                invoice_data["tax_percent"],
                invoice_data["tax_amount"],
                invoice_data["payment_method"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
        except Exception as e:
            messagebox.showwarning("Cloud Save Error", 
                f"Invoice saved locally but failed to update Google Sheets:\n{str(e)}")

class ClientDB:
    """Manages client data storage in JSON format"""
    
    @staticmethod
    def load_clients():
        try:
            with open(CLIENTS_DB, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_clients(clients):
        with open(CLIENTS_DB, "w") as f:
            json.dump(clients, f, indent=2)

    @staticmethod
    def add_client(client_data):
        clients = ClientDB.load_clients()
        client_data["id"] = generate_id("CLT")
        clients.append(client_data)
        ClientDB.save_clients(clients)
        return client_data["id"]

    @staticmethod
    def update_client(client_id, new_data):
        clients = ClientDB.load_clients()
        for client in clients:
            if client["id"] == client_id:
                client.update(new_data)
                break
        ClientDB.save_clients(clients)

class ClientManager(tk.Toplevel):
    """Dialog window for managing client information"""
    
    def __init__(self, parent, client_data=None):
        super().__init__(parent)
        self.title("Manage Client" if client_data else "New Client")
        self.client_data = client_data or {}
        self.result = None
        self.build_ui()
        self.grab_set()

    def build_ui(self):
        fields = [
            ("Name", "name"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Address", "address")
        ]
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(self, text=f"{label}:").grid(row=i, column=0, padx=5, pady=2)
            entry = ttk.Entry(self)
            entry.grid(row=i, column=1, padx=5, pady=2)
            if self.client_data:
                entry.insert(0, self.client_data.get(field, ""))
            setattr(self, f"{field}_entry", entry)

        ttk.Button(self, text="Save", command=self.save).grid(row=4, columnspan=2, pady=10)

    def save(self):
        data = {
            "name": self.name_entry.get(),
            "email": self.email_entry.get(),
            "phone": self.phone_entry.get(),
            "address": self.address_entry.get()
        }
        if not data["name"]:
            messagebox.showerror("Error", "Client name is required")
            return
        self.result = data
        self.destroy()

class InvoiceApp(tk.Tk):
    """Main application window for invoice generation"""
    
    def __init__(self):
        super().__init__()
        self.title("Invoice Generator")
        self.configure(bg=COLOR_SCHEME["background"])
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        self.init_data()
        self.build_ui()
        self.load_clients()

    def configure_styles(self):
        style_configs = {
            "TFrame": {"background": COLOR_SCHEME["background"]},
            "TLabel": {"background": COLOR_SCHEME["background"], 
                      "foreground": COLOR_SCHEME["primary"]},
            "TButton": {"background": COLOR_SCHEME["secondary"], 
                       "foreground": COLOR_SCHEME["text"]},
            "TLabelFrame": {"background": COLOR_SCHEME["background"], 
                           "foreground": COLOR_SCHEME["primary"]},
            "TCombobox": {"fieldbackground": "white"}
        }
        for style, config in style_configs.items():
            self.style.configure(style, **config)

    def init_data(self):
        self.clients = []
        self.current_client_id = tk.StringVar()
        
        self.client_vars = {field: tk.StringVar() for field in ["name", "email", "phone", "address"]}
        
        self.services = []
        self.service_totals = []
        for i in range(6):
            service = {field: tk.StringVar() for field in ["desc", "qty", "price"]}
            for var in service.values():
                var.trace("w", lambda *args, idx=i: self.update_service(idx))
            self.services.append(service)
            self.service_totals.append(tk.StringVar(value="0.00"))
        
        self.tax_percent = tk.StringVar(value="21")
        self.payment_vars = {field: tk.StringVar() for field in ["method", "entity", "name", "number"]}

    def build_ui(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Invoice Generator", font=('Helvetica', 16, 'bold'), 
                foreground=COLOR_SCHEME["secondary"]).pack(side=tk.LEFT)
        
        business_info = "\n".join(BUSINESS_INFO.values())
        ttk.Label(header_frame, text=business_info, justify=tk.RIGHT).pack(side=tk.RIGHT)

        client_sel_frame = ttk.Frame(self)
        client_sel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(client_sel_frame, text="Select Client:").pack(side=tk.LEFT)
        self.client_cb = ttk.Combobox(client_sel_frame, textvariable=self.current_client_id, state="readonly")
        self.client_cb.pack(side=tk.LEFT, padx=5)
        self.client_cb.bind("<<ComboboxSelected>>", self.on_client_select)
        
        ttk.Button(client_sel_frame, text="New", command=self.new_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(client_sel_frame, text="Edit", command=self.edit_client).pack(side=tk.LEFT)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.build_client_section(main_frame)
        self.build_services_section(main_frame)
        self.build_payment_section(main_frame)
        
        ttk.Button(main_frame, text="Generate Invoice", command=self.generate_invoice, 
                  style="TButton").grid(row=3, column=0, pady=15)

    def build_client_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Client Details", padding=10)
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        fields = ["name", "email", "phone", "address"]
        for i, field in enumerate(fields):
            ttk.Label(frame, text=f"{field.title()}:").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            ttk.Entry(frame, textvariable=self.client_vars[field]).grid(row=i, column=1, pady=2, sticky="ew")

    def build_services_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Services", padding=10)
        frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        headers = ["Description", "Qty", "Price", "Total"]
        for col, header in enumerate(headers):
            ttk.Label(frame, text=header, font=('Helvetica', 9, 'bold')).grid(
                row=0, column=col, padx=5, pady=2, sticky="ew")

        self.service_rows = []
        for i in range(6):
            row = []
            for col, field in enumerate(["desc", "qty", "price"]):
                entry = ttk.Entry(frame, width=15, 
                                textvariable=self.services[i][field],
                                state="disabled" if i > 0 else "normal")
                entry.grid(row=i+1, column=col, padx=2, pady=2, sticky="ew")
                row.append(entry)
            
            total_label = ttk.Label(frame, textvariable=self.service_totals[i],
                                   background=COLOR_SCHEME["background"])
            total_label.grid(row=i+1, column=3, padx=5, pady=2, sticky="e")
            self.service_rows.append(row)

    def build_payment_section(self, parent):
        frame = ttk.Frame(parent)
        frame.grid(row=2, column=0, sticky="ew", pady=10)

        tax_frame = ttk.LabelFrame(frame, text="Tax Settings", padding=10)
        tax_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        ttk.Label(tax_frame, text="Tax Percentage (%):").pack(side=tk.LEFT)
        ttk.Entry(tax_frame, textvariable=self.tax_percent, width=8).pack(side=tk.LEFT, padx=5)

        payment_frame = ttk.LabelFrame(frame, text="Payment Details", padding=10)
        payment_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        fields = [
            ("Method", "method"),
            ("Entity", "entity"),
            ("Account Name", "name"),
            ("Account Number", "number")
        ]
        for i, (label, field) in enumerate(fields):
            ttk.Label(payment_frame, text=f"{label}:").grid(row=i, column=0, sticky="e", padx=2)
            ttk.Entry(payment_frame, textvariable=self.payment_vars[field]).grid(row=i, column=1, pady=2)

    def load_clients(self):
        self.clients = ClientDB.load_clients()
        self.client_cb["values"] = [f"{c['name']} ({c['id']})" for c in self.clients]

    def on_client_select(self, event):
        selected = self.client_cb.get()
        client_id = selected.split("(")[-1].strip(")")
        client = next((c for c in self.clients if c["id"] == client_id), None)
        if client:
            for field in ["name", "email", "phone", "address"]:
                self.client_vars[field].set(client.get(field, ""))

    def new_client(self):
        dialog = ClientManager(self)
        self.wait_window(dialog)
        if dialog.result:
            client_id = ClientDB.add_client(dialog.result)
            self.load_clients()
            self.current_client_id.set(f"{dialog.result['name']} ({client_id})")

    def edit_client(self):
        selected = self.client_cb.get()
        if not selected: return
        client_id = selected.split("(")[-1].strip(")")
        client = next((c for c in self.clients if c["id"] == client_id), None)
        if client:
            dialog = ClientManager(self, client)
            self.wait_window(dialog)
            if dialog.result:
                ClientDB.update_client(client_id, dialog.result)
                self.load_clients()
                self.on_client_select(None)

    def update_service(self, idx):
        try:
            qty = float(self.services[idx]["qty"].get() or 0)
            price = float(self.services[idx]["price"].get() or 0)
            self.service_totals[idx].set(f"{qty * price:.2f}")
        except ValueError:
            self.service_totals[idx].set("0.00")
        
        if idx < 5 and any(var.get() for var in self.services[idx].values()):
            for widget in self.service_rows[idx+1]:
                widget.config(state="normal")

    def generate_invoice(self):
        placeholders = {
            "[invoice_id]": generate_id(),
            "[date_time]": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "[client_name]": self.client_vars["name"].get(),
            "[client_email]": self.client_vars["email"].get(),
            "[client_phone]": self.client_vars["phone"].get(),
            "[client_adress]": self.client_vars["address"].get(),
            "[business_name]": BUSINESS_INFO["name"],
            "[business_email]": BUSINESS_INFO["email"],
            "[business_phone]": BUSINESS_INFO["phone"],
            "[business_adress]": BUSINESS_INFO["address"],
            "[tax_%]": self.tax_percent.get(),
            "[payment_method]": self.payment_vars["method"].get(),
            "[payment_entity]": self.payment_vars["entity"].get(),
            "[payment_name]": self.payment_vars["name"].get(),
            "[payment_number]": self.payment_vars["number"].get(),
        }

        subtotal = 0.0
        for i in range(6):
            qty = float(self.services[i]["qty"].get() or 0)
            price = float(self.services[i]["price"].get() or 0)
            total = qty * price
            subtotal += total
            placeholders.update({
                f"[service{i+1}]": self.services[i]["desc"].get(),
                f"[s{i+1}num]": f"{qty:.2f}",
                f"[s{i+1}pri]": f"{price:.2f}",
                f"[s{i+1}sum]": f"{total:.2f}"
            })

        try:
            tax_percent = float(self.tax_percent.get() or 0)
        except ValueError:
            tax_percent = 0.0
        iva = subtotal * (tax_percent / 100)
        placeholders.update({
            "[iva]": f"{iva:.2f}",
            "[total_iva]": f"{subtotal + iva:.2f}"
        })

        try:
            doc = Document(TEMPLATE_PATH)
            for p in doc.paragraphs:
                for key, value in placeholders.items():
                    if key in p.text:
                        p.text = p.text.replace(key, value)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            for key, value in placeholders.items():
                                if key in p.text:
                                    p.text = p.text.replace(key, value)
            
            temp_doc = "temp_invoice.docx"
            doc.save(temp_doc)
            
            output_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
                title="Save Invoice As",
                initialfile=f"{placeholders['[invoice_id]']}.pdf"
            )

            if output_path:
                convert(temp_doc, output_path)
                GoogleSheetsManager.save_invoice({
                    "invoice_id": placeholders["[invoice_id]"],
                    "date": placeholders["[date_time]"],
                    "client_name": placeholders["[client_name]"],
                    "client_email": placeholders["[client_email]"],
                    "total_amount": placeholders["[total_iva]"],
                    "tax_percent": placeholders["[tax_%]"],
                    "tax_amount": placeholders["[iva]"],
                    "payment_method": placeholders["[payment_method]"]
                })
                messagebox.showinfo("Success", f"Invoice saved to:\n{output_path}")
                
        except FileNotFoundError:
            messagebox.showerror("Error", f"Template file not found at {TEMPLATE_PATH}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice:\n{str(e)}")
        finally:
            if os.path.exists(temp_doc):
                os.remove(temp_doc)

if __name__ == "__main__":
    app = InvoiceApp()
    app.mainloop()