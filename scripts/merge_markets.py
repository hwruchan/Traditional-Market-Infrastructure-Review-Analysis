import pandas as pd
import numpy as np

def merge_market_data():
    """두 전통시장 CSV 파일을 시장명을 기준으로 합병하는 함수"""
    
    print("📊 전통시장 데이터 합병 시작...")
    
    try:
        # CSV 파일 읽기 (인코딩 문제 해결)
        print("📁 첫 번째 파일 읽는 중...")
        df1 = pd.read_csv('소상공인시장진흥공단_전통시장현황_20240719.csv', encoding='cp949')
        
        print("📁 두 번째 파일 읽는 중...")
        df2 = pd.read_csv('전국전통시장표준데이터.csv', encoding='cp949')
        
        print(f"✅ 첫 번째 파일: {len(df1)}개 행, {len(df1.columns)}개 컬럼")
        print(f"✅ 두 번째 파일: {len(df2)}개 행, {len(df2.columns)}개 컬럼")
        
        # 컬럼명 확인
        print("\n🔍 첫 번째 파일 컬럼명:")
        print(df1.columns.tolist()[:10])  # 처음 10개만 출력
        
        print("\n🔍 두 번째 파일 컬럼명:")
        print(df2.columns.tolist()[:10])  # 처음 10개만 출력
        
        # 시장명 컬럼 찾기
        market_name_col1 = None
        market_name_col2 = None
        
        # 첫 번째 파일에서 시장명 컬럼 찾기
        for col in df1.columns:
            if '시장' in col or '명' in col:
                market_name_col1 = col
                break
        
        # 두 번째 파일에서 시장명 컬럼 찾기  
        for col in df2.columns:
            if '시장' in col or '명' in col:
                market_name_col2 = col
                break
        
        if market_name_col1 is None:
            market_name_col1 = df1.columns[1]  # 두 번째 컬럼을 시장명으로 가정
        if market_name_col2 is None:
            market_name_col2 = df2.columns[0]  # 첫 번째 컬럼을 시장명으로 가정
            
        print(f"\n🏪 첫 번째 파일 시장명 컬럼: {market_name_col1}")
        print(f"🏪 두 번째 파일 시장명 컬럼: {market_name_col2}")
        
        # 시장명 데이터 정제
        df1[market_name_col1] = df1[market_name_col1].astype(str).str.strip()
        df2[market_name_col2] = df2[market_name_col2].astype(str).str.strip()
        
        # 시장명 표준화 (괄호 안 내용 제거, 공백 정리)
        df1['시장명_정제'] = df1[market_name_col1].str.replace(r'\([^)]*\)', '', regex=True).str.strip()
        df2['시장명_정제'] = df2[market_name_col2].str.replace(r'\([^)]*\)', '', regex=True).str.strip()
        
        print(f"\n📈 첫 번째 파일 고유 시장 수: {df1['시장명_정제'].nunique()}")
        print(f"📈 두 번째 파일 고유 시장 수: {df2['시장명_정제'].nunique()}")
        
        # 샘플 시장명 출력
        print(f"\n🔍 첫 번째 파일 시장명 샘플:")
        print(df1['시장명_정제'].head(10).tolist())
        
        print(f"\n🔍 두 번째 파일 시장명 샘플:")
        print(df2['시장명_정제'].head(10).tolist())
        
        # 데이터 합병 (outer join으로 모든 데이터 보존)
        print("\n🔄 데이터 합병 중...")
        merged_df = pd.merge(df1, df2, left_on='시장명_정제', right_on='시장명_정제', 
                           how='outer', suffixes=('_파일1', '_파일2'))
        
        print(f"✅ 합병 완료: {len(merged_df)}개 행")
        
        # 매칭 결과 분석
        both_files = merged_df.dropna(subset=[market_name_col1, market_name_col2])
        only_file1 = merged_df[merged_df[market_name_col2].isna()]
        only_file2 = merged_df[merged_df[market_name_col1].isna()]
        
        print(f"\n📊 매칭 결과:")
        print(f"   - 두 파일 모두에 있는 시장: {len(both_files)}개")
        print(f"   - 첫 번째 파일에만 있는 시장: {len(only_file1)}개")
        print(f"   - 두 번째 파일에만 있는 시장: {len(only_file2)}개")
        
        # 결과 저장
        output_filename = '전통시장_합병데이터.csv'
        merged_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 합병된 데이터 저장: {output_filename}")
        
        # 매칭된 시장들만 별도 저장
        if len(both_files) > 0:
            matched_filename = '전통시장_매칭데이터.csv'
            both_files.to_csv(matched_filename, index=False, encoding='utf-8-sig')
            print(f"💾 매칭된 데이터만 저장: {matched_filename}")
        
        # 요약 정보 저장
        summary_data = {
            '구분': ['전체 합병 데이터', '두 파일 모두 매칭', '첫 번째 파일만', '두 번째 파일만'],
            '개수': [len(merged_df), len(both_files), len(only_file1), len(only_file2)],
            '비율(%)': [
                100.0,
                round(len(both_files)/len(merged_df)*100, 1),
                round(len(only_file1)/len(merged_df)*100, 1),
                round(len(only_file2)/len(merged_df)*100, 1)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_filename = '합병_요약정보.csv'
        summary_df.to_csv(summary_filename, index=False, encoding='utf-8-sig')
        print(f"💾 요약 정보 저장: {summary_filename}")
        
        print("\n📋 합병 요약:")
        print(summary_df.to_string(index=False))
        
        return merged_df, both_files
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None, None

if __name__ == "__main__":
    merged_data, matched_data = merge_market_data()
    
    if merged_data is not None:
        print(f"\n🎉 데이터 합병 완료!")
        print(f"📁 생성된 파일:")
        print(f"   1. 전통시장_합병데이터.csv - 전체 합병 결과")
        print(f"   2. 전통시장_매칭데이터.csv - 매칭된 데이터만")
        print(f"   3. 합병_요약정보.csv - 합병 결과 요약")
    else:
        print("❌ 데이터 합병 실패") 