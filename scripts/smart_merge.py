import csv
import re
from collections import defaultdict

def read_csv_with_encoding(filename, encodings=['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']):
    """다양한 인코딩으로 CSV 파일을 읽어보는 함수"""
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding, newline='') as file:
                reader = csv.reader(file)
                data = list(reader)
                print(f"✅ {filename} 파일을 {encoding} 인코딩으로 성공적으로 읽었습니다.")
                return data, encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    raise Exception(f"파일 {filename}을 읽을 수 없습니다. 지원하는 인코딩: {encodings}")

def clean_market_name(name):
    """시장명 정제 함수"""
    if not name:
        return ""
    
    # 특수 예외 처리: '운수대통! 생거진천전통시장' → '운수대통 생거진천전통시장'
    if '운수대통!' in name and '생거진천전통시장' in name:
        name = name.replace('운수대통!', '운수대통')
    
    # 괄호와 그 안의 내용 제거
    name = re.sub(r'\([^)]*\)', '', name)
    
    # 공백 정리
    name = ' '.join(name.split())
    
    return name.strip()

def standardize_region(address):
    """지역명 표준화 - 강원특별자치도 → 강원도, 전북특별자치도 → 전라북도"""
    if not address:
        return address
    
    # 지역명 표준화
    address = address.replace('강원특별자치도', '강원도')
    address = address.replace('전북특별자치도', '전라북도')
    
    return address

def normalize_address(address):
    """주소 정규화 - 비교를 위한 주소 정제"""
    if not address:
        return ""
    
    # 지역명 표준화
    address = standardize_region(address)
    
    # 공백 정리 및 소문자 변환
    address = re.sub(r'\s+', ' ', address).strip()
    
    # 특수문자 제거 (비교용)
    address = re.sub(r'[^\w\s가-힣]', '', address)
    
    return address

def extract_key_address_parts(address):
    """주소에서 핵심 부분 추출 (시군구 + 동/읍/면)"""
    if not address:
        return ""
    
    # 시군구와 동/읍/면 패턴 찾기
    pattern = r'([\w]+시|[\w]+군|[\w]+구)\s*([\w]+동|[\w]+읍|[\w]+면)'
    match = re.search(pattern, address)
    
    if match:
        return f"{match.group(1)} {match.group(2)}"
    
    # 시군구만 있는 경우
    sigungu_pattern = r'([\w]+시|[\w]+군|[\w]+구)'
    match = re.search(sigungu_pattern, address)
    if match:
        return match.group(1)
    
    return ""

def create_final_header():
    """최종 헤더 생성"""
    
    # 기본 정보 컬럼들
    basic_columns = [
        '시장코드',
        '시장명',
        '지번주소',
        '도로명주소',
        '시도',
        '시군구',
        '시장개설주기',
        '점포수',
        '개설연도',
        '취급품목'
    ]
    
    # 첫 번째 파일의 시설 보유여부 컬럼들
    facility_columns_file1 = [
        '아케이드',
        '엘리베이터/에스컬레이터',
        '고객지원센터',
        '스프링쿨러',
        '화재감지기',
        '유아놀이방',
        '종합콜센터',
        '고객휴게실',
        '수유센터',
        '물품보관함',
        '자전거보관함',
        '체육시설',
        '간이도서관',
        '쇼핑카트',
        '외국인안내센터',
        '고객동선통로',
        '방송센터',
        '문화교실',
        '공동물류창고',
        '시장전용고객주차장',
        '교육장',
        '회의실',
        '자동심장충격기'
    ]
    
    # 두 번째 파일의 시설 보유여부 컬럼들
    facility_columns_file2 = [
        '공중화장실',
        '주차장'
    ]
    
    # 위치 및 연락처 정보
    location_contact_columns = [
        '위도',
        '경도',
        '전화번호'
    ]
    
    # 전체 헤더 구성
    header = basic_columns + facility_columns_file1 + facility_columns_file2 + location_contact_columns
    
    return header

def get_value_from_file(row, header, column_name):
    """파일에서 특정 컬럼 값 가져오기"""
    if not row or not column_name or column_name not in header:
        return ""
    try:
        idx = header.index(column_name)
        return row[idx] if len(row) > idx else ""
    except (ValueError, IndexError):
        return ""

