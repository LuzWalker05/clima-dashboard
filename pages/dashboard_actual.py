import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Dashboard Climático", layout="wide")

# Diccionario de meses en español
MESES_ESP = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Cargar y preparar datos
@st.cache_data
def load_data():
    df = pd.read_csv("clima.csv")
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['FECHA'])  # Elimina filas con fechas inválidas
    df['AÑO'] = df['FECHA'].dt.year
    df['MES'] = df['FECHA'].dt.month
    df = df[(df['MES'] >= 1) & (df['MES'] <= 12)]  # Filtra meses válidos
    return df

df = load_data()

# Sidebar con filtros
with st.sidebar:
    st.header("Filtros Avanzados")
    
    # Selección de localidad
    localidades = df['LOCALIDAD'].dropna().unique()
    localidad = st.selectbox("Selecciona localidad:", localidades)
    
    # Filtros por año (solo años disponibles para la localidad seleccionada)
    años_disponibles = sorted(df[df['LOCALIDAD'] == localidad]['AÑO'].unique())
    año_seleccionado = st.selectbox("Selecciona año:", años_disponibles)
    
    # Filtros por mes (solo meses disponibles para el año y localidad seleccionados)
    meses_disponibles = sorted(df[(df['LOCALIDAD'] == localidad) & 
                                (df['AÑO'] == año_seleccionado)]['MES'].unique())
    mes_seleccionado = st.selectbox("Selecciona mes:", 
                                   meses_disponibles,
                                   format_func=lambda x: MESES_ESP[x])

# Filtrar datos según selección
datos_filtrados = df[
    (df['LOCALIDAD'] == localidad) & 
    (df['AÑO'] == año_seleccionado) & 
    (df['MES'] == mes_seleccionado)
].sort_values('FECHA')

# Mostrar datos filtrados
st.subheader(f"Datos para {localidad} - {MESES_ESP[mes_seleccionado]} {año_seleccionado}")
with st.expander("Ver datos completos"):
    st.dataframe(datos_filtrados)

# Mostrar métricas resumidas
if not datos_filtrados.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperatura Máxima Promedio", f"{datos_filtrados['TMAX'].mean():.1f}°C")
    with col2:
        st.metric("Temperatura Mínima Promedio", f"{datos_filtrados['TMIN'].mean():.1f}°C")
    with col3:
        st.metric("Precipitación Total", f"{datos_filtrados['PRECIP'].sum():.1f} mm")

# Gráficos de series temporales
if not datos_filtrados.empty:
    st.subheader("Tendencias Climáticas")
    
    tab1, tab2 = st.tabs(["Temperaturas", "Precipitación"])
    
    with tab1:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(datos_filtrados['FECHA'], datos_filtrados['TMAX'], 'r-', label='Máxima')
        ax.plot(datos_filtrados['FECHA'], datos_filtrados['TMIN'], 'b-', label='Mínima')
        ax.fill_between(datos_filtrados['FECHA'], 
                       datos_filtrados['TMIN'], 
                       datos_filtrados['TMAX'],
                       color='gray', alpha=0.1)
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Temperatura (°C)")
        ax.legend()
        st.pyplot(fig)
    
    with tab2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(datos_filtrados['FECHA'], datos_filtrados['PRECIP'], label='Precipitación')
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Precipitación (mm)")
        ax.legend()
        st.pyplot(fig)
else:
    st.warning("No hay datos disponibles para los filtros seleccionados")

# Sección de predicciones mejorada
st.subheader("🔮 Predicciones Climáticas")

if st.button("Generar Predicción para el Próximo Mes", 
             help="Predice la temperatura máxima para el mes siguiente"):
    
    with st.spinner('Entrenando modelo y generando predicción...'):
        try:
            # Preparar datos históricos para el modelo
            datos_historicos = df[df['LOCALIDAD'] == localidad]
            
            if len(datos_historicos) < 12:  # Mínimo 1 año de datos
                raise ValueError("Se requieren al menos 12 meses de datos históricos")
            
            # Crear características adicionales
            datos_historicos['MES_SIN'] = datos_historicos['MES'].apply(
                lambda x: np.sin(2 * np.pi * x / 12))
            datos_historicos['MES_COS'] = datos_historicos['MES'].apply(
                lambda x: np.cos(2 * np.pi * x / 12))
            
            X = datos_historicos[['AÑO', 'MES_SIN', 'MES_COS']]
            y = datos_historicos['TMAX']
            
            # Entrenar modelo
            model = LinearRegression()
            model.fit(X, y)
            
            # Predecir para el próximo mes
            if mes_seleccionado == 12:
                proximo_mes = 1
                proximo_año = año_seleccionado + 1
            else:
                proximo_mes = mes_seleccionado + 1
                proximo_año = año_seleccionado
            
            proximo_mes_sin = np.sin(2 * np.pi * proximo_mes / 12)
            proximo_mes_cos = np.cos(2 * np.pi * proximo_mes / 12)
            
            prediccion = model.predict([[proximo_año, proximo_mes_sin, proximo_mes_cos]])
            
            # Mostrar resultados
            st.success(f"""
            **Predicción para {MESES_ESP[proximo_mes]} {proximo_año}:**
            - Temperatura máxima estimada: **{prediccion[0]:.1f}°C**
            - Precisión del modelo (R²): **{model.score(X, y):.2f}**
            """)
            
            # Gráfico de tendencia histórica
            st.info("Tendencia histórica de temperaturas máximas:")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.scatter(datos_historicos['FECHA'], datos_historicos['TMAX'], 
                      label='Datos históricos', alpha=0.6)
            
            # Predecir para visualizar la tendencia
            fechas_pred = pd.date_range(
                start=datos_historicos['FECHA'].min(),
                end=f"{proximo_año}-{proximo_mes:02d}-28",
                freq='M'
            )
            pred_df = pd.DataFrame({
                'FECHA': fechas_pred,
                'AÑO': fechas_pred.year,
                'MES': fechas_pred.month
            })
            pred_df['MES_SIN'] = pred_df['MES'].apply(lambda x: np.sin(2 * np.pi * x / 12))
            pred_df['MES_COS'] = pred_df['MES'].apply(lambda x: np.cos(2 * np.pi * x / 12))
            pred_df['PREDICCION'] = model.predict(pred_df[['AÑO', 'MES_SIN', 'MES_COS']])
            
            ax.plot(pred_df['FECHA'], pred_df['PREDICCION'], 'r-', label='Tendencia predicha')
            ax.axvline(x=datetime.now(), color='gray', linestyle='--', label='Hoy')
            ax.set_title(f"Tendencia de temperaturas en {localidad}")
            ax.set_ylabel("Temperatura máxima (°C)")
            ax.legend()
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error al generar predicción: {str(e)}")
            st.info("Asegúrate de tener suficientes datos históricos para la localidad seleccionada")

# Botón para volver
if st.button("🔙 Volver al Inicio"):
    st.session_state.page = "main"
    st.experimental_rerun()
