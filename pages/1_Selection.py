import streamlit as st
import pandas as pd

# Fonction pour sauvegarder les paramètres dans la session
def save_parameters():
    st.session_state['currency'] = st.session_state.get('currency_input')
    st.session_state['stock_index'] = st.session_state.get('stock_index_input')
    st.session_state['indice'] = st.session_state.get('indice_input')
    st.session_state['country'] = st.session_state.get('country_input') if st.session_state.get('indice_input') == 'Géographique' else None

# Initialisation des valeurs par défaut dans la session
if 'currency' not in st.session_state:
    st.session_state.currency = 'USD'
if 'stock_index' not in st.session_state:
    st.session_state.stock_index = 'S&P500'
if 'indice' not in st.session_state:
    st.session_state.indice = 'High vol PER'
if 'country' not in st.session_state:
    st.session_state.country = None

st.title('Sélection des Paramètres')

# Widgets de sélection
st.selectbox(
    'Choisissez la devise des résultats:',
    ['USD', 'EUR', 'GBP', 'JPY', 'CNY'],
    key='currency_input',
    index=['USD', 'EUR', 'GBP', 'JPY', 'CNY'].index(st.session_state.currency)
)

st.selectbox(
    'Choisissez l\'univers d\'investissement:',
    ['S&P500', 'Eurostoxx600'],
    key='stock_index_input',
    index=['S&P500', 'Eurostoxx600'].index(st.session_state.stock_index)
)

# Widget pour sélectionner l'indice, déclenchant une mise à jour instantanée
indice = st.radio(
    'Choisissez l\'indice que vous souhaitez afficher:',
    ['High vol PER', 'Momentum 6 months', 'Géographique'],
    key='indice_input',
    index=['High vol PER', 'Momentum 6 months', 'Géographique'].index(st.session_state.indice)
)

# Si "Géographique" est sélectionné, afficher la liste des pays
if indice == 'Géographique':
    try:
        # Charger la liste des pays depuis le fichier Excel
        countries_list = pd.read_excel("Data_projets_M1EEF - fige.xlsx", sheet_name="Qualitativ_2018")["COUNTRY"].unique().tolist()
        countries_list.sort()

        # Widget pour choisir un pays
        st.selectbox(
            'Choisissez le pays à étudier:',
            countries_list,
            key='country_input',
            index=countries_list.index(st.session_state.country) if st.session_state.country in countries_list else 0
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement de la liste des pays : {e}")

# Bouton de validation
if st.button('Valider les paramètres'):
    save_parameters()
    st.success('Paramètres sauvegardés! Vous pouvez maintenant aller à la page de visualisation.')
