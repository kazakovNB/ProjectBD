import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    user="postgres",
    password="admin123",
    dbname="veomodern",
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT role_id, role_name FROM roles ORDER BY role_id;")
rows = cur.fetchall()
print("BEFORE:", rows)

# предполагаем что роли идут 1..4 (как создавались)
updates = [
    (1, "Администратор"),
    (2, "Врач"),
    (3, "Разработчик"),
    (4, "Студент"),
]
for role_id, name in updates:
    cur.execute("UPDATE roles SET role_name=%s WHERE role_id=%s;", (name, role_id))

cur.execute("SELECT role_id, role_name FROM roles ORDER BY role_id;")
print("AFTER:", cur.fetchall())

cur.close()
conn.close()
print("OK")
