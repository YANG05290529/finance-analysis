from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'finance.db')

# 初始化資料庫
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS personal_financial (
                email TEXT PRIMARY KEY,
                name TEXT,
                phone TEXT,
                income REAL,
                expenses REAL,
                insurance REAL,
                emergencyFund REAL,
                debt REAL,
                rsavings REAL,
                targetSavings REAL,
                riskProfile TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                email TEXT PRIMARY KEY,
                financialHealth TEXT,
                savingsGoal TEXT,
                incomeDistribution TEXT,
                improvementSuggestions TEXT,
                copingStrategies TEXT,
                FOREIGN KEY(email) REFERENCES personal_financial(email)
            )
        ''')
        conn.commit()

# 新增首頁與狀態檢查路由
@app.route("/", methods=["GET"])
def home():
    return "✅ Finance Analysis API is running!"

@app.route("/status", methods=["GET"])
def status():
    return jsonify(success=True, message="API status OK")
@app.route("/")
def index():
    return render_template('index.html')
@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()
        email = data.get('email')

        print("收到資料：", data)  # 除錯用

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 插入或更新 personal_financial
        cursor.execute("SELECT email FROM personal_financial WHERE email = ?", (email,))
        if cursor.fetchone():
            cursor.execute('''
                UPDATE personal_financial SET
                    name = ?, phone = ?, income = ?, expenses = ?, insurance = ?,
                    emergencyFund = ?, debt = ?, rsavings = ?, targetSavings = ?, riskProfile = ?
                WHERE email = ?
            ''', (
                data.get('name'), data.get('phone'), data.get('income'), data.get('expenses'),
                data.get('insurance'), data.get('emergencyFund'), data.get('debt'),
                data.get('rsavings'), data.get('targetSavings'), data.get('riskProfile'), email
            ))
        else:
            cursor.execute('''
                INSERT INTO personal_financial (
                    email, name, phone, income, expenses, insurance, emergencyFund,
                    debt, rsavings, targetSavings, riskProfile
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email, data.get('name'), data.get('phone'), data.get('income'),
                data.get('expenses'), data.get('insurance'), data.get('emergencyFund'),
                data.get('debt'), data.get('rsavings'), data.get('targetSavings'),
                data.get('riskProfile')
            ))

        # 插入或更新 analysis_results
        cursor.execute("SELECT email FROM analysis_results WHERE email = ?", (email,))
        if cursor.fetchone():
            cursor.execute('''
                UPDATE analysis_results SET
                    financialHealth = ?, savingsGoal = ?, incomeDistribution = ?,
                    improvementSuggestions = ?, copingStrategies = ?
                WHERE email = ?
            ''', (
                data.get('financialHealth'), data.get('savingsGoal'),
                data.get('incomeDistribution'), data.get('improvementSuggestions'),
                data.get('copingStrategies'), email
            ))
        else:
            cursor.execute('''
                INSERT INTO analysis_results (
                    email, financialHealth, savingsGoal, incomeDistribution,
                    improvementSuggestions, copingStrategies
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                email, data.get('financialHealth'), data.get('savingsGoal'),
                data.get('incomeDistribution'), data.get('improvementSuggestions'),
                data.get('copingStrategies')
            ))

        conn.commit()
        conn.close()

        return jsonify(success=True, message="資料已成功寫入或更新")

    except Exception as e:
        print("❌ 錯誤：", str(e))
        response = jsonify(success=False, message=str(e))
        response.status_code = 500
        return response

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
