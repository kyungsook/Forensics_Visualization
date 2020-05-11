import sqlite3


class DBManager:

    def __init__(self, dbName):  # DBManager 클래스 초기화
        self.dbName = dbName
        self.con = sqlite3.connect(self.dbName)
        self.cur = self.con.cursor()
        self.create_table()
        key = '1'
        valType = '11'
        valName = '111'
        val = '11111'
        self.cur.execute("INSERT INTO Hive Values (?, ?, ?, ?);", [key, valType, valName, val])

    def create_table(self):
        # self.cur.execute("CREATE TABLE IF NOT EXISTS Hive(Key text, ValueType text, ValueName text, Value text, Timestamp text);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS Hive(Key text, ValueType text, ValueName text, Value text);")


    def drop_table(self):
        self.cur = self.con.cursor()
        self.cur.execute("DROP TABLE Hive;")
        print("drop table")

    def insert_record(self, key, valType, valName, val):  # DB에 데이터 넣기
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO Hive Values (?, ?, ?, ?);", [key, valType, valName, val])

    def close_db(self):
        self.con.commit()
        self.con.close()

    def just_test(self):
        print("this is test method")

if __name__ == '__main__':
    print("DBManager")
    db = DBManager('./test.db')
    # db.drop_table()
    db.close_db()
