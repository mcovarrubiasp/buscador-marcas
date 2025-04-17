import streamlit as st
import pandas as pd
import requests
import re

# Configuración de la página
st.set_page_config(page_title="Buscador de Productos", layout="wide")

# API Key de SerpAPI
API_KEY = "c564bcfd30dc7e38f22ab9ac05511b434b5cb9b523d4203c3d56568f3301a6bf"

# Diccionario de marcas conocidas
marcas_conocidas = [
    "Foset", "Rotoplas", "Coflex", "IUSA", "Helvex", "Urrea", "Oatey", "Weld-On", "Truper", "Contact",
    "Siler", "FXN", "Ezweld", "Christy's", "Presto", "Rain-R-Shine", "Surtek", "Rali", "MINIPIT",
    "Silverplastic", "Wetweld", "Foset","omega","Omega","Conduit", "Rotoplas", "Coflex", "RUGO", "IUSA", "Amanco Wavin", "Cinsa", "Calorex", "Helvex", "Urrea",
    "Oatey", "Tubo Plus", "Dica", "Optimus", "Hesa", "Tatsa", "Eureka", "Conducto", "Ledes", "Atkore", "ABB",
    "Kohler", "Moen", "Delta Faucet", "Grohe", "American Standard", "TOTO", "Geberit", "Hansgrohe", "Roca",
    "Brizo", "Pfister", "Jacuzzi", "Sloan", "Gerber", "CRH", "Saint-Gobain", "Lowe’s", "Zurn", "Elkay",
    "Centrica", "UFP Industries", "Georg Fischer", "Uponor", "REHAU", "Viega", "NIBCO", "IPEX", "Charlotte Pipe",
    "Astral Pipes", "Wavin", "Pipelife", "JM Eagle", "Aliaxis", "Philmac", "Aquatherm", "GF Hakan", "Plasson",
    "Apex Piping Systems", "Polypipe", "Thermoplastics Ltd.", "Durapipe", "Mueller Industries", "BrassCraft",
    "Legend Valve", "SharkBite", "Watts", "Sioux Chief", "RWC", "Jaquar", "Franke", "VitrA", "Ideal Standard",
    "Duravit", "LIXIL", "CEMEX", "LafargeHolcim", "Heidelberg Materials", "UltraTech Cement", "Buzzi Unicem",
    "Boral", "Votorantim Cimentos", "Argos", "JK Cement", "Dangote Cement", "Asia Cement", "Anhui Conch",
    "Taiheiyo Cement", "Wienerberger", "Acme Brick", "General Shale", "Glen-Gery", "Grupo Lamosa", "Heluz",
    "Brickworks", "Xella", "CSR", "ArcelorMittal", "Nucor", "Tata Steel", "POSCO", "Baosteel", "JSW Steel",
    "Thyssenkrupp", "Gerdau", "Salzgitter", "EVRAZ", "Outokumpu", "NLMK", "SSAB", "BlueScope", "AGC Glass",
    "Guardian Glass", "NSG Pilkington", "Vitro", "Xinyi Glass", "Cardinal Glass", "Şişecam", "VELUX",
    "Andersen Windows", "Pella", "JELD-WEN", "Milgard", "Atrium", "Marvin", "Simonton", "Aluplast",
    "Kommerling", "Schuco", "Technal", "Reynaers", "Schneider Electric", "Legrand", "Siemens", "Eaton",
    "Hager", "GE Industrial", "Mitsubishi Electric", "Panasonic", "Honeywell", "Lutron", "Hubbell",
    "Rockwell Automation", "Sika", "Mapei", "BASF Construction Chemicals", "Henkel", "3M", "Bostik",
    "Dow Building Solutions", "Grace Construction", "W.R. Meadows", "Tremco", "Soudal", "Ardex", "Carlisle",
    "GAF", "Firestone Building Products", "IKO", "Owens Corning", "Johns Manville", "Knauf", "CertainTeed",
    "Kingspan", "USG", "Lafarge", "National Gypsum", "Georgia-Pacific", "Armstrong", "Contact", "Siler",
    "FXN", "Ezweld", "Christy's", "Presto", "Rain-R-Shine", "Surtek", "Truper", "Rali", "MINIPIT",
    "Silverplastic", "Wetweld", "Weld-On","Fluidmaster"
]

