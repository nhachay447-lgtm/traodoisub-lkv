from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "LKV_MEDIA_PRODUCTION_KEY_2026"

# Giao diện HTML được gộp thẳng vào code Python
HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LKV MEDIA - Hệ Thống Trao Đổi Sub</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #1a1c29; color: #ffffff; display: flex; justify-content: center; padding: 20px; }
        .container { background-color: #23273a; width: 100%; max-width: 450px; border-radius: 20px; padding: 24px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid #3b4160; padding-bottom: 15px; }
        .coin-badge { background-color: #eab308; color: #000; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: bold; }
        .btn-logout { font-size: 12px; color: #f87171; text-decoration: none; margin-top: 4px; display: inline-block; }
        h3 { margin-bottom: 12px; font-size: 16px; color: #94a3b8; text-transform: uppercase; }
        .section { background-color: #2f344d; padding: 16px; border-radius: 12px; margin-bottom: 20px; }
        .job-item { background-color: #1a1c29; border: 1px solid #3b4160; border-radius: 8px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .job-info p { font-size: 14px; font-weight: 500; }
        .job-info span { font-size: 12px; color: #eab308; }
        .btn-job { background-color: #3b82f6; color: white; border: none; padding: 8px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; }
        label { display: block; font-size: 13px; color: #cbd5e1; margin-bottom: 4px; }
        input, select { width: 100%; padding: 10px; background-color: #1a1c29; border: 1px solid #3b4160; border-radius: 6px; color: white; font-size: 14px; margin-bottom: 12px; outline: none; }
        .btn-buy { background-color: #10b981; color: white; border: none; width: 100%; padding: 12px; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <p style="font-size: 14px; color: #94a3b8;">Thành viên,</p>
                <h2 style="font-size: 18px;">{{ username }}</h2>
                <a href="/logout" class="btn-logout">Đăng xuất</a>
            </div>
            <div class="coin-badge">Xu: <span id="coinDisplay">{{ coin_formatted }}</span></div>
        </div>

        <h3>Nhiệm vụ trao đổi chéo</h3>
        <div class="section">
            {% if jobs %}
                {% for job in jobs %}
                <div class="job-item" id="job-card-{{ job.id }}">
                    <div class="job-info">
                        <p>{% if job.type == 'tiktok_follow' %}🚀 Tăng Follow TikTok{% else %}❤️ Tăng Tim TikTok{% endif %}</p>
                        <span>Thưởng: +{{ job.reward }} Xu</span>
                    </div>
                    <button class="btn-job" onclick="doJob('{{ job.id }}', '{{ job.link }}')">Làm NV</button>
                </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; font-size: 14px; color: #94a3b8;">Hệ thống đang đợi cập nhật nhiệm vụ mới!</p>
            {% endif %}
        </div>

        <h3>Mua tương tác (Đổi Xu)</h3>
        <div class="section">
            <label>Loại tương tác:</label>
            <select id="buyType">
                <option value="tiktok_follow">Tăng Follow TikTok (600 Xu/Lượt)</option>
                <option value="tiktok_like">Tăng Tim TikTok (400 Xu/Lượt)</option>
            </select>
            
            <label>Nhập link kênh hoặc video của bạn:</label>
            <input type="text" id="buyLink" placeholder="https://www.tiktok.com/@...">
            
            <label>Số lượng cần mua:</label>
            <input type="number" id="buyQuantity" placeholder="Ví dụ: 10" min="1">
            
            <button class="btn-buy" onclick="buySubChéo()">Cài Đơn Lên Hệ Thống</button>
        </div>
    </div>

    <script>
        function doJob(jobId, link) {
            window.open(link, '_blank');
            alert("Đang chuyển hướng sang TikTok. Bấm nút Follow/Like xong hãy quay lại trang này bấm OK để nhận xu!");
            
            fetch('/api/complete-job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: jobId })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === "success") {
                    alert(data.message);
                    document.getElementById('coinDisplay').innerText = data.new_coin;
                    document.getElementById('job-card-' + jobId).remove();
                } else {
                    alert(data.message);
                }
            });
        }

        function buySubChéo() {
            const type = document.getElementById('buyType').value;
            const link = document.getElementById('buyLink').value.trim();
            const quantity = document.getElementById('buyQuantity').value;

            if(!link || !quantity) { alert("Vui lòng điền đầy đủ link và số lượng!"); return; }

            fetch('/api/create-job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: type, link: link, quantity: quantity })
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if(data.status === "success") {
                    document.getElementById('coinDisplay').innerText = data.new_coin;
                    document.getElementById('buyLink').value = "";
                    document.getElementById('buyQuantity').value = "";
                    setTimeout(() => { location.reload(); }, 500);
                }
            });
        }
    </script>
</body>
</html>
'''

def init_db():
    conn = sqlite3.connect('traodoisub_prod.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            coin INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            link TEXT,
            reward INTEGER,
            remains INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    conn = sqlite3.connect('traodoisub_prod.db')
    cursor = conn.cursor()
    cursor.execute("SELECT coin FROM users WHERE username = ?", (session['username'],))
    user_coin = cursor.fetchone()[0]
    cursor.execute("SELECT id, type, link, reward FROM jobs WHERE remains > 0")
    raw_jobs = cursor.fetchall()
    conn.close()
    
    jobs = [{"id": j[0], "type": j[1], "link": j[2], "reward": j[3]} for j in raw_jobs]
    coin_formatted = f"{user_coin:,}".replace(",", ".")
    
    return render_template_string(HTML_LAYOUT, username=session['username'], coin_formatted=coin_formatted, jobs=jobs)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        conn = sqlite3.connect('traodoisub_prod.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Sai tài khoản hoặc mật khẩu! <a href='/login'>Thử lại</a>"
            
    return '''
        <body style="background:#1a1c29;color:white;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
            <form method="post" style="background:#23273a;padding:30px;border-radius:15px;width:300px;">
                <h2 style="margin-bottom:20px;text-align:center;">LKV MEDIA LOGIN</h2>
                <input type="text" name="username" placeholder="Tên tài khoản" style="width:100%;padding:10px;margin-bottom:15px;background:#1a1c29;border:1px solid #3b4160;color:white;border-radius:5px;" required><br>
                <input type="password" name="password" placeholder="Mật khẩu" style="width:100%;padding:10px;margin-bottom:20px;background:#1a1c29;border:1px solid #3b4160;color:white;border-radius:5px;" required><br>
                <button type="submit" style="width:100%;padding:12px;background:#10b981;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:bold;">Đăng Nhập</button>
                <p style="font-size:13px;text-align:center;margin-top:15px;color:#94a3b8;">Chưa có tài khoản? <a href="/register" style="color:#10b981;">Đăng ký ngay</a></p>
            </form>
        </body>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        if not username or not password:
            return "Không được để trống thông tin!"
            
        try:
            conn = sqlite3.connect('traodoisub_prod.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, coin) VALUES (?, ?, 2000)", (username, password))
            conn.commit()
            conn.close()
            return "Đăng ký thành công! <a href='/login'>Đăng nhập ngay</a>"
        except sqlite3.IntegrityError:
            return "Tài khoản này đã tồn tại! <a href='/register'>Thử lại</a>"
            
    return '''
        <body style="background:#1a1c29;color:white;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
            <form method="post" style="background:#23273a;padding:30px;border-radius:15px;width:300px;">
                <h2 style="margin-bottom:20px;text-align:center;color:#10b981;">ĐĂNG KÝ HỆ THỐNG</h2>
                <input type="text" name="username" placeholder="Tên tài khoản mới" style="width:100%;padding:10px;margin-bottom:15px;background:#1a1c29;border:1px solid #3b4160;color:white;border-radius:5px;" required><br>
                <input type="password" name="password" placeholder="Mật khẩu" style="width:100%;padding:10px;margin-bottom:20px;background:#1a1c29;border:1px solid #3b4160;color:white;border-radius:5px;" required><br>
                <button type="submit" style="width:100%;padding:12px;background:#10b981;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:bold;">Tạo Tài Khoản</button>
                <p style="font-size:13px;text-align:center;margin-top:15px;color:#94a3b8;">Đã có tài khoản? <a href="/login" style="color:#10b981;">Đăng nhập</a></p>
            </form>
        </body>
    '''

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

@app.route('/api/complete-job', methods=['POST'])
def complete_job():
    if 'username' not in session: return jsonify({"status": "error", "message": "Chưa đăng nhập!"})
    data = request.json
    job_id = data.get('job_id')
    conn = sqlite3.connect('traodoisub_prod.db'); cursor = conn.cursor()
    cursor.execute("SELECT reward, remains FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    if not job or job[1] <= 0:
        conn.close(); return jsonify({"status": "error", "message": "Nhiệm vụ hết lượt!"})
    reward_coin = job[0]
    cursor.execute("UPDATE jobs SET remains = remains - 1 WHERE id = ?", (job_id,))
    cursor.execute("UPDATE users SET coin = coin + ? WHERE username = ?", (reward_coin, session['username']))
    cursor.execute("SELECT coin FROM users WHERE username = ?", (session['username'],))
    new_coin = cursor.fetchone()[0]
    conn.commit(); conn.close()
    return jsonify({"status": "success", "message": f"Thành công! +{reward_coin} Xu.", "new_coin": f"{new_coin:,}".replace(",", ".")})

@app.route('/api/create-job', methods=['POST'])
def create_job():
    if 'username' not in session: return jsonify({"status": "error", "message": "Chưa đăng nhập!"})
    data = request.json
    link = data.get('link'); job_type = data.get('type'); quantity = int(data.get('quantity', 0))
    if not link or quantity <= 0: return jsonify({"status": "error", "message": "Thiếu dữ liệu!"})
    price_per_sub = 600 if job_type == "tiktok_follow" else 400
    total_cost = price_per_sub * quantity
    conn = sqlite3.connect('traodoisub_prod.db'); cursor = conn.cursor()
    cursor.execute("SELECT coin FROM users WHERE username = ?", (session['username'],))
    current_coin = cursor.fetchone()[0]
    if current_coin < total_cost:
        conn.close(); return jsonify({"status": "error", "message": "Không đủ xu!"})
    cursor.execute("UPDATE users SET coin = coin - ? WHERE username = ?", (total_cost, session['username']))
    cursor.execute("INSERT INTO jobs (type, link, reward, remains) VALUES (?, ?, ?, ?)", (job_type, link, int(price_per_sub * 0.8), quantity))
    cursor.execute("SELECT coin FROM users WHERE username = ?", (session['username'],))
    new_coin = cursor.fetchone()[0]
    conn.commit(); conn.close()
    return jsonify({"status": "success", "message": f"Đã cài đơn! Trừ {total_cost} Xu.", "new_coin": f"{new_coin:,}".replace(",", ".")})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
