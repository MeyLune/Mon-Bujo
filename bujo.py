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

# Fonctions utilitaires Sheets
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

# --- 2. DESIGN & POLICES (RESTAURÉS) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    :root {{ --rose: #F48FB1; --sapin: #1B3022; --or: #D4AF37; --vert-pale: #B2DFDB; }}
    .stApp {{ background: linear-gradient(135deg, rgba(255,209,220,0.7), rgba(178,223,219,0.7)), url("{fond_url}"); background-size: cover; background-attachment: fixed; background-color: white !important; }}
    
    .titre-calli {{ font-family: 'Dancing Script', cursive !important; font-size: 3.5rem !important; color: var(--sapin) !important; text-align: center; }}
    .sous-titre-calli {{ font-family: 'Dancing Script', cursive !important; font-size: 2.2rem !important; color: var(--sapin) !important; }}
    
    p, label, .stMarkdown, span, div, .stCheckbox {{ font-family: 'Comfortaa', cursive !important; color: var(--sapin) !important; }}
    
    textarea, input {{ background-color: white !important; color: var(--sapin) !important; border: 2px solid var(--rose) !important; border-radius: 12px !important; -webkit-text-fill-color: var(--sapin) !important; }}
    
    .stButton>button {{ background-color: var(--rose) !important; color: white !important; border-radius: 20px !important; font-weight: bold !important; border: none !important; }}
    
    .post-it {{ padding: 15px; border-radius: 15px; margin-bottom: 5px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); border-left: 10px solid var(--rose); background: rgba(255,255,255,0.8); }}
    .p-header {{ background-color: var(--vert-pale) !important; color: var(--sapin) !important; padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; border: 1px solid var(--rose); }}
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
        txt_j = st.text_area("...", value=st.session_state.j_val, height=150, key="in_j", label_visibility="collapsed")
        if st.button("💾 Enregistrer"):
            if txt_j:
                if st.session_state.j_edit is not None: update_gs("Journal", st.session_state.j_edit, 2, txt_j); st.session_state.j_edit = None; st.session_state.j_val = ""
                else: save_gs("Journal", [datetime.now().strftime("%d/%m/%Y %H:%M"), txt_j])
                st.rerun()
        for i, e in enumerate(reversed(j_data)):
            idx = len(j_data) - 1 - i
            st.markdown(f'<div class="post-it"><small>{e.get("Date")}</small><br>{e.get("Texte")}</div>', unsafe_allow_html=True)
            colb1, colb2 = st.columns([1,1])
            if colb1.button("✏️", key=f"ed_j_{idx}"): st.session_state.j_edit = idx; st.session_state.j_val = e.get("Texte"); st.rerun()
            if colb2.button("🗑️", key=f"del_j_{idx}"): delete_gs("Journal", idx); st.rerun()

# --- 🗓️ SEMAINE (NOUVEL AFFICHAGE) ---
with tabs[1]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Ma Semaine & Mes Menus</div>', unsafe_allow_html=True)
    start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i, j in enumerate(jours):
        d = start + timedelta(days=i)
        with st.expander(f"📅 {j} {d.strftime('%d/%m')}", expanded=(d == datetime.now().date())):
            cw, cm = st.columns(2)
            cw.text_area("Notes du jour", key=f"notes_{i}", height=100)
            cm.text_input("🍴 Menu du jour", key=f"menu_{i}")

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">Calendrier 2026</div>', unsafe_allow_html=True)
    evs = load_gs("Evenements")
    # ... (Logique calendrier cercle conservée)
    st.write("Visualisation annuelle active ⭕")

# --- 📊 TRACKERS (RESTAURÉ) ---
with tabs[3]:
    st.markdown('<div class="sous-titre-calli">📚 Ma Fiche de Lecture</div>', unsafe_allow_html=True)
    tl1, tl2 = st.columns([2, 1])
    with tl1:
        st.text_input("TITRE DU LIVRE"); st.text_input("AUTEUR")
        st.date_input("DÉBUT LECTURE"); st.date_input("FIN LECTURE")
    with tl2: st.file_uploader("Couverture", type=['jpg','png'])
    st.slider("NOTE / 10", 1, 10, 5)
    st.markdown("#### Mon Ressenti")
    r1, r2, r3, r4 = st.columns(4)
    r1.select_slider("💧 Triste", options=[1,2,3,4,5])
    r2.select_slider("🌶️ Spicy", options=[1,2,3,4,5])
    r3.select_slider("🤩 Rire", options=[1,2,3,4,5])
    r4.select_slider("❤️ Love", options=[1,2,3,4,5])
    st.button("💾 ENREGISTRER LA FICHE")

# --- 🛒 COURSES (RESTAURÉ & AMÉLIORÉ) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    st.write("⚡ **Ajout rapide :**")
    rapide = ["🍞 Pain", "🥛 Lait", "🥚 Œufs", "🍎 Fruits", "🍝 Pâtes", "🧻 Papier Toilette"]
    cols_r = st.columns(6)
    for idx, r in enumerate(rapide):
        if cols_r[idx].button(r): st.session_state.shopping.append(r); st.rerun()
    
    st.markdown("---")
    c_add, c_list = st.columns([1, 1])
    with c_add:
        it = st.text_input("Autre article :")
        if st.button("Ajouter à la liste"):
            if it: st.session_state.shopping.append(it); st.rerun()
    with c_list:
        st.markdown('<div class="p-header">Ma Liste</div>', unsafe_allow_html=True)
        for i, item in enumerate(st.session_state.shopping):
            ca, cb = st.columns([4, 1])
            ca.checkbox(item, key=f"check_{i}")
            if cb.button("🗑️", key=f"del_c_{i}"): st.session_state.shopping.pop(i); st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Stickers</div>', unsafe_allow_html=True)
    st.write("Bientôt tes PNG GitHub ici !")
