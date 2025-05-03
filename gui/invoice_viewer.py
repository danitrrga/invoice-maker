import customtkinter as ctk
from config import app_config
from db import InvoiceDB
from .theme import setup_theme

class InvoiceViewer(ctk.CTkToplevel):
    _instance = None
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Invoice Database Viewer")
        self.geometry("1200x800")
        self.theme = setup_theme(app_config)
        # Set window to always stay on top
        self.attributes("-topmost", True)
        # Set custom icon
        from .icons import get_icon_path
        icon_path = get_icon_path('database')
        try:
            self.iconbitmap(icon_path)
        except:
            pass  # Fallback to default icon if SVG conversion fails
        
        # Initialize selected invoices set
        self.selected_invoices = set()
        
        self.create_widgets()
        self.focus_force()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, **self.theme["frame"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create toolbar frame
        toolbar_frame = ctk.CTkFrame(main_frame, **self.theme["frame"])
        toolbar_frame.pack(fill="x", padx=5, pady=(5, 0))

        # Add delete button
        self.delete_button = ctk.CTkButton(
            toolbar_frame,
            text="Delete Selected",
            command=self.delete_selected_invoices,
            state="disabled",
            **self.theme["button"]
        )
        self.delete_button.pack(side="right", padx=5, pady=5)

        # Create table frame
        table_frame = ctk.CTkFrame(main_frame, **self.theme["frame"])
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create a scrollable frame for the table
        self.table_container = ctk.CTkScrollableFrame(table_frame, **self.theme["frame"])
        self.table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Headers configuration
        self.headers = [
            "Select", "Invoice ID", "Client", "Date", "Total", "Tax", "Method", "Status"
        ]
        self.column_widths = [50, 200, 250, 120, 100, 100, 150, 150]
        
        # Create header row
        header_frame = ctk.CTkFrame(self.table_container, fg_color=self.theme["button"]["fg_color"])
        header_frame.pack(fill="x", padx=2, pady=(0, 2))
        
        for i, (header, width) in enumerate(zip(self.headers, self.column_widths)):
            header_label = ctk.CTkLabel(
                header_frame,
                text=header,
                width=width,
                font=('Inter', 14, 'bold'),
                text_color=self.theme["text_color"]
            )
            header_label.grid(row=0, column=i, padx=2, pady=5)
        
        # Create container for data rows
        self.data_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.data_frame.pack(fill="both", expand=True)
        
        # Bind double click event to the data frame
        self.data_frame.bind("<Double-Button-1>", self.show_details)
        self.load_invoices()

    def load_invoices(self):
        # Clear existing rows
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        # Clear selected invoices
        self.selected_invoices.clear()
        self.update_delete_button()
        
        # Load and display invoices
        for row_idx, inv in enumerate(InvoiceDB.get_all_invoices()):
            row_frame = ctk.CTkFrame(self.data_frame, fg_color=self.theme["entry"]["fg_color"] if row_idx % 2 == 0 else "white")
            row_frame.pack(fill="x", padx=2, pady=1)
            
            # Add checkbox
            checkbox = ctk.CTkCheckBox(
                row_frame,
                text="",
                width=self.column_widths[0],
                command=lambda inv_id=inv[0]: self.toggle_invoice_selection(inv_id),
                **self.theme["checkbox"]
            )
            checkbox.grid(row=0, column=0, padx=2, pady=3)
            
            # Add invoice data
            for col_idx, (value, width) in enumerate(zip(inv, self.column_widths[1:])):
                if col_idx == 3 or col_idx == 4:  # Format Total and Tax amounts
                    value = f"${value:.2f}"
                cell = ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    width=width,
                    font=('Inter', 14),
                    text_color=self.theme["text_color"]
                )
                cell.grid(row=0, column=col_idx + 1, padx=2, pady=3)
                
                # Add double-click event for details
                if col_idx == 0:  # Invoice ID column
                    cell.bind("<Double-Button-1>", lambda e, inv_id=inv[0]: self.show_details_by_id(inv_id))
                
    def show_details_by_id(self, invoice_id):
        details = InvoiceDB.get_invoice_details(invoice_id)
        self.show_details_window(details)

    def show_details_window(self, details):
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(f"Invoice Details - {details[1]}")
        detail_window.geometry("600x400")
        
        # Create main frame
        main_frame = ctk.CTkFrame(detail_window, **self.theme["frame"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        fields = [
            ("Invoice ID:", details[1]),
            ("Client Name:", details[2]),
            ("Client Email:", details[3]),
            ("Client Phone:", details[4]),
            ("Client Address:", details[5]),
            ("Total Amount:", f"${details[6]:.2f}"),
            ("Tax Amount:", f"${details[7]:.2f}"),
            ("Invoice Date:", details[8]),
            ("Payment Method:", details[9]),
            ("Payment Entity:", details[10]),
            ("Status:", details[11])
        ]
        
        for i, (label, value) in enumerate(fields):
            label_widget = ctk.CTkLabel(
                main_frame,
                text=label,
                font=('Inter', 14, 'bold'),
                text_color=self.theme["text_color"]
            )
            label_widget.grid(row=i, column=0, padx=(20, 10), pady=5, sticky='e')
            
            value_widget = ctk.CTkLabel(
                main_frame,
                text=str(value),
                font=('Inter', 14),
                text_color=self.theme["text_color"]
            )
            value_widget.grid(row=i, column=1, padx=(10, 20), pady=5, sticky='w')
        
        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Center the window
        detail_window.update_idletasks()
        width = detail_window.winfo_width()
        height = detail_window.winfo_height()
        x = (detail_window.winfo_screenwidth() // 2) - (width // 2)
        y = (detail_window.winfo_screenheight() // 2) - (height // 2)
        detail_window.geometry(f"{width}x{height}+{x}+{y}")
        
    def toggle_invoice_selection(self, invoice_id):
        if invoice_id in self.selected_invoices:
            self.selected_invoices.remove(invoice_id)
        else:
            self.selected_invoices.add(invoice_id)
        self.update_delete_button()
    
    def update_delete_button(self):
        if self.selected_invoices:
            self.delete_button.configure(state="normal")
        else:
            self.delete_button.configure(state="disabled")
    
    def delete_selected_invoices(self):
        if not self.selected_invoices:
            return
            
        # Ask for confirmation
        confirm = ctk.CTkInputDialog(
            text=f"Are you sure you want to delete {len(self.selected_invoices)} invoice(s)? Type 'DELETE' to confirm:",
            title="Confirm Deletion"
        )
        if confirm.get_input() == "DELETE":
            for invoice_id in self.selected_invoices:
                try:
                    InvoiceDB.delete_invoice(invoice_id)
                except Exception as e:
                    print(f"Error deleting invoice {invoice_id}: {str(e)}")
            self.load_invoices()
    
    def show_details(self, event):
        # This method is kept for backward compatibility
        widget = event.widget
        if isinstance(widget, ctk.CTkFrame):
            # Get the invoice ID from the second cell in the row (after checkbox)
            invoice_id = widget.grid_slaves(row=0, column=1)[0]["text"]
            self.show_details_by_id(invoice_id)