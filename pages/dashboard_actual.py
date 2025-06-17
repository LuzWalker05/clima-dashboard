import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk

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
    </style>
""", unsafe_allow_html=True)

st.title("📈 Dashboard Climático Detallado")

# Cargar y preparar datos
df = pd.read_csv("clima.csv")
df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce')
for col in ['PRECIP', 'TMAX', 'TMIN']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

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
data_localidad = df[df['LOCALIDAD'] == localidad]

# Métricas por localidad
st.subheader(f"📍 Datos para {localidad}")
col5, col6, col7, col8 = st.columns(4)
col5.metric("🌧️ Precipitación Prom", f"{data_localidad['PRECIP'].mean():.2f} mm")
col6.metric("🌡️ T. Máxima Prom", f"{data_localidad['TMAX'].mean():.2f} °C")
col7.metric("🌡️ T. Mínima Prom", f"{data_localidad['TMIN'].mean():.2f} °C")
col8.metric("🗃️ Registros", len(data_localidad))

# Mapa de la localidad seleccionada
if 'LATITUD' in df.columns and 'LONGITUD' in df.columns:
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

# Gráficos
st.markdown("---")
st.subheader("📊 Evolución de Temperaturas")

data_localidad = data_localidad.sort_values(by='FECHA')

fig, ax = plt.subplots(figsize=(12,6))
ax.plot(data_localidad['FECHA'], data_localidad['TMAX'], label='TMAX', color='crimson')
ax.plot(data_localidad['FECHA'], data_localidad['TMIN'], label='TMIN', color='dodgerblue')
ax.set_ylabel("Temperatura (°C)")
ax.set_xlabel("Fecha")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("🌧️ Evolución de Precipitación")
fig2, ax2 = plt.subplots(figsize=(12,4))
ax2.plot(data_localidad['FECHA'], data_localidad['PRECIP'], label='PRECIP', color='seagreen')
ax2.set_ylabel("Precipitación (mm)")
ax2.set_xlabel("Fecha")
ax2.legend()
plt.xticks(rotation=45)
st.pyplot(fig2)

st.markdown("---")

# Botón para volver
if st.button("🔙 Volver al Inicio"):
    st.switch_page("main.py")

st.caption("© Dashboard Climático desarrollado con ❤️ por LuzWalker")
