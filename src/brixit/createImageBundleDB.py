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
    create_BriXit_db(cu.settings.DB_Parts, "partsSchema.sql")
