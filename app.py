import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuration de la page adaptée aux mobiles
st.set_page_config(page_title="HACCP Mobile - Chambres Froides", layout="centered")

# 2. Sécurité par mot de passe
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Accès Cuisine - HACCP")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if password == "Haccp2026":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# --- INITIALISATION DES DONNÉES ---
if "data_cf" not in st.session_state:
    st.session_state["data_cf"] = pd.DataFrame(columns=[
        "Date/Heure", "Contrôleur", "Zone", "Chambre Froide", "Température (°C)", "Conformité", "Observations"
    ])

# --- INTERFACE MOBILE ---
st.title("🌡️ Contrôle Chambres Froides")
st.write("Zone d'enregistrement rapide pour smartphone.")

with st.form("form_mobile_cf", clear_on_submit=True):
    nom_ctrl = st.text_input("Nom de l'hygiéniste / contrôleur", value="Khaled Dahmani")
    
    zone = st.selectbox("Zone :", ["Cuisine Centrale", "Boulangerie", "Pâtisserie", "Boucherie", "Économat"])
    
    nom_cf = st.text_input("Nom / N° de la Chambre Froide", placeholder="Ex: CF Viandes N°1")
    
    # Un sélecteur adapté aux écrans tactiles des téléphones
    temperature = st.number_input("Température relevée (°C)", value=2.0, step=0.5)
    
    remarques = st.text_input("Remarques (Actions si non-conforme)")
    
    submit = st.form_submit_button("📱 Enregistrer le contrôle")
    
    if submit:
        if not nom_cf:
            st.error("Veuillez écrire le nom de la chambre froide.")
        else:
            # Règle HACCP standard : conforme si <= 4.0°C
            statut = "Conforme ✅" if temperature <= 4.0 else "NON CONFORME ❌"
            
            nouvelle_ligne = pd.DataFrame([{
                "Date/Heure": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Contrôleur": nom_ctrl,
                "Zone": zone,
                "Chambre Froide": nom_cf,
                "Température (°C)": temperature,
                "Conformité": statut,
                "Observations": remarques if remarques else "R.A.S"
            }])
            
            st.session_state["data_cf"] = pd.concat([st.session_state["data_cf"], nouvelle_ligne], ignore_index=True)
            st.success(f"✅ Enregistré pour {nom_cf} !")

# --- COIN TÉLÉCHARGEMENT SUR LE TÉLÉPHONE ---
if not st.session_state["data_cf"].empty:
    st.write("---")
    st.subheader("📊 Mesures de la journée")
    st.dataframe(st.session_state["data_cf"])
    
    csv = st.session_state["data_cf"].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Télécharger le fichier Excel sur mon téléphone",
        data=csv,
        file_name=f"haccp_chambres_froides_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
