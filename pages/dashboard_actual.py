import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Dashboard Climático", layout="wide")

# Cargar y preparar datos
@st.cache_data
def load_data():
    df = pd.read_csv("clima.csv")
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce')
    df['AÑO'] = df['FECHA'].dt.year
    df['MES'] = df['FECHA'].dt.month
    for col in ['PRECIP', 'TMAX', 'TMIN']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()

# Sidebar con filtros
with st.sidebar:
    st.header("Filtros")
    
    # Selección de localidad
    localidades = df['LOCALIDAD'].dropna().unique()
    localidad = st.selectbox("Selecciona localidad:", localidades)
    
    # Filtros por año y mes
    años = sorted(df['AÑO'].unique())
    año_seleccionado = st.selectbox("Selecciona año:", años)
    
    meses = sorted(df['MES'].unique())
    mes_seleccionado = st.selectbox("Selecciona mes:", meses, format_func=lambda x: datetime(1900, x, 1).strftime('%B'))

# Filtrar datos
datos_filtrados = df[
    (df['LOCALIDAD'] == localidad) & 
    (df['AÑO'] == año_seleccionado) & 
    (df['MES'] == mes_seleccionado)
]

# Mostrar datos filtrados
st.subheader(f"Datos para {localidad} - {mes_seleccionado}/{año_seleccionado}")
st.dataframe(datos_filtrados)

# Gráficos
st.subheader("Temperaturas")
fig, ax = plt.subplots()
ax.plot(datos_filtrados['FECHA'], datos_filtrados['TMAX'], label='Máxima')
ax.plot(datos_filtrados['FECHA'], datos_filtrados['TMIN'], label='Mínima')
ax.set_xlabel("Fecha")
ax.set_ylabel("Temperatura (°C)")
ax.legend()
st.pyplot(fig)

# Sección de predicciones
st.subheader("Predicciones")
if st.button("Generar Predicción para el Próximo Mes"):
    try:
        # Preparar datos para el modelo
        datos_historicos = df[df['LOCALIDAD'] == localidad]
        X = datos_historicos[['AÑO', 'MES']]
        y = datos_historicos['TMAX']
        
        # Entrenar modelo
        model = LinearRegression()
        model.fit(X, y)
        
        # Predecir
        if mes_seleccionado == 12:
            proximo_mes = 1
            proximo_año = año_seleccionado + 1
        else:
            proximo_mes = mes_seleccionado + 1
            proximo_año = año_seleccionado
            
        prediccion = model.predict([[proximo_año, proximo_mes]])
        
        st.success(f"Predicción de temperatura máxima para {proximo_mes}/{proximo_año}: {prediccion[0]:.1f}°C")
        
    except Exception as e:
        st.error(f"Error al generar predicción: {str(e)}")

# Botón para volver
if st.button("🔙 Volver al Inicio"):
    st.session_state.page = "main"
    st.experimental_rerun()
