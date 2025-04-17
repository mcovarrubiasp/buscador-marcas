import streamlit as st
import pandas as pd
import requests
import re
from io import BytesIO

st.set_page_config(page_title="Buscador de Productos", layout="wide")

API_KEY = "c564bcfd30dc7e38f22ab9ac05511b434b5cb9b523d4203c3d56568f3301a6bf"

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

def detectar_marca_completa(titulo, fuente, link):
    texto = f"{titulo} {fuente} {link}".lower()
    for marca in marcas_conocidas:
        if marca.lower() in texto:
            return marca
    return "Sin marca"

def limpiar_precio(valor):
    if isinstance(valor, str):
        valor = valor.replace("$", "").replace(",", "")
        try:
            return float(re.findall(r"\d+\.\d+", valor)[0])
        except:
            return None
    return valor

def es_mayoreo(texto):
    palabras = ['pzas', 'paquete', 'kit', 'caja', 'mayoreo', 'set', 'combo', 'x unidades']
    return any(p in texto.lower() for p in palabras)

def mostrar_estadisticas(df, titulo):
    df['PrecioNum'] = df['Precio'].apply(limpiar_precio)
    resumen = df.groupby("Marca")["PrecioNum"].agg(["count", "mean", "median", "std"]).round(2)
    resumen = resumen.rename(columns={"count": "Cantidad", "mean": "Promedio", "median": "Mediana", "std": "DesvEstándar"})
    resumen['Promedio'] = resumen['Promedio'].apply(lambda x: f"${x:,.2f}")
    resumen['Mediana'] = resumen['Mediana'].apply(lambda x: f"${x:,.2f}")
    resumen['DesvEstándar'] = resumen['DesvEstándar'].apply(lambda x: f"{x:,.2f}")
    st.subheader(titulo)
    st.dataframe(resumen)
    return resumen

def mostrar_resultados(df, titulo):
    df = df.copy()
    df['Ver producto'] = df['Link'].apply(lambda x: f'[Ver producto]({x})')
    df = df.drop(columns=['Link'])
    st.subheader(titulo)
    st.dataframe(df)
    return df

def obtener_productos(descripcion, marca):
    query = f"{descripcion} {marca}"
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

def clasificar_coincidencias(df, modelo):
    df = df.copy()
    df['Coincidencia'] = df['Producto'].apply(lambda x: 'Exacto' if modelo.lower() in x.lower() else 'Similar')
    return df

def convertir_a_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# UI
st.title("🔍 Buscador de Productos")

modo = st.radio("Selecciona el modo de búsqueda:", ["General", "Específica"])
descripcion = st.text_input("📝 Descripción:")
marca = st.text_input("🏷️ Marca:")
modelo = st.text_input("🔢 Modelo:")
dimension = st.text_input("📏 Dimensión:")

if st.button("Buscar"):
    if not descripcion or not marca:
        st.warning("La descripción y la marca son obligatorias.")
    else:
        df = obtener_productos(descripcion, marca)
        df = df[~df['Producto'].apply(es_mayoreo)].copy()

        if df.empty:
            st.info("No se encontraron productos.")
        elif modo == "General":
            mostrar_resultados(df, "🛒 Resultados Generales")
            resumen = mostrar_estadisticas(df, "📊 Estadísticas Generales")
            st.download_button("⬇️ Descargar Resultados", convertir_a_csv(df), "resultados_generales.csv", "text/csv")
            st.download_button("⬇️ Descargar Estadísticas", convertir_a_csv(resumen), "estadisticas_generales.csv", "text/csv")

        elif modo == "Específica":
            df = clasificar_coincidencias(df, modelo)
            exactos = df[df['Coincidencia'] == 'Exacto']
            similares = df[df['Coincidencia'] == 'Similar']

            if not exactos.empty:
                df1 = mostrar_resultados(exactos, "✅ Coincidencias Exactas")
                res1 = mostrar_estadisticas(exactos, "📊 Estadísticas Exactas")
                st.download_button("⬇️ Descargar Exactos", convertir_a_csv(df1), "exactos.csv", "text/csv")
                st.download_button("⬇️ Descargar Estadísticas Exactos", convertir_a_csv(res1), "estadisticas_exactos.csv", "text/csv")

            if not similares.empty:
                df2 = mostrar_resultados(similares, "🔄 Coincidencias Similares")
                res2 = mostrar_estadisticas(similares, "📊 Estadísticas Similares")
                st.download_button("⬇️ Descargar Similares", convertir_a_csv(df2), "similares.csv", "text/csv")
                st.download_button("⬇️ Descargar Estadísticas Similares", convertir_a_csv(res2), "estadisticas_similares.csv", "text/csv")
