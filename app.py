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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_FOLDER   = "database_chatbot"
FOLDER_TARGET = os.path.join(BASE_FOLDER, "nasional_datagoid")
os.makedirs(FOLDER_TARGET, exist_ok=True)

# ==========================================
# 1. API KEYS
# ==========================================
API_KEYS_DICT = {
    # "🔑 Key 1 (Utama)":      "",
    # "🔑 Key 2 (Cadangan 1)": "",
    # "🔑 Key 3 (Cadangan 2)": "",
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
    "anjing","babi","bangsat","bajingan","goblok","tolol",
    "kontol","memek","brengsek","ngentot","jancok","ndasmu",
    "fuck","shit","asshole","bitch","damn"
}
def is_rude(text):
    return any(re.search(rf"\b{w}\b", text.lower()) for w in KATA_KASAR)

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

    plt.style.use("dark_background")
    # ↓ figsize lebih kecil: (6, 3) menggantikan (8, 4)
    fig, ax = plt.subplots(figsize=(5.5, 3))
    fig.patch.set_facecolor("#1E293B")
    ax.set_facecolor("#1E293B")
    ax.tick_params(colors="#94A3B8", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#334155")

    if ctype == "line":
        ax.plot(labels, values, marker="o", color="#6366F1", linewidth=2)
        ax.fill_between(range(len(labels)), values, alpha=.15, color="#6366F1")
    elif ctype == "pie":
        ax.pie(values, labels=labels, autopct="%1.1f%%",
               startangle=140, colors=sns.color_palette("plasma", len(labels)),
               textprops={"fontsize": 8})
    else:
        bars = ax.bar(labels, values, color=sns.color_palette("plasma", len(labels)))
        ax.bar_label(bars, fmt="%.0f", color="#F8FAFC", padding=2, fontsize=8)

    ax.set_title(title, fontsize=10, fontweight="bold", color="#F8FAFC", pad=8)
    if xlabel:
        ax.set_xlabel(xlabel, color="#94A3B8", fontsize=8)
    if ylabel:
        ax.set_ylabel(ylabel, color="#94A3B8", fontsize=8)
    plt.xticks(rotation=25, ha="right", color="#94A3B8", fontsize=7)
    plt.tight_layout(pad=1.0)

    # Render dalam kolom agar tidak full-width
    col_chart, _ = st.columns([1, 1])
    with col_chart:
        st.pyplot(fig, use_container_width=False)
    plt.close(fig)
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
    # Header singkat (tanpa gambar besar)
    st.markdown(
        "<div style='text-align:center;padding:4px 0'>"
        "<span style='font-size:1.8rem'>🛡️</span><br>"
        "<b style='font-size:1rem;color:#F8FAFC'>LERES</b><br>"
        "<small style='color:#94A3B8;font-size:.68rem'>E-Gov Smart Assistant</small>"
        "</div>",
        unsafe_allow_html=True
    )

    # Jam real-time — inline, height minimal
    components.html("""
    <div id="clk" style="font-size:.72rem;font-weight:600;font-family:monospace;
        color:#10B981;background:#0F172A;border:1px solid #334155;
        padding:4px 8px;border-radius:6px;text-align:center;margin:4px 0"></div>
    <script>
      function tick(){
        const n=new Date();
        document.getElementById('clk').innerText=n.toLocaleString('id-ID',
          {day:'numeric',month:'short',year:'numeric',
           hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
      }
      setInterval(tick,1000);tick();
    </script>""", height=32)

    st.divider()

    # API Key — label singkat supaya fit
    key_opts = list(API_KEYS_VALID.keys())
    if key_opts:
        sel_lbl = st.selectbox("🔑 API Key aktif:", key_opts, key="selected_api_key_label", label_visibility="visible")
        kv = API_KEYS_VALID[sel_lbl]
        masked = f"{kv[:4]}…{kv[-4:]}"
        st.markdown(f"<small style='color:#10B981'>✅ {masked}</small>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Isi API key di app.py")

    st.divider()

    # Unduh data
    if st.button("🔄 Unduh data.go.id"):
        bar = st.empty()
        n = harvest_datagoid(progress_fn=lambda m: bar.caption(m))
        bar.empty()
        st.success(f"✅ {n} file")

    if st.button("🗑️ Hapus Riwayat"):
        st.session_state.msgs = [{
            "role": "bot",
            "content": (
                "Halo! Saya **LERES** — asisten layanan publik kamu 👋\n\n"
                "Mau tanya soal bansos, cek hoaks, atau minta grafik data? Langsung aja!"
            ),
            "urls": [], "chart_tag": "", "hoax_tag": "", "topic_text": ""
        }]
        st.rerun()

    n_local = len(get_local_files())
    st.markdown(f"<small style='color:#64748B'>📂 {n_local} file lokal tersedia</small>", unsafe_allow_html=True)

# ==========================================
# 10. CHAT PAGE
# ==========================================
st.title("🛡️ LERES Chatbot")
st.caption("Asisten Pintar Layanan Publik • Cek Bansos • Verifikasi Hoaks • Grafik Data")

if "msgs" not in st.session_state:
    st.session_state.msgs = [{
        "role": "bot",
        "content": (
            "Halo! Saya **LERES** — asisten layanan publik kamu 👋\n\n"
            "Mau tanya soal bansos, cek hoaks, atau minta grafik data? Langsung aja!"
        ),
        "urls": [], "chart_tag": "", "hoax_tag": "", "topic_text": ""
    }]

def append_bot(content, urls=None, chart_tag="", hoax_tag="", topic_text=""):
    st.session_state.msgs.append({
        "role": "bot", "content": content,
        "urls": urls or [], "chart_tag": chart_tag, "hoax_tag": hoax_tag,
        "topic_text": topic_text
    })

def append_user(content):
    st.session_state.msgs.append({"role": "user", "content": content})

# Render history
for i, msg in enumerate(st.session_state.msgs):
    if msg["role"] == "user":
        st.markdown(f'<div class="cb-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="cb-bot">{msg["content"]}</div>', unsafe_allow_html=True)

        if msg.get("chart_tag"):
            render_chart(msg["chart_tag"])

        for j, u in enumerate((msg.get("urls") or [])[:3]):
            lbl = "🌐 Sumber Resmi (.go.id)" if ".go.id" in u else "🌐 Lihat Sumber"
            st.link_button(lbl, u, key=f"src_{i}_{j}")

        # Tombol hubungi hanya jika ada topik relevan
        topic_text = msg.get("topic_text", "")
        if topic_text:
            render_contact_button(topic_text, key_suffix=str(i))

        # Badge & WA hoaks
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
                    st.link_button("📲 Laporkan ke Kominfo (WA)", f"https://wa.me/6281111111111?text={txt}", key=f"wa_{i}")
            except Exception:
                pass

# ==========================================
# 11. CHAT INPUT PROCESSING
# ==========================================
user_input = st.chat_input("Tanya bansos, cek hoaks, minta grafik…")

if user_input:
    st.markdown(f'<div class="cb-user">{user_input}</div>', unsafe_allow_html=True)
    append_user(user_input)

    # Moderasi
    if is_rude(user_input):
        warn = "Yuk gunakan bahasa yang sopan supaya aku bisa bantu dengan baik 😊"
        st.markdown(f'<div class="cb-bot">{warn}</div>', unsafe_allow_html=True)
        append_bot(warn)
    else:
        # Konteks data lokal
        local_files = get_local_files()
        ctx = ""
        src_url = "https://data.go.id"

        matched = best_file(user_input, local_files)
        if matched:
            ctx = file_context(matched)
        else:
            ctx = mock_context(user_input)

        # Deteksi kebutuhan visualisasi
        viz_kw = ["grafik","chart","diagram","visualisasi","tabel","perbandingan",
                  "bandingkan","statistik","distribusi","jumlah","persen","proporsi","plot"]
        needs_viz = any(kw in user_input.lower() for kw in viz_kw)

        sys_prompt = f"""Kamu adalah LERES, asisten layanan publik yang santai, to-the-point, dan ramah kayak teman.

WAKTU: {datetime.now().strftime('%d %B %Y %H:%M')}

GAYA: jawab singkat & kasual. Kalau user curhat/galau, validasi dulu sebelum kasih solusi. Jangan sapaan ulang.

ATURAN:
1. Jangan tempel URL mentah di jawaban. Taruh sumber di [SOURCES:["url1","url2"]] di akhir.
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
        with st.spinner("Bentar ya…"):
            try:
                raw = run_gemini(user_input, sys_prompt)
            except Exception as e:
                api_error = e

        if api_error is not None:
            st.error(f"⚠️ Gagal hubungi AI: {api_error}")
            fallback = "Maaf, ada gangguan ke AI. Coba ganti API Key di sidebar ya!"
            st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
            append_bot(fallback, urls=["https://data.go.id"])

        elif raw is None:
            fallback = "Hmm, nggak dapat respons dari AI. Coba lagi ya!"
            st.markdown(f'<div class="cb-bot">{fallback}</div>', unsafe_allow_html=True)
            append_bot(fallback, urls=["https://data.go.id"])

        else:
            # Ekstrak tag khusus
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
                sources  = [u.rstrip(".,;)\"]>") for u in raw_urls]
                for u in raw_urls:
                    raw = raw.replace(u, "")

            if not sources:
                sources = [src_url]

            clean_resp = re.sub(r'\n{3,}', '\n\n', raw).strip()

            # Tampilkan respons
            st.markdown(f'<div class="cb-bot">{clean_resp}</div>', unsafe_allow_html=True)

            # Grafik (ukuran kompak)
            if chart_tag:
                render_chart(chart_tag)

            # Tombol sumber
            unique_srcs = list(dict.fromkeys(sources))[:3]
            for j, u in enumerate(unique_srcs):
                lbl = "🌐 Sumber Resmi (.go.id)" if ".go.id" in u else "🌐 Lihat Sumber"
                st.link_button(lbl, u, key=f"src_new_{j}")

            # Tombol hubungi instansi — kontekstual berdasarkan topik (#22)
            topic_text = user_input + " " + clean_resp
            render_contact_button(topic_text, key_suffix="new")

            # Badge & WA hoaks
            if hoax_tag:
                try:
                    hd     = json.loads(hoax_tag)
                    claim  = hd.get("claim", "")
                    status = hd.get("status", "HOAKS")
                    bclass = "b-hoaks" if status == "HOAKS" else ("b-valid" if status == "VALID" else "b-unclear")
                    st.markdown(f'<span class="badge {bclass}">{status}</span>', unsafe_allow_html=True)
                    if status in ("HOAKS", "BUTUH KLARIFIKASI"):
                        txt = urllib.parse.quote(f'Laporan hoaks:\n"{claim}"\nMohon ditindaklanjuti.')
                        st.link_button("📲 Laporkan ke Kominfo (WA)", f"https://wa.me/6281111111111?text={txt}", key="wa_new")
                except Exception:
                    pass

            append_bot(clean_resp, urls=unique_srcs, chart_tag=chart_tag,
                       hoax_tag=hoax_tag, topic_text=topic_text)
