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

# Fonctions outils
def save_gs(ws_n, row):
    try: sh.worksheet(ws_n).append_row(row)
    except: pass

def load_gs(ws_n):
    try: return sh.worksheet(ws_n).get_all_records()
    except: return []

def update_gs(ws_n, idx, col, val):
    try: sh.worksheet(ws_n).update_cell(idx + 2, col, val)
    except: pass

# --- 2. STYLE DESIGN "ROSE PÊCHE & MENTHE" ---
st.set_page_config(page_title="MeyLune Bujo", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Comfortaa:wght@400;700&display=swap');
    
    :root { 
        --peche: #FFAB91; 
        --rose-clair: #FCE4EC; 
        --vert-douceur: #E0F2F1; 
        --sapin: #1B3022; 
        --rose-vif: #F48FB1;
    }

    .stApp {
        background: linear-gradient(180deg, var(--peche) 0%, var(--rose-clair) 30%, var(--vert-douceur) 100%) !important;
        background-attachment: fixed;
    }

    /* FIX BOUTONS : Fond blanc, texte rose/noir, bordure rose */
    .stButton>button {
        background-color: white !important;
        color: var(--sapin) !important;
        border: 2px solid var(--rose-vif) !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: var(--rose-vif) !important;
        color: white !important;
    }

    /* FIX INPUTS : Fini le noir */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: white !important;
        color: #1B3022 !important;
        border: 1px solid var(--rose-vif) !important;
        -webkit-text-fill-color: #1B3022 !important;
    }

    .titre-calli { font-family: 'Dancing Script'; font-size: 3.8rem; color: var(--sapin); text-align: center; text-shadow: 1px 1px 2px white; }
    .sous-titre-calli { font-family: 'Dancing Script'; font-size: 2.2rem; color: var(--sapin); margin-bottom: 10px; }
    
    .card-blanc { background: rgba(255, 255, 255, 0.7); border-radius: 20px; padding: 20px; border: 1px solid white; backdrop-filter: blur(5px); }
</style>
""", unsafe_allow_html=True)

if 'shopping' not in st.session_state: st.session_state.shopping = []

st.markdown('<div class="titre-calli">🌸 Mon Univers Quotidien</div>', unsafe_allow_html=True)
tabs = st.tabs(["✍️ JOURNAL", "🗓️ SEMAINE", "📅 ANNEE", "📊 TRACKERS", "🛒 COURSES"])

# --- TRACKERS (SANTÉ & LECTURE MIS À JOUR) ---
with tabs[3]:
    tr_tabs = st.tabs(["📚 BIBLIOTHÈQUE", "🩺 BIEN-ÊTRE & SANTÉ", "🏠 RESPONSABILITÉS"])
    
    with tr_tabs[0]: # Lecture détaillée
        st.markdown('<div class="sous-titre-calli">📚 Ma Fiche de Lecture</div>', unsafe_allow_html=True)
        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                titre = st.text_input("Titre de l'œuvre", placeholder="Ex: Orgueil et Préjugés")
                auteur = st.text_input("Auteur")
                genre = st.selectbox("Genre", ["Roman", "Développement Personnel", "Cuisine", "Poésie", "Autre"])
            with c2:
                statut = st.radio("Statut", ["En cours 📖", "Terminé ✅", "Coup de cœur ❤️"], horizontal=True)
                note = st.select_slider("Ma note", options=range(11), value=5)
            citation = st.text_area("Passage ou citation favorite")
            if st.button("💾 Sauvegarder dans ma bibliothèque"):
                save_gs("Lecture", [datetime.now().strftime("%d/%m/%Y"), titre, auteur, genre, statut, note, citation])
                st.success("Livre ajouté !")

    with tr_tabs[1]: # Santé Migraine & Sport
        st.markdown('<div class="sous-titre-calli">🩺 Suivi Santé & Sport</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.markdown("### 🏃‍♀️ Sport du jour")
            type_sport = st.text_input("Activité", placeholder="Yoga, Marche, Cardio...")
            duree = st.number_input("Durée (minutes)", 0, 300, 30)
            intensite_s = st.select_slider("Intensité Sport", options=["Douce", "Moyenne", "Intense"], key="sport_int")
        
        with col_s2:
            st.markdown("### 🤕 Suivi Migraine")
            migraine = st.checkbox("J'ai une migraine aujourd'hui")
            if migraine:
                niveau = st.slider("Intensité (1 à 10)", 1, 10, 5)
                zone = st.selectbox("Localisation", ["Front", "Tempes", "Nuque", "Oeil droit/gauche"])
                declencheur = st.text_input("Déclencheur potentiel (Écran, Stress, Aliment...)")
            else:
                st.write("Tout va bien aujourd'hui ! ✨")
        
        if st.button("💾 Enregistrer mon bilan santé"):
            # Logique de sauvegarde ici
            st.balloons()

    with tr_tabs[2]: # Responsabilités (Tableau simplifié)
        st.markdown('<div class="sous-titre-calli">🏠 Missions de la Tribu</div>', unsafe_allow_html=True)
        membres = ["Maman 🌸", "Papa 👔", "Enfant 1 👦", "Enfant 2 👧", "Enfant 3 👶"]
        qui = st.selectbox("Qui valide ?", membres)
        m_data = load_gs("Menage")
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        # Affichage compact
        for idx, row in enumerate(m_data):
            with st.expander(f"📍 {row.get('Tache', 'Mission')}"):
                cols = st.columns(7)
                for i, j in enumerate(jours):
                    val = row.get(j, "")
                    if not val or val == "0":
                        if cols[i].button("✨", key=f"m_{idx}_{i}"):
                            update_gs("Menage", idx, i + 2, qui); st.rerun()
                    else:
                        cols[i].markdown(f"**{val[:2]}**")

# --- COURSES (BOUTONS VISIBLES) ---
with tabs[4]:
    st.markdown('<div class="sous-titre-calli">🛒 Liste de Courses</div>', unsafe_allow_html=True)
    rapide = ["🍞 Pain", "🥛 Lait", "🍎 Fruits", "🍝 Pâtes", "🍚 Riz", "🧻 Papier T."]
    st.write("Ajout rapide :")
    cols_r = st.columns(6)
    for idx, r in enumerate(rapide):
        if cols_r[idx].button(r, key=f"btn_r_{idx}"):
            st.session_state.shopping.append(r); st.rerun()
    
    new_it = st.text_input("Autre chose ?", key="add_shop")
    if st.button("➕ Ajouter à la liste"):
        if new_it: st.session_state.shopping.append(new_it); st.rerun()
    
    st.markdown("---")
    for i, item in enumerate(st.session_state.shopping):
        c1, c2 = st.columns([5, 1])
        c1.checkbox(item, key=f"check_{i}")
        if c2.button("🗑️", key=f"del_{i}"):
            st.session_state.shopping.pop(i); st.rerun()
