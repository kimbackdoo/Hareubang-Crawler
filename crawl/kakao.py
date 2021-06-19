from selenium import webdriver
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pandas as pd
import time
import os
import sys
import json
import re
class KakaoCrawling:
    def kakao_crawling(url, downloadpath):
        
        driver = webdriver.Chrome()
        driver.get('https://accounts.kakao.com/login/kakaostory')
        
        user_id = ''
        user_pw = ''

        driver.find_element_by_xpath('//*[@id="id_email_2"]').send_keys(user_id)
        driver.find_element_by_xpath('//*[@id="id_password_3"]').send_keys(user_pw)
        driver.find_element_by_xpath('//*[@id="login-form"]/fieldset/div[8]/button').click()

        time.sleep(2)

        driver.get(url)
        soup = bs(driver.page_source, 'html.parser')
        script = str(soup.find_all('script')[1]).split('\n')

        #sripte 태그 + 불필요한 부분 제거 + 제이슨 형식으로 변경
        test = script[1].replace("boot.parseInitialData(",'')
        test = test.replace( ");" , '')

        #image 원본 url 저장할 배열
        img_urls = []

        title = downloadpath.split('\\')[-1]
        
        #content 저장할 주소
        #폴더 없으면 생성
        if not(os.path.exists(downloadpath)):
            os.makedirs(downloadpath)
        textfile = downloadpath + "\\" + title + ".txt"

        try:
            data = json.loads(test)
            getCreatedDate = data['activity']['created_at'].split('T')
            date = str(getCreatedDate[0]) + "\n"
        
            #제품 정보
            info = data['activity']['content']
            images = data['activity']['media']
            
            #text작성
            f = open(textfile, "w" , -1, "utf-8")
            f.write(date)
            for i in info:
                f.write(i)

        except:

            #제품정보
            r = re.compile('"content":(.*?),"require')
            m = r.search(test)
            if m:
                content = m.group(1)
                info = content.split('\\n')

            #image url
            i = re.compile('"media":(.*?),"content"')
            j = i.search(test)     
            if j:
                images = json.loads(j.group(1))

            #제품 등록 날짜
            a = re.compile('"created_at":"(.*?),"with_tag_count"')
            b = a.search(test)
            if b:
                date = str(b.group(1)).split('T')[0] + '\n'
            
            #text 파일 만들기
            f = open(textfile, "w" , -1, "utf-8")
            f.write(date)
            for i in info:
                f.write(i+'\n')

        #원본 url 저장
        for img in images:
            img_urls.append( img['origin_url'] )

        #이미지 다운로드
        for index in range(len(img_urls)):
            
            #원본url 읽어오기
            t = urlopen(img_urls[index]).read() 

            filename = downloadpath + "/" + str(index) + '.jpg'

            #해당 파일이 있으면 저장하지 않고 없으면
            if not(os.path.exists(filename)):
                with open(filename,"wb") as f:
                    f.write(t)
                print("Image Save Success")
        
        f.close()

        print("Done!")
        driver.quit()
       
        return True