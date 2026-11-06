import streamlit as st
from groq import Groq

st.markdown("""
<style>
h1 { color: #6a0dad !important; }
h3 { color: #8a2be2 !important; }
p, .stMarkdown { color: #4b0082 !important; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Dumiluv 2.0", page_icon="📚", layout="centered")

# --- ESTILO ---
st.markdown("""
<style>
.stApp { background: #f8f9ff; }
.ejemplo-card {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #e6e6ff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    cursor: pointer;
    height: 110px;
    transition: 0.2s;
}
.ejemplo-card:hover { transform: scale(1.02); border-color: #a48fff; }
</style>
""", unsafe_allow_html=True)

# --- NOMBRE DEL USUARIO ---
if "nombre" not in st.session_state:
    st.session_state.nombre = ""

with st.sidebar:
    st.title("💗 Dumiluv 2.0")
    st.session_state.nombre = st.text_input("¿Cómo te llamas?", value=st.session_state.nombre, placeholder="Ej: Lili")
    st.divider()
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        api_key = st.text_input("Groq API Key:", type="password")
    st.caption("Tu tutor 100% en la nube ☁️")

if not api_key:
    st.info("👋 Configura tu GROQ_API_KEY en Secrets para comenzar.")
    st.stop()

client = Groq(api_key=api_key)

nombre_display = st.session_state.nombre if st.session_state.nombre else "tú"
saludo_nombre = f"Te llamarás {st.session_state.nombre}. Úsalo para personalizar tus respuestas de forma cálida." if st.session_state.nombre else "El usuario no ha dado su nombre, sé amable y pregunta su nombre si es natural."

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": ""
Eres Dumiluv 2.0, tutora de prepa amable pero muy atenta a los detalles.

REGLAS OBLIGATORIAS:
1. Si el usuario escribe una ecuación o ejercicio mal escrito, con datos faltantes o ilógico (ej: "x² + = 6" o "calcula la velocidad sin dar tiempo"), NO intentes adivinar.
2. Primero dile con cariño que se equivocó y qué dato exacto falta o está mal.
3. Ejemplo: "¡Ojo por aquí! 💜 Me pusiste C2H6 + O2 -> pero te faltó decir que quieres obtener. ¿Quieres balancearla a CO2 + H2O?"
4. Si todo está bien, ahí sí explica paso a paso.
5. Siempre usa el nombre del estudiante si lo sabes.
6. Habla en español, en tonos morados, motivadora.

Objetivo: Que el alumno aprenda a escribir bien sus ejercicios.
""}
    ]

# --- TITULO ---
st.title("📚 Dumiluv 2.0")
st.image("dumiluv.png", width=250)
if st.session_state.nombre:
    st.subheader(f"Hola {st.session_state.nombre} 💗, ¿qué vamos a aprender hoy?")
else:
    st.subheader("Tu tutor de prepa 100% libre en la nube")

# --- SI NO HAY CHAT, MUESTRA LOS 4 CUADROS ---
if len(st.session_state.messages) == 1:
    st.write(f"¡Hola {nombre_display}! Elige un ejemplo para empezar 👇")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📐 ¿Cómo resuelvo x² -5x +6 =0 paso a paso?", use_container_width=True):
            st.session_state.ejemplo = "¿Cómo resuelvo x² -5x +6 =0 paso a paso? Explícame como si fuera mi primera vez"
            st.rerun()
        if st.button("⚛️ Explícame la 2da Ley de Newton con un ejemplo real", use_container_width=True):
            st.session_state.ejemplo = "Explícame la 2da Ley de Newton con un ejemplo de la vida real y un ejercicio"
            st.rerun()
    with col2:
        if st.button("🧪 ¿Cómo balanceo C2H6 + O2 -> CO2 + H2O?", use_container_width=True):
            st.session_state.ejemplo = "¿Cómo balanceo la ecuación química C2H6 + O2 -> CO2 + H2O? Enséñame paso a paso"
            st.rerun()
        if st.button("📈 ¿Qué es una derivada y para qué sirve?", use_container_width=True):
            st.session_state.ejemplo = "¿Qué es una derivada y para qué sirve? Dame un ejemplo fácil"
            st.rerun()

# --- MOSTRAR HISTORIAL ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- MANEJO DE PROMPT ---
prompt = None
if "ejemplo" in st.session_state:
    prompt = st.session_state.ejemplo
    del st.session_state["ejemplo"]
else:
    prompt = st.chat_input(f"Escribe tu duda, {nombre_display}...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b", # CAMBIADO: este sí existe y es gratis
            messages=st.session_state.messages,
            stream=True
        )
        
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            full_response += content
            response_placeholder.markdown(full_response + "▌")
            
        response_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
