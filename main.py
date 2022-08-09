import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                DROP TABLE phone;
                DROP TABLE client;
                """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40),
                    last_name VARCHAR(40),
                    email VARCHAR(80) UNIQUE
                );
                """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS phone(
                    number VARCHAR(20) PRIMARY KEY,
                    client_id INTEGER NOT NULL REFERENCES client(id)
                );
                """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO client(first_name, last_name, email) VALUES(%s, %s, %s) RETURNING id;
            """, (first_name, last_name, email))
        id = cur.fetchone()[0]
        if phone:
            cur.execute("""
                INSERT INTO phone(number, client_id) VALUES(%s, %s);
                """, (phone, id))
            conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phone(number, client_id) VALUES(%s, %s);
            """, (phone, client_id))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    if first_name:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE client SET first_name=%s WHERE id=%s;
                """, (first_name, client_id))
            conn.commit()
    if last_name:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE client SET last_name=%s WHERE id=%s;
                """, (last_name, client_id))
            conn.commit()
    if email:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE client SET email=%s WHERE id=%s;
                """, (email, client_id))
            conn.commit()
    if phone:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM phone WHERE client_id=%s;
                """, (client_id,))
            cur.execute("""
                INSERT INTO phone(number, client_id) VALUES(%s, %s);
                """, (phone, client_id))
            conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone WHERE client_id=%s AND number=%s;
            """, (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone WHERE client_id=%s;
            """, (client_id,))
        cur.execute("""
                    DELETE FROM client WHERE id=%s;
                    """, (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    if first_name:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM client WHERE first_name=%s;
                """, (first_name,))
            print(f'first_name={first_name}; clients: {cur.fetchall()}')
    if last_name:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM client WHERE last_name=%s;
                """, (last_name,))
            print(f'last_name={last_name}; clients: {cur.fetchall()}')
    if email:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM client WHERE email=%s;
                """, (email,))
            print(f'email={email}; clients: {cur.fetchall()}')
    if phone:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM client LEFT JOIN phone ON id = client_id WHERE number=%s;
                """, (phone,))
            print(f'phone={phone}; clients: {cur.fetchall()}')


with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
    create_db(conn)
    add_client(conn, 'Иван', 'Иванов', 'ivanov_ii@mail.ru', '+79876543210')
    add_client(conn, 'Петр', 'Петров', 'petrov_pp@mail.ru')
    add_client(conn, 'Роман', 'Романов', 'romanov_rr@mail.ru', '+79076543210')
    add_phone(conn, 1, '+79876543211')
    add_phone(conn, 2, '+79876543212')
    add_phone(conn, 3, '+79076543213')
    change_client(conn, 1, first_name='Джон')
    change_client(conn, 2, last_name='Петрофф')
    change_client(conn, 1, email='ivanoff@mail.ru')
    change_client(conn, 3, phone='+79076543000')
    delete_phone(conn, 1, '+79876543211')
    delete_client(conn, 3)
    find_client(conn, first_name='Петр')
    find_client(conn, last_name='Петрофф')
    find_client(conn, email='petrov_pp@mail.ru')
    find_client(conn, phone='+79876543212')

conn.close()