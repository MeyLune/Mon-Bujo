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

# Fonctions CRUD (Create, Read, Update, Delete)
def save_gs(ws_n, row):
    try: sh.worksheet(ws_n).append_row(row)
    except: pass

def load_gs(ws_n):
    try: return sh.worksheet(ws_n).get_all_records()
    except: return []

def delete_gs(ws_n, idx):
    try: sh.worksheet(ws_n).delete_rows(idx + 2)
    except: pass

def update_gs(ws_n, idx, col, val):
    try: sh.worksheet(ws_n).update_cell(idx + 2, col, val)
    except: pass

# --- 2. LOGIQUE VISUELLE CALENDRIER ---
def get_circled_num(n):
    circled = {i: chr(9311 + i) for i in range(1, 21)}
    circled.update({21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕", 26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚", 31: "㉛"})
    return circled.get(n, str(n))

# --- 3. DESIGN & POLICES (iPad Optimized) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --or: #D4AF37; --vert-pale: #B2DFDB; }
    
    .stApp { 
        background-color: white !important;
        background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), 
                    url("https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg");
        background-size: cover; background-attachment: fixed;
    }
    
    .titre-calli { font-family: 'Dancing Script', cursive !important; font-size: 3.5rem !important; color: var(--sapin) !important; text-align: center; padding: 10px; }
    .sous-titre-calli { font-family: 'Dancing Script', cursive !important; font-size: 2.2rem !important; color: var(--sapin) !important; }
    
    p, label, .stMarkdown, span, div, .stCheckbox { font-family: 'Comfortaa' !important; color: var(--sapin) !important; }
    
    textarea, input { 
        background-color: white !important; color: var(--sapin) !important; 
        border: 2px solid var(--rose) !important; border-radius: 12px !important; 
    }
    
    .stButton>button { background-color: var(--rose) !important; color: white !important; border-radius: 20px !important; font-weight: bold; border: none; }
    
    .post-it { padding: 12px; border-radius: 15px; margin-bottom: 8px; border-left: 10px solid var(--rose); background: rgba(255,255,255,0.9); box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .p-header { background-color: var(--vert-pale) !important; color: var(--sapin) !important; padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; border: 1px solid var(--rose); }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'j_edit' not in st.session_state: st.session_state.j_edit = None
if 'j_val' not in st.session_state: st.session_state.j_val = ""
if 'shopping' not in st.session_state: st.session_state.shopping = []

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
    c1, c2 = st.columns(2)
    j_data = load_gs("Journal")
    g_data = load_gs("Gratitude")
    with c1:
        st.markdown('<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        txt_j = st.text_area("...", value=st.session_state.j_val, height=180, key="txt_journal", label_visibility="collapsed")
        if st.button("💾 Enregistrer pensée"):
            if txt_j:
                if st.session_state.j_edit is not None: update_gs("Journal", st.session_state.j_edit, 2, txt_j); st.session_state.j_edit = None; st.session_state.j_val = ""
                else: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), txt_j])
                st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data) - 1 - i
            st.markdown(f'<div class="post-it"><small>{e.get("Date")}</small><br>{e.get("Texte")}</div>', unsafe_allow_html=True)
            colb1, colb2 = st.columns(2)
            if colb1.button("✏️", key=f"ej_{idx}"): st.session_state.j_edit = idx; st.session_state.j_val = e.get("Texte"); st.rerun()
            if colb2.button("🗑️", key=f"dj_{idx}"): delete_gs("Journal", idx); st.rerun()
    with c2:
        st.markdown('<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        txt_g = st.text_area("...", height=180, key="txt_grat", label_visibility="collapsed")
        if st.button("🙏 Enregistrer gratitude"):
            if txt_g: save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y %H:%M"), txt_g]); st.rerun()
        for i, e in enumerate(reversed(g_data)):
            idx_g = len(g_data) - 1 - i
            st.markdown(f'<div class="post-it" style="border-left-color:var(--or);"><i>{e.get("Texte")}</i></div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dg_{idx_g}"): delete_gs("Gratitude", idx_g); st.rerun()

# --- 🗓️ SEMAINE (Espace Planning Amélioré) ---
with tabs[1]:
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    st.markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine {start.isocalendar()[1]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;">Du {start.strftime("%d/%m")} au {(start+timedelta(days=6)).strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    
    st.markdown("### 📝 Planning Hebdomadaire")
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    # 2 lignes pour plus de largeur sur iPad
    r1 = st.columns(4)
    r2 = st.columns(4)
    all_c = r1 + r2
    for i, j in enumerate(jours):
        d_p = start + timedelta(days=i)
        with all_c[i]:
            st.markdown(f'<div class="p-header">{j} {d_p.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            st.text_area("", key=f"plan_{i}", height=200, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 🍎 Menus")
    cols_m = st.columns(7)
    for i, j in enumerate(jours):
        with cols_m[i]:
            st.markdown(f'<div class="p-header" style="background:white!important; font-size:0.7rem;">{j[:3]}</div>', unsafe_allow_html=True)
            st.text_input("M", key=f"m1_{i}", placeholder="Matin", label_visibility="collapsed")
            st.text_input("D", key=f"m2_{i}", placeholder="Midi", label_visibility="collapsed")
            st.text_input("S", key=f"m3_{i}", placeholder="Soir", label_visibility="collapsed")

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier Annuel 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    marked = {f"{datetime.strptime(str(e['Date']), '%d/%m/%Y').month}-{datetime.strptime(str(e['Date']), '%d/%m/%Y').day}": e['Evenement'] for e in evs if e.get('Date')}
    
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
    ca, cl = st.columns(2)
    with ca:
        sd = st.date_input("Date importante", key="date_imp")
        en = st.text_input("Événement", key="ev_imp")
        if st.button("📍 Marquer"): save_gs("Evenements", [sd.strftime("%d/%m/%Y"), en]); st.rerun()
    with cl:
        for i, ev in enumerate(evs):
            ctx, cbt = st.columns([4,1])
            ctx.write(f"⭕ {ev.get('Date')} : {ev.get('Evenement')}")
            if cbt.button("🗑️", key=f"dev_{i}"): delete_gs("Evenements", i); st.rerun()

# --- 📊 TRACKERS ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🩺 SANTÉ"])
    with tr_tabs[0]:
        cl1, cl2 = st.columns([2, 1])
        with cl1:
            st.text_input("Titre du livre", key="bk_t"); st.text_input("Auteur", key="bk_a")
            st.date_input("Début", key="bk_d"); st.date_input("Fin", key="bk_f")
        with cl2: st.file_uploader("Couverture", key="bk_img")
        st.slider("Note / 10", 1, 10, 5, key="bk_n")
        st.markdown("#### Ressenti")
        r1, r2, r3, r4 = st.columns(4)
        r1.select_slider("💧 Triste", options=[1,2,3,4,5], key="r1")
        r2.select_slider("🌶️ Spicy", options=[1,2,3,4,5], key="r2")
        r3.select_slider("🤩 Rire", options=[1,2,3,4,5], key="r3")
        r4.select_slider("❤️ Love", options=[1,2,3,4,5], key="r4")
        st.button("💾 Sauver Lecture", key="btn_bk")
    with tr_tabs[1]:
        st.markdown('<div class="sous-titre-calli">🩺 Suivi Santé</div>', unsafe_allow_html=True)
        st.date_input("Date", key="h_date")
        st.multiselect("État général", ["Forme ✨", "Fatigue 😴", "Douleurs 🤕", "Stress 😰"], key="h_etat")
        st.text_area("Notes / Sommeil / Traitement", key="h_notes")
        st.button("💾 Sauver Santé", key="btn_h")

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🥚 Œufs"]
    cols_r = st.columns(len(rapide))
    for idx, r in enumerate(rapide):
        if cols_r[idx].button(r, key=f"rap_{idx}"): st.session_state.shopping.append(r); st.rerun()
    it = st.text_input("Ajouter un article...", key="c_add")
    if st.button("➕ Ajouter", key="c_btn"):
        if it: st.session_state.shopping.append(it); st.rerun()
    for i, item in enumerate(st.session_state.shopping):
        ca, cb = st.columns([4, 1])
        ca.checkbox(item, key=f"ch_{i}")
        if cb.button("🗑️", key=f"dc_{i}"): st.session_state.shopping.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Mes Stickers</div>', unsafe_allow_html=True)
    st.info("Espace prêt pour tes futurs stickers !")
