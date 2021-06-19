import requests
import re

class WebCrawling:
    def __init__(self, url, user_id, user_pw):
        self.url = url
        self.user_id = user_id
        self.user_pw = user_pw

    def web_crawling(self):
        print("#########################")
        print("현재 아이디, 비밀번호")
        print("ID: {0}, PW: {1}".format(self.user_id, self.user_pw))
        print("#########################")

        # 헤더 설정
        header = {
            "referer": self.url + "/Login",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36" # 크롬 버전에 맞는 user agent
        }

        login = {
            'mem_type:': 'A',
            'mem_userid': self.user_id,
            'mem_userpwd': self.user_pw,
            'mem_savechk': 'true',
            'user_id': self.user_id,
            'user_pwd': self.user_pw,
            'save_id1': 'on',
            'user_id': '',
            'user_pwd': ''
        }

        total_list = []
        p = re.compile('img_[0-9]+')
        error_log = ""
        with requests.Session() as s:
            try:
                site = s.post(self.url + "/Login", headers=header)
                site.raise_for_status()
                print("cookie")
                print(site.cookies.get_dict())

                r = s.get(self.url+ "/LoginOK", headers=header, data=login, cookies=site.cookies)
                if r.text.strip() != "true":
                    raise Exception("로그인에 실패했습니다.")

                # 찜 목록
                gd_no_list = []
                wish_list = s.get(self.url + "/jSel").json()
                print(wish_list)

                if not wish_list:
                    raise IndexError

                for wish in wish_list:
                    gd_no_list.append(wish["gd_no"])
                print(gd_no_list)

                for gd_no in gd_no_list:
                    data = {}
                    jginfo = {}
                    img_list = []

                    jginfo["gd_no"] = gd_no
                    wish = s.post(self.url + "/jGinfo", data=jginfo).json()
                    print(wish_list)

                    # 특수문자 제거(파일 생성 안됨) 후 제품명 가져오기
                    title = re.sub('[\/:*?"<>|]', '-', wish[0]['gd_name1'])
                    data['title'] = title
                    print('[제품명: ' + title + ']')

                    # 상세 사이즈
                    length = "상세 사이즈 : " + wish[0]['gd_sizestr']
                    data['length'] = length

                    # 가격
                    price = "가격 : " + str(wish[0]['gd_vprice'])
                    data['price'] = price

                    # 원산지
                    origin = "원산지 : " + wish[0]['gd_origin']
                    data['origin'] = origin

                    # 스타일
                    style = "스타일 : " + wish[0]['gd_class1']
                    data['style'] = style

                    # 모델 정보
                    if wish[0]['gd_modelstr'] == "":  # 쇼핑몰 사이트 마다 모델 정보가 다름 따라서 예외 처리
                        model = "모델정보 : " + wish[0]['gd_info5']
                    else:
                        model = "모델정보 : " + wish[0]['gd_modelstr'].split("||")[1]  # 모델 번호 빼기 (157||)이런거

                    data['model'] = model

                    # 혼용
                    mxratio = "혼용율 : " + wish[0]['gd_matter3']
                    data['mxratio'] = mxratio

                    # 등록 일자
                    date = "등록일자 : " + wish[0]['r_date']
                    data['date'] = date

                    # 세부정보
                    detail = "상세정보\n" + wish[0]['gd_myinfostr']
                    data['detail'] = detail

                    # 색상선택
                    color = "-- 색상 --\n" + wish[0]['gd_optcolornm'].replace("|", "\n")
                    data['color'] = color

                    # 사이즈
                    size = "-- 사이즈 --\n" + wish[0]['gd_optsize']
                    data['size'] = size.split('|')[0]

                    # txt 파일 하단 모델정보
                    if wish[0]['gd_modelstr'] == "":  # 쇼핑몰 사이트 마다 모델 정보가 다름 따라서 예외 처리
                        model_bottom = "-- 모델정보 --\n" + wish[0]['gd_info5']
                    else:
                        model_bottom = "-- 모델정보 --\n" + wish[0]['gd_modelstr'].split("||")[1]  # 모델 번호 빼기 (157||)이런거

                    data['model_bottom'] = model_bottom

                    # 이미지
                    for i in wish[0].keys():
                        if p.match(i):  # 정규식
                            img_list.append(wish[0].get(i))

                    # img_list중에 None값 제외
                    img_list = list(filter(None, img_list))
                    data['img_list'] = img_list

                    total_list.append(data)

                    # 찜하기 해제
                    print('찜하기 해제')
                    jjim_flag = {'gd_no': gd_no, 'gd_flag': '0'}
                    w = s.post(self.url + '/sLike', data=jjim_flag)

            except requests.exceptions.HTTPError as e:
                print("Http Error:", e)
                error_log = str(e)

            except IndexError:
                print('찜하기를 아직 누르지 않으셨습니다. 다시 눌러주세요')
                error_log = '찜하기를 아직 누르지 않으셨습니다. 다시 눌러주세요'

            except Exception as e:
                print('Exception 에러 발생!')
                print(str(e))
                error_log = str(e)

            else:
                error_log = "성공했습니다."

            finally:
                return total_list, error_log