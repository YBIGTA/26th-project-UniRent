import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd 
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from time import sleep


class BaseCrawler(ABC):
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    @abstractmethod
    def start_browser(self):
        pass

    @abstractmethod
    def scrape_reviews(self):
        pass

    @abstractmethod
    def save_to_database(self):
        pass

class ThreeThreeCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.output_dir = os.path.join(output_dir, "threethree.json")
        self.data = []
        self.driver:webdriver.Chrome = webdriver.Chrome()
        self.url = f"https://33m2.co.kr/webpc/search/keyword?keyword=서대문구&start_date=2025-02-12&end_date=2025-02-18&week=1"

    def start_browser(self) -> None:
        '''start chrome browser'''
        driver:webdriver.Chrome = self.driver
        driver.maximize_window()
        driver.get(self.url)
        sleep(3)

    def scrape_reviews(self):
        """Scrape reviews from the specified URL."""
        self.start_browser()
        driver = self.driver
        url = self.url
        
        driver.get(url)
        sleep(3)
        
        # # 리뷰 더보기로 이동
        # more_btn=browser.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]')
        # more_btn.click()
        # sleep(3)
        
        # # div태그 스크롤 
        # js_scripts = '''
        # let aa = document.getElementsByClassName('section-scrollbox')[0];
        # aa.scrollBy(0,10000);
        # '''
        # browser.execute_script(js_scripts)
        # sleep(3) 
        
        data = []
        main_window = driver.current_window_handle
        for i in range(1, 3):
            html = driver.page_source
            soup = bs(html, 'html.parser')

            for i in range(1, 16):
                room = {} 
                driver.find_element(By.XPATH, f'//*[@id="div_search_result_inner"]/div[2]/a[{i}]').click()
                sleep(2)

                title_selector = f'body > div.wrap > section > div > div.room_detail > div:nth-child(1) > div.title > strong'
                title = soup.select(title_selector)
                if title:
                    room['title'] = title[0].text
                else:
                    room['title'] = ""
                
                addr_selector = f'body > div.wrap > section > div > div.room_detail > div:nth-child(1) > p'
                addr = soup.select(addr_selector)
                if addr:
                    room['addr'] = addr[0].text
                else:
                    room['addr'] = ""
                    
                price_table_selector = f'body > div.wrap > section > div > div.room_detail > div:nth-child(9) > table > tbody > tr'
                rent_fee_selector = f'{price_table_selector} > td:nth-child(1)'
                rent_fee = soup.select(rent_fee_selector)
                if rent_fee:
                    room['rent_fee'] = rent_fee[0].text
                else:
                    room['rent_fee'] = ""
                
                maintenece_fee_selector = f'{price_table_selector} > td:nth-child(2)'
                maintenece_fee = soup.select(maintenece_fee_selector)
                if maintenece_fee:
                    room['maintenece_fee'] = maintenece_fee[0].text
                else:
                    room['maintenece_fee'] = ""
                
                cleaning_fee_selector = f'{price_table_selector} > td:nth-child(3)'
                cleaning_fee = soup.select(cleaning_fee_selector)
                if cleaning_fee:
                    room['cleaning_fee'] = cleaning_fee[0].text
                else:
                    room['cleaning_fee'] = ""
                
                deposit_selector = f'{price_table_selector} > td:nth-child(4)'
                deposit = soup.select(deposit_selector)
                if deposit:
                    room['deposit'] = deposit[0].text
                else:
                    room['deposit'] = ""
                
                # driver.close()
                driver.switch_to.window(main_window)
                

        
        self.data = data
                
    def save_to_database(self) -> None:
        """Save reviews."""
        with open(self.output_dir, 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def close_browser(self) -> None:
        """Close the Selenium WebDriver."""
        if self.browser:
            self.browser.quit()
            self.browser = None
