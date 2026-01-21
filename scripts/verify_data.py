import csv

def verify_merged_data():
    """생성된 합병 데이터의 화재감지기와 전화번호 확인"""
    
    filename = '전통시장_수정합병데이터.csv'
    
    try:
        with open(filename, 'r', encoding='utf-8-sig', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            print(f"=== {filename} 검증 ===")
            print(f"총 컬럼 수: {len(header)}")
            
            # 화재감지기와 전화번호 컬럼 위치 찾기
            fire_detector_idx = -1
            phone_idx = -1
            
            for i, col in enumerate(header):
                if '화재감지기' in col:
                    fire_detector_idx = i
                    print(f"화재감지기 컬럼: 인덱스 {i} - {col}")
                if '전화번호' in col:
                    phone_idx = i
                    print(f"전화번호 컬럼: 인덱스 {i} - {col}")
            
            # 데이터 검증
            fire_detector_count = 0
            phone_count = 0
            total_count = 0
            
            print(f"\n처음 10개 시장 데이터:")
            for i, row in enumerate(reader):
                total_count += 1
                if i >= 10:  # 처음 10개만 확인
                    break
                
                market_name = row[1] if len(row) > 1 else "이름없음"
                
                # 화재감지기 데이터
                fire_value = ""
                if fire_detector_idx >= 0 and len(row) > fire_detector_idx:
                    fire_value = row[fire_detector_idx]
                    if fire_value and fire_value.strip():
                        fire_detector_count += 1
                
                # 전화번호 데이터
                phone_value = ""
                if phone_idx >= 0 and len(row) > phone_idx:
                    phone_value = row[phone_idx]
                    if phone_value and phone_value.strip():
                        phone_count += 1
                
                print(f"  {i+1:2d}. {market_name[:20]:20s} | 화재감지기: '{fire_value}' | 전화번호: '{phone_value}'")
            
            # 전체 데이터 통계
            file.seek(0)
            reader = csv.reader(file)
            next(reader)  # 헤더 스킵
            
            total_fire_count = 0
            total_phone_count = 0
            total_rows = 0
            
            for row in reader:
                total_rows += 1
                
                # 화재감지기 데이터 카운트
                if fire_detector_idx >= 0 and len(row) > fire_detector_idx:
                    fire_value = row[fire_detector_idx]
                    if fire_value and fire_value.strip():
                        total_fire_count += 1
                
                # 전화번호 데이터 카운트
                if phone_idx >= 0 and len(row) > phone_idx:
                    phone_value = row[phone_idx]
                    if phone_value and phone_value.strip():
                        total_phone_count += 1
            
            print(f"\n📊 전체 데이터 통계:")
            print(f"   - 총 시장 수: {total_rows}")
            print(f"   - 화재감지기 데이터 있는 시장: {total_fire_count}개 ({total_fire_count/total_rows*100:.1f}%)")
            print(f"   - 전화번호 데이터 있는 시장: {total_phone_count}개 ({total_phone_count/total_rows*100:.1f}%)")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    verify_merged_data() 