import sys
import struct


class FAT32:
    END_CLUSTER = 0x0fffffff
    dir_list=[]
    file_list=[]
    reg_list=[]

    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, "rb")
        self.read_vbr()

    def read_vbr(self): # vbr 1섹터 읽기
        self.fd.seek(0)
        vbr = self.fd.read(512)
        self.bps = struct.unpack_from("<H", vbr, 11)[0] #byte per sector
        self.spc = struct.unpack_from("<B", vbr, 13)[0] #sector per cluster
        self.reserved_sectors = struct.unpack_from("<H", vbr, 14)[0]
        self.number_of_fats = struct.unpack_from("<B", vbr, 16)[0]
        self.sectors = struct.unpack_from("<I", vbr, 32)[0]
        self.fat_size = struct.unpack_from("<I", vbr, 36)[0]
        self.root_cluster = struct.unpack_from("<I", vbr, 44)[0]
        self.first_data_sector = self.fat_size * self.number_of_fats + self.reserved_sectors

    def read_byte(self, offset, count=1):
        self.fd.seek(offset)
        return self.fd.read(count)

    def read_sector(self, offset, count=1):
        self.fd.seek(offset * self.bps)
        return self.fd.read(self.bps * count)

    def read_cluster(self, cluster, count=1):
        if cluster < 2:
            raise Exception("Can't read under cluster 2")

        real_cluster = cluster - 2
        return self.read_sector(self.first_data_sector + real_cluster * self.spc, count * self.spc)

    def seek(self, offset, whence=0):
        self.fd.seek(offset, whence)

    def read_clusters(self, fats):
        data = bytes(0)
        for i in fats:
            data += self.read_cluster(i)

        return data

    def to_decode(self, data, encoding):
        if len(data) == 0:
            return ""

        return data.decode(encoding)

    def to_utf_16_le(self, data):
        return self.to_decode(data, 'utf-16-le')

    def to_euc_kr(self, data):
        return self.to_decode(data, 'euc-kr')

    def filter_unused_lfn(self, data):
        length = len(data)
        for i in range(len(data), 0, -2):
            if data[i - 2:i] == b'\xff\xff' or data[i - 2:i] == b'\x00\x00':
                length = i - 2
            else:
                break

        return data[:length]

    def parse_dir_entry_lfn(self, data, lfn):
        order = data[0]
        name1 = self.to_utf_16_le(self.filter_unused_lfn(data[1:11]))
        name2 = self.to_utf_16_le(self.filter_unused_lfn(data[14:26]))
        name3 = self.to_utf_16_le(self.filter_unused_lfn(data[28:32]))

        return {'name': name1 + name2 + name3 + lfn}

    def parse_dir_entry(self, data, lfn):
        attr = data[11]
        is_LFN = attr & 0x0F is 0x0F

        if data[0]==0xE5 :
            name='!'
            name=name+self.to_euc_kr(data[2:7]).rstrip()

        else :
            name = self.to_euc_kr(data[0:8]).rstrip()

        ext = self.to_euc_kr(data[8:11]).rstrip()

        if len(ext) > 0:
            name = name + "." + ext

        create_time = struct.unpack_from("<H", data, 14)[0]
        create_date = struct.unpack_from("<H", data, 16)[0]
        lad = struct.unpack_from("<H", data, 18)[0] #last access date
        highcluster = struct.unpack_from("<H", data, 20)[0]
        write_time = struct.unpack_from("<H", data, 22)[0]
        write_date = struct.unpack_from("<H", data, 24)[0]
        lowcluster = struct.unpack_from("<H", data, 26)[0]
        cluster = highcluster << 16 | lowcluster
        size = struct.unpack_from("<I", data, 28)[0]

        db_ext_byte = self.get_real_ext(cluster)
        real_ext_byte = db_ext_byte[0:8]
        real_ext_high = real_ext_byte[0:4]
        real_ext=''

        if real_ext_high == b'PK\x03\x04':
            real_ext = 'ZIP/PPTX/XLSX/DOCX'

        elif real_ext_high == b'\xFF\xD8\xFF\xE0':
            real_ext = 'JPG'

        elif real_ext_byte == b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A':
            real_ext = 'PNG'

        elif real_ext_high == b'\x25\x50\x44\x46':
            real_ext = 'PDF'

        elif real_ext_byte == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':
            real_ext = 'HWP'

        elif db_ext_byte == b'\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00':
            real_ext = 'SQLite'

        elif real_ext_high == b'regf':
            real_ext = 'registry hive file'

        entry = {'sname': name, 'attr': attr, 'cluster': cluster, 'size': size, 'ext': ext, 'real_ext': real_ext,
                 'create_time': create_time, 'create_date': create_date, 'lad': lad, 'write_time': write_time, 'write_date': write_date }


        if len(lfn) > 0:
            entry['name'] = lfn

        if data[0] == 0xE5:
            entry['del']='deleted'

        return entry

    def get_real_ext(self, cluster):
        real_ext = self.read_byte(((cluster-2)* self.spc + self.first_data_sector)*512, 16)
        return real_ext

    def get_content(self, cluster): #연결된 fat를 찾아서 data를 다 읽어온다
        fats = self.get_fats_by_start_cluster(cluster)
        return self.read_clusters(fats)

    def get_files(self, cluster):
        fats = self.get_fats_by_start_cluster(cluster)
        data = self.read_clusters(fats)

        lfn = ""
        for i in range(0, len(data), 32):
            entry_data = data[i:i + 32]  # 한 entry 씩 땡기네
            c = struct.unpack("<QQQQ", entry_data)
            if c[0] == 0 and c[1] == 0 and c[2] == 0 and c[3] == 0:
                break

            attr = entry_data[11]
            is_LFN = attr & 0x0F is 0x0F

            if not is_LFN:
                entry = self.parse_dir_entry(entry_data, lfn.strip())
                lfn = ""
                #print(entry)
                self.define_dir(entry)
            else:
                entry = self.parse_dir_entry_lfn(entry_data, lfn)
                lfn = entry['name']

    def get_fats_by_start_cluster(self, cluster, fat=1):
        # To get fat chain, it uses fat.
        base_sector = self.reserved_sectors + self.fat_size * (fat - 1)
        fats_per_sector = self.bps / 4

        fats = []

        next_cluster = cluster
        while next_cluster != self.END_CLUSTER:
            fats.append(next_cluster)
            sector, idx = divmod(next_cluster, fats_per_sector)
            sector = int(sector)
            idx = int(idx)

            data = self.read_sector(base_sector + sector)
            next_cluster = struct.unpack_from("<I", data, idx * 4)[0]

        return fats

    def define_dir(self,entry):

       """if entry['attr']==8 :
           print("volume :" + entry['sname'] + '    ' + str(entry['attr']))"""

       if entry['attr'] == 8 or entry['attr'] == 16 or entry['attr'] == 22:
           entry['ext']='Directory'
           self.dir_list.append(entry)

       elif entry['real_ext'] == 'registry hive file':
           self.file_list.append(entry)
           self.reg_list.append(entry)

       else:
            self.file_list.append(entry)


    def renew_list(self):
        self.dir_list=[]
        self.file_list=[]


if __name__ == '__main__':
    print("Fat32")

    fs = FAT32(sys.argv[1])

    #print(fs.root_cluster)
    fs.get_files(fs.root_cluster)
    print(fs.dir_list)

    """fs.renew_list()
    fs.get_files(7)
    for i in fs.dir_list:
        print(i['sname'])"""
