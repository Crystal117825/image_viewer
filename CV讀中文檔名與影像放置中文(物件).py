import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tkinter.filedialog
import math

class Cvplot():
    # 建立類別屬性來設定畫布大小
    # 屬性參考網頁：https://www.learncodewithmike.com/2020/01/python-attribute.html
    background_size = [600,1000]

    def __init__(self, raws = 1): # 建構式
        # 產生一個私有屬性list, 儲存所有被開啟圖片的絕對路徑, 使用tkinter產生開啟檔案視窗, 並可一次開啟多個檔案, 回傳檔案的絕對路徑, 設定只可選擇副檔名為jpg或png的檔案
        # 參考網頁1：https://docs.python.org/3/library/dialog.html#module-tkinter.filedialog
        # 參考網頁2：https://shengyu7697.github.io/python-tkinter-filedialog/
        # 參考網頁3：https://stackoverflow.com/questions/44403566/add-multiple-extensions-in-one-filetypes-mac-tkinter-filedialog-askopenfilenam
        self.__file_path_string = tkinter.filedialog.askopenfilenames(filetypes =(("影像檔",".jpg"),("影像檔" ,".png")))
        self.__filename_list = self.get_file_name()  # 呼叫getfilename方法 產生一個私有屬性list 裡面儲存所有圖片的檔名
        self.raw = raws                              # 圖片排列在背景上的raw數

    def get_file_name(self): # 取得開啟檔案的檔案名稱
        if self.__file_path_string.__len__() != 0:                  # 檢查__file_path_string是否有內容
            list1 = []                                              # 建立空的list
            for item in self.__file_path_string:                    # 將__file_path_string內的檔名拆分出來後放入list1內
                list1.append(item.split("/")[-1].split(".")[0])
            return list1                                            # 回傳list1
        else:                                                       # 若沒有內容則回傳None
            return None

    def showimage(self):
        if self.file_path_string.__len__() == 0:
            print("沒有選取圖片")
        else:
            if self.__file_path_string.__len__() > 30:
                print("選擇照片不可超過30張")
            else:
                if self.raw > 4:
                    print("raw設定數量過多")
                else:
                    frame_max_h, frame_max_w, interval_h, interval_w, total_col = self.__set_frame_size()             # 設定畫框大小
                    np_imgs_list = self.__cv2_imread(self.__file_path_string)                                         # 到路徑內將所有圖片轉成ndarray組成的list
                    merged_imgs_list = self.__merge_picture(np_imgs_list, frame_max_h, frame_max_w, total_col)        # 將圖片及文字放到畫框內存在list裡面
                    background = np.zeros((Cvplot.background_size[0], Cvplot.background_size[1]), np.uint8)           # 建立背景畫布
                    background = self.__cv2_Chinese_Text(background, '為什麼我放假不好好休息要折磨自己', 150, 30, 255, 45) # 將文字放到背景畫布上
                    # 結果可能上面的執行結果讓background變成不可修改, 造成後面出錯, 因此重新copy一份來使用
                    # 參考網頁：https://stackoverflow.com/questions/39554660/np-arrays-being-immutable-assignment-destination-is-read-only
                    img = background.copy()
                    for i in range(self.raw):          # 開始將畫框放到背景畫布上
                        for j in range(total_col):
                            if i * total_col + j >= len(merged_imgs_list):
                                break
                            else:
                                row_start = 100 + i * merged_imgs_list[0].shape[0] + interval_h * i
                                row_end = 100 + (i + 1) * merged_imgs_list[0].shape[0] + interval_h * i
                                col_start = 50 + j * merged_imgs_list[0].shape[1] + interval_w * j
                                col_end = 50 + (j + 1) * merged_imgs_list[0].shape[1] + interval_w * j
                                img[row_start:row_end, col_start:col_end] = merged_imgs_list[i * total_col + j][:, :]
                    cv2.imshow("Give back my holiday", img)
                    cv2.waitKey(0)
        return None


    @property # 使用裝飾器將私有屬性偽裝成功公開屬性
    def file_path_string(self):
        return self.__file_path_string

    @file_path_string.setter # 設定__file_path_string私有屬性時會呼叫這個方法
    def file_path_string(self, anything):
        self.__file_path_string = tkinter.filedialog.askopenfilenames(filetypes=(("影像檔", ".jpg"), ("影像檔", ".png")))
        self.__filename_list = self.getfilename()
        return None

    @property # 使用裝飾器將私有屬性偽裝成功公開屬性
    def filename_list(self):
        return self.__filename_list

    @filename_list.setter # 設定__filename_list私有屬性時會呼叫這個方法
    def filename_list(self, anything):
        self.__filename_list = self.get_file_name()
        return None

    def __cv2_imread(self, filepaths): #將路徑內的圖片轉成ndarray存入cv_img內
        cv_img = []
        for paths in filepaths:
            cv_img.append(cv2.imdecode(np.fromfile(paths, dtype=np.uint8), cv2.IMREAD_GRAYSCALE))
        return cv_img

    def __cv2_Chinese_Text(self, img, text, left, top, textColor, fontSize):
        ''' 建立中文字輸出 '''
        # 影像轉成 PIL影像格式
        if (isinstance(img, np.ndarray)):
            img = Image.fromarray(img)
        draw = ImageDraw.Draw(img)  # 建立PIL繪圖物件
        fontText = ImageFont.truetype(  # 建立字型 - 新細明體
            "C:\Windows\Fonts\msjh.ttc",  # 新細明體
            fontSize,  # 字型大小
            encoding="utf-8")  # 編碼方式
        draw.text((left, top), text, textColor, font=fontText)  # 繪製中文字
        # 將PIL影像格式轉成OpenCV影像格式
        return np.asarray(img)

    def __set_frame_size(self):   #根據選擇的檔案數量及raw數計算圖框大小及間距
        col = math.ceil(len(self.__file_path_string) / self.raw)
        frame_max_h = math.ceil((self.background_size[0] - 300) / self.raw)  # 圖框的最大高度
        frame_max_w = math.ceil((self.background_size[1] - 200) / col)       # 圖框的最大寬度
        interval_h = 0                                                       # 圖框間距
        if self.raw > 1:                            # raw>1才計算縱向間距
            interval_h = math.ceil(100 / (self.raw - 1))
        interval_w = 0
        if col > 1:                                 # col>1才計算橫向間距
            interval_w = math.ceil(100 / (col-1))
        return frame_max_h, frame_max_w, interval_h, interval_w, col

    def __merge_picture(self, np_imgs_list, frame_max_h, frame_max_w, col):
        # 將圖片放入圖框內並加入檔名
        merged_imgs_list = []
        img_h = frame_max_h - 40
        img_w = frame_max_w
        # 根據圖片的長寬不同, 選擇依據高度或寬度進行維持原比例的影像縮放, 再將檔名放到圖片上方
        for i, ndarray in enumerate(np_imgs_list):
            if ndarray.shape[0]/img_h > ndarray.shape[1]/img_w:
                # 圖片依高度調整
                imgarr = cv2.resize(ndarray, (math.ceil(ndarray.shape[1]/ndarray.shape[0]*img_h), img_h), interpolation=cv2.INTER_NEAREST)
                frame = np.zeros((frame_max_h, frame_max_w), np.uint8)
                frame[40:,:imgarr.shape[1]] = imgarr
                frame = self.__cv2_Chinese_Text(frame, self.__filename_list[i], 0, 0, 255, math.ceil(30/col)) # 中/英文檔名放置
                merged_imgs_list.append(frame)
            else:
                # 圖片依寬度調整
                imgarr = cv2.resize(ndarray, (img_w, math.ceil(ndarray.shape[0]/ndarray.shape[1]*img_w)),interpolation=cv2.INTER_NEAREST)
                frame = np.zeros((frame_max_h, frame_max_w), np.uint8)
                frame[40:40+imgarr.shape[0], :] = imgarr
                frame = self.__cv2_Chinese_Text(frame, self.__filename_list[i], 0, 0, 255, math.ceil(30/col)) # 中/英文檔名放置
                merged_imgs_list.append(frame)
        return merged_imgs_list






a = Cvplot(4) #可選擇排列數量(不寫預設1排)最多可選擇4排
a.showimage() #顯示圖片
#a.file_path_string = "anything"  #重新選取檔案
#a.showimage() #顯示圖片

