import csv

def check_fire_detector_and_phone():
    """화재감지기와 전화번호 컬럼 확인"""
    
    # 첫 번째 파일 확인
    print("=== 첫 번째 파일 (소상공인시장진흥공단) ===")
    try:
        with open('소상공인시장진흥공단_전통시장현황_20240719.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header1 = next(reader)
            
            print(f"총 컬럼 수: {len(header1)}")
            print("\n모든 컬럼:")
            for i, col in enumerate(header1):
                print(f"  {i:2d}: {col}")
            
            # 화재감지기 관련 컬럼 찾기
            fire_detector_cols = []
            for i, col in enumerate(header1):
                if '화재' in col or '감지' in col:
                    fire_detector_cols.append((i, col))
            
            print(f"\n화재/감지 관련 컬럼:")
            for idx, col in fire_detector_cols:
                print(f"  인덱스 {idx}: {col}")
            
            # 전화번호 관련 컬럼 찾기
            phone_cols = []
            for i, col in enumerate(header1):
                if '전화' in col:
                    phone_cols.append((i, col))
            
            print(f"\n전화번호 관련 컬럼:")
            for idx, col in phone_cols:
                print(f"  인덱스 {idx}: {col}")
            
            # 첫 번째 데이터 행 확인
            first_row = next(reader)
            print(f"\n첫 번째 데이터 행 (총 {len(first_row)}개 값):")
            
            # 화재감지기 데이터 확인
            if fire_detector_cols:
                for idx, col in fire_detector_cols:
                    value = first_row[idx] if len(first_row) > idx else "없음"
                    print(f"  {col} (인덱스 {idx}): '{value}'")
            
            # 전화번호 데이터 확인
            if phone_cols:
                for idx, col in phone_cols:
                    value = first_row[idx] if len(first_row) > idx else "없음"
                    print(f"  {col} (인덱스 {idx}): '{value}'")
                    
    except Exception as e:
        print(f"첫 번째 파일 읽기 오류: {e}")
    
    print("\n" + "="*50)
    
    # 두 번째 파일 확인
    print("=== 두 번째 파일 (전국전통시장표준데이터) ===")
    try:
        with open('전국전통시장표준데이터.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header2 = next(reader)
            
            print(f"총 컬럼 수: {len(header2)}")
            print("\n모든 컬럼:")
            for i, col in enumerate(header2):
                print(f"  {i:2d}: {col}")
            
            # 전화번호 관련 컬럼 찾기
            phone_cols = []
            for i, col in enumerate(header2):
                if '전화' in col:
                    phone_cols.append((i, col))
            
            print(f"\n전화번호 관련 컬럼:")
            for idx, col in phone_cols:
                print(f"  인덱스 {idx}: {col}")
            
            # 첫 번째 데이터 행 확인
            first_row = next(reader)
            print(f"\n첫 번째 데이터 행 (총 {len(first_row)}개 값):")
            
            # 전화번호 데이터 확인
            if phone_cols:
                for idx, col in phone_cols:
                    value = first_row[idx] if len(first_row) > idx else "없음"
                    print(f"  {col} (인덱스 {idx}): '{value}'")
                    
    except Exception as e:
        print(f"두 번째 파일 읽기 오류: {e}")

if __name__ == "__main__":
    check_fire_detector_and_phone() 