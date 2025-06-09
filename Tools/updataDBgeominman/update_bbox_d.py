
import math
import pandas as pd
from shapely.geometry import shape
import orjson
from sqlalchemy import create_engine, text
from multiprocessing import Pool, cpu_count, freeze_support
from tqdm import tqdm
import traceback
from datetime import datetime
import os

# ✅ Configuration: Fill in with your DB credentials
# ✅ 설정: 여기에 본인의 DB 접속 정보를 입력하세요
DB_USER = "your_user"         # DB username / DB 사용자명
DB_PASS = "your_pass"         # DB password / DB 비밀번호
DB_HOST = "s2024.soxcorp.co.kr"
DB_PORT = 33306
DB_NAME = "collectdata"
TABLE_NAME = "vmap2025"
CHUNKSIZE = 100_000  # Number of rows to process per chunk / 한 번에 처리할 행 수

# 🔹 Extract bounding box (minX, maxX, minY, maxY) from geometry JSON
# 🔹 geometry 컬럼에서 bounding box 정보 추출
def extract_bounds(row):
    try:
        geom = shape(orjson.loads(row['geometry']))  # Convert JSON to geometry / JSON을 geometry 객체로 변환
        minx, miny, maxx, maxy = geom.bounds  # Get bounds / 경계 계산
        return (row['id'], minx, maxx, miny, maxy)
    except Exception as e:
        # Log error to error_log.txt if parsing fails
        # 파싱 실패 시 error_log.txt에 기록
        with open("error_log.txt", "a", encoding="utf-8") as log:
            log.write(f"[ID {row['id']}] ❌ 오류: {e}\n{row['geometry']}\n\n")
        return (row['id'], None, None, None, None)

# 🔹 Run extract_bounds in parallel using multiprocessing
# 🔹 extract_bounds를 멀티코어로 병렬 실행
def process_chunk(df_chunk):
    with Pool(cpu_count()) as pool:
        return pool.map(extract_bounds, df_chunk.to_dict(orient='records'))

# 🔹 Main function: connects to DB, fetches rows chunk by chunk, updates bounding box values
# 🔹 메인 함수: DB 연결 후 geometry를 읽어 경계값을 계산하고 DB 업데이트
def main():
    try:
        # Create database engine / DB 엔진 생성
        db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        engine = create_engine(db_url)

        # Get total number of rows / 전체 행 수 가져오기
        with engine.connect() as conn:
            total_rows = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()

        progress = tqdm(total=total_rows, desc="🚀 Processing Rows", unit="row")  # Progress bar
        offset = 0

        while offset < total_rows:
            # Read a chunk of rows from the DB / 일정량의 행을 DB에서 가져옴
            query = f"SELECT shapeid as id, geometry FROM {TABLE_NAME} LIMIT {CHUNKSIZE} OFFSET {offset}"
            df = pd.read_sql(query, engine)

            if df.empty:
                break  # No more rows / 더 이상 읽을 행이 없으면 종료

            results = process_chunk(df)  # Run bounding box calculation in parallel / 병렬로 경계값 계산

            # Bulk update bounding box columns / 계산된 경계값을 DB에 대량 업데이트
            with engine.begin() as conn:
                update_sql = text(f"""
                    UPDATE {TABLE_NAME}
                    SET minX = :minX, maxX = :maxX, minY = :minY, maxY = :maxY
                    WHERE shapeid = :id
                """)
                conn.execute(update_sql, [
                    {"id": rid, "minX": minx, "maxX": maxx, "minY": miny, "maxY": maxy}
                    for (rid, minx, maxx, miny, maxy) in results
                ])

            offset += CHUNKSIZE
            progress.update(len(df))  # Update progress bar / 진행률 갱신

        progress.close()
        print("✅ 전체 완료되었습니다.")  # All done
        input("▶ 실행이 끝났습니다. Enter 키를 누르세요.")

    except Exception as e:
        # Log unexpected error / 예외 발생 시 로그 파일 기록
        with open("log.txt", "a", encoding="utf-8") as log:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"\n[{timestamp}] ❌ 프로그램 오류 발생:\n")
            log.write(traceback.format_exc())
        print("❌ 프로그램이 예기치 않게 종료되었습니다. log.txt를 확인하세요.")
        print("🔍 로그 저장 위치:", os.path.abspath("log.txt"))
        input("▶ 종료 전 Enter 키를 누르세요.")

# ✅ Windows용 멀티프로세싱 호환 처리
# ✅ Required for multiprocessing to work correctly on Windows
if __name__ == "__main__":
    freeze_support()
    main()
