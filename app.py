import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Filtro de Transacciones", layout="wide")

st.title("Buscador y Filtro de Transacciones")
st.write("Sube tu estado de cuenta en formato CSV para filtrar los movimientos por beneficiario.")

# Widget para subir el archivo
uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # 1. Leer el archivo como texto para encontrar dónde empieza la tabla real
        content = uploaded_file.getvalue().decode("utf-8").split('\n')
        header_row = 0
        
        for i, line in enumerate(content):
            # Buscamos las columnas clave de tu estado de cuenta
            if "Fecha" in line and "Beneficiario" in line and "Monto" in line:
                header_row = i
                break
        
        # 2. Volver al inicio del archivo para que pandas lo lea desde la fila correcta
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, skiprows=header_row)
        
        # 3. Limpieza de datos
        # Eliminar columnas vacías o sin nombre (comunes por las comas al inicio de la fila)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        # Eliminar filas que no tengan datos en 'Fecha' o 'Beneficiario'
        df = df.dropna(subset=['Fecha', 'Beneficiario'], how='all')
        
        st.success("Archivo procesado correctamente.")
        
        # --- SECCIÓN DE FILTRADO ---
        st.subheader("Filtrar por Beneficiario / Nombre")
        
        # Extraer la lista de nombres únicos
        lista_nombres = df['Beneficiario'].dropna().unique().tolist()
        lista_nombres.sort() # Ordenar alfabéticamente
        
        # Widget para seleccionar uno o varios nombres
        nombres_seleccionados = st.multiselect(
            "Selecciona o escribe los nombres que deseas buscar:",
            options=lista_nombres
        )
        
        # Aplicar el filtro
        if nombres_seleccionados:
            df_filtrado = df[df['Beneficiario'].isin(nombres_seleccionados)]
        else:
            df_filtrado = df # Si no hay nada seleccionado, mostrar todo
            
        st.write(f"**Mostrando {len(df_filtrado)} transacciones:**")
        st.dataframe(df_filtrado, use_container_width=True)
        
        # --- MÉTRICAS (Opcional pero muy útil para flujos financieros) ---
        if 'Monto' in df_filtrado.columns and not df_filtrado.empty:
            # Convertir la columna Monto a número (por si pandas la lee como texto)
