import streamlit as st
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & DESIGN ENCHANTÉ 2.0
# ==========================================
st.set_page_config(page_title="Mon BuJo Enchanté", layout="wide")

# Intégration de polices : une élégante pour les titres et une manuscrite pour les notes
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>
    /* Fond dégradé Sapin/Or */
    .stApp {
        background: linear-gradient(135deg, #1a2e26 0%, #2d4c3e 40%, #d4a373 100%);
        background-attachment: fixed;
    }
    
    /* Bannière titre blanche (ton annotation) */
    .header-banner {
        background-color: white;
        padding: 15px;
        border-radius: 50px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .header-banner h1 { 
        color: #1a2e26 !important; 
        margin: 0; 
        font-family: 'Playfair Display', serif;
        font-size: 32px; 
    }

    /* Carte centrale style papier */
    .bujo-card {
        background-color: rgba(255, 255, 255, 0.94);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* Zone de note manuscrite (ton post-it) */
    .handwritten-note {
        background-color: #fff9c4;
        font-family: 'Caveat', cursive;
        font-size: 26px;
        padding: 25px;
        border-radius: 5px;
        border-left: 6px solid #fbc02d;
        color: #5d4037 !important;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
        margin-top: 20px;
        line-height: 1.2;
    }

    /* Sidebar et Stickers */
    [data-testid="stSidebar"] { background-color: #0e1a15 !important; border-right: 3px solid #d4a373; }
    .sticker-zone {
        text-align: center;
        border: 2px dashed #d4a373;
        padding: 10px;
        border-radius: 15px;
        margin-top: 20px;
        color: #d4a373;
        font-style: italic;
    }

    /* Boutons Vert d'eau */
    .stButton>button {
        background-color: #7fb79e !important;
        color: #1a2e26 !important;
        border: 2px solid #1a2e26;
        border-radius: 12px;
        font-weight: bold;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALISATION DES DONNÉES
# ==========================================
if "db" not in st.session_state:
    st.session_state.db = {
        "user": "MeyLune",
        "notes": [],
        "hand_note": "Mes réflexions du moment...",
        "finances": {"revenus": {}, "fixes": {}, "variables": {}}
    }
db = st.session_state.db

# ==========================================
# 3. SIDEBAR (NAVIGATION & STICKERS)
# ==========================================
with st.sidebar:
    st.markdown(f"# 🌿 {db['user']}")
    page = st.radio("Navigation", ["📅 Daily Log", "💰 Finances", "🔒 Secrets", "⚙️ Config"])
    
    st.markdown('<div class="sticker-zone">✨ Espace Stickers<br>🍃 🌸 🦋 🥥</div>', unsafe_allow_html=True)
    st.write("---")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# ==========================================
# 4. AFFICHAGE DES PAGES
# ==========================================

# Bannière fixe en haut
st.markdown(f'<div class="header-banner"><h1>Journal de {db["user"]}</h1></div>', unsafe_allow_html=True)

st.markdown('<div class="bujo-card">', unsafe_allow_html=True)

if page == "📅 Daily Log":
    st.subheader(f"Aujourd'hui, le {datetime.now().strftime('%d %B')}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        txt = st.text_input("Note ou tâche...", placeholder="Ex: Prendre rendez-vous I.R.M")
    with col2:
        sym = st.selectbox("Type", ["🍃 Note", "📌 Tâche", "✨ Événement", "♡"])
    
    if st.button("Enregistrer"):
        if txt:
            db["notes"].append({"h": datetime.now().strftime("%H:%M"), "t": txt, "s": sym})
            st.rerun()

    st.write("---")
    for n in reversed(db["notes"]):
        st.markdown(f"**{n['s']}** {n['t']}  *(🕒 {n['h']})*")

    # Zone "Note à la main" annotée sur ta capture
    st.markdown("### 🖋️ Note libre manuscrite")
    db["hand_note"] = st.text_area("Écris ici tes pensées libres...", value=db["hand_note"], label_visibility="collapsed")
    st.markdown(f'<div class="handwritten-note">{db["hand_note"]}</div>', unsafe_allow_html=True)

elif page == "💰 Finances":
    st.title("💹 Gestion Budget")
    t1, t2, t3 = st.tabs(["💵 Revenus", "🏠 Fixes", "🛍️ Variables"])
    
    with t1:
        n_r = st.text_input("Source de revenu", key="nr")
        m_r = st.number_input("Montant €", key="mr", min_value=0.0)
        if st.button("Ajouter Revenu"):
            db["finances"]["revenus"][n_r] = m_r; st.rerun()
            
    with t2:
        n_f = st.text_input("Charge fixe (Loyer, etc.)", key="nf")
        m_f = st.number_input("Montant €", key="mf", min_value=0.0)
        if st.button("Ajouter Charge"):
            db["finances"]["fixes"][n_f] = m_f; st.rerun()

    with t3:
        n_v = st.text_input("Dépense (Courses, etc.)", key="nv")
        m_v = st.number_input("Montant €", key="mv", min_value=0.0)
        if st.button("Ajouter Dépense"):
            db["finances"]["variables"][n_v] = m_v; st.rerun()

    st.write("---")
    rev = sum(db["finances"]["revenus"].values())
    dep = sum(db["finances"]["fixes"].values()) + sum(db["finances"]["variables"].values())
    reste = rev - dep
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenus", f"{rev} €")
    c2.metric("Dépenses", f"{dep} €", delta=f"-{dep}", delta_color="inverse")
    c3.metric("Reste à vivre", f"{reste} €")

elif page == "⚙️ Config":
    st.title("⚙️ Paramètres")
    db["user"] = st.text_input("Nom de l'utilisateur :", db["user"])
    if st.button("Sauvegarder le nom"): st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
