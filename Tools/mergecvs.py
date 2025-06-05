import pandas as pd
import glob
import os
import traceback
from datetime import datetime

# 현재 실행 파일 위치
folder_path = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(folder_path, "log.txt")

def log_message(message):
    print(message)
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

# 기존 log.txt 지우고 새로 시작하려면 아래 줄의 주석 해제
# open(log_file_path, 'w', encoding='utf-8').close()

try:
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        raise FileNotFoundError("❌ 병합할 CSV 파일이 없습니다.")

    log_message("📄 합칠 파일 목록:")
    for f in csv_files:
        log_message(" - " + os.path.basename(f))

    dataframes = []
    for file in csv_files:
        success = False
        for enc in ['utf-8', 'cp949', 'euc-kr']:
            try:
                df = pd.read_csv(file, encoding=enc)
                dataframes.append(df)
                if enc != 'utf-8':
                    log_message(f"⚠️ {os.path.basename(file)}: utf-8 실패 → {enc}로 성공")
                success = True
                break
            except Exception as e:
                continue
        if not success:
            log_message(f"🚫 {os.path.basename(file)}: 인코딩 모두 실패")

    if not dataframes:
        raise ValueError("❌ 유효한 CSV 파일을 읽지 못했습니다.")

    combined_df = pd.concat(dataframes, ignore_index=True)
    output_path = os.path.join(folder_path, "combined_output.csv")
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    log_message("✅ 병합 완료: combined_output.csv 생성됨")

except Exception as e:
    log_message("🚨 병합 중 오류 발생:\n" + traceback.format_exc())

