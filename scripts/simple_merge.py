import csv
import codecs
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
    
    # 괄호와 그 안의 내용 제거
    import re
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

def create_final_header():
    """최종 헤더 생성 - 지정된 컬럼들로만"""
    
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
    
    # 첫 번째 파일의 시설 보유여부 컬럼들 (Y/N 값이 있는 것들)
    facility_columns_file1 = [
        '아케이드 보유 여부',
        '엘리베이터_에스컬레이터_보유여부',
        '고객지원센터 보유 여부',
        '스프링쿨러 보유 여부',
        '화재감지기 보유여부',
        '유아놀이방_보유여부',
        '종합콜센터_보유여부',
        '고객휴게실_보유여부',
        '수유센터_보유여부',
        '물품보관함_보유여부',
        '자전거보관함_보유여부',
        '체육시설_보유여부',
        '간이 도서관_보유여부',
        '쇼핑카트_보유여부',
        '외국인 안내센터_보유여부',
        '고객동선통로_보유여부',
        '방송센터_보유여부',
        '문화교실_보유여부',
        '공동물류창고_보유여부',
        '시장전용 고객주차장_보유여부',
        '교육장_보유여부',
        '회의실_보유여부',
        '자동심장충격기_보유여부'
    ]
    
    # 두 번째 파일의 시설 보유여부 컬럼들
    facility_columns_file2 = [
        '공중화장실보유여부',
        '주차장보유여부'
    ]
    
    # 시설 컬럼명 정리 (보유여부, _보유여부 제거)
    facility_clean_names = []
    for col in facility_columns_file1:
        clean_name = col.replace('_보유여부', '').replace(' 보유 여부', '').replace('_', ' ')
        facility_clean_names.append(clean_name)
    
    for col in facility_columns_file2:
        clean_name = col.replace('보유여부', '')
        facility_clean_names.append(clean_name)
    
    # 위치 및 연락처 정보
    location_contact_columns = [
        '위도',
        '경도',
        '전화번호'
    ]
    
    # 전체 헤더 구성
    header = basic_columns + facility_clean_names + location_contact_columns
    
    return header, facility_columns_file1, facility_columns_file2

