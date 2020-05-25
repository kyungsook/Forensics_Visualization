<<<<<<< HEAD
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
            sql_select = "SELECT substr(Timestamp, 0, 11) AS WriteDate, COUNT(*) AS Num " \
                         "FROM Hive WHERE Timestamp BETWEEN '%s' AND '%s' " \
                         "GROUP BY substr(Timestamp, 0, 11) ORDER BY Timestamp;" %(date_from, date_to)


        elif tableName == 'GeneralFile':
            #print("generalFile")
            sql_select = "SELECT substr(WriteTime, 0, 11) AS WriteDate, COUNT(*) FROM GeneralFile " \
                         "WHERE WriteDate BETWEEN '%s' AND '%s' GROUP BY WriteDate;" %(date_from, date_to)

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
    db.select_record('Hive', str_from, str_to)
    # db.drop_table('GeneralFile')
    db.close_db()
=======
import sqlite3
import datetime


class DBManager:

    def __init__(self, dbName):  # DBManager 클래스 초기화
        self.dbName = dbName
        self.con = sqlite3.connect(self.dbName)
        self.cur = self.con.cursor()

    def create_table(self, tableName):
        if tableName == 'Hive':
            self.cur.execute('CREATE TABLE IF NOT EXISTS %s '
                             '(FileName text, Type text, Key text, ValType text, ValName text, Val text, TimeStamp text)' %(tableName))
        elif tableName == 'GeneralFile':
            self.cur.execute('CREATE TABLE IF NOT EXISTS %s '
                            '(Name text, FileExt text, FileSig text, FileSize int, CreateTime datetime, WriteTime datetime, AccessTime datetime)' % (
                                tableName))
        print("create table")

    def drop_table(self, tableName):
        self.cur = self.con.cursor()
        self.cur.execute("DROP TABLE %s;" %(tableName))
        print("drop table")

    def insert_record(self, tableName, filename = 0, type = 0, key = 0, valType = 0, valName = 0, val = 0, timeStamp = "", name = 0, ext = 0, sig = 0, size = 0, create = 0, write = 0, access = 0):  # DB에 데이터 넣기
        self.cur = self.con.cursor()
        if tableName == 'Hive':
            self.cur.execute("INSERT INTO Hive Values (?, ?, ?, ?, ?, ?, ?);", [filename, type, key, valType, valName, val, timeStamp])
        elif tableName == 'GeneralFile':
            self.cur.execute("INSERT INTO GeneralFile VALUES (?, ?, ?, ?, ?, ?, ?)", [name, ext, sig, size, create, write, access])

    def select_record(self, tableName, date_from, date_to):
        self.cur = self.con.cursor()
        result = ""
        if tableName == 'Hive':
            print("select hive")
            self.cur.execute("SELECT * FROM Hive WHERE Timestamp BETWEEN '%s' AND '%s'" % (date_from, date_to))

        elif tableName == 'GeneralFile':
            print("select generalFile")
            self.cur.execute("SELECT * FROM GeneralFile WHERE WriteTime BETWEEN '%s' AND '%s';" % (date_from, date_to))

        elif tableName == 'urls':
            print("select urls")

        self.con.commit()
        result = self.cur.fetchall()
        print(type(result), result)
        return result

    def order_by_date(self, tableName, date_from, date_to):
        self.cur = self.con.cursor()

        if tableName == 'Hive':
            print("hive - order by date")
            self.cur.execute("SELECT substr(Timestamp, 0, 11) AS WriteDate, COUNT(*) AS Num "
                             "FROM Hive WHERE Timestamp BETWEEN '%s' AND '%s' "
                             "GROUP BY substr(Timestamp, 0, 11) ORDER BY Timestamp" % (date_from, date_to))

        elif tableName == 'GeneralFile':
            print("general - order by date")
            date_from = date_from.replace('-','/')
            date_to = date_to.replace('-','/')
            # print(date_from, date_to)
            self.cur.execute("SELECT substr(WriteTime, 0, 11) AS WriteDate, COUNT(*) AS Num "
                             "FROM GeneralFile Where WriteDate BETWEEN '%s' AND '%s' "
                             "GROUP BY substr(WriteTime, 0, 11) ORDER BY WriteDate" % (date_from, date_to))

        elif tableName == 'urls':
            print("urls - order by date")
            self.cur.execute("SELECT date(datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')) AS lvt,"
                             " COUNT(*) FROM urls WHERE lvt BETWEEN '%s' AND '%s' GROUP BY lvt;" % (date_from, date_to))

        self.con.commit()
        temp = self.cur.fetchall()
        result = {}
        for i in temp:
            result[i[0].replace('/','-')] = i[1]
        print(result)
        return result

    def close_db(self):
        self.con.commit()
        self.con.close()

    def just_test(self):
        print("this is test method")

if __name__ == '__main__':
    print("DBManager")
    # db = DBManager('./test.db', 'GeneralFile')
    db = DBManager('./test.db')
    str_from = '2020/03/01'
    str_to = '2020/03/31'
    # print(datetime.datetime.strptime(str_from, '%Y/%m/%d'))
    # print(type(datetime.datetime.strptime(str_from, '%Y/%m/%d')))
    db.order_by_date('GeneralFile', str_from, str_to)
    # db.select_record(str_from, str_to)
    # db.drop_table('GeneralFile')
    # db.order_by_date('Hive', str_from, str_to)
    # db.drop_table('Hive')
    db.close_db()
>>>>>>> eed90133fe4c157786bc421c50f50b8e233a4487
