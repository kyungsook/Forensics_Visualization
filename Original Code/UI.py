import sys, os, enum
# QT5 Python Binding
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from operator import itemgetter

import fat32Test

class Mode(enum.Enum):
    READ = 0  # Purely read the hex.
    ADDITION = 1  # Add to the hex.
    OVERRIDE = 2  # Override the current text.


class FileSelector(QFileDialog):  # FILE 입출력부
    def __init__(self):
        super().__init__()

        self.selectFile()  # FILE 선택창 열어줌
        self.show()  # 위젯에 띄워줌

    def selectFile(self):  # FILE 선택창 설정
        options = QFileDialog.Options()  # 이 속성은 대화 상자의 모양과 느낌에 영향을 미치는 다양한 옵션을 보유함
        options != QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files(*))", options=options) #fileName에 open한 file name 받아서 저장하고 그 외에 return값은 무시
        # 사용자가 선택한 기존 파일을 반환하는 편의 정적 기능이다. 사용자가 취소를 누르면 null 문자열이 반환된다.
        # 윈도우즈 및 macOS에서 이 정적 기능은 QFileDialog가 아닌 기본 파일 대화 상자를 사용한다.
        # 1. 어느 위젯에 띄울지결정 하는포인터인것 같고, 다이어로그창 이름, 작업하려는 dir 시작점, 필터 (ex / All dir 로 걸면 dir 만 보임), option 인데
        # 필터 여러개중 고를 수 있네
        # Dir 인자는 제대로 돌아가는지 모르겠네

        self.fileName = fileName


class InputDialogue(QInputDialog):  # 대화상자에 input값과 get 설정
    def __init__(self, title, text):
        super().__init__()

        # Dialogue options.
        self.dialogueTitle = title
        self.dialogueText = text

        self.initUI()

    # initUI ... Initialize the main view of the dialogue.
    def initUI(self):
        dialogueResponse, dialogueComplete = QInputDialog.getText(self, self.dialogueTitle, self.dialogueText,
                                                                  QLineEdit.Normal, '')
        # 1. 부모위젯 포인터 , 2, 타이틀, 3,그 머고 XXX : ___ 에 XX 담당 인듯,4. 그리고 mode ( echo mode ) 같은것, 4.  받아오는 스트링

        if dialogueComplete and dialogueResponse:
            self.dialogueReponse = dialogueResponse

        else:
            self.dialogueReponse = ''


