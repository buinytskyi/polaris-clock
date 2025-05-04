import sqlite3
import os

class Config:
    def __init__(self, db_name):
        db_name = os.path.join(os.path.dirname(__file__), db_name)
        self.db_name = db_name
        self.__private_create_table()

    def __private_create_table(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS geo_day
                          (id INTEGER PRIMARY KEY, tz TEXT, lon TEXT, lat TEXT)''')
        conn.commit()
        conn.close()

    def check(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM geo_day")
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == 0:
            return True
        else:
            return False

    def save(self, tz, lon, lat):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO geo_day (id, tz, lon, lat)
                          VALUES (1, ?, ?, ?)''', (tz, lon, lat))
        conn.commit()
        conn.close()

    def get(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT tz, lon, lat FROM geo_day")
        result = cursor.fetchall()
        conn.close()
        if result:
            self.tz, self.lon, self.lat = result[0]
        return result
