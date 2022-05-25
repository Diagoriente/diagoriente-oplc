import streamlit as st
import skill_importance_measure
import skill_distance
import skill_accessibility

def home():
    st.write("Sélectionnez un cas d'étude ci-dessus")

pages = {
        "Accueil": home,
        "Comparaison de mesures de centralité": skill_importance_measure.run,
        "Comparaison de distances entre compétences": skill_distance.run,
        "Mesurer l'accessibilité d'une compétence": skill_accessibility.run,
        }

page = st.selectbox("Cas d'étude:", list(pages.keys()))

pages[page]()
