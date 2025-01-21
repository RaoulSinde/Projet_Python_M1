import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def composition_index(df_weights):
    """
    Extraire la liste des titres composant l'indice, et leurs poids
    """
    composition = df_weights.index.tolist()
    
    return composition

def create_composition_table(composition, title):
    """
    Crée un tableau Plotly affichant les titres et leurs poids dans l'indice.
    """
    # Créer le tableau Plotly à partir de la liste des titres
    table_composition = go.Figure(data=[go.Table(
        header=dict(values=["Titres"]),
        cells=dict(values=[composition])  # Utilisation de "composition" ici pour les valeurs des cellules
    )])
    
    # Ajouter un titre au tableau
    table_composition.update_layout(
        title=title,
        title_font=dict(size=16, color='white'),
        title_x=0,
        title_xanchor='left',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return table_composition


# Titre de la page
st.title('Composition de l\'Indice')

# Vérifier si les données nécessaires sont disponibles
if 'df_weights' not in st.session_state:
    st.error('Veuillez d\'abord visualiser les résultats dans la page de visualisation ou calculer les poids de l\'indice.')
    st.stop()

try:
    # Récupérer les données des poids de l'indice
    df_weights = st.session_state['df_weights']

    # Extraire la composition de l'indice (titres et poids)
    composition = df_weights.index.tolist()

    # Titre dynamique pour la composition de l'indice
    titre_composition = f"Composition de l'indice {st.session_state.get('indice')}"

    # Créer le tableau de la composition de l'indice
    composition_table = create_composition_table(composition, titre_composition)

    # Afficher le tableau dans Streamlit
    st.plotly_chart(composition_table)
    
except Exception as e:
    st.error(f"Une erreur s'est produite lors de l'affichage de la composition de l'indice: {str(e)}")
    st.write("Veuillez vérifier les données d'entrée et réessayer.")
