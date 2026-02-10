import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & DESIGN ENCHANTÉ
# ==========================================
st.set_page_config(page_title="Mon BuJo Enchanté", layout="wide")

st.markdown("""
<style>
    /* Fond dégradé et motif de feuilles */
    .stApp {
        background: linear-gradient(135deg, #2d4c3e 0%, #7fb79e 50%, #d4a373 100%);
        background-attachment: fixed;
    }
    
    /* Overlay pour l'effet "feuilles" et texture papier */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url('https://www.transparenttextures.com/patterns/leaf.png');
        opacity: 0.15;
        pointer-events: none;
    }

    /* Conteneur principal style papier premium */
    .bujo-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-top: 10px;
        border: 1px solid #e0e0e0;
    }

    /* Style des titres et textes */
    h1, h2, h3, p, span, label { color: #2d4c3e !important; font-family: 'Georgia', serif; }
    
    /* Sidebar style Vert Sapin */
    [data-testid="stSidebar"] {
        background-color: #1a2e26 !important;
        border-right: 2px solid #d4a373;
    }
    [data-testid="stSidebar"] * { color: #fcfaf7 !important; }

    /* Boutons et inputs */
    .stButton>button {
        background: #2d4c3e !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); background: #d4a373 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALISATION DES DONNÉES
# ==========================================
if "db_bujo" not in st.session_state:
    st.session_state.db_bujo = {
        "nom_journal": "MeyLune",
        "notes": [],
        "finances": {} # Structure: { "mois_annee": {"revenus": [], "fixes": [], "variables": []} }
    }

db = st.session_state.db_bujo

# ==========================================
# 3. SIDEBAR & NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown(f"# 🌿 {db['nom_journal']}")
    st.write("---")
    page = st.sidebar.selectbox("Navigation", ["📅 Daily Log", "💰 Finances", "🔒 Mes Secrets", "📊 Trackers", "⚙️ Configuration"])
    st.write("---")
    st.caption(f"📅 {datetime.now().strftime('%A %d %B %Y')}")

# ==========================================
# 4. PAGES
# ==========================================
st.markdown('<div class="bujo-card">', unsafe_allow_html=True)

# --- CONFIGURATION (Comme l'app Assmat) ---
if page == "⚙️ Configuration":
    st.title("⚙️ Réglages du Journal")
    db["nom_journal"] = st.text_input("Nom de ton BuJo :", db["nom_journal"])
    st.success("Configuration enregistrée !")

# --- DAILY LOG ---
elif page == "📅 Daily Log":
    st.title(f"Journal de {db['nom_journal']}")
    col1, col2 = st.columns([3, 1])
    note = col1.text_input("Nouvelle pensée...", placeholder="Écris ici...")
    style = col2.selectbox("Type", ["🍃 Note", "📌 Tâche", "✨ Événement", "♡ Coup de coeur"])
    
    if st.button("Enregistrer"):
        if note:
            db["notes"].append({"heure": datetime.now().strftime("%H:%M"), "texte": note, "type": style})
            st.rerun()
    
    st.write("---")
    for n in reversed(db["notes"]):
        st.markdown(f"**{n['type']}** {n['texte']} *(à {n['heure']})*")

# --- FINANCES (Nouveauté !) ---
elif page == "💰 Finances":
    st.title("💹 Gestion Budget")
    mois_sel = st.selectbox("Mois à consulter", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
    
    # Initialisation du mois si inexistant
    if mois_sel not in db["finances"]:
        db["finances"][mois_sel] = {"revenus": [], "fixes": [], "variables": []}
    
    f_data = db["finances"][mois_sel]

    tab_rev, tab_fix, tab_var = st.tabs(["💰 Revenus", "🏠 Charges Fixes", "🛍️ Variables"])

    with tab_rev:
        col_a, col_b = st.columns(2)
        nom_rev = col_a.text_input("Source (ex: Salaire)", key="rev_n")
        mont_rev = col_b.number_input("Montant (€)", min_value=0.0, key="rev_m")
        if st.button("Ajouter Revenu"):
            f_data["revenus"].append({"nom": nom_rev, "montant": mont_rev})
            st.rerun()

    with tab_fix:
        col_c, col_d = st.columns(2)
        nom_fix = col_c.text_input("Charge (ex: Loyer)", key="fix_n")
        mont_fix = col_d.number_input("Montant (€)", min_value=0.0, key="fix_m")
        if st.button("Ajouter Charge Fixe"):
            f_data["fixes"].append({"nom": nom_fix, "montant": mont_fix})
            st.rerun()

    with tab_var:
        col_e, col_f = st.columns(2)
        nom_var = col_e.text_input("Dépense (ex: Courses)", key="var_n")
        mont_var = col_f.number_input("Montant (€)", min_value=0.0, key="var_m")
        if st.button("Ajouter Dépense"):
            f_data["variables"].append({"nom": nom_var, "montant": mont_var})
            st.rerun()

    # --- RÉCAPITULATIF FINANCIER ---
    st.markdown("---")
    total_rev = sum(i["montant"] for i in f_data["revenus"])
    total_dep = sum(i["montant"] for i in f_data["fixes"]) + sum(i["montant"] for i in f_data["variables"])
    solde = total_rev - total_dep

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenus", f"{total_rev:.2f} €")
    c2.metric("Total Dépenses", f"{total_dep:.2f} €", delta=f"-{total_dep:.2f}", delta_color="inverse")
    c3.metric("Reste à vivre", f"{solde:.2f} €")

# --- SECRETS ---
elif page == "🔒 Mes Secrets":
    st.title("🔒 Pages Protégées")
    pin = st.text_input("Code de consultation :", type="password")
    if pin == "1234":
        st.success("Accès aux pages privées")
        st.write("Ici tes notes partagées avec code.")
    elif pin:
        st.error("Code incorrect")

st.markdown('</div>', unsafe_allow_html=True)
