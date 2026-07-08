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
import requests
import urllib3
import urllib.parse
import glob
import hashlib
import streamlit.components.v1 as components
from datetime import datetime
import plotly.express as px

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_FOLDER   = "database_chatbot"
FOLDER_TARGET = os.path.join(BASE_FOLDER, "nasional_datagoid")
os.makedirs(FOLDER_TARGET, exist_ok=True)

# ==========================================
# 1. API KEYS
# ==========================================
API_KEYS_DICT = {
    "🔑 Key 1 (Utama)":     st.secrets["API_KEY_1"],
    # "🔑 Key 2 (Cadangan 1)": "MASUKKAN_API_KEY_2_DI_SINI",
    # "🔑 Key 3 (Cadangan 2)": "MASUKKAN_API_KEY_3_DI_SINI",
}
API_KEYS_VALID = {
    lbl: k for lbl, k in API_KEYS_DICT.items()
    if k and not k.startswith("MASUKKAN_")
}

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="LERES – Layanan E-Gov Rekomendasi & Edukasi Smart",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ── Global ── */
.stApp{background:#0F172A;color:#F8FAFC;font-family:'Inter',sans-serif;}

/* ── Sidebar: compact, NO scroll ── */
section[data-testid="stSidebar"]{
    background:#1E293B!important;
    border-right:1px solid #334155;
    min-width:220px!important;
    max-width:240px!important;
    overflow:hidden!important;
    height:100vh!important;
}
section[data-testid="stSidebar"] > div:first-child{
    overflow:hidden!important;
    padding:10px 12px!important;
    height:100vh!important;
    display:flex!important;
    flex-direction:column!important;
}
/* shrink default margins inside sidebar */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{margin:0 0 4px 0!important;font-size:1.1rem!important;}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] .stCaption{font-size:.72rem!important;margin:0!important;}
section[data-testid="stSidebar"] hr{margin:6px 0!important;}
section[data-testid="stSidebar"] .stSelectbox label{font-size:.73rem!important;}
section[data-testid="stSidebar"] .stButton button{padding:4px 10px!important;font-size:.75rem!important;}

/* ── Chat bubbles ── */
.cb-user{
    background:#6366F1;color:#fff;
    padding:10px 14px;border-radius:16px 16px 2px 16px;
    margin:6px 0 6px 18%;line-height:1.5;}
.cb-bot{
    background:#1E293B;color:#F8FAFC;border:1px solid #334155;
    padding:10px 14px;border-radius:16px 16px 16px 2px;
    margin:6px 18% 6px 0;line-height:1.6;}

