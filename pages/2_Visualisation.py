import streamlit as st
import fonctions_projet_streamlit as f
import pandas as pd

st.title('Visualisation des Résultats')

# Vérifier si les paramètres ont été sélectionnés
if not all(param in st.session_state for param in ['currency', 'stock_index', 'indice']):
    st.error('Veuillez d\'abord sélectionner les paramètres dans la page de sélection.')
    st.stop()

# Récupérer les paramètres
currency = st.session_state['currency']
stock_index = st.session_state['stock_index']
indice = st.session_state['indice']
country = st.session_state.get('country')

# Selon l'univers d'investissement, choisir le ticker
ticker = "SPX" if stock_index == "S&P500" else "SXXP"

# Récupérer les données de change (Forex)
df_forex = f.get_forex_data()

# Création du dataframe des prix des actions
df_prices = f.get_df_prices(ticker)

# Création de dataframes des données qualitatives des titres
df_qualitative_years = {}
for year in range(2018, 2021):
    df_qualitative_years[f"df_qualitative_{year}"] = f.get_df_qualitative(df_prices, year)

# Extraction de la série des prix de l'indice de référence 
df_reference_prices = f.get_reference_prices(ticker)

# Création de différents dataframes de prix selon l'intervalle temporel
interval = [2010, 2018]
df_prices_2010_2018 = f.get_prices_series(df_prices, interval)

df_prices_years = {}
for year in range(2018, 2022):
    if year == 2018:
        interval = [2010, year]
    else:   
        interval = [year, year]
    df_prices_years[f"df_prices_{year}"] = f.get_prices_series(df_prices, interval)

# Chargement des données en fonction de l'indice choisi
if indice == "High vol PER":
    # Calcul des rendements quotidiens des titres
    df_returns_years = {}
    for year in range(2018, 2021):
        df_returns_years[f"df_returns_{year}"] = f.calculate_daily_returns(df_prices_years[f"df_prices_{year}"])

    # Calcul de la volatilité annuelle des rendements des titres
    df_volatility_years = {}
    for year in range(2018, 2021):
        df_volatility_years[f"df_volatility_{year}"] = f.calculate_volatility(df_returns_years[f"df_returns_{year}"])

    # Sélection des 60% des titres les plus volatils
    df_high_vol_years = {}
    for year in range(2018, 2021):
        df_high_vol_years[f"df_high_vol_{year}"] = f.get_percentile(df_volatility_years[f"df_volatility_{year}"], 0.4)

    # Sélection des 30% des titres avec le PER le plus élevé
    indicator = "PE_RATIO"
    df_per_years = {}
    df_high_per_years = {}
    for year in range(2018, 2021):
        df_per_years[f"df_per_{year}"] = f.get_indicator_data_num(df_qualitative_years[f"df_qualitative_{year}"], indicator)
        df_high_per_years[f"df_high_per_{year}"] = f.get_percentile(df_per_years[f"df_per_{year}"], 0.7)

    # Sélection des titres communs aux deux sélections précédentes
    stocks_index_years = {}
    for year in range(2018, 2021):
        stocks_index_years[f"stocks_index_{year}"] = f.get_intersection(df_high_vol_years[f"df_high_vol_{year}"], df_high_per_years[f"df_high_per_{year}"])

    # Extraction de la capitalisation boursière des titres sélectionnés
    indicator = "CUR_MKT_CAP"
    df_capitalization_years = {}
    for year in range(2018, 2021):
        df_capitalization_years[f"df_capitalization_{year}"] = f.get_indicator_data_num(df_qualitative_years[f"df_qualitative_{year}"], indicator)
        df_capitalization_years[f"df_capitalization_{year}"] = f.reduce_series(df_capitalization_years[f"df_capitalization_{year}"], stocks_index_years[f"stocks_index_{year}"])

    # Calcul du poids des titres dans l'indice selon leur capitalisation boursière
    df_weights_years = {}
    for year in range(2018, 2021):
        df_weights_years[f"df_weights_{year}"] = f.calculate_weights(df_capitalization_years[f"df_capitalization_{year}"])

    # Suivi de la valeur de l'indice
    df_index_values_years = {}
    for year in range(2019, 2022):
        df_index_values_years[f"df_index_values_{year}"] = f.index_tracking(df_prices_years[f"df_prices_{year}"], df_weights_years[f"df_weights_{year-1}"])
        
        if year > 2019:
            df_index_values_years[f"df_index_values_{year}"] = f.continuity_index(df_index_values_years[f"df_index_values_{year}"], df_index_values_years[f"df_index_values_{year-1}"])

    # Concaténation et traitement final
    df_index_values = f.aggregate_series(*df_index_values_years.values())
    df_index_values = pd.DataFrame(df_index_values)
    df_index_values = pd.DataFrame(f.convert_prices(df_index_values[0], df_forex, currency).dropna())

    # Préparation et affichage du graphique
    df_complete_prices = f.get_common_elements(df_index_values, df_reference_prices)
    for column in df_complete_prices.columns:
        df_complete_prices[column] = df_complete_prices[column] / df_complete_prices[column].iloc[0] * 100
    df_complete_prices.columns = ["High vol PER Index", f"{stock_index}"]

     # Sauvegarde des données dans le session_state
    st.session_state['df_indice'] = df_complete_prices["High vol PER Index"]
    st.session_state['df_reference'] = df_complete_prices[stock_index]

    # Sauvegarde des données de poids dans le session_state
    st.session_state['df_weights'] = df_weights_years["df_weights_2020"]

    title = f"Évolution de l'indice High volatility & High PER entre 2019 et 2022 et du {stock_index}"
    fig = f.plot_series(df_complete_prices, title)
    st.plotly_chart(fig)

