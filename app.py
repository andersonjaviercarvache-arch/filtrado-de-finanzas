import streamlit as st
import pandas as pd

# Configuración principal de la página
st.set_page_config(page_title="Filtro de Estado de Cuenta", page_icon="📊", layout="wide")

st.title("📊 Analizador de Estados de Cuenta")
st.write("Sube tu estado de cuenta bancario para filtrar las transacciones por beneficiario o monto.")

# 1. Carga de archivo
archivo_subido = st.file_uploader("Sube tu archivo (CSV o Excel)", type=["csv", "xlsx"])

if archivo_subido is not None:
    try:
        # Leer el archivo dependiendo de su formato
        if archivo_subido.name.endswith('.csv'):
            df = pd.read_csv(archivo_subido)
        else:
            df = pd.read_excel(archivo_subido)
            
        st.success("Archivo cargado correctamente.")
        st.divider()
        
        st.subheader("⚙️ Configuración de Columnas")
        # 2. Selección dinámica de columnas
        col_opciones = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            col_beneficiario = st.selectbox("Selecciona la columna de Beneficiario / Descripción:", col_opciones, index=0)
        with col2:
            # Intenta preseleccionar la última columna por defecto (suele ser el saldo o monto)
            index_monto = len(col_opciones) - 1 if len(col_opciones) > 1 else 0
            col_monto = st.selectbox("Selecciona la columna de Monto:", col_opciones, index=index_monto)

        st.divider()
        st.subheader("🔍 Filtros de Búsqueda")
        
        # Limpieza de la columna de monto (quita comas de miles y convierte a número)
        df[col_monto] = pd.to_numeric(df[col_monto].astype(str).str.replace(',', ''), errors='coerce')
        
        # Eliminar temporalmente las filas que no tengan un monto válido para no romper el filtro
        df_limpio = df.dropna(subset=[col_monto])

        # 3. Controles de Filtro
        col3, col4 = st.columns(2)
        with col3:
            buscar_beneficiario = st.text_input("🔎 Filtrar por nombre (o parte del nombre):", "")
            
        with col4:
            # Determinar el rango máximo y mínimo para el slider de dinero
            if not df_limpio.empty:
                min_monto = float(df_limpio[col_monto].min())
                max_monto = float(df_limpio[col_monto].max())
            else:
                min_monto, max_monto = 0.0, 1000.0
            
            # Asegurarse de que el mínimo y máximo no sean exactamente iguales para que el slider funcione
            if min_monto == max_monto:
                max_monto = min_monto + 1.0

            rango_monto = st.slider(
                "💰 Rango de Monto:", 
                min_value=min_monto, 
                max_value=max_monto, 
                value=(min_monto, max_monto)
            )

        # 4. Aplicar Filtros
        df_filtrado = df_limpio.copy()

        # Filtro de texto (ignora mayúsculas/minúsculas)
        if buscar_beneficiario:
            df_filtrado = df_filtrado[df_filtrado[col_beneficiario].astype(str).str.contains(buscar_beneficiario, case=False, na=False)]

        # Filtro de números
        df_filtrado = df_filtrado[(df_filtrado[col_monto] >= rango_monto[0]) & (df_filtrado[col_monto] <= rango_monto[1])]

        # 5. Mostrar Resultados
        st.divider()
        st.subheader(f"📑 Resultados: {len(df_filtrado)} transacciones encontradas")
        st.dataframe(df_filtrado, use_container_width=True)

        # 6. Botón de Descarga
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv,
            file_name='estado_cuenta_filtrado.csv',
            mime='text/csv',
        )

    except Exception as e:
        st.error(f"Hubo un error al procesar el documento. Verifica que las columnas seleccionadas sean correctas. Detalle técnico: {e}")
