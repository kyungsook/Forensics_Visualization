class Dir:
    #추후 날짜 입력받아서 필터링할때 사용예정
    total_dir_list = []
    total_file_list = []

    def __init__(self, entry=None):
        self.current_dir = entry
        self.file_list = []
        self.dir_obj_list = []  # 객체 배열
        self.dir_list = []  # 엔트리 배열
        self.reg_obj_list = [] # 레지스트리 객체 배열
        self.reg_list = []  # 레지스트리 엔트리 배열

    def get_current(self, entry):
        self.current_dir = entry

    def get_parent(self, entry):
        self.parent_dir = entry