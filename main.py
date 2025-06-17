import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64

# Configuración de página
st.set_page_config(
    page_title="Clima por Localidad",
    layout="wide",
    page_icon="🌤️"
)

# Estilo CSS optimizado para visualización perfecta
st.markdown("""
    <style>
        :root {
            --primary-color: #1e3a8a;
            --secondary-color: #2563eb;
            --text-color: #374151;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
        }
        
        body {
            background-color: var(--bg-color);
            font-family: 'Inter', sans-serif;
        }
        
        /* Tarjeta con dimensiones fijas y scroll interno */
        .perfect-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 0;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
            height: 480px; /* Altura fija */
            width: 360px;  /* Ancho fijo */
            display: flex;
            flex-direction: column;
            margin: 0 auto;
            transition: all 0.3s ease;
        }
        
        .perfect-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        /* Contenedor de imagen con altura fija */
        .perfect-image-container {
            width: 100%;
            height: 200px; /* Altura aumentada para imágenes */
            overflow: hidden;
            position: relative;
            flex-shrink: 0; /* Evita que se reduzca */
        }
        
        .perfect-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }
        
        .perfect-card:hover .perfect-image {
            transform: scale(1.05);
        }
        
        /* Contenido con scroll si es necesario */
        .perfect-content {
            padding: 16px;
            flex-grow: 1;
            overflow-y: auto; /* Scroll vertical si el contenido es largo */
            height: calc(480px - 200px - 32px); /* Restamos altura de imagen y padding */
        }
        
        .perfect-title {
            color: var(--primary-color);
            font-size: 1.3rem;
            font-weight: 600;
            margin: 0 0 12px 0;
            text-align: center;
        }
        
        .perfect-description {
            color: var(--text-color);
            font-size: 0.95rem;
            line-height: 1.6;
            text-align: justify;
        }
        
        /* Icono por defecto */
        .perfect-default-icon {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
            color: #94a3b8;
        }
        
        /* Grid contenedor responsive */
        .perfect-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 24px;
            padding: 16px;
            width: 100%;
        }
        
        /* Cabecera */
        .perfect-header {
            text-align: center;
            margin-bottom: 32px;
            padding: 20px 0;
        }
        
        .perfect-main-title {
            font-size: 2.2rem;
            color: var(--primary-color);
            margin-bottom: 8px;
            font-weight: 700;
        }
        
        .perfect-subtitle {
            color: #64748b;
            font-size: 1.1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Función para convertir imagen a base64
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Icono por defecto SVG optimizado
DEFAULT_ICON = """
<svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="#94a3b8" stroke-width="2"/>
    <path d="M12 11C13.1046 11 14 10.1046 14 9C14 7.89543 13.1046 7 12 7C10.8954 7 10 7.89543 10 9C10 10.1046 10.8954 11 12 11Z" stroke="#94a3b8" stroke-width="2"/>
</svg>
"""

# Descripciones para cada localidad
DESCRIPCIONES = {
    "Amecameca de Juarez": "El clima en Amecameca, Estado de México, es templado subhúmedo con lluvias principalmente en verano y otoño. La temperatura máxima puede llegar a los 32°C y la mínima a -8°C, con una media anual de 14.1°C.",
    "Atlautla": "El clima en Atlautla, Estado de México, es generalmente subhúmedo con lluvias en verano. La temperatura promedio anual varía entre 2°C y 20°C. Se encuentra a una elevación de 2,355 metros sobre el nivel del mar.",
    "Juchitepec": "El clima en Juchitepec es templado subhúmedo, con temperaturas promedio anuales que oscilan entre 16 y 25 grados Celsius. Durante el verano, las temperaturas pueden alcanzar los 30 grados, mientras que en invierno pueden bajar a menos de 6 grados, con vientos fuertes.",
    "San Luis Ameca": "El clima en San Luis Ameca se caracteriza por ser semicálido semihúmedo. La temperatura media anual es de 20.7°C, con mínimas promedio de 8.5°C y máximas de 32.9°C. La precipitación media anual es de 924 mm.",
    "San Pedro Nexapa": "En San Pedro Nexapa, el clima es templado subhúmedo, con una temperatura media anual de alrededor de 14°C. La temperatura media máxima mensual puede alcanzar los 20°C, mientras que la mínima puede descender hasta los 10°C. La probabilidad de lluvia es alta, con un promedio de 25 días de lluvia al mes.",
    "San Rafael": "El clima en San Rafael, Estado de México, es generalmente templado subhúmedo con lluvias en verano. La temperatura media anual varía entre 22° y 30°C, y la precipitación total anual oscila entre 800 y 1200 mm.",
    "Tlalmanalco": "Tlalmanalco, Estado de México, tiene un clima templado subhúmedo con lluvias en verano. La temperatura promedio anual es de 15°C. La precipitación pluvial anual varía entre 800 y 1200 mm, con mayor intensidad de lluvias en julio y agosto."
}

@st.cache_data
def load_data():
    df = pd.read_csv("clima.csv")
    df['LOCALIDAD'] = df['LOCALIDAD'].str.strip()
    return df

# Interfaz principal
df = load_data()

st.markdown("""
    <div class="perfect-header">
        <h1 class="perfect-main-title">🌤️ Clima por Localidad</h1>
        <p class="perfect-subtitle">Descripciones detalladas del clima en cada región</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="perfect-grid">', unsafe_allow_html=True)

for loc in df['LOCALIDAD'].dropna().unique():
    try:
        # Manejo de imágenes
        image_path = f"images/{loc.lower().replace(' ', '_')}.jpeg"
        
        if os.path.exists(image_path):
            base64_img = image_to_base64(image_path)
            image_content = f'<img src="data:image/jpeg;base64,{base64_img}" class="perfect-image" alt="{loc}">'
        else:
            image_content = f'<div class="perfect-default-icon">{DEFAULT_ICON}</div>'
        
        # Obtener descripción
        descripcion = DESCRIPCIONES.get(loc, "Información climática no disponible.")
        
        # Construcción de la tarjeta
        html = f"""
        <div class="perfect-card">
            <div class="perfect-image-container">
                {image_content}
            </div>
            <div class="perfect-content">
                <h3 class="perfect-title">{loc}</h3>
                <p class="perfect-description">{descripcion}</p>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error mostrando {loc}: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

st.caption("© Dashboard Climático desarrollado por ❤️ por LuzWalker")
