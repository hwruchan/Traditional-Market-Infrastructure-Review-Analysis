import csv

def debug_region_columns():
    """두 번째 파일의 지역 정보 컬럼 확인"""
    
    print("=== 두 번째 파일 지역 정보 컬럼 확인 ===")
    
    try:
        with open('전국전통시장표준데이터.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            print(f"총 컬럼 수: {len(header)}")
            print("\n모든 컬럼:")
            for i, col in enumerate(header):
                print(f"  {i:2d}: {col}")
            
            # 지역 관련 컬럼 찾기
            region_cols = []
            for i, col in enumerate(header):
                if any(keyword in col for keyword in ['시도', '시군구', '지역', '도', '시', '군', '구']):
                    region_cols.append((i, col))
            
            print(f"\n지역 관련 컬럼:")
            for idx, col in region_cols:
                print(f"  인덱스 {idx}: {col}")
            
            # 첫 번째 데이터 행 확인
            first_row = next(reader)
            print(f"\n첫 번째 데이터 행:")
            for i, val in enumerate(first_row):
                if i < 18:  # 모든 컬럼 출력
                    print(f"  {i:2d}: '{val}'")
            
            # 지역 정보가 있는 컬럼들의 데이터 확인
            if region_cols:
                print(f"\n지역 관련 데이터:")
                for idx, col in region_cols:
                    value = first_row[idx] if len(first_row) > idx else "없음"
                    print(f"  {col} (인덱스 {idx}): '{value}'")
                    
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    debug_region_columns() 