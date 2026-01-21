import pandas as pd
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as fm

# 경고 메시지 무시
warnings.filterwarnings('ignore')

# CSV 파일 경로
facility_file = '전통시장_매칭데이터.csv'
review_file = 'review_result_test.csv'

# 데이터 불러오기 (한글 깨짐 방지를 위해 인코딩 처리)
try:
    df_facility = pd.read_csv(facility_file, encoding='utf-8')
    df_review = pd.read_csv(review_file, encoding='utf-8')
    print("utf-8 인코딩으로 파일 로딩 성공")
except UnicodeDecodeError:
    print("utf-8 인코딩 실패, cp949로 재시도")
    try:
        df_facility = pd.read_csv(facility_file, encoding='cp949')
        df_review = pd.read_csv(review_file, encoding='cp949')
        print("cp949 인코딩으로 파일 로딩 성공")
    except Exception as e:
        print(f"파일 로딩 실패: {e}")
        exit(1)
except Exception as e:
    print(f"파일 로딩 중 오류 발생: {e}")
    exit(1)

print(f"시설 데이터: {df_facility.shape[0]}개 시장, {df_facility.shape[1]}개 컬럼")
print(f"리뷰 데이터: {df_review.shape[0]}개 시장, {df_review.shape[1]}개 컬럼")

# 시설 데이터의 중복 확인 및 제거
print(f"\n=== 시설 데이터 중복 확인 ===")
print(f"원본 시설 데이터 수: {len(df_facility)}")
print(f"고유 시장코드 수: {df_facility['시장코드'].nunique()}")

# 시장코드 중복 확인
duplicate_codes = df_facility[df_facility.duplicated(subset=['시장코드'], keep=False)]
if len(duplicate_codes) > 0:
    print(f"중복된 시장코드 발견: {len(duplicate_codes)}개")
    print("중복된 시장코드 상세:")
    print(duplicate_codes[['시장코드', '시장명', '시군구', '지번주소']].sort_values('시장코드').to_string())
    
    # 중복된 시장코드 제거 (첫 번째만 유지)
    df_facility = df_facility.drop_duplicates(subset=['시장코드'], keep='first')
    print(f"\n중복 제거 후 시설 데이터 수: {len(df_facility)}")

# --- 데이터 전처리 및 결합 ---

# 1. 시설 데이터의 '시장명' 표준화 (지역명 추가 + 고유 식별자)
# 동일한 시군구 내 같은 이름의 시장을 구분하기 위해 고유 식별자 추가
df_facility['시장명_표준'] = df_facility['시군구'] + ' ' + df_facility['시장명']

# 중복된 시장명이 있는지 확인하고 고유 식별자 추가
duplicate_mask = df_facility.duplicated(subset=['시장명_표준'], keep=False)
if duplicate_mask.any():
    print(f"중복된 시장명 발견: {duplicate_mask.sum()}개")
    
    # 중복된 시장명에 대해 시장코드를 이용한 고유 식별자 추가
    df_facility['시장명_고유'] = df_facility['시장명_표준'].copy()
    for name in df_facility[duplicate_mask]['시장명_표준'].unique():
        mask = df_facility['시장명_표준'] == name
        indices = df_facility[mask].index
        for i, idx in enumerate(indices):
            if i > 0:  # 첫 번째는 그대로 두고, 두 번째부터 식별자 추가
                df_facility.loc[idx, '시장명_고유'] = f"{name}_{df_facility.loc[idx, '시장코드']}"
else:
    df_facility['시장명_고유'] = df_facility['시장명_표준']

print(f"시설 데이터 - 표준화 전 고유 시장명 수: {df_facility['시장명'].nunique()}")
print(f"시설 데이터 - 표준화 후 고유 시장명 수: {df_facility['시장명_표준'].nunique()}")
print(f"시설 데이터 - 고유 식별자 적용 후: {df_facility['시장명_고유'].nunique()}")

# 2. '시장명'을 기준으로 두 데이터프레임 결합 (left join)
# 중복 시장명 처리: 첫 번째 시장만 리뷰 데이터와 매칭
df_facility_for_merge = df_facility.copy()

# 중복된 시장명의 경우, 두 번째부터는 매칭하지 않도록 임시 시장명 생성
if duplicate_mask.any():
    print("중복 시장명 처리: 첫 번째 시장만 리뷰 데이터와 매칭")
    df_facility_for_merge['매칭용_시장명'] = df_facility_for_merge['시장명_표준'].copy()
    
    for name in df_facility[duplicate_mask]['시장명_표준'].unique():
        mask = df_facility_for_merge['시장명_표준'] == name
        indices = df_facility_for_merge[mask].index
        for i, idx in enumerate(indices):
            if i > 0:  # 두 번째부터는 매칭되지 않도록 고유한 이름 부여
                df_facility_for_merge.loc[idx, '매칭용_시장명'] = f"{name}_UNIQUE_{idx}"
