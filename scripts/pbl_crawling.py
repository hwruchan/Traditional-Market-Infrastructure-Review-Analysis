import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
from selenium import webdriver  # 동적크롤링
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def extract_review():
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    rev = []
    # #_review_list 아래 모든 li에서 텍스트 추출
    review_list = soup.select('#_review_list > li')
    for li in review_list:
        # li 내부에서 텍스트만 추출 (공백 제거)
        text = li.get_text(separator=' ', strip=True)
        if text:
            rev.append(text)
    return rev


# 시장명 데이터 불러오기
df = pd.read_csv('C:/Users/jeongchan/iCloudDrive/iCloud~md~obsidian/obsidian/SMU/2025-1/공공빅데이터PBL/전통시장_매칭데이터.csv', encoding='utf-8-sig')
search_keywords = df[['시군구', '시장명']].dropna().apply(lambda x: f"{x['시군구']} {x['시장명']}", axis=1).tolist()
market_names = df['시장명'].dropna().tolist()

# 결과 저장용 딕셔너리
rev_dict = {}

# 크롬 옵션
options = Options()
options.add_argument('--start-maximized')
# options.add_argument('--headless')  # 필요시 주석 해제

driver = webdriver.Chrome(options=options)

for market in tqdm(search_keywords):
    rev_dict[market] = {'별점': '', '리뷰': []}  # for문 시작할 때 미리 초기화
    print(f'[{market}] 검색 중...')
    driver.get(f'https://map.naver.com/v5/search/{market}')
    time.sleep(3)
    
    # 검색 결과에서 맨 위 값 클릭
    try:
        # searchIframe 진입
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="searchIframe"]'))
        time.sleep(1)
        clicked = False
        try:
            # 첫 번째 방식 시도
            top_result = driver.find_element(By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.qbGlu > div.ouxiq > div.ApCpt > a > span.YwYLL')
            top_result.click()
            clicked = True
        except Exception as e1:
            print(f'  - 첫 번째 selector 실패, 두 번째 selector 시도: {e1}')
            try:
                # 두 번째 방식 시도
                top_li = driver.find_element(By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li:nth-child(1)')
                top_li.click()
                clicked = True
            except Exception as e2:
                print(f'  - 두 번째 selector 실패, 세 번째 selector 시도: {e2}')
                try:
                    # 세 번째 방식 시도
                    third_result = driver.find_element(By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li > div.Np1CD > div > div.SbNoJ > a > span.t3s7S')
                    third_result.click()
                    clicked = True
                except Exception as e3:
                    print(f'[{market}] 검색 결과 클릭 실패(세 selector 모두 실패): {e3}')
                    driver.switch_to.default_content()
                    continue
        if not clicked:
            driver.switch_to.default_content()
            continue
        time.sleep(2)
        driver.switch_to.default_content()
    except Exception as e:
        print(f'[{market}] 검색 결과 클릭 실패(iframe 진입 실패): {e}')
        continue
    
    try:
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="entryIframe"]')) # iframe 이동
        time.sleep(3) 
    except:
        print(f'[{market}] 검색 결과 없음')
        continue
    
    # entryIframe 진입 후
    # 별점 추출
    rating = ''
        
    try:
        # 탭 메뉴 span들 모두 찾기
        tab_spans = driver.find_elements(By.CSS_SELECTOR, 'span')
        found = False
        for span in tab_spans:
            if span.text.strip() == "리뷰":
                # 부모 a 태그가 있으면 그걸 클릭
                try:
                    parent_a = span.find_element(By.XPATH, './ancestor::a')
                    parent_a.click()
                except:
                    # a 태그가 없으면 span 자체 클릭
                    span.click()
                time.sleep(2)
                found = True
                break
        if not found:
            print('  - 리뷰탭(텍스트 기반) 없음')
    except Exception as e:
        print(f'  - 리뷰탭(텍스트 기반) 클릭 실패: {e}')


    try:
        rating_elem = driver.find_element(By.CSS_SELECTOR, 'span.xobxM.fNnpD')
        # 자식 노드 중 텍스트 노드만 추출
        rating = driver.execute_script(
        "let el=arguments[0];"
        "for(let n of el.childNodes){if(n.nodeType===3)return n.nodeValue.trim();}"
        "return '';",
        rating_elem
    )
    except Exception as e:
        print(f'  - 별점 추출 실패: {e}')
        

    rev = extract_review()
    rev_dict[market] = {'별점': rating, '리뷰': rev}  # 시장명 key로, 별점/리뷰 저장
    print({'별점': rating, '리뷰': rev})
    result_df = pd.DataFrame([
    {'시장명': k, '별점': v['별점'], '리뷰': v['리뷰']} for k, v in rev_dict.items()
])
    result_df.to_csv('review_result_naver.csv', index=False, encoding='utf-8-sig')




