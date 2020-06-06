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

        self.bps = self.imgFile.bps
        self.spc = self.imgFile.spc
        self.reserved_sectors = self.imgFile.reserved_sectors
        self.number_of_fats = self.imgFile.number_of_fats
        self.sectors = self.imgFile.sectors
        self.fat_size = self.imgFile.fat_size
        self.root_cluster = self.imgFile.root_cluster
        self.fds = self.imgFile.first_data_sector

        #create Dir class to make tree structure of fat32 disk image file
        self.fatTreeStructure = Dir()
        self.imgFile.tree_structure(self.imgFile.root_cluster, self.fatTreeStructure)

    #create DB file from fat32 Disk Image file
    def createDB(self, src, filename):
        '''
        :param src: data
        :param filename: name of newly created DB file
        :return:
        '''

        self.dbFileName = filename
        DBfd = open(self.dbFileName, 'wb')
        DBfd.write(src)
        DBfd.close()

    def get_content(self, cluster): #연결된 fat를 찾아서 data 다 읽어온다
        return self.imgFile.get_content(cluster)

    def get_files(self, cluster):
        self.imgFile.get_files(cluster)

    def cluster_to_offset(self, cluster):
        offset = ((cluster-2) * self.imgFile.spc + self.imgFile.first_data_sector) * self.imgFile.bps
        return offset

    def read_register(self, cluster, size):
        offset = self.cluster_to_offset(cluster)
        self.temp = Registry.Registry(self.imgFile, offset, size)
        Registry.rec2(self.temp.root())

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

class Dir:
    def __init__(self, entry=None):
        self.current_dir = entry
        self.file_list = []
        self.sub_dir_list = []
        self.dir_list = []
        self.reg_list = []

    def get_current(self, entry):
        self.current_dir = entry

    def get_parent(self, entry):
        self.parent_dir = entry

    def get_dir_list(self, entry):
        if entry['real_ext'] == 'Directory':
            self.dir_list.append(entry)

        elif entry['real_ext'] == 'registry hive file':
            self.reg_list.append(entry)
            self.file_list.append(entry)

        else:
            self.file_list.append(entry)

    def sub_dir(self, object):
        self.sub_dir_list.append(object)

def print_recursive(root):
    print(root.file_list)

    for i in root.sub_dir_list:
        print_recursive(i)

if __name__ == '__main__':
    app = RegistryImage(sys.argv[1])
    #print_recursive(app.fatTreeStructure)
    #buf = app.get_content(63142)
    #app.createDB(buf, 'a.db')


