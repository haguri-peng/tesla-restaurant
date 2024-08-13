""" convert_db_to_json """
import sqlite3
import json
import os
import tempfile
import requests

# GitHub Pages에서 DB 파일 다운로드
db_url = 'https://raw.githubusercontent.com/haguri-peng/' \
        'tesla-restaurant/master/db/TeslaRestaurant.db'
response = requests.get(db_url, timeout=10)
response.raise_for_status()  # 오류 발생 시 예외 발생

# 임시 파일 생성
with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    temp_file.write(response.content)
    temp_file_path = temp_file.name

# 소스 데이터베이스 연결 (임시 파일)
src_conn = sqlite3.connect(temp_file_path)

# 메모리에 새 데이터베이스 연결
dest_conn = sqlite3.connect(':memory:')

# 소스에서 대상으로 데이터베이스 복사
src_conn.backup(dest_conn)

# 연결 닫기 및 임시 파일 삭제
src_conn.close()
os.unlink(temp_file_path)

cursor = dest_conn.cursor()

# 모든 테이블 이름 가져오기
# 우선 [TESLA_RESTAURANT] 테이블만
cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'TESLA_RESTAURANT';")
tables = cursor.fetchall()

data = {}

# 각 테이블의 데이터를 JSON으로 변환
for table in tables:
    table_name = table[0]
    # cursor.execute(f"SELECT * FROM {table_name}")
    # TEST (TESLA_RESTAURANT 테이블만 들어온다.)
    cursor.execute(f"SELECT * FROM {table_name} " \
            "WHERE base_dt = (SELECT MAX(base_dt) FROM TESLA_RESTAURANT)")
    rows = cursor.fetchall()

    # 컬럼 이름 가져오기
    column_names = [description[0] for description in cursor.description]

    # 데이터를 딕셔너리 리스트로 변환
    table_data = []
    for row in rows:
        table_data.append(dict(zip(column_names, row)))

    data[table_name] = table_data

dest_conn.close()

# JSON 파일로 저장
with open('json/bookmarks.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Conversion completed. JSON file saved as 'json/bookmarks.json'")