def smart_merge_csv_files():
    """시장명 우선, 중복 시 주소 매칭하는 스마트 합병"""
    
    print("🚀 스마트 시장 데이터 합병 시작...")
    print("📋 매칭 전략: 시장명 우선 → 도로명주소 → 지번주소")
    
    try:
        # 첫 번째 파일 읽기
        print("\n📁 첫 번째 파일 읽는 중...")
        file1_data, encoding1 = read_csv_with_encoding('소상공인시장진흥공단_전통시장현황_20240719.csv')
        print(f"✅ 첫 번째 파일: {len(file1_data)}개 행, 인코딩: {encoding1}")
        
        # 두 번째 파일 읽기
        print("📁 두 번째 파일 읽는 중...")
        file2_data, encoding2 = read_csv_with_encoding('전국전통시장표준데이터.csv')
        print(f"✅ 두 번째 파일: {len(file2_data)}개 행, 인코딩: {encoding2}")
        
        if not file1_data or not file2_data:
            print("❌ 파일이 비어있습니다.")
            return
        
        # 헤더 추출
        header1 = file1_data[0] if file1_data else []
        header2 = file2_data[0] if file2_data else []
        
        print(f"\n🔍 첫 번째 파일 컬럼 수: {len(header1)}")
        print(f"🔍 두 번째 파일 컬럼 수: {len(header2)}")
        
        # 최종 헤더 생성
        final_header = create_final_header()
        
        print(f"\n📋 최종 헤더 ({len(final_header)}개 컬럼):")
        for i, col in enumerate(final_header):
            print(f"   {i+1:2d}. {col}")
        
        # 첫 번째 파일 데이터 구조화
        print(f"\n🔄 첫 번째 파일 데이터 구조화...")
        file1_markets = {}
        file1_name_groups = defaultdict(list)  # 같은 이름의 시장들 그룹화
        
        for i, row in enumerate(file1_data[1:], 1):
            if len(row) > 1:
                market_code = row[0] if len(row) > 0 else ""
                market_name = clean_market_name(row[1]) if len(row) > 1 else ""
                road_addr = get_value_from_file(row, header1, '도로명주소')
                jibun_addr = get_value_from_file(row, header1, '지번주소')
                
                if market_code and market_name:
                    market_info = {
                        'row': row,
                        'market_code': market_code,
                        'market_name': market_name,
                        'road_addr': road_addr,
                        'jibun_addr': jibun_addr,
                        'road_addr_norm': normalize_address(road_addr),
                        'jibun_addr_norm': normalize_address(jibun_addr),
                        'addr_key': extract_key_address_parts(road_addr if road_addr and road_addr != '0' else jibun_addr)
                    }
                    
                    file1_markets[market_code] = market_info
                    file1_name_groups[market_name].append(market_info)
        
        print(f"✅ 첫 번째 파일: {len(file1_markets)}개 시장 구조화 완료")
        
        # 두 번째 파일 데이터 구조화
        print(f"🔄 두 번째 파일 데이터 구조화...")
        file2_markets = []
        file2_name_groups = defaultdict(list)
        
        for i, row in enumerate(file2_data[1:], 1):
            if len(row) > 0:
                market_name = clean_market_name(row[0]) if len(row) > 0 else ""
                road_addr = get_value_from_file(row, header2, '소재지도로명주소')
                jibun_addr = get_value_from_file(row, header2, '소재지지번주소')
                
                if market_name:
                    market_info = {
                        'row': row,
                        'market_name': market_name,
                        'road_addr': road_addr,
                        'jibun_addr': jibun_addr,
                        'road_addr_norm': normalize_address(road_addr),
                        'jibun_addr_norm': normalize_address(jibun_addr),
                        'addr_key': extract_key_address_parts(road_addr if road_addr else jibun_addr),
                        'matched': False
                    }
                    
                    file2_markets.append(market_info)
                    file2_name_groups[market_name].append(market_info)
        
        print(f"✅ 두 번째 파일: {len(file2_markets)}개 시장 구조화 완료")
        
        # 매칭 과정
        print(f"\n🔗 매칭 과정 시작...")
        matches = []
        
        # 1단계: 시장명이 고유한 경우 직접 매칭
        print(f"1️⃣ 고유 시장명 매칭...")
        unique_name_matches = 0
        
        for name, file1_group in file1_name_groups.items():
            if len(file1_group) == 1 and name in file2_name_groups and len(file2_name_groups[name]) == 1:
                file1_market = file1_group[0]
                file2_market = file2_name_groups[name][0]
                
                matches.append((file1_market, file2_market))
                file2_market['matched'] = True
                unique_name_matches += 1
        
        print(f"   ✅ 고유 시장명 매칭: {unique_name_matches}개")
        
        # 2단계: 중복 시장명의 경우 주소로 매칭
        print(f"2️⃣ 중복 시장명 주소 매칭...")
        address_matches = 0
        
        for name, file1_group in file1_name_groups.items():
            if len(file1_group) > 1 or (name in file2_name_groups and len(file2_name_groups[name]) > 1):
                if name in file2_name_groups:
                    file2_group = [m for m in file2_name_groups[name] if not m['matched']]
                    
                    for file1_market in file1_group:
                        best_match = None
                        best_score = 0
                        
                        for file2_market in file2_group:
                            if file2_market['matched']:
                                continue
                            
                            score = 0
                            
                            # 도로명주소 비교
                            if (file1_market['road_addr_norm'] and file2_market['road_addr_norm'] and 
                                file1_market['road_addr_norm'] == file2_market['road_addr_norm']):
                                score += 100
                            
                            # 지번주소 비교
                            elif (file1_market['jibun_addr_norm'] and file2_market['jibun_addr_norm'] and 
                                  file1_market['jibun_addr_norm'] == file2_market['jibun_addr_norm']):
                                score += 90
                            
                            # 주소 핵심 부분 비교
                            elif (file1_market['addr_key'] and file2_market['addr_key'] and 
                                  file1_market['addr_key'] == file2_market['addr_key']):
                                score += 70
                            
                            # 부분 주소 매칭
                            elif (file1_market['road_addr_norm'] and file2_market['road_addr_norm']):
                                if file1_market['addr_key'] in file2_market['road_addr_norm'] or file2_market['addr_key'] in file1_market['road_addr_norm']:
                                    score += 50
                            
                            if score > best_score:
                                best_score = score
                                best_match = file2_market
                        
                        if best_match and best_score >= 50:  # 최소 점수 기준
                            matches.append((file1_market, best_match))
                            best_match['matched'] = True
                            address_matches += 1
        
        print(f"   ✅ 주소 매칭: {address_matches}개")
        
        # 3단계: 매칭되지 않은 시장들 처리
        print(f"3️⃣ 매칭되지 않은 시장 처리...")
        unmatched_file1 = []
        unmatched_file2 = [m for m in file2_markets if not m['matched']]
        
        for market_code, market_info in file1_markets.items():
            if not any(market_info == match[0] for match in matches):
                unmatched_file1.append(market_info)
        
        print(f"   ⚠️  매칭되지 않은 첫 번째 파일 시장: {len(unmatched_file1)}개")
        print(f"   ⚠️  매칭되지 않은 두 번째 파일 시장: {len(unmatched_file2)}개")
        
        # 최종 데이터 생성
        print(f"\n📊 최종 데이터 생성...")
        final_data = [final_header]
        
        # 매칭된 데이터 처리
        for file1_market, file2_market in matches:
            final_row = create_merged_row(file1_market, file2_market, header1, header2, final_header)
            final_data.append(final_row)
        
        # 매칭되지 않은 첫 번째 파일 데이터 추가
        for file1_market in unmatched_file1:
            final_row = create_merged_row(file1_market, None, header1, header2, final_header)
            final_data.append(final_row)
        
        # 매칭되지 않은 두 번째 파일 데이터 추가
        for file2_market in unmatched_file2:
            final_row = create_merged_row(None, file2_market, header1, header2, final_header)
            final_data.append(final_row)
        
        # 결과 저장
        output_filename = '전통시장_최종합병데이터.csv'
        with open(output_filename, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(final_data)
        
        # 매칭된 데이터만 별도 저장
        matched_filename = '전통시장_최종매칭데이터.csv'
        matched_data = [final_header] + [create_merged_row(f1, f2, header1, header2, final_header) for f1, f2 in matches]
        with open(matched_filename, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(matched_data)
        
        # 결과 요약
        print(f"\n🎉 스마트 합병 완료!")
        print(f"📁 생성된 파일:")
        print(f"   1. {output_filename} - 전체 합병 결과 ({len(final_data)-1}개 시장)")
        print(f"   2. {matched_filename} - 매칭된 데이터만 ({len(matches)}개 시장)")
        
        print(f"\n📊 매칭 결과:")
        print(f"   - 고유 시장명 매칭: {unique_name_matches}개")
        print(f"   - 주소 기반 매칭: {address_matches}개")
        print(f"   - 총 매칭: {len(matches)}개")
        print(f"   - 매칭률: {len(matches)}/{len(file1_markets)} = {len(matches)/len(file1_markets)*100:.1f}%")
        
        # 매칭 예시 출력
        print(f"\n🔍 매칭 예시 (처음 5개):")
        for i, (f1, f2) in enumerate(matches[:5]):
            print(f"   {i+1}. {f1['market_name']}")
            print(f"      파일1: {f1['market_code']} | {f1['road_addr'][:30]}...")
            print(f"      파일2: {f2['road_addr'][:30]}...")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def create_merged_row(file1_market, file2_market, header1, header2, final_header):
    """두 시장 정보를 합병하여 최종 행 생성"""
    
    final_row = []
    
    for col in final_header:
        value = ""
        
        if col == '시장코드':
            value = file1_market['market_code'] if file1_market else ""
        
        elif col == '시장명':
            if file1_market:
                value = file1_market['market_name']
            elif file2_market:
                value = file2_market['market_name']
        
        elif col == '지번주소':
            if file1_market and file1_market['jibun_addr']:
                value = standardize_region(file1_market['jibun_addr'])
            elif file2_market and file2_market['jibun_addr']:
                value = standardize_region(file2_market['jibun_addr'])
        
        elif col == '도로명주소':
            if file1_market and file1_market['road_addr'] and file1_market['road_addr'] != '0':
                value = standardize_region(file1_market['road_addr'])
            elif file2_market and file2_market['road_addr']:
                value = standardize_region(file2_market['road_addr'])
        
        elif col == '시도':
            value = get_value_from_file(file1_market['row'], header1, '시도') if file1_market else ""
            if not value and file2_market:
                # 주소에서 시도 추출
                addr = file2_market['road_addr'] if file2_market['road_addr'] else file2_market['jibun_addr']
                value = extract_sido_from_address(addr)
        
        elif col == '시군구':
            value = get_value_from_file(file1_market['row'], header1, '시군구') if file1_market else ""
            if not value and file2_market:
                # 주소에서 시군구 추출
                addr = file2_market['road_addr'] if file2_market['road_addr'] else file2_market['jibun_addr']
                value = extract_sigungu_from_address(addr)
        
        elif col in ['시장개설주기', '점포수', '개설연도', '취급품목', '위도', '경도', '전화번호']:
            # 두 번째 파일에서 가져오기
            if file2_market:
                if col == '전화번호':
                    value = get_value_from_file(file2_market['row'], header2, '전화번호')
                else:
                    value = get_value_from_file(file2_market['row'], header2, col)
        
        elif col in ['공중화장실', '주차장']:
            # 두 번째 파일의 시설 정보
            if file2_market:
                col_name = col + '보유여부'
                value = get_value_from_file(file2_market['row'], header2, col_name)
        
        else:
            # 첫 번째 파일의 시설 정보
            if file1_market:
                # 컬럼명 매핑
                facility_mapping = {
                    '아케이드': '아케이드 보유 여부',
                    '엘리베이터/에스컬레이터': '엘리베이터_에스컬레이터_보유여부',
                    '고객지원센터': '고객지원센터 보유 여부',
                    '스프링쿨러': '스프링쿨러 보유 여부',
                    '화재감지기': '화재감지기 보유여부',
                    '유아놀이방': '유아놀이방_보유여부',
                    '종합콜센터': '종합콜센터_보유여부',
                    '고객휴게실': '고객휴게실_보유여부',
                    '수유센터': '수유센터_보유여부',
                    '물품보관함': '물품보관함_보유여부',
                    '자전거보관함': '자전거보관함_보유여부',
                    '체육시설': '체육시설_보유여부',
                    '간이도서관': '간이 도서관_보유여부',
                    '쇼핑카트': '쇼핑카트_보유여부',
                    '외국인안내센터': '외국인 안내센터_보유여부',
                    '고객동선통로': '고객동선통로_보유여부',
                    '방송센터': '방송센터_보유여부',
                    '문화교실': '문화교실_보유여부',
                    '공동물류창고': '공동물류창고_보유여부',
                    '시장전용고객주차장': '시장전용 고객주차장_보유여부',
                    '교육장': '교육장_보유여부',
                    '회의실': '회의실_보유여부',
                    '자동심장충격기': '자동심장충격기_보유여부'
                }
                
                original_col = facility_mapping.get(col, col)
                value = get_value_from_file(file1_market['row'], header1, original_col)
        
        final_row.append(value)
    
    return final_row

def extract_sido_from_address(addr):
    """주소에서 시도 추출"""
    if not addr:
        return ""
    
    addr = standardize_region(addr)
    
    sido_patterns = [
        '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', 
        '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
        '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
    ]
    
    for sido in sido_patterns:
        if sido in addr:
            return sido
    
    return ""

def extract_sigungu_from_address(addr):
    """주소에서 시군구 추출"""
    if not addr:
        return ""
    
    # 시군구 패턴 찾기
    sigungu_pattern = r'([\w]+시|[\w]+군|[\w]+구)'
    matches = re.findall(sigungu_pattern, addr)
    
    if matches:
        # 시도명이 아닌 첫 번째 매치를 시군구로 사용
        sido_names = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', 
                     '광주광역시', '대전광역시', '울산광역시', '세종특별자치시']
        
        for match in matches:
            if match not in sido_names:
                return match
    
    return ""

if __name__ == "__main__":
    smart_merge_csv_files() 