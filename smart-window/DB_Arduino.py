import sqlite3
import os
import uuid


path_db = r'C:\Users\Emanuele\PycharmProjects\iot-clean-air\Smart-Window\db_UUID'


class Database:
    def getName(self):
        """ create a database connection to a SQLite database """
        # Exists => there is also the name
        if os.path.isfile(path_db):

            conn = None
            try:
                conn = sqlite3.connect(path_db)
                print(sqlite3.version)
            except sqlite3.Error as e:
                print(e)
            finally:
                if conn:
                    cur = conn.cursor()
                    uuid_Arduino = cur.execute(
                        'SELECT uuid FROM dataArduino').fetchone()[0]

                conn.close()

        else:
            conn = None
            try:
                conn = sqlite3.connect(path_db)
                print(sqlite3.version)
            except sqlite3.Error as e:
                print(e)
            finally:
                if conn:
                    cur = conn.cursor()
                    cur.execute('''CREATE TABLE dataArduino
                                   (uuid text)''')
                    uuid_Arduino = uuid.uuid1()
                    cur.execute(
                        "INSERT INTO dataArduino VALUES (?)", uuid_Arduino)
                    print("Valore immesso")
                    conn.commit()
                    conn.close()
        print("uuid_Arduino:", uuid_Arduino)
        return uuid_Arduino
