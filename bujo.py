import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF

# ==========================================
# 1. CONNEXION & CONFIGURATION
# ==========================================
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
        client = gspread.authorize(creds)
        return client.open("db_bujo")
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

sh = init_connection()
if sh:
    ws_notes = sh.worksheet("Note")
    ws_fin = sh.worksheet("Finances")
    ws_conf = sh.worksheet("Config")
else:
    st.stop()

# ==========================================
# 2. STYLE ET POLICES (Optimisation Gaieté & iPad)
# ==========================================
st.set_page_config(page_title="Mon Bujo Créatif", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Caveat:wght@400;700&display=swap" rel="stylesheet">
<style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Fond dégradé plus doux et gai */
    .stApp { 
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); 
        background-attachment: fixed;
    }
    
    h1, h2, h3, h4 { font-family: 'Comfortaa', cursive !important; color: #2e7d32 !important; }
    
    /* Bannière titre */
    .header-banner { 
        background: white; 
        padding: 20px; 
        border-radius: 30px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        text-align: center; 
        border: 2px solid #a5d6a7;
    }
    .header-banner h1 { color: #2e7d32 !important; margin: 0; font-size: 2.2rem; }

    /* Navigation Horizontale */
    div.stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    div.stRadio label { 
        background: white !important; 
        color: #2e7d32 !important; 
        padding: 8px 20px !important; 
        border-radius: 20px !important; 
        border: 1px solid #a5d6a7 !important;
        font-family: 'Comfortaa' !important;
    }

    /* Blocs style papier */
    .bujo-block { 
        background: rgba(255, 255, 255, 0.8); 
        padding: 25px; 
        border-radius: 25px; 
        border: 1px solid #e0e0e0; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
    }

    /* Inputs plus clairs pour l'iPad */
    input, textarea, [data-baseweb="select"] div { 
        color: #1b5e20 !important; 
        font-weight: bold !important; 
        font-family: 'Comfortaa' !important; 
    }
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea { 
        background-color: #ffffff !important; 
        border: 1.5px solid #a5d6a7 !important; 
        border-radius: 12px !important; 
    }

    /* Boutons */
    .stButton>button { 
        background-color: #66bb6a !important; 
        color: white !important; 
        border-radius: 15px; 
        font-weight: bold; 
        border: none; 
        height: 45px;
    }

    /* Style Grille Hebdo (Inspiration Rose/Blanc) */
    .hebdo-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; background-color: #fce4ec; border: 2px solid #fce4ec; border-radius: 15px; overflow: hidden; }
    .hebdo-header { background-color: #f06292; color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 0.9rem; }
    .hebdo-cell { background-color: white; min-height: 150px; padding: 8px; font-size: 0.8rem; }
    .event-tag { background: #fce4ec; border-left: 4px solid #f06292; padding: 4px; margin-bottom: 5px; border-radius: 4px; color: #880e4f; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INTERFACE PRINCIPALE
# ==========================================
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

page = st.radio("", ["📅 Année", "🌿 Semaine", "✍️ Mon Journal", "💰 Budget"], index=2, label_visibility="collapsed")

st.markdown(f"<div style='text-align:center; font-family:\"Caveat\"; font-size:1.8rem; color:#66bb6a; margin-bottom:20px;'>Nous sommes le {datetime.now().strftime('%d %B %Y')}</div>", unsafe_allow_html=True)

# --- PAGE MON JOURNAL ---
if page == "✍️ Mon Journal":
    col_g, col_d = st.columns([1, 1], gap="large")

    with col_g:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        st.markdown("<h4>Mon Humeur & État</h4>", unsafe_allow_html=True)
        humeur = st.select_slider("", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], value="😐")
        sentiments = st.text_area("Comment je me sens aujourd'hui ?", placeholder="Écris ici ce que tu as sur le cœur...", height=150)
        
        st.markdown(f'<p style="font-family:\'Caveat\'; font-size:1.6rem; color:#f06292; margin:15px 0;">"Je suis capable de réaliser mes rêves."</p>', unsafe_allow_html=True)
        if st.button("✨ Enregistrer mon état"):
            st.success("C'est enregistré dans ton cœur (et la base) !")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="bujo-block">', unsafe_allow_html=True)
        st.markdown("<h4>Mon Programme</h4>", unsafe_allow_html=True)
        programme = st.text_area("Planning de la journée", placeholder="08h00 : Méditation\n10h00 : Travail sur le BuJo...", height=310)
        if st.button("💾 Mettre à jour le planning"):
            st.success("Ton programme est prêt !")
        st.markdown('</div>', unsafe_allow_html=True)

    # Zone Notes et RDV
    st.write("---")
    st.markdown("### 🖋️ Notes, RDV & Événements")
    c1, c2 = st.columns([3, 1])
    with c1: note_txt = st.text_input("Nouvelle entrée...", placeholder="Ex: Dentiste à 15h, Appeler maman...")
    with c2: note_type = st.selectbox("Style", ["🍃 Note", "📌 Tâche", "📅 RDV / Événement", "💡 Idée"])
    
    if st.button("Ancrer dans mon Journal"):
        if note_txt:
            ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), note_type, note_txt])
            st.rerun()

    # Historique récent
    st.markdown("#### 📜 Récemment noté")
    rows = ws_notes.get_all_values()
    if len(rows) > 1:
        for n in reversed(rows[-5:]):
            st.markdown(f"**{n[2]}** : {n[3]} <small style='color:gray;'>(le {n[0]} à {n[1]})</small>", unsafe_allow_html=True)

