import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="12345678",
    database="testdatabase"
)

cursor = db.cursor()

# cursor.execute("DROP TABLE Person")

# cursor.execute("CREATE TABLE Person (name VARCHAR(20), age smallint, personID int PRIMARY KEY AUTO_INCREMENT)")
# cursor.execute("DESCRIBE Person")

# cursor.execute("INSERT INTO Person (name, age) VALUES (%s, %s)",
#                ("Kyrylo", 17)
#                )
# db.commit()

cursor.execute("SELECT * FROM Person")

for user in cursor.fetchall():
    print(user)
