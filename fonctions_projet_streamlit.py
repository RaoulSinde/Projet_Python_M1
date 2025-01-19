# Fichier contenant les fonctions nécessaires au fonctionnement du code

# Importation des packages nécessaires

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st


# Fonctions de collecte des données


# Fonction qui crée et retraite un data frame à partir du prix des actions d'un indice
@st.cache_data
def get_df_prices(ticker):
    index_sheet = ticker + "_PX_LAST"
    df_prices = pd.read_excel("Data_projets_M1EEF - fige.xlsx", sheet_name=index_sheet)

    # Supprimer la première colonne et mettre les dates en indice
    df_prices = df_prices.drop(df_prices.columns[0], axis=1)
    df_prices = df_prices.set_index(df_prices.columns[0])

    # Gestion des valeurs manquantes

    # Suppression des colonnes dont la proportion de valeurs manquantes dépasse 10%
    df_prices = df_prices.dropna(axis=1, thresh=0.9*len(df_prices))

    # Remplacement des valeurs manquantes par la valeur précédente
    df_prices = df_prices.ffill()

    return df_prices


# Fonction qui crée des séries de prix pour différents intervalles de temps
@st.cache_data
def get_prices_series(df_prices, interval):
    index_prices_interval = df_prices[(df_prices.index.year >= interval[0]) & (df_prices.index.year <= interval[1])]

    return index_prices_interval


# Fonction qui crée un dataframe des données qualitatives des titres de l'indice sélectionné
@st.cache_data
def get_df_qualitative(df_prices, year):
    df_qualitative = pd.read_excel("Data_projets_M1EEF - fige.xlsx", sheet_name="Qualitativ_" + str(year))
    df_qualitative = df_qualitative.set_index(df_qualitative.columns[0])
    
    common_titles = df_prices.columns.intersection(df_qualitative.index)
    df_qualitative = df_qualitative.loc[common_titles]
    
    return df_qualitative


# Fonction qui extrait les données du facteur qualitatif numérique sélectionné
@st.cache_data
def get_indicator_data_num(df_qualitative, indicator):
    indicator_data = df_qualitative[indicator]
    indicator_data = indicator_data[pd.to_numeric(indicator_data, errors='coerce').notna()]

    return indicator_data


# Fonction qui extrait les données du facteur qualitatif sélectionné
@st.cache_data
def get_indicator_data(df_qualitative, indicator):
    indicator_data = df_qualitative[indicator]

    return indicator_data

@st.cache_data
def filter_qualitative_by_country(qualitative_data, country_target):
    # Filtrer les données qualitatives pour ne garder que les actions du pays cible
    qualitative_data_filtered = qualitative_data[qualitative_data['COUNTRY'].str.contains(country_target)]

    return qualitative_data_filtered

@st.cache_data
def filter_prices_by_country(prices, qualitative_data_filtered):   
    # Filtrer les prix pour ne garder que les actions dont le nom est en commun avec les données qualitatives filtrées
    prices_filtered = prices[prices.columns.intersection(qualitative_data_filtered.index)]

    return prices_filtered


# Fonction qui extrait les prix de l'indice de référence
@st.cache_data
def get_reference_prices(ticker):
    
    df_indices = pd.read_excel("Data_projets_M1EEF - fige.xlsx", sheet_name="Index")

    
    col_name = ticker + " Index" 
    col_idx = df_indices.columns.get_loc(col_name)


    df_reference_prices = df_indices.iloc[:, [col_idx - 1, col_idx]]
    df_reference_prices = df_reference_prices.set_index(df_reference_prices.columns[0])
    df_reference_prices = df_reference_prices.sort_index()

    return df_reference_prices


# Fonction qui extrait les données Forex
@st.cache_data
def get_forex_data():
    df_forex = pd.read_excel("Data_projets_M1EEF - fige.xlsx", sheet_name="Forex")

    df_forex = df_forex.drop(df_forex.columns[0], axis=1)
    df_forex = df_forex.set_index(df_forex.columns[0])
    df_forex = df_forex.loc["2019":"2021"]
    
    return df_forex


# Fonctions de calcul à partir des données collectées


# Fonction qui calcule les rendements quotidiens d'un dataframe de prix
@st.cache_data
def calculate_daily_returns(df_prices):
    df_daily_returns = df_prices.pct_change()

    return df_daily_returns


# Fonction qui calcule la volatilité annuelle d'un dataframe de rendements quotidiens
@st.cache_data
def calculate_volatility(df_daily_returns):
    df_vol = df_daily_returns.std() * np.sqrt(252)

    return df_vol


# Fonction qui convertit les prix d'une devise à une autre
@st.cache_data
def convert_prices(df_prices, df_forex, currency):

    if currency == "USD":
        df_prices_converted = df_prices
    else:
        df_prices_converted = df_prices / df_forex["EURUSD"]
        
        if currency != "EUR":
            pair = "EUR" + currency
            df_prices_converted = df_prices * df_forex[pair]

    return df_prices_converted

# Fonctions pour créer des séries à partir de conditions sur les données pour la construction des indices


# Fonction qui extrait les titres correspondant à un certain quantile d'une série
@st.cache_data
def get_percentile(df_values, percentile):
    quantile = df_values.quantile(percentile)
    df_percentile = df_values[(df_values >= quantile)]
    
    return df_percentile
    


# Fonction qui détermine les titres qui appartiennent à deux séries
@st.cache_data
def get_intersection(df1, df2):
    df_intersection = df1.index.intersection(df2.index)

    return df_intersection


# Fonction qui permet de réduire une série pour qu'elle corresponde aux indices d'une série index
def reduce_series(df, df_ref):
    df_reduced = df.loc[df_ref]

    return df_reduced

# Fonction qui renvoie un dataframe avec les éléments de deux séries avec les mêmes indices
@st.cache_data
def get_common_elements(df1, df2):
    df_common = pd.merge(df1, df2, left_index=True, right_index=True, how="inner")

    return df_common


# Fonction qui détermine les poids des titres dans un indice selon la capitalisation boursière
@st.cache_data
def calculate_weights(df_capitalization):
    df_weights = df_capitalization / df_capitalization.sum()

    return df_weights



# Fonctions de suivi d'indice


# Fonction qui suit la valeur de l'indice 
@st.cache_data
def index_tracking(df_prices, df_weights):
    
    df_index_values = []
   
    # Calculer les prix de l'indice 
    for date in df_prices.index:
        df_index = (df_weights*df_prices.loc[date]).sum()
        df_index_values.append(df_index)
        
    # Convertir la liste en Series avec l'index de df_prices
    df_index_values = pd.Series(df_index_values, index=df_prices.index)

    return df_index_values


# Fonction qui assure la continuité des valeurs de l'indice après rebalancement
@st.cache_data
def continuity_index(df_index_values, df_previous_values):
    df_new_values = df_index_values * df_previous_values.iloc[-1] / df_index_values.iloc[0]

    return df_new_values



# Fonctions de visualisation

# Fonction qui concatène les séries temporelles de plusieurs dataframes
@st.cache_data
def aggregate_series(*series):
    aggregated_series = pd.concat(series, axis=0)

    return aggregated_series


# Fonction qui trace les séries temporelles d'un 
@st.cache_data
def plot_series(df_values, title):
    
    fig = go.Figure()
    
    for col in df_values.columns:
        fig.add_trace(go.Scatter(
            x=df_values.index, 
            y=df_values[col], 
            mode='lines', 
            name=col 
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Valeur',
        legend_title='Séries'
    )

    return fig






# Fonction qui crée des séries de prix pour différents intervalles de temps (année et mois)
@st.cache_data
def get_prices_series_2(df_prices, interval):
    # Filtrage par intervalle d'années
    index_prices_interval = df_prices[(df_prices.index.year >= interval[0]) & (df_prices.index.year <= interval[1])]
    
    # Série pour les 6 premiers mois
    first_half = index_prices_interval[index_prices_interval.index.month <= 6]
    
    # Série pour les 6 derniers mois
    second_half = index_prices_interval[index_prices_interval.index.month > 6]
    
    return first_half, second_half


def selection_top_100(df_returns):
    
    df_decroiss = df_returns.sort_values(by=df_returns.columns[0], ascending=False)
    top_100_df = df_decroiss.head(100)
    
    return top_100_df


