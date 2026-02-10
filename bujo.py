import streamlit as st
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & STYLE IPAD
# ==========================================
st.set_page_config(page_title="Mon BuJo Digital", layout="wide")

st.markdown("""
<style>
    /* Fond couleur papier crème */
    .stApp { background-color: #fcfaf7 !important; }
    
    /* Style du texte pour être bien noir et lisible */
    h1, h2, h3, p, span, li, label { 
        color: #2c3e50 !important; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* Conteneur principal style carnet */
    .bujo-page {
        background-color: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        min-height: 85vh;
        border: 1px solid #e0e0e0;
        margin-top: -30px; /* Remonte la page */
    }

    /* Adaptation des champs de saisie pour iPad */
    .stTextInput>div>div>input {
        background-color: #f9f9f9 !important;
        color: #2c3e50 !important;
        border-radius: 8px !important;
    }
    
    /* Bouton plus visible */
    .stButton>button {
        background-color: #2c3e50 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GESTION DES DONNÉES (SESSION)
# ==========================================
if "mon_journal" not in st.session_state:
    st.session_state.mon_journal = []

def ajouter_note(texte, icone):
    heure = datetime.now().strftime("%H:%M")
    st.session_state.mon_journal.append({"heure": heure, "note": texte, "type": icone})

# ==========================================
# 3. NAVIGATION LATÉRALE
# ==========================================
with st.sidebar:
    st.markdown("## 📓 Mon BuJo")
    page = st.radio("Aller à :", ["📅 Daily Log", "📊 Trackers", "🔒 Mes Secrets"])
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# ==========================================
# 4. CONTENU DES PAGES
# ==========================================
st.markdown('<div class="bujo-page">', unsafe_allow_html=True)

if page == "📅 Daily Log":
    st.title(f"Journal du {datetime.now().strftime('%d %B')}")
    
    # Formulaire de saisie rapide
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            nouvelle_note = st.text_input("Quoi de neuf ?", placeholder="Écris une tâche ou une note...", key="input_bujo")
        with col2:
            symbole = st.selectbox("Style", ["•", "!", "○", "♡", "✘"])
        
        if st.button("Enregistrer dans le journal"):
            if nouvelle_note:
                ajouter_note(nouvelle_note, symbole)
                st.rerun()

    st.markdown("---")
    
    # Affichage des notes
    if not st.session_state.mon_journal:
        st.info("C'est ici que tes notes apparaîtront. Commence par en ajouter une !")
    else:
        # On affiche les notes les plus récentes en haut
        for item in reversed(st.session_state.mon_journal):
            st.markdown(f"### {item['type']} {item['note']}")
            st.caption(f"🕒 {item['heure']}")
            st.markdown("---")

elif page == "🔒 Mes Secrets":
    st.title("Espace Privé")
    st.write("Certaines pages de ton BuJo sont protégées.")
    pin = st.text_input("Entrez votre code secret :", type="password")
    if pin == "1234":
        st.success("Accès autorisé")
        st.text_area("Note confidentielle", "Ici tu peux écrire tes pensées les plus secrètes...")
    elif pin != "":
        st.error("Code incorrect")

elif page == "📊 Trackers":
    st.title("Mes Suivis")
    st.info("Cette section sera bientôt prête pour suivre tes habitudes (eau, sport, sommeil).")

st.markdown('</div>', unsafe_allow_html=True)
