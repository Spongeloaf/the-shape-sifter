import commonUtils as cu
import random
import string
import Constants as k
import sqlite3
from sqlite3 import Error


def GenerateSerial():
    """ Creates a serial key for a new user and inserts it into the database """
    key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(k.kSerialLength))
    sql = sqlite3.connect(cu.settings.DB_User)
    if sql.execute('SELECT serialKey FROM keys WHERE serialKey = ?', [key]).fetchone() is not None:
        print("Error: Serial key in use!")
        return

    sql.execute('INSERT INTO keys (serialKey) VALUES (?)', [key])
    sql.commit()
    print("Here is your new serial key:")
    print(key)


def create_BriXit_db(db_file, schema):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Sqlite version: " + sqlite3.version)
        print("Filename: " + db_file)

        f = open(schema)
        conn.executescript(f.read())

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    while True:
        x = int(input("Enter a number:\r\n0: New serial key\r\n1: Create part DB\r\n2: Create log DB\r\n3: Create user DB\r\n4: Exit\r\n"))

        if x == 4:
            break

        if x == 0:
            GenerateSerial()
        if x == 1:
            create_BriXit_db(cu.settings.DB_Parts, "partsSchema.sql")
        if x == 2:
            create_BriXit_db(cu.settings.DB_LabelLog, "logSchema.sql")
        if x == 3:
            create_BriXit_db(cu.settings.DB_User, "userSchema.sql")
