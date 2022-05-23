import streamlit as st
import skill_importance_measure
import skill_distance

pages = {
        "Comparaison de mesures de centralité": skill_importance_measure.run,
        "Comparaison de distances entre compétences": skill_distance.run,
        }

page = st.selectbox("Cas d'étude:", list(pages.keys()))

pages[page]()
