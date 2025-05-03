from db import InvoiceDB
from gui import InvoiceApp

# Initialize the database
InvoiceDB.initialize()

if __name__ == "__main__":
    app = InvoiceApp()
    app.mainloop()
