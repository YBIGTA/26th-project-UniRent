from crawler.crawler import ThreeThreeCrawler, HowBoutHereCrawler
from database.mongodb_connection import MongoDB
from app.dependencies import get_mongodb
from time import sleep

def update_func(db: MongoDB, output_dir: str = "./output", place: str = "서대문구"):
    """
    각 사이트별(단기임대, 모텔) 크롤링 후 DB 업데이트:
      - 기존 DB의 제목 목록(prev_titles)을 가져와서,
      - 새로 크롤링한 데이터 중 신규 항목(new_data)을 DB에 추가하고,
      - 기존 DB에 있었으나 크롤링 결과에 없는 항목은 삭제합니다.
    """
    # 사이트별 크롤러와 property type 매핑
    crawler_mapping = {
        "threethree": (ThreeThreeCrawler, "단기임대"),
        "howbouthere": (HowBoutHereCrawler, "모텔")
    }

    for key, (crawler_cls, prop_type) in crawler_mapping.items():
        # DB에서 해당 타입의 기존 제목 목록 조회
        prev_titles = db.get_titles_by_type(prop_type)
        
        # 해당 크롤러 실행 (제목만 가져옴)
        crawler = crawler_cls(output_dir, place)
        crawler.search_titles()
        
        # 신규 데이터 (DB에 없는 제목) 선별
        new_titles = [room["title"] for room in crawler.data if room.get("title")]
        new_data = [title for title in new_titles if title not in prev_titles]

        # 🔹 신규 항목에 대해 상세 정보 수집
        detailed_data = []
        for title in new_data:
            room_details = crawler.scrape_review_by_title(title)  # 🔥 추가된 함수
            if room_details:
                detailed_data.append(room_details)

        # 🔹 신규 항목을 DB에 추가
        if detailed_data:
            db.add_properties(detailed_data, prop_type)

        # 🔹 기존 DB에 있었으나 크롤링 결과에 없는 항목 삭제
        to_delete = list(set(prev_titles) - set(new_titles))
        if to_delete:
            db.delete_properties_by_titles(to_delete)
    
    db.close()
