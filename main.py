import sqlite3
import datetime

class Store:
    def __init__(self):
        self.conn = sqlite3.connect('store.db')
        self.cursor = self.conn.cursor()
        
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT,
                price REAL
            );
        """)
    
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                order_date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """)
        self.conn.commit()
    
    def insert_simple_data(self):
        self.cursor.execute(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            ('iPhone 13', 'Смартфони', 799.99)
        )

        self.cursor.execute("SELECT * FROM customers WHERE email = ?", ("oleg@example.com",))
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)",
                ("Олег", "Петренко", "oleg@example.com")
            )

        self.cursor.execute(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
            (1, 1, 2, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        self.cursor.execute(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            ("Samsung Galaxy S21", "Смартфони", 699.99)
        )
        self.cursor.execute("SELECT * FROM customers WHERE email = ?", ("maria@example.com",))
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)",
                ("Марія", "Іванова", "maria@example.com")
            )

        self.cursor.execute(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
            (2, 2, 1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        self.conn.commit()

    def total_sales(self):
        result = self.cursor.execute("""
            SELECT SUM(p.price * o.quantity)
            FROM orders o
            JOIN products p ON o.product_id = p.product_id;
        """).fetchone()
        
        print(f"Загальний обсяг продажів: {result[0]} грн.")

    def most_popular_category(self):
        result = self.cursor.execute("""
            SELECT p.category, COUNT(*) AS count
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            GROUP BY p.category
            ORDER BY count DESC
            LIMIT 1;
        """).fetchone()
    
        if result:
            print(f"Найпопулярніша категорія: {result[0]}, кількість продажів: {result[1]}")
        else:
            print("Немає даних про продажі.")

    def insert_order(self, customer_id, product_id, quantity):
        order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
            (customer_id, product_id, quantity, order_date)
        )
        self.conn.commit()

    def orders_per_customer(self, customer_id):
        result = self.cursor.execute("""
            SELECT c.first_name || ' ' || c.last_name AS customer, COUNT(o.id) AS total_orders
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            WHERE c.id = ?
            GROUP BY c.id;
        """, (customer_id,)).fetchall()

        for row in result:
            print(f"Клієнт: {row[0]}, Загальна кількість замовлень: {row[1]}")
    
    def average_order_value(self):
        result = self.cursor.execute("""
            SELECT AVG(p.price * o.quantity)
            FROM orders o
            JOIN products p ON o.product_id = p.product_id;
        """).fetchone()
        print(f"Середній чек замовлення: {result[0]:.2f} грн.")
    
    def products_per_category(self):
        result = self.cursor.execute("""
            SELECT category, COUNT(*) AS count
            FROM products
            GROUP BY category;
        """).fetchall()
        
        for category, count in result:
            print(f"Категорія: {category}, Кількість продуктів: {count}")
    
    def update_smartphone_price(self, product_id=None, new_price=None):
        if product_id and new_price:
            self.cursor.execute(
                "UPDATE products SET price = ? WHERE product_id = ? AND category = 'Смартфони';",
                (new_price, product_id)
            )
        else:
            self.cursor.execute(
                "UPDATE products SET price = price * 1.10 WHERE category = 'Смартфони';"
            )
        self.conn.commit()
        print("Ціна оновлена.")

    def run_cli(self):
        while True:
            print("\nМеню:")
            print("1. Додати товар")
            print("2. Додати клієнта")
            print("3. Створити замовлення")
            print("4. Сумарний обсяг продажів")
            print("5. Кількість замовлень на клієнта")
            print("6. Cередній чек замовлення")
            print("7. Найпопулярніша категорія")
            print("8. Кількість товарів по категоріях")
            print("9. Збільшити ціни на смартфони на 10%")
            print("10. Зберегти зміни в базі")
            print("0. Вихід")
            
            choice = input("Виберіть опцію: ")
            
            if choice == '1':
                name = input("Введіть назву товару: ")
                category = input("Введіть категорію товару (Смартфони/Ноутбуки/Планшети): ")
                price = float(input("Введіть ціну товару: "))
                self.cursor.execute(
                    "INSERT INTO products (name, category, price) VALUES (?, ?, ?);",
                    (name, category, price)
                )
                print("Товар додано.")
            elif choice == '2':
                first_name = input("Введіть ім'я клієнта: ")
                last_name = input("Введіть прізвище клієнта: ")
                email = input("Введіть email клієнта: ")
                self.cursor.execute(
                    "INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?);",
                    (first_name, last_name, email)
                )
                print("Клієнт додано.")
            elif choice == '3':
                customer_id = int(input("Введіть ID клієнта: "))
                product_id = int(input("Введіть ID товару: "))
                quantity = int(input("Введіть кількість товару: "))
                self.insert_order(customer_id, product_id, quantity)
                print("Замовлення створено.")
            elif choice == '4':
                self.total_sales()
            elif choice == '5':
                customer_id = int(input("Введіть ID клієнта: "))
                self.orders_per_customer(customer_id)
            elif choice == '6':
                self.average_order_value()
            elif choice == '7':
                self.most_popular_category()
            elif choice == '8':
                self.products_per_category()
            elif choice == '9':
                self.update_smartphone_price()
            elif choice == '10':
                self.conn.commit()
                print("Зміни збережено в базі даних.")
            elif choice == '0':
                print("Вихід з програми.")
                break
            else:
                print("Невірний вибір. Спробуйте ще раз.")

if __name__ == "__main__":
    store = Store()
    store.create_table()
    store.insert_simple_data()
    store.run_cli()
