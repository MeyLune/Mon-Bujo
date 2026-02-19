import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar

# --- 1. CONNEXION ---
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds_info = {
            "type": "service_account",
            "project_id": "airy-semiotics-486311-v5",
            "private_key": st.secrets["MY_PRIVATE_KEY"],
            "client_email": st.secrets["MY_CLIENT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds).open("db_bujo")
    except Exception: return None

sh = init_connection()

def save_to_gsheet(worksheet_name, data_row):
    try:
        ws = sh.worksheet(worksheet_name)
        ws.append_row(data_row)
    except: pass

def load_from_gsheet(worksheet_name):
    try:
        ws = sh.worksheet(worksheet_name)
        return ws.get_all_records()
    except: return []

def delete_from_gsheet(worksheet_name, row_index):
    try:
        ws = sh.worksheet(worksheet_name)
        ws.delete_rows(row_index + 2)
    except: pass

def update_gsheet(worksheet_name, row_index, new_text):
    try:
        ws = sh.worksheet(worksheet_name)
        ws.update_cell(row_index + 2, 2, new_text)
    except: pass

# --- 2. LOGIQUE CALENDRIER ---
def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)} # ①-⑳
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 3. DESIGN ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    :root {{ --rose: #F48FB1; --sapin: #1B3022; --or: #D4AF37; --vert-pale: #B2DFDB; }}
    .stApp {{ background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(178, 223, 219, 0.7)), url("{fond_url}"); background-size: cover; background-attachment: fixed; }}
    .titre-calli {{ font-family: 'Dancing Script', cursive !important; font-size: 3.5rem; color: var(--sapin); text-align: center; }}
    .sous-titre-calli {{ font-family: 'Dancing Script', cursive !important; font-size: 2.2rem; color: var(--sapin); }}
    p, label, span, div {{ font-family: 'Comfortaa', cursive !important; color: var(--sapin); }}
    textarea, input {{ background-color: white !important; color: var(--sapin) !important; border: 2px solid var(--rose) !important; border-radius: 12px !important; -webkit-text-fill-color: var(--sapin) !important; }}
    .stButton>button {{ background-color: var(--rose) !important; color: white !important; border-radius: 20px; font-weight: bold; border: none; }}
    .post-it {{ padding: 12px; border-radius: 15px; margin-bottom: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); border-left: 8px solid var(--rose); background: rgba(255,255,255,0.8); }}
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'edit_mode_j' not in st.session_state: st.session_state.edit_mode_j = None
if 'edit_val_j' not in st.session_state: st.session_state.edit_val_j = ""

