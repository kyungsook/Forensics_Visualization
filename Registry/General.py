from __future__ import print_function

import sys
import sqlite3
import struct
import ntpath
from enum import Enum

import fat32Test
import Registry
import DBManager

class RegistryImage:
    def __init__(self, filename):
        self.filename = filename
        self.imgFile = fat32Test.FAT32(self.filename) #이미지 파일을 rb로 열어서 vbr영역만큼 읽는다

        self.byteWidth = 2  # How many bits to include in a byte.
        self.space = ' '
        self.rowSpacing = 4  # How many bytes before a double space.
        self.rowLength = 16  # 헥사 창에 얼마나 많은 byte 가 들어갈 것인지
        self.fds = self.imgFile.first_data_sector
        self.dirList = []
        self.fileList = []
        self.regList = []

    def createDB(self):
        print()

    def readFile(self, offset, count=1):    #파일을 offset에서부터 count까지 읽기
        self.imgFile.read_sector(offset, count)
        print()

    def get_content(self, cluster): #연결된 fat를 찾아서 data 다 읽어온다
        return self.imgFile.get_content(cluster)

    def get_files(self, cluster):
        self.imgFile.get_files(cluster)

    def get_dirList(self):  #dir list 반환
        self.dirList = self.imgFile.dir_list
        return self.dirList

    def get_fileList(self): #file list 반환
        self.fileList = self.imgFile.file_list
        return self.fileList

    def get_regList(self):
        self.regList = self.imgFile.reg_list
        return self.regList

    def cluster_to_offset(self, cluster):
        offset = ((cluster-2) * self.imgFile.spc + self.imgFile.first_data_sector) * self.imgFile.bps
        return offset

    def read_register(self, cluster, size):
        offset = self.cluster_to_offset(cluster)
        self.temp = Registry.Registry(self.imgFile, offset, size)
        print(offset)
        Registry.rec2(self.temp.root())
        #myDB = DBManager.DBManager('test.db')
        #myDB.drop_table()
        #myDB.create_table('Hive')
        #Registry.write_db(self.temp.root(), myDB)
        #Registry.rec2(self.temp.root(), 0)
        #myDB.close_db()

    def get_offsetText(self, data, cluster):   #offset 반환
        offsetText = '' #return할 offsetText

        if cluster == 0:    #시작 cluster가 0이면
            offset = 0      #offset 0부터 시작

        else:   #그렇지 않으면
            offset = ((cluster - 2) * self.imgFile.spc + self.imgFile.first_data_sector) * 512  #시작 offset 구하기

        for chars in range(1, len(data) + 1):   #data길이만큼
            if chars % self.rowLength == 0 and chars != 0:  #16마다
                offsetText += format(offset, '08x') + '\n'  #offset을 길이 8인 hex값으로 바꾸어서 text 형태로 offsetText에 저장
                offset += 16    #offset 16더함

        return offsetText

    def get_hexText(self, data):      #hex값 반환
        hexText = ''

        for chars in range(1, len(data)+1):
            byte = data[chars-1]

            # main text 가 중앙에 있는것
            hexText += (format(byte, '02X') + self.space)

            if chars % self.rowLength == 0 and chars != 0:  #길이 16마다 개행
                hexText += '\n'

            elif chars % self.rowSpacing == 0:  #길이 4마다 띄어쓰기 2번
                hexText += self.space

        return hexText

    def get_asciiText(self):
        asciiText = ''
        return asciiText

if __name__ == '__main__':
    app = RegistryImage(sys.argv[1])
    #print(app.spc)
    #app.get_regList()
    app.read_register(60778, 4571136)
    #app.rec2()
    #print(app.get_offsetText(app.get_content(60778), 60778), end='')
    #print(app.get_hexText(app.get_content(60778)))
    #print(app.fds)
    #print(app.regList)
