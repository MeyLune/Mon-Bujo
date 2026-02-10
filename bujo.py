import streamlit as st
from datetime import datetime
import json

# ==========================================
# 1. CONFIGURATION & STYLE
# ==========================================
st.set_page_config(page_title="Mon BuJo Digital", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #fcfaf7; }
    /* Style pour que le texte soit bien visible sur iPad */
    h1, h2, h3, p, span, li { color: #2c3e50 !important; }
    .bujo-page {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
        min-height: 80vh;
        border: 1px solid #e0e0e0;
    }
    input { background-color: white !important; color: black !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GESTION DES DONNÉES (MÉMOIRE)
# ==========================================
# Pour débuter, on utilise la mémoire de session (on connectera Google Sheets juste après)
if "mon_journal" not in st.session_state:
    st.session_state.mon_journal = []

def ajouter_note(texte, icone):
    heure = datetime.now().strftime("%H:%M")
    st.session_state.mon_journal.append({"heure": heure, "note": texte, "type": icone})

# ==========================================
# 3. NAVIGATION
# ==========================================
with st.sidebar:
    st.title("📓 Mon BuJo")
    page = st.radio("Aller à :", ["📅 Daily Log", "📊 Trackers", "🔒 Mes Secrets"])
    st.divider()
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# ==========================================
# 4. CONTENU DES PAGES
# ==========================================
st.markdown('<div class="bujo-page">', unsafe_allow_html=True)

if page == "📅 Daily Log":
    st.header(f"Journal du {datetime.now().strftime('%d %B %Y')}")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        nouvelle_note = st.text_input("📝 Quoi de neuf ?", placeholder="Écris ici...")
    with col2:
        symbole = st.selectbox("Style", ["•", "!", "○", "♡"])
    
    if st.button("Enregistrer"):
        if nouvelle_note:
            ajouter_note(nouvelle_note, symbole)
            st.rerun()

    st.divider()
    
    # Affichage des notes enregistrées
    if not st.session_state.mon_journal:
        st.info("Aucune note pour aujourd'hui. Commencez à écrire !")
    else:
        for item in reversed(st.session_state.mon_journal):
            st.markdown(f"**{item['type']}** {item['note']} *(à {item['heure']})*")

elif page == "🔒 Mes Secrets":
    st.title("Zone Privée")
    code = st.text_input("Entrez le code PIN :", type="password")
    if code == "1234":
        st.success("Accès autorisé")
        st.text_area("Note secrète :", "Ceci est un exemple de page protégée.")
    elif code:
        st.error("Code erroné")

st.markdown('</div>', unsafe_allow_html=True)
