import streamlit as st
import requests
import difflib

st.set_page_config(page_title="OtterWise – Gels des avoirs", page_icon="🦦")
st.markdown("""
<style>
h1 { text-align: center; color: #00b4d8; }
header, footer { visibility: hidden; }
footer:after {
    content:'Propulsé par OtterWise 🦦';
    visibility: visible;
    display: block;
    text-align: center;
    padding: 1rem;
    color: gray;
    font-size: 0.9em;
}
</style>
""", unsafe_allow_html=True)

st.title("🔍 OtterWise – Recherche Gels des avoirs")

nom = st.text_input("🔠 Nom (obligatoire)").strip().upper()
prenom = st.text_input("🧑‍🦱 Prénom (optionnel)").strip()
recherche_floue = st.checkbox("🔁 Activer la recherche approximative", value=True)

API_URL = "https://gels-avoirs.dgtresor.gouv.fr/ApiPublic/api/v1/publication/derniere-publication-fichier-json"
HEADERS = {"User-Agent": "OtterWise/1.0 (+https://otterwise.fr)"}

def charger_donnees():
    try:
        r = requests.get(API_URL, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        publication = data.get("Publications", [])[0]
        date = publication.get("Date", "inconnue")
        return publication.get("PublicationDetail", []), date
    except Exception as e:
        return None, str(e)

if st.button("🔍 Rechercher"):
    if not nom:
        st.warning("Merci d’entrer un nom.")
    else:
        registre, date_pub = charger_donnees()
        if not registre:
            st.error(f"Erreur API : {date_pub}")
        else:
            st.caption(f"📅 Données publiées le **{date_pub}**")
            resultats = []

            for personne in registre:
                nom_p = personne.get("Nom", "").upper()
                prenom_p = ""
                naissance = motifs = fondement = ""

                for champ in personne.get("RegistreDetail", []):
                    if champ["TypeChamp"] == "PRENOM": prenom_p = champ["Valeur"]
                    if champ["TypeChamp"] == "DATE_DE_NAISSANCE": naissance = champ["Valeur"]
                    if champ["TypeChamp"] == "MOTIFS": motifs = champ["Valeur"]
                    if champ["TypeChamp"] == "FONDEMENT_JURIDIQUE": fondement = champ["Valeur"]

                if recherche_floue:
                    nom_match = difflib.get_close_matches(nom, [nom_p], n=1, cutoff=0.7)
                    prenom_match = True if not prenom else difflib.get_close_matches(prenom.lower(), [prenom_p.lower()], n=1, cutoff=0.7)
                else:
                    nom_match = nom == nom_p
                    prenom_match = True if not prenom else prenom.lower() == prenom_p.lower()

                if nom_match and prenom_match:
                    resultats.append({
                        "Nom": nom_p,
                        "Prénom": prenom_p,
                        "Naissance": naissance,
                        "Motif": motifs,
                        "Fondement juridique": fondement
                    })

            st.success(f"✅ {len(resultats)} résultat(s) trouvé(s)")
            for r in resultats:
                st.markdown("---")
                st.markdown(f"### 👤 {r['Nom']} {r['Prénom']}")
                if r["Naissance"]: st.write(f"📅 Naissance : {r['Naissance']}")
                if r["Motif"]: st.write(f"📌 Motif : {r['Motif']}")
                if r["Fondement juridique"]: st.write(f"⚖️ Fondement juridique : {r['Fondement juridique']}")

            if not resultats:
                st.info("Aucun résultat trouvé. Essaie une autre orthographe ou active la recherche approximative.")
