from argparse import ArgumentParser
from typing import Dict, Type
from crawler import ThreeThreeCrawler, YanoljaCrawler, HowBoutHereCrawler

# 모든 크롤링 클래스를 예시 형식으로 적어주세요. 
CRAWLER_CLASSES = {
    ThreeThreeCrawler,
    YanoljaCrawler,
    HowBoutHereCrawler
}


if __name__ == "__main__":

    output_dir = "./data"
    for crawler_class in CRAWLER_CLASSES:
        crawler = crawler_class(output_dir)
        crawler.scrape_reviews()
        crawler.save_to_database()