# --- LOGIN ---
if "user_data" not in st.session_state:
    st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_data = {"Nom": "MeyLune"}; st.rerun()
    st.stop()

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ✍️ JOURNAL ---
with tabs[0]:
    col1, col2 = st.columns(2)
    j_data = load_from_gsheet("Journal")
    g_data = load_from_gsheet("Gratitude")

    with col1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        # Gestion Modification
        label_btn = "💾 Mettre à jour" if st.session_state.edit_mode_j else "💾 Enregistrer la pensée"
        new_j = st.text_area("...", value=st.session_state.edit_val_j, height=150, key="input_j", label_visibility="collapsed")
        
        if st.button(label_btn):
            if new_j:
                if st.session_state.edit_mode_j is not None:
                    update_gsheet("Journal", st.session_state.edit_mode_j, new_j)
                    st.session_state.edit_mode_j = None; st.session_state.edit_val_j = ""
                else:
                    save_to_gsheet("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), new_j])
                st.rerun()

        for i, e in enumerate(reversed(j_data)):
            # On récupère l'index réel (car reversed)
            real_idx = len(j_data) - 1 - i
            txt = e.get("Texte", "") if e.get("Texte") else ""
            if txt != "None" and txt != "":
                with st.container():
                    c_txt, c_btns = st.columns([4, 1.2])
                    c_txt.markdown(f'<div class="post-it"><small>{e.get("Date")}</small><br>{txt}</div>', unsafe_allow_html=True)
                    cb1, cb2 = c_btns.columns(2)
                    if cb1.button("✏️", key=f"ed_j_{real_idx}"):
                        st.session_state.edit_mode_j = real_idx
                        st.session_state.edit_val_j = txt
                        st.rerun()
                    if cb2.button("🗑️", key=f"del_j_{real_idx}"):
                        delete_from_gsheet("Journal", real_idx); st.rerun()

    with col2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        new_g = st.text_area("...", height=150, key="input_g", label_visibility="collapsed")
        if st.button("🙏 Enregistrer"):
            if new_g: save_to_gsheet("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), new_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            real_idx_g = len(g_data) - 1 - i
            txt_g = e.get("Texte", "") if e.get("Texte") else ""
            if txt_g:
                with st.container():
                    cx, cy = st.columns([4, 0.5])
                    cx.markdown(f'<div class="post-it" style="border-left-color:var(--or); background:white;"><i>{txt_g}</i></div>', unsafe_allow_html=True)
                    if cy.button("🗑️", key=f"del_g_{real_idx_g}"): delete_from_gsheet("Gratitude", real_idx_g); st.rerun()

# --- 🗓️ SEMAINE ---
with tabs[1]:
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday()))
    st.markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine en cours</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cols_w = st.columns(7)
    for idx, j in enumerate(jours):
        with cols_w[idx]:
            st.markdown(f'<div style="background:var(--vert-pale); padding:5px; text-align:center; border-radius:10px; border:1px solid var(--rose); font-weight:bold; font-size:0.8rem;">{j}</div>', unsafe_allow_html=True)
            st.text_area("", height=150, key=f"wk_in_{idx}", label_visibility="collapsed")

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    events = load_from_gsheet("Evenements")
    marked = {f"{datetime.strptime(ev['Date'], '%d/%m/%Y').month}-{datetime.strptime(ev['Date'], '%d/%m/%Y').day}": ev['Evenement'] for ev in events if ev.get('Date')}
    
    for r in range(4):
        cols = st.columns(3)
        for c in range(3):
            m_idx = r * 3 + c + 1
            with cols[c]:
                st.markdown(f'<div style="background:var(--rose); color:white; padding:5px; text-align:center; border-radius:12px 12px 0 0; font-weight:bold;">{calendar.month_name[m_idx].upper()}</div>', unsafe_allow_html=True)
                cal = calendar.monthcalendar(2026, m_idx)
                res = "Lu Ma Me Je Ve Sa Di\n"
                for w in cal:
                    line = ""
                    for d in w:
                        if d == 0: line += "   "
                        else:
                            line += f"{get_circled_num(d)} " if f"{m_idx}-{d}" in marked else f"{d:2} "
                    res += line + "\n"
                st.markdown(f'<div style="font-family:\'Courier Prime\'; background:white; padding:10px; border:1px solid var(--rose); border-radius:0 0 12px 12px; white-space:pre; text-align:center; font-size:0.8rem;">{res}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    c_a, c_l = st.columns(2)
    with c_a:
        sd = st.date_input("Date")
        en = st.text_input("Événement")
        if st.button("📍 Marquer"): 
            save_to_gsheet("Evenements", [sd.strftime("%d/%m/%Y"), en]); st.rerun()
    with c_l:
        for i, ev in enumerate(events):
            col_t, col_d = st.columns([4, 1])
            col_t.write(f"⭕ {ev.get('Date')} : {ev.get('Evenement')}")
            if col_d.button("🗑️", key=f"dev_{i}"): delete_from_gsheet("Evenements", i); st.rerun()

# --- TRACKERS / COURSES / STICKERS ---
with tabs[3]: st.write("📚 Tracker de lecture actif")
with tabs[4]: st.write("🛒 Liste de courses active")
with tabs[5]: st.write("🎨 Planche de stickers active")