elif indice == "Momentum 6 months":
    # Extraction de séries de prix par période de 6 mois
    df_prices_months = {}
    for year in range(2018, 2022):  
        interval = [year, year]
        for i in range(2):
            df_prices_months[f"df_prices_{year}_{i}"] = f.get_prices_series_semi(df_prices, interval)[i]

    # Calcul des rendements
    df_returns_months = {}
    for year in range(2018, 2021):  
        for i in range(2):
            df_returns_months[f"df_returns_{year}_{i}"] = f.calculate_daily_returns(df_prices_months[f"df_prices_{year}_{i}"])

    # Pour chaque période, sélection des 100 titres les plus performants
    df_top_100_returns = {}
    for year in range(2018, 2021):
        for i in range(2):
            df_top_100_returns[f"df_top_100_returns_{year}_{i}"] = f.selection_top_100_returns(df_returns_months[f"df_returns_{year}_{i}"])

    # Extraction de la capitalisation boursière des titres sélectionnés
    indicator = "CUR_MKT_CAP"
    df_capitalization_months = {}
    for year in range(2018, 2021):
        for i in range(2):
            df_capitalization_months[f"df_capitalization_{year}_{i}"] = f.get_indicator_data_num(df_qualitative_years[f"df_qualitative_{year}"], indicator)
            df_capitalization_months[f"df_capitalization_{year}_{i}"] = f.reduce_series(df_capitalization_months[f"df_capitalization_{year}_{i}"], df_top_100_returns[f"df_top_100_returns_{year}_{i}"])

    # Calcul du poids des titres
    df_weights_months = {}
    for year in range(2018, 2021):
        for i in range(2):
            df_weights_months[f"df_weights_{year}_{i}"] = f.calculate_weights(df_capitalization_months[f"df_capitalization_{year}_{i}"])

    # Suivi de la valeur de l'indice
    df_index_values_months = {}
    for year in range(2019, 2022):
        for i in range(2):
            df_index_values_months[f"df_index_values_{year}_{i}"] = f.index_tracking(df_prices_months[f"df_prices_{year}_{i}"], df_weights_months[f"df_weights_{year-1}_{i}"])
            
            if year > 2019 or i > 0:
                if i == 1:
                    df_index_values_months[f"df_index_values_{year}_{i}"] = f.continuity_index(df_index_values_months[f"df_index_values_{year}_{i}"], df_index_values_months[f"df_index_values_{year}_{i-1}"])
                else:
                    df_index_values_months[f"df_index_values_{year}_{i}"] = f.continuity_index(df_index_values_months[f"df_index_values_{year}_{i}"], df_index_values_months[f"df_index_values_{year-1}_{i+1}"])

    # Concaténation et traitement final
    df_index_values = f.aggregate_series(*df_index_values_months.values())
    df_index_values = pd.DataFrame(df_index_values)
    df_index_values = pd.DataFrame(f.convert_prices(df_index_values[0], df_forex, currency).dropna())

    # Préparation et affichage du graphique
    df_complete_prices2 = f.get_common_elements(df_index_values, df_reference_prices)
    for column in df_complete_prices2.columns:
        df_complete_prices2[column] = df_complete_prices2[column] / df_complete_prices2[column].iloc[0] * 100
    df_complete_prices2.columns = ["Momentum 6 months", f"{stock_index}"]

    # Sauvegarde des données dans le session_state
    st.session_state['df_indice'] = df_complete_prices2["Momentum 6 months"]
    st.session_state['df_reference'] = df_complete_prices2[stock_index]

    # Sauvegarde des données de poids dans le session_state
    st.session_state['df_weights'] = df_weights_months["df_weights_2020_1"]

    title = f"Évolution de l'indice Momentum 6 months entre 2019 et 2022 et du {stock_index}"
    fig = f.plot_series(df_complete_prices2, title)
    st.plotly_chart(fig)

