import requests as re
from bs4 import BeautifulSoup as bs
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abc import ABC, abstractmethod
from time import sleep
import boto3
from fastapi import FastAPI, APIRouter, Depends, Query
from database.mongodb_connection import MongoDB
import shutil
import stat
import tempfile
import logging
import json
import io

class BaseCrawler(ABC):
    def __init__(self, output_dir: str, place=""):
        self.output_dir = output_dir
        self.url = ""
        self.driver = None
        self.name = None

    def remove_readonly(self, func, path, _):
        """읽기 전용 파일 삭제를 위한 권한 변경"""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def send_to_db(self, data, db: "MongoDB"):  # ✅ 문자열 타입 힌팅
        logging.info(f"MongoDB 저장 시작, 저장할 데이터 개수: {len(data)}")

        inserted_ids = []
        logging.info(data)
        for property_data in data:
            logging.info(property_data)
            try:
                if isinstance(property_data, str):  # ✅ JSON 문자열이면 변환
                    property_data = json.loads(property_data)

                if not isinstance(property_data, dict):  # ✅ 변환 실패 시 건너뜀
                    logging.error(f"MongoDB 저장 실패: 예상=dict, 실제={type(property_data)}")
                    continue

                property_id = db.add_property(property_data, self.name)
                logging.info(f"MongoDB 저장 완료: {property_id}")
                inserted_ids.append(property_id)
            except Exception as e:
                logging.error(f"MongoDB 저장 중 오류 발생: {e}", exc_info=True)

        logging.info(f"MongoDB 저장 완료, 총 {len(inserted_ids)}개 항목이 추가됨")

    def start_browser(self) -> None:
        """안전한 user-data-dir을 사용하여 Chrome 브라우저 실행"""
        # 기존 실행 중인 Chrome 프로세스 종료
        running_processes = os.popen("pgrep -f chrome").read().strip()
        if running_processes:
            os.system("pkill -f chrome")

        options = webdriver.ChromeOptions()
        options.binary_location = "/opt/chrome/chrome-linux64/chrome"  # Chrome 실행 파일 경로 설정
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36") 

        # 프로세스별 고유 user-data-dir 생성
        user_data_dir = tempfile.mkdtemp()
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir, onerror=self.remove_readonly)
        options.add_argument(f"--user-data-dir={user_data_dir}")

        # Chromedriver 경로 지정
        service = Service("/usr/local/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(1920, 1080)
        self.driver.get(self.url)
        # 초기 페이지 로드를 위해 잠깐 대기(또는 특정 요소 대기로 대체 가능)
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    @abstractmethod
    def scrape_reviews(self):
        pass

    def save_to_database(self) -> None:
        """크롤링 결과를 JSON 파일로 저장"""
        with open(os.path.join(self.output_dir, "data.json"), 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


class ThreeThreeCrawler(BaseCrawler):
    def __init__(self, output_dir, place="서대문구"):
        self.output_dir = os.path.join(output_dir, "threethree")
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = []
        self.url = 'https://33m2.co.kr/webpc/search/keyword?keyword=서대문구&start_date=&end_date=&week='
        self.place = place
        self.name = "단기임대"

    def scrape_reviews(self):
        """단기임대 사이트에서 리뷰를 스크랩"""
        self.start_browser()
        driver = self.driver
        driver.get(self.url)
        sleep(3)
        wait = WebDriverWait(driver, 10)
        # 페이지 로드 완료 대기 (예: 검색 결과 영역)
        wait.until(EC.presence_of_element_located((By.ID, "div_search_result_inner")))
        # 페이지 로드 후 소스의 일부를 로깅 (디버깅용)
        logging.info("Initial page source snapshot: %s", driver.page_source[:500])
       
        s3 = boto3.client('s3')
        bucket_name = "uni-rent-bucket"
        data = []
        page = 1
        flag = True
        while flag:
            for i in range(1, 16):
                try:
                    # 요소가 클릭 가능할 때까지 대기 후 클릭
                    link = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f'//*[@id="div_search_result_inner"]/div[2]/a[{i}]')
                    ))
                    link.click()
                    sleep(3)
                    
                    # 새 창 전환 후 타이틀 요소가 나타날 때까지 대기
                    wait.until(EC.number_of_windows_to_be(2))
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])
                    
                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong')
                    ))
                    # 새 창에서 소스의 일부를 로깅
                    logging.info("Detail page source snapshot: %s", driver.page_source[:500])
                    
                    soup = bs(driver.page_source, 'html.parser')
                    room = {}
                    # title
                    title_selector = 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong'
                    title = soup.select(title_selector)
                    room['title'] = title[0].text if title else ""
                    
                    # images
                    img_name = room['title']
                    if img_name:
                        parent_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'swiper-wrapper')))
                        images = parent_div.find_elements(By.TAG_NAME, "img")
                        for index, img in enumerate(images):
                            img_url = img.get_attribute("src")
                            if img_url:
                                img_data = re.get(img_url).content
                                sleep(2)
                                s3.upload_fileobj(
                                    io.BytesIO(img_data), bucket_name, f'{img_name}/{index}.jpg'
                                )
                    
                    # addr
                    addr_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(1) > p'
                    addr = soup.select(addr_selector)
                    room['addr'] = addr[0].text if addr else ""
                    
                    # price
                    price_table = {}
                    price_selector = 'body > div.wrap > section > div > div.room_sticky > div.room_pay > p > strong'
                    price = soup.select(price_selector)
                    price_table['1week'] = price[0].text if price else ""
                    room['price_table'] = price_table
                        
                    # options
                    options = []
                    option_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(5) > ul'
                    option = soup.select(option_selector)
                    if option:
                        for p in option[0].find_all('p', recursive=True):
                            options.append(p.text)
                    option_etc_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(6) > ul'
                    option_etc = soup.select(option_etc_selector)
                    if option_etc:
                        for p in option_etc[0].find_all('p', recursive=True):
                            options.append(p.text)
                    room['options'] = options
                    room['url'] = driver.current_url
                    data.append(room)
                    
                    # 창 닫기 및 원래 창 복귀
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        wait.until(EC.presence_of_element_located((By.ID, "div_search_result_inner")))
                        sleep(3)
                    
                except Exception as e:
                    logging.error("Exception during crawling item: %s", e, exc_info=True)
                    flag = False
                    break

            try:
                next_index = 1 if page == 1 else (11 if page % 10 == 0 else page % 10 + 1)
                page += 1
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f'//*[@id="div_search_result_inner"]/div[3]/a[{next_index}]')
                ))
                next_button.click()
                wait.until(EC.presence_of_element_located((By.ID, "div_search_result_inner")))
                sleep(3)
            except Exception as e:
                logging.error("Next page exception: %s", e, exc_info=True)
                flag = False
        self.data = data



