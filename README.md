# Automated Invoice Generator

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

A professional invoice generation system with GUI client management and SQL database integration.

## Features

- 🖥️ Graphical User Interface (GUI) with Tkinter
- 📄 PDF invoice generation from Word templates
- 📦 **SQL database management** for clients and invoices
- 🔢 Automatic calculations (taxes, totals)
- 🆔 Smart invoice ID generation
- 📁 Automatic filename suggestions
- 📱 Responsive UI with modern design
- 🔄 Real-time service calculations
- 📤 Multi-format export capabilities
- ⚙️ **Settings tab** for business configuration
- 🔒 Data persistence with relational database

## Installation

### Prerequisites
- Python 3.6+
- SQLite (included with Python)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/invoice-generator.git
   cd invoice-generator
   ```

2. **Install required libraries**
   ```bash
   pip install python-docx docx2pdf
   ```

3. **Database Setup**
   - The application automatically creates an SQLite database (`invoices.db`) on first launch
   - Schema includes tables for:
     - Clients
     - Invoices
     - Services
     - Business configurations

4. **Configuration**
   - Modify template path if needed in the code (optional):
     ```python
     TEMPLATE_PATH = "invoice_template.docx"  # Word template path
     ```
   - **All other configurations** (business info, colors, etc.) can be set via the **Settings Tab** in the GUI

## Usage

1. **Run the application**
   ```bash
   python invoice_generator.py
   ```

2. **Settings Tab**
   - Configure business details (name, address, email)
   - Customize UI color scheme
   - Set default tax rates and payment methods
   - Accessed via the gear icon (⚙️) in the toolbar

3. **Manage clients**
   - Add/edit clients using intuitive forms
   - Client data stored in SQL database
   - Search and filter clients directly in the UI

4. **Generate invoices**
   - Select client from database
   - Add services with real-time cost calculations
   - Preview PDF before saving
   - Invoices automatically recorded in the database

## Template Setup

Create `invoice_template.docx` with these exact placeholders:

```text
[invoice_id] [date_time]
[client_name] [client_email] [client_phone] [client_address]
[business_name] [business_email] [business_phone] [business_address]

Services Table:
[service1] [s1num] [s1pri] [s1sum]
[service2] [s2num] [s2pri] [s2sum]
...
[service6] [s6num] [s6pri] [s6sum]

Tax Section:
[tax_%] [iva] [total_iva]

Payment Details:
[payment_method] [payment_entity] [payment_name] [payment_number]
```

## Database Structure
- **Clients Table**  
  `id, name, email, phone, address, created_at`
- **Invoices Table**  
  `id, client_id, date, total, tax_amount, payment_method, timestamp`
- **Services Table**  
  `id, invoice_id, description, quantity, unit_price`
- **Settings Table**  
  `business_name, business_email, business_phone, business_address, tax_rate, color_scheme`

## Support
For issues or feature requests, open an issue on the [GitHub repository](https://github.com/yourusername/invoice-generator).

<p align="center" style="text-color: #B2B2B2;">Thanks for using my work 🤗</p>
