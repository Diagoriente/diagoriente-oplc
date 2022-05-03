import streamlit as st
import skill_importance_measure

pages = {
        "Comparaison de mesures de centralité": skill_importance_measure.run,
        "Comparaison de mesures de centralité2": skill_importance_measure.run,
        }

page = st.selectbox("Cas d'étude:", list(pages.keys()))

pages[page]()
