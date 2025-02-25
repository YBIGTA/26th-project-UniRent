import requests
from bs4 import BeautifulSoup as bs
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from abc import ABC, abstractmethod
from time import sleep
import boto3
from fastapi import FastAPI, APIRouter, Depends, Query
import re 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from database.mongodb_connection import MongoDB


class BaseCrawler(ABC):
    def __init__(self, output_dir: str, place=""):
        self.output_dir = output_dir
        self.url = ""
        self.driver = None



    def start_browser(self) -> None:
        '''start chrome browser'''
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(self.url)
        sleep(3)
        self.driver = driver

    @abstractmethod
    def scrape_reviews(self):
        pass

    def save_to_database(self) -> None:
        """Save reviews."""
        with open(os.path.join(self.output_dir, "data.json"),  'w', encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


class ThreeThreeCrawler(BaseCrawler):
    def __init__(self, output_dir, place="서대문구"):
        self.output_dir = os.path.join(output_dir, "threethree")
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = []
        
        options = Options()
        # options.add_argument("--headless")  # UI 없이 실행 (필요시 주석 해제)
        options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=options)
        self.url = f'https://33m2.co.kr/webpc/search/keyword?keyword={place}&start_date=&end_date=&week='
        self.place = place

    def scrape_reviews(self):
        driver = self.driver
        driver.get(self.url)
        sleep(3)

        data = []
        page = 1
        flag = True

        while flag:
            try:
                # 📌 현재 페이지에서 방 목록 가져오기
                room_elements = driver.find_elements(By.CLASS_NAME, "room_item")

                for index, room in enumerate(room_elements):
                    try:
                        # ✅ 방 클릭
                        room.find_element(By.XPATH, "./ancestor::a").click()
                        sleep(3)
                        
                        # ✅ 새 창으로 이동
                        windows = driver.window_handles
                        if len(windows) > 1:
                            driver.switch_to.window(windows[1])

                        # ✅ HTML 파싱
                        soup = bs(driver.page_source, 'html.parser')
                        room_data = {}

                        # 📌 1️⃣ 방 제목 크롤링
                        title_selector = 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong'
                        title = soup.select_one(title_selector)
                        room_data['title'] = title.text.strip() if title else "unknown"

                        # 📌 2️⃣ 폴더 생성 (특수 문자 제거)
                        safe_title = re.sub(r'[\/:*?"<>|]', '_', room_data['title'])
                        img_dir = os.path.join(self.output_dir, safe_title)
                        img_dir = os.path.normpath(img_dir)
                        os.makedirs(img_dir, exist_ok=True)

                        print(f"✅ 폴더 생성 완료: {img_dir}")

                        # 📌 3️⃣ 이미지 크롤링 및 저장
                        try:
                            parent_div = driver.find_element(By.CLASS_NAME, 'swiper-wrapper')
                            images = parent_div.find_elements(By.TAG_NAME, "img")

                            image_urls = set()  # 중복 제거

                            for img in images:
                                img_url = img.get_attribute("src")
                                if img_url:
                                    image_urls.add(img_url)

                            for idx, img_url in enumerate(image_urls):
                                try:
                                    response = requests.get(img_url, stream=True)
                                    img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                                    img_path = os.path.join(img_dir, f"{idx}{img_ext}")
                                    img_path = os.path.normpath(img_path)

                                    if response.status_code == 200:
                                        with open(img_path, "wb") as file:
                                            for chunk in response.iter_content(1024):
                                                file.write(chunk)
                                        print(f"✅ Downloaded: {img_url}")

                                except Exception as e:
                                    print(f"❌ 이미지 다운로드 실패: {img_url}, 오류: {e}")

                        except Exception as e:
                            print(f"❌ Swiper 이미지 크롤링 오류: {e}")

                        # 📌 4️⃣ 주소 크롤링
                        addr_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(1) > p'
                        addr = soup.select_one(addr_selector)
                        room_data['addr'] = addr.text.strip() if addr else ""

                        # 📌 5️⃣ 가격 크롤링
                        price_selector = 'body > div.wrap > section > div > div.room_sticky > div.room_pay > p > strong'
                        price = soup.select_one(price_selector)
                        room_data['price'] = price.text.strip() if price else ""

                        # 📌 6️⃣ 옵션 크롤링
                        options = []
                        option_selectors = [
                            'body > div.wrap > section > div > div.room_detail > div:nth-child(5) > ul',
                            'body > div.wrap > section > div > div.room_detail > div:nth-child(6) > ul'
                        ]
                        for selector in option_selectors:
                            option_elements = soup.select(selector)
                            for option in option_elements:
                                options.extend([p.text.strip() for p in option.find_all('p')])

                        room_data['options'] = options

                        # 📌 7️⃣ 방 상세 페이지 URL 저장
                        room_data['url'] = driver.current_url
                        data.append(room_data)

                        # ✅ 창 닫기 및 원래 창으로 복귀
                        driver.close()
                        driver.switch_to.window(windows[0])
                        sleep(2)

                    except Exception as e:
                        print(f"❌ 방 크롤링 오류: {e}")

                # 📌 8️⃣ 다음 페이지로 이동
                try:
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'next'))
                    )
                    next_page_button.click()
                    print("✅ 다음 페이지 이동 성공")
                    sleep(3)

                except Exception as e:
                    print("❌ 다음 페이지 없음. 크롤링 종료")
                    flag = False

            except Exception as e:
                print("❌ 페이지 크롤링 오류:", e)
                flag = False

        self.data = data

        # ✅ 크롤링 완료 후 드라이버 종료
        driver.quit()
    


                


