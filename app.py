import streamlit as st
import requests
import difflib
import json

st.set_page_config(page_title="Gels des avoirs - Recherche API", page_icon="🔒")
st.title("🔍 Recherche dans le registre national des gels (API État)")

# Champs utilisateur
nom = st.text_input("Nom (obligatoire)").strip().upper()
prenom = st.text_input("Prénom (optionnel)").strip()
recherche_floue = st.checkbox("🔁 Activer la recherche approximative", value=True)

# Endpoint officiel + User-Agent
API_URL = "https://gels-avoirs.dgtresor.gouv.fr/ApiPublic/api/v1/publication/derniere-publication-fichier-json"
HEADERS = {"User-Agent": "OtterWise/RechercheGelsApp"}

@st.cache_data
def charger_donnees_depuis_api():
    try:
        r = requests.get(API_URL, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        publication = data.get("Publications", [])[0]
        date = publication.get("Date", "inconnue")
        details = publication.get("PublicationDetail", [])
        return details, date
    except Exception as e:
        return None, str(e)

# Bouton de recherche
if st.button("Rechercher"):
    if not nom:
        st.warning("Merci d’entrer au moins un nom.")
    else:
        registre, date_pub = charger_donnees_depuis_api()

        if registre is None:
            st.error(f"Erreur lors de la récupération des données : {date_pub}")
        else:
            st.write(f"📅 Données publiées le **{date_pub}**")
            resultats = []

            for personne in registre:
                nom_personne = personne.get("Nom", "").upper()
                prenom_personne = ""
                naissance = motifs = fondement = ""

                for champ in personne.get("RegistreDetail", []):
                    if champ["TypeChamp"] == "PRENOM":
                        prenom_personne = champ["Valeur"]
                    if champ["TypeChamp"] == "DATE_DE_NAISSANCE":
                        naissance = champ["Valeur"]
                    if champ["TypeChamp"] == "MOTIFS":
                        motifs = champ["Valeur"]
                    if champ["TypeChamp"] == "FONDEMENT_JURIDIQUE":
                        fondement = champ["Valeur"]

                if recherche_floue:
                    nom_match = difflib.get_close_matches(nom, [nom_personne], n=1, cutoff=0.7)
                    prenom_match = True if not prenom else difflib.get_close_matches(prenom.lower(), [prenom_personne.lower()], n=1, cutoff=0.7)
                else:
                    nom_match = nom == nom_personne
                    prenom_match = True if not prenom else prenom.lower() == prenom_personne.lower()

                if nom_match and prenom_match:
                    resultats.append({
                        "Nom": nom_personne,
                        "Prénom": prenom_personne,
                        "Naissance": naissance,
                        "Motif": motifs,
                        "Fondement juridique": fondement
                    })

            st.success(f"✅ {len(resultats)} résultat(s) trouvé(s)")
            for r in resultats:
                st.markdown("---")
                st.write(f"**👤 {r.get('Nom')} {r.get('Prénom', '')}**")
                if r.get("Naissance"):
                    st.write(f"📅 Naissance : {r['Naissance']}")
                if r.get("Motif"):
                    st.write(f"📌 Motif : {r['Motif']}")
                if r.get("Fondement juridique"):
                    st.write(f"⚖️ Base juridique : {r['Fondement juridique']}")

            if not resultats:
                st.info("Aucun résultat trouvé. Essaie une autre orthographe ou active la recherche approximative.")
