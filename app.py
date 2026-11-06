import streamlit as st
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="Dumiluv 2.0 - Tu Tutor Personal",
    page_icon="💖",
    layout="centered"
)

# 2. Estilos visuales con temática rosada kawaii
st.markdown("""
    <style>
    .stApp {
        background-color: #fff0f5;
    }
    .main-header {
        background: linear-gradient(135deg, #ff758c, #ff7eb3);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(255, 117, 140, 0.3);
        margin-bottom: 25px;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.3rem;
    }
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
        margin-top: 8px;
    }
    .stChatMessage {
        border-radius: 15px !important;
        padding: 12px 18px !important;
        margin-bottom: 10px !important;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #ffd1dc;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Encabezado visual con la imagen de Dumiluv y título rosado
col_img, col_txt = st.columns([1, 3])
with col_img:
    try:
        st.image("dumiluv.png", width=120)
    except:
        st.write("💖")

with col_txt:
    st.markdown("""
        <div class="main-header" style="margin-bottom: 0px; padding: 15px;">
            <h1>✨ Dumiluv 2.0 ✨</h1>
            <p>💖 Tu tierno tutor escolar en la nube</p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# 4. Configuración de la API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    with st.sidebar:
        st.header("⚙️ Configuración")
        api_key = st.text_input("Ingresa tu Groq API Key:", type="password")
        st.info("💡 Consejo: Agrega la clave a st.secrets en Streamlit Cloud.")

if not api_key:
    st.warning("⚠️ Por favor ingresa tu API Key para comenzar a chatear con Dumiluv.")
    st.stop()

client = Groq(api_key=api_key)

# 5. Historial y personalidad de tutor tierno
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres Dumiluv, un personaje tierno, dulce, empático y muy inteligente. Eres un tutor de preparatoria que ayuda a los estudiantes a resolver dudas de matemáticas, física y ciencias con amor, paciencia, viñetas y emojis rosados o tiernos."
        }
    ]

# 6. Mostrar el historial del chat usando la imagen de Dumiluv como avatar del asistente
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "dumiluv.png" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# 7. Entrada de chat del usuario con respuestas en tiempo real
if prompt := st.chat_input("Escribe tu duda escolar aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="dumiluv.png"):
        response_placeholder = st.empty()
        full_response = ""
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=True
        )
        
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            full_response += content
            response_placeholder.markdown(full_response + "▌")
            
        response_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
