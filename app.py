import streamlit as st
import pandas as pd
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import re

# 🗝️ API KEY
API_KEY = "c564bcfd30dc7e38f22ab9ac05511b434b5cb9b523d4203c3d56568f3301a6bf"

# 🧱 SUPERLISTA DE MARCAS
marcas_conocidas = [
    "Foset","omega","Omega","Conduit", "Rotoplas", "Coflex", "RUGO", "IUSA", "Amanco Wavin", "Cinsa", "Calorex", "Helvex", "Urrea",
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
    "Silverplastic", "Wetweld", "Weld-On"
]

frases_excluir = ["the home depot", "mercado libre", "sodimac", "amazon", "linio", "elektra", "uber eats"]

# 🔍 Scraper de respaldo
def detectar_marca_scraping(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return 'Sin marca'
        soup = BeautifulSoup(response.content, 'html.parser')
        contenido = ' '.join(soup.stripped_strings).lower()
        for marca in marcas_conocidas:
            if marca.lower() in contenido:
                return marca
        return 'Sin marca'
    except:
        return 'Sin marca'

# 🎯 Detección completa con orden de prioridad
def detectar_marca_completa(titulo, product_brand, source, link):
    if product_brand and product_brand.strip().lower() != "unknown":
        return product_brand.strip()

    titulo_clean = titulo.lower()
    for palabra in frases_excluir:
        titulo_clean = titulo_clean.replace(palabra, "")

    for marca in marcas_conocidas:
        if marca.lower() in titulo_clean:
            return marca

    fuente = f"{source} {link}".lower()
    for marca in marcas_conocidas:
        if marca.lower() in fuente:
            return marca

    return detectar_marca_scraping(link)

def limpiar_precio(valor):
    if isinstance(valor, str):
        valor = valor.replace("$", "").replace(",", "")
        try:
            return float(re.findall(r"\d+\.\d+", valor)[0])
        except:
            return None
    return valor

def buscar_producto(query):
    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "es",
        "gl": "mx",
        "api_key": API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    productos = results.get("shopping_results", [])

    data = []
    for p in productos:
        titulo = p.get("title", "")
        marca = detectar_marca_completa(
            titulo,
            p.get("product_brand"),
            p.get("source", ""),
            p.get("link", "")
        )
        data.append({
            "Producto": titulo,
            "Marca": marca,
            "Precio": p.get("price"),
            "Tienda": p.get("source"),
            "Link": p.get("link")
        })
    return pd.DataFrame(data)

# 🚀 STREAMLIT INTERFAZ
st.set_page_config(page_title="Buscador de Precios", layout="wide")
st.title("🛍️ Buscador de Productos - Google Shopping")

query = st.text_input("¿Qué producto deseas buscar?", placeholder="Ej: cemento para PVC")

if query:
    st.write(f"🔍 Buscando: **{query}**...")
    df = buscar_producto(query)

    if df.empty:
        st.warning("⚠️ No se encontraron productos.")
    else:
        df["PrecioNum"] = df["Precio"].apply(limpiar_precio)
        st.dataframe(df[["Producto", "Marca", "Precio", "Tienda", "Link"]])

        resumen = df.groupby("Marca")["PrecioNum"].agg(["mean", "median", "std"]).round(2)
        resumen = resumen.rename(columns={"mean": "Promedio", "median": "Mediana", "std": "DesvEstándar"})

        st.subheader("📊 Estadísticas por Marca")
        st.dataframe(resumen)

        # Botón de descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Productos", data=csv, file_name='productos.csv', mime='text/csv')