class App(QMainWindow, QWidget):  # 창의 대부분의 기능
    def __init__(self):  # 창 기본 세팅 설정
        super().__init__()

        # Window options!
        self.title = 'HexQT'
        self.left = 0
        self.top = 0
        self.width = 1280
        self.height = 840


        self.byteWidth = 2  # How many bits to include in a byte.
        self.mode = Mode.READ
        self.initUI()
        self.read_cluster=2


    # openFile ... Opens a file directory and returns the filename.
    def openFile(self):
        fileSelect = FileSelector()
        fileName = fileSelect.fileName

        if fileName != '':
            self.readFile(fileName)


    # readFile ... Reads file data from a file in the form of bytes and generates the text for the hex-editor.
    def readFile(self, fileName):
        self.read_FAT_DATA = fat32Test.FAT32(fileName)
        self.read_cluster = self.read_FAT_DATA.root_cluster

        self.read_FAT_DATA.get_files(self.read_cluster)
        self.generateView(self.read_FAT_DATA.read_sector(0, 32), 0) # 처음 시작했을 때는 vbr 영역만큼(32 sector) 읽는다


    def saveFile(self):
        print('Saved!')

    def sizeAscFile(self):
        print('size asc')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('size'))
        self.read_FAT_DATA.file_list.sort(key=itemgetter('size'))
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def sizeDesFile(self):
        print('size des')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('size'), reverse=True)
        self.read_FAT_DATA.file_list.sort(key=itemgetter('size'), reverse=True)
        print(self.read_FAT_DATA.file_list)
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def createAscFile(self):
        print('create asc')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('create_date', 'create_time'))
        self.read_FAT_DATA.file_list.sort(key=itemgetter('create_date', 'create_time'))
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def createDesFile(self):
        print('create des')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('create_date', 'create_time'), reverse=True)
        self.read_FAT_DATA.file_list.sort(key=itemgetter('create_date', 'create_time'), reverse=True)
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def writeAscFile(self):
        print('write asc')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('write_date', 'write_time'))
        self.read_FAT_DATA.file_list.sort(key=itemgetter('write_date', 'write_time'))
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def writeDesFile(self):
        print('write des')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('write_date', 'write_time'), reverse=True)
        self.read_FAT_DATA.file_list.sort(key=itemgetter('write_date', 'write_time'), reverse=True)
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def ladAscFile(self):
        print('lad asc')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('lad'))
        self.read_FAT_DATA.file_list.sort(key=itemgetter('lad'))
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def ladDesFile(self):
        print('lad des')
        self.read_FAT_DATA.renew_list()
        self.read_FAT_DATA.get_files(self.read_cluster)
        self.read_FAT_DATA.dir_list.sort(key=itemgetter('lad'), reverse=True)
        self.read_FAT_DATA.file_list.sort(key=itemgetter('lad'), reverse=True)
        self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    # generateView ... Generates text view for hexdump likedness.
    def generateView(self, text,cluster):

        space = ' '
        rowSpacing = 4  # How many bytes before a double space.
        rowLength = 16  # 헥사 창에 얼마나 많은 byte 가 들어갈 것인지

        if cluster == 0:
            offset = 0

        else:
            offset = ((cluster - 2) * self.read_FAT_DATA.spc + self.read_FAT_DATA.first_data_sector) * 512

        offsetText = ''
        mainText = ''
        asciiText = ''

        for i in reversed(range(self.button_list_area.count())):
            self.button_list_area.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.file_button_list_area.count())):
            self.file_button_list_area.itemAt(i).widget().setParent(None)

        button_data = []
        file_button_data = []

        for i in self.read_FAT_DATA.dir_list:
            if 'name' in i:
                button_data.append(i['name'])

            else:
                button_data.append(i['sname'])

        for i in self.read_FAT_DATA.file_list:
            if 'name' in i:
                file_button_data.append(i['name'])
            else:
                file_button_data.append(i['sname'])


        for chars in range(1, len(text) + 1):
            byte = text[chars - 1]
            char = chr(text[chars - 1])

            # Asciitext 는 오른쪽 출력부
            if char is ' ':
                asciiText += '.'

            elif char is '\n':
                asciiText += '!'

            else:
                asciiText += char
            # main text 가 중앙에 있는것
            mainText += format(byte, '02X')

            if chars % rowLength is 0 and chars != 0:
                offsetText += format(offset, '08x')+'\n'
                offset += 16
                mainText += '\n'
                #asciiText += '\n'

            elif chars % rowSpacing is 0:
                mainText += space * 2

            else:
                mainText += space

        out = ''
        byte_arr = QByteArray(text)

        val = self.QByteArrayToString(byte_arr)
        a = list(val.split(','))
        for i in range(len(a)):
            if int(a[i]) != 0:
                out += chr(int(a[i]))

        for i in self.read_FAT_DATA.file_list:
            if i['cluster'] == cluster:
                #byte_arr = QByteArray(text)
                self.asciiImageArea.loadFromData(byte_arr, i['ext'])


        self.offsetTextArea.setText(offsetText)
        self.mainTextArea.setText(mainText)
        self.asciiTextArea.setText(asciiText)
        self.TextArea.setText(out)


        button_list_info = self.btn_list(button_data, 0)
        file_button_list_info=self.btn_list(file_button_data, 1)

        for i in range(len(button_list_info)):
            self.button_list_area.addWidget(button_list_info[i])
            button_list_info[i].clicked.connect(lambda state,a=i: self.button_on_clicked(button_data[a]))

        for i in range(len(file_button_list_info)):
            self.file_button_list_area.addWidget(file_button_list_info[i])
            file_button_list_info[i].clicked.connect(lambda state, a=i: self.file_button_on_clicked(file_button_data[a]))

        self.button_list_area.setAlignment(Qt.AlignTop)
        self.file_button_list_area.setAlignment(Qt.AlignTop)
        self.Imagelb.setPixmap(self.asciiImageArea)

    def file_generateView(self, text,cluster):
        space = ' '

        rowSpacing = 4
        rowLength = 16

        offset = ((cluster - 2) * self.read_FAT_DATA.spc + self.read_FAT_DATA.first_data_sector) *512
        offsetText = ''
        mainText = ''
        asciiText = ''

        for chars in range(1, len(text) + 1):
            byte = text[chars - 1]
            char = chr(text[chars - 1])

            # Asciitext 는 오른쪽 출력부
            if char is ' ':
                asciiText += '.'

            elif char is '\n' or char is '\r':
                asciiText += '.'

            else:
                asciiText += char
            # main text 가 중앙에 있는것
            mainText += format(byte, '02X')

            if chars % rowLength is 0 and chars != 0:
                offsetText += format(offset, '08x')+'\n'
                offset += 16
                mainText += '\n'
                asciiText += '\n'

            elif chars % rowSpacing is 0:
                mainText += space * 2

            else:
                mainText += space

        out = ''
        byte_arr = QByteArray(text)

        val = self.QByteArrayToString(byte_arr)

        a = list(val.split(','))
        for i in range(len(a)):
            if int(a[i]) != 0:
                out += chr(int(a[i]))

        for i in self.read_FAT_DATA.file_list:
            if i['cluster'] == cluster:
                self.asciiImageArea.loadFromData(byte_arr, i['ext'])

        self.offsetTextArea.setText(offsetText)
        self.mainTextArea.setText(mainText)
        self.asciiTextArea.setText(asciiText)
        self.TextArea.setText(out)

        self.button_list_area.setAlignment(Qt.AlignTop)
        self.file_button_list_area.setAlignment(Qt.AlignTop)
        self.Imagelb.setPixmap(self.asciiImageArea)


    def QByteArrayToString(self, _val):
        out_str = ''
        for i in range(_val.count()):
            out_str += str(ord(_val[i]))
            if i < _val.count() - 1:
                out_str += ','
        return out_str

    def btn_list(self, name, type):
        btnList = []
        self.btnTop = 100

        for i in range(len(name)):
            btnList.append(self.button_create(name[i], type))
            btnList[i].resize(QSize(80, 25))
            btnList[i].move(10, self.btnTop)

        return btnList

    def button_create(self, name, type):
        button = QPushButton(name, self)

        if type == 0: #if directory
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirIcon')))

        elif type == 1: #if file
            button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileIcon')))

        button.setToolTip(name)
        button.setFixedSize(230,20)
        button.setStyleSheet("QPushButton { text-align: left; }")

        return button

    def button_on_clicked(self, name):
        for i in self.read_FAT_DATA.dir_list:
            if (name==i['sname']) or ('name' in i and name ==i['name']) :
                if 'del' in i:
                    i['real_ext'] = 'Deleted Directory'
                    create_string = str(((i['create_date'] & 65024) >> 9) + 1980) + '/' + str(
                            (i['create_date'] & 480) >> 5) + '/' + str(i['create_date'] & 31) + ' - ' + str(
                                            (i['create_time'] & 63488) >> 11) + ':' + str(
                                            (i['create_time'] & 2016) >> 5) + ':' + str(
                                            (i['create_time'] & 31) * 2)

                    write_string = str(((i['write_date'] & 65024) >> 9) + 1980) + '/' + str(
                            (i['write_date'] & 480) >> 5) + '/' + str(i['write_date'] & 31) + ' - ' + str(
                                           (i['write_time'] & 63488) >> 11) + ':' + str(
                                           (i['write_time'] & 2016) >> 5) + ':' + str(
                                           (i['write_time'] & 31) * 2)

                    infoText = 'File Extension: ' + i['ext'] + '\nFile Signature: ' + i[
                        'real_ext'] + '\nSize: ' + str(
                        i['size']) + '\ncreate: ' + create_string + '\nwrite: ' + write_string

                    self.asciiTextArea.setText('Deleted Directory')
                    self.TextArea.setText('')
                    self.asciiImageArea.loadFromData(QByteArray(b''), i['ext'])
                    self.Imagelb.setPixmap(self.asciiImageArea)
                    self.infoArea.setText(infoText)
                    break;

                else:
                    self.read_cluster=i['cluster']
                    if self.read_cluster == 0:
                       self.read_cluster=2
                    #self.read_FAT_DATA.renew_list()
                    i['real_ext'] = 'Directory'
                    create_string = str(((i['create_date'] & 65024) >> 9) + 1980) + '/' + str(
                        (i['create_date'] & 480) >> 5) + '/' + str(i['create_date'] & 31) + ' - ' + str(
                        (i['create_time'] & 63488) >> 11) + ':' + str(
                        (i['create_time'] & 2016) >> 5) + ':' + str(
                        (i['create_time'] & 31) * 2)

                    write_string = str(((i['write_date'] & 65024) >> 9) + 1980) + '/' + str(
                        (i['write_date'] & 480) >> 5) + '/' + str(i['write_date'] & 31) + ' - ' + str(
                        (i['write_time'] & 63488) >> 11) + ':' + str(
                        (i['write_time'] & 2016) >> 5) + ':' + str(
                        (i['write_time'] & 31) * 2)

                    infoText = 'File Extension: ' + i['ext'] + '\nFile Signature: ' + i[
                        'real_ext'] + '\nSize: ' + str(
                        i['size']) + '\ncreate: ' + create_string + '\nwrite: ' + write_string
                    self.infoArea.setText(infoText)
                    self.asciiImageArea.loadFromData(QByteArray(b''), i['ext'])
                    self.Imagelb.setPixmap(self.asciiImageArea)
                    self.read_FAT_DATA.renew_list()
                    self.read_FAT_DATA.get_files(self.read_cluster)
                    self.generateView(self.read_FAT_DATA.get_content(self.read_cluster), self.read_cluster)

    def file_button_on_clicked(self, name):
        for i in self.read_FAT_DATA.file_list:
            if (name==i['sname']) or ('name' in i and name ==i['name']) :
                if 'del' in i:
                    print("it's delete")
                    i['real_ext']='Deleted File'
                    create_string = str(((i['create_date'] & 65024) >> 9) + 1980) + '/' + str(
                        (i['create_date'] & 480) >> 5) + '/' + str(i['create_date'] & 31) + ' - ' + str(
                        (i['create_time'] & 63488) >> 11) + ':' + str(
                        (i['create_time'] & 2016) >> 5) + ':' + str(
                        (i['create_time'] & 31) * 2)

                    write_string = str(((i['write_date'] & 65024) >> 9) + 1980) + '/' + str(
                        (i['write_date'] & 480) >> 5) + '/' + str(i['write_date'] & 31) + ' - ' + str(
                        (i['write_time'] & 63488) >> 11) + ':' + str(
                        (i['write_time'] & 2016) >> 5) + ':' + str(
                        (i['write_time'] & 31) * 2)

                    infoText = 'File Extension: ' + i['ext'] + '\nFile Signature: ' + i[
                        'real_ext'] + '\nSize: ' + str(
                        i['size']) + '\ncreate: ' + create_string + '\nwrite: ' + write_string

                    self.asciiTextArea.setText('Deleted File')
                    self.TextArea.setText('')
                    self.asciiImageArea.loadFromData(QByteArray(b''), i['ext'])
                    self.Imagelb.setPixmap(self.asciiImageArea)
                    self.infoArea.setText(infoText)
                    break;

                if 'size'==0 in i: #파일 목록에서 디렉토리일때
                    self.read_cluster = i['cluster']
                    if self.read_cluster == 0:
                        self.read_cluster = 2
                    # self.read_FAT_DATA.renew_list()

                else:
                    #self.read_cluster=i['cluster']
                    if self.read_cluster == 0:
                      self.read_cluster=2
                   # self.read_FAT_DATA.renew_list()

                create_string = str(((i['create_date'] & 65024) >> 9) + 1980) + '/' + str(
                    (i['create_date'] & 480) >> 5) + '/' + str(i['create_date'] & 31) + ' - ' + str(
                    (i['create_time'] & 63488) >> 11) + ':' + str(
                    (i['create_time'] & 2016) >> 5) + ':' + str(
                    (i['create_time'] & 31) * 2)

                write_string = str(((i['write_date'] & 65024) >> 9) + 1980) + '/' + str(
                    (i['write_date'] & 480) >> 5) + '/' + str(i['write_date'] & 31) + ' - ' + str(
                    (i['write_time'] & 63488) >> 11) + ':' + str(
                    (i['write_time'] & 2016) >> 5) + ':' + str(
                    (i['write_time'] & 31) * 2)

                infoText = 'File Extension: ' + i['ext'] + '\nFile Signature: ' + i[
                    'real_ext'] + '\nSize: ' + str(i['size']) + '\ncreate: ' + create_string + '\nwrite: ' + write_string
                self.infoArea.setText(infoText)
                self.file_generateView(self.read_FAT_DATA.get_content(i['cluster']), i['cluster'])

    # highlightMain ... Bi-directional highlighting from main.
    def highlightMain(self):
        # Create and get cursors for getting and setting selections.
        highlightCursor = QTextCursor(self.asciiTextArea.document())
        # asciitextArea의 처음을 가르치는 커서를 구성
        cursor = self.mainTextArea.textCursor()
        # 커서의 위치의 사본을 따서 복사 함
        # Clear any current selections and reset text color.
        highlightCursor.select(QTextCursor.Document)
        highlightCursor.setCharFormat(QTextCharFormat())
        highlightCursor.clearSelection()

        # Information about where selections and rows start.
        selectedText = cursor.selectedText()  # The actual text selected.
        selectionStart = cursor.selectionStart()
        selectionEnd = cursor.selectionEnd()

        mainText = self.mainTextArea.toPlainText().replace('\n', 'A')

        totalBytes = 0

        for char in mainText[selectionStart:selectionEnd]:
            if char is not ' ':
                totalBytes += len(char)

        asciiStart = 0

        for char in mainText[:selectionStart]:
            if char is not ' ':
                asciiStart += len(char)

        totalBytes = round(totalBytes / self.byteWidth)
        asciiStart = round(asciiStart / self.byteWidth)
        asciiEnd = asciiStart + totalBytes

        asciiText = self.asciiTextArea.toPlainText()

        # Select text and highlight it.
        highlightCursor.setPosition(asciiStart, QTextCursor.MoveAnchor)
        highlightCursor.setPosition(asciiEnd, QTextCursor.KeepAnchor)

        highlight = QTextCharFormat()
        highlight.setBackground(Qt.darkCyan)
        highlightCursor.setCharFormat(highlight)
        highlightCursor.clearSelection()

    # highlightAscii ... Bi-directional highlighting from ascii.
    def highlightAscii(self):
        selectedText = self.asciiTextArea.textCursor().selectedText()
        # Create and get cursors for getting and setting selections.
        highlightCursor = QTextCursor(self.mainTextArea.document())
        # asciitextArea의 처음을 가르치는 커서를 구성
        cursor = self.asciiTextArea.textCursor()
        # 커서의 위치의 사본을 따서 복사 함
        # Clear any current selections and reset text color.
        highlightCursor.select(QTextCursor.Document)
        highlightCursor.setCharFormat(QTextCharFormat())
        highlightCursor.clearSelection()

        # Information about where selections and rows start.
        selectedText = cursor.selectedText()  # The actual text selected.
        selectionStart = cursor.selectionStart()
        selectionEnd = cursor.selectionEnd()
       # print(self.ascilTextArea.toPlainText());
        asciiText = self.asciiTextArea.toPlainText().replace('\n', 'A')

        totalBytes = 0

        for char in asciiText[selectionStart:selectionEnd]:
            if char is not ' ':
                totalBytes += len(char)

        MainStart = 0

        for char in asciiText[:selectionStart]:
            if char is not ' ':
               MainStart += len(char)

        totalBytes = round(totalBytes * self.byteWidth)
        MainStart = round(MainStart * self.byteWidth)
        MainEnd = MainStart + totalBytes

        asciiText = self.asciiTextArea.toPlainText()

        # Select text and highlight it.
        highlightCursor.setPosition(MainStart, QTextCursor.MoveAnchor)
        highlightCursor.setPosition(MainEnd, QTextCursor.KeepAnchor)

        highlight = QTextCharFormat()
        highlight.setBackground(Qt.darkCyan)
        highlightCursor.setCharFormat(highlight)
        highlightCursor.clearSelection()

    # offsetJump ... Creates a dialogue and gets the offset to jump to and then jumps to that offset.

    def offsetJump(self):  # input dialog 를 활용 하여 jump to ofsset 을 만듭니다.
        jumpText = InputDialogue('Jump to Offset', 'Offset').dialogueReponse

        if jumpText != '':
            jumpOffset = int(int(jumpText) / 512)
            if jumpOffset == 0 :
                jumpCluster = 0

            else :
                jumpCluster = int((jumpOffset-self.read_FAT_DATA.first_data_sector)/self.read_FAT_DATA.spc+2)
            print(jumpOffset)
            print(jumpCluster)
            self.generateView(self.read_FAT_DATA.read_sector(jumpOffset), jumpCluster)


    # createMainView ... Creates the primary view and look of the application (3-text areas.)
    def createMainView(self):
        file_list_Widget = QWidget()
        file_list = QWidget()
        Button_area = QHBoxLayout()
        file_list_Widget.setStyleSheet("background-color:black;")
        file_list.setStyleSheet("background-color:black;")

        hexa_info_box = QHBoxLayout()
        totalBox = QVBoxLayout()

        # file list button 출력 widget
        file_list_Widget.setFixedSize(600, 300)

        # file list button 붙일 button box
        self.button_list_area = QVBoxLayout()  # buttonbox 생성
        self.file_button_list_area = QVBoxLayout()  # file쪽

        # Image 출력할 영역
        self.Imagelb = QLabel()
        self.Imagescrollarea = QScrollArea()
        self.Imagescrollarea.setWidgetResizable(True)

        # hexa, offset 출력할 영역
        self.mainTextArea = QTextEdit()
        self.offsetTextArea = QTextEdit()


        self.tab = QTabWidget()  # tab 생성

        self.asciiTextArea = QTextEdit()  # ascii text 출력
        self.asciiImageArea = QPixmap()  # 이미지 파일의 경우 이미지 출력
        self.TextArea = QTextEdit()  # 문서파일의 경우 text 출력
        self.infoArea = QTextEdit() # directory entry에 저장된 확장자와 실제 파일의 확장자를 출력

        self.Imagelb.setStyleSheet("background-color:black;")
        self.Imagescrollarea.setWidget(self.Imagelb)

        # Create the fonts and styles to be used and then apply them.
        font = QFont("Consolas", 11, QFont.Normal, False)

        self.mainTextArea.setFont(font)
        self.asciiTextArea.setFont(font)
        self.offsetTextArea.setFont(font)
        self.TextArea.setFont(font)
        self.infoArea.setFont(font)

        self.tab.addTab(self.asciiTextArea, "ASCII")
        self.tab.addTab(self.TextArea, "TEXT")
        self.tab.addTab(self.Imagescrollarea, "IMAGE")
        self.tab.addTab(self.infoArea, "INFO")

        # Initialize them all to read only.
        self.mainTextArea.setReadOnly(True)
        self.asciiTextArea.setReadOnly(True)
        self.offsetTextArea.setReadOnly(True)
        self.TextArea.setReadOnly(True)
        self.infoArea.setReadOnly(True)

        # Syncing scrolls.
        syncScrolls(self.mainTextArea, self.asciiTextArea, self.offsetTextArea, self.TextArea)

        # Highlight linking. BUG-GY
        self.mainTextArea.selectionChanged.connect(self.highlightMain)
        self.asciiTextArea.selectionChanged.connect(self.highlightAscii)

        file_list_Widget.setLayout(self.button_list_area);  # button list
        file_list.setLayout(self.file_button_list_area);
        hexa_info_box.addWidget(self.offsetTextArea, 1)
        hexa_info_box.addWidget(self.mainTextArea, 4)
        hexa_info_box.addWidget(self.tab, 4)

        Button_area.addWidget(file_list_Widget)
        Button_area.addWidget(file_list)
        totalBox.addLayout(Button_area)
        totalBox.addLayout(hexa_info_box)
        return totalBox


    # initUI ... Initializes the min look of the application.
    def initUI(self):
        # Initialize basic window options.
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Center the window.
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # Creates a menu bar, (file, edit, options, etc...)
        mainMenu = self.menuBar()

        # Menus for window.
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        helpMenu = mainMenu.addMenu('Help')

        fileMenu.setToolTipsVisible(True)
        editMenu.setToolTipsVisible(True)
        viewMenu.setToolTipsVisible(True)
        helpMenu.setToolTipsVisible(True)

        # FILE MENU ---------------------------------------

        # Open button.
        openButton = QAction(QIcon(), 'Open', self)
        openButton.setShortcut('Ctrl+O')
        openButton.setToolTip('Open file')
        openButton.triggered.connect(self.openFile)

        # Save button.
        saveButton = QAction(QIcon(), 'Save', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.setToolTip('Open file')
        saveButton.triggered.connect(self.saveFile)

        # Optional exit stuff.
        exitButton = QAction(QIcon(), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setToolTip('Exit application')
        exitButton.triggered.connect(self.close)

        fileMenu.addAction(openButton)
        fileMenu.addAction(saveButton)
        fileMenu.addAction(exitButton)

        # EDIT MENU ---------------------------------------

        # Jump to Offset
        offsetButton = QAction(QIcon(), 'Jump to Offset', self)
        offsetButton.setShortcut('Ctrl+J')
        offsetButton.setToolTip('Jump to Offset')
        offsetButton.triggered.connect(self.offsetJump)

        editMenu.addAction(offsetButton)

        # VIEW MENU ---------------------------------------

        """openButton = QAction(QIcon(), 'Open', self)
        openButton.setShortcut('Ctrl+O')
        openButton.setStatusTip('Open file')
        openButton.triggered.connect(self.openFile)"""

        # Sort Files by Size in Ascending Order
        sizeAscButton = QAction(QIcon(), 'size ↑', self)
        sizeAscButton.setToolTip('Sort Files by Size in Ascending Order')
        sizeAscButton.triggered.connect(self.sizeAscFile)

        # Sort Files by Size in Descending Order
        sizeDesButton = QAction(QIcon(), 'size ↓', self)
        sizeDesButton.setToolTip('Sort Files by Size in Descending Order')
        sizeDesButton.triggered.connect(self.sizeDesFile)

        # Sort Files by Create Time in Ascending Order
        createAscButton = QAction(QIcon(), 'Create ↑', self)
        createAscButton.setToolTip('Sort Files by Create Time in Ascending Order')
        createAscButton.triggered.connect(self.createAscFile)

        # Sort Files by Create Time in Descending Order
        createDesButton = QAction(QIcon(), 'Create ↓', self)
        createDesButton.setToolTip('Sort Files by Create Time in Descending Order')
        createDesButton.triggered.connect(self.createDesFile)

        #Sort Files by Write Time in Ascending Order
        writeAscButton = QAction(QIcon(), 'Write ↑', self)
        writeAscButton.setToolTip('Sort Files by Write Time in Ascending Order')
        writeAscButton.triggered.connect(self.writeAscFile)

        # Sort Files by Write Time in Descending Order
        writeDesButton = QAction(QIcon(), 'Write ↓', self)
        writeDesButton.setToolTip('Sort Files by Write Time in Descending Order')
        writeDesButton.triggered.connect(self.writeDesFile)

        #Sort Files by Last Access Date in Ascending Order
        ladAscButton = QAction(QIcon(), 'Last Access ↑', self)
        ladAscButton.setToolTip('Sort Files by Last Access Date in Ascending Order')
        ladAscButton.triggered.connect(self.ladAscFile)

        # Sort Files by Last Access Date in Descending Order
        ladDesButton = QAction(QIcon(), 'Last Access ↓', self)
        ladDesButton.setToolTip('Sort Files by Last Access Date in Descending Order')
        ladDesButton.triggered.connect(self.ladDesFile)

        viewMenu.addAction(sizeAscButton)
        viewMenu.addAction(sizeDesButton)
        viewMenu.addAction(createAscButton)
        viewMenu.addAction(createDesButton)
        viewMenu.addAction(writeAscButton)
        viewMenu.addAction(writeDesButton)
        viewMenu.addAction(ladAscButton)
        viewMenu.addAction(ladDesButton)

        # Creating a widget for the central widget thingy.
        centralWidget = QWidget()
        centralWidget.setLayout(self.createMainView())

        self.setCentralWidget(centralWidget)

        # Show our masterpiece.
        self.show()


# syncScrolls ... Syncs the horizontal scrollbars of multiple qTextEdit objects. Rather clunky but it works.
def syncScrolls(qTextObj0, qTextObj1, qTextObj2, qTextObj3):
    scroll0 = qTextObj0.verticalScrollBar()
    scroll1 = qTextObj1.verticalScrollBar()
    scroll2 = qTextObj2.verticalScrollBar()
    scroll3 = qTextObj3.verticalScrollBar()

    # There seems to be no better way of doing this at present so...

    scroll0.valueChanged.connect(
        scroll1.setValue
    )

    scroll0.valueChanged.connect(
        scroll2.setValue
    )

    scroll0.valueChanged.connect(
        scroll3.setValue
    )

    scroll1.valueChanged.connect(
        scroll0.setValue
    )

    scroll1.valueChanged.connect(
        scroll2.setValue
    )

    scroll1.valueChanged.connect(
        scroll3.setValue
    )

    scroll2.valueChanged.connect(
        scroll0.setValue
    )

    scroll2.valueChanged.connect(
        scroll1.setValue
    )

    scroll2.valueChanged.connect(
        scroll3.setValue
    )


# setStyle ... Sets the style of the QT Application. Right now using edgy black.

def setStyle(qApp):
    qApp.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, Qt.black)
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.white)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)


    qApp.setPalette(dark_palette)

    qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


def main():

    app = QApplication(sys.argv)
    setStyle(app)
    hexqt = App()

    sys.exit(app.exec_())


# Initialize the brogram.
if __name__ == '__main__':
    main()