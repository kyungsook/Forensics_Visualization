from __future__ import print_function

import sys
import sqlite3
import struct
import ntpath
from enum import Enum

import fat32Test
import Registry
import DBManager
import Dir

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
        self.fatTreeStructure = Dir.Dir()
        self.imgFile.tree_structure(self.imgFile.root_cluster, self.fatTreeStructure)

    #create DB file from fat32 Disk Image file
    def extractDB(self, src, filename):
        '''
        extract DB file from Disk Image file
        :param src: data
        :param filename: name of newly created DB file
        :return: None
        '''

        self.dbFileName = filename
        DBfd = open(self.dbFileName, 'wb')
        DBfd.write(src)
        DBfd.close()

    def get_vbr_data_binary(self):
        return self.imgFile.read_sector(0, 32)

    def get_content(self, cluster):
        '''
        read all data from connected FAT
        :param cluster: start cluster
        :return: data
        '''
        return self.imgFile.get_content(cluster)

    def cluster_to_offset(self, cluster):
        offset = ((cluster-2) * self.imgFile.spc + self.imgFile.first_data_sector) * self.imgFile.bps
        return offset

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
            hexText += '%02X ' % byte

            if chars % self.rowLength == 0:  #길이 16마다 개행
                hexText += '\n'

            elif chars % self.rowSpacing == 0:  #길이 4마다 띄어쓰기 2번
                hexText += self.space

        return hexText

    def get_asciiText(self):
        asciiText = ''
        return asciiText


def print_dir_recursive(root):
    print(root.dir_list)

    for i in root.dir_obj_list:
        print_dir_recursive(i)


def print_file_recursive(root):
    print(root.file_list)

    for i in root.dir_obj_list:
        print_file_recursive(i)

def print_reg_recursive(root):
    try:
        for i in root.reg_obj_list:
            Registry.rec2(i.root())
    except AttributeError:
        pass

    for i in root.dir_obj_list:
        print_reg_recursive(i)

if __name__ == '__main__':
    app = RegistryImage(sys.argv[1])    #처음에 디스크 이미지 파일을 읽고 디렉토리 트리구조를 저장
    #print_dir_recursive(app.fatTreeStructure)
    print_file_recursive(app.fatTreeStructure)
    #buf = app.get_content(63142)
    #app.createDB(buf, 'a.db')
    #print_reg_recursive(app.fatTreeStructure)


