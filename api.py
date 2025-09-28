from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

app = Flask(__name__)

# Cache 2 phút
CACHE = {"fruits": [], "last_update": None}
CACHE_TIMEOUT = 120  # giây
AUTHOR = "Tino_TMH"  # viết tắt tên người làm

def fetch_stock():
    page = "Blox_Fruits_%22Stock%22"
    url = f"https://blox-fruits.fandom.com/api.php?action=parse&page={page}&prop=text&format=json"
    response = requests.get(url)
    data = response.json()
    html_content = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html_content, "html.parser")
    stock_div = soup.find("div", class_="stock-box")
    if not stock_div:
        return None
    fruits = []
    for fruit_div in stock_div.find_all("div", class_="fruit-stock"):
        a_tag = fruit_div.find("a", title=True)
        if a_tag and a_tag["title"] != "Money":
            fruits.append(a_tag["title"])
    return list(dict.fromkeys(fruits))

@app.route("/api/current_stock", methods=["GET"])
def api_current_stock():
    now = datetime.now(timezone.utc)
    if CACHE["last_update"] and (now - CACHE["last_update"]).total_seconds() < CACHE_TIMEOUT:
        return jsonify({
            "status": "ok",
            "fruits": CACHE["fruits"],
            "author": AUTHOR
        })

    try:
        fruits = fetch_stock()
        if fruits is None:
            return jsonify({
                "status": "error",
                "fruits": [],
                "author": AUTHOR,
                "error": "Không tìm thấy stock_div"
            })

        if fruits != CACHE["fruits"]:
            CACHE["fruits"] = fruits.copy()
        CACHE["last_update"] = now

        return jsonify({
            "status": "ok",
            "fruits": CACHE["fruits"],
            "author": AUTHOR
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "fruits": [],
            "author": AUTHOR,
            "error": str(e)
        })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
