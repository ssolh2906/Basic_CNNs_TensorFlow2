'''
args 2개로 이미지 사이즈 입력
args = x, y
'''
import os
import shutil
import sys
from configuration import TRAIN_SET_RATIO, TEST_SET_RATIO
from PIL import Image

global target_size_x
global target_size_y

# Split Dataset 3
# Start~End frame 들을 한 세트로 움직임

class SplitDataset():
    def __init__(self, dataset_dir, saved_dataset_dir, train_ratio=TRAIN_SET_RATIO, test_ratio=TEST_SET_RATIO,
                 show_progress=False):
        self.dataset_dir = dataset_dir  # original data set
        self.saved_dataset_dir = saved_dataset_dir  # data set(result folder)
        self.saved_train_dir = saved_dataset_dir + "/train/"
        self.saved_valid_dir = saved_dataset_dir + "/valid/"
        self.saved_test_dir = saved_dataset_dir + "/test/"
        self.exception_dir = dataset_dir + "/size_exception/"
        # [self.index_label_dict[index][class], self.index_label_dict[index][subclass], list((경로,[S01.jpg,M01.jpg]),(경로2,[S01,M01,E01] ),...)]

        self.index_label_dict = {}  # class 이름을 value로 갖는 dict {0:class, 1:B001, 2:B002, class2, ...}
        # >>이중 dict {0:{"class":, "subclass":}, 1: {"class":, "subclass":}.... }

        self.show_progress = show_progress

        if not os.path.exists(self.exception_dir):
            os.mkdir(self.exception_dir)

        self.json_missing = []

        # if not os.path.exists(self.saved_train_dir):
        #     os.mkdir(self.saved_train_dir)
        # if not os.path.exists(self.saved_test_dir):
        #     os.mkdir(self.saved_test_dir)
        # if not os.path.exists(self.saved_valid_dir):
        #     os.mkdir(self.saved_valid_dir)

    def __get_label_names(self):
        label_names = []
        for class_dir in os.listdir(self.dataset_dir):  # original data set의 모든 파일에 대해
            if os.path.isdir(os.path.join(self.dataset_dir, class_dir)):
                for item in os.listdir(os.path.join(self.dataset_dir, class_dir)):
                    # item : string,폴더명 >> item : dict {"class":, "subclass":} / class 폴더는 예외처리
                    item_path = os.path.join(self.dataset_dir, class_dir,
                                             item)  # os.path.join :  두인자를 하나로 합쳐 1개 경로로 만듬, 경로 + 파일명 >> join(root, class, item)
                    class_subclass = item_path[item_path.find(self.dataset_dir) + len(self.dataset_dir) + 1:]
                    class_name = os.path.split(os.path.split(item_path)[0])[1]
                    if os.path.isdir(item_path):  # 디렉토리면
                        label_names.append({"class": class_name, "subclass": item})  # label name 리스트에 추가 <label name
        return label_names  # class 명을 저장하는 1차원배열, [class1, B001, B002, class2, ...  ] >> list of dictionary [{"class":, "item": },{"class":, "item":}, ....]


    def __get_all_file_path(self):
        all_file_path = []
        index = 0
        for file_type in self.__get_label_names():  # 모든 class (폴더명) 에 대하여 >> file_type : {"class":, "item":} 형태
            self.index_label_dict[index] = file_type  # append dict on dict
            index += 1
            # >> filetype : dict {"class":, "subclass":}
            type_file_path = os.path.join(self.dataset_dir, file_type["class"], file_type["subclass"])
            # root + 폴더명 (B003 의 경우 class명 빠진 상태) >> root + class + subclass
            file_path = dict()
            # type_file_path : root/class/subclass/
            for file in os.listdir(type_file_path):  # 해당 class/subclass 를 열고 내부의 모든 파일에 대해
                single_file_path = os.path.join(type_file_path, file[:file.rfind("-")+1])
                #ex : /경로/P-001-001-B003-M-A2009-N-20210819-01-01-

                frame_name = file[file.rfind("-")+1:]
                if not single_file_path in file_path:
                    #해당프레임의 첫 이미지
                    file_path[single_file_path] = list([frame_name])
                else :
                    file_path[single_file_path].append(frame_name)


                    #file path : dict {"경로명+액션명": list(S01.jpg, S01.json....), }
            all_file_path.append(file_path)
        return all_file_path  # list of list , 행 : class/subclass 열 : filename

    def start_cleansing(self):
        all_file_paths = self.__get_all_file_path()

        for action in all_file_paths:  # action : dict
            for key, file_list in action.items():
                for file in file_list:
                    if 'jpg' in file:
                        full_file_path = key+file
                        image = Image.open(full_file_path)

                        # size exception file found
                        if image.size[0] != target_size_x or image.size[1] != target_size_y :
                            dir_lv3 = os.path.split(full_file_path)
                            dir_lv2 = os.path.split(dir_lv3[0])
                            dir_lv1 = os.path.split(dir_lv2[0])

                            if self.show_progress:
                                print("[Image size exception] :", full_file_path)


    def start_comparing(self):
        all_file_paths = self.__get_all_file_path()
        targets = ["S01.jpg", "M01.jpg", "E01.jpg"]
        for action in all_file_paths: #action : dict
            for key, file_list in action.items():
                missing = False
                missing_files = []
                for target in targets :
                    if target not in file_list:
                        missing = True
                        missing_files.append(target)
                if missing:
                    print("MISSING FRAMES IN ", key)
                    print(missing_files)











if __name__ == '__main__':
    target_size_x = sys.argv[1]
    target_size_y = sys.argv[2]
    split_dataset = SplitDataset(dataset_dir="original_dataset",
                                 saved_dataset_dir="dataset",
                                 show_progress=True)
    split_dataset.start_cleansing()
