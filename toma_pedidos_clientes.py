import streamlit as st
from datetime import datetime
import mercadopago
import pandas as pd
import os

# 🚨 PONE AQUÍ TU ACCESS TOKEN DE PRODUCCIÓN:
ACCESS_TOKEN = "TU_ACCESS_TOKEN_PRODUCCION"

# Inicializamos el SDK de MercadoPago
sdk = mercadopago.SDK(ACCESS_TOKEN)

# Inicializamos el estado de sesión si no existe
if 'pedido_confirmado' not in st.session_state:
    st.session_state['pedido_confirmado'] = False

# Definimos archivo CSV de base de datos
CSV_FILE = "pedidos.csv"

# Si no existe el archivo, lo creamos con las columnas correctas
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "Fecha Pedido", "Nombre", "Teléfono", "Barrio", "Dirección",
        "Tipo de Leña", "Cantidad", "Fecha Entrega", "Notas",
        "Total", "Método Pago", "Monto a Pagar",
        "Estado Pago", "Estado Entrega"
    ])
    df_init.to_csv(CSV_FILE, index=False)

st.title("Hacé tu pedido de leña")

# Barrios de San Rafael, Mendoza
barrios = [
    "Centro", "Cuadro Nacional", "El Cerrito", "Villa 25 de Mayo", "Las Paredes", 
    "Rama Caída", "Monte Comán", "Real del Padre", "Goudge", "La Llave", 
    "Jaime Prats", "El Nihuil", "Salto de las Rosas", "Las Malvinas"
]

# Precios de test bajos
precios_por_tipo = {
    "Eucalipto": 5,
    "Quebracho": 7,
    "Mix": 6,
    "Otro": 4
}

if not st.session_state['pedido_confirmado']:
    # Formulario de pedido
    st.subheader("Completá los datos de tu pedido:")

    nombre = st.text_input("Nombre completo", key="nombre")
    telefono = st.text_input("Teléfono de contacto", key="telefono")
    barrio = st.selectbox("Barrio de entrega", barrios, key="barrio")
    direccion = st.text_input("Dirección de entrega", key="direccion")
    tipo_lena = st.selectbox("Tipo de leña", list(precios_por_tipo.keys()), key="tipo_lena")
    cantidad = st.number_input("Cantidad (Kg)", min_value=1, step=1, key="cantidad")
    fecha_entrega = st.date_input("Fecha de entrega", value=datetime.today(), key="fecha_entrega")
    notas = st.text_area("Notas adicionales (opcional)", key="notas")

    precio_unitario = precios_por_tipo[st.session_state["tipo_lena"]]
    total = precio_unitario * st.session_state["cantidad"]
    st.markdown(f"### Total del pedido: ${total:,.2f}")

    metodo_pago = st.selectbox("¿Cómo querés pagar?", ["Pagar ahora", "Seña (50% anticipado)", "Pago contra entrega"], key="metodo_pago")

    if metodo_pago == "Pagar ahora":
        monto_a_pagar = total
    elif metodo_pago == "Seña (50% anticipado)":
        monto_a_pagar = total * 0.5
    else:
        monto_a_pagar = 0

    if metodo_pago != "Pago contra entrega":
        st.markdown(f"### Monto a pagar ahora: ${monto_a_pagar:,.2f}")
    else:
        st.markdown(f"### Se pagará al momento de la entrega.")

    def confirmar_pedido():
        st.session_state['pedido_confirmado'] = True
        st.session_state['pedido'] = {
            'fecha_pedido': datetime.today().strftime("%Y-%m-%d"),
            'nombre': st.session_state["nombre"],
            'telefono': st.session_state["telefono"],
            'barrio': st.session_state["barrio"],
            'direccion': st.session_state["direccion"],
            'tipo_lena': st.session_state["tipo_lena"],
            'cantidad': st.session_state["cantidad"],
            'fecha_entrega': st.session_state["fecha_entrega"].strftime("%Y-%m-%d"),
            'notas': st.session_state["notas"],
            'total': total,
            'metodo_pago': st.session_state["metodo_pago"],
            'monto_a_pagar': monto_a_pagar
        }

    st.button("Confirmar pedido", on_click=confirmar_pedido)

else:
    pedido = st.session_state['pedido']

    st.success("Pedido recibido correctamente ✅")
    st.subheader("Resumen de tu pedido:")

    st.write(f"**Cliente:** {pedido['nombre']}")
    st.write(f"**Teléfono:** {pedido['telefono']}")
    st.write(f"**Barrio:** {pedido['barrio']}")
    st.write(f"**Dirección:** {pedido['direccion']}")
    st.write(f"**Tipo de leña:** {pedido['tipo_lena']}")
    st.write(f"**Cantidad:** {pedido['cantidad']} Kg")
    st.write(f"**Fecha de entrega:** {pedido['fecha_entrega']}")
    st.write(f"**Notas:** {pedido['notas'] if pedido['notas'] else '-'}")
    st.write(f"**Total del pedido:** ${pedido['total']:,.2f}")
    st.write(f"**Método de pago:** {pedido['metodo_pago']}")

    estado_pago = "Pagado" if pedido['monto_a_pagar'] == 0 else "Pendiente"

    # Guardamos el pedido al CSV
    df = pd.read_csv(CSV_FILE)
    nuevo_pedido = pd.DataFrame([{
        "Fecha Pedido": pedido['fecha_pedido'],
        "Nombre": pedido['nombre'],
        "Teléfono": pedido['telefono'],
        "Barrio": pedido['barrio'],
        "Dirección": pedido['direccion'],
        "Tipo de Leña": pedido['tipo_lena'],
        "Cantidad": pedido['cantidad'],
        "Fecha Entrega": pedido['fecha_entrega'],
        "Notas": pedido['notas'],
        "Total": pedido['total'],
        "Método Pago": pedido['metodo_pago'],
        "Monto a Pagar": pedido['monto_a_pagar'],
        "Estado Pago": estado_pago,
        "Estado Entrega": "Pendiente"
    }])
    df = pd.concat([df, nuevo_pedido], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    if pedido['monto_a_pagar'] > 0:
        st.write(f"**Monto a pagar ahora:** ${pedido['monto_a_pagar']:,.2f}")

        # Creamos la preferencia de MercadoPago
        preference_data = {
            "items": [
                {
                    "title": f"Pedido de leña ({pedido['tipo_lena']})",
                    "quantity": 1,
                    "unit_price": float(pedido['monto_a_pagar'])
                }
            ],
            "back_urls": {
                "success": "https://www.tusitio.com/success",
                "failure": "https://www.tusitio.com/failure",
                "pending": "https://www.tusitio.com/pending"
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        st.markdown("### 🔗 [Hacé click aquí para pagar con MercadoPago]({})".format(preference["init_point"]))
    else:
        st.info("Pago contra entrega confirmado.")

    def resetear_formulario():
        st.session_state['pedido_confirmado'] = False

    st.button("Cargar nuevo pedido", on_click=resetear_formulario)