class HowBoutHereCrawler(BaseCrawler):
    def __init__(self, output_dir: str, place="서대문구"):
        self.output_dir = os.path.join(output_dir, "howbouthere")
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = []
        self.url = (
            """https://www.yeogi.com/domestic-accommodations?
            keyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&
            autoKeyword=%EC%84%9C%EC%9A%B8+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC&
            checkIn=2025-02-22&checkOut=2025-02-23&personal=2&freeForm=false"""
        )
        self.place = place
        self.name = "모텔"

    def scrape_reviews(self):
        """모텔 사이트에서 리뷰를 스크랩"""
        self.start_browser()
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 10)
        # 메인 컨텐츠 영역 로드 대기
        wait.until(EC.presence_of_element_located((By.ID, "__next")))
        # 초기 페이지 소스 스냅샷 로깅 (디버깅용)
        logging.info("HowBoutHere - Initial page source snapshot: %s", driver.page_source[:500])
        
        s3 = boto3.client('s3')
        bucket_name = "uni-rent-bucket"
        data = []
        page = 1
        while True:
            i = 1
            while True:
                try:
                    # 각 항목 클릭 전 대기
                    link = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f'//*[@id="__next"]/div/main/section/div[2]/a[{i}]')
                    ))
                    link.click()
                    sleep(3)
                    
                    wait.until(EC.number_of_windows_to_be(2))
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])
                    
                    # 상세 페이지 로드 대기 후 소스 스냅샷 로깅
                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#overview > div.css-3fvoms > div.css-mn17j9 > div.css-hn31yc > div.css-1tn66r8 > h1')
                    ))
                    logging.info("HowBoutHere - Detail page source snapshot: %s", driver.page_source[:500])
                    
                    soup = bs(driver.page_source, 'html.parser')
                    room = {}
                    
                    title_selector = '#overview > div.css-3fvoms > div.css-mn17j9 > div.css-hn31yc > div.css-1tn66r8 > h1'
                    title = soup.select(title_selector)
                    room['title'] = title[0].text if title else ""
                    
                    # 이미지 처리
                    img_name = room['title']
                    if img_name:
                        parent_div = wait.until(EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="overview"]/article/div[1]/ul')
                        ))
                        images = parent_div.find_elements(By.TAG_NAME, "img")
                        for index, img in enumerate(images):
                            img_url = img.get_attribute("src")
                            if img_url:
                                img_data = re.get(img_url).content
                                sleep(1)
                                s3.upload_fileobj(
                                    io.BytesIO(img_data), bucket_name, f'{img_name}/{index}.jpg'
                                )
                    
                    addr_selector = '#overview > div.css-3fvoms > div.css-y3ur5y > div.css-1insk2s > a > p'
                    addr = soup.select(addr_selector)
                    room['addr'] = addr[0].text if addr else ""
                    
                    # 가격 테이블 처리
                    price_table = {}
                    j = 1
                    while True:
                        try:
                            price_selector = (f'#room > div.css-g6g7mu > div:nth-child({j}) > '
                                              'div.css-gp2jfw > div.css-hn31yc > div.css-1a09zno > '
                                              'div:nth-child(2) > div.css-1rw2dq2 > div.css-zpds22 > '
                                              'div > div > div.css-1l31u4y > div > div > div.css-a34t1s')
                            price = soup.select(price_selector)[0].text
                            key_selector = (f'#room > div.css-g6g7mu > div:nth-child({j}) > '
                                            'div.css-gp2jfw > div.css-zjkjbb > div.css-1ywt6mt > div')
                            key = soup.select(key_selector)[0].text
                            price_table[key] = price
                            j += 1
                        except Exception:
                            break
                    room['price_table'] = price_table
                    
                    # 옵션 처리
                    options = []
                    j = 1
                    while True:
                        try:
                            option_selector = (f'#__next > div > main > section.css-g9w49m > '
                                               f'div.css-2nct5r > div.css-1nuurnu > div.css-1kglajm > '
                                               f'div:nth-child({j}) > div > span')
                            option = soup.select(option_selector)[0].text
                            options.append(option)
                            j += 1
                        except Exception:
                            break
                    room['options'] = options
                    room['url'] = driver.current_url
                    data.append(room)
                    
                    # 창 닫기 및 원래 창 복귀
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        wait.until(EC.presence_of_element_located((By.ID, "__next")))
                        sleep(3)
                    i += 1
                
                except Exception as e:
                    logging.error("Exception during motel crawling: %s", e, exc_info=True)
                    break

            try:
                next_index = page % 10 + 2
                page += 1
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f'//*[@id="__next"]/div/main/section/div[2]/div/div/button[{next_index}]')
                ))
                next_button.click()
                wait.until(EC.presence_of_element_located((By.ID, "__next")))
                sleep(3)
            except Exception as e:
                logging.error("Next page exception (motel): %s", e, exc_info=True)
                break
        self.data = data

