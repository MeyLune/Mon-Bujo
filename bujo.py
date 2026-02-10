import streamlit as st
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & STYLE IPAD
# ==========================================
st.set_page_config(page_title="Mon BuJo Digital", layout="wide")

# CSS pour donner un aspect "Carnet" et optimiser pour le tactile
st.markdown("""
<style>
    .stApp { background-color: #fcfaf7; }
    .bujo-page {
        background-color: white;
        padding: 40px;
        border-radius: 5px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        min-height: 80vh;
        border-left: 2px solid #e0e0e0;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #dcdcdc;
        background-color: white;
        color: #444;
    }
    /* Adaptation iPad : plus de padding et gros titres */
    h1 { font-family: 'serif'; color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIQUE DE SÉCURITÉ (LE CODE PIN)
# ==========================================
def verifier_pin():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        pin = st.text_input("🔑 Entrez le code pour cette page :", type="password")
        if pin == "1234": # Ton code secret (à changer plus tard)
            st.session_state.authenticated = True
            st.rerun()
        elif pin != "":
            st.error("Code incorrect.")
        return False
    return True

# ==========================================
# 3. NAVIGATION LATÉRALE
# ==========================================
with st.sidebar:
    st.title("📓 Mon BuJo")
    page = st.radio("Aller à :", ["📅 Daily Log", "📊 Trackers", "🔒 Mes Secrets", "⚙️ Paramètres"])
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%A %d %B')}")

# ==========================================
# 4. CONTENU DES PAGES
# ==========================================
st.markdown('<div class="bujo-page">', unsafe_allow_html=True)

if page == "📅 Daily Log":
    st.title("Journal du jour")
    
    # Zone de saisie rapide (Rapid Logging)
    col1, col2 = st.columns([3, 1])
    with col1:
        task = st.text_input("📝 Nouvelle note ou tâche...", placeholder="Ex: Acheter du thé")
    with col2:
        type_note = st.selectbox("Type", ["• Tâche", "- Note", "○ Événement"])
    
    if st.button("Ajouter au log"):
        st.success("Ajouté au journal !") # On ajoutera la sauvegarde plus tard

    st.divider()
    st.write("### Flux du jour")
    # Simulation d'affichage
    st.markdown("- [ ] Faire le point sur le projet BuJo")
    st.markdown("• Ne pas oublier de prendre rendez-vous chez le dentiste")

elif page == "🔒 Mes Secrets":
    st.title("Espace Protégé")
    if verifier_pin():
        st.write("🔓 Bienvenue dans ton espace privé.")
        st.text_area("Mes pensées secrètes...", height=300)
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()

elif page == "📊 Trackers":
    st.title("Habit Tracker")
    st.write("Ici, nous mettrons tes graphiques de suivi (Sommeil, Eau, Humeur).")

st.markdown('</div>', unsafe_allow_html=True)
