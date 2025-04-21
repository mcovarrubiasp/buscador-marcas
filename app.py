import streamlit as st
import pandas as pd
import requests
import json

# ----------------------
# 🔑 API Keys
# ----------------------
SERPAPI_KEY = "c564bcfd30dc7e38f22ab9ac05511b434b5cb9b523d4203c3d56568f3301a6bf"
HF_TOKEN = "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"

# ----------------------
# 🔍 Función para buscar productos en SerpAPI
# ----------------------
def buscar_productos_serpapi(api_key, query, gl='us', hl='en', num=10):
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "gl": gl,
        "hl": hl,
        "num": num
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    productos = []
    if "shopping_results" in data:
        for item in data["shopping_results"]:
            productos.append({
                "Título": item.get("title"),
                "Precio": item.get("price"),
                "Tienda": item.get("source"),
                "Link": f"[Ver producto]({item.get('link')})",
                "Descripción": item.get("snippet", "")
            })
    return pd.DataFrame(productos)

# ----------------------
# 🎯 Lógica de filtro inteligente
# ----------------------
def filtrar_productos(df, producto, uso, modelo, dimension, modo):
    if df.empty:
        return df, "Sin resultados para mostrar."

    def cumple(producto_row):
        title = (producto_row["Título"] or "").lower()
        desc = (producto_row["Descripción"] or "").lower()
        todo_texto = title + " " + desc

        if producto.lower() not in todo_texto:
            return False
        if modo == "especifica":
            if uso and uso.lower() not in todo_texto:
                return False
            if modelo and modelo.lower() not in todo_texto:
                return False
            if dimension and dimension.lower() not in todo_texto:
                return False
        else:
            if uso and uso.lower() not in todo_texto:
                return False
        return True

    filtrado = df[df.apply(cumple, axis=1)]
    explicacion = "Modo específico aplicado con filtros estrictos." if modo == "especifica" else "Modo general aplicado con tolerancia amplia."
    return filtrado, explicacion

# ----------------------
# 🤖 Llamada a Hugging Face Mistral 7B para razonamiento
# ----------------------
def razonamiento_gpt(prompt):
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"temperature": 0.7, "max_new_tokens": 250}
    }
    response = requests.post(url, headers=headers, json=payload)
    try:
        return response.json()[0]["generated_text"]
    except:
        return "⚠️ No se pudo obtener la respuesta del modelo."

# ----------------------
# 🎨 Interfaz Streamlit
# ----------------------
st.title("🧠 Agente IA de Búsqueda y Razonamiento de Productos")

modo = st.radio("Selecciona el tipo de búsqueda:", ["general", "especifica"])
producto = st.text_input("Producto", value="Conector Flexible de Acero Inoxidable")
uso = st.text_input("Uso (opcional en general)", value="Lavabo")
modelo = st.text_input("Modelo (opcional en general)", value="AL-A40")
dimension = st.text_input("Dimensión (ej: 40 cm)", value="40 cm")

if st.button("Buscar"):
    with st.spinner("🔍 Buscando en SerpAPI..."):
        consulta = f"{producto} {modelo} {dimension} {uso}"
        resultados = buscar_productos_serpapi(SERPAPI_KEY, consulta)
        filtrados, explicacion = filtrar_productos(resultados, producto, uso, modelo, dimension, modo)

    st.subheader("📊 Resultados Filtrados")
    if not filtrados.empty:
        st.dataframe(filtrados[["Título", "Precio", "Tienda", "Link"]], use_container_width=True)
    else:
        st.warning("No se encontraron productos que cumplan los criterios.")

    st.markdown(f"**🔍 Lógica aplicada:** {explicacion}")

    with st.spinner("🧠 Analizando con inteligencia artificial..."):
        resumen_prompt = f"""
Actúa como un agente de compras experto. El usuario está buscando lo siguiente:
Producto: {producto}
Uso: {uso}
Modelo: {modelo}
Medida: {dimension}
Tipo de búsqueda: {modo}

Estos son los productos encontrados:
{filtrados.to_string(index=False)}

Evalúa cuáles cumplen y por qué, y da una explicación final sobre qué producto(s) recomendarías.
"""
        respuesta = razonamiento_gpt(resumen_prompt)
        st.markdown("### 🤖 Razonamiento IA")
        st.markdown(respuesta)
