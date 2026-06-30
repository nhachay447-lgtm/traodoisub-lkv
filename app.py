from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "LKV_MEDIA_PRODUCTION_KEY_2026"

# ================= GIAO DIỆN CHÍNH (INDEX) =================
HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LKV MEDIA - Hệ Thống Trao Đổi Sub</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #0f111a; color: #ffffff; display: flex; justify-content: center; padding: 20px; }
        .container { background: linear-gradient(145deg, #181a26, #23273a); width: 100%; max-width: 450px; border-radius: 20px; padding: 24px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); border: 1px solid #2f344d; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid #3b4160; padding-bottom: 15px; }
        .coin-badge { background: linear-gradient(90deg, #eab308, #ca8a04); color: #000; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: bold; box-shadow: 0 4px 12px rgba(234,179,8,0.2); }
        .btn-logout { font-size: 13px; color: #f87171; text-decoration: none; margin-top: 6px; display: inline-block; font-weight: 500; }
        h3 { margin-bottom: 12px; font-size: 15px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        .section { background-color: #1e2235; padding: 16px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #2f344d; }
        .job-item { background-color: #131622; border: 1px solid #2f344d; border-radius: 8px; padding: 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .job-info p { font-size: 14px; font-weight: 600; color: #e2e8f0; }
        .job-info span { font-size: 12px; color: #eab308; font-weight: 500; }
        .btn-job { background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 10px rgba(37,99,235,0.2); }
        label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 6px; font-weight: 500; }
        input, select { width: 100%; padding: 12px; background-color: #131622; border: 1px solid #2f344d; border-radius: 8px; color: white; font-size: 14px; margin-bottom: 14px; outline: none; transition: 0.3s; }
        input:focus, select:focus { border-color: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.2); }
        .btn-buy { background: linear-gradient(90deg, #10b981, #059669); color: white; border: none; width: 100%; padding: 14px; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(16,185,129,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <p style="font-size: 13px; color: #94a3b8;">Thành viên,</p>
                <h2 style="font-size: 20px; color: #f1f5f9;">{{ username }}</h2>
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
                <p style="text-align: center; font-size: 14px; color: #94a3b8; padding: 10px 0;">Hệ thống đang đợi cập nhật nhiệm vụ mới!</p>
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
            alert("Đang chuyển hướng sang TikTok. Hãy bấm nút Follow/Like xong quay lại trang này bấm OK để nhận xu!");
            
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

# ================= GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ MỚI XỊN HƠN =================
AUTH_LAYOUT = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LKV MEDIA - Auth</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #0c0e17; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; padding: 15px; }
        .auth-card { background: #161925; padding: 35px 25px; border-radius: 16px; width: 100%; max-width: 360px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); border: 1px solid #23283c; position: relative; }
        .auth-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #10b981, #3b82f6); border-top-left-radius: 16px; border-top-right-radius: 16px; }
        h2 { margin-bottom: 24px; text-align: center; font-size: 22px; font-weight: 700; letter-spacing: 1px; }
        .title-login { color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.1); }
        .title-register { color: #10b981; text-shadow: 0 0 10px rgba(16,185,129,0.2); }
        input { width: 100%; padding: 12px; margin-bottom: 16px; background: #0c0e17; border: 1px solid #2a314a; color: white; border-radius: 8px; font-size: 14px; outline: none; transition: 0.3s; }
        input:focus { border-color: #3b82f6; box-shadow: 0 0 8px rgba(59,130,246,0.3); }
        button { width: 100%; padding: 13px; background: linear-gradient(90deg, #10b981, #059669); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: bold; transition: 0.3s; box-shadow: 0 4px 12px rgba(16,185,129,0.2); margin-bottom: 10px; }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        .switch-mode { font-size: 13px; text-align: center; margin-top: 15px; color: #64748b; }
        .switch-mode a { color: #10b981; text-decoration: none; font-weight: 600; }
        /* Khu vực hiện chữ báo lỗi nhỏ dưới nút bấm */
        #msgBox { text-align: center; font-size: 13px; font-weight: 500; margin-top: 10px; min-height: 20px; transition: 0.3s; }
        .msg-error { color: #f87171; }
        .msg-success { color: #34d399; }
    </style>
</head>
<body>
    <div class="auth-card">
        {% if mode == 'login' %}
            <h2 class="title-login">LKV MEDIA LOGIN</h2>
            <form id="authForm">
                <input type="text" id="username" placeholder="Tên tài khoản" required>
                <input type="password" id="password" placeholder="Mật khẩu" required>
                <button type="submit">Đăng Nhập</button>
            </form>
            <div id="msgBox"></div>
            <p class="switch-mode">Chưa có tài khoản? <a href="/register">Đăng ký ngay</a></p>
        {% else %}
            <h2 class="title-register">ĐĂNG KÝ HỆ THỐNG</h2>
            <form id="authForm">
                <input type="text" id="username" placeholder="Tên tài khoản mới" required>
                <input type="password" id="password" placeholder="Mật khẩu" required>
                <button type="submit" style="background: linear-gradient(90deg, #3b82f6, #1d4ed8); box-shadow: 0 4px 12px rgba(59,130,246,0.2);">Tạo Tài Khoản</button>
            </form>
            <div id="msgBox"></div>
            <p class="switch-mode">Đã có tài khoản? <a href="/login" style="color:#3b82f6;">Đăng nhập</a></p>
        {% endif %}
    </div>

    <script>
        document.getElementById('authForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const user = document.getElementById('username').value.trim();
            const pass = document.getElementById('password').value.trim();
            const msgBox = document.getElementById('msgBox');
            
            msgBox.innerHTML = "Đang xử lý...";
            msgBox.className = "";

            const targetUrl = "{{ 'api/login' if mode == 'login' else 'api/register' }}";

            fetch('/' + targetUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: user, password: pass })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === "success") {
                    msgBox.innerHTML = data.message;
                    msgBox.className = "msg-success";
                    if ("{{ mode }}" === "login") {
                        setTimeout(() => { window.location.href = "/"; }, 800);
                    } else {
                        setTimeout(() => { window.location.href = "/login"; }, 1200);
                    }
                } else {
                    msgBox.innerHTML = data.message;
                    msgBox.className = "msg-error";
                }
            })
            .catch(() => {
                msgBox.innerHTML = "Lỗi kết nối máy chủ!";
                msgBox.className = "msg-error";
            });
        });
    </script>
</body>
</html>
'''

# ================= CODE LOGIC BACKEND XỬ LÝ DỮ LIỆU =================
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

@app.route('/login')
def login_page():
    if 'username' in session: return redirect(url_for('index'))
    return render_template_string(AUTH_LAYOUT, mode='login')

@app.route('/register')
def register_page():
    if 'username' in session: return redirect(url_for('index'))
    return render_template_string(AUTH_LAYOUT, mode='register')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Vui lòng điền đủ thông tin!"})
        
    conn = sqlite3.connect('traodoisub_prod.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['username'] = username
        return jsonify({"status": "success", "message": "Đăng nhập thành công! Đang chuyển hướng..."})
    else:
        return jsonify({"status": "error", "message": "Sai tài khoản hoặc mật khẩu!"})

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Không được để trống thông tin!"})
        
    try:
        conn = sqlite3.connect('traodoisub_prod.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, coin) VALUES (?, ?, 2000)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Đăng ký thành công! Đang chuyển sang đăng nhập..."})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Tài khoản này đã tồn tại rồi!"})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

@app.route('/api/complete-job', methods=['POST'])
def complete_job():
    if 'username' not in session: return jsonify({"status": "error", "message": "Chưa đăng nhập!"})
    data = request.json or {}
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
    data = request.json or {}
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
