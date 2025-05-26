import streamlit as st
import requests
import difflib

# CONFIG PAGE
st.set_page_config(
    page_title="OtterWise – Recherche Gels des Avoirs",
    page_icon="🦦",
    layout="centered",
)

# STYLE HEADER
st.markdown("""
<style>
h1 {
    text-align: center;
    color: #00b4d8;
}
header, footer {visibility: hidden;}
footer:after {
    content:'Propulsé par OtterWise 🦦 – Solutions no-code intelligentes';
    visibility: visible;
    display: block;
    text-align: center;
    padding: 1rem;
    color: gray;
    font-size: 0.9em;
}
</style>
""", unsafe_allow_html=True)

# BANDEAU
st.image("https://avatars.githubusercontent.com/u/150202170", width=72)
st.title("🔍 OtterWise – Registre des gels des avoirs")

# FORM
nom = st.text_input("🔠 Nom recherché (obligatoire)").strip().upper()
prenom = st.text_input("🧑‍🦱 Prénom (optionnel)").strip()
recherche_floue = st.checkbox("🔁 Activer la recherche approximative", value=True)

# API CONFIG
API_URL = "https://gels-avoirs.dgtresor.gouv.fr/ApiPublic/api/v1/publication/derniere-publication-fichier-json"
HEADERS = {"User-Agent": "OtterWise/1.0 (+https://otterwise.fr)"}

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

# RECHERCHE
if st.button("🔍 Rechercher"):
    if not nom:
        st.warning("Merci d’entrer au moins un nom.")
    else:
        registre, date_pub = charger_donnees_depuis_api()

        if registre is None:
            st.error(f"❌ Erreur API : {date_pub}")
        else:
            st.caption(f"📅 Dernière publication : {date_pub}")
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
                st.markdown(f"### 👤 {r['Nom']} {r['Prénom']}")
                if r["Naissance"]:
                    st.write(f"📅 Naissance : {r['Naissance']}")
                if r["Motif"]:
                    st.write(f"📌 Motif : {r['Motif']}")
                if r["Fondement juridique"]:
                    st.write(f"⚖️ Fondement juridique : {r['Fondement juridique']}")

            if not resultats:
                st.info("Aucun résultat trouvé. Essaie une autre orthographe ou active la recherche floue.")
