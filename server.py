import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/articles", methods=["GET"])
def get_articles():
    """
    This method returns the articles from the database
    """
    conn = sqlite3.connect("verge_articles.db")
    c = conn.cursor()
    c.execute("SELECT * FROM articles")
    data = c.fetchall()
    to_return = []
    for item in data:
        to_return.append({
            "id": item[0],
            "URL": item[1],
            "headline": item[2],
            "author": item[3],
            "date": item[4]
        })
    conn.close()
    return jsonify(to_return)

# run the app
if __name__ == "__main__":
    app.run(debug=True)
