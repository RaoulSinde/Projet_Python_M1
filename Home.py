import streamlit as st

st.set_page_config(
    page_title="Application d'Investissement",
    page_icon="📈",
)

st.title('Bienvenue dans l\'Application d\'Investissement')

st.markdown("""
Cette application vous permet d'analyser différents indices d'investissement.

### Comment utiliser l'application:

1. Allez à la page **📊 Selection** pour choisir vos paramètres:
   - Devise
   - Univers d'investissement
   - Type d'indice
   - Pays (si applicable)

2. Une fois les paramètres validés, rendez-vous sur la page **📈 Visualisation** pour voir les résultats

### Types d'indices disponibles:
- High vol PER
- Momentum 6 months
- Géographique

Commencez par la page de sélection pour paramétrer votre analyse.
""")
