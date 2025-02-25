import requests
import re 
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
from dotenv import load_dotenv

load_dotenv()
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
aws_bucket_name = os.getenv("AWS_S3_BUCKET_NAME")

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

                        # 📌 2️⃣ 이미지 크롤링 및 S3 업로드
                        try:
                            s3 = boto3.client(
                                's3', aws_access_key_id=aws_access_key,
                                aws_secret_access_key=aws_secret_key,
                                region_name=aws_region,
                            )
                            bucket_name = "uni-rent-bucket"
                            img_name = room_data['title']
                            if img_name:
                                parent_div = driver.find_element(By.CLASS_NAME, 'swiper-wrapper')
                                images = parent_div.find_elements(By.TAG_NAME, "img")
                                for idx, img in enumerate(images):
                                    img_url = img.get_attribute("src")
                                    if img_url:
                                        try:
                                            img_response = requests.get(img_url)
                                            if img_response.status_code == 200:
                                                img_data = img_response.content
                                                sleep(2)
                                                s3.upload_fileobj(
                                                    io.BytesIO(img_data), bucket_name, f'{img_name}/{idx}.jpg'
                                                )
                                                print(f"✅ S3 업로드 완료: {img_url}")
                                        except Exception as e:
                                            print(f"❌ S3 업로드 실패: {img_url}, 오류: {e}")
                        except Exception as e:
                            print(f"❌ Swiper 이미지 크롤링 오류: {e}")

                        # 📌 3️⃣ 주소 크롤링
                        addr_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(1) > p'
                        addr = soup.select_one(addr_selector)
                        room_data['addr'] = addr.text.strip() if addr else ""

                        # 📌 4️⃣ 가격 크롤링
                        price_selector = 'body > div.wrap > section > div > div.room_sticky > div.room_pay > p > strong'
                        price = soup.select_one(price_selector)
                        room_data['price'] = price.text.strip() if price else ""

                        # 📌 5️⃣ 옵션 크롤링
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

                        # 📌 6️⃣ 방 상세 페이지 URL 저장
                        room_data['url'] = driver.current_url
                        data.append(room_data)

                        # ✅ 창 닫기 및 원래 창으로 복귀
                        driver.close()
                        driver.switch_to.window(windows[0])
                        sleep(2)

                    except Exception as e:
                        print(f"❌ 방 크롤링 오류: {e}")

                # 📌 7️⃣ 다음 페이지로 이동
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


    def search_titles(self):
        """매물 목록에서 타이틀(title)만 수집 (방 목록 클릭 방식)"""
        self.start_browser()
        driver = self.driver
        driver.get(self.url)
        sleep(3)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "div_search_result_inner")))
        
        data = []
        flag = True

        while flag:
            try:
                # 📌 현재 페이지에서 방 목록 가져오기
                room_elements = driver.find_elements(By.CLASS_NAME, "room_item")
                for room in room_elements:
                    try:
                        # ✅ 방 클릭
                        room.find_element(By.XPATH, "./ancestor::a").click()
                        sleep(3)
                        
                        # ✅ 새 창으로 이동
                        windows = driver.window_handles
                        if len(windows) > 1:
                            driver.switch_to.window(windows[1])
                        
                        # ✅ 상세 페이지에서 제목 요소 로드 대기 후 HTML 파싱
                        wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong')
                        ))
                        soup = bs(driver.page_source, 'html.parser')
                        title_selector = 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong'
                        title_elem = soup.select_one(title_selector)
                        title_text = title_elem.text.strip() if title_elem else ""
                        data.append({"title": title_text})
                        logging.info(f"Collected title: {title_text}")
                        
                        # ✅ 창 닫기 및 원래 창으로 복귀
                        driver.close()
                        driver.switch_to.window(windows[0])
                        sleep(2)
                        
                    except Exception as e:
                        logging.error("Exception during room title extraction: %s", e, exc_info=True)
                        if len(driver.window_handles) > 1:
                            driver.switch_to.window(driver.window_handles[1])
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                # 📌 다음 페이지로 이동
                try:
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'next'))
                    )
                    next_page_button.click()
                    sleep(3)
                except Exception as e:
                    logging.error("Next page exception: %s", e, exc_info=True)
                    flag = False
                    
            except Exception as e:
                logging.error("Exception during room listing extraction: %s", e, exc_info=True)
                flag = False

        self.data = data
        driver.quit()

    def scrape_review_by_title(self, target_title):
        """
        주어진 제목(target_title)과 일치하는 방의 상세 정보를 스크랩하여
        {title, addr, price, options, url, region, type} 형식의 딕셔너리로 반환.
        """
        # 브라우저 시작 및 초기 페이지 로드
        self.start_browser()
        driver = self.driver
        driver.get(self.url)
        sleep(3)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "div_search_result_inner")))
        
        room_data = None
        found = False
        flag = True
        
        while flag and not found:
            # 현재 페이지에서 방 목록 가져오기
            room_elements = driver.find_elements(By.CLASS_NAME, "room_item")
            for room in room_elements:
                try:
                    # 방 목록에서 해당 항목 클릭
                    room.find_element(By.XPATH, "./ancestor::a").click()
                    sleep(3)
                    
                    # 새 창(상세 페이지)로 전환
                    windows = driver.window_handles
                    if len(windows) > 1:
                        driver.switch_to.window(windows[1])
                    
                    # 상세 페이지의 타이틀 요소 로드 대기
                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong')
                    ))
                    soup = bs(driver.page_source, 'html.parser')
                    title_selector = 'body > div.wrap > section > div > div.room_detail > div.room_info > div.title > strong'
                    title_elem = soup.select_one(title_selector)
                    detail_title = title_elem.text.strip() if title_elem else ""
                    
                    # 입력한 제목과 일치하는지 확인
                    if detail_title == target_title:
                        room_data = {}
                        room_data['title'] = detail_title
                        
                        # 주소 추출
                        addr_selector = 'body > div.wrap > section > div > div.room_detail > div:nth-child(1) > p'
                        addr_elem = soup.select_one(addr_selector)
                        room_data['addr'] = addr_elem.text.strip() if addr_elem else ""
                        
                        # 가격 추출
                        price_selector = 'body > div.wrap > section > div > div.room_sticky > div.room_pay > p > strong'
                        price_elem = soup.select_one(price_selector)
                        room_data['price'] = price_elem.text.strip() if price_elem else ""
                        
                        # 옵션 추출 (두 영역 통합)
                        options = []
                        option_selectors = [
                            'body > div.wrap > section > div > div.room_detail > div:nth-child(5) > ul',
                            'body > div.wrap > section > div > div.room_detail > div:nth-child(6) > ul'
                        ]
                        for selector in option_selectors:
                            option_elem = soup.select_one(selector)
                            if option_elem:
                                options.extend([p.text.strip() for p in option_elem.find_all('p')])
                        room_data['options'] = options
                        
                        # 상세 페이지 URL 저장
                        room_data['url'] = driver.current_url
                        # region 및 type 추가 (클래스 초기화 시 입력한 값 사용)
                        def extract_region(addr: str) -> str:
                            """
                            📌 주소(addr)에서 동(洞) 단위 지역명을 추출하는 함수
                            예: "서울특별시 서대문구 홍제동 00번지" -> "홍제동"
                            """
                            match = re.search(r'([가-힣]+동)', addr)
                            return match.group(1) if match else "알 수 없음"  # 동 이름이 없으면 "알 수 없음" 반환

                        # 📌 1️⃣ 'region' 필드 자동 추가 (addr에서 동(洞) 추출)
                        room["region"] = extract_region(room.get("addr", ""))
                        room_data['type'] = self.name
                        
                        found = True
                        # 상세 페이지 창 닫고 목록 창으로 복귀
                        driver.close()
                        driver.switch_to.window(windows[0])
                        break
                    else:
                        # 일치하지 않으면 상세 페이지 창 닫고 목록 창으로 돌아감
                        driver.close()
                        driver.switch_to.window(windows[0])
                        sleep(1)
                except Exception as e:
                    print(f"Error processing a room: {e}")
                    # 오류 발생 시, 열린 창이 있다면 닫고 원래 창으로 복귀
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
            
            # 현재 페이지에서 찾지 못했으면 다음 페이지로 이동 시도
            if not found:
                try:
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'next'))
                    )
                    next_page_button.click()
                    sleep(3)
                    wait.until(EC.presence_of_element_located((By.ID, "div_search_result_inner")))
                except Exception as e:
                    print("No more pages or error navigating to next page:", e)
                    flag = False
        
        driver.quit()
        return room_data
    
    def delete_properties_by_titles(self, titles) -> int:
        """
        주어진 제목 리스트에 포함된 모든 매물을 MongoDB 컬렉션에서 삭제합니다.
        
        :param titles: 삭제할 매물 제목들의 리스트
        :return: 삭제된 문서 개수
        """
        if not titles:
            return 0

        result = self.properties.delete_many({"title": {"$in": titles}})
        return result.deleted_count





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
        
        s3 = boto3.client(
            's3', aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
            )
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

