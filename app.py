import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import re
import json
import os
import sqlite3
import requests
import urllib3
import urllib.parse
import glob
import hashlib
import streamlit.components.v1 as components
from datetime import datetime
from contextlib import contextmanager
# pyrefly: ignore [missing-import]
import plotly.express as px

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_FOLDER   = "database_chatbot"
FOLDER_TARGET = os.path.join(BASE_FOLDER, "nasional_datagoid")
DB_PATH       = os.path.join(BASE_FOLDER, "leres_history.db")
os.makedirs(FOLDER_TARGET, exist_ok=True)

# ==========================================
# 1. API KEYS
# ==========================================
API_KEYS_DICT = {
    " Nusantara 1.0 ": st.secrets["API_KEY_1"],
    " Nusantara 2.0 ": st.secrets["API_KEY_2"],
    " Nusantara 3.0 ": st.secrets["API_KEY_3"],
    # "\U0001f511 Key 2 (Cadangan 1)": "MASUKKAN_API_KEY_2_DI_SINI",
}
API_KEYS_VALID = {
    lbl: k for lbl, k in API_KEYS_DICT.items()
    if k and not k.startswith("MASUKKAN_")
}

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="LERES \u2013 Layanan E-Gov Rekomendasi & Edukasi Smart",
    page_icon="\U0001f6e1\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp{background:#0F172A;color:#F8FAFC;font-family:'Inter',sans-serif;}

section[data-testid="stSidebar"]{
    background:#1E293B!important;
    border-right:1px solid #334155;
    min-width:240px!important;
    max-width:260px!important;
    height:100vh!important;
}
section[data-testid="stSidebar"] > div:first-child{
    overflow-y:auto!important;
    padding:10px 12px!important;
    height:100vh!important;
    display:flex!important;
    flex-direction:column!important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{margin:0 0 4px 0!important;font-size:1.1rem!important;}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] .stCaption{font-size:.72rem!important;margin:0!important;}
section[data-testid="stSidebar"] hr{margin:6px 0!important;}
section[data-testid="stSidebar"] .stSelectbox label{font-size:.73rem!important;}
section[data-testid="stSidebar"] .stButton button{padding:4px 10px!important;font-size:.75rem!important;}

.cb-user{
    background:#b76216;color:#fff;
    padding:10px 14px;border-radius:16px 16px 2px 16px;
    margin:6px 0 6px 18%;line-height:1.5;}
.cb-bot{
    background:#1E293B;color:#F8FAFC;border:1px solid #334155;
    padding:10px 14px;border-radius:16px 16px 16px 2px;
    margin:6px 18% 6px 0;line-height:1.6;}

