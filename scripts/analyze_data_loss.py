import csv
from collections import defaultdict

def analyze_data_loss():
    """데이터 손실 원인 분석"""
    
    print("📊 데이터 개수 변화 분석")
    print("="*50)
    
    # 원본 파일들 확인
    try:
        # 첫 번째 파일
        with open('소상공인시장진흥공단_전통시장현황_20240719.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header1 = next(reader)
            data1 = list(reader)
            
        print(f"📁 첫 번째 파일:")
        print(f"   - 헤더 제외 데이터 행 수: {len(data1)}")
        print(f"   - 총 행 수 (헤더 포함): {len(data1) + 1}")
        
        # 두 번째 파일
        with open('전국전통시장표준데이터.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header2 = next(reader)
            data2 = list(reader)
            
        print(f"📁 두 번째 파일:")
        print(f"   - 헤더 제외 데이터 행 수: {len(data2)}")
        print(f"   - 총 행 수 (헤더 포함): {len(data2) + 1}")
        
        print(f"\n🔍 시장명 정제 과정 분석:")
        
        # 시장명 정제 함수 (simple_merge.py와 동일)
        def clean_market_name(name):
            if not name:
                return ""
            import re
            name = re.sub(r'\([^)]*\)', '', name)
            name = ' '.join(name.split())
            return name.strip()
        
        # 첫 번째 파일 시장명 분석
        file1_markets = {}
        file1_empty_names = 0
        file1_duplicates = defaultdict(list)
        
        for i, row in enumerate(data1):
            if len(row) > 1:
                original_name = row[1]
                cleaned_name = clean_market_name(original_name)
                
                if not cleaned_name:
                    file1_empty_names += 1
                    print(f"   첫 번째 파일 행 {i+2}: 빈 시장명 - 원본: '{original_name}'")
                else:
                    if cleaned_name in file1_markets:
                        file1_duplicates[cleaned_name].append(i+2)
                    else:
                        file1_markets[cleaned_name] = i+2
        
        print(f"\n📈 첫 번째 파일 시장명 분석:")
        print(f"   - 전체 데이터 행: {len(data1)}")
        print(f"   - 빈 시장명: {file1_empty_names}개")
        print(f"   - 고유 시장명: {len(file1_markets)}개")
        print(f"   - 중복 시장명: {len(file1_duplicates)}개")
        
        if file1_duplicates:
            print(f"   중복 시장명 예시:")
            count = 0
            for name, rows in file1_duplicates.items():
                if count < 5:  # 처음 5개만 출력
                    print(f"     '{name}': 행 {rows}")
                    count += 1
        
        # 두 번째 파일 시장명 분석
        file2_markets = {}
        file2_empty_names = 0
        file2_duplicates = defaultdict(list)
        
        for i, row in enumerate(data2):
            if len(row) > 0:
                original_name = row[0]
                cleaned_name = clean_market_name(original_name)
                
                if not cleaned_name:
                    file2_empty_names += 1
                    print(f"   두 번째 파일 행 {i+2}: 빈 시장명 - 원본: '{original_name}'")
                else:
                    if cleaned_name in file2_markets:
                        file2_duplicates[cleaned_name].append(i+2)
                    else:
                        file2_markets[cleaned_name] = i+2
        
        print(f"\n📈 두 번째 파일 시장명 분석:")
        print(f"   - 전체 데이터 행: {len(data2)}")
        print(f"   - 빈 시장명: {file2_empty_names}개")
        print(f"   - 고유 시장명: {len(file2_markets)}개")
        print(f"   - 중복 시장명: {len(file2_duplicates)}개")
        
        if file2_duplicates:
            print(f"   중복 시장명 예시:")
            count = 0
            for name, rows in file2_duplicates.items():
                if count < 5:  # 처음 5개만 출력
                    print(f"     '{name}': 행 {rows}")
                    count += 1
        
        # 매칭 분석
        all_markets = set(file1_markets.keys()) | set(file2_markets.keys())
        matched_markets = set(file1_markets.keys()) & set(file2_markets.keys())
        only_file1 = set(file1_markets.keys()) - set(file2_markets.keys())
        only_file2 = set(file2_markets.keys()) - set(file1_markets.keys())
        
        print(f"\n🔗 매칭 분석:")
        print(f"   - 첫 번째 파일만: {len(only_file1)}개")
        print(f"   - 두 번째 파일만: {len(only_file2)}개")
        print(f"   - 두 파일 모두: {len(matched_markets)}개")
        print(f"   - 전체 고유 시장: {len(all_markets)}개")
        
        print(f"\n📊 데이터 손실 원인:")
        total_original = len(data1)
        total_after_cleaning = len(file1_markets) + len(file2_markets) - len(matched_markets)
        
        print(f"   1. 원본 데이터: {total_original}개")
        print(f"   2. 빈 시장명 제거: -{file1_empty_names + file2_empty_names}개")
        print(f"   3. 중복 시장명 제거: -{len(file1_duplicates) + len(file2_duplicates)}개")
        print(f"   4. 최종 고유 시장: {len(all_markets)}개")
        print(f"   5. 손실된 데이터: {total_original - len(all_markets)}개")
        
        # 빈 시장명이나 중복이 많은 경우 상세 분석
        if file1_empty_names > 0 or file2_empty_names > 0:
            print(f"\n⚠️  빈 시장명 상세 분석:")
            
            # 첫 번째 파일의 빈 시장명 확인
            if file1_empty_names > 0:
                print(f"   첫 번째 파일 빈 시장명 {file1_empty_names}개:")
                count = 0
                for i, row in enumerate(data1):
                    if len(row) > 1:
                        original_name = row[1]
                        cleaned_name = clean_market_name(original_name)
                        if not cleaned_name and count < 10:
                            print(f"     행 {i+2}: '{original_name}' → '{cleaned_name}'")
                            count += 1
            
            # 두 번째 파일의 빈 시장명 확인
            if file2_empty_names > 0:
                print(f"   두 번째 파일 빈 시장명 {file2_empty_names}개:")
                count = 0
                for i, row in enumerate(data2):
                    if len(row) > 0:
                        original_name = row[0]
                        cleaned_name = clean_market_name(original_name)
                        if not cleaned_name and count < 10:
                            print(f"     행 {i+2}: '{original_name}' → '{cleaned_name}'")
                            count += 1
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_data_loss() 