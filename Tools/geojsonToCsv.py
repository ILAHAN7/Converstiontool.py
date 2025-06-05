import os
import glob
import json
import csv
from datetime import datetime
import time

folder_path = os.path.dirname(os.path.abspath(__file__))
geojsonl_files = glob.glob(os.path.join(folder_path, "*.geojsonl"))

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}", flush=True)

def convert_geojsonl_to_csv(input_path):
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(folder_path, base_name + ".csv")

    rows = []
    fieldnames = set()
    success_lines = 0
    failed_lines = 0

    log(f"📂 처리 시작: {os.path.basename(input_path)}")

    # 🔄 이모지 애니메이션용 타이머
    spinner = ["⠁", "⠂", "⠄", "⠂"]
    spin_index = 0
    last_report_time = time.time()

    with open(input_path, "r", encoding="cp949", errors="replace") as infile:
        for line_num, line in enumerate(infile, start=1):
            # 매 3초마다 진행상황 표시
            if time.time() - last_report_time >= 3:
                print(f"🔄 {line_num}번째 줄 처리 중... {spinner[spin_index]}", flush=True)
                spin_index = (spin_index + 1) % len(spinner)
                last_report_time = time.time()

            try:
                feature = json.loads(line.strip())
                props = feature.get("properties", {})
                geom = feature.get("geometry", {})

                lon, lat = None, None
                try:
                    if geom.get("type") == "MultiPolygon":
                        lon, lat = geom["coordinates"][0][0][0]
                    elif geom.get("type") == "Polygon":
                        lon, lat = geom["coordinates"][0][0]
                except Exception:
                    pass

                props["geom_lon"] = lon
                props["geom_lat"] = lat

                fieldnames.update(props.keys())
                rows.append(props)
                success_lines += 1
            except Exception as e:
                failed_lines += 1
                if failed_lines <= 5:
                    log(f"⚠️ {base_name} - {line_num}번째 줄 오류: {e}")
                continue

    if not rows:
        log(f"🚫 실패: {base_name}는 유효한 데이터가 없습니다.")
        return

    fieldnames = sorted(list(fieldnames))
    with open(output_path, "w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    log(f"✅ 완료: {os.path.basename(output_path)} (성공 {success_lines}줄, 실패 {failed_lines}줄)")

# 전체 처리
log("🚀 GeoJSONL → CSV 변환 시작")
if not geojsonl_files:
    log("❌ 변환할 geojsonl 파일이 없습니다.")
else:
    for file in geojsonl_files:
        convert_geojsonl_to_csv(file)
log("🏁 전체 변환 작업 종료")

