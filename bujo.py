import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import calendar

# --- 1. CONFIG ET STYLE DE FORCE ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&display=swap');
    :root { --rose: #F48FB1; --sapin: #1B3022; --vert: #B2DFDB; --or: #D4AF37; }
    
    .stApp { background: #fdf2f5 !important; }

    /* FORCE LE NOIR SUR TOUT L'IPAD */
    p, span, div, label, input, textarea, h1, h2, h3, .stMarkdown {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* Champs de saisie */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: white !important;
        color: black !important;
        border: 2px solid var(--rose) !important;
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3rem; color: var(--sapin); text-align: center; }
    
    /* Look Calendrier */
    .cal-box {
        background: white;
        border: 2px solid var(--rose);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .cal-month-title {
        background: var(--rose);
        color: white !important;
        -webkit-text-fill-color: white !important;
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    /* Sticker Mission */
    .sticker-mission {
        background: #e0f2f1;
        border: 1px solid var(--rose);
        padding: 5px;
        border-radius: 5px;
        margin-top: 5px;
        font-size: 0.9rem;
        font-weight: bold;
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION SÉCURISÉE ---
def init_connection():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = {
            "type": "service_account", "project_id": "airy-semiotics-486311-v5",
            "private_key": st.secrets["MY_PRIVATE_KEY"], "client_email": st.secrets["MY_CLIENT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds).open("db_bujo")
    except: return None

sh = init_connection()

# Initialisation des variables d'état (évite l'erreur que tu as eue)
if 'shopping' not in st.session_state: st.session_state.shopping = []

def save_gs(ws_n, row):
    try: sh.worksheet(ws_n).append_row(row)
    except: pass

def load_gs(ws_n):
    try: return sh.worksheet(ws_n).get_all_records()
    except: return []

# --- 3. INTERFACE ---
st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TAB 1 : JOURNAL & GRATITUDE ---
with tabs[0]:
    c1, c2 = st.columns(2)
    j_data = load_gs("Journal")
    g_data = load_gs("Gratitude")
    with c1:
        st.subheader("🖋️ Pensées")
        t_j = st.text_area("Aujourd'hui...", height=100, key="journal_in")
        if st.button("Sauver Pensée"):
            save_gs("Journal", [datetime.now().strftime("%d/%m/%Y"), t_j]); st.rerun()
        for e in reversed(j_data[-3:]):
            st.info(e.get("Texte", ""))
    with c2:
        st.subheader("✨ Gratitude")
        t_g = st.text_area("Reconnaissante pour...", height=100, key="grat_in")
        if st.button("Sauver Bonheur"):
            save_gs("Gratitude", [datetime.now().strftime("%d/%m/%Y"), t_g]); st.rerun()
        # Le fameux post-it gratitude
        st.markdown('<div style="background:#FFF9C4; padding:15px; border-left:8px solid #D4AF37; border-radius:5px;"><b>Mes Gratitudes :</b>', unsafe_allow_html=True)
        for e in reversed(g_data[-5:]):
            st.write(f"• {e.get('Texte', '')}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3 : ANNEE (RÉPARÉ ET JOLI) ---
with tabs[2]:
    st.markdown("### 📅 Calendrier Annuel 2026")
    # On crée 4 lignes de 3 colonnes pour un affichage carré
    for row in range(4):
        cols = st.columns(3)
        for col in range(3):
            month_idx = row * 3 + col + 1
            with cols[col]:
                st.markdown(f'<div class="cal-box"><div class="cal-month-title">{calendar.month_name[month_idx].upper()}</div>', unsafe_allow_html=True)
                # Affichage texte du calendrier bien aligné
                cal_str = calendar.month(2026, month_idx).split('\n', 2)[2]
                st.code("Lu Ma Me Je Ve Sa Di\n" + cal_str, language=None)
                st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4 : MISSIONS TRIBU (FORCE COULEUR) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 LECTURE", "🏠 MISSIONS"])
    with tr_tabs[1]:
        m_data = load_gs("Menage")
        mq, mt = st.columns(2)
        qui = mq.selectbox("Qui ?", ["Enfant 1 👦", "Enfant 2 👧", "Maman 🌸", "Papa 👔"])
        mission = mt.selectbox("Quoi ?", ["🍽️ Vaisselle", "🗑️ Poubelles", "🧹 Ménage", "🔌 Aspi"])
        if st.button("🚀 Valider Mission"):
            save_gs("Menage", [mission, datetime.now().strftime("%d/%m/%Y"), qui]); st.rerun()
        
        st.write("---")
        # Grille des jours
        cols = st.columns(7)
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        start_w = datetime.now().date() - timedelta(days=datetime.now().weekday())
        for i, j in enumerate(jours):
            d_str = (start_w + timedelta(days=i)).strftime("%d/%m/%Y")
            with cols[i]:
                st.markdown(f"<center><b>{j}</b><br><small>{d_str[:5]}</small></center>", unsafe_allow_html=True)
                for m in m_data:
                    if d_str in str(m.values()):
                        st.markdown(f'<div class="sticker-mission">{m.get("Tache","")}<br>{m.get("Qui","")}</div>', unsafe_allow_html=True)

# --- TAB 5 : COURSES (FIX ERREUR) ---
with tabs[4]:
    st.subheader("🛒 Ma Liste")
    new_item = st.text_input("Ajouter un article...", key="shop_input")
    if st.button("Ajouter à la liste", key="shop_btn"):
        if new_item: st.session_state.shopping.append(new_item); st.rerun()
    
    st.markdown('<div style="background:#f1f8e9; padding:15px; border-radius:10px; border:1px dashed green;">', unsafe_allow_html=True)
    for item in st.session_state.shopping:
        st.write(f"☐ {item}")
    st.markdown('</div>', unsafe_allow_html=True)
