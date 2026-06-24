import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuration de la page adaptée au téléphone
st.set_page_config(page_title="HACCP Mobile - Températures", layout="centered")

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
        "Date/Heure", "Contrôleur", "Zone / Service", "Élément Contrôlé", "Température (°C)", "Conformité", "Observations"
    ])

# --- INTERFACE MOBILE ---
st.title("🌡️ Contrôle des Températures")
st.write("Saisie rapide pour les Chambres Froides et Buffets.")

with st.form("form_haccp_mobile", clear_on_submit=True):
    nom_ctrl = st.text_input("Nom du contrôleur", value="Khaled Dahmani")
    
    # Bouton automatique pour la date et l'heure actuelle
    date_saisie = st.text_input("📅 Date & Heure du contrôle", value=datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    # Reprise exacte des 6 zones de ton premier programme
    zone = st.selectbox("Sélectionner la Zone / Service :", [
        "Cuisine Centrale", 
        "Restaurant Principal", 
        "Boulangerie", 
        "Pâtisserie", 
        "Boucherie", 
        "Banquet"
    ])
    
    # Saisie simplifiée du nom de la Chambre Froide ou du Buffet
    nom_element = st.text_input("Nom / N° de l'élément", placeholder="Ex: CF Viandes N°1, Buffet Salades, Bain-marie N°2")
    
    # Type d'équipement pour appliquer la bonne alerte HACCP
    type_equipement = st.radio("Type d'équipement :", ["Chambre Froide", "Buffet Froid", "Buffet Chaud"], horizontal=True)
    
    # Température
    temperature = st.number_input("Température relevée (°C) :", value=2.0, step=0.5)
    
    remarques = st.text_input("Observations / Actions Correctives")
    
    submit = st.form_submit_button("📱 Enregistrer le contrôle", use_container_width=True)
    
    if submit:
        if not nom_element:
            st.error("⚠️ Veuillez écrire le nom de l'élément contrôlé.")
        else:
            # Règles de conformité et alertes automatiques
            if type_equipement == "Chambre Froide" and temperature <= 4.0:
                statut = "Conforme ✅"
                st.success(f"✅ Température conforme pour {nom_element} ({temperature} °C)")
            elif type_equipement == "Buffet Froid" and temperature <= 3.0:
                statut = "Conforme ✅"
                st.success(f"✅ Température conforme pour {nom_element} ({temperature} °C)")
            elif type_equipement == "Buffet Chaud" and temperature >= 63.0:
                statut = "Conforme ✅"
                st.success(f"✅ Température conforme pour {nom_element} ({temperature} °C)")
            else:
                statut = "🚨 NON CONFORME"
                st.error(f"🚨 ALERTE HORS NORME pour {nom_element} : {temperature} °C !")

            # Ajout au tableau
            nouvelle_mesure = pd.DataFrame([{
                "Date/Heure": date_saisie,
                "Contrôleur": nom_ctrl,
                "Zone / Service": zone,
                "Élément Contrôlé": f"{type_equipement} - {nom_element}",
                "Température (°C)": f"{temperature} °C",
                "Conformité": statut,
                "Observations": remarques if remarques else "R.A.S"
            }])
            
            st.session_state["data_mobile_cf"] = pd.concat([st.session_state["data_mobile_cf"], nouvelle_mesure], ignore_index=True)

# --- TABLEAU DE BORD ET TÉLÉCHARGEMENT ---
if not st.session_state["data_mobile_cf"].empty:
    st.write("---")
    st.subheader("📊 Mesures de la session")
    st.dataframe(st.session_state["data_mobile_cf"], use_container_width=True)
    
    csv_mobile = st.session_state["data_mobile_cf"].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Télécharger le rapport (.csv)",
        data=csv_mobile,
        file_name=f"haccp_mobile_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
