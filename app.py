import pandas as pd
import streamlit as st
from rapidfuzz import process, fuzz
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Mapa SJ UC", layout="wide")
st.markdown("# 🗺️ Mapa interactivo Campus San Joaquín")

@st.cache_data
def cargar_datos(path="lugares.csv"):
    df = pd.read_csv(path)
    alias = df["alias"] if "alias" in df.columns else ""
    df["buscable"] = (
        df["facultad"].fillna("") + " " +
        df["edificio"].fillna("") + " " +
        df["sala"].fillna("") + " " +
        alias.fillna("")
    ).str.lower()
    return df

df = cargar_datos()

q = st.sidebar.text_input("Buscar sala o edificio", "")

def fuzzy_filtrar(df_in, query, top_n=20):
    if not query.strip():
        return df_in
    choices = df_in["buscable"].tolist()
    results = process.extract(query.lower(), choices, scorer=fuzz.WRatio, limit=top_n)
    idxs = [i for (_, score, i) in results if score >= 60]
    return df_in.iloc[idxs] if idxs else df_in.iloc[[]]

resultados = fuzzy_filtrar(df, q)

st.subheader("Resultados")
if resultados.empty:
    st.warning("No se encontró nada.")
else:
    st.write(resultados[["facultad","edificio","sala","piso"]])

st.subheader("Mapa")
if not resultados.empty:
    center = [resultados["lat"].mean(), resultados["lon"].mean()]
else:
    center = [-33.4983, -70.6148]  # centro aprox del campus

m = folium.Map(location=center, zoom_start=16)
for _, r in resultados.iterrows():
    folium.Marker([r["lat"], r["lon"]], tooltip=r["edificio"]).add_to(m)

st_folium(m, width=700, height=500)
