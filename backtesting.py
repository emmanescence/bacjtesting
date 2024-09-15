import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

def download_data(ticker, start_date, end_date):
    """Descargar datos históricos de un ticker."""
    return yf.download(ticker, start=start_date, end=end_date)

def plot_sma_crossover(data):
    """Graficar la estrategia de cruce de medias móviles simples (SMA)."""
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    data['Signal'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)
    data['Signal'] = np.where(data['SMA_50'] < data['SMA_200'], -1, data['Signal'])
    
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)
    plt.plot(data['SMA_50'], label='SMA 50', color='green', alpha=0.75)
    plt.plot(data['SMA_200'], label='SMA 200', color='red', alpha=0.75)
    
    plt.title('SMA Crossover Strategy')
    plt.legend()
    st.pyplot(plt)

def plot_breakout(data):
    """Graficar la estrategia de breakout de máximos/mínimos."""
    lookback_period = 20
    data['Max_20'] = data['Close'].rolling(window=lookback_period).max()
    data['Min_20'] = data['Close'].rolling(window=lookback_period).min()
    
    data['Signal'] = 0
    data['Signal'] = np.where(data['Close'] > data['Max_20'].shift(1), 1, data['Signal'])
    data['Signal'] = np.where(data['Close'] < data['Min_20'].shift(1), -1, data['Signal'])
    
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)
    plt.plot(data['Max_20'], label='Max 20 Days', color='green', linestyle='--', alpha=0.5)
    plt.plot(data['Min_20'], label='Min 20 Days', color='red', linestyle='--', alpha=0.5)
    
    plt.plot(data[data['Signal'] == 1].index, data['Close'][data['Signal'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')
    plt.plot(data[data['Signal'] == -1].index, data['Close'][data['Signal'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
    
    plt.title('Breakout Strategy')
    plt.legend()
    st.pyplot(plt)

def plot_ema_crossover(data):
    """Graficar la estrategia de cruce de medias móviles exponenciales (EMA)."""
    data['EMA_10'] = data['Close'].ewm(span=10, adjust=False).mean()
    data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
    
    data['Signal'] = 0
    data['Signal'] = np.where(data['EMA_10'] > data['EMA_50'], 1, 0)
    data['Signal'] = np.where(data['EMA_10'] < data['EMA_50'], -1, data['Signal'])
    
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)
    plt.plot(data['EMA_10'], label='EMA 10', color='green', alpha=0.5)
    plt.plot(data['EMA_50'], label='EMA 50', color='red', alpha=0.5)
    
    plt.plot(data[data['Signal'] == 1].index, data['EMA_10'][data['Signal'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')
    plt.plot(data[data['Signal'] == -1].index, data['EMA_10'][data['Signal'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
    
    plt.title('EMA Crossover Strategy')
    plt.legend()
    st.pyplot(plt)

def plot_bollinger_bands(data):
    """Graficar la estrategia de Bandas de Bollinger."""
    def calculate_bollinger_bands(data, window=20, num_std_dev=2):
        rolling_mean = data['Close'].rolling(window=window).mean()
        rolling_std = data['Close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std_dev)
        lower_band = rolling_mean - (rolling_std * num_std_dev)
        return rolling_mean, upper_band, lower_band
    
    data['SMA_20'], data['Upper_Band'], data['Lower_Band'] = calculate_bollinger_bands(data)
    
    data['Signal'] = 0
    data['Signal'] = np.where((data['Close'] < data['Lower_Band'].shift(1)) & (data['Close'] > data['Lower_Band']), 1, data['Signal'])
    data['Signal'] = np.where((data['Close'] > data['Upper_Band'].shift(1)) & (data['Close'] < data['Upper_Band']), -1, data['Signal'])
    
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)
    plt.plot(data['SMA_20'], label='SMA 20', color='orange', alpha=0.5)
    plt.plot(data['Upper_Band'], label='Upper Band', color='green', linestyle='--', alpha=0.5)
    plt.plot(data['Lower_Band'], label='Lower Band', color='red', linestyle='--', alpha=0.5)
    
    plt.plot(data[data['Signal'] == 1].index, data['Close'][data['Signal'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')
    plt.plot(data[data['Signal'] == -1].index, data['Close'][data['Signal'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
    
    plt.title('Bollinger Bands Strategy')
    plt.legend()
    st.pyplot(plt)

def main():
    st.title('Backtesting de Estrategias de Trading')

    # Selección del ticker
    ticker = st.text_input('Ingrese el ticker de la acción', 'AAPL')
    
    # Rango de fechas
    start_date = st.date_input('Fecha de inicio', pd.to_datetime('2010-01-01'))
    end_date = st.date_input('Fecha de fin', pd.to_datetime('2023-12-31'))

    # Selección de la estrategia
    strategy = st.selectbox('Selecciona una estrategia', ['SMA Crossover', 'Breakout', 'EMA Crossover', 'Bandas de Bollinger'])

    if st.button('Ejecutar'):
        # Descargar datos
        data = download_data(ticker, start_date, end_date)

        # Mostrar datos
        st.write(data.head())

        # Graficar según la estrategia seleccionada
        if strategy == 'SMA Crossover':
            plot_sma_crossover(data)
        elif strategy == 'Breakout':
            plot_breakout(data)
        elif strategy == 'EMA Crossover':
            plot_ema_crossover(data)
        elif strategy == 'Bandas de Bollinger':
            plot_bollinger_bands(data)

if __name__ == "__main__":
    main()
