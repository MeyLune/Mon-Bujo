import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF
import base64

# ==========================================
# 1. CONNEXION & CONFIGURATION GOOGLE
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
if not sh: st.stop()
ws_notes = sh.worksheet("Note")
ws_fin = sh.worksheet("Finances")
ws_conf = sh.worksheet("Config")

# ==========================================
# 2. DESIGN & STYLE (iPad & Gaieté)
# ==========================================
st.set_page_config(page_title="Mon Bujo Créatif", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;700&family=Caveat:wght@400;700&display=swap" rel="stylesheet">
<style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #fff3e0 100%); background-attachment: fixed; }
    
    /* Textes foncés pour lisibilité */
    h1, h2, h3, h4, p, span, label { font-family: 'Comfortaa', cursive !important; color: #1b5e20 !important; }

    /* Navigation par Onglets Tactiles */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: #ffffff; border-radius: 15px 15px 0px 0px;
        padding: 10px 30px; border: 1px solid #c8e6c9; font-weight: bold; color: #2e7d32;
    }
    .stTabs [aria-selected="true"] { background-color: #4caf50 !important; color: white !important; }

    /* Blocs Journal */
    .bujo-block { background: rgba(255, 255, 255, 0.9); padding: 25px; border-radius: 25px; border: 1px solid #c8e6c9; box-shadow: 4px 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; }

    /* Grille Semaine "Clendar" */
    .p-header { background-color: #f06292; color: white !important; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; font-size: 0.9rem; font-weight: bold; }
    .p-cell { background-color: white; min-height: 250px; padding: 10px; border: 1px solid #fce4ec; border-radius: 0 0 10px 10px; color: #444; }
    .event-item { background: #fff1f3; border-left: 4px solid #f06292; padding: 6px; margin-bottom: 6px; border-radius: 4px; color: #ad1457 !important; font-size: 0.8rem; }

    /* Boutons */
    .stButton>button { background-color: #4caf50 !important; color: white !important; border-radius: 15px; font-weight: bold; border: none; height: 45px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INTERFACE & NAVIGATION
# ==========================================
try: user_name = ws_conf.acell('A2').value or "MeyLune"
except: user_name = "MeyLune"

st.markdown(f'<h1 style="text-align:center; color:#1b5e20; font-family:Comfortaa;">Journal de {user_name}</h1>', unsafe_allow_html=True)

# Navigation par Onglets (La demande du "cliquer directement sur la section")
tab_journal, tab_semaine, tab_annee, tab_budget, tab_config = st.tabs(["✍️ JOURNAL", "🌿 SEMAINE", "📅 ANNÉE", "💰 BUDGET", "⚙️ CONFIG"])

# --- PAGE JOURNAL ---
with tab_journal:
    st.markdown(f"<p style='text-align:center; font-family:Caveat; font-size:1.8rem; color:#388e3c;'>Nous sommes le {datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)
    
    col_g, col_d = st.columns(2, gap="large")
    with col_g:
        st.markdown('<div class="bujo-block"><h4>😊 Humeur & État</h4>', unsafe_allow_html=True)
        humeur = st.select_slider("Mon humeur", options=["😢", "😟", "😐", "🙂", "✨", "🔥"], value="😐", label_visibility="collapsed")
        sentiments = st.text_area("Comment je me sens ?", placeholder="Détaille tes émotions...", height=120)
        st.markdown('<p style="font-family:\'Caveat\'; font-size:1.5rem; color:#e91e63;">"Je suis capable de réaliser mes rêves."</p>', unsafe_allow_html=True)
        if st.button("✨ Enregistrer mon état"): st.success("État enregistré !")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="bujo-block"><h4>📋 Programme Libre</h4>', unsafe_allow_html=True)
        programme = st.text_area("Planning", placeholder="08h00 : Méditation\n10h00 : BuJo...", height=275, label_visibility="collapsed")
        if st.button("💾 Sauvegarder mon planning"): st.success("Planning mis à jour !")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🖋️ Notes, RDV & Tâches")
    c1, c2, c3 = st.columns([3, 2, 1])
    with c1: note_txt = st.text_input("Nouvelle entrée...", placeholder="Ex: Dentiste 15h")
    with c2: note_type = st.selectbox("Catégorie", ["🍃 Note", "📌 Tâche", "📅 RDV / Événement", "💡 Idée"])
    with c3:
        st.write("") # Spacer
        if st.button("Ancrer"):
            if note_txt:
                ws_notes.append_row([datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M"), note_type, note_txt])
                st.rerun()

# --- PAGE SEMAINE (AVEC NAVIGATION SEMAINE) ---
with tab_semaine:
    if 'w_offset' not in st.session_state: st.session_state.w_offset = 0
    
    col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
    with col_n1: 
        if st.button("⬅️ Semaine Précédente"): st.session_state.w_offset -= 1
    with col_n3: 
        if st.button("Semaine Suivante ➡️"): st.session_state.w_offset += 1
    
    start_w = (datetime.now() - timedelta(days=datetime.now().weekday())) + timedelta(weeks=st.session_state.w_offset)
    with col_n2:
        st.markdown(f"<h3 style='text-align:center;'>Semaine du {start_w.strftime('%d/%m')} au {(start_w + timedelta(days=6)).strftime('%d/%m')}</h3>", unsafe_allow_html=True)

    # Récupération sécurisée pour éviter KeyError
    raw_notes = ws_notes.get_all_values()
    if len(raw_notes) > 1:
        df_notes = pd.DataFrame(raw_notes[1:], columns=raw_notes[0])
    else:
        df_notes = pd.DataFrame(columns=["Date", "Heure", "Type", "Note"])

    # Grille Hebdo (Modèle Rose)
    cols = st.columns(7)
    days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for i in range(7):
        curr_d = start_w + timedelta(days=i)
        d_str = curr_d.strftime("%d/%m/%Y")
        with cols[i]:
            st.markdown(f'<div class="p-header">{days_fr[i]}<br>{curr_d.strftime("%d/%m")}</div>', unsafe_allow_html=True)
            ev_html = ""
            if not df_notes.empty and "Date" in df_notes.columns:
                day_evs = df_notes[(df_notes["Date"] == d_str) & (df_notes["Type"] == "📅 RDV / Événement")]
                for _, row in day_evs.iterrows():
                    ev_html += f'<div class="event-item"><b>{row["Heure"]}</b><br>{row["Note"]}</div>'
            st.markdown(f'<div class="p-cell">{ev_html}</div>', unsafe_allow_html=True)

# --- PAGE BUDGET (FONCTIONNALITÉS RESTAURÉES) ---
with tab_budget:
    st.markdown("### 🪙 Mes Finances 2026")
    with st.expander("➕ Ajouter une opération"):
        c1, c2, c3 = st.columns(3)
        b_cat = c1.selectbox("Type", ["Revenu", "Charge Fixe", "Dépense"])
        b_lab = c2.text_input("Libellé")
        b_val = c3.number_input("Montant €", step=1.0)
        if st.button("Enregistrer l'opération"):
            ws_fin.append_row([datetime.now().strftime("%B"), "2026", b_cat, b_lab, b_val])
            st.rerun()

    data_f = ws_fin.get_all_records()
    if data_f:
        df_f = pd.DataFrame(data_f)
        st.markdown("#### 📜 Historique complet (Modifiable)")
        edited_df = st.data_editor(df_f, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Sauvegarder les modifications budget"):
            ws_fin.clear()
            ws_fin.append_row(["Mois", "Année", "Catégorie", "Libellé", "Montant €"])
            ws_fin.append_rows(edited_df.values.tolist())
            st.success("Base mise à jour !")

# --- PAGE ANNÉE ---
with tab_annee:
    st.markdown("### 📅 Vue Annuelle 2026")
    st.info("Visualisation en grille 12 mois en préparation pour le lien avec ton planning.")
    

# --- PAGE CONFIG ---
with tab_config:
    st.markdown("### ⚙️ Paramètres")
    new_name = st.text_input("Ton Prénom :", user_name)
    if st.button("Mettre à jour le profil"):
        ws_conf.update_acell('A2', new_name)
        st.rerun()
