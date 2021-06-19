from selenium import webdriver
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import time
import os
import re

class NaverCrawling:
    def naver_cafe(page, downloadPath):

        driver = webdriver.Chrome()

        driver.get('https://nid.naver.com/nidlogin.login')

        user_id = ''
        user_pw = ''
        
        driver.execute_script("document.getElementsByName('id')[0].value=\'" + user_id + "\'")
        driver.execute_script("document.getElementsByName('pw')[0].value=\'" + user_pw + "\'")
        driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

        time.sleep(1)

        base_url = 'https://cafe.naver.com/ArticleList.nhn?search.clubid=29179343&search.menuid=6&search.boardtype=L&search.totalCount=151'


        driver.get(base_url + "&search.page=" + page)
        driver.switch_to.frame('cafe_main')

        article_list = driver.find_elements_by_css_selector('span.aaa > a.m-tcol-c')
        article_urls = [ i.get_attribute('href') for i in article_list ]
        res_list = []

        for article in article_urls:
            driver.get(article)
            driver.switch_to.frame('cafe_main')
            soup = bs(driver.page_source, 'html.parser')

            #제품설명
            title = soup.select('div.tit-box span.b')[0].get_text()
            createDate = soup.select('div.tit-box td.date')[0].get_text() + "\n\n"
            context = str(soup.select('div.tbody p')[0]).replace('<br/>','\n')
            context = createDate + str(re.sub('<.+?>', '', context, 0).strip())
            
            #원본url이 써있는 script 가져옴
            photoAlbum = soup.find_all('script',{'filename':'externalFile.jpg'}) 

            filepath = downloadPath + title
            textfile = filepath + "/" + title + ".txt"

            #제품설명txt
            if not(os.path.exists(filepath)):
                os.makedirs(filepath)
                f = open(textfile, "w" , -1, "utf-8")
                for i in context:
                    f.write(i)

            for i in enumerate(photoAlbum):
                index = str(i[0])
                downloadEnd = False
                
                #원본url 읽어오기
                t = urlopen(i[1].attrs['fileurl']).read() 

                filename = filepath + "/" + index + '.jpg'

                #해당 파일이 없으면 저장
                if not(os.path.exists(filename)):
                    with open(filename,"wb") as f:
                        f.write(t)
                    print("Image Save Success")

                else:
                    downloadEnd = True
                    print("pass")
                    break

            if downloadEnd :
                print("done!!")
                break
        driver.quit()

        return True

    def naver_blog(posturl, download_path):
        driver = webdriver.Chrome()
        driver.get(posturl)

        driver.switch_to.frame('mainFrame')
        soup = bs(driver.page_source, 'html.parser')

        details = soup.select('div.se-module')

        title = download_path.split('\\')[-1]
        textfile = download_path + "\\"+ title + ".txt"

        if not(os.path.exists(download_path)):
            os.makedirs(download_path)
            f = open(textfile, "w" , -1, "utf-8")
            for detail in details:
                f.write(detail.get_text() + '\n')

        if not(os.path.exists(download_path)):
            os.makedirs(download_path)

        imgs = soup.select('img.se-image-resource')

        for index, url in enumerate(imgs):
            filename = download_path + "/" + str(index) + ".jpg"
            original = url.attrs['src'].split('?')[0].replace('postfiles','blogfiles')
            
            if not(os.path.exists(filename)):
                with open(filename, 'wb') as f:
                    f.write(urlopen(original).read())
            print('success')
        
        driver.quit()



    