else:
    df_facility_for_merge['매칭용_시장명'] = df_facility_for_merge['시장명_표준']

# 매칭용 시장명으로 결합
df_merged = pd.merge(df_facility_for_merge, df_review, left_on='매칭용_시장명', right_on='시장명', how='left')

# 매칭 성공률 확인
total_facilities = len(df_facility)
matched_facilities = (df_merged['카카오별점'].notna() | df_merged['네이버별점'].notna()).sum()
match_rate = (matched_facilities / total_facilities) * 100
print(f"매칭 성공률: {match_rate:.1f}% ({matched_facilities}/{total_facilities})")

# 데이터 무결성 확인
print(f"원본 시설 데이터 수: {len(df_facility)}")
print(f"결합 후 데이터 수: {len(df_merged)}")
print(f"데이터 수 일치 여부: {'✅ 일치' if len(df_facility) == len(df_merged) else '❌ 불일치'}")

# 중복 시장명 처리 결과 확인
if duplicate_mask.any():
    print("\n=== 중복 시장명 처리 결과 ===")
    duplicate_results = df_merged[df_merged['시장코드'].isin(df_facility[duplicate_mask]['시장코드'])]
    print(duplicate_results[['시장코드', '시장명_x', '시장명_고유', '매칭용_시장명', '카카오별점', '네이버별점']].to_string())

# 3. 만족도 점수 생성 (카카오, 네이버 별점 평균)
# 두 별점 중 하나만 있어도 점수를 부여하고, 둘 다 있으면 평균을 계산합니다.
df_merged['종합만족도'] = df_merged[['카카오별점', '네이버별점']].mean(axis=1)

# 4. 시설 데이터(Y/N)를 숫자(1/0)로 변환
# 분석할 주요 시설 컬럼들을 선택합니다.
facility_columns = [
    '아케이드', '주차장', '공중화장실', '고객휴게실',
    '수유센터', '유아놀이방', '엘리베이터/에스컬레이터'
]

for col in facility_columns:
    if col in df_merged.columns:
        df_merged[col] = df_merged[col].apply(lambda x: 1 if x == 'Y' else 0)

# --- 결과 확인 ---

# 전처리가 완료된 데이터의 정보와 상위 5개 행을 출력
print("--- 결합 및 전처리 완료된 데이터 정보 ---")
# 분석에 사용할 주요 컬럼만 선택하여 확인
selected_columns = ['시장명_x', '종합만족도'] + facility_columns
print(df_merged[selected_columns].info())

print("\n--- 결합 및 전처리 완료된 데이터 (상위 5개) ---")
print(df_merged[selected_columns].head())

# --- 한글 폰트 설정 ---
# 시스템에 맞는 한글 폰트 경로를 설정합니다. (Windows: Malgun Gothic)
try:
    plt.rc('font', family='Malgun Gothic')
except:
    print("Malgun Gothic 폰트를 찾을 수 없습니다. 기본 폰트로 설정됩니다. 그래프의 한글이 깨질 수 있습니다.")

# --- 심층 분석 및 시각화 ---

# 분석을 위해 별점이 있는 데이터만 추출
df_analysis = df_merged.dropna(subset=['종합만족도'])
print(f"\n--- 분석 대상 시장 수: {len(df_analysis)}개 ---")

# 1. 시설-만족도 상관관계 분석 (히트맵)
# 분석할 컬럼만 선택
corr_columns = ['종합만족도'] + facility_columns
correlation_matrix = df_analysis[corr_columns].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('시설과 종합만족도의 상관관계 히트맵')
plt.savefig('correlation_heatmap.png')
print("\n'correlation_heatmap.png' 파일이 저장되었습니다.")
plt.close() # 이전 그래프 닫기

# 2. 시설 유무에 따른 만족도 비교 분석 (막대그래프)
facility_impact = []
for col in facility_columns:
    # 시설이 있는 경우와 없는 경우의 평균 만족도 계산
    mean_with = df_analysis[df_analysis[col] == 1]['종합만족도'].mean()
    mean_without = df_analysis[df_analysis[col] == 0]['종합만족도'].mean()
    facility_impact.append({
        '시설': col,
        '평균만족도': mean_with,
        '유무': '보유'
    })
    facility_impact.append({
        '시설': col,
        '평균만족도': mean_without,
        '유무': '미보유'
    })

df_impact = pd.DataFrame(facility_impact)

plt.figure(figsize=(14, 8))
sns.barplot(x='시설', y='평균만족도', hue='유무', data=df_impact)
plt.title('시설 유무에 따른 시장 평균 만족도 비교')
plt.ylabel('평균 만족도 점수')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout() # 레이아웃 최적화
plt.savefig('facility_impact_analysis.png')
print("'facility_impact_analysis.png' 파일이 저장되었습니다.")
plt.close() 