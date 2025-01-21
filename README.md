This project aims to create three stock market indices based on the data of securities from the S&P500 and Eurostoxx600.

We have constructed the following indices:

- An index that combines high-volatility and high-PER securities.
- A Momentum index that groups the best-performing stocks from the last six months.
- A geographical index that allows for the selection of securities from a specific country.
- 
We create and visualize the evolution of the indices, along with their performance indicators and compositions.

All functions called are from the file "functions_project.py".

The code is dynamic and allows changes to the initial parameters:

- Investment universe (S&P500 or Eurostoxx600).
- Currency for presenting results (USD, EUR, GBP, JPY, or CNY).
- Country for the geographical index.
- 
The dynamic nature of the code is fully leveraged through the web app built with Streamlit, which can be used by running the "Home.py" file in the terminal: streamlit run Home.py.
