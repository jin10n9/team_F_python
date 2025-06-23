# azure_insert.py
import psycopg2
from db_config import DB_CONFIG

def register_to_azure(weather_entry, sales):
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            sslmode=DB_CONFIG["sslmode"]
        )
        cur = conn.cursor()

        insert_sql = """
        INSERT INTO sales_weather (date, temperature, precipitation, sales)
        VALUES (%s, %s, %s, %s)
        """

        cur.execute(insert_sql, (
            weather_entry["date"],                  # 日付
            weather_entry["temperature"],           # 気温（例: 25.3）
            weather_entry["precipitation"],         # 降水量（例: 3.2）
            sales                                    # 売上（int）
        ))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"DB登録エラー: {e}")
