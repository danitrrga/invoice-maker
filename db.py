import json
import os
import sqlite3
from datetime import datetime
import random
import string
from config import app_config

def generate_id(prefix="INV"):
    date_str = datetime.now().strftime("%y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_str}-{random_str}"

class ClientDB:
    @staticmethod
    def load_clients():
        try:
            with open(app_config["clients_db"], "r", encoding='utf-8') as f:
                try:
                    clients = json.load(f)
                    if not isinstance(clients, list):
                        clients = []
                except json.JSONDecodeError:
                    clients = []
                
                # Validate and ensure all clients have required fields
                validated_clients = []
                for client in clients:
                    if isinstance(client, dict) and client.get("id") and client.get("name"):
                        # Ensure all required fields exist
                        client.setdefault("email", "")
                        client.setdefault("phone", "")
                        client.setdefault("address", "")
                        client.setdefault("created_at", datetime.now().isoformat())
                        validated_clients.append(client)
                return validated_clients
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(app_config["clients_db"], "w", encoding='utf-8') as f:
                json.dump([], f, indent=2)
            return []
        except json.JSONDecodeError:
            # Backup corrupted file and create new one
            backup_name = f"clients_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename(app_config["clients_db"], backup_name)
            with open(app_config["clients_db"], "w", encoding='utf-8') as f:
                json.dump([], f, indent=2)
            return []

    @staticmethod
    def save_clients(clients):
        # Validate clients before saving
        validated_clients = []
        for client in clients:
            if isinstance(client, dict) and client.get("id") and client.get("name"):
                # Ensure all required fields exist
                client.setdefault("email", "")
                client.setdefault("phone", "")
                client.setdefault("address", "")
                client.setdefault("created_at", datetime.now().isoformat())
                validated_clients.append(client)
        
        try:
            with open(app_config["clients_db"], "w", encoding='utf-8') as f:
                json.dump(validated_clients, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save clients: {str(e)}")

    @staticmethod
    def add_client(client_data):
        if not client_data.get("name"):
            raise ValueError("Client name is required")
        clients = ClientDB.load_clients()
        client_data["id"] = generate_id("CLT")
        client_data["created_at"] = datetime.now().isoformat()
        clients.append(client_data)
        ClientDB.save_clients(clients)
        return client_data["id"]

    @staticmethod
    def update_client(client_id, new_data):
        clients = ClientDB.load_clients()
        updated = False
        for client in clients:
            if client["id"] == client_id:
                client.update(new_data)
                client["updated_at"] = datetime.now().isoformat()
                updated = True
                break
        if not updated:
            raise ValueError(f"Client with ID {client_id} not found")
        ClientDB.save_clients(clients)

    @staticmethod
    def search_clients(query):
        clients = ClientDB.load_clients()
        query = query.lower()
        return [client for client in clients if
                query in client.get("name", "").lower() or
                query in client.get("email", "").lower() or
                query in client.get("phone", "").lower() or
                query in client.get("address", "").lower()]

    @staticmethod
    def get_client(client_id):
        clients = ClientDB.load_clients()
        for client in clients:
            if client["id"] == client_id:
                return client
        return None

    @staticmethod
    def delete_client(client_id):
        clients = ClientDB.load_clients()
        initial_length = len(clients)
        clients = [client for client in clients if client["id"] != client_id]
        if len(clients) == initial_length:
            raise ValueError(f"Client with ID {client_id} not found")
        ClientDB.save_clients(clients)


class InvoiceDB:
    @staticmethod
    def initialize():
        conn = sqlite3.connect(app_config["invoices_db"])
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      invoice_id TEXT UNIQUE,
                      client_name TEXT,
                      client_email TEXT,
                      client_phone TEXT,
                      client_address TEXT,
                      total_amount REAL,
                      tax_amount REAL,
                      invoice_date TEXT,
                      payment_method TEXT,
                      payment_entity TEXT,
                      status TEXT DEFAULT 'pending',
                      created_at TEXT,
                      updated_at TEXT)''')
        conn.commit()
        conn.close()

    @staticmethod
    def save_invoice(invoice_data):
        required_fields = ['invoice_id', 'client_name', 'total_amount']
        for field in required_fields:
            if not invoice_data.get(field):
                raise ValueError(f"{field} is required")

        conn = sqlite3.connect(app_config["invoices_db"])
        try:
            c = conn.cursor()
            invoice_data['created_at'] = datetime.now().isoformat()
            invoice_data['updated_at'] = invoice_data['created_at']
            c.execute('''INSERT INTO invoices 
                         (invoice_id, client_name, client_email, client_phone, client_address,
                          total_amount, tax_amount, invoice_date, payment_method, payment_entity,
                          status, created_at, updated_at)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (invoice_data['invoice_id'],
                       invoice_data['client_name'],
                       invoice_data.get('client_email', ''),
                       invoice_data.get('client_phone', ''),
                       invoice_data.get('client_address', ''),
                       invoice_data['total_amount'],
                       invoice_data.get('tax_amount', 0.0),
                       invoice_data.get('invoice_date', datetime.now().isoformat()),
                       invoice_data.get('payment_method', ''),
                       invoice_data.get('payment_entity', ''),
                       invoice_data.get('status', 'pending'),
                       invoice_data['created_at'],
                       invoice_data['updated_at']))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Invoice ID {invoice_data['invoice_id']} already exists")
        finally:
            conn.close()

    @staticmethod
    def get_all_invoices(filters=None, order_by='invoice_date DESC'):
        conn = sqlite3.connect(app_config["invoices_db"])
        try:
            c = conn.cursor()
            query = '''SELECT invoice_id, client_name, invoice_date, 
                       total_amount, tax_amount, payment_method, status 
                       FROM invoices'''
            params = []
            
            if filters:
                conditions = []
                if filters.get('client_name'):
                    conditions.append("client_name LIKE ?")
                    params.append(f"%{filters['client_name']}%")
                if filters.get('status'):
                    conditions.append("status = ?")
                    params.append(filters['status'])
                if filters.get('date_from'):
                    conditions.append("invoice_date >= ?")
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    conditions.append("invoice_date <= ?")
                    params.append(filters['date_to'])
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            query += f" ORDER BY {order_by}"
            c.execute(query, params)
            invoices = c.fetchall()
            return invoices
        finally:
            conn.close()

    @staticmethod
    def get_invoice_details(invoice_id):
        conn = sqlite3.connect(app_config["invoices_db"])
        try:
            c = conn.cursor()
            c.execute('''SELECT * FROM invoices WHERE invoice_id = ?''', (invoice_id,))
            details = c.fetchone()
            if not details:
                raise ValueError(f"Invoice with ID {invoice_id} not found")
            return details
        finally:
            conn.close()

    @staticmethod
    def update_invoice_status(invoice_id, status):
        conn = sqlite3.connect(app_config["invoices_db"])
        try:
            c = conn.cursor()
            c.execute('''UPDATE invoices 
                         SET status = ?, updated_at = ? 
                         WHERE invoice_id = ?''',
                      (status, datetime.now().isoformat(), invoice_id))
            if c.rowcount == 0:
                raise ValueError(f"Invoice with ID {invoice_id} not found")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete_invoice(invoice_id):
        conn = sqlite3.connect(app_config["invoices_db"])
        try:
            c = conn.cursor()
            c.execute('DELETE FROM invoices WHERE invoice_id = ?', (invoice_id,))
            if c.rowcount == 0:
                raise ValueError(f"Invoice with ID {invoice_id} not found")
            conn.commit()
        finally:
            conn.close()

# Initialize the invoice database
InvoiceDB.initialize()