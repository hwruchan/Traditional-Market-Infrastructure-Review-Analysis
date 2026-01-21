import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def extract_review():
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    rev = []
    review_list = soup.select('#_review_list > li')
    for li in review_list:
        try:
            review_text = li.select_one('div.pui__vn15t2 > a:nth-child(1)')
            if review_text:
                text = review_text.get_text(strip=True)
                if text:
                    rev.append(text)
        except:
            continue
    return rev


def save_results(rev_dict, filename='review_result_naver.csv'):
    result_df = pd.DataFrame([
        {'시장명': k, '별점': v['별점'], '리뷰': v['리뷰']} for k, v in rev_dict.items()
    ])
    result_df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f'결과가 {filename}에 저장되었습니다.')


# 시장명 데이터 불러오기
df = pd.read_csv('C:/Users/user/iCloudDrive/iCloud~md~obsidian/obsidian/SMU/2025-1/공공빅데이터PBL/전통시장_매칭데이터.csv', encoding='utf-8-sig')
search_keywords = df[['시군구', '시장명']].dropna().apply(lambda x: f"{x['시군구']} {x['시장명']}", axis=1).tolist()
market_names = df['시장명'].dropna().tolist()
rev_dict = {}

# 크롬 옵션
options = Options()
options.add_argument('--start-maximized')
# options.add_argument('--headless')  # 필요시 주석 해제

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)  # 최대 10초 대기

# 중간 저장 간격 설정 (10개 시장마다 저장)
save_interval = 10
processed_count = 0

try:
    for market in tqdm(search_keywords):
        rev_dict[market] = {'별점': '', '리뷰': []}
        print(f'[{market}] 검색 중...')
        driver.get(f'https://map.naver.com/v5/search/{market}')
        time.sleep(3)
        
        try:
            # 검색창에 검색어 입력
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#input_search1749860435540')))
            search_input.clear()
            search_input.send_keys(market)
            search_input.send_keys(Keys.ENTER)
            time.sleep(3)  # 검색 결과 로딩 대기
            
            # iframe으로 전환
            driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '#searchIframe'))
            time.sleep(2)
            
            # 첫 번째 검색 결과 클릭
            try:
                first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.qbGlu > div.ouxiq > div.ApCpt > a')))
                first_result.click()
                time.sleep(2)
            except Exception as e:
                print(f'  - 첫 번째 검색 결과 클릭 실패: {e}')
                driver.switch_to.default_content()
                continue
            
            # 기본 프레임으로 돌아가기
            driver.switch_to.default_content()
            time.sleep(2)
            
            # 별점 추출
            try:
                rating_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#app-root > div > div > div > div.place_section.no_margin.OP4V8 > div.zD5Nm.undefined > div.dAsGb > span.PXMot.LXIwF')))
                rating = rating_elem.text.strip()
            except:
                rating = ''
                print(f'  - 별점 없음')
            
            # 리뷰 탭 클릭
            try:
                review_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#app-root > div > div > div > div.place_fixed_maintab > div > div > div > div > a:nth-child(2)')))
                review_tab.click()
                time.sleep(2)
                
                # 리뷰 추출
                rev = extract_review()
            except:
                rev = []
                print(f'  - 리뷰 없음')
            
            rev_dict[market] = {'별점': rating, '리뷰': rev}
            print({'별점': rating, '리뷰': rev})
            
            # 중간 저장
            processed_count += 1
            if processed_count % save_interval == 0:
                save_results(rev_dict, f'review_result_naver_intermediate_{processed_count}.csv')
            
        except Exception as e:
            print(f'[{market}] 처리 중 오류 발생: {e}')
            continue

finally:
    # 최종 결과 저장
    save_results(rev_dict, 'review_result_naver.csv')
    driver.quit()



