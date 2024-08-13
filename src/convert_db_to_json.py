""" convert_db_to_json """
import sqlite3
import json
import io
import requests

# GitHub Pages에서 DB 파일 다운로드
db_url = 'https://raw.githubusercontent.com/haguri-peng/' \
        'tesla-restaurant/master/db/TeslaRestaurant.db'
response = requests.get(db_url, timeout=10)
response.raise_for_status()  # 오류 발생 시 예외 발생

# 메모리에서 SQLite 데이터베이스 연결
conn = sqlite3.connect(':memory:')

# 바이트 스트림에서 데이터베이스 로드
buffer = io.BytesIO(response.content)
buffer.seek(0)
dest = conn.cursor()
src = sqlite3.connect(buffer)
src.backup(dest)
src.close()

cursor = conn.cursor()

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

conn.close()

# JSON 파일로 저장
with open('json/bookmarks.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Conversion completed. JSON file saved as 'json/bookmarks.json'")
