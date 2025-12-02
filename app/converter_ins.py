import json
import csv
import re
from collections import Counter

# 1. JSON을 간단한 CSV로 변환
def json_to_csv():
    # JSON 파일 읽기
    with open('/mnt/user-data/uploads/all_user_media.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # CSV로 저장
    with open('/mnt/user-data/outputs/posts.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['날짜', '제목/내용', '링크'])  # 헤더
        
        for post in data:
            # 날짜 간단히 변환 (YYYY-MM-DD 형식)
            date = post['timestamp'][:10] if 'timestamp' in post else ''
            # 내용
            caption = post.get('caption', '').replace('\n', ' ').replace('\r', '')[:500]  # 500자로 제한
            # 링크
            link = post.get('permalink', '')
            
            writer.writerow([date, caption, link])
    
    print("✅ posts.csv 파일 생성 완료!")

# 2. 사용된 단어만 뽑기
def extract_words():
    # JSON 파일 읽기
    with open('scripts/all_user_media.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 모든 텍스트 합치기
    all_text = ""
    for post in data:
        caption = post.get('caption', '')
        if caption:
            all_text += caption + " "
    
    # 한국어 단어만 추출 (2글자 이상)
    korean_words = re.findall(r'[가-힣]{2,}', all_text)
    
    # 빈도 계산
    word_count = Counter(korean_words)
    
    # 결과를 간단한 CSV로 저장
    with open('scripts/words.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['단어', '횟수'])  # 헤더
        
        # 빈도 높은 순으로 저장
        for word, count in word_count.most_common():
            writer.writerow([word, count])
    
    print(f"✅ words.csv 파일 생성 완료! (총 {len(word_count)}개 단어)")
    
    # 상위 20개 단어 출력
    print("\n📊 가장 많이 사용된 단어 TOP 20:")
    for i, (word, count) in enumerate(word_count.most_common(20), 1):
        print(f"{i:2d}. {word} ({count}회)")

# 실행
if __name__ == "__main__":
    print("🚀 변환 시작...")
    json_to_csv()
    extract_words()
    print("\n✨ 모든 작업 완료!")