.badge{display:inline-block;padding:2px 9px;border-radius:20px;
       font-size:.78rem;font-weight:700;color:#fff!important;}
.b-valid{background:#10B981;}.b-hoaks{background:#EF4444;}.b-unclear{background:#F59E0B;}

.stButton>button,.stLinkButton>a{
    background:#6366F1!important;color:#fff!important;
    border-radius:8px!important;border:none!important;
    padding:6px 14px!important;font-size:.82rem!important;
    transition:all .2s ease!important;margin-right:6px!important;}
.stButton>button:hover,.stLinkButton>a:hover{
    background:#4F46E5!important;box-shadow:0 0 10px rgba(99,102,241,.45)!important;}

.section-label{
    font-size:.65rem;font-weight:700;color:#64748B;
    text-transform:uppercase;letter-spacing:.08em;margin:8px 0 4px 0;}

/* ── History: switch button = card itself ── */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button {
    text-align: left !important;
    padding: 8px 10px !important;
    min-height: 52px !important;
    height: auto !important;
    line-height: 1.5 !important;
    white-space: pre-line !important;
    font-size: .72rem !important;
    justify-content: flex-start !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
}
/* Inactive — dark card look */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button[kind="secondary"] {
    background: #0F172A !important;
    border: 1px solid #334155 !important;
    color: #CBD5E1 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button[kind="secondary"]:hover {
    background: #1a2744 !important;
    border-color: #6366F1 !important;
    color: #F8FAFC !important;
    box-shadow: none !important;
}
/* Active — purple accent */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button[kind="primary"] {
    background: #1e1f4a !important;
    border: 1px solid #6366F1 !important;
    color: #F8FAFC !important;
    box-shadow: none !important;
}

/* ── History: delete button ── */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
    min-height: 52px !important;
    height: 52px !important;
    width: 100% !important;
    padding: 0 !important;
    font-size: 1rem !important;
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #EF4444 !important;
    box-shadow: none !important;
    transition: background .2s, border-color .2s !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button:hover {
    background: rgba(239,68,68,.15) !important;
    border-color: #EF4444 !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. GEMINI CALL
# ==========================================
def run_gemini(prompt, system="", json_mode=False):
    keys = []
    sel = st.session_state.get("selected_api_key_label")
    if sel and sel in API_KEYS_VALID:
        keys.append(API_KEYS_VALID[sel])
    for k in API_KEYS_VALID.values():
        if k not in keys:
            keys.append(k)
    env = os.environ.get("GEMINI_API_KEY")
    if env and env not in keys:
        keys.append(env)
    if not keys:
        raise RuntimeError("Tidak ada API key valid.")

    gen_cfg = {"response_mime_type": "application/json"} if json_mode else {}
    last_err = RuntimeError("Semua model gagal.")
    for key in keys:
        genai.configure(api_key=key)
        for model_name in ["gemini-3.5-flash", "gemini-3.5-flash-latest", "gemini-pro"]:
            try:
                mdl = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=gen_cfg,
                    system_instruction=system or None
                )
                return mdl.generate_content(prompt).text
            except Exception as e:
                last_err = e
                continue
    raise last_err

# ==========================================
# 4. CKAN HARVESTER
# ==========================================
def harvest_datagoid(progress_fn=None):
    URL_API = "https://data.go.id/api/3/action/package_search?q=*:*&rows=1000"
    if progress_fn:
        progress_fn("Menghubungi data.go.id\u2026")
    try:
        resp = requests.get(URL_API, timeout=30, verify=False)
        if resp.status_code != 200:
            return 0
        datasets = resp.json()["result"]["results"]
    except Exception as e:
        if progress_fn:
            progress_fn(f"Gagal: {e}")
        return 0

    downloaded = 0
    for data in datasets:
        for resource in data.get("resources", []):
            fmt = (resource.get("format") or "").lower()
            if fmt not in ("csv", "json"):
                continue
            url = resource.get("url", "")
            if not url.startswith("http"):
                continue
            raw_name = resource.get("name") or resource.get("id") or "unnamed"
            clean = "".join(c for c in raw_name if c.isalnum() or c in " _-").rstrip()[:80]
            uid   = hashlib.md5(url.encode()).hexdigest()[:6]
            fname = os.path.join(FOLDER_TARGET, f"{clean}_{uid}.{fmt}")
            if os.path.exists(fname):
                downloaded += 1
                continue
            try:
                fd = requests.get(url, timeout=20, verify=False)
                if fd.status_code == 200:
                    with open(fname, "wb") as f:
                        f.write(fd.content)
                    downloaded += 1
            except Exception:
                continue
    return downloaded

# ==========================================
# 5. LOCAL FILE SCANNER
# ==========================================
def get_local_files():
    files = []
    for ext in ("*.csv", "*.json"):
        files.extend(glob.glob(f"{BASE_FOLDER}/**/{ext}", recursive=True))
    return files

def best_file(query, files):
    words = query.lower().split()
    scores = {}
    for f in files:
        s = sum(10 for w in words if w in os.path.basename(f).lower())
        if s:
            scores[f] = s
    return max(scores, key=scores.get) if scores else None

def file_context(path):
    try:
        if path.endswith(".csv"):
            df = pd.read_csv(path, nrows=15)
            return f"[{os.path.basename(path)}]\n{df.to_string()}"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return f"[{os.path.basename(path)}]\n{json.dumps(data[:5], indent=2)}"
        return f"[{os.path.basename(path)}]\n{json.dumps(data, indent=2)[:3000]}"
    except Exception as e:
        return f"Gagal baca file: {e}"

MOCK = {
    "pkh":  "PKH \u2013 Program Keluarga Harapan: terdaftar DTKS. https://cekbansos.kemensos.go.id",
    "bpjs": "KIS/PBI \u2013 iuran BPJS dibayar pemerintah. https://bpjs-kesehatan.go.id",
    "kip":  "KIP Kuliah \u2013 beasiswa PTN/PTS keluarga kurang mampu. https://kip-kuliah.kemdikbud.go.id",
    "bnpb": "Bantuan Bencana \u2013 logistik, tenda, sembako. https://bnpb.go.id",
    "dtks": "DTKS \u2013 basis data penerima bansos Kemensos. https://dtks.kemensos.go.id",
}
def mock_context(query):
    ql = query.lower()
    return "\n".join(v for k, v in MOCK.items() if k in ql) or ""

# ==========================================
# 6. PROFANITY FILTER
# ==========================================
KATA_KASAR = {
    "anjing","babi","bangsat","bajingan","goblok","tolol",
    "kontol","memek","brengsek","ngentot","jancok","ndasmu",
    "fuck","shit","asshole","bitch","damn"
}
def is_rude(text):
    return any(re.search(rf"\b{w}\b", text.lower()) for w in KATA_KASAR)

def get_button_label(url):
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc or parsed.path.split('/')[0]
        if netloc.startswith("www."):
            netloc = netloc[4:]
        if ".go.id" in netloc.lower():
            return f"\U0001f310 Sumber Resmi Pemerintah ({netloc})"
        return f"\U0001f310 Sumber Resmi ({netloc})"
    except Exception:
        return "\U0001f310 Sumber Resmi Pemerintah (.go.id)"

# ==========================================
# 7. CHART RENDERER
# ==========================================
def render_chart(tag_json):
    try:
        cd = json.loads(tag_json)
    except Exception:
        return False

    title  = cd.get("title", "Visualisasi")
    labels = cd.get("labels", [])
    values = cd.get("values", [])
    ctype  = cd.get("type", "bar").lower()
    xlabel = cd.get("xlabel", "")
    ylabel = cd.get("ylabel", "")

    if not labels or not values:
        return False
    try:
        values = [float(v) for v in values]
    except Exception:
        return False

    df = pd.DataFrame({"Kategori": labels, "Jumlah": values})
    theme_layout = {
        "paper_bgcolor": "#1E293B", "plot_bgcolor": "#1E293B",
        "font": {"color": "#F8FAFC", "family": "Inter, sans-serif"},
        "margin": {"l": 40, "r": 20, "t": 40, "b": 45},
        "title": {"font": {"size": 12, "color": "#F8FAFC", "weight": "bold"}},
        "xaxis": {"gridcolor": "#334155", "zerolinecolor": "#334155", "tickfont": {"size": 9}},
        "yaxis": {"gridcolor": "#334155", "zerolinecolor": "#334155", "tickfont": {"size": 9}},
    }

    if ctype == "line":
        fig = px.line(df, x="Kategori", y="Jumlah", title=title, markers=True)
        fig.update_traces(line=dict(color="#6366F1", width=2.5), marker=dict(size=7, color="#818CF8"))
    elif ctype == "pie":
        fig = px.pie(df, names="Kategori", values="Jumlah", title=title,
                     color_discrete_sequence=px.colors.sequential.Plasma_r)
        fig.update_traces(textposition="inside", textinfo="percent+label")
    else:
        fig = px.bar(df, x="Kategori", y="Jumlah", title=title,
                     color_discrete_sequence=["#6366F1"])
        fig.update_traces(marker_line_color="#818CF8", marker_line_width=1, opacity=0.9)

    fig.update_layout(**theme_layout)
    if xlabel:
        fig.update_xaxes(title_text=xlabel, title_font={"size": 10, "color": "#94A3B8"})
    else:
        fig.update_xaxes(title_text=None)
    if ylabel:
        fig.update_yaxes(title_text=ylabel, title_font={"size": 10, "color": "#94A3B8"})
    else:
        fig.update_yaxes(title_text=None)

    fig.update_layout(width=480, height=280)
    col_chart, _ = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    return True

# ==========================================
# 8. INSTANSI CONTACT
# ==========================================
INSTANSI_MAP = [
    {"keywords": ["kip","kuliah","beasiswa","pendidikan","sekolah","ptn","pts","kemendikbud"],
     "nama": "Kemendikbudristek", "telp": "177",
     "portal": "https://kip-kuliah.kemdikbud.go.id", "label": "Pendidikan / KIP Kuliah"},
    {"keywords": ["bpjs","kesehatan","pkm","puskesmas","rawat","obat","rumah sakit","kis","pbi"],
     "nama": "BPJS Kesehatan", "telp": "165",
     "portal": "https://bpjs-kesehatan.go.id", "label": "Kesehatan / BPJS"},
    {"keywords": ["pkh","bansos","dtks","kemensos","sembako","beras","raskin","bpnt","kks"],
     "nama": "Kementerian Sosial", "telp": "171",
     "portal": "https://cekbansos.kemensos.go.id", "label": "Bansos / Sosial"},
    {"keywords": ["gempa","banjir","bencana","longsor","bnpb","bpbd","evakuasi","darurat"],
     "nama": "BNPB / BPBD", "telp": "112",
     "portal": "https://bnpb.go.id", "label": "Bencana / Darurat"},
    {"keywords": ["hoaks","hoax","berita palsu","disinformasi","kominfo","konten","internet"],
     "nama": "Kominfo", "telp": "159",
     "portal": "https://kominfo.go.id", "label": "Hoaks / Konten Digital"},
]

def detect_instansi(text):
    tl = text.lower()
    best, best_score = None, 0
    for inst in INSTANSI_MAP:
        score = sum(1 for kw in inst["keywords"] if kw in tl)
        if score > best_score:
            best_score = score
            best = inst
    return best

def render_contact_button(combined_text, key_suffix=""):
    inst = detect_instansi(combined_text)
    if inst is None:
        return
    st.markdown(
        f"<small style='color:#64748B'>\U0001f4de Hubungi: **{inst['nama']}** \u2014 "
        f"<a href='{inst['portal']}' target='_blank' style='color:#6366F1'>"
        f"{inst['portal'].replace('https://','')}</a> "
        f"| Call Center: **{inst['telp']}**</small>",
        unsafe_allow_html=True
    )

# ==========================================
# 9. SQLITE DATABASE LAYER
# ==========================================
@contextmanager
def _db():
    """Context manager untuk koneksi SQLite yang aman."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def db_init():
    """Buat tabel jika belum ada."""
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                title       TEXT NOT NULL DEFAULT 'Percakapan Baru',
                created_at  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                urls        TEXT DEFAULT '[]',
                chart_tag   TEXT DEFAULT '',
                hoax_tag    TEXT DEFAULT '',
                topic_text  TEXT DEFAULT '',
                created_at  TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_msgs_session ON messages(session_id);
        """)

def db_get_sessions():
    """Ambil semua sesi, urut terbaru dulu."""
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at FROM sessions ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]

def db_create_session(sid, title="Percakapan Baru"):
    """Buat sesi baru dan tambahkan pesan selamat datang."""
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    with _db() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)",
            (sid, title, now)
        )
        conn.execute(
            """INSERT INTO messages
               (session_id, role, content, urls, chart_tag, hoax_tag, topic_text, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (sid, "bot",
             "Selamat datang di LERES. Sampaikan kebutuhan atau pertanyaan Anda, dan kami akan membantu menemukan informasi layanan publik yang sesuai berdasarkan sumber resmi.",
             "[]", "", "", "", now)
        )

def db_get_messages(session_id):
    """Ambil semua pesan dari satu sesi."""
    with _db() as conn:
        rows = conn.execute(
            """SELECT role, content, urls, chart_tag, hoax_tag, topic_text
               FROM messages WHERE session_id = ? ORDER BY id ASC""",
            (session_id,)
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["urls"] = json.loads(d["urls"])
        except Exception:
            d["urls"] = []
        result.append(d)
    return result

def db_add_message(session_id, role, content, urls=None, chart_tag="", hoax_tag="", topic_text=""):
    """Simpan satu pesan ke DB."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    urls_json = json.dumps(urls or [])
    with _db() as conn:
        conn.execute(
            """INSERT INTO messages
               (session_id, role, content, urls, chart_tag, hoax_tag, topic_text, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, role, content, urls_json, chart_tag or "", hoax_tag or "", topic_text or "", now)
        )

def db_update_title(session_id, title):
    """Update judul sesi."""
    with _db() as conn:
        conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))

def db_delete_session(session_id):
    """Hapus sesi beserta semua pesannya."""
    with _db() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

def db_session_exists(session_id):
    with _db() as conn:
        row = conn.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,)).fetchone()
    return row is not None

def db_session_title_is_default(session_id):
    with _db() as conn:
        row = conn.execute("SELECT title FROM sessions WHERE id = ?", (session_id,)).fetchone()
    return row and row["title"] == "Percakapan Baru"

# ==========================================
# 10. SESSION STATE HELPERS
# ==========================================
def _new_session_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def _init_app():
    """Inisialisasi DB dan session state saat pertama kali load."""
    db_init()
    sessions = db_get_sessions()
    if not sessions:
        sid = _new_session_id()
        db_create_session(sid)
        st.session_state.active_session = sid
    elif "active_session" not in st.session_state:
        st.session_state.active_session = sessions[0]["id"]

def _create_new_session():
    sid = _new_session_id()
    db_create_session(sid)
    st.session_state.active_session = sid

def _delete_session(sid):
    db_delete_session(sid)
    sessions = db_get_sessions()
    if not sessions:
        _create_new_session()
    else:
        st.session_state.active_session = sessions[0]["id"]

def _append_bot(content, urls=None, chart_tag="", hoax_tag="", topic_text=""):
    sid = st.session_state.active_session
    db_add_message(sid, "bot", content, urls, chart_tag, hoax_tag, topic_text)

def _append_user(content):
    sid = st.session_state.active_session
    db_add_message(sid, "user", content)
    # Update judul sesi jika masih default
    if db_session_title_is_default(sid):
        title = content[:35] + ("\u2026" if len(content) > 35 else "")
        db_update_title(sid, title)

# ==========================================
# INIT APP
# ==========================================
_init_app()

# ==========================================
# 11. SIDEBAR \u2014 dengan history permanen
# ==========================================
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:12px 10px;background:#0F172A;border-radius:12px;"
        "border:1px solid #334155;margin-bottom:10px;'>"
        "<span style='font-size:1.8rem'>\U0001f6e1\ufe0f</span><br>"
        "<b style='font-size:1.1rem;color:#F8FAFC;letter-spacing:0.5px;'>LERES</b><br>"
        "<div style='color:#94A3B8;font-size:.68rem;margin-top:2px;'>"
        "Layanan E-Government Rekomendasi &amp; Edukasi Smart</div>"
        "</div>",
        unsafe_allow_html=True
    )


    # API Key Selector
    key_opts = list(API_KEYS_VALID.keys())
    if key_opts:
        sel_lbl = st.selectbox("model:", key_opts, key="selected_api_key_label")
    else:
        st.warning("\u26a0\ufe0f Isi API key di app.py")

    st.markdown("<hr style='margin:10px 0;border-color:#334155;'>", unsafe_allow_html=True)

    # Tombol Chat Baru
    if st.button("\u270f\ufe0f Chat Baru", use_container_width=True, key="btn_new_chat"):
        _create_new_session()
        st.rerun()

    st.markdown("<div class='section-label'>Riwayat Percakapan</div>", unsafe_allow_html=True)

    # Daftar sesi dari DB
    all_sessions = db_get_sessions()
    active_sid   = st.session_state.active_session

    if not all_sessions:
        st.markdown("<div style='color:#64748B;font-size:.72rem;text-align:center;padding:10px;'>Belum ada riwayat</div>", unsafe_allow_html=True)
    else:
        for sess in all_sessions:
            sid       = sess["id"]
            is_active = sid == active_sid
            icon = "\U0001f4ac" if is_active else "\U0001f5d2\ufe0f"

            col_hist, col_del = st.columns([5, 1])
            with col_hist:
                # Button IS the card — label: 2 baris (judul + tanggal)
                label = f"{icon} {sess['title']}\n{sess['created_at']}"
                if st.button(label, key=f"sw_{sid}",
                             use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    st.session_state.active_session = sid
                    st.rerun()

            with col_del:
                if st.button("\U0001f5d1", key=f"del_{sid}",
                             use_container_width=True, help="Hapus sesi ini"):
                    _delete_session(sid)
                    st.rerun()




# ==========================================
# 12. CHAT PAGE
# ==========================================
st.title("\U0001f6e1\ufe0f LERES AI")
st.caption("Temukan Informasi Layanan Publik Resmi dengan Cepat dan Mudah")

# Render semua pesan dari sesi aktif (baca dari DB)
active_msgs = db_get_messages(st.session_state.active_session)

for i, msg in enumerate(active_msgs):
    if msg["role"] == "user":
        st.markdown(f'<div class="cb-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="cb-bot">{msg["content"]}</div>', unsafe_allow_html=True)

        if msg.get("chart_tag"):
            render_chart(msg["chart_tag"])

        for j, u in enumerate((msg.get("urls") or [])[:3]):
            lbl = get_button_label(u)
            st.link_button(lbl, u, key=f"src_{i}_{j}")

        topic_text = msg.get("topic_text", "")
        if topic_text:
            render_contact_button(topic_text, key_suffix=str(i))

        hoax_tag = msg.get("hoax_tag", "")
        if hoax_tag:
            try:
                hd     = json.loads(hoax_tag)
                claim  = hd.get("claim", "")
                status = hd.get("status", "HOAKS")
                bclass = "b-hoaks" if status == "HOAKS" else ("b-valid" if status == "VALID" else "b-unclear")
                st.markdown(f'<span class="badge {bclass}">{status}</span>', unsafe_allow_html=True)
                if status in ("HOAKS", "BUTUH KLARIFIKASI"):
                    txt = urllib.parse.quote(f'Laporan hoaks:\n"{claim}"\nMohon ditindaklanjuti.')
                    st.link_button("\U0001f4f2 Laporkan ke Kominfo (WA)",
                                   f"https://wa.me/6281111111111?text={txt}", key=f"wa_{i}")
            except Exception:
                pass

# ==========================================
# 13. CHAT INPUT PROCESSING
# ==========================================
user_input = st.chat_input("Tanya bansos, cek hoaks, minta grafik\u2026")

if user_input:
    st.markdown(f'<div class="cb-user">{user_input}</div>', unsafe_allow_html=True)
    _append_user(user_input)   # simpan ke DB

    if is_rude(user_input):
        warn = "Yuk gunakan bahasa yang sopan supaya aku bisa bantu dengan baik \U0001f60a"
        st.markdown(f'<div class="cb-bot">{warn}</div>', unsafe_allow_html=True)
        _append_bot(warn)
    else:
        local_files = get_local_files()
        ctx     = ""
        src_url = "https://data.go.id"

        matched = best_file(user_input, local_files)
        if matched:
            ctx = file_context(matched)
        else:
            ctx = mock_context(user_input)

        viz_kw = ["grafik","chart","diagram","visualisasi","tabel","perbandingan",
                  "bandingkan","statistik","distribusi","jumlah","persen","proporsi","plot"]
        needs_viz = any(kw in user_input.lower() for kw in viz_kw)

        sys_prompt = f"""Kamu adalah LERES, asisten layanan publik yang santai, to-the-point, dan ramah kayak teman.

WAKTU: {datetime.now().strftime('%d %B %Y %H:%M')}

GAYA: jawab singkat & kasual. Kalau user curhat/galau, validasi dulu sebelum kasih solusi. Jangan sapaan ulang.

ATURAN:
1. Jangan tempel URL mentah di jawaban. Taruh sumber resmi di [SOURCES:["https://sumber1.go.id","https://sumber2.go.id"]] di akhir.
   Setiap URL wajib merupakan website resmi pemerintah Indonesia yang mengandung `.go.id`.
2. Hoaks: tambahkan [HOAKS_CHECK:{{"claim":"...","status":"HOAKS"|"VALID"|"BUTUH KLARIFIKASI"}}]
3. Grafik: {"WAJIB buat grafik karena user minta! " if needs_viz else ""}Kalau ada angka yang cocok divisualisasikan, tambahkan:
   [CHART:{{"title":"...","type":"bar"|"line"|"pie","labels":[...],"values":[angka_murni],"xlabel":"...","ylabel":"..."}}]
   - values hanya angka (float/int), bukan string
   - Kalau perbandingan, buat juga tabel markdown
4. Konteks data:
{ctx if ctx else "Tidak ada data lokal. Jawab dari pengetahuan umum kamu."}
"""

        raw = None
        api_error = None
        with st.spinner("Bentar ya\u2026"):
            try:
                raw = run_gemini(user_input, sys_prompt)
            except Exception as e:
                api_error = e

        if api_error is not None:
            err_str = str(api_error).lower()
            is_quota = "429" in err_str or "resource exhausted" in err_str or "quota" in err_str
            if is_quota:
                fallback = (
                    "\u26a0\ufe0f Model sedang over-limit (429 Resource Exhausted).\n\n"
                    "Silakan ganti model di dropdown model: di sidebar, lalu kirim ulang pertanyaanmu ya!"
                )
            else:
                fallback = (
                    f"\u26a0\ufe0f Gagal hubungi AI: `{api_error}`\n\n"
                    "Coba ganti model di sidebar atau coba lagi sebentar."
                )
            st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
            _append_bot(fallback)


        elif raw is None:
            fallback = "Hmm, nggak dapat respons dari AI. Coba lagi ya!"
            st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
            _append_bot(fallback, urls=["https://data.go.id"])

        else:
            chart_tag = ""
            hoax_tag  = ""
            sources   = []

            cm = re.search(r'\[CHART:(\{.*?\})\]', raw, re.DOTALL)
            if cm:
                chart_tag = cm.group(1)
                raw = raw[:cm.start()] + raw[cm.end():]

            hm = re.search(r'\[HOAKS_CHECK:(\{.*?\})\]', raw, re.DOTALL)
            if hm:
                hoax_tag = hm.group(1)
                raw = raw[:hm.start()] + raw[hm.end():]

            sm = re.search(r'\[SOURCES:(\[.*?\])\]', raw, re.DOTALL)
            if sm:
                try:
                    sources = json.loads(sm.group(1))
                except Exception:
                    sources = []
                raw = raw[:sm.start()] + raw[sm.end():]

            if not sources:
                raw_urls = re.findall(r'https?://[^\s\)\]>"\']+', raw)
                sources  = [u.rstrip('.,;)">\x27') for u in raw_urls]
                for u in raw_urls:
                    raw = raw.replace(u, "")

            sources = [u for u in sources if ".go.id" in u.lower()]
            if not sources:
                sources = [src_url]

            clean_resp = re.sub(r'\n{3,}', '\n\n', raw).strip()

            st.markdown(f'<div class="cb-bot">{clean_resp}</div>', unsafe_allow_html=True)

            if chart_tag:
                render_chart(chart_tag)

            unique_srcs = list(dict.fromkeys(sources))[:3]
            for j, u in enumerate(unique_srcs):
                lbl = get_button_label(u)
                st.link_button(lbl, u, key=f"src_new_{j}")

            topic_text = user_input + " " + clean_resp
            render_contact_button(topic_text, key_suffix="new")

            if hoax_tag:
                try:
                    hd     = json.loads(hoax_tag)
                    claim  = hd.get("claim", "")
                    status = hd.get("status", "HOAKS")
                    bclass = "b-hoaks" if status == "HOAKS" else ("b-valid" if status == "VALID" else "b-unclear")
                    st.markdown(f'<span class="badge {bclass}">{status}</span>', unsafe_allow_html=True)
                    if status in ("HOAKS", "BUTUH KLARIFIKASI"):
                        txt = urllib.parse.quote(f'Laporan hoaks:\n"{claim}"\nMohon ditindaklanjuti.')
                        st.link_button(" Laporkan ke Admin (WA)",
                                       f"https://wa.me/62895605210076?text={txt}", key="wa_new")
                except Exception:
                    pass

            _append_bot(clean_resp, urls=unique_srcs, chart_tag=chart_tag,
                        hoax_tag=hoax_tag, topic_text=topic_text)