class HowBoutHereCrawler(BaseCrawler):
    def __init__(self, output_dir: str, place="서대문구"):
        '''Constructor for JSCrawler'''
        self.output_dir = os.path.join(output_dir, "howbouthere")
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = []
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")  # Recommended for some systems
        self.driver: webdriver.Chrome = webdriver.Chrome(options=options)
        self.url = "https://www.yeogi.com/domestic-accommodations?keyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&autoKeyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&checkIn=2025-02-22&checkOut=2025-02-23&personal=2&freeForm=false"
        self.place = place
    
    def scrape_reviews(self):
        driver = self.driver
        url = self.url
        driver.get(url)
        sleep(3)

        data = []
        page = 1

        while True:
            i = 1
            while True:
                try:
                    driver.find_element(By.XPATH, f'//*[@id="__next"]/div/main/section/div[2]/a[{i}]').click()
                    sleep(2)
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])
                    soup = bs(driver.page_source, 'html.parser')
                    room = {}
                    
                    # 숙소 제목 크롤링
                    title_selector = '#overview > div.css-3fvoms > div.css-mn17j9 > div.css-hn31yc > div.css-1tn66r8 > h1'
                    title = soup.select(title_selector)
                    room['title'] = title[0].text.strip() if title else "unknown"

                    # 📌 특수 문자 제거 후 폴더명 변환
                    safe_title = re.sub(r'[\/:*?"<>|]', '_', room['title'])
                    img_dir = os.path.join(self.output_dir, safe_title)
                    img_dir = os.path.normpath(img_dir)  # 운영체제별 경로 정리
                    os.makedirs(img_dir, exist_ok=True)
                    print(f"✅ 폴더 생성 완료: {img_dir}")

                    # # 📌 이미지 크롤링 및 저장
                    # try:
                    #     parent_div = driver.find_element(By.XPATH, '//*[@id="overview"]/article/div[1]/ul')
                    #     images = parent_div.find_elements(By.TAG_NAME, "img")

                    #     image_urls = set()  # 중복 제거를 위한 Set

                    #     for img in images:
                    #         img_url = img.get_attribute("src")
                    #         if img_url and img_url not in image_urls:
                    #             image_urls.add(img_url)

                    #     # 이미지 다운로드 및 저장
                    #     for index, img_url in enumerate(image_urls):
                    #         try:
                    #             headers = {
                    #                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                    #             }

                    #             response = requests.get(img_url, headers=headers, stream=True)
                    #             print(f"응답 데이터 크기: {len(response.content)} 바이트")

                    #             # 📌 이미지 확장자 자동 추출
                    #             img_ext = os.path.splitext(img_url.split("?")[0])[1]
                    #             if not img_ext:  # 확장자가 없으면 기본값 설정
                    #                 img_ext = ".jpg"

                    #             # 📌 올바른 저장 경로 생성
                    #             img_path = os.path.join(img_dir, f"{index}{img_ext}")
                    #             img_path = os.path.normpath(img_path)  # 운영체제별 경로 정리

                    #             print(f"이미지가 저장될 경로: {img_path}")

                    #             if response.status_code == 200:
                    #                 with open(img_path, "wb") as file:
                    #                     for chunk in response.iter_content(1024):
                    #                         file.write(chunk)
                    #                 print(f"✅ Downloaded: {img_url}")

                    #         except Exception as e:
                    #             print(f"❌ 이미지 다운로드 실패: {img_url}, 오류: {e}")

                    # except Exception as e:
                    #     print(f"❌ 이미지 크롤링 오류: {e}")

                    # 📌 주소 크롤링
                    addr_selector = '#overview > div.css-3fvoms > div.css-y3ur5y > div.css-1insk2s > a > p'
                    addr = soup.select(addr_selector)
                    room['addr'] = addr[0].text.strip() if addr else ""

                    def extract_region(addr: str) -> str:
                        """
                        📌 주소(addr)에서 동(洞) 단위 지역명을 추출하는 함수
                        예: "서울특별시 서대문구 홍제동 00번지" -> "홍제동"
                        """
                        match = re.search(r'([가-힣]+동)', addr)
                        return match.group(1) if match else "알 수 없음"  # 동 이름이 없으면 "알 수 없음" 반환

                    # 📌 1️⃣ 'region' 필드 자동 추가 (addr에서 동(洞) 추출)
                    room["region"] = extract_region(room.get("addr", ""))

                    # 📌 2️⃣ 숙소 유형(type) 추가 ("모텔"로 고정)
                    room["type"] = "모텔"

                    # 📌 가격 크롤링 및 최저가 계산
                    j = 1
                    price_table = {}
                    min_price = float('inf')  # 최저가 찾기 위한 초기값

                    while True:
                        try:
                            # 📌 가격 정보 크롤링
                            price_selector = f'#room > div.css-g6g7mu > div:nth-child({j}) > div.css-gp2jfw > div.css-hn31yc > div.css-1a09zno > div:nth-child(2) > div.css-1rw2dq2 > div.css-zpds22 > div > div > div.css-1l31u4y > div > div > div.css-a34t1s'
                            key_selector = f'#room > div.css-g6g7mu > div:nth-child({j}) > div.css-gp2jfw > div.css-zjkjbb > div.css-1ywt6mt > div'

                            price_text = soup.select(price_selector)[0].text.strip()
                            key_text = soup.select(key_selector)[0].text.strip()

                            # 📌 가격 문자열에서 숫자만 추출 (예: "₩120,000" → "120000")
                            price_numeric = int(re.sub(r"[^\d]", "", price_text))

                            # 📌 가격 테이블에 저장
                            price_table[key_text] = price_numeric

                            # 📌 최저가 업데이트
                            min_price = min(min_price, price_numeric)

                            j += 1  # 다음 가격 항목으로 이동

                        except:
                            break  # 더 이상 가격 데이터가 없으면 종료

                    # 📌 최저가 기반 1주일 가격 계산 (최저가 * 7)
                    room['price_table'] = price_table
                    room['price'] = min_price * 7 if min_price != float('inf') else None  # 가격이 없으면 None 저장

                    # 📌 데이터 저장
                    room['url'] = driver.current_url
                    data.append(room)

                    # 📌 창 닫기 및 원래 창으로 복귀
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])
                        driver.close()
                        driver.switch_to.window(windows[0])
                        sleep(2)
                    
                    i += 1
                
                except Exception as e:
                    print(e)
                    break

            # 📌 다음 페이지 이동
            try:
                next_page = page % 10 + 2
                page += 1
                driver.find_element(By.XPATH, f'//*[@id="__next"]/div/main/section/div[2]/div/div/button[{next_page}]').click()
                sleep(3)
                
            except:
                break
        
        self.data = data
