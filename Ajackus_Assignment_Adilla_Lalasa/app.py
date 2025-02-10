from flask import Flask, request, jsonify
import sqlite3
import nltk
from nltk.tokenize import word_tokenize

nltk.download("punkt")

app = Flask(__name__)

# Database connection
def query_db(query, args=()):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.close()
    return result

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask Server is Running! Use /chat to send queries."})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Invalid request. Provide a query."}), 400

    query = data["query"].lower()
    words = word_tokenize(query)

    # Handle queries
    if "employees" in words and "department" in words:
        dept = query.split("department")[-1].strip().replace("?", "")
        employees = query_db("SELECT Name FROM Employees WHERE Department = ?", (dept,))
        return jsonify({"employees": [e[0] for e in employees]})

    elif "manager" in words and "department" in words:
        dept = query.split("department")[-1].strip().replace("?", "")
        manager = query_db("SELECT Manager FROM Departments WHERE Name = ?", (dept,))
        return jsonify({"manager": manager[0][0] if manager else "Not found"})

    elif "hired after" in query:
        date = query.split("after")[-1].strip()
        employees = query_db("SELECT Name FROM Employees WHERE Hire_Date > ?", (date,))
        return jsonify({"employees": [e[0] for e in employees]})

    elif "total salary" in query and "department" in words:
        dept = query.split("department")[-1].strip().replace("?", "")
        total_salary = query_db("SELECT SUM(Salary) FROM Employees WHERE Department = ?", (dept,))
        return jsonify({"total_salary": total_salary[0][0] if total_salary[0][0] else 0})

    else:
        return jsonify({"message": "Query not recognized."})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render assigns a dynamic port
    app.run(host="0.0.0.0", port=port, debug=False)

