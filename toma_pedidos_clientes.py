import streamlit as st
from datetime import datetime

# Inicializamos el estado de sesión si no existe
if 'pedido_confirmado' not in st.session_state:
    st.session_state['pedido_confirmado'] = False

st.title("Hacé tu pedido de leña")

# Barrios de San Rafael, Mendoza
barrios = [
    "Centro", "Cuadro Nacional", "El Cerrito", "Villa 25 de Mayo", "Las Paredes", 
    "Rama Caída", "Monte Comán", "Real del Padre", "Goudge", "La Llave", 
    "Jaime Prats", "El Nihuil", "Salto de las Rosas", "Las Malvinas"
]

# Precios unitarios por Kg (versión test productivo)
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

    # Función para procesar el pedido y cambiar de pantalla
    def confirmar_pedido():
        st.session_state['pedido_confirmado'] = True
        st.session_state['pedido'] = {
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

    if pedido['monto_a_pagar'] > 0:
        st.write(f"**Monto a pagar ahora:** ${pedido['monto_a_pagar']:,.2f}")
        st.warning("Aquí luego irá el link de pago MercadoPago 🔗")
    else:
        st.info("Pago contra entrega confirmado.")

    # Función para resetear el formulario al cargar nuevo pedido
    def resetear_formulario():
        st.session_state['pedido_confirmado'] = False

    st.button("Cargar nuevo pedido", on_click=resetear_formulario)


