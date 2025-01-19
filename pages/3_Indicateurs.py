import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import plotly.graph_objects as go

def calculer_indicateurs(df_indice: pd.Series, df_reference: pd.Series, risk_free_rate=0.01):
    """
    Calcule les indicateurs de performance et de risque pour l'indice sélectionné.
    """
    # Convertir les séries en DataFrame
    df_indice = df_indice.to_frame()
    df_reference = df_reference.to_frame()
    
    # Performance totale
    performance_totale = ((df_indice.iloc[-1, 0] - df_indice.iloc[0, 0]) / df_indice.iloc[0, 0]) * 100

    # Rendements mensuels
    rend_indice = df_indice.pct_change()
    rend_reference = df_reference.pct_change()
    
    # Performance annualisée
    perf_annuelle = ((1 + rend_indice.mean().iloc[0])**12 - 1) * 100
    
    # Max drawdown
    cumulative_max = df_indice.cummax()
    drawdowns = (df_indice - cumulative_max) / cumulative_max
    max_drawdown = (drawdowns.min().iloc[0] * 100).round(2)
    
    # Volatilité annualisée
    volatilite_annuelle = ((rend_indice.std().iloc[0] * np.sqrt(12)) * 100).round(2)
    
    # Ratio de Sharpe
    sharpe_ratio = ((perf_annuelle - risk_free_rate) / volatilite_annuelle).round(2)
    
    # Beta et Alpha
    rend_indice_clean = rend_indice.dropna()
    rend_reference_clean = rend_reference.dropna()
    
    # S'assurer que les deux séries ont la même longueur
    common_index = rend_indice_clean.index.intersection(rend_reference_clean.index)
    rend_indice_clean = rend_indice_clean.loc[common_index]
    rend_reference_clean = rend_reference_clean.loc[common_index]
    
    X = sm.add_constant(rend_reference_clean)
    model = sm.OLS(rend_indice_clean, X).fit()
    beta = model.params[1].round(2)
    alpha = (model.params[0] * 12).round(4)  # Annualisé

    return {
        "Performance Totale": f"{performance_totale.round(2)}%",
        "Performance Annualisée": f"{perf_annuelle.round(2)}%",
        "Max Drawdown": f"{max_drawdown}%",
        "Volatilité Annualisée": f"{volatilite_annuelle}%",
        "Ratio de Sharpe": sharpe_ratio,
        "Beta": beta,
        "Alpha": alpha
    }

st.title('Indicateurs de Performance')

# Vérifier si les données nécessaires sont disponibles
required_data = ['currency', 'stock_index', 'indice', 'df_indice', 'df_reference']
if not all(param in st.session_state for param in required_data):
    st.error('Veuillez d\'abord visualiser les résultats dans la page de visualisation.')
    st.stop()

try:
    # Récupérer les paramètres et les données
    indice = st.session_state['indice']
    stock_index = st.session_state['stock_index']
    country = st.session_state.get('country')
    
    # Titre dynamique selon l'indice
    if indice == "Géographique":
        titre_indice = f"l'indice {country}"
    else:
        titre_indice = f"l'indice {indice}"
    
    # Calculer les indicateurs
    indicateurs_dict = calculer_indicateurs(
        st.session_state['df_indice'],
        st.session_state['df_reference']
    )
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Indicateurs</b>", "<b>Valeurs</b>"],
            fill_color='royalblue',  # Couleur de fond des en-têtes
            font=dict(color='white', size=14),  # Texte blanc pour les en-têtes
            align='center'
        ),
        cells=dict(
            values=[list(indicateurs_dict.keys()), list(indicateurs_dict.values())],
            fill_color='#d4f5d4',  # Fond vert clair pour les cellules
            font=dict(color='black', size=12),  # Texte noir pour les cellules
            align='center'
        )
    )])

    # Personnalisation du tableau
    fig.update_layout(
        title_text=f"Indicateurs de performance pour {titre_indice}",
        title_font=dict(size=16, color='white'),
        title_x=0,
        title_xanchor='left',
        margin=dict(l=20, r=20, t=50, b=20)
    )

    # Afficher le tableau dans Streamlit
    st.plotly_chart(fig)

    
    # Ajouter des explications sur les indicateurs
    with st.expander("Explications des indicateurs"):
        st.markdown("""
        - **Performance Totale**: Rendement total de l'indice sur la période étudiée
        - **Performance Annualisée**: Rendement annuel moyen de l'indice
        - **Max Drawdown**: Perte maximale subie par l'indice depuis son plus haut historique
        - **Volatilité Annualisée**: Mesure de la dispersion des rendements sur une base annuelle
        - **Ratio de Sharpe**: Mesure de la performance ajustée du risque (rendement excédentaire par unité de risque)
        - **Beta**: Mesure de la sensibilité de l'indice aux variations du marché de référence
        - **Alpha**: Surperformance de l'indice par rapport au marché de référence (annualisé)
        """)

except Exception as e:
    st.error(f"Une erreur s'est produite lors du calcul des indicateurs: {str(e)}")
    st.write("Veuillez vérifier les données d'entrée et réessayer.")