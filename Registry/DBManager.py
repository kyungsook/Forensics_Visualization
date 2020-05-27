import sqlite3
import sys
import datetime

class DBManager:

    def __init__(self, dbName):  # DBManager 클래스 초기화
        self.dbName = dbName
        self.con = sqlite3.connect(self.dbName)
        self.cur = self.con.cursor()

    def create_table(self, tableName):
        if tableName == 'Hive':
            self.cur.execute('CREATE TABLE IF NOT EXISTS %s '
                             '(FileName text, Type text, Key text, ValType text, ValName text, Val text, TimeStamp datetime)' %(tableName))
        elif tableName == 'GeneralFile':
            self.cur.execute('CREATE TABLE IF NOT EXISTS %s '
                            '(Name text, FileExt text, FileSig text, FileSize int, CreateTime datetime, WriteTime datetime, AccessTime datetime)' % (
                                tableName))
        print("create table")

    def drop_table(self, tableName):
        self.cur = self.con.cursor()
        self.cur.execute("DROP TABLE %s;" %(tableName))
        print("drop the table")

    def insert_record(self, tableName, filename = 0, type = 0, key = 0, valType = 0, valName = 0, val = 0, timeStamp = 0, name = 0, ext = 0, sig = 0, size = 0, create = 0, write = 0, access = 0):  # DB에 데이터 넣기
        self.cur = self.con.cursor()
        if tableName == 'Hive':
            self.cur.execute("INSERT INTO Hive Values (?, ?, ?, ?, ?, ?, ?);", [filename, type, key, valType, valName, val, timeStamp])
        elif tableName == 'GeneralFile':
            self.cur.execute("INSERT INTO GeneralFile VALUES (?, ?, ?, ?, ?, ?, ?)", [name, ext, sig, size, create, write, access])

    def select_record(self, tableName, date_from, date_to):
        self.cur = self.con.cursor()
        sql_select = ""
        if tableName == 'Hive':
            #print("hive")
            sql_select = "SELECT ValType, substr(Timestamp, 0, 11) AS WriteDate, COUNT(*) AS Num " \
                         "FROM Hive WHERE Timestamp BETWEEN '%s' AND '%s' GROUP BY ValType, substr(Timestamp, 0, 11) " \
                         "ORDER BY Timestamp" % (date_from, date_to)


        elif tableName == 'GeneralFile':
            #print("generalFile")
            date_from = date_from.replace('-', '/')
            date_to = date_to.replace('-', '/')
            sql_select = "SELECT FileSig, substr(WriteTime, 0, 11) AS WriteDate, COUNT(*) AS Num " \
                         "FROM GeneralFile Where WriteDate BETWEEN '%s' AND '%s' GROUP BY FileSig, WriteDate " \
                         "ORDER BY WriteDate" % (date_from, date_to)

        elif tableName == 'urls':
            #print("urls")
            sql_select = "SELECT date(datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')) AS lvt, COUNT(*) " \
                         "FROM urls WHERE lvt BETWEEN '%s' AND '%s' GROUP BY lvt;" %(date_from, date_to)

        self.cur.execute(sql_select)
        self.con.commit()
        total = self.cur.fetchall()
        result = {}

        if tableName == 'GeneralFile':
            for i in total:
                result[i[0].replace("/", "-")] = i[1]

        else:
            for i in total:
                result[i[0]] = i[1]


        print(result)
        return result

    def close_db(self):
        self.con.commit()
        self.con.close()
        print('disconnected')

    def just_test(self):
        print("this is test method")

if __name__ == '__main__':
    print("DBManager")
    db = DBManager('./test.db')
    str_from = '2020-03-01'
    str_to = '2020-05-01'
    db.select_record('GeneralFile', str_from, str_to)
    # db.drop_table('GeneralFile')
    db.close_db()
