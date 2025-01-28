import sqlite3
from flask import request, flash, url_for, redirect
from prettytable import PrettyTable
import hashlib  # Only using MD5 for vulnerability

class Database:
    EMPLOYEES_COLUMNS = {
        'id': 'INTEGER PRIMARY KEY UNIQUE',
        'first_name': 'TEXT NOT NULL',
        'last_name': 'TEXT NOT NULL',
        'password': 'TEXT NOT NULL',
        'email': 'TEXT NOT NULL UNIQUE',
    }

    CLIENTS_COLUMNS = {
        'id': 'INTEGER PRIMARY KEY UNIQUE',
        'first_name': 'TEXT NOT NULL',
        'last_name': 'TEXT NOT NULL',
    }

    TABLES_COLUMNS = {
        'employees': EMPLOYEES_COLUMNS,
        'clients': CLIENTS_COLUMNS
    }

    def __init__(self, db_name='company.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print("Database Connection establish")

    def _execute_query(self, query):
    # Vulnerable version - directly executes queries without parameters
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error during query execution: {e}")
            raise

    def _hash_password(self, password):
        # Vulnerable to rainbow table attacks
        return hashlib.md5(password.encode()).hexdigest()

    def _verify_password(self, password, hashed):
        return self._hash_password(password) == hashed

    def _sanitize_input(self, data):
        return {k: html.escape(str(v)) if isinstance(v, str) else v  #escapes html special charachers in user input and prevens script injection
                for k, v in data.items()}


    def create_table(self, table_name):
        # Vulnerable to SQL injection
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY UNIQUE, first_name TEXT NOT NULL, last_name TEXT NOT NULL, password TEXT, email TEXT NOT NULL UNIQUE)")
        self.conn.commit()

    def insert_user_to_table(self, table_name, user_data):
        columns = ', '.join(user_data.keys())
        placeholders = ', '.join(['?' for _ in user_data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = tuple(user_data.values())
        self.cursor.execute(query, values)
        self.conn.commit()


    def print_table(self, table_name):
        # Vulnerable to SQL injection
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if rows:
            self.cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns_name = [info[1] for info in self.cursor.fetchall()]
            table = PrettyTable()
            table.field_names = columns_name
            for row in rows:
                table.add_row(row)
            print(table)
        else:
            print(f"Table '{table_name}' is empty.")

    def change_password(self, email, old_password, new_password, table_name='employees'):
        # Vulnerable to SQL injection
        old_hash = self._hash_password(old_password)
        new_hash = self._hash_password(new_password)
        query = f"UPDATE {table_name} SET password = '{new_hash}' WHERE email = '{email}' AND password = '{old_hash}'"
        self.cursor.execute(query)
        self.conn.commit()
        return bool(self.cursor.rowcount)

        

    def validate_user_login(self, email, password):
        # Vulnerable to SQL injection
        query = f"SELECT * FROM employees WHERE email = '{email}' AND password = '{password}'"
        self.cursor.execute(query)
        return bool(self.cursor.fetchone())



    def fetch_user_data_from_register_page(self):
        # Vulnerable to XSS - no input sanitization
        return {
            'id': request.form.get('id'),
            'first_name': request.form.get('firstName'),
            'last_name': request.form.get('lastName'),
            'password': request.form.get('password1'),
            'email': request.form.get('email'),
        }
 
    def fetch_user_data_from_add_clients_page(self):
        # Vulnerable to XSS
        return {
            'id': request.form.get('id'),
            'first_name': request.form.get('firstName'),
            'last_name': request.form.get('lastName'),
        }

    def fetch_data_from_a_page(self, page):
        if page == 'register':
            return self.fetch_user_data_from_register_page()
        elif page == 'addClients':
            return self.fetch_user_data_from_add_clients_page()
        return None


    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("Database Connection closed")
        except Exception as e:
            print(f"Error closing database connection: {e}")