# Diccionario de categorías de uso
categorias_de_uso = {
    "lavabo": ["lavabo", "baño", "lavamanos", "lavamaní", "fregadero"],
    "boiler": ["boiler", "calentador", "caldera", "termotanque"],
    "refrigerador": ["refrigerador", "frigorífico", "nevera", "heladera"],
    "sanitario": ["sanitario", "inodoro", "wc", "taza", "retrete", "excusado", "cisterna"],
    "ducha": ["ducha", "regadera", "shower", "cabezal de ducha", "maneral"],
    "cocina": ["cocina", "tarja", "fregadero", "grifería de cocina", "mezcladora cocina"],
    "mingitorio": ["mingitorio", "urinal"],
    "instalación": ["instalación", "tubería", "conexión", "acople", "válvula", "unión", "plomería", "ensamble"],
    "construcción": ["obra", "construcción", "materiales", "prefabricado", "cemento", "pegamento", "bloque", "aditivo"],
    "industrial": ["industrial", "alta presión", "uso rudo", "uso intensivo"],
    "general": ["multiuso", "universal", "compatible", "doméstico", "residencial"]
}

# Diccionario de dimensiones equivalentes
dimensiones_equivalentes = {
    '1/2"': ["1/2", "0.5", '½', "1.27cm", "1.2 cm", "1,27 cm"],
    '3/4"': ["3/4", "0.75", "¾", "1.9cm", "1.91 cm"],
    '1"': ["1", "2.54 cm", "2,5cm"],
    '1 1/2"': ["1 1/2", "1.5", "1½", "3.8 cm", "3.81cm"],
    '2"': ["2", "5.08 cm", "5cm", "5,1cm"],
    '3"': ["3", "7.6cm", "7.62 cm"],
    '4"': ["4", "10 cm", "10.1 cm", "10.16cm"],
    '6"': ["6", "15.2 cm", "15.24cm"],
    '8"': ["8", "20.3 cm", "20.32cm"]
}

# Generar dimensiones métricas comunes
centimetros = [f"{i} cm" for i in range(5, 105, 5)] + [f"{i}cm" for i in range(5, 105, 5)]
metros = [f"{i} m" for i in range(1, 101)] + [f"{i}m" for i in range(1, 101)]
metros_en_cm = [f"{i * 100} cm" for i in range(1, 101)] + [f"{i*100}cm" for i in range(1, 101)]
dimensiones_metricas_equivalentes = list(set(centimetros + metros + metros_en_cm))

# Función para detectar marca
def detectar_marca_completa(titulo, fuente, link):
    titulo = titulo.lower()
    fuente = fuente.lower()
    link = link.lower()
    for marca in marcas_conocidas:
        if marca.lower() in titulo or marca.lower() in fuente or marca.lower() in link:
            return marca
    return "Sin marca"

# Limpieza de precio
def limpiar_precio(valor):
    if isinstance(valor, str):
        valor = valor.replace("$", "").replace(",", "")
        try:
            return float(re.findall(r"\d+\.\d+", valor)[0])
        except:
            return None
    return valor

