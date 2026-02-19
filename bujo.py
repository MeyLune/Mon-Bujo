import streamlit as st
from datetime import datetime, timedelta
import calendar

# --- 1. CONFIGURATION & DESIGN (FIX IPAD) ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide", initial_sidebar_state="collapsed")
fond_url = "https://raw.githubusercontent.com/MeyLune/Mon-Bujo/main/Avec%200.jpg"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@700&family=Courier+Prime&display=swap');
    
    :root {{
        --rose: #F48FB1;
        --sapin: #1B3022;
        --or: #D4AF37;
        --vert-doux: #B2DFDB;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(255, 209, 220, 0.7), rgba(178, 223, 219, 0.7)), url("{fond_url}");
        background-size: cover; background-attachment: fixed; background-color: white !important;
    }}

    /* TITRES */
    .titre-calli {{
        font-family: 'Dancing Script', cursive !important; font-size: 3.5rem !important;
        color: var(--sapin) !important; text-align: center; margin-bottom: 10px;
    }}
    .sous-titre-calli {{
        font-family: 'Dancing Script', cursive !important; font-size: 2.2rem !important;
        color: var(--sapin) !important; margin-bottom: 15px;
    }}

    /* FIX COULEURS IPAD & BLOC NOIR */
    textarea, input, div[data-baseweb="base-input"], div[data-baseweb="textarea"] {{
        background-color: white !important; color: var(--sapin) !important;
        -webkit-text-fill-color: var(--sapin) !important;
        border: 2px solid var(--rose) !important; border-radius: 12px !important;
    }}

    .stButton>button {{
        background-color: var(--rose) !important; color: white !important;
        border-radius: 20px !important; font-weight: bold !important; border: none !important;
    }}

    .post-it {{ padding: 15px; border-radius: 15px; margin-bottom: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }}
    
    .p-header {{ 
        background-color: var(--vert-doux) !important; color: var(--sapin) !important;
        padding: 8px; text-align: center; border-radius: 12px 12px 0 0; font-weight: bold; border: 1px solid var(--rose);
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION DES ETATS (POUR EVITER LES ERREURS) ---
for key in ['list_pensees', 'list_gratitudes', 'shopping_list', 'p_ver', 'g_ver', 'edit_p', 'edit_g']:
    if key not in st.session_state:
        if 'list' in key: st.session_state[key] = []
        elif 'ver' in key: st.session_state[key] = 0
        else: st.session_state[key] = ""

# --- 3. LOGIN ---
if "user_logged" not in st.session_state: st.session_state.user_logged = False
if not st.session_state.user_logged:
    st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        code = st.text_input("Code secret :", type="password")
        if st.button("Ouvrir mon journal") or code == "2125":
            st.session_state.user_logged = True
            st.rerun()
    st.stop()

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES", "🎨 STICKERS"])

# --- ✍️ JOURNAL ---
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="sous-titre-calli">🖋️ Mes pensées</div>', unsafe_allow_html=True)
        txt_p = st.text_area("...", value=st.session_state.edit_p, height=120, key=f"p_in_{st.session_state.p_ver}", label_visibility="collapsed")
        if st.button("💾 Enregistrer la pensée"):
            if txt_p:
                st.session_state.list_pensees.insert(0, {"t": txt_p, "h": datetime.now().strftime("%H:%M")})
                st.session_state.p_ver += 1; st.session_state.edit_p = ""; st.rerun()
        for idx, e in enumerate(st.session_state.list_pensees):
            st.markdown(f'<div class="post-it" style="background:rgba(255,209,220,0.6); border-left:8px solid var(--rose);">{e["t"]}</div>', unsafe_allow_html=True)
            if st.button("Modifier", key=f"mp_{idx}"):
                st.session_state.edit_p = e["t"]; st.session_state.list_pensees.pop(idx); st.rerun()
    with c2:
        st.markdown(f'<div class="sous-titre-calli">✨ Gratitude</div>', unsafe_allow_html=True)
        txt_g = st.text_area("...", value=st.session_state.edit_g, height=120, key=f"g_in_{st.session_state.g_ver}", label_visibility="collapsed")
        if st.button("🙏 Enregistrer"):
            if txt_g:
                st.session_state.list_gratitudes.insert(0, {"t": txt_g, "h": datetime.now().strftime("%H:%M")})
                st.session_state.g_ver += 1; st.session_state.edit_g = ""; st.rerun()
        for idx, e in enumerate(st.session_state.list_gratitudes):
            st.markdown(f'<div class="post-it" style="background:white; border-left:8px solid var(--or);"><i>{e["t"]}</i></div>', unsafe_allow_html=True)
            if st.button("Modifier", key=f"mg_{idx}"):
                st.session_state.edit_g = e["t"]; st.session_state.list_gratitudes.pop(idx); st.rerun()

# --- 🗓️ SEMAINE ---
with tabs[1]:
    start_week = (datetime.now().date() - timedelta(days=datetime.now().weekday()))
    st.markdown(f'<div class="sous-titre-calli" style="text-align:center;">Semaine {start_week.isocalendar()[1]}</div>', unsafe_allow_html=True)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    cg, cd = st.columns([3, 1])
    with cg:
        for j in jours:
            st.markdown(f'<div class="p-header">{j}</div>', unsafe_allow_html=True)
            st.text_area("", height=60, key=f"note_{j}", label_visibility="collapsed")
    with cd:
        st.markdown('<div class="p-header">🍎 Menu</div>', unsafe_allow_html=True)
        for j in jours: st.text_input(j[:2], key=f"menu_{j}")

# --- 📅 ANNEE ---
with tabs[2]:
    st.markdown('<div class="sous-titre-calli" style="text-align:center;">2026</div>', unsafe_allow_html=True)
    # Rendu ultra-simple pour éviter bug Safari
    cols = st.columns(3)
    for m in range(1, 13):
        with cols[(m-1)%3]:
            st.markdown(f'<div class="p-header">{calendar.month_name[m]}</div>', unsafe_allow_html=True)
            st.write(calendar.month(2026, m))

# --- 🛒 COURSES ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    cl, cr = st.columns([2, 1])
    with cl:
        item = st.text_input("Nouvel article :", key="course_in")
        if st.button("➕ Ajouter") and item:
            st.session_state.shopping_list.append(item); st.rerun()
        rapides = ["Lait", "Pain", "Oeufs", "Fruits"]
        for r in rapides:
            if st.button(f"Ajouter {r}"): st.session_state.shopping_list.append(r); st.rerun()
    with cr:
        st.markdown('<div class="p-header" style="background:var(--rose)!important; color:white!important;">Ma Liste</div>', unsafe_allow_html=True)
        for i, it in enumerate(st.session_state.shopping_list):
            st.write(f"• {it}")
        if st.button("🗑️ Vider tout"): st.session_state.shopping_list = []; st.rerun()

# --- 🎨 STICKERS ---
with tabs[5]:
    st.markdown('<div class="sous-titre-calli">🎨 Stickers</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload", type=['png', 'jpg'])
    if up: st.image(up, width=100)
