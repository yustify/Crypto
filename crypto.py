import streamlit as st
import requests
import pandas as pd
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cripto Tracker", page_icon="🪙", layout="wide")

# --- ESTILO CSS (Opcional) ---
st.markdown("""
<style>
    h1 {
        text-align: center;
        color: #f7931a; /* Naranja Bitcoin */
    }
    .stDataFrame {
        font-size: 1.1em;
    }
    /* Colorear el cambio de 24h */
    td[data-testid^="dataframe-cell-price_change_percentage_24h:"] > div {
        font-weight: bold;
    }
    td[data-testid^="dataframe-cell-price_change_percentage_24h:"][data-testid$="positive"] > div {
        color: #4CAF50; /* Verde */
    }
    td[data-testid^="dataframe-cell-price_change_percentage_24h:"][data-testid$="negative"] > div {
        color: #F44336; /* Rojo */
    }
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.title("🪙 Rastreador Cripto Top 10")
st.write("Precios y datos de las 10 criptomonedas con mayor capitalización de mercado (actualizado cada 5 minutos).")

# --- FUNCIÓN PARA OBTENER DATOS DE COINGECKO ---
@st.cache_data(ttl=300) # Guarda los datos en caché por 300 segundos (5 minutos)
def obtener_datos_cripto():
    """Obtiene los datos de las top 10 criptos desde la API de CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    parametros = {
        'vs_currency': 'eur', # Moneda de comparación (puedes cambiar a 'usd')
        'order': 'market_cap_desc', # Ordenar por capitalización de mercado
        'per_page': 10, # Número de resultados
        'page': 1,
        'sparkline': 'false', # No necesitamos minigráficos
        'locale': 'es' # Nombres en español
    }
    try:
        respuesta = requests.get(url, params=parametros, timeout=10)
        respuesta.raise_for_status() # Lanza un error si la petición falla
        datos = respuesta.json()
        return datos
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API de CoinGecko: {e}")
        return None

# --- OBTENER Y PROCESAR DATOS ---
datos_api = obtener_datos_cripto()

if datos_api:
    # Crear un DataFrame de Pandas con los datos relevantes
    df = pd.DataFrame(datos_api)
    df = df[[
        'market_cap_rank',
        'image',
        'name',
        'symbol',
        'current_price',
        'price_change_percentage_24h',
        'market_cap',
        'total_volume'
    ]]

    # Renombrar columnas para claridad
    df.columns = [
        'Rank',
        'Logo',
        'Nombre',
        'Símbolo',
        'Precio (€)',
        '% Cambio 24h',
        'Capitalización (€)',
        'Volumen 24h (€)'
    ]

    # Formatear columnas numéricas y añadir color al % Cambio
    df['Símbolo'] = df['Símbolo'].str.upper()
    df['% Cambio 24h'] = df['% Cambio 24h'].map('{:,.2f}%'.format)

    # --- MOSTRAR LA TABLA ---
    st.dataframe(
        df,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo", width="small"),
            "Precio (€)": st.column_config.NumberColumn(format="€ %.2f"),
            "Capitalización (€)": st.column_config.NumberColumn(format="€ %d"),
            "Volumen 24h (€)": st.column_config.NumberColumn(format="€ %d"),
        },
        hide_index=True,
        use_container_width=True # Ajusta la tabla al ancho de la página
    )

    st.caption(f"Datos obtenidos de CoinGecko a las {time.strftime('%H:%M:%S')}. Se actualizan cada 5 minutos.")

else:
    st.warning("No se pudieron cargar los datos. Inténtalo de nuevo más tarde.")

