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
                             '(Type text, Key text, ValType text, ValName text, Val text, TimeStamp text)' %(tableName))
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
            self.cur.execute("INSERT INTO Hive Values (?, ?, ?, ?, ?, ?);", [type, key, valType, valName, val, timeStamp])
        elif tableName == 'GeneralFile':
            self.cur.execute("INSERT INTO GeneralFile VALUES (?, ?, ?, ?, ?, ?, ?)", [name, ext, sig, size, create, write, access])

    def select_all(self, tableName, date_from, date_to):
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
            regbinRes = {}
            regdwordRes = {}
            regexpandszRes = {}
            regmultiszRes = {}
            regqwordRes = {}
            regszRes = {}

            self.cur.execute("SELECT ValType, substr(Timestamp, 0, 11) AS WriteDate, COUNT(*) AS Num "
                             "FROM Hive WHERE Timestamp BETWEEN '%s' AND '%s' "
                             "GROUP BY ValType, substr(Timestamp, 0, 11) ORDER BY Timestamp" % (date_from, date_to))
            self.con.commit()
            temp = self.cur.fetchall()

            for i in temp:
                if i[0] == "RegBin":
                    regbinRes[i[1]] = i[2]
                elif i[0] == "RegDWord":
                    regdwordRes[i[1]] = i[2]
                elif i[0] == "RegExpandSZ":
                    regexpandszRes[i[1]] = i[2]
                elif i[0] == "RegMultiSZ":
                    regmultiszRes[i[1]] = i[2]
                elif i[0] == "RegQWord":
                    regqwordRes[i[1]] = i[2]
                elif i[0] == "RegSZ":
                    regszRes[i[1]] = i[2]

            return regbinRes, regdwordRes, regexpandszRes, regmultiszRes, regqwordRes, regszRes

        elif tableName == 'GeneralFile':
            print("general - order by date")
            delRes = {}
            hwpRes = {}
            pdfRes = {}
            jpegRes = {}
            pngRes = {}
            pptxRes = {}

            self.cur.execute("SELECT FileSig, substr(WriteTime, 0, 11) AS WriteDate, COUNT(*) AS Num "
                             "FROM GeneralFile WHERE WriteDate BETWEEN '%s' AND '%s' "
                             "GROUP BY FileSig, substr(WriteTime, 0, 11) ORDER BY WriteDate" % (date_from, date_to))
            # self.cur.execute("SELECT FileSig, WriteTime, COUNT(*) AS Num "
            #                  "FROM GeneralFile Where substr(WriteTime, 0, 11) BETWEEN '%s' AND '%s' "
            #                  "GROUP BY FileSig, substr(WriteTime, 0, 11) ORDER BY WriteTime" % (date_from, date_to))
            self.con.commit()
            temp = self.cur.fetchall()

            for i in temp:
                if i[0] == "Deleted File":
                    delRes[i[1]] = i[2]
                elif i[0] == "HWP":
                    hwpRes[i[1]] = i[2]
                elif i[0] == "JPG":
                    jpegRes[i[1]] = i[2]
                elif i[0] == "PDF":
                    pdfRes[i[1]] = i[2]
                elif i[0] == "PNG":
                    pngRes[i[1]] = i[2]
                elif i[0] == "PPTX":
                    pptxRes[i[1]] = i[2]

            return delRes, hwpRes, jpegRes, pdfRes, pngRes, pptxRes

        elif tableName == 'urls':
            print("urls - order by date")
            chromeRes = {}
            whaleRes = {}

            self.cur.execute("SELECT date(datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')) AS lvt,"
                             " COUNT(*) FROM urls_chrome WHERE lvt BETWEEN '%s' AND '%s' GROUP BY lvt;" % (date_from, date_to))
            self.con.commit()
            tot_chrome = self.cur.fetchall()

            for i in tot_chrome:
                chromeRes[i[0]] = i[1]

            self.cur.execute(
                "SELECT date(datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')) AS lvt,"
                " COUNT(*) FROM urls_whale WHERE lvt BETWEEN '%s' AND '%s' GROUP BY lvt;" % (date_from, date_to))
            self.con.commit()
            tot_whale = self.cur.fetchall()

            for i in tot_whale:
                whaleRes[i[0]] = i[1]

            return chromeRes, whaleRes

    def select_history(self, tableName, date_from, date_to):
        self.cur = self.con.cursor()

        if tableName == 'Hive':
            self.cur.execute("SELECT * FROM Hive WHERE substr(TimeStamp, 0, 11) BETWEEN '%s' AND '%s' "
                             "ORDER BY TimeStamp" % (date_from, date_to))
            self.con.commit()
            hive_history = self.cur.fetchall()

            return hive_history

        elif tableName == 'GeneralFile':
            self.cur.execute("SELECT * FROM GeneralFile WHERE substr(WriteTime, 0, 11) BETWEEN '%s' AND '%s' "
                             "ORDER BY WriteTime" % (date_from, date_to))
            self.con.commit()
            general_history = self.cur.fetchall()

            return general_history

        elif tableName == 'urls':
            self.cur.execute("SELECT url, title,"
                             "date(datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')) AS lvt "
                             "FROM urls_chrome WHERE lvt BETWEEN '%s' AND '%s' GROUP BY lvt ORDER BY lvt;"
                             % (date_from, date_to))
            self.con.commit()
            chrome_history = self.cur.fetchall()

            self.cur.execute("SELECT url, title,"
                             "date(datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')) AS lvt "
                             "FROM urls_whale WHERE lvt BETWEEN '%s' AND '%s' GROUP BY lvt ORDER BY lvt;"
                             % (date_from, date_to))
            self.con.commit()
            whale_history = self.cur.fetchall()

            return chrome_history, whale_history

    def close_db(self):
        self.con.commit()
        self.con.close()
        print("close db")

    def just_test(self):
        print("this is test method")

if __name__ == '__main__':
    print("DBManager")
    db = DBManager('./test.db')
    str_from = '2020-03-01'
    str_to = '2020-03-31'

    # db.order_by_date('GeneralFile', str_from, str_to)
    # db.select_all(str_from, str_to)
    db.select_history('Hive', str_from, str_to)

    # db.drop_table('GeneralFile')
    db.close_db()