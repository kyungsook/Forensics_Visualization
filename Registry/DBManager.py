import sqlite3
import sys

class DBManager:

    def __init__(self, dbName): # DBManager 클래스 초기화
        self.dbName = dbName
        self.con = sqlite3.connect(self.dbName)
        self.cur = self.con.cursor()

    def checkTableList(self):   #db의 table 이름을 self.tableList에 리스트 형태로 저장
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        self.tableList = []

        for i in self.cur:
            self.tableList += i

        print(self.tableList)   #tableList 체크

    def checkTable(self, tableName):    #원하는 테이블이 db에 생성되어있는지 체크하는 함수
        if tableName in self.tableList:
            return True

        return False

    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS Hive(Key text, ValueType text, ValueName text, Value text, Timestamp text);")

    def drop_table(self):
        #self.cur = self.con.cursor()
        self.cur.execute("DROP TABLE Hive;")
        print("drop table")

    def insert_record(self, key, valType, valName, val, timestamp):
        self.cur = self.con.cursor()
        self.cur.execute("INSERT INTO Hive Values (?, ?, ?, ?, ?);", [key, valType, valName, val, timestamp])


    def connect_db(self, dbName, tableName):   #DB에 연결
        self.con = sqlite3.connect(dbName)

        if db.checkTable(tableName) == False:   #원하는 테이블이 db에 없으면 생성
            self.cur.execute("CREATE TABLE Hive(Key text);")
            #print("만들자~~~")

    def insert_db(self, val): #DB에 데이터 넣기
        self.cur.execute("INSERT INTO Hive Values (?);", [val])
        self.con.commit()


    def delete_db(self, val):
        print("삭제~~~~~")

    def close_db(self):
        self.con.commit()
        self.con.close()
        print("disconnected")

    def just_test(self):
        print("this is test method")

if __name__ == '__main__':
    print("DBManager")
    db = DBManager(sys.argv[1])

    db.checkTableList()
    db.disconnect_db()





