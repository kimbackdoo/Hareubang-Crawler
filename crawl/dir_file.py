import html
import os
import re

import requests

class DirFile:
    def __init__(self, shop_data_dict, img_list, path, shop):
        self.shop_data_dict = shop_data_dict
        self.img_list = img_list
        self.path = path
        self.shop = shop

    def save_to_local(self):
        try:
            folder_name = self.shop_data_dict["title"]
            folder_name = folder_name.replace(" ", "")
            folder = self.path + "/" + self.shop + "-" + folder_name

            print("===================================================================")
            if not os.path.exists(folder):
                os.makedirs(folder)
                print("파일생성")
            else:
                print("파일 존재")

        except OSError:
            print('Error : Creating folder with ' + folder)

        except Exception as e:
            print('Exception 에러 발생!')
            print(str(e))

        else:
            txt_file_location = folder + "/" + folder_name + ".txt"
            cleanr = re.compile("<.*?>")
            print(txt_file_location)
            # txt 파일 저장
            with open(txt_file_location, "w", encoding="utf-8") as txtFile:
                for shop_data in self.shop_data_dict.values():
                    txtFile.write(html.unescape(re.sub(cleanr, "", str(shop_data).replace("</p>", "\n").replace("<br />", "\n"))) + "\n\n")

                print("txt 파일 저장 완료")
            # 이미지 저장
            key = 0
            for img_file in self.img_list:
                img_file_name = folder + "/" + folder_name + '_' + str(key + 1) + '.jpg'

                r = requests.get(img_file)
                file = open(img_file_name, "wb")
                file.write(r.content)
                file.close()

                key += 1
            print("이미지 저장 완료")
            print("===================================================================")