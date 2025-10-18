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
st.title("🪙 Rastreador Cripto Top 10 + ADA")
st.write("Precios y datos de las criptomonedas con mayor capitalización de mercado, asegurando que Cardano (ADA) esté siempre incluida (actualizado cada 5 minutos).")

# --- FUNCIÓN PARA OBTENER DATOS DE COINGECKO ---
@st.cache_data(ttl=300) # Guarda los datos en caché por 300 segundos (5 minutos)
def obtener_datos_cripto():
    """Obtiene los datos de las top 10 criptos + Cardano desde la API de CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    
    # --- CAMBIO PRINCIPAL: Pedimos el Top 10 Y específicamente Cardano ---
    # 1. Obtener los IDs del Top 10 actual
    try:
        top_10_ids_response = requests.get(url, params={'vs_currency': 'eur', 'order': 'market_cap_desc', 'per_page': 10, 'page': 1}, timeout=10)
        top_10_ids_response.raise_for_status()
        top_10_ids = [coin['id'] for coin in top_10_ids_response.json()]
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener Top 10 IDs de CoinGecko: {e}")
        return None

    # 2. Asegurarse de que 'cardano' está en la lista de IDs a pedir
    ids_a_pedir = set(top_10_ids) # Usamos un set para evitar duplicados si ADA ya está en el top 10
    ids_a_pedir.add('cardano')
    ids_string = ','.join(list(ids_a_pedir)) # Convertir a string separado por comas para la API

    # 3. Pedir los datos de mercado para esa lista combinada de IDs
    parametros = {
        'vs_currency': 'eur',
        'ids': ids_string, # Pedimos por IDs específicos
        'order': 'market_cap_desc', # Aún así, ordenamos el resultado por capitalización
        'sparkline': 'false',
        'locale': 'es'
    }
    try:
        respuesta = requests.get(url, params=parametros, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return datos
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API de CoinGecko para datos de mercado: {e}")
        return None

# --- OBTENER Y PROCESAR DATOS ---
datos_api = obtener_datos_cripto()

if datos_api:
    # Crear un DataFrame de Pandas con los datos relevantes
    df = pd.DataFrame(datos_api)
    # Asegurarnos de que tenemos las columnas esperadas, incluso si la API falla parcialmente
    columnas_esperadas = ['market_cap_rank', 'image', 'name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap', 'total_volume']
    for col in columnas_esperadas:
        if col not in df.columns:
            df[col] = None # Añadir columna vacía si falta

    df = df[columnas_esperadas] # Reordenar y seleccionar columnas

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
    # Usamos apply con lambda para manejar posibles valores None antes de formatear
    df['% Cambio 24h'] = df['% Cambio 24h'].apply(lambda x: '{:,.2f}%'.format(x) if x is not None else 'N/A')

    # --- MOSTRAR LA TABLA ---
    st.dataframe(
        df,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo", width="small"),
            "Precio (€)": st.column_config.NumberColumn(format="€ %.2f"),
            "Capitalización (€)": st.column_config.NumberColumn(format="€ %d"),
            "Volumen 24h (€)": st.column_config.NumberColumn(format="€ %d"),
            # Añadimos configuración para el Rank por si acaso es None
            "Rank": st.column_config.NumberColumn(format="%d")
        },
        hide_index=True,
        use_container_width=True
    )

    st.caption(f"Datos obtenidos de CoinGecko a las {time.strftime('%H:%M:%S')}. Se actualizan cada 5 minutos.")

else:
    st.warning("No se pudieron cargar los datos. Inténtalo de nuevo más tarde.")

