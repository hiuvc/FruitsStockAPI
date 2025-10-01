from flask import Flask, jsonify
import requests
import threading
import time

app = Flask(__name__)

SOURCE_URL = "https://www.gamersberg.com/api/blox-fruits/stock"
cache_data = {
    "status": "initializing",
    "author": "Tino_TMH",  # 👈 bạn đổi thành tên bạn
    "mirageStock": [],
    "normalStock": []
}

# Hàm cập nhật dữ liệu mỗi 2 phút
def update_stock():
    global cache_data
    while True:
        try:
            response = requests.get(SOURCE_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"]:
                    server_data = data["data"][0]
                    cache_data = {
                        "status": "success",
                        "author": "Hieu Tran",  # 👈 tên tác giả
                        "mirageStock": [
                            {"name": fruit["name"], "price": fruit["price"]}
                            for fruit in server_data.get("mirageStock", [])
                        ],
                        "normalStock": [
                            {"name": fruit["name"], "price": fruit["price"]}
                            for fruit in server_data.get("normalStock", [])
                        ]
                    }
                    print("✅ Đã cập nhật stock thành công.")
                else:
                    cache_data["status"] = "error"
                    print("⚠️ API gốc trả về rỗng.")
            else:
                cache_data["status"] = "error"
                print(f"❌ Lỗi khi gọi API gốc: {response.status_code}")
        except Exception as e:
            cache_data["status"] = "error"
            print("❌ Exception:", e)

        time.sleep(30)  # đợi 2 phút rồi cập nhật lại


@app.route("/fruitstock", methods=["GET"])
def get_fruitstock():
    return jsonify(cache_data)


if __name__ == "__main__":
    # Chạy thread cập nhật dữ liệu
    t = threading.Thread(target=update_stock, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
