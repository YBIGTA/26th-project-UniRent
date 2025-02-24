from argparse import ArgumentParser
from typing import Dict, Type
from crawler import ThreeThreeCrawler, HowBoutHereCrawler

# 모든 크롤링 클래스를 예시 형식으로 적어주세요. 
output_dir = "./data"
Three = ThreeThreeCrawler(output_dir)
How = HowBoutHereCrawler(output_dir)

CRAWLER_CLASSES = {
    Three,
    How
}



if __name__ == "__main__":

    output_dir = "./data"
    for crawler in CRAWLER_CLASSES:
        crawler.scrape_reviews()
        crawler.save_to_database()