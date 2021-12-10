import os
import random
import shutil
from configuration import TRAIN_SET_RATIO, TEST_SET_RATIO

class SplitDataset():
    def __init__(self, dataset_dir, saved_dataset_dir, train_ratio=TRAIN_SET_RATIO, test_ratio=TEST_SET_RATIO, show_progress=False):
        self.dataset_dir = dataset_dir                      #original data set
        self.saved_dataset_dir = saved_dataset_dir          #data set(result folder)
        self.saved_train_dir = saved_dataset_dir + "/train/"
        self.saved_valid_dir = saved_dataset_dir + "/valid/"
        self.saved_test_dir = saved_dataset_dir + "/test/"


        self.train_ratio = train_ratio
        self.test_radio = test_ratio
        self.valid_ratio = 1 - train_ratio - test_ratio

        self.train_file_path = []
        self.valid_file_path = []
        self.test_file_path = []

        self.index_label_dict = {}                          # class 이름을 key로 갖는 dict

        self.show_progress = show_progress

        if not os.path.exists(self.saved_train_dir):
            os.mkdir(self.saved_train_dir)
        if not os.path.exists(self.saved_test_dir):
            os.mkdir(self.saved_test_dir)
        if not os.path.exists(self.saved_valid_dir):
            os.mkdir(self.saved_valid_dir)


    def __get_label_names(self):
        label_names = []
        for item in os.listdir(self.dataset_dir):                   # original data set의 모든 파일에 대해
            item_path = os.path.join(self.dataset_dir, item)        # os.path.join :  두인자를 하나로 합쳐 1개 경로로 만듬, 경로 + 파일명
            if os.path.isdir(item_path):                            # 디렉토리면
                label_names.append(item)                            # label name 리스트에 추가
        return label_names #class 명을 저장하는 1차원배열

    def __get_all_file_path(self):
        all_file_path = []
        index = 0
        for file_type in self.__get_label_names():                      # 모든 class 에 대하여
            self.index_label_dict[index] = file_type                    # index_label_dict 에 전체 경로명 추가
            index += 1
            type_file_path = os.path.join(self.dataset_dir, file_type)
            file_path = []
            for file in os.listdir(type_file_path):                     #해당 class를 열고 내부의 모든 파일에 대해
                single_file_path = os.path.join(type_file_path, file)
                file_path.append(single_file_path)
            all_file_path.append(file_path)
        return all_file_path # list of list                             # all_file_path = [[class1내부모든파일], [class2내부모든파일...],....]

    def __copy_files(self, type_path, type_saved_dir):
        for item in type_path:
            src_path_list = item[1]
            dst_path = type_saved_dir + "%s/" % (item[0])
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)
            for src_path in src_path_list:
                shutil.copy(src_path, dst_path)
                if self.show_progress:
                    print("Copying file "+src_path+" to "+dst_path)

    def __split_dataset(self):
        all_file_paths = self.__get_all_file_path()                 # all_file_path = [[class1내부모든파일], [class2내부모든파일...],....]
        for index in range(len(all_file_paths)):                    # 모든 class에 대하여 (index == class 이름)
                                                                    # filepathlist = 현재보고있는 class 내부에있는 모든 파일 리스트
            file_path_list = all_file_paths[index]                  # 해당 클래스 내부의 파일갯수를 세고
            file_path_list_length = len(file_path_list)
            random.shuffle(file_path_list)                          # 클래스내부에서섞는다

            train_num = int(file_path_list_length * self.train_ratio)
            test_num = int(file_path_list_length * self.test_radio)

            self.train_file_path.append([self.index_label_dict[index], file_path_list[: train_num]])
            self.test_file_path.append([self.index_label_dict[index], file_path_list[train_num:train_num + test_num]])
            self.valid_file_path.append([self.index_label_dict[index], file_path_list[train_num + test_num:]])
                                                                    # append 되는 요소: list [filetype(class), filepath] 중 80%

    def start_splitting(self):
        self.__split_dataset()
        self.__copy_files(type_path=self.train_file_path, type_saved_dir=self.saved_train_dir)
        self.__copy_files(type_path=self.valid_file_path, type_saved_dir=self.saved_valid_dir)
        self.__copy_files(type_path=self.test_file_path, type_saved_dir=self.saved_test_dir)


if __name__ == '__main__':
    split_dataset = SplitDataset(dataset_dir="original_dataset",
                                 saved_dataset_dir="dataset",
                                 show_progress=True)
    split_dataset.start_splitting()