# Filtro por uso
def filtrar_uso_adaptativo(texto, uso_deseado):
    texto = texto.lower()
    uso_deseado = uso_deseado.lower()
    palabras_deseadas = categorias_de_uso.get(uso_deseado, [])
    palabras_conflictivas = [
        palabra
        for categoria

 # Filtro por dimensión en pulgadas
def filtrar_por_dimension_robusta(texto, dimension_deseada):
    texto = texto.lower()
    if not dimension_deseada:
        return True

    formas_deseadas = dimensiones_equivalentes.get(dimension_deseada, [])
    formas_otros = [
        variante
        for key, variantes in dimensiones_equivalentes.items()
        if key != dimension_deseada
        for variante in variantes
    ]

    if any(forma in texto for forma in formas_deseadas):
        return True
    if any(forma in texto for forma in formas_otros):
        return False
    return True

# Filtro por longitud métrica
def filtrar_por_longitud(texto, longitud_deseada):
    texto = texto.lower()
    if not longitud_deseada:
        return True

    deseada = longitud_deseada.lower().strip()
    if deseada in texto:
        return True

    otras_longitudes = [l for l in dimensiones_metricas_equivalentes if l != deseada]
    if any(l in texto for l in otras_longitudes):
        return False
    return True

# Función para obtener productos desde SerpAPI
def obtener_productos(query):
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": API_KEY,
        "hl": "es",
        "gl": "mx"
    }
    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json().get("shopping_results", [])
    data = []
    for item in results:
        titulo = item.get("title", "")
        precio = item.get("price", "")
        tienda = item.get("source", "")
        link = item.get("link", "")
        marca_detectada = item.get("product_brand", "") or detectar_marca_completa(titulo, tienda, link)
        data.append({
            "Producto": titulo,
            "Marca": marca_detectada,
            "Precio": precio,
            "Tienda": tienda,
            "Link": link
        })
    return pd.DataFrame(data)

# Función para filtrar resultados según los criterios
def filtrar_resultados(df, modelo, uso, dimension, longitud):
    df_filtrado = df.copy()
    df_filtrado['Texto'] = df_filtrado['Producto'].str.lower() + ' ' + df_filtrado['Tienda'].str.lower()

    if modelo:
        df_filtrado = df_filtrado[df_filtrado['Texto'].str.contains(modelo.lower())]

    if uso:
        df_filtrado = df_filtrado[df_filtrado['Texto'].apply(lambda x: filtrar_uso_adaptativo(x, uso))]

    if dimension:
        df_filtrado = df_filtrado[df_filtrado['Texto'].apply(lambda x: filtrar_por_dimension_robusta(x, dimension))]

    if longitud:
        df_filtrado = df_filtrado[df_filtrado['Texto'].apply(lambda x: filtrar_por_longitud(x, longitud))]

    df_filtrado = df_filtrado.drop(columns=['Texto'])
    return df_filtrado

# Función para convertir DataFrame a CSV
def convertir_a_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Función para reiniciar la búsqueda
def reiniciar_busqueda():
    st.session_state.descripcion = ""
    st.session_state.marca = ""
    st.session_state.modelo = ""
    st.session_state.dimension = ""
    st.session_state.uso = ""
    st.session_state.longitud = ""

# Interfaz de usuario
st.title("🔍 Buscador de Productos")

descripcion = st.text_input("📝 Descripción:", key="descripcion")
marca = st.text_input("🏷️ Marca:", key="marca")
modelo = st.text_input("🔢 Modelo:", key="modelo")
dimension = st.text_input("📏 Dimensión (pulgadas):", key="dimension")
longitud = st.text_input("📐 Longitud (cm o m):", key="longitud")
uso = st.text_input("🔧 Uso:", key="uso")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🔍 Buscar"):
        if not descripcion or not marca:
            st.warning("Por favor, ingresa al menos la descripción y la marca.")
        else:
            query = f"{descripcion} {marca}"
            df = obtener_productos(query)
            df_filtrado = filtrar_resultados(df, modelo, uso, dimension, longitud)
            if not df_filtrado.empty:
                df_filtrado['Ver producto'] = df_filtrado['Link'].apply(lambda x: f'[Ver producto]({x})')
                df_filtrado = df_filtrado.drop(columns=['Link'])
                st.dataframe(df_filtrado)
                csv = convertir_a_csv(df_filtrado)
                st.download_button(
                    label="📥 Descargar resultados",
                    data=csv,
                    file_name='resultados.csv',
                    mime='text/csv',
                )
            else:
                st.info("No se encontraron resultados con los criterios proporcionados.")

with col2:
    if st.button("🔄 Reiniciar búsqueda"):
        reiniciar_busqueda()

