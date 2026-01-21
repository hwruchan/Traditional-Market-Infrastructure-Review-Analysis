import csv
import re

def test_address_extraction():
    """주소에서 지역 정보 추출 테스트"""
    
    print("🏠 주소에서 지역 정보 추출 테스트")
    print("="*50)
    
    def extract_region_from_address(address):
        if not address:
            return "", ""
        
        # 시도 추출 (서울특별시, 부산광역시, 경기도 등)
        sido_pattern = r'(서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|경기도|강원도|충청북도|충청남도|전라북도|전라남도|경상북도|경상남도|제주특별자치도)'
        sido_match = re.search(sido_pattern, address)
        sido = sido_match.group(1) if sido_match else ""
        
        # 시군구 추출
        sigungu_pattern = r'([\w]+시|[\w]+군|[\w]+구)'
        sigungu_matches = re.findall(sigungu_pattern, address)
        
        # 시도 다음에 오는 첫 번째 시군구를 선택
        sigungu = ""
        if sigungu_matches:
            for match in sigungu_matches:
                # 시도명에 포함된 '시'는 제외
                if sido and match in sido:
                    continue
                sigungu = match
                break
        
        return sido, sigungu
    
    try:
        # 두 번째 파일에서 주소 샘플 확인
        with open('전국전통시장표준데이터.csv', 'r', encoding='cp949', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            
            print(f"📋 헤더:")
            for i, col in enumerate(header):
                if i in [0, 2, 3]:  # 시장명, 도로명주소, 지번주소
                    print(f"   {i}: {col}")
            
            print(f"\n🔍 주소 추출 테스트 (처음 10개):")
            
            for i, row in enumerate(reader):
                if i >= 10:  # 처음 10개만
                    break
                    
                market_name = row[0] if len(row) > 0 else ""
                road_address = row[2] if len(row) > 2 else ""
                jibun_address = row[3] if len(row) > 3 else ""
                address = road_address if road_address else jibun_address
                
                sido, sigungu = extract_region_from_address(address)
                
                print(f"\n   {i+1:2d}. 시장명: {market_name}")
                print(f"       도로명주소: {road_address}")
                print(f"       지번주소: {jibun_address}")
                print(f"       사용주소: {address}")
                print(f"       추출결과: 시도='{sido}', 시군구='{sigungu}'")
                
                if not sido:
                    print(f"       ⚠️  시도 추출 실패!")
                    
        # 특별한 경우들 테스트
        print(f"\n🧪 특별 케이스 테스트:")
        test_addresses = [
            "충청북도 청주시 상당구 남사로 89번길 61",
            "강원도 고성군 간성읍 간성로 17",
            "전라북도 임실군 임실읍 호국로 1630",
            "서울특별시 중구 을지로 지하 1",
            "부산광역시 사하구 낙동대로 550번길 37"
        ]
        
        for addr in test_addresses:
            sido, sigungu = extract_region_from_address(addr)
            print(f"   주소: {addr}")
            print(f"   결과: 시도='{sido}', 시군구='{sigungu}'")
            print()
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_address_extraction() 