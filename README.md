# Automated Invoice Generator

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)

A professional invoice generation system with GUI client management and Google Sheets integration.

## Features

- 🖥️ Graphical User Interface (GUI) with Tkinter
- 📄 PDF invoice generation from Word templates
- 📦 Client database management (JSON storage)
- ☁️ Google Sheets integration for accounting
- 🔢 Automatic calculations (taxes, totals)
- 🆔 Smart invoice ID generation
- 📁 Automatic filename suggestions
- 📱 Responsive UI with modern design
- 🔄 Real-time service calculations
- 📤 Multi-format export capabilities

## Installation

### Prerequisites
- Python 3.6+
- Google account for Sheets integration

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/invoice-generator.git
   cd invoice-generator
2. Install required libraries
    ```python
    pip install python-docx docx2pdf gspread oauth2client
3. Google Sheets Integration Setup

   1. Enable Google Sheets API
        - Go to Google Cloud Console
        - Create a new project or select an existing one
        - Enable "Google Sheets API" from the library
     
   3. Create Service Account credentials:
        - Navigate to "APIs & Services" > "Credentials"
        - Click "Create Credentials" > "Service Account"
        - Fill in details and create JSON key file

   3. Configure Google Sheet
        - Create a new Google Sheet named "Invoices"
        - Share the sheet with your service account email (found in JSON credentials)
        - Add these headers in the first row:
          ```csv
          Invoice ID, Date, Client Name, Client Email, Total Amount, Tax %, Tax Amount, Payment Method, Timestamp
          
   4. Application Configuration
       - Place credentials JSON file in project root
       - Rename it to credentials.json
       - Update configuration in code if needed:
          ```python
          # In configuration section
          GS_SHEET_NAME = "Invoices"  # Change to your sheet name
          GS_CREDENTIALS = "credentials.json"  # Keep this filename
    
  3. JSON Data Storage
     - Client Database (clients.json)
     - Automatically created and maintained by the application:
        ```json
        
        [
          {
            "id": "CLT-231015-A3B",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": "123 Client St, City, Country"
          }
        ]
  4. Configuration Variables
      - Update these in the code's configuration section:
        ```python
        # Essential configurations
        TEMPLATE_PATH = "invoice_template.docx"  # Word template path
        CLIENTS_DB = "clients.json"             # Client database file
        GS_CREDENTIALS = "credentials.json"     # Google API credentials
        # Business Information (modify with your details)
        BUSINESS_INFO = {
            "name": "Your Business Name",
            "email": "business@example.com",
            "phone": "+123 456 7890",
            "address": "123 Business St, City, Country"
        }
        # Color scheme (optional customization)
        COLOR_SCHEME = {
            "background": "#F0F0F0",
            "primary": "#2C3E50",
            "secondary": "#3498DB",
            "text": "#FFFFFF"
        }
  
## Usage
  1. Run the application
      ```bash
      python invoice_generator.py
  3. Manage clients
     - Add new clients with "New" button
     - Edit existing clients with "Edit" button
     - Select clients from dropdown
      
  4. Generate invoices
     - Enter service details (minimum 1 service required)
     - Add payment information
     - Click "Generate Invoice"
     - Choose save location (PDF suggested with invoice ID)

## Template Setup
Create invoice_template.docx with these exact placeholders:

  ```text
  [invoice_id] [date_time]
  [client_name] [client_email] [client_phone] [client_adress]
  [business_name] [business_email] [business_phone] [business_adress]
  
  Services Table:
  [service1] [s1num] [s1pri] [s1sum]
  [service2] [s2num] [s2pri] [s2sum]
  ...
  [service6] [s6num] [s6pri] [s6sum]
  
  Tax Section:
  [tax_%] [iva] [total_iva]
  
  Payment Details:
  [payment_method] [payment_entity] [payment_name] [payment_number]
