import csv
from collections import defaultdict

def analyze_matching_issue():
    """매칭 문제 분석 - 왜 데이터가 늘어나는가?"""
    
    print("🔍 매칭 문제 분석")
    print("="*60)
    
    def clean_market_name(name):
        if not name:
            return ""
        import re
        name = re.sub(r'\([^)]*\)', '', name)
        name = ' '.join(name.split())
        return name.strip()

    def extract_region_from_address(address):
        if not address:
            return "", ""
        import re
        sido_pattern = r'(서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|경기도|강원도|충청북도|충청남도|전라북도|전라남도|경상북도|경상남도|제주특별자치도)'
        sido_match = re.search(sido_pattern, address)
        sido = sido_match.group(1) if sido_match else ""
        
        sigungu_pattern = r'([\w]+시|[\w]+군|[\w]+구)'
        sigungu_matches = re.findall(sigungu_pattern, address)
        
        sigungu = ""
        if sigungu_matches:
            for match in sigungu_matches:
                if sido and match in sido:
                    continue
                sigungu = match
                break
        
        return sido, sigungu

    def create_unique_market_key(market_name, sido, sigungu):
        if not market_name:
            return ""
        sido_clean = sido.strip() if sido else ""
        sigungu_clean = sigungu.strip() if sigungu else ""
        unique_key = f"{market_name}|{sido_clean}|{sigungu_clean}"
        return unique_key

    try:
        # 첫 번째 파일 읽기
        with open('소상공인시장진흥공단_전통시장현황_20240719.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header1 = next(reader)
            data1 = list(reader)

        # 두 번째 파일 읽기
        with open('전국전통시장표준데이터.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header2 = next(reader)
            data2 = list(reader)

        print(f"📁 원본 데이터:")
        print(f"   첫 번째 파일: {len(data1)}개")
        print(f"   두 번째 파일: {len(data2)}개")

        # 첫 번째 파일 처리
        file1_keys = {}
        file1_names = {}
        
        for i, row in enumerate(data1):
            if len(row) > max(1, 5, 6):
                market_name = clean_market_name(row[1])
                sido = row[5] if len(row) > 5 else ""
                sigungu = row[6] if len(row) > 6 else ""
                
                if market_name:
                    unique_key = create_unique_market_key(market_name, sido, sigungu)
                    if unique_key:
                        file1_keys[unique_key] = i + 2  # 행 번호
                        file1_names[market_name] = file1_names.get(market_name, 0) + 1

        # 두 번째 파일 처리
        file2_keys = {}
        file2_names = {}
        
        for i, row in enumerate(data2):
            if len(row) > 0:
                market_name = clean_market_name(row[0])
                
                # 주소에서 지역 정보 추출
                road_address = row[2] if len(row) > 2 else ""
                jibun_address = row[3] if len(row) > 3 else ""
                address = road_address if road_address else jibun_address
                
                sido, sigungu = extract_region_from_address(address)
                
                if market_name:
                    unique_key = create_unique_market_key(market_name, sido, sigungu)
                    if unique_key:
                        file2_keys[unique_key] = i + 2  # 행 번호
                        file2_names[market_name] = file2_names.get(market_name, 0) + 1

        print(f"\n📊 처리 결과:")
        print(f"   첫 번째 파일 고유 키: {len(file1_keys)}개")
        print(f"   두 번째 파일 고유 키: {len(file2_keys)}개")

        # 매칭 분석
        matched_keys = set(file1_keys.keys()) & set(file2_keys.keys())
        only_file1 = set(file1_keys.keys()) - set(file2_keys.keys())
        only_file2 = set(file2_keys.keys()) - set(file1_keys.keys())

        print(f"\n🔗 매칭 분석:")
        print(f"   매칭된 키: {len(matched_keys)}개")
        print(f"   첫 번째 파일만: {len(only_file1)}개")
        print(f"   두 번째 파일만: {len(only_file2)}개")
        print(f"   전체 고유 키: {len(matched_keys) + len(only_file1) + len(only_file2)}개")

        # 매칭되지 않은 키들 분석
        print(f"\n❌ 첫 번째 파일에만 있는 키 (처음 10개):")
        for i, key in enumerate(sorted(only_file1)[:10]):
            market_name = key.split('|')[0]
            print(f"   {i+1:2d}. {key}")

        print(f"\n❌ 두 번째 파일에만 있는 키 (처음 10개):")
        for i, key in enumerate(sorted(only_file2)[:10]):
            market_name = key.split('|')[0]
            print(f"   {i+1:2d}. {key}")

        # 같은 시장명이지만 다른 지역으로 인식된 경우 찾기
        print(f"\n🔍 같은 시장명의 서로 다른 키 분석:")
        
        # 첫 번째 파일에서 중복 시장명 찾기
        duplicate_names_file1 = {name: count for name, count in file1_names.items() if count > 1}
        if duplicate_names_file1:
            print(f"   첫 번째 파일 중복 시장명: {len(duplicate_names_file1)}개")
            for name, count in list(duplicate_names_file1.items())[:5]:
                print(f"     '{name}': {count}개")
                # 해당 시장명의 모든 키 찾기
                matching_keys = [key for key in file1_keys.keys() if key.startswith(name + '|')]
                for key in matching_keys[:3]:  # 처음 3개만
                    print(f"       → {key}")

        # 두 번째 파일에서 중복 시장명 찾기
        duplicate_names_file2 = {name: count for name, count in file2_names.items() if count > 1}
        if duplicate_names_file2:
            print(f"   두 번째 파일 중복 시장명: {len(duplicate_names_file2)}개")
            for name, count in list(duplicate_names_file2.items())[:5]:
                print(f"     '{name}': {count}개")
                # 해당 시장명의 모든 키 찾기
                matching_keys = [key for key in file2_keys.keys() if key.startswith(name + '|')]
                for key in matching_keys[:3]:  # 처음 3개만
                    print(f"       → {key}")

        # 지역 정보 추출 문제 확인
        print(f"\n🏠 지역 정보 추출 문제 확인:")
        
        # 빈 지역 정보가 있는 키들
        empty_region_file1 = [key for key in file1_keys.keys() if key.endswith('||')]
        empty_region_file2 = [key for key in file2_keys.keys() if key.endswith('||')]
        
        print(f"   첫 번째 파일 빈 지역 정보: {len(empty_region_file1)}개")
        print(f"   두 번째 파일 빈 지역 정보: {len(empty_region_file2)}개")
        
        if empty_region_file1:
            print(f"   첫 번째 파일 빈 지역 예시:")
            for key in empty_region_file1[:5]:
                print(f"     {key}")
                
        if empty_region_file2:
            print(f"   두 번째 파일 빈 지역 예시:")
            for key in empty_region_file2[:5]:
                print(f"     {key}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_matching_issue() 