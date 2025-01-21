import streamlit as st

st.set_page_config(
    page_title="Analyse d\'indices",
    page_icon="📈",
)

st.title('Bienvenue dans l\'Application d\'analyse d\'indices')

st.markdown("""
Cette application vous permet d'analyser différents indices boursiers.
            
### Comment utiliser l'application :

1. Allez à la page **Sélection** pour choisir vos paramètres :
   - Devise
   - Univers d'investissement
   - Type d'indice
   - Pays

2. Une fois les paramètres validés, rendez-vous sur la page **Visualisation** pour voir les résultats

3. Ensuite, vous pouvez consulter les **Indicateurs de Performance** et la **Composition de l'Indice** aux pages correspondantes.

### Types d'indices disponibles :
- High vol PER
- Momentum 6 months
- Géographique
            
Attention : - les premiers graphiques peuvent prendre un peu de temps à s'afficher, merci de patienter.
            - s'assurer de sélectionner le bon unnivers d'investissement avant de choisir le pays pour l'indice géographique.


Commencez par la page de sélection pour paramétrer votre analyse.
""")
