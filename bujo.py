import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd

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
# 2. STYLE ET POLICES (iPad Optimisé & Clair)
# ==========================================
st.set_page_config(page_title="Mon Bujo Créatif", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Caveat:wght@400;700&display=swap" rel="stylesheet">
<style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); background-attachment: fixed; }
    
    /* Textes en vert foncé pour la lisibilité */
    h1, h2, h3, h4, p, span, label { font-family: 'Comfortaa', cursive !important; color: #1b5e20 !important; }

    .header-banner { background: white; padding: 20px; border-radius: 30px; margin-bottom: 20px; text-align: center; border: 2px solid #a5d6a7; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .header-banner h1 { color: #1b5e20 !important; margin: 0; }

    /* Grille Hebdomadaire Style "Clendar Planner" (Rose & Blanc) */
    .planner-container { background-color: #fce4ec; padding: 10px; border-radius: 10px; border: 1px solid #f8bbd0; }
    .planner-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 1px; background-color: #f8bbd0; }
    .planner-header { background-color: #f06292; color: white !important; padding: 12px; text-align: center; font-weight: bold; font-size: 0.9rem; }
    .planner-cell { background-color: white; min-height: 250px; padding: 8px; font-size: 0.8rem; overflow-y: auto; }
    .event-item { background: #fff1f3; border-left: 3px solid #f06292; padding: 4px; margin-bottom: 6px; border-radius: 4px; color: #880e4f !important; line-height: 1.2; }

    /* Blocs Bujo */
    .bujo-block { background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 20px; border: 1px solid #c8e6c9; margin-bottom: 15px; }
    
    /* Inputs et Boutons */
    input, textarea, [data-baseweb="select"] div { color: #1b5e20 !important; }
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea { background-color: #ffffff !important; border: 1.5px solid #81c784 !important; border-radius: 12px !important; }
    .stButton>button { background-color: #4caf50 !important; color: white !important; border-radius: 15px; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOGIQUE & PAGES
# ==========================================
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

st.markdown(f'<div class="header-banner"><h1>Journal de {user_name}</h1></div>', unsafe_allow_html=True)

page = st.radio("", ["📅 Année", "🌿 Semaine", "✍️ Mon Journal", "💰 Budget"], index=2, horizontal=True, label_visibility="collapsed")

# --- PAGE MON JOURNAL ---
if page == "✍️ Mon Journal":
    st.markdown(f"<p style='text-align:center; font-family:\"Caveat\"; font-size:1.8rem; color:#388e3c;'>Nous sommes le {datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)
    
    col_g, col_d = st.columns(2, gap="medium")
    with col_g:
        st.markdown('<div class="bujo-block"><h4>😊 Humeur & État</h4>', unsafe_allow_html=True)
        humeur = st.select_slider("", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], value="😐")
        st.text_area("Sentiments", placeholder="Comment vas-tu ?", label_visibility="collapsed", height=100)
        st.markdown('<p style="font-family:\'Caveat\'; font-size:1.4rem; color:#e91e63;">"Chaque jour est une nouvelle chance."</p></div>', unsafe_allow_html=True)
        
    with col_d:
        st.markdown('<div class="bujo-block"><h4>📋 Programme</h4>', unsafe_allow_html=True)
        st.text_area("Planning", placeholder="08h00 : ...", label_visibility="collapsed", height=180)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🖋️ Notes, RDV & Événements")
    c1, c2, c3 = st.columns([3, 2, 1])
    with c1: note_txt = st.text_input("Saisir une note...", placeholder="Ex: Dentiste 15h")
    with c2: note_type = st.selectbox("Type", ["🍃 Note", "📌 Tâche", "📅 RDV / Événement", "💡 Idée"])
    with c3:
        st.write("") # Espacement
        btn_add = st.button("Ancrer")

    if btn_add and note_txt:
        ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), note_type, note_txt])
        st.rerun()

# --- PAGE SEMAINE (VISUEL MODÈLE ROSE) ---
elif page == "🌿 Semaine":
    st.markdown("### 🗓️ Mon Planning Hebdomadaire")
    
    # Calcul dates
    today = datetime.now()
    start_week = today - timedelta(days=today.weekday())
    
    # Récupération données (avec gestion erreur de colonnes)
    data = ws_notes.get_all_records()
    df = pd.DataFrame(data)

    st.markdown('<div class="planner-container">', unsafe_allow_html=True)
    cols = st.columns(7)
    days_fr = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]

    for i in range(7):
        current_day = start_week + timedelta(days=i)
        date_str = current_day.strftime("%d/%m/%Y")
        
        with cols[i]:
            st.markdown(f'<div class="planner-header">{days_fr[i]}<br>{current_day.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            
            events_html = ""
            if not df.empty and 'Date' in df.columns and 'Type' in df.columns:
                # Filtrage : On cherche les RDV pour ce jour précis
                mask = (df['Date'] == date_str) & (df['Type'] == "📅 RDV / Événement")
                day_events = df[mask]
                for _, row in day_events.iterrows():
                    events_html += f'<div class="event-item"><b>{row["Heure"]}</b><br>{row["Note"]}</div>'
            
            st.markdown(f'<div class="planner-cell">{events_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE BUDGET (RESTAURÉE) ---
elif page == "💰 Budget":
    st.markdown("### 🪙 Gestion Budgétaire")
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter une opération", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1: b_cat = st.selectbox("Catégorie", ["Revenu", "Charge Fixe", "Dépense"])
        with c2: b_lab = st.text_input("Libellé")
        with c3: b_val = st.number_input("Montant €", min_value=0.0, step=1.0)
        
        if st.button("Ajouter à la liste"):
            ws_fin.append_row([datetime.now().strftime("%B"), "2026", b_cat, b_lab, b_val])
            st.success("Opération ajoutée !")
            st.rerun()

    # Historique et Calculs
    data_fin = ws_fin.get_all_records()
    if data_fin:
        df_fin = pd.DataFrame(data_fin)
        st.markdown("#### 📜 Historique (Modifier ou Supprimer)")
        # Éditeur de données
        edited_df = st.data_editor(df_fin, use_container_width=True, num_rows="dynamic")
        
        if st.button("Enregistrer les modifications"):
            ws_fin.clear()
            ws_fin.append_row(["Mois", "Année", "Catégorie", "Libellé", "Montant €"])
            ws_fin.append_rows(edited_df.values.tolist())
            st.success("Modifications enregistrées !")
            st.rerun()

# --- PAGE ANNÉE (À VENIR) ---
elif page == "📅 Année":
    st.info("Cette page est en cours de préparation. On y mettra bientôt ton calendrier annuel avec le même visuel !")
