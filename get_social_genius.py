import sqlite3
import json

DB_PATH = "data/radar.db"

def get_product_details(product_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

if __name__ == "__main__":
    details = get_product_details("socialgenius")
    if details:
        print(json.dumps(details, indent=2))
    else:
        print("Product 'socialgenius' not found.")