elif indice == "Géographique":
    # Vérifier si le pays est sélectionné
    if country is None:
        st.error('Veuillez sélectionner un pays dans la page de sélection.')
        st.stop()

    # Extraction des données du pays à étudier
    df_qualitative_countries_years = {}
    for year in range(2018, 2021):
        df_qualitative_countries_years[f"df_qualitative_countries_{year}"] = f.filter_qualitative_by_country(df_qualitative_years[f"df_qualitative_{year}"], country)

    # Extraction des prix des actions des titres du pays
    df_prices_countries_years = {}
    for year in range(2019, 2022):
        df_prices_countries_years[f"df_prices_countries_{year}"] = f.filter_prices_by_country(df_prices_years[f"df_prices_{year}"], df_qualitative_countries_years[f"df_qualitative_countries_{year-1}"])

    # Extraction de la capitalisation boursière
    indicator = "CUR_MKT_CAP"
    df_capitalization_countries_years = {}
    for year in range(2018, 2021):
        df_capitalization_countries_years[f"df_capitalization_countries_{year}"] = f.get_indicator_data_num(df_qualitative_countries_years[f"df_qualitative_countries_{year}"], indicator)

    # Calcul du poids des titres
    df_weights_countries_years = {}
    for year in range(2018, 2021):
        df_weights_countries_years[f"df_weights_countries_{year}"] = f.calculate_weights(df_capitalization_countries_years[f"df_capitalization_countries_{year}"])

    # Suivi de la valeur de l'indice
    df_index_values_countries_years = {}
    for year in range(2019, 2022):
        df_index_values_countries_years[f"df_index_values_countries_{year}"] = f.index_tracking(df_prices_countries_years[f"df_prices_countries_{year}"], df_weights_countries_years[f"df_weights_countries_{year-1}"])
        
        if year > 2019:
            df_index_values_countries_years[f"df_index_values_countries_{year}"] = f.continuity_index(df_index_values_countries_years[f"df_index_values_countries_{year}"], df_index_values_countries_years[f"df_index_values_countries_{year-1}"])

    # Concaténation et traitement final
    df_index_values = f.aggregate_series(*df_index_values_countries_years.values())
    df_index_values = pd.DataFrame(df_index_values)
    df_index_values = pd.DataFrame(f.convert_prices(df_index_values[0], df_forex, currency).dropna())

    # Préparation et affichage du graphique
    df_complete_prices_countries = f.get_common_elements(df_index_values, df_reference_prices)
    for column in df_complete_prices_countries.columns:
        df_complete_prices_countries[column] = df_complete_prices_countries[column] / df_complete_prices_countries[column].iloc[0] * 100
    df_complete_prices_countries.columns = [f"Indice {country}", stock_index]

    # Sauvegarde des données dans le session_state
    st.session_state['df_indice'] = df_complete_prices_countries[f"Indice {country}"]
    st.session_state['df_reference'] = df_complete_prices_countries[stock_index]

    # Sauvegarde des données de poids dans le session_state
    st.session_state['df_weights'] = df_weights_countries_years[f"df_weights_countries_2020"]

    title = f"Évolution de l'indice {country} entre 2019 et 2022"
    fig = f.plot_series(df_complete_prices_countries, title)
    st.plotly_chart(fig)