from argparse import ArgumentParser
from typing import Dict, Type
from crawler import ThreeThreeCrawler, YanoljaCrawler, HowBoutHereCrawler

# 모든 크롤링 클래스를 예시 형식으로 적어주세요. 
CRAWLER_CLASSES = {
    # ThreeThreeCrawler,
    # YanoljaCrawler,
    HowBoutHereCrawler
}

def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-o', '--output-dir', type=str, required=True, help="Output file directory. Example: ../../database")
    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    for crawler_class in CRAWLER_CLASSES:
        crawler = crawler_class(args.output_dir)
        crawler.scrape_reviews()
        crawler.save_to_database()