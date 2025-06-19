import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="🌤️Dashboard Climático🌤️", layout="wide")

# Estilo moderno
st.markdown("""
    <style>
        body {
            background-color: #f8f9fa;
        }
        .metric-label {
            font-weight: bold;
            color: #333;
        }
        .volver-btn {
            background-color: #333;
            color: white;
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
        }
        .map-container {
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .filter-container {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Dashboard Climático Detallado")

# Cargar y preparar datos
@st.cache_data
def load_data():
    df = pd.read_csv("clima.csv")
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce')
    for col in ['PRECIP', 'TMAX', 'TMIN']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Extraer año y mes para filtros
    df['AÑO'] = df['FECHA'].dt.year
    df['MES'] = df['FECHA'].dt.month
    df['DIA'] = df['FECHA'].dt.day
    return df

df = load_data()

# Resumen general
st.subheader("📋 Resumen General")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Localidades", df['LOCALIDAD'].nunique())
col2.metric("Total Registros", len(df))
col3.metric("Temp. Máx Prom", f"{df['TMAX'].mean():.2f} °C")
col4.metric("Precip. Prom", f"{df['PRECIP'].mean():.2f} mm")
st.markdown("---")

# Selección de localidad
localidades = df['LOCALIDAD'].dropna().unique()
params = st.experimental_get_query_params() if hasattr(st, 'experimental_get_query_params') else {}
localidad_param = params.get("localidad", [None])[0]
if localidad_param and localidad_param[0] in localidades:
    localidad_default = localidad_param[0]
else:
    localidad_default = localidades[0]

localidad = st.selectbox("Selecciona una localidad:", localidades, index=list(localidades).index(localidad_default))
data_localidad = df[df['LOCALIDAD'] == localidad].copy()

# Filtros por fecha
st.subheader("🔍 Filtros de Fecha")
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    
    # Opciones de filtrado
    filtro_opcion = st.radio("Seleccione el tipo de filtro:", 
                            ["Todo el histórico", "Por año", "Por mes y año", "Rango de fechas"],
                            horizontal=True)
    
    data_filtrada = data_localidad.copy()
    
    if filtro_opcion == "Por año":
        años_disponibles = sorted(data_localidad['AÑO'].unique(), reverse=True)
        año_seleccionado = st.selectbox("Seleccione el año:", años_disponibles)
        data_filtrada = data_localidad[data_localidad['AÑO'] == año_seleccionado]
        
    elif filtro_opcion == "Por mes y año":
        col1, col2 = st.columns(2)
        with col1:
            años_disponibles = sorted(data_localidad['AÑO'].unique(), reverse=True)
            año_seleccionado = st.selectbox("Año:", años_disponibles)
        with col2:
            mes_seleccionado = st.selectbox("Mes:", range(1,13), format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
        data_filtrada = data_localidad[(data_localidad['AÑO'] == año_seleccionado) & 
                                      (data_localidad['MES'] == mes_seleccionado)]
        
    elif filtro_opcion == "Rango de fechas":
        fecha_min = data_localidad['FECHA'].min().to_pydatetime()
        fecha_max = data_localidad['FECHA'].max().to_pydatetime()
        rango_fechas = st.date_input("Seleccione rango de fechas:", 
                                    [fecha_min, fecha_max],
                                    min_value=fecha_min,
                                    max_value=fecha_max)
        if len(rango_fechas) == 2:
            data_filtrada = data_localidad[
                (data_localidad['FECHA'] >= pd.to_datetime(rango_fechas[0])) & 
                (data_localidad['FECHA'] <= pd.to_datetime(rango_fechas[1]))
    
    st.markdown('</div>', unsafe_allow_html=True)

# Métricas por localidad (filtradas)
st.subheader(f"📍 Datos para {localidad} - {filtro_opcion}")
col5, col6, col7, col8 = st.columns(4)
col5.metric("🌧️ Precipitación Prom", f"{data_filtrada['PRECIP'].mean():.2f} mm" if not data_filtrada.empty else "N/A")
col6.metric("🌡️ T. Máxima Prom", f"{data_filtrada['TMAX'].mean():.2f} °C" if not data_filtrada.empty else "N/A")
col7.metric("🌡️ T. Mínima Prom", f"{data_filtrada['TMIN'].mean():.2f} °C" if not data_filtrada.empty else "N/A")
col8.metric("🗃️ Registros", len(data_filtrada))

# Mapa de la localidad seleccionada
if 'LATITUD' in df.columns and 'LONGITUD' in df.columns and not data_filtrada.empty:
    st.subheader(f"🗺️ Mapa de {localidad}")
    localidad_data = df[df['LOCALIDAD'] == localidad].iloc[0]
    
    with st.container():
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=localidad_data['LATITUD'],
                longitude=localidad_data['LONGITUD'],
                zoom=10,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=pd.DataFrame([{
                        'LATITUD': localidad_data['LATITUD'],
                        'LONGITUD': localidad_data['LONGITUD'],
                        'LOCALIDAD': localidad
                    }]),
                    get_position='[LONGITUD, LATITUD]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=500,
                    pickable=True
                ),
            ],
            tooltip={"text": "{LOCALIDAD}"}
        ))

# Gráficos con datos filtrados
if not data_filtrada.empty:
    st.markdown("---")
    st.subheader("📊 Evolución de Temperaturas")
    
    data_filtrada = data_filtrada.sort_values(by='FECHA')
    
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(data_filtrada['FECHA'], data_filtrada['TMAX'], label='TMAX', color='crimson')
    ax.plot(data_filtrada['FECHA'], data_filtrada['TMIN'], label='TMIN', color='dodgerblue')
    ax.set_ylabel("Temperatura (°C)")
    ax.set_xlabel("Fecha")
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    st.subheader("🌧️ Evolución de Precipitación")
    fig2, ax2 = plt.subplots(figsize=(12,4))
    ax2.plot(data_filtrada['FECHA'], data_filtrada['PRECIP'], label='PRECIP', color='seagreen')
    ax2.set_ylabel("Precipitación (mm)")
    ax2.set_xlabel("Fecha")
    ax2.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig2)
    
    # Predicciones con regresión lineal
    st.markdown("---")
    st.subheader("🔮 Predicciones Climáticas")
    
    if len(data_filtrada) > 10:  # Necesitamos suficientes datos para hacer predicciones
        # Preparar datos para el modelo
        data_filtrada['DIAS'] = (data_filtrada['FECHA'] - data_filtrada['FECHA'].min()).dt.days
        
        # Modelo para TMAX
        model_tmax = LinearRegression()
        X = data_filtrada[['DIAS']]
        y_tmax = data_filtrada['TMAX'].values
        model_tmax.fit(X, y_tmax)
        
        # Modelo para TMIN
        model_tmin = LinearRegression()
        y_tmin = data_filtrada['TMIN'].values
        model_tmin.fit(X, y_tmin)
        
        # Modelo para PRECIP (usamos PolynomialFeatures para mejor ajuste)
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.pipeline import make_pipeline
        
        model_precip = make_pipeline(
            PolynomialFeatures(degree=2),
            LinearRegression()
        )
        y_precip = data_filtrada['PRECIP'].values
        model_precip.fit(X, y_precip)
        
        # Predicciones futuras (30 días adelante)
        ultima_fecha = data_filtrada['FECHA'].max()
        dias_prediccion = 30
        fechas_futuras = pd.date_range(ultima_fecha, periods=dias_prediccion+1)
        dias_futuros = (fechas_futuras - data_filtrada['FECHA'].min()).days.values.reshape(-1, 1)
        
        pred_tmax = model_tmax.predict(dias_futuros)
        pred_tmin = model_tmin.predict(dias_futuros)
        pred_precip = model_precip.predict(dias_futuros)
        
        # Gráfico de predicciones
        fig_pred, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Temperaturas
        ax1.plot(data_filtrada['FECHA'], data_filtrada['TMAX'], label='TMAX Histórico', color='crimson')
        ax1.plot(data_filtrada['FECHA'], data_filtrada['TMIN'], label='TMIN Histórico', color='dodgerblue')
        ax1.plot(fechas_futuras, pred_tmax, '--', label='Predicción TMAX', color='darkred')
        ax1.plot(fechas_futuras, pred_tmin, '--', label='Predicción TMIN', color='darkblue')
        ax1.set_ylabel("Temperatura (°C)")
        ax1.set_title("Predicción de Temperaturas para los próximos 30 días")
        ax1.legend()
        
        # Precipitación
        ax2.plot(data_filtrada['FECHA'], data_filtrada['PRECIP'], label='PRECIP Histórico', color='seagreen')
        ax2.plot(fechas_futuras, pred_precip, '--', label='Predicción PRECIP', color='darkgreen')
        ax2.set_ylabel("Precipitación (mm)")
        ax2.set_title("Predicción de Precipitación para los próximos 30 días")
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig_pred)
        
        # Mostrar valores predichos
        st.write("**Valores predichos para los próximos días:**")
        
        # Crear DataFrame con las predicciones
        pred_df = pd.DataFrame({
            'Fecha': fechas_futuras,
            'TMAX Predicha': pred_tmax,
            'TMIN Predicha': pred_tmin,
            'PRECIP Predicha': pred_precip
        })
        
        # Mostrar tabla con las predicciones
        st.dataframe(pred_df.set_index('Fecha').style.format("{:.1f}"), height=300)
        
        # Explicación del modelo
        st.markdown("""
        **Nota sobre las predicciones:**
        - Las predicciones se realizan usando un modelo de regresión lineal para las temperaturas.
        - Para la precipitación se usa una regresión polinomial de grado 2 para capturar mejor los patrones.
        - Estas predicciones son aproximadas y deben tomarse como referencia general.
        """)
    else:
        st.warning("Se necesitan al menos 10 registros para generar predicciones. Ajuste los filtros para incluir más datos.")
else:
    st.warning("No hay datos disponibles con los filtros seleccionados.")

st.markdown("---")

if st.button("🔙 Volver al Inicio"):
    st.session_state.page = "main"  
    st.experimental_rerun()  

st.caption("© Dashboard Climático desarrollado por ❤️ por LuzWalker")
