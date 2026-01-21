import pandas as pd
import numpy as np
from ast import literal_eval
import google.generativeai as genai

# Gemini API 키 입력 (여기에 본인의 키를 입력하세요)
genai.configure(api_key="AIzaSyA0Zqg3n82JEFP3E2Iw6r8hlJWJgsqiUpc")

# 이미지에서 추출한 키워드 리스트
KEYWORDS = [
    '아케이드', '엘리베이터', '고객지원', '선스프링클러', '화재감지기', '유아놀이방', '종합콜센터', '고객휴게실',
    '수유센터', '물품보관함', '자전거보관', '체육시설', '간이도서관', '쇼핑카트', '외국인안내', '고객동선',
    '방송센터', '문화교실', '공동물류', '침시장전용교육장', '회의실', '자동심장충격기', '공중화장실', '주차장'
]

def extract_reviews(val):
    try:
        if pd.isna(val) or val == '':
            return []
        return literal_eval(val)
    except:
        return []

def gemini_extract_keywords(review_text, keywords):
    prompt = (
        f"아래 리뷰에서 다음 키워드(시설/서비스)가 의미적으로 언급되었는지 분석해서, "
        f"해당되는 키워드만 콤마로 나열해줘. 키워드: {', '.join(keywords)}\n"
        f"리뷰:\n{review_text}\n"
        f"정답 예시: 엘리베이터,주차장"
    )
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    response = model.generate_content(prompt)
    return response.text.strip()

# 파일 경로는 환경에 맞게 수정하세요
df = pd.read_csv('C:/Users/jeongchan/iCloudDrive/iCloud~md~obsidian/obsidian/SMU/2025-1/PBL/review_result_test.csv', encoding='utf-8')

result = []
for idx, row in df.iterrows():
    market = row['시장명']
    kakao_reviews = extract_reviews(row.get('카카오리뷰', ''))
    naver_reviews = extract_reviews(row.get('네이버리뷰', ''))
    all_reviews = ' '.join(kakao_reviews + naver_reviews)
    keywords = gemini_extract_keywords(all_reviews, KEYWORDS)
    # 별점 평균
    kakao_score = row.get('카카오별점', '')
    naver_score = row.get('네이버별점', '')
    scores = [float(s) for s in [kakao_score, naver_score] if str(s).replace('.', '', 1).isdigit()]
    avg_score = round(np.mean(scores), 2) if scores else ''
    result.append({'시장명': market, '평균별점': avg_score, '키워드': keywords})

result_df = pd.DataFrame(result)
result_df.to_csv('review_keyword.csv', index=False, encoding='utf-8-sig')
