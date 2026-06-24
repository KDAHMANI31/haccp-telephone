import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuration de la page adaptée au téléphone
st.set_page_config(page_title="HACCP Mobile - Chambres Froides", layout="centered")

# 2. Sécurité par mot de passe
if "auth_mobile" not in st.session_state:
    st.session_state["auth_mobile"] = False

if not st.session_state["auth_mobile"]:
    st.title("🔐 Accès Mobile - HACCP")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter", use_container_width=True):
        if password == "Haccp2026":
            st.session_state["auth_mobile"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# --- INITIALISATION DU REGISTRE ---
if "data_mobile_cf" not in st.session_state:
    st.session_state["data_mobile_cf"] = pd.DataFrame(columns=[
        "Date/Heure", "Contrôleur", "Zone / Service", "Chambre Froide", "Température", "Conformité", "Observations"
    ])

# --- STRUCTURE EXACTE DES CHAMBRES FROIDES ---
STRUCTURE_HOTEL = {
    "Cuisine Centrale": [
        "Chambre 1 (Positive)", 
        "Chambre 2 (Positive)", 
        "Chambre 3 (Positive)", 
        "Chambre 4 (Négative)"
    ],
    "Pâtisserie": [
        "Chambre 5 (Positive)", 
        "Chambre 6 (Positive)", 
        "Chambre 7 (Positive)", 
        "Chambre 8 (Négative)"
    ],
    "Boucherie": [
        "Chambre 9 (Positive)", 
        "Chambre 10 (Négative)", 
        "Chambre 11 (Positive)", 
        "Chambre 12 (Négative)", 
        "Chambre 13 (Positive)", 
        "Chambre 14 (Négative)", 
        "Chambre 15 (Positive)", 
        "Chambre 16 (Négative)"
    ],
    "Food Store": [
        "Chambre 17 (Positive)", 
        "Chambre 18 (Négative)", 
        "Chambre 19 (Positive)", 
        "Chambre 20 (Négative)", 
        "Chambre 21 (Positive)", 
        "Chambre 22 (Positive)", 
        "Chambre 23 (Positive)"
    ]
}

# --- INTERFACE MOBILE ---
st.title("🌡️ Répertoire des Chambres Froides")
st.write("Saisie sectorisée avec alertes HACCP automatiques.")

with st.form("form_haccp_mobile", clear_on_submit=True):
    nom_ctrl = st.text_input("Nom du contrôleur", value="Khaled Dahmani")
    date_saisie = st.text_input("📅 Date & Heure du contrôle", value=datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    # 1. Sélection de la Zone
    zone_choisie = st.selectbox("Sélectionner la Zone :", list(STRUCTURE_HOTEL.keys()))
    
    # 2. Sélection de la Chambre de cette zone
    cf_choisie = st.selectbox("Sélectionner la Chambre Froide :", STRUCTURE_HOTEL[zone_choisie])
    
    # 🛑 CASE HORS SERVICE
    hors_service = st.checkbox("❌ Cet équipement est HORS SERVICE")
    
    # 3. Saisie de la température (Masquée automatiquement si Hors Service)
    valeur_defaut = -18.0 if "Négative" in cf_choisie else 2.0
    temperature = st.number_input("Température relevée (°C) :", value=valeur_defaut, step=0.5)
    
    remarques = st.text_input("Observations / Actions Correctives")
    
    submit = st.form_submit_button("📱 Enregistrer le contrôle", use_container_width=True)
    
    if submit:
        # Cas 1 : La chambre froide est Hors Service
        if hors_service:
            statut = "HORS SERVICE ❌"
            temp_finale = "N/A"
            obs_finale = f"ÉQUIPEMENT HORS SERVICE. {remarques}".strip()
            st.warning(f"⚠️ {cf_choisie} enregistrée comme Hors Service.")
        
        # Cas 2 : La chambre froide est en fonction (Calcul HACCP)
        else:
            temp_finale = f"{temperature} °C"
            obs_finale = remarques if remarques else "R.A.S"
            
            if "Négative" in cf_choisie:
                # Règle Négative : <= -18°C
                if temperature <= -18.0:
                    statut = "Conforme ✅"
                    st.success(f"✅ Conforme : {cf_choisie} est à {temperature} °C")
                else:
                    statut = "🚨 ALERTE NON-CONFORME"
                    st.error(f"🚨 ALERTE : {cf_choisie} est trop chaude ({temperature} °C) ! Norme <= -18°C")
            else:
                # Règle Positive : <= 4°C
                if temperature <= 4.0:
                    statut = "Conforme ✅"
                    st.success(f"✅ Conforme : {cf_choisie} est à {temperature} °C")
                else:
                    statut = "🚨 ALERTE NON-CONFORME"
                    st.error(f"🚨 ALERTE : {cf_choisie} est trop chaude ({temperature} °C) ! Norme <= 4°C")

        # Ajout des données au tableau de la session
        nouvelle_mesure = pd.DataFrame([{
            "Date/Heure": date_saisie,
            "Contrôleur": nom_ctrl,
            "Zone / Service": zone_choisie,
            "Chambre Froide": cf_choisie,
            "Température": temp_finale,
            "Conformité": statut,
            "Observations": obs_finale
        }])
        
        st.session_state["data_mobile_cf"] = pd.concat([st.session_state["data_mobile_cf"], nouvelle_mesure], ignore_index=True)

# --- RECAPITULATIF ET TELECHARGEMENT ---
if not st.session_state["data_mobile_cf"].empty:
    st.write("---")
    st.subheader("📊 Données enregistrées (Session)")
    st.dataframe(st.session_state["data_mobile_cf"], use_container_width=True)
    
    csv_mobile = st.session_state["data_mobile_cf"].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Télécharger le rapport (.csv)",
        data=csv_mobile,
        file_name=f"haccp_chambres_froides_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
