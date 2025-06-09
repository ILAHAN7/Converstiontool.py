
===========================================
📦 update_bbox_documented.py - README (EN + 한국어)
===========================================

▶ DESCRIPTION / 설명
-------------------------------------------
This Python program reads a GeoJSON-style geometry column in a database table 
and calculates bounding boxes (minX, maxX, minY, maxY), then updates the table in bulk 
using fast multiprocessing.

이 Python 프로그램은 DB 테이블의 geometry 컬럼에서 GeoJSON 정보를 읽고 
경계값(minX, maxX, minY, maxY)을 계산하여 대량으로 업데이트합니다. 
멀티코어 병렬처리를 지원합니다.

▶ REQUIREMENTS / 필수 조건
-------------------------------------------
1. Python 3.8 or higher / Python 3.8 이상
2. Install required packages:
   pip install pandas shapely sqlalchemy pymysql orjson tqdm

3. Database table must contain:
   - shapeid (unique key)
   - geometry (GeoJSON string)
   - minX, maxX, minY, maxY (columns to be updated)

DB 테이블 구성 필수 요소:
- shapeid (고유 ID 필드)
- geometry (GeoJSON 문자열 필드)
- minX, maxX, minY, maxY (업데이트 대상 컬럼)

▶ DB CONFIGURATION / DB 설정
-------------------------------------------
Edit the following variables at the top of the Python script:
스크립트 상단 변수 수정:

DB_USER = "your_user"
DB_PASS = "your_pass"
DB_HOST = "your_host"
DB_PORT = 3306
DB_NAME = "your_db"
TABLE_NAME = "your_table"

▶ HOW TO RUN / 실행 방법
-------------------------------------------
python update_bbox.py

▶ FEATURES / 주요 기능
-------------------------------------------
- Reads DB rows in chunks (default: 100,000)
- Extracts bounding boxes using shapely
- Parallel processing with multiprocessing
- Real-time progress bar via tqdm
- Error logging in `log.txt` and `error_log.txt`

- geometry 필드에서 경계값 추출
- tqdm으로 실시간 진행률 표시
- 멀티코어 병렬 처리 (CPU 자동 인식)
- 에러 발생 시 로그 파일 자동 저장

▶ OUTPUT FILES / 출력 파일
-------------------------------------------
- log.txt            → fatal errors and traceback logs
- error_log.txt      → rows that failed to parse geometry

▶ ESTIMATED TIME / 예상 처리 시간
-------------------------------------------
1 million rows: ~8-10 minutes (8-core CPU)
10 million rows: ~1.5-2 hours

백만건: 약 8~10분, 천만건: 약 1.5~2시간 (8코어 기준)

▶ TROUBLESHOOTING / 문제 해결
-------------------------------------------
- No module named ... → install missing module via pip
- Unknown column ...  → check column names in DB
- tqdm stuck at 0%   → wait for heavy initial load

▶ OPTIONAL EXTENSIONS / 확장 가능 기능
-------------------------------------------
- ETA estimate
- Thread pool limit
- WHERE filter for target subset
- Windows executable version (.exe)