/* ── Badges ── */
.badge{display:inline-block;padding:2px 9px;border-radius:20px;
       font-size:.78rem;font-weight:700;color:#fff!important;}
.b-valid{background:#10B981;}.b-hoaks{background:#EF4444;}.b-unclear{background:#F59E0B;}

/* ── Buttons ── */
.stButton>button,.stLinkButton>a{
    background:#6366F1!important;color:#fff!important;
    border-radius:8px!important;border:none!important;
    padding:6px 14px!important;font-size:.82rem!important;
    transition:all .2s ease!important;margin-right:6px!important;}
.stButton>button:hover,.stLinkButton>a:hover{
    background:#4F46E5!important;box-shadow:0 0 10px rgba(99,102,241,.45)!important;}
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
        raise RuntimeError("Tidak ada API key valid. Isi API_KEYS_DICT di app.py.")

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
# 4. CKAN HARVESTER — data.go.id 1000 rows
# ==========================================
def harvest_datagoid(progress_fn=None):
    URL_API = "https://data.go.id/api/3/action/package_search?q=*:*&rows=1000"
    if progress_fn:
        progress_fn("Menghubungi data.go.id…")
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
    "pkh":  "PKH – Program Keluarga Harapan: terdaftar DTKS, ada balita/bumil/lansia/disabilitas. https://cekbansos.kemensos.go.id",
    "bpjs": "KIS/PBI – iuran BPJS dibayar pemerintah. Daftar lewat Dinsos/kelurahan. https://bpjs-kesehatan.go.id",
    "kip":  "KIP Kuliah – beasiswa PTN/PTS keluarga kurang mampu. https://kip-kuliah.kemdikbud.go.id",
    "bnpb": "Bantuan Bencana – logistik, tenda, sembako. Lapor ke BPBD. https://bnpb.go.id",
    "dtks": "DTKS – basis data penerima bansos Kemensos. Daftar lewat kelurahan. https://dtks.kemensos.go.id",
}
def mock_context(query):
    ql = query.lower()
    return "\n".join(v for k, v in MOCK.items() if k in ql) or ""

# ==========================================
# 6. PROFANITY FILTER
# ==========================================
KATA_KASAR = {
    "anjing", "babi", "bangsat", "bajingan", "goblok", "tolol",
    "kontol", "memek", "brengsek", "ngentot", "jancok", "ndasmu",
    "fuck", "shit", "asshole", "bitch", "damn", "lonte", "perek",
    "keparat", "bego"
}
def is_rude(text):
    tl = text.lower()
    return any(w in tl for w in KATA_KASAR)

def get_button_label(url):
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc or parsed.path.split('/')[0]
        if netloc.startswith("www."):
            netloc = netloc[4:]
        if ".go.id" in netloc.lower():
            return f"🌐 Sumber Resmi Pemerintah ({netloc})"
        return f"🌐 Sumber Resmi ({netloc})"
    except Exception:
        return "🌐 Sumber Resmi Pemerintah (.go.id)"

# ==========================================
# 7. CHART RENDERER — ukuran kompak (#20)
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

    df = pd.DataFrame({
        "Kategori": labels,
        "Jumlah": values
    })

    theme_layout = {
        "paper_bgcolor": "#1E293B",
        "plot_bgcolor": "#1E293B",
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
        fig.update_traces(textposition='inside', textinfo='percent+label')
    else: # bar
        fig = px.bar(df, x="Kategori", y="Jumlah", title=title,
                     color_discrete_sequence=["#6366F1"])
        fig.update_traces(marker_line_color='#818CF8', marker_line_width=1, opacity=0.9)

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

    # Render dalam kolom agar tidak full-width
    col_chart, _ = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    return True

# ==========================================
# 8. CONTEXT-AWARE CONTACT BUTTON (#22)
# ==========================================
INSTANSI_MAP = [
    {
        "keywords": ["kip","kuliah","beasiswa","pendidikan","sekolah","ptn","pts","kemendikbud"],
        "nama":     "Kemendikbudristek",
        "telp":     "177",
        "portal":   "https://kip-kuliah.kemdikbud.go.id",
        "label":    "Pendidikan / KIP Kuliah",
    },
    {
        "keywords": ["bpjs","kesehatan","pkm","puskesmas","rawat","obat","rumah sakit","kis","pbi"],
        "nama":     "BPJS Kesehatan",
        "telp":     "165",
        "portal":   "https://bpjs-kesehatan.go.id",
        "label":    "Kesehatan / BPJS",
    },
    {
        "keywords": ["pkh","bansos","dtks","kemensos","sembako","beras","raskin","bpnt","kks"],
        "nama":     "Kementerian Sosial",
        "telp":     "171",
        "portal":   "https://cekbansos.kemensos.go.id",
        "label":    "Bansos / Sosial",
    },
    {
        "keywords": ["gempa","banjir","bencana","longsor","bnpb","bpbd","evakuasi","darurat"],
        "nama":     "BNPB / BPBD",
        "telp":     "112",
        "portal":   "https://bnpb.go.id",
        "label":    "Bencana / Darurat",
    },
    {
        "keywords": ["hoaks","hoax","berita palsu","disinformasi","kominfo","konten","internet"],
        "nama":     "Kominfo",
        "telp":     "159",
        "portal":   "https://kominfo.go.id",
        "label":    "Hoaks / Konten Digital",
    },
]

def detect_instansi(text):
    """Deteksi instansi paling relevan dari teks pertanyaan+jawaban."""
    tl = text.lower()
    best = None
    best_score = 0
    for inst in INSTANSI_MAP:
        score = sum(1 for kw in inst["keywords"] if kw in tl)
        if score > best_score:
            best_score = score
            best = inst
    return best  # None kalau tidak ada kecocokan sama sekali

def render_contact_button(combined_text, key_suffix=""):
    """Tampilkan satu tombol hubungi instansi yang relevan, atau tidak tampil jika tidak relevan."""
    inst = detect_instansi(combined_text)
    if inst is None:
        return
    wa_text = urllib.parse.quote(
        f"Halo, saya ingin bertanya mengenai layanan {inst['label']}.\n"
        f"(Diarahkan dari LERES Chatbot)"
    )
    wa_url  = f"https://wa.me/62{inst['telp'].replace('-', '')}?text={wa_text}"
    st.markdown(
        f"<small style='color:#64748B'>📞 Hubungi: **{inst['nama']}** — "
        f"<a href='{inst['portal']}' target='_blank' style='color:#6366F1'>{inst['portal'].replace('https://','')}</a> "
        f"| Call Center: **{inst['telp']}**</small>",
        unsafe_allow_html=True
    )

# ==========================================
# 9. SIDEBAR — compact, no scroll (#21)
# ==========================================
with st.sidebar:
    # Logo & Deskripsi Instansi
    st.markdown(
        "<div style='text-align:center;padding:12px 10px;background:#0F172A;border-radius:12px;border:1px solid #334155;margin-bottom:10px;'>"
        "<span style='font-size:1.8rem'>🛡️</span><br>"
        "<b style='font-size:1.1rem;color:#F8FAFC;letter-spacing:0.5px;'>LERES</b><br>"
        "<div style='color:#94A3B8;font-size:.68rem;margin-top:2px;'>Layanan E-Government Rekomendasi & Edukasi Smart</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # Jam Realtime
    components.html("""
    <div id="clk" style="font-size:.72rem;font-weight:600;font-family:monospace;
        color:#10B981;background:#0F172A;border:1px solid #334155;
        padding:6px 8px;border-radius:6px;text-align:center;"></div>
    <script>
      function tick(){
        const n=new Date();
        document.getElementById('clk').innerText=n.toLocaleString('id-ID',
          {day:'numeric',month:'short',year:'numeric',
           hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
      }
      setInterval(tick,1000);tick();
    </script>""", height=32)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # API Key Selector
    key_opts = list(API_KEYS_VALID.keys())
    if key_opts:
        sel_lbl = st.selectbox("🔑 API Key Aktif:", key_opts, key="selected_api_key_label")
        kv = API_KEYS_VALID[sel_lbl]
        masked = f"{kv[:4]}…{kv[-4:]}"
        st.markdown(f"<div style='background:#0F172A;padding:6px 10px;border-radius:6px;border:1px solid #334155;margin-top:4px;'><span style='color:#10B981;font-size:.72rem;font-weight:600;'>✅ {masked}</span></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Isi API key di app.py")

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Hapus Riwayat Chat — reset keduanya
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.msgs_layanan = [{
            "role": "bot",
            "content": "Halo! Saya LERES 👋 Tanya aja soal bansos, KIS, KIP, atau layanan publik lainnya!",
            "urls": [], "chart_tag": "", "topic_text": ""
        }]
        st.session_state.msgs_hoaks = [{
            "role": "bot",
            "content": "Halo! Di sini kamu bisa tempel informasi yang mau dicek kebenarannya. Aku akan bandingkan dengan data resmi pemerintah. 🔍",
            "urls": [], "hoax_tag": ""
        }]
        st.rerun()

    n_local = len(get_local_files())
    st.markdown(f"<div style='text-align:center;margin-top:auto;padding-top:15px;color:#64748B;font-size:.7rem;'>📂 {n_local} database lokal aktif</div>", unsafe_allow_html=True)

# ==========================================
# 10. SESSION STATE INIT
# ==========================================
if "msgs_layanan" not in st.session_state:
    st.session_state.msgs_layanan = [{
        "role": "bot",
        "content": "Halo! Saya LERES 👋 Tanya aja soal bansos, KIS, KIP, atau layanan publik lainnya!",
        "urls": [], "chart_tag": "", "topic_text": ""
    }]

if "msgs_hoaks" not in st.session_state:
    st.session_state.msgs_hoaks = [{
        "role": "bot",
        "content": "Halo! Di sini kamu bisa tempel informasi yang mau dicek kebenarannya. Aku akan bandingkan dengan data resmi pemerintah. 🔍",
        "urls": [], "hoax_tag": ""
    }]

def append_bot_layanan(content, urls=None, chart_tag="", topic_text=""):
    st.session_state.msgs_layanan.append({
        "role": "bot", "content": content,
        "urls": urls or [], "chart_tag": chart_tag, "topic_text": topic_text
    })

def append_user_layanan(content):
    st.session_state.msgs_layanan.append({"role": "user", "content": content})

def append_bot_hoaks(content, urls=None, hoax_tag=""):
    st.session_state.msgs_hoaks.append({
        "role": "bot", "content": content,
        "urls": urls or [], "hoax_tag": hoax_tag
    })

def append_user_hoaks(content):
    st.session_state.msgs_hoaks.append({"role": "user", "content": content})

# ==========================================
# 11. TWO-TAB PAGES
# ==========================================
st.markdown("""
<style>
/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #0F172A;
    border-bottom: 2px solid #334155;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: #1E293B;
    border-radius: 8px 8px 0 0 !important;
    color: #94A3B8 !important;
    font-weight: 600;
    font-size: .9rem;
    padding: 8px 20px !important;
    border: 1px solid #334155;
    border-bottom: none;
}
.stTabs [aria-selected="true"] {
    background: #6366F1 !important;
    color: #fff !important;
    border-color: #6366F1 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 16px;
}
</style>
""", unsafe_allow_html=True)

tab_layanan, tab_hoaks = st.tabs(["💬  AI Layanan Publik", "🔍  Cek Fakta / Hoaks"])

# ══════════════════════════════════════════
# TAB 1 — AI Layanan Publik
# ══════════════════════════════════════════
with tab_layanan:
    st.markdown(
        "<div style='margin-bottom:8px'>"
        "<span style='font-size:1.3rem;font-weight:700;color:#F8FAFC;'>💬 Asisten Layanan Publik</span><br>"
        "<span style='font-size:.8rem;color:#94A3B8;'>Tanya tentang bansos, KIS, KIP, prosedur, atau layanan pemerintah lainnya</span>"
        "</div>",
        unsafe_allow_html=True
    )

    # Render history
    for i, msg in enumerate(st.session_state.msgs_layanan):
        if msg["role"] == "user":
            st.markdown(f'<div class="cb-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cb-bot">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("chart_tag"):
                render_chart(msg["chart_tag"])
            for j, u in enumerate((msg.get("urls") or [])[:3]):
                st.link_button(get_button_label(u), u, key=f"lay_src_{i}_{j}")
            topic_text = msg.get("topic_text", "")
            if topic_text:
                render_contact_button(topic_text, key_suffix=f"lay_{i}")

    # Input
    user_input_lay = st.chat_input("Tanya soal bansos, KIS, KIP, layanan publik…", key="input_layanan")

    if user_input_lay:
        st.markdown(f'<div class="cb-user">{user_input_lay}</div>', unsafe_allow_html=True)
        append_user_layanan(user_input_lay)

        if is_rude(user_input_lay):
            warn = "Yuk gunakan bahasa yang sopan supaya aku bisa bantu dengan baik 😊"
            st.markdown(f'<div class="cb-bot">{warn}</div>', unsafe_allow_html=True)
            append_bot_layanan(warn)
        else:
            local_files = get_local_files()
            src_url = "https://data.go.id"
            ctx = ""
            matched = best_file(user_input_lay, local_files)
            if matched:
                ctx = file_context(matched)
            else:
                ctx = mock_context(user_input_lay)

            viz_kw = ["grafik","chart","diagram","visualisasi","tabel","perbandingan",
                      "bandingkan","statistik","distribusi","jumlah","persen","proporsi","plot"]
            needs_viz = any(kw in user_input_lay.lower() for kw in viz_kw)

            sys_lay = f"""Kamu adalah LERES, asisten layanan publik yang santai, to-the-point, dan ramah kayak teman.

WAKTU: {datetime.now().strftime('%d %B %Y %H:%M')}

GAYA: jawab singkat & kasual. Kalau user curhat/galau, validasi dulu sebelum kasih solusi. Jangan sapaan ulang.

FOKUS: Hanya menjawab pertanyaan seputar layanan publik dan bantuan sosial pemerintah Indonesia.
Jika ada angka/data yang cocok divisualisasikan, buat grafik.

ATURAN:
1. Jangan tempel URL mentah di jawaban. Taruh sumber resmi di [SOURCES:["https://sumber1.go.id","https://sumber2.go.id"]] di akhir.
   Setiap URL wajib domain pemerintah .go.id.
2. {"WAJIB buat grafik! " if needs_viz else ""}Kalau ada angka divisualisasikan, tambahkan:
   [CHART:{{"title":"...","type":"bar"|"line"|"pie","labels":[...],"values":[angka_murni],"xlabel":"...","ylabel":"..."}}]
   values hanya angka (float/int).
3. Konteks data:
{ctx if ctx else "Tidak ada data lokal. Jawab dari pengetahuan umum."}
"""

            raw = None
            api_error = None
            with st.spinner("Bentar ya…"):
                try:
                    raw = run_gemini(user_input_lay, sys_lay)
                except Exception as e:
                    api_error = e

            if api_error is not None:
                st.error(f"⚠️ Gagal hubungi AI: {api_error}")
                fallback = "Maaf, ada gangguan ke AI. Coba ganti API Key di sidebar ya!"
                st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
                append_bot_layanan(fallback, urls=["https://data.go.id"])
            elif raw is None:
                fallback = "Hmm, nggak dapat respons dari AI. Coba lagi ya!"
                st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
                append_bot_layanan(fallback, urls=["https://data.go.id"])
            else:
                chart_tag = ""
                sources   = []

                cm = re.search(r'\[CHART:(\{.*?\})\]', raw, re.DOTALL)
                if cm:
                    chart_tag = cm.group(1)
                    raw = raw[:cm.start()] + raw[cm.end():]

                sm = re.search(r'\[SOURCES:(\[.*?\])\]', raw, re.DOTALL)
                if sm:
                    try:
                        sources = json.loads(sm.group(1))
                    except Exception:
                        sources = []
                    raw = raw[:sm.start()] + raw[sm.end():]

                if not sources:
                    raw_urls = re.findall(r'https?://[^\s\)\]>"\']+', raw)
                    sources  = [u.rstrip(".,;)\"]>") for u in raw_urls]
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
                    st.link_button(get_button_label(u), u, key=f"lay_src_new_{j}")

                topic_text = user_input_lay + " " + clean_resp
                render_contact_button(topic_text, key_suffix="lay_new")

                append_bot_layanan(clean_resp, urls=unique_srcs, chart_tag=chart_tag, topic_text=topic_text)

# ══════════════════════════════════════════
# TAB 2 — Cek Fakta / Hoaks
# ══════════════════════════════════════════
with tab_hoaks:
    st.markdown(
        "<div style='margin-bottom:8px'>"
        "<span style='font-size:1.3rem;font-weight:700;color:#F8FAFC;'>🔍 Verifikasi Fakta & Cek Hoaks</span><br>"
        "<span style='font-size:.8rem;color:#94A3B8;'>Tempel informasi yang ingin kamu verifikasi — AI akan cek ke data resmi pemerintah</span>"
        "</div>",
        unsafe_allow_html=True
    )

    # Render history
    for i, msg in enumerate(st.session_state.msgs_hoaks):
        if msg["role"] == "user":
            st.markdown(f'<div class="cb-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cb-bot">{msg["content"]}</div>', unsafe_allow_html=True)
            for j, u in enumerate((msg.get("urls") or [])[:3]):
                st.link_button(get_button_label(u), u, key=f"hx_src_{i}_{j}")
            hoax_tag = msg.get("hoax_tag", "")
            if hoax_tag:
                try:
                    hd          = json.loads(hoax_tag)
                    claim       = hd.get("claim", "")
                    status      = hd.get("status", "BUTUH KLARIFIKASI")
                    reason      = hd.get("reason", "")
                    bclass      = "b-hoaks" if status == "HOAKS" else ("b-valid" if status == "VALID" else "b-unclear")
                    icon        = "❌" if status == "HOAKS" else ("✅" if status == "VALID" else "⚠️")
                    reason_html = f"<br><small style='color:#94A3B8;margin-top:6px;display:block;'>{reason}</small>" if reason else ""
                    st.markdown(
                        f"<div style='background:#0F172A;border:1px solid #334155;border-radius:10px;"
                        f"padding:10px 14px;margin:6px 0;'>"
                        f"<span class='badge {bclass}'>{icon} {status}</span>"
                        f"{reason_html}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    if status in ("HOAKS", "BUTUH KLARIFIKASI"):
                        txt = urllib.parse.quote(f'Laporan hoaks:\n"{claim}"\nMohon ditindaklanjuti.')
                        st.link_button("📲 Laporkan ke Kominfo", f"https://wa.me/6281111111111?text={txt}", key=f"hx_wa_{i}")
                except Exception:
                    pass

    # Input
    user_input_hx = st.chat_input("Tempel informasi / berita yang ingin dicek kebenarannya…", key="input_hoaks")

    if user_input_hx:
        st.markdown(f'<div class="cb-user">{user_input_hx}</div>', unsafe_allow_html=True)
        append_user_hoaks(user_input_hx)

        if is_rude(user_input_hx):
            warn = "Yuk gunakan bahasa yang sopan supaya aku bisa bantu dengan baik 😊"
            st.markdown(f'<div class="cb-bot">{warn}</div>', unsafe_allow_html=True)
            append_bot_hoaks(warn)
        else:
            sys_hx = f"""Kamu adalah LERES, modul verifikasi fakta layanan publik berbasis data resmi pemerintah.

WAKTU: {datetime.now().strftime('%d %B %Y %H:%M')}

TUGAS: Analisis klaim atau informasi yang diberikan user. Bandingkan dengan data resmi pemerintah Indonesia.

ATURAN:
1. SELALU sertakan tag di akhir respons:
   [HOAKS_CHECK:{{"claim":"<ringkasan klaim>","status":"HOAKS"|"VALID"|"BUTUH KLARIFIKASI","reason":"<alasan singkat 1-2 kalimat>"}}]
2. Sertakan referensi sumber resmi pemerintah:
   [SOURCES:["https://sumber1.go.id","https://sumber2.go.id"]]
   Hanya domain .go.id yang diperbolehkan.
3. Format jawaban:
   - Ringkasan klaim yang dianalisis
   - Poin-poin alasan (valid/tidak valid)
   - Referensi instansi terkait
4. Jika informasi menyebut domain non-.go.id, nilai itu sebagai indikasi HOAKS.
5. Jawab singkat, jelas, dan mudah dipahami warga awam.
"""

            raw = None
            api_error = None
            with st.spinner("Sedang memverifikasi…"):
                try:
                    raw = run_gemini(user_input_hx, sys_hx)
                except Exception as e:
                    api_error = e

            if api_error is not None:
                st.error(f"⚠️ Gagal hubungi AI: {api_error}")
                fallback = "Maaf, ada gangguan ke AI. Coba ganti API Key di sidebar ya!"
                st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
                append_bot_hoaks(fallback)
            elif raw is None:
                fallback = "Hmm, nggak dapat respons dari AI. Coba lagi ya!"
                st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
                append_bot_hoaks(fallback)
            else:
                hoax_tag = ""
                sources  = []

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
                    sources  = [u.rstrip(".,;)\"]>") for u in raw_urls]
                    for u in raw_urls:
                        raw = raw.replace(u, "")

                sources = [u for u in sources if ".go.id" in u.lower()]
                if not sources:
                    sources = ["https://data.go.id", "https://kominfo.go.id"]

                clean_resp = re.sub(r'\n{3,}', '\n\n', raw).strip()
                st.markdown(f'<div class="cb-bot">{clean_resp}</div>', unsafe_allow_html=True)

                unique_srcs = list(dict.fromkeys(sources))[:3]
                for j, u in enumerate(unique_srcs):
                    st.link_button(get_button_label(u), u, key=f"hx_src_new_{j}")

                # Badge Verifikasi
                if hoax_tag:
                    try:
                        hd          = json.loads(hoax_tag)
                        claim       = hd.get("claim", "")
                        status      = hd.get("status", "BUTUH KLARIFIKASI")
                        reason      = hd.get("reason", "")
                        bclass      = "b-hoaks" if status == "HOAKS" else ("b-valid" if status == "VALID" else "b-unclear")
                        icon        = "❌" if status == "HOAKS" else ("✅" if status == "VALID" else "⚠️")
                        reason_html = f"<br><small style='color:#94A3B8;margin-top:6px;display:block;'>{reason}</small>" if reason else ""
                        st.markdown(
                            f"<div style='background:#0F172A;border:1px solid #334155;border-radius:10px;"
                            f"padding:10px 14px;margin:6px 0;'>"
                            f"<span class='badge {bclass}'>{icon} {status}</span>"
                            f"{reason_html}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        if status in ("HOAKS", "BUTUH KLARIFIKASI"):
                            txt = urllib.parse.quote(f'Laporan hoaks:\n"{claim}"\nMohon ditindaklanjuti.')
                            st.link_button("📲 Laporkan ke Kominfo", f"https://wa.me/6281111111111?text={txt}", key="hx_wa_new")
                    except Exception:
                        pass

                append_bot_hoaks(clean_resp, urls=unique_srcs, hoax_tag=hoax_tag)
