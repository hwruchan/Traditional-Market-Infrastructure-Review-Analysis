import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tqdm import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_review():
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        rev = []
        # 리뷰 목록에서 텍스트 추출 - 정확한 선택자 사용
        review_list = soup.select('#mainContent > div.main_detail > div.detail_cont > div.section_comm.section_review > div.group_review > ul > li')
        print(f"  - 발견된 리뷰 수: {len(review_list)}")
        
        for li in review_list:
            try:
                # 정확한 리뷰 텍스트 선택자 사용
                review_text = li.select_one('div > div.area_review > div > div.review_detail > div.wrap_review > a > p')
                if review_text:
                    text = review_text.get_text(strip=True)
                    if text:
                        rev.append(text)
            except Exception as e:
                print(f"  - 개별 리뷰 추출 중 오류: {e}")
                continue
                
        return rev
    except Exception as e:
        print(f"  - 리뷰 추출 중 오류 발생: {e}")
        return []


# 시장명 데이터 불러오기
df = pd.read_csv('C:/Users/user/iCloudDrive/iCloud~md~obsidian/obsidian/SMU/2025-1/공공빅데이터PBL/전통시장_매칭데이터.csv', encoding='utf-8-sig')
# '시군구'와 '시장명'을 합쳐서 검색 키워드 생성
search_keywords = df[['시군구', '시장명']].dropna().apply(lambda x: f"{x['시군구']} {x['시장명']}", axis=1).tolist()
market_names = df['시장명'].dropna().tolist()  # 시장명 리스트는 결과 저장용으로 유지
# 결과 저장용 딕셔너리
rev_dict = {}

# 크롬 옵션
options = Options()
options.add_argument('--start-maximized')
# options.add_argument('--headless')  # 필요시 주석 해제

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)  # 최대 10초 대기

for market in tqdm(search_keywords):
    rev_dict[market] = {'별점': '', '리뷰': []}  # for문 시작할 때 미리 초기화
    print(f'\n[{market}] 검색 중...')
    
    try:
        # 카카오맵 접속
        driver.get('https://map.kakao.com/')
        time.sleep(3)
        
        # 검색창 찾기 및 검색어 입력
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#search\.keyword\.query')))
        search_box.clear()
        search_box.send_keys(market)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # 첫 번째 검색 결과 클릭 - 별점/리뷰 버튼이 있는지 확인
        try:
            first_result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#info\.search\.place\.list > li.PlaceItem.clickArea.PlaceItem-ACTIVE > div.rating.clickArea > span.score > a')))
            first_result.click()
            time.sleep(3)
            
            # 새로 열린 페이지로 전환
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)
            
            # 별점 추출
            try:
                rating_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainContent > div.main_detail > div.detail_cont > div.section_comm.section_review > div.group_total > div.head_total > span > span.num_star')))
                rating = rating_elem.text.strip()
                print(f"  - 별점: {rating}")
            except Exception as e:
                print(f"  - 별점 추출 실패: {e}")
                rating = ''
            
            # 리뷰 추출
            rev = extract_review()
            rev_dict[market] = {'별점': rating, '리뷰': rev}
            print(f"  - 저장된 리뷰 수: {len(rev)}")
            
            # 새로 열린 창 닫고 원래 창으로 돌아가기
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
        except Exception as e:
            print(f"  - 별점/리뷰 버튼이 없거나 클릭할 수 없음: {e}")
            rev_dict[market] = {'별점': '', '리뷰': []}
        
        # 중간 저장 (성공/실패 모두)
        result_df = pd.DataFrame([
            {'시장명': k, '별점': v['별점'], '리뷰': v['리뷰']} for k, v in rev_dict.items()
        ])
        result_df.to_csv('review_result_kakao.csv', index=False, encoding='utf-8-sig')
        print(f"  - 중간 저장 완료")
        
    except Exception as e:
        print(f"[{market}] 처리 중 오류 발생: {e}")
        # 오류 발생 시에도 창 전환 처리
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        continue

# 최종 결과 저장
print("\n최종 결과 저장 중...")
result_df = pd.DataFrame([
    {'시장명': k, '별점': v['별점'], '리뷰': v['리뷰']} for k, v in rev_dict.items()
])
result_df.to_csv('review_result_kakao.csv', index=False, encoding='utf-8-sig')
print("크롤링 완료!")



