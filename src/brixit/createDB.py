import sqlite3
from sqlite3 import Error
import commonUtils as cu


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
        x = int(input("Enter a number:\r\n0: Exit\r\n1: Create part DB\r\n2: Create log DB\r\n3: Create user DB\r\n"))

        if x == 0:
            break

        if x == 1:
            create_BriXit_db(cu.settings.DB_Parts, "partsSchema.sql")
        if x == 2:
            create_BriXit_db(cu.settings.DB_LabelLog, "logSchema.sql")
        if x == 3:
            create_BriXit_db(cu.settings.DB_User, "userSchema.sql")
