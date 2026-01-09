from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import secrets
import html

import db
import auth

# In-memory sessions: {session_id: user_id}
SESSIONS = {}

def page(title: str, body: str) -> bytes:
    html_doc = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; background:#f6f7fb; margin:0; }}
    .wrap {{ max-width: 820px; margin: 40px auto; padding: 0 16px; }}
    .card {{ background:#fff; border:1px solid #e7e7ef; border-radius:14px; padding: 18px; box-shadow: 0 6px 18px rgba(0,0,0,.06); }}
    h1 {{ margin:0 0 10px; font-size: 22px; }}
    p {{ margin: 10px 0; }}
    a {{ color:#2b59ff; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .nav {{ display:flex; gap:12px; margin-bottom:12px; flex-wrap:wrap; }}
    label {{ display:block; margin: 10px 0 6px; font-weight:600; }}
    input {{ width:100%; padding: 10px 12px; border-radius:10px; border:1px solid #d7d7e6; }}
    button {{ width:100%; padding: 10px 12px; border-radius:10px; border:0; background:#111827; color:#fff; font-weight:700; cursor:pointer; }}
    button:hover {{ opacity: .92; }}
    .badge {{ display:inline-block; padding: 4px 10px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size: 12px; }}
    .error {{ background:#fff1f2; border:1px solid #fecdd3; color:#9f1239; padding: 10px 12px; border-radius:10px; }}
    .ok {{ background:#ecfdf5; border:1px solid #bbf7d0; color:#065f46; padding: 10px 12px; border-radius:10px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="nav">
      <a href="/">Home</a>
      <a href="/register">Register</a>
      <a href="/login">Login</a>
      <a href="/profile">Profile</a>
      <a href="/logout">Logout</a>
    </div>
    <div class="card">
      {body}
    </div>
  </div>
</body>
</html>"""
    return html_doc.encode("utf-8")

def get_cookie(headers, name: str):
    cookie = headers.get("Cookie")
    if not cookie:
        return None
    for part in [c.strip() for c in cookie.split(";")]:
        if part.startswith(name + "="):
            return part.split("=", 1)[1]
    return None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_html(200, page("Home", self.home_body()))
            return
        if self.path == "/register":
            self.send_html(200, page("Register", self.register_form()))
            return
        if self.path == "/login":
            self.send_html(200, page("Login", self.login_form()))
            return
        if self.path == "/profile":
            self.handle_profile()
            return
        if self.path == "/logout":
            self.handle_logout()
            return

        self.send_html(404, page("Not Found", "<h1>404</h1><p>Page not found.</p>"))

    def do_POST(self):
        if self.path == "/register":
            self.handle_register()
            return
        if self.path == "/login":
            self.handle_login()
            return

        self.send_html(404, page("Not Found", "<h1>404</h1><p>Page not found.</p>"))

    def send_html(self, status: int, content: bytes, extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(content)

    def read_form(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        return {k: v[0] for k, v in parse_qs(data).items()}

    def current_user(self):
        sid = get_cookie(self.headers, "sid")
        if not sid:
            return None
        user_id = SESSIONS.get(sid)
        if not user_id:
            return None
        return db.get_user_by_id(int(user_id))

    def home_body(self):
        user = self.current_user()
        if user:
            name = html.escape(user["name"])
            return f"""
<h1>Online Shop <span class="badge">Clothes</span></h1>
<p class="ok">Welcome back, <b>{name}</b> ✅</p>
<p>This demo implements two use cases: <b>Register</b> and <b>Login</b> (no frameworks).</p>
<p>Database: <b>MySQL</b></p>
<p>Go to <a href="/profile">Profile</a> to see your info.</p>
"""
        return """
<h1>Online Shop <span class="badge">Clothes</span></h1>
<p>This is a simple Python web app (no frameworks) for the Running Project.</p>
<p>Database: <b>MySQL</b></p>
<p><a href="/register">Register</a> or <a href="/login">Login</a></p>
"""

    def register_form(self, msg: str = "", msg_class: str = "error"):
        alert = f'<div class="{msg_class}">{html.escape(msg)}</div>' if msg else ""
        return f"""
<h1>Register</h1>
{alert}
<form method="POST" action="/register">
  <label>Name</label>
  <input name="name" required placeholder="Your name" />
  <label>Email</label>
  <input name="email" required placeholder="name@example.com" />
  <label>Password</label>
  <input name="password" required type="password" placeholder="********" />
  <div style="height:12px"></div>
  <button type="submit">Create Account</button>
</form>
<p style="margin-top:14px">Already have an account? <a href="/login">Login</a></p>
"""

    def login_form(self, msg: str = "", msg_class: str = "error"):
        alert = f'<div class="{msg_class}">{html.escape(msg)}</div>' if msg else ""
        return f"""
<h1>Login</h1>
{alert}
<form method="POST" action="/login">
  <label>Email</label>
  <input name="email" required placeholder="name@example.com" />
  <label>Password</label>
  <input name="password" required type="password" placeholder="********" />
  <div style="height:12px"></div>
  <button type="submit">Login</button>
</form>
<p style="margin-top:14px">No account yet? <a href="/register">Register</a></p>
"""

    def handle_register(self):
        form = self.read_form()
        name = (form.get("name") or "").strip()
        email = (form.get("email") or "").strip().lower()
        password = form.get("password") or ""

        if len(name) < 2:
            self.send_html(200, page("Register", self.register_form("Name must be at least 2 characters.")))
            return
        if "@" not in email or "." not in email:
            self.send_html(200, page("Register", self.register_form("Please enter a valid email.")))
            return
        if len(password) < 6:
            self.send_html(200, page("Register", self.register_form("Password must be at least 6 characters.")))
            return

        if db.get_user_by_email(email):
            self.send_html(200, page("Register", self.register_form("This email is already registered.")))
            return

        pw_hash = auth.hash_password(password)
        try:
            db.create_user(name, email, pw_hash)
        except Exception:
            self.send_html(200, page("Register", self.register_form("Could not create user (maybe email exists).")))
            return

        user = db.get_user_by_email(email)
        sid = secrets.token_urlsafe(24)
        SESSIONS[sid] = user["id"]
        headers = {"Set-Cookie": f"sid={sid}; HttpOnly; Path=/"}
        self.send_html(200, page("Register", self.login_form("Account created! You are logged in ✅", "ok")), headers)

    def handle_login(self):
        form = self.read_form()
        email = (form.get("email") or "").strip().lower()
        password = form.get("password") or ""

        user = db.get_user_by_email(email)
        if not user or not auth.verify_password(password, user["password_hash"]):
            self.send_html(200, page("Login", self.login_form("Email or password is incorrect.")))
            return

        sid = secrets.token_urlsafe(24)
        SESSIONS[sid] = user["id"]
        headers = {"Set-Cookie": f"sid={sid}; HttpOnly; Path=/"}
        self.send_html(200, page("Login", self.login_form("Logged in successfully ✅", "ok")), headers)

    def handle_profile(self):
        user = self.current_user()
        if not user:
            self.send_html(200, page("Profile", '<h1>Profile</h1><p class="error">You are not logged in.</p><p><a href="/login">Login</a></p>'))
            return
        body = f"""
<h1>Profile</h1>
<p class="ok">Logged in ✅</p>
<p><b>Name:</b> {html.escape(user["name"])}</p>
<p><b>Email:</b> {html.escape(user["email"])}</p>
<p><a href="/logout">Logout</a></p>
"""
        self.send_html(200, page("Profile", body))

    def handle_logout(self):
        sid = get_cookie(self.headers, "sid")
        if sid and sid in SESSIONS:
            del SESSIONS[sid]
        headers = {"Set-Cookie": "sid=deleted; Path=/; Max-Age=0"}
        self.send_html(200, page("Logout", '<h1>Logout</h1><p class="ok">Logged out ✅</p><p><a href="/">Home</a></p>'), headers)

    def log_message(self, format, *args):
        return

def main():
    db.init_db()
    print("Server running on http://localhost:8000")
    HTTPServer(("localhost", 8000), Handler).serve_forever()

if __name__ == "__main__":
    main()