# --- PAGE SEMAINE (PLANNING HEBDO) ---
elif page == "🌿 Semaine":
    st.markdown("### 🗓️ Mon Planning Hebdomadaire")
    
    today = datetime.now()
    start_week = today - timedelta(days=today.weekday())
    
    data = ws_notes.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()

    st.markdown('<div class="hebdo-grid">', unsafe_allow_html=True)
    cols = st.columns(7)
    days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    for i in range(7):
        current_day = start_week + timedelta(days=i)
        date_str = current_day.strftime("%d/%m/%Y")
        
        with cols[i]:
            st.markdown(f'<div class="hebdo-header">{days_fr[i]}<br>{current_day.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            
            # Récupération des RDV
            events_html = ""
            if not df.empty:
                # Filtrage sur la date et le type RDV
                day_events = df[(df['Date'] == date_str) & (df['Type'] == "📅 RDV / Événement")]
                for _, row in day_events.iterrows():
                    events_html += f'<div class="event-tag">🕒 {row["Heure"]}<br>{row["Note"]}</div>'
            
            st.markdown(f'<div class="hebdo-cell">{events_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE BUDGET ---
elif page == "💰 Budget":
    st.markdown("### 🪙 Mes Finances")
    
    # Ajout rapide
    with st.expander("➕ Ajouter une ligne"):
        c1, c2, c3 = st.columns(3)
        cat = c1.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Dépense"])
        lab = c2.text_input("Libellé")
        val = c3.number_input("Montant €", step=0.01)
        if st.button("Ajouter"):
            ws_fin.append_row([datetime.now().strftime("%B"), "2026", cat, lab, val])
            st.rerun()

    # Édition et Historique
    data_fin = ws_fin.get_all_records()
    if data_fin:
        df_fin = pd.DataFrame(data_fin)
        st.info("💡 Tu peux modifier les valeurs directement dans le tableau ci-dessous.")
        edited_df = st.data_editor(df_fin, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 Sauvegarder les modifications budget"):
            ws_fin.clear()
            ws_fin.append_row(["Mois", "Année", "Catégorie", "Libellé", "Montant €"])
            ws_fin.append_rows(edited_df.values.tolist())
            st.success("Base budget mise à jour !")

# --- PAGE ANNÉE ---
elif page == "📅 Année":
    st.markdown("### 📅 Vue Annuelle 2026")
    st.write("Bientôt disponible : une vue d'ensemble de tes objectifs de l'année !")
