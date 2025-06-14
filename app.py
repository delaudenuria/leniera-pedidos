import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Nombre del archivo CSV donde guardamos los pedidos
CSV_FILE = "pedidos.csv"

# Si el archivo no existe, lo creamos con las columnas
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        'Fecha Pedido', 'Cliente', 'Tipo de Leña', 'Cantidad', 'Precio', 'Estado Entrega', 'Estado Pago', 'Notas'
    ])
    df.to_csv(CSV_FILE, index=False)

# Leer los pedidos guardados
df = pd.read_csv(CSV_FILE)

st.title("Gestión de Pedidos - Leñera")

# ---------------------------
# Registro de nuevo pedido
# ---------------------------

st.subheader("Registrar nuevo pedido")

with st.form("pedido_form"):
    fecha_pedido = st.date_input("Fecha del pedido", value=datetime.today())
    cliente = st.text_input("Nombre del cliente")
    tipo_lena = st.selectbox("Tipo de leña", ["Eucalipto", "Quebracho", "Mix", "Otro"])
    cantidad = st.number_input("Cantidad (Kg o m3)", min_value=0.0, step=1.0)
    precio = st.number_input("Precio total ($)", min_value=0.0, step=1.0)
    estado_entrega = st.selectbox("Estado de entrega", ["Pendiente", "Entregado"])
    estado_pago = st.selectbox("Estado de pago", ["Pendiente", "Pagado"])
    notas = st.text_area("Notas adicionales")

    submitted = st.form_submit_button("Guardar pedido")

    if submitted:
        nuevo_pedido = pd.DataFrame([{
            'Fecha Pedido': fecha_pedido.strftime("%Y-%m-%d"),
            'Cliente': cliente,
            'Tipo de Leña': tipo_lena,
            'Cantidad': cantidad,
            'Precio': precio,
            'Estado Entrega': estado_entrega,
            'Estado Pago': estado_pago,
            'Notas': notas
        }])
        nuevo_pedido.to_csv(CSV_FILE, mode='a', header=False, index=False)
        st.success("Pedido guardado correctamente.")


# ---------------------------
# Buscador mejorado FULL PRO
# ---------------------------

st.subheader("Buscar y eliminar pedidos")

# Selector de campo de búsqueda
campo_busqueda = st.selectbox("Buscar por campo:", ["Cliente", "Tipo de Leña", "Estado Entrega", "Estado Pago"])

# Mapeo de columnas
mapeo_columnas = {
    "Cliente": "Cliente",
    "Tipo de Leña": "Tipo de Leña",
    "Estado Entrega": "Estado Entrega",
    "Estado Pago": "Estado Pago"
}
columna = mapeo_columnas[campo_busqueda]

# Dependiendo el campo mostramos input o selectbox
if campo_busqueda == "Estado Pago":
    filtro_valor = st.selectbox("Estado de pago:", ["Pendiente", "Pagado"])
elif campo_busqueda == "Estado Entrega":
    filtro_valor = st.selectbox("Estado de entrega:", ["Pendiente", "Entregado"])
elif campo_busqueda == "Tipo de Leña":
    filtro_valor = st.selectbox("Tipo de leña:", ["Eucalipto", "Quebracho", "Mix", "Otro"])
else:
    filtro_valor = st.text_input(f"Buscar por {campo_busqueda}:")

df_filtrado = df.copy()

if filtro_valor:
    df_filtrado = df_filtrado[df_filtrado[columna].astype(str).str.contains(filtro_valor, case=False, na=False)]

if len(df_filtrado) == 0:
    st.write("No hay pedidos que coincidan con la búsqueda.")
else:
    for idx, row in df_filtrado.iterrows():
        with st.container(border=True):
            st.write(f"**Fecha:** {row['Fecha Pedido']}")
            st.write(f"**Cliente:** {row['Cliente']}")
            st.write(f"**Leña:** {row['Tipo de Leña']} - **Cantidad:** {row['Cantidad']} - **Precio:** ${row['Precio']}")
            st.write(f"**Entrega:** {row['Estado Entrega']} - **Pago:** {row['Estado Pago']}")
            st.write(f"**Notas:** {row['Notas'] if pd.notna(row['Notas']) else '-'}")

            eliminar_click = st.button("🗑️ Eliminar pedido", key=f"delete_{idx}")
            if eliminar_click:
                with st.container(border=True):
                    st.warning("⚠️ ¿Estás seguro que querés eliminar este pedido?")
                    confirmar = st.button("Sí, eliminar definitivamente", key=f"confirm_{idx}")
                    cancelar = st.button("Cancelar", key=f"cancel_{idx}")
                    if confirmar:
                        df.drop(index=idx, inplace=True)
                        df.reset_index(drop=True, inplace=True)
                        df.to_csv(CSV_FILE, index=False)
                        st.success("Pedido eliminado correctamente.")