def merge_csv_files():
    """두 CSV 파일을 시장코드 기준으로 1:1 매칭하여 합병"""
    
    print("📊 시장코드 기준 1:1 매칭 시작...")
    
    try:
        # 첫 번째 파일 읽기
        print("📁 첫 번째 파일 읽는 중...")
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
        
        # 헤더 출력 (디버깅용)
        print(f"\n📋 첫 번째 파일 헤더:")
        for i, col in enumerate(header1[:10]):
            print(f"   {i:2d}. {col}")
        
        print(f"\n📋 두 번째 파일 헤더:")
        for i, col in enumerate(header2[:10]):
            print(f"   {i:2d}. {col}")
        
        # 최종 헤더 생성
        final_header, facility_columns_file1, facility_columns_file2 = create_final_header()
        
        print(f"\n📋 최종 헤더 ({len(final_header)}개 컬럼):")
        for i, col in enumerate(final_header):
            print(f"   {i+1:2d}. {col}")
        
        def get_value_from_file(row, header, column_name):
            """파일에서 특정 컬럼 값 가져오기"""
            if not row or not column_name or column_name not in header:
                return ""
            try:
                idx = header.index(column_name)
                return row[idx] if len(row) > idx else ""
            except (ValueError, IndexError):
                return ""
        
        # 첫 번째 파일 데이터를 시장코드 기준으로 딕셔너리 생성
        file1_dict = {}
        for i, row in enumerate(file1_data[1:], 1):
            if len(row) > 0:
                market_code = row[0] if len(row) > 0 else ""  # 시장코드 (인덱스 0)
                if market_code:
                    file1_dict[market_code] = row
        
        # 두 번째 파일에서 시장명을 기준으로 첫 번째 파일의 시장코드 찾기
        file2_dict = {}
        market_name_to_code = {}
        
        # 첫 번째 파일에서 시장명 → 시장코드 매핑 생성
        for market_code, row in file1_dict.items():
            if len(row) > 1:
                market_name = clean_market_name(row[1])
                if market_name:
                    market_name_to_code[market_name] = market_code
        
        # 두 번째 파일 데이터 처리
        for i, row in enumerate(file2_data[1:], 1):
            if len(row) > 0:
                market_name = clean_market_name(row[0])  # 시장명 (인덱스 0)
                if market_name and market_name in market_name_to_code:
                    market_code = market_name_to_code[market_name]
                    file2_dict[market_code] = row
        
        print(f"\n📈 첫 번째 파일 시장 수: {len(file1_dict)}")
        print(f"📈 두 번째 파일에서 매칭된 시장 수: {len(file2_dict)}")
        
        # 매칭 분석
        all_codes = set(file1_dict.keys()) | set(file2_dict.keys())
        matched_codes = set(file1_dict.keys()) & set(file2_dict.keys())
        only_file1_codes = set(file1_dict.keys()) - set(file2_dict.keys())
        only_file2_codes = set(file2_dict.keys()) - set(file1_dict.keys())
        
        print(f"\n📊 시장코드 기준 매칭 결과:")
        print(f"   - 전체 고유 시장코드 수: {len(all_codes)}")
        print(f"   - 두 파일 모두에 있는 시장: {len(matched_codes)}")
        print(f"   - 첫 번째 파일에만 있는 시장: {len(only_file1_codes)}")
        print(f"   - 두 번째 파일에만 있는 시장: {len(only_file2_codes)}")
        
        # 매칭 예시 출력
        print(f"\n🔗 매칭된 시장 예시 (처음 5개):")
        for i, code in enumerate(sorted(matched_codes)[:5]):
            row1 = file1_dict.get(code, [])
            row2 = file2_dict.get(code, [])
            name1 = row1[1] if len(row1) > 1 else ""
            name2 = row2[0] if len(row2) > 0 else ""
            print(f"   {i+1}. 코드: {code}")
            print(f"      파일1: {name1}")
            print(f"      파일2: {name2}")
            if clean_market_name(name1) != clean_market_name(name2):
                print(f"      ⚠️  시장명 불일치!")
        
        # 최종 데이터 생성
        final_data = [final_header]
        
        for code in sorted(all_codes):
            row1 = file1_dict.get(code, [])
            row2 = file2_dict.get(code, [])
            
            final_row = []
            
            # 시장코드
            final_row.append(code)
            
            # 시장명 (파일1 우선, 없으면 파일2)
            market_name = ""
            if row1 and len(row1) > 1:
                market_name = row1[1]
            elif row2 and len(row2) > 0:
                market_name = row2[0]
            final_row.append(market_name)
            
            # 지번주소 (파일1 우선, 없으면 파일2)
            jibun1 = get_value_from_file(row1, header1, '지번주소')
            jibun2 = get_value_from_file(row2, header2, '소재지지번주소')
            if jibun1:
                final_row.append(standardize_region(jibun1))
            elif jibun2:
                final_row.append(standardize_region(jibun2))
            else:
                final_row.append("")
            
            # 도로명주소 (파일1 우선, 없으면 파일2)
            road1 = get_value_from_file(row1, header1, '도로명주소')
            road2 = get_value_from_file(row2, header2, '소재지도로명주소')
            if road1 and road1 != '0':  # '0'은 빈값으로 처리
                final_row.append(standardize_region(road1))
            elif road2:
                final_row.append(standardize_region(road2))
            else:
                final_row.append("")
            
            # 시도 (파일1 우선, 없으면 파일2에서 추출)
            sido1 = get_value_from_file(row1, header1, '시도')
            if sido1:
                # 시도명 표준화
                sido1 = sido1.replace('강원특별자치도', '강원도').replace('전북특별자치도', '전라북도')
                final_row.append(sido1)
            else:
                # 파일2에서 주소로부터 시도 추출
                road_addr = get_value_from_file(row2, header2, '소재지도로명주소')
                jibun_addr = get_value_from_file(row2, header2, '소재지지번주소')
                addr = road_addr if road_addr else jibun_addr
                if addr:
                    # 간단한 시도 추출
                    if '서울' in addr:
                        final_row.append('서울특별시')
                    elif '부산' in addr:
                        final_row.append('부산광역시')
                    elif '대구' in addr:
                        final_row.append('대구광역시')
                    elif '인천' in addr:
                        final_row.append('인천광역시')
                    elif '광주' in addr:
                        final_row.append('광주광역시')
                    elif '대전' in addr:
                        final_row.append('대전광역시')
                    elif '울산' in addr:
                        final_row.append('울산광역시')
                    elif '세종' in addr:
                        final_row.append('세종특별자치시')
                    elif '경기' in addr:
                        final_row.append('경기도')
                    elif '강원' in addr:
                        final_row.append('강원도')
                    elif '충북' in addr or '충청북' in addr:
                        final_row.append('충청북도')
                    elif '충남' in addr or '충청남' in addr:
                        final_row.append('충청남도')
                    elif '전북' in addr or '전라북' in addr:
                        final_row.append('전라북도')
                    elif '전남' in addr or '전라남' in addr:
                        final_row.append('전라남도')
                    elif '경북' in addr or '경상북' in addr:
                        final_row.append('경상북도')
                    elif '경남' in addr or '경상남' in addr:
                        final_row.append('경상남도')
                    elif '제주' in addr:
                        final_row.append('제주특별자치도')
                    else:
                        final_row.append("")
                else:
                    final_row.append("")
            
            # 시군구 (파일1 우선, 없으면 파일2에서 추출)
            sigungu1 = get_value_from_file(row1, header1, '시군구')
            if sigungu1:
                final_row.append(sigungu1)
            else:
                # 파일2에서 주소로부터 시군구 추출 (간단한 방식)
                road_addr = get_value_from_file(row2, header2, '소재지도로명주소')
                jibun_addr = get_value_from_file(row2, header2, '소재지지번주소')
                addr = road_addr if road_addr else jibun_addr
                if addr:
                    import re
                    # 시군구 패턴 찾기
                    sigungu_pattern = r'([\w]+시|[\w]+군|[\w]+구)'
                    matches = re.findall(sigungu_pattern, addr)
                    if matches:
                        # 첫 번째 매치를 시군구로 사용 (시도명 제외)
                        for match in matches:
                            if match not in ['서울특별시', '부산광역시', '대구광역시', '인천광역시', 
                                           '광주광역시', '대전광역시', '울산광역시', '세종특별자치시']:
                                final_row.append(match)
                                break
                        else:
                            final_row.append("")
                    else:
                        final_row.append("")
                else:
                    final_row.append("")
            
            # 시장개설주기 (파일2에서)
            final_row.append(get_value_from_file(row2, header2, '시장개설주기'))
            
            # 점포수 (파일2에서)
            final_row.append(get_value_from_file(row2, header2, '점포수'))
            
            # 개설연도 (파일2에서)
            final_row.append(get_value_from_file(row2, header2, '개설연도'))
            
            # 취급품목 (파일2에서)
            final_row.append(get_value_from_file(row2, header2, '취급품목'))
            
            # 시설 보유여부 항목들 추가 (파일1에서)
            for col in facility_columns_file1:
                value = get_value_from_file(row1, header1, col)
                final_row.append(value)
            
            # 시설 보유여부 항목들 추가 (파일2에서)
            for col in facility_columns_file2:
                value = get_value_from_file(row2, header2, col)
                final_row.append(value)
            
            # 위도 (파일2에서)
            final_row.append(get_value_from_file(row2, header2, '위도'))
            
            # 경도 (파일2에서)
            final_row.append(get_value_from_file(row2, header2, '경도'))
            
            # 전화번호 (파일2에서)
            final_row.append(get_value_from_file(row2, header2, '전화번호'))
            
            final_data.append(final_row)
        
        # 최종 결과 저장
        output_filename = '전통시장_시장코드기준합병데이터.csv'
        with open(output_filename, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(final_data)
        
        print(f"\n💾 최종 데이터 저장: {output_filename}")
        print(f"📊 총 {len(final_data)-1}개 시장 데이터 저장")
        print(f"📋 컬럼 수: {len(final_header)}개")
        
        # 매칭된 데이터만 별도 저장
        if matched_codes:
            matched_data = [final_header]
            for code in sorted(matched_codes):
                for row in final_data[1:]:
                    if row[0] == code:  # 시장코드로 비교 (인덱스 0)
                        matched_data.append(row)
                        break
            
            matched_filename = '전통시장_시장코드매칭데이터.csv'
            with open(matched_filename, 'w', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(matched_data)
            
            print(f"💾 시장코드 매칭 데이터 저장: {matched_filename}")
            print(f"📊 시장코드 매칭된 {len(matched_data)-1}개 시장 데이터 저장")
        
        # 데이터 검증
        print(f"\n🔍 데이터 검증:")
        fire_detector_count = 0
        phone_count = 0
        
        # 화재감지기 컬럼 위치 찾기
        fire_detector_idx = -1
        for i, col in enumerate(final_header):
            if '화재감지기' in col:
                fire_detector_idx = i
                break
        
        # 전화번호는 마지막 컬럼
        phone_idx = len(final_header) - 1
        
        sample_count = 0
        for row in final_data[1:]:  # 헤더 제외
            sample_count += 1
            if sample_count > 10:  # 처음 10개만 확인
                break
                
            # 화재감지기 데이터 확인
            fire_detector_value = ""
            if fire_detector_idx >= 0 and len(row) > fire_detector_idx:
                fire_detector_value = row[fire_detector_idx]
                if fire_detector_value and fire_detector_value.strip():
                    fire_detector_count += 1
                    
            # 전화번호 데이터 확인
            phone_value = row[phone_idx] if len(row) > phone_idx else ""
            if phone_value and phone_value.strip():
                phone_count += 1
            
            print(f"   {sample_count:2d}. {row[1][:20]:20s} | 화재감지기: '{fire_detector_value}' | 전화번호: '{phone_value}'")
        
        print(f"\n   - 처음 10개 시장 중 화재감지기 데이터 있는 시장: {fire_detector_count}개")
        print(f"   - 처음 10개 시장 중 전화번호 데이터 있는 시장: {phone_count}개")
        
        print(f"\n🎉 시장코드 기준 1:1 매칭 완료!")
        print(f"📁 생성된 파일:")
        print(f"   1. {output_filename} - 전체 시장코드 기준 합병 결과")
        if matched_codes:
            print(f"   2. {matched_filename} - 시장코드 매칭 데이터만")
        
        print(f"\n✨ 최종 결과:")
        print(f"   - 시장코드 기준 정확한 1:1 매칭")
        print(f"   - 강원특별자치도 → 강원도, 전북특별자치도 → 전라북도 표준화")
        print(f"   - 지정된 컬럼들로만 구성")
        print(f"   - 화재감지기와 전화번호 데이터 매핑 완료")
        print(f"   - 매칭률: {len(matched_codes)}/{len(file1_dict)} = {len(matched_codes)/len(file1_dict)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    merge_csv_files() 