import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot

import crawl.shop as wc
import crawl.dir_file as fd

from crawl.kakao import KakaoCrawling as kc
from crawl.sinsang import SinsangCrwaling as sc
from crawl.naver import NaverCrawling as nc

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 750, 750)
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle("하르방")

        self.tab_widget = MyTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.show()

class MyTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout()

        self.path = "C:/Users/metasoft/Desktop/info"

        f = open("./shop/shops.txt", 'r',  encoding='UTF8')
        data = f.read().split('\n')
        f.close()

        self.shops = {}
        for i in range(len(data)):
            if i % 2 == 0:
                self.shops[data[i]] = data[i+1]

        self.user_id = '아이디'  # 아이디
        self.user_pw = '비밀번호'  # 비밀번호

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(500, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "거래처")
        self.tabs.addTab(self.tab2, "기타")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)

        # 라벨 설정 및 폰트 설정
        self.downloadLabel = QLabel("다운로드 경로 지정")
        self.downloadFont = self.downloadLabel.font()
        self.downloadFont.setPointSize(13)
        self.downloadLabel.setFont(self.downloadFont)

        self.tab1.layout.addWidget(self.downloadLabel)

        # 경로 지정 박스
        self.pathGroupbox = QGroupBox()
        self.pathGbox = QGridLayout()
        self.pathGroupbox.setLayout(self.pathGbox)

        self.downloadPath = QLineEdit(self.path)
        self.downloadPathButton = QPushButton('경로')
        self.saveButton = QPushButton('저장')

        self.pathGbox.addWidget(self.downloadPath, 1, 1)
        self.pathGbox.addWidget(self.downloadPathButton, 1, 2)
        self.pathGbox.addWidget(self.saveButton, 1, 3)

        # 경로 버튼 연결
        self.downloadPathButton.clicked.connect(self.localDownloadPath)
        self.saveButton.clicked.connect(self.savePath)

        self.tab1.layout.addWidget(self.pathGroupbox)

        # 전제 거래처 라벨 및 ID, PW 설정
        self.totalCountGroupbox = QGroupBox()
        self.totalCountGbox = QGridLayout()
        self.totalCountGroupbox.setLayout(self.totalCountGbox)

        # 전체 거래처 라벨 설정
        self.totalCountLabel = QLabel("전체 거래처 ({}개)".format(len(data) // 2))
        self.totalCountFont = self.totalCountLabel.font()
        self.totalCountFont.setPointSize(13)
        self.totalCountLabel.setFont(self.totalCountFont)

        # 크롤링 버튼
        self.crawlButton = QPushButton("Crawl")
        # self.crawlButton.setStyleSheet("padding: 10px; background-color: #FA8072;")
        self.crawlButton.setStyleSheet("padding: 10px; background-color: #F0F8FF;")

        # ID, PW 설정 버튼
        self.loginButton = QPushButton("전체 ID/PW 설정")
        # self.loginButton.setStyleSheet("padding: 10px; background-color: #66CDAA;")
        self.loginButton.setStyleSheet("padding: 10px;")
        self.loginButton.clicked.connect(self.loginDialog)

        self.totalCountGbox.addWidget(self.totalCountLabel, 1, 1)
        self.totalCountGbox.addWidget(self.loginButton, 1, 2)
        self.totalCountGbox.addWidget(self.crawlButton, 1, 3)

        self.tab1.layout.addWidget(self.totalCountGroupbox)

        # 거래처 리스트
        self.shopList = QListWidget(self)
        self.shopList.setSelectionMode(2)
        self.shopList.setStyleSheet("font-size: 17px;")

        for index, (key, value) in enumerate(self.shops.items()):
            self.shopList.addItem(key)

        shopBtnVbox = QVBoxLayout()
        for text, slot in (("거래처 추가", self.add), ("수정", self.edit), ("삭제", self.remove), ("정렬", self.sort)):
            button = QPushButton(text)
            # button.setStyleSheet("padding: 15px; background-color: #FDF5E6;")
            button.setStyleSheet("padding: 15px;")
            buttonFont = button.font()
            buttonFont.setPointSize(13)
            button.setFont(buttonFont)
            shopBtnVbox.addWidget(button)
            button.clicked.connect(slot)

        shopListHbox = QHBoxLayout()
        shopListHbox.addWidget(self.shopList)
        shopListHbox.addLayout(shopBtnVbox)
        self.tab1.layout.addLayout(shopListHbox)

        # 선택한 거래처명, url 표시
        self.shopName = QLabel(self)
        self.shopName.setStyleSheet("font-size: 17px;")
        self.tab1.layout.addWidget(self.shopName)

        self.shopUrl = QLabel(self)
        self.shopUrl.setStyleSheet("font-size: 17px;")
        self.tab1.layout.addWidget(self.shopUrl)

        # 리스트 아이템에 변화가 있을 경우 현재 아이템 가져오기
        self.shopList.currentItemChanged.connect(self.shopInfo)
        # 현재 선택된 아이템 크롤링
        self.crawlButton.clicked.connect((lambda state : self.pageCrawling(state, self.path, self.shopUrl.text(), self.shopName.text())))

        self.tab1.setLayout(self.tab1.layout)

        #Create second tab
        self.tab2.layout = QVBoxLayout(self)

        #카카오
        self.groupbox1 = QGroupBox("카카오스토리")
        self.gbox = QGridLayout()

        self.groupbox1.setLayout(self.gbox)

        self.l1 = QLabel()
        self.l1.setText('url')
        self.kakaoUrl = QLineEdit()
        self.gbox.addWidget(self.l1, 0, 0)
        self.gbox.addWidget(self.kakaoUrl, 0, 1)

        self.l2 = QLabel()
        self.l2.setText('다운로드 경로')
        self.kakaoPath = QLineEdit()
        self.kakaoPath.setText(self.path)

        self.fileButton1 = QPushButton('File')

        self.gbox.addWidget(self.l2, 1, 0)
        self.gbox.addWidget(self.kakaoPath, 1, 1)
        self.gbox.addWidget(self.fileButton1, 1, 3)

        self.kakaoButton = QPushButton('Crawl')
        self.gbox.addWidget(self.kakaoButton, 2,3)

        # 신상마켓
        self.groupbox2 = QGroupBox("신상마켓")
        self.gbox = QGridLayout()

        self.groupbox2.setLayout(self.gbox)

        self.l3 = QLabel()
        self.l3.setText('url')
        self.sinsangUrl = QLineEdit()
        self.gbox.addWidget(self.l3, 0, 0)
        self.gbox.addWidget(self.sinsangUrl, 0, 1)

        self.l8 = QLabel()
        self.l8.setText('다운로드 경로')
        self.sinsangPath = QLineEdit()
        self.sinsangPath.setText(self.path)

        self.fileButton4 = QPushButton('File')

        self.gbox.addWidget(self.l8, 1, 0)
        self.gbox.addWidget(self.sinsangPath, 1, 1)
        self.gbox.addWidget(self.fileButton4, 1, 3)

        self.sinsangButton = QPushButton('Crawl')
        self.gbox.addWidget(self.sinsangButton, 2,3)

        # 네이버 블로그
        self.groupbox4 = QGroupBox("네이버 블로그")
        self.gbox = QGridLayout()

        self.groupbox4.setLayout(self.gbox)

        self.l4 = QLabel()
        self.l4.setText('url')
        self.blogUrl = QLineEdit()
        self.gbox.addWidget(self.l4, 0, 0)
        self.gbox.addWidget(self.blogUrl, 0, 1)

        self.l5 = QLabel()
        self.l5.setText('다운로드 경로')
        self.blogPath = QLineEdit()
        self.blogPath.setText(self.path)

        self.fileButton2 = QPushButton('File')

        self.gbox.addWidget(self.l5, 1, 0)
        self.gbox.addWidget(self.blogPath, 1, 1)
        self.gbox.addWidget(self.fileButton2, 1, 3)

        self.blogButton = QPushButton('Crawl')
        self.gbox.addWidget(self.blogButton, 2,3)

        #네이버 카페
        self.groupbox3 = QGroupBox("네이버 카페")
        self.gbox = QGridLayout()

        self.groupbox3.setLayout(self.gbox)

        self.l6 = QLabel()
        self.l6.setText('page')
        self.cafePage = QLineEdit()
        self.gbox.addWidget(self.l6, 0, 0)
        self.gbox.addWidget(self.cafePage, 0, 1)

        self.l7 = QLabel()
        self.l7.setText('다운로드 경로')
        self.cafePath = QLineEdit()
        self.cafePath.setText(self.path)

        self.fileButton3 = QPushButton('File')

        self.gbox.addWidget(self.l7, 1, 0)
        self.gbox.addWidget(self.cafePath, 1, 1)
        self.gbox.addWidget(self.fileButton3, 1, 3)

        self.cafeButton = QPushButton('Crawl')
        self.gbox.addWidget(self.cafeButton, 2,3)

        #tab2 layout set
        self.tab2.layout.addWidget(self.groupbox1)
        self.tab2.layout.addWidget(self.groupbox2)
        self.tab2.layout.addWidget(self.groupbox3)
        self.tab2.layout.addWidget(self.groupbox4)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # 버튼 click function 연결
        self.fileButton1.clicked.connect((lambda state, number=1 : self.findPath(state, number)))
        self.fileButton2.clicked.connect((lambda state, number=2 : self.findPath(state, number)))
        self.fileButton3.clicked.connect((lambda state, number=3 : self.findPath(state, number)))
        self.fileButton4.clicked.connect((lambda state, number=4 : self.findPath(state, number)))

        self.kakaoButton.clicked.connect(self.kakaoCrawling)
        self.sinsangButton.clicked.connect(self.sinsangCrawling)
        self.blogButton.clicked.connect(self.blogCrawling)
        self.cafeButton.clicked.connect(self.cafeCrawling)

    def shopInfo(self):
        print(self.shopList.selectedItems())
        self.shopLists = [item.text() for item in self.shopList.selectedItems()]

        # print(self.shopLists)
        # item = self.shopList.currentItem()
        # self.shopName.setText(item.text())
        # self.shopUrl.setText(self.shops[item.text()])

    def loginDialog(self):
        self.loginInfoDialog = QDialog(self)
        self.loginInfoDialog.setWindowTitle("전체 ID/PW 설정")
        self.loginInfoDialog.resize(352, 147)

        self.lbID = QLabel("ID :   "); idFont = self.lbID.font(); idFont.setPointSize(13); self.lbID.setFont(idFont)
        self.editID = QLineEdit(self.user_id)

        self.lbPW = QLabel("PW : "); pwFont = self.lbPW.font(); pwFont.setPointSize(13); self.lbPW.setFont(pwFont)
        self.editPW = QLineEdit(self.user_pw)

        btnOk = QPushButton("저장")
        btnOk.clicked.connect(self.saveLoginBtn)
        btnCancel = QPushButton("취소")
        btnCancel.clicked.connect(self.cancelLoginBtn)

        vbox = QVBoxLayout(self)
        hboxID = QHBoxLayout(self)
        hboxID.addWidget(self.lbID); hboxID.addWidget(self.editID)
        vbox.addLayout(hboxID)

        hboxPW = QHBoxLayout(self)
        hboxPW.addWidget(self.lbPW); hboxPW.addWidget(self.editPW)
        vbox.addLayout(hboxPW)

        hboxBtn = QHBoxLayout(self)
        hboxBtn.addWidget(btnOk); hboxBtn.addWidget(btnCancel)
        vbox.addLayout(hboxBtn)

        self.loginInfoDialog.setLayout(vbox)
        self.loginInfoDialog.show()

    def saveLoginBtn(self):
        self.user_id = self.editID.text()
        self.user_pw = self.editPW.text()
        self.loginInfoDialog.close()

    def cancelLoginBtn(self):
        self.loginInfoDialog.close()

    def localDownloadPath(self):
        fname = QFileDialog.getExistingDirectory(self)
        self.downloadPath.setText(fname)

    def savePath(self):
        if self.downloadPath.text() == "":
            QMessageBox.question(self, "Message", "빈칸입니다.", QMessageBox.Ok, QMessageBox.Ok)
        else:
            ok = QMessageBox.question(self, "Message", "저장되었습니다.", QMessageBox.Ok, QMessageBox.Ok)
            if ok == QMessageBox.Ok:
                self.path = self.downloadPath.text()

    def add(self):
        self.addDialog = QDialog(self)
        self.addDialog.setWindowTitle("거래처 추가")
        self.addDialog.resize(352, 147)

        self.lbAddShop = QLabel("거래처 : ")
        shopFont = self.lbAddShop.font()
        shopFont.setPointSize(13)
        self.lbAddShop.setFont(shopFont)
        self.addShop = QLineEdit()

        self.lbAddUrl = QLabel("url :        ")
        urlFont = self.lbAddUrl.font()
        urlFont.setPointSize(13)
        self.lbAddUrl.setFont(urlFont)
        self.addUrl = QLineEdit()

        addBtnOk = QPushButton("저장")
        addBtnOk.clicked.connect(self.addSaveBtn)
        addBtnCancel = QPushButton("취소")
        addBtnCancel.clicked.connect(self.addCancelBtn)

        vbox = QVBoxLayout(self)
        hboxShop = QHBoxLayout(self)
        hboxShop.addWidget(self.lbAddShop)
        hboxShop.addWidget(self.addShop)
        vbox.addLayout(hboxShop)

        hboxUrl = QHBoxLayout(self)
        hboxUrl.addWidget(self.lbAddUrl)
        hboxUrl.addWidget(self.addUrl)
        vbox.addLayout(hboxUrl)

        hboxBtn = QHBoxLayout(self)
        hboxBtn.addWidget(addBtnOk)
        hboxBtn.addWidget(addBtnCancel)
        vbox.addLayout(hboxBtn)

        self.addDialog.setLayout(vbox)
        self.addDialog.show()

    def edit(self):
        row = self.shopList.currentRow()
        item = self.shopList.item(row)
        if item is None:
            QMessageBox.question(self, "Message", "선택된 항목이 없습니다.", QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.editDialog = QDialog(self)
            self.editDialog.setWindowTitle("거래처 수정")
            self.editDialog.resize(352, 147)

            self.lbEditShop = QLabel("거래처 : ")
            shopFont = self.lbEditShop.font()
            shopFont.setPointSize(13)
            self.lbEditShop.setFont(shopFont)
            self.editShop = QLineEdit(item.text())

            self.lbEditUrl = QLabel("url :        ")
            urlFont = self.lbEditUrl.font()
            urlFont.setPointSize(13)
            self.lbEditUrl.setFont(urlFont)
            self.editUrl = QLineEdit(self.shops[item.text()])

            editBtnOk = QPushButton("저장")
            editBtnOk.clicked.connect(self.editSaveBtn)
            editbtnCancel = QPushButton("취소")
            editbtnCancel.clicked.connect(self.editCancelBtn)

            vbox = QVBoxLayout(self)
            hboxShop = QHBoxLayout(self)
            hboxShop.addWidget(self.lbEditShop)
            hboxShop.addWidget(self.editShop)
            vbox.addLayout(hboxShop)

            hboxUrl = QHBoxLayout(self)
            hboxUrl.addWidget(self.lbEditUrl)
            hboxUrl.addWidget(self.editUrl)
            vbox.addLayout(hboxUrl)

            hboxBtn = QHBoxLayout(self)
            hboxBtn.addWidget(editBtnOk)
            hboxBtn.addWidget(editbtnCancel)
            vbox.addLayout(hboxBtn)

            self.editDialog.setLayout(vbox)
            self.editDialog.show()

    def remove(self):
        row = self.shopList.currentRow()
        item = self.shopList.item(row)
        if item is not None:
            reply = QMessageBox.question(self, "Message", "{}을 삭제하시겠습니까?".format(self.shopName.text()), QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                item = self.shopList.takeItem(row)
                del self.shops[item.text()]
                del item
        else:
            QMessageBox.question(self, "Message", "선택된 항목이 없습니다.", QMessageBox.Ok, QMessageBox.Ok)

    def sort(self):
        self.shopList.sortItems()

    def addSaveBtn(self):
        if self.addShop.text() == "" or self.addUrl.text() == "":
            QMessageBox.question(self, "Message", "빈칸입니다.", QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.shops[self.addShop.text()] = self.addUrl.text()

            QMessageBox.question(self, "Message", "저장되었습니다.", QMessageBox.Ok, QMessageBox.Ok)
            self.shopList.addItem(self.addShop.text())

            self.addDialog.close()

    def addCancelBtn(self):
        self.addDialog.close()

    def editSaveBtn(self):
        if self.editShop.text() == "" or self.editUrl.text() == "":
            QMessageBox.question(self, "Message", "빈칸입니다.", QMessageBox.Ok, QMessageBox.Ok)
        else:
            row = self.shopList.currentRow()
            item = self.shopList.item(row)

            self.shops[self.editShop.text()] = self.shops[item.text()]
            del self.shops[item.text()]

            self.shops[self.editShop.text()] = self.editUrl.text()

            QMessageBox.question(self, "Message", "저장되었습니다.", QMessageBox.Ok, QMessageBox.Ok)
            item.setText(self.editShop.text())
            self.shopName.setText(item.text())
            self.shopUrl.setText(self.shops[item.text()])

            self.editDialog.close()

    def editCancelBtn(self):
        self.editDialog.close()

    @pyqtSlot()
    def pageCrawling(self, state, path, url, shop):
        print(self.shopLists)
        self.shopLists = []

        if url == "" or shop == "":
            QMessageBox.question(self, "Message", "선택된 항목이 없습니다.", QMessageBox.Ok, QMessageBox.Ok)
        else:
            crawl = wc.WebCrawling(url, self.user_id, self.user_pw)
            wc_data = crawl.web_crawling()
            data_list, error_log = wc_data
            for shop_data_dict in data_list:
                img_list = shop_data_dict["img_list"]
                del shop_data_dict["img_list"]

                download = fd.DirFile(shop_data_dict, img_list, path, shop)
                download.save_to_local()

            print("===================================================================")
            print("shop: " + shop)
            print("url: " + url)
            if data_list != []: print("Crawling Success")
            else: print("Crawling Fail")
            print("===================================================================")

    def findPath(self, state, number):
        fname = QFileDialog.getExistingDirectory(self)
        if number == 1:
            self.kakaoPath.setText(fname)
        elif number == 2:
            self.blogPath.setText(fname)
        elif number == 3:
            self.cafePath.setText(fname)
        else:
            self.sinsanPath.Text(fname)

    def kakaoCrawling(self):
        url = self.kakaoUrl.text()
        downloadpath_kakao = self.kakaoPath.text()
        kc.kakao_crawling(url, downloadpath_kakao)

    def sinsangCrawling(self):
        url = self.sinsangUrl.text()
        path = self.sinsangPath.text()
        sc.singsang_crawling(url, path)

    def blogCrawling(self):
        url = self.blogUrl.text()
        download_blog = self.blogPath.text()
        nc.naver_blog(url, download_blog)

    def cafeCrawling(self):
        download_path = self.cafePath.text()
        page = self.cafePage.text()
        nc.naver_cafe(page, download_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
