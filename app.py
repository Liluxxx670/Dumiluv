

import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import os

st.set_page_config(page_title="Dumiluv", page_icon="💗", layout="wide")

# --- ESTADOS ---
if "tema" not in st.session_state:
    st.session_state.tema = "purple" # rosa por defecto = imagen 3
if "nombre" not in st.session_state:
    st.session_state.nombre = ""
if "voz_activa" not in st.session_state:
    st.session_state.voz_activa = False
if "messages" not in st.session_state:
    st.session_state.messages = []

COLORES = {
    "purple": {"bg":"#e9d5ff", "window":"#f5e6ff", "header":"#f8b5d8", "chat":"#fce7ff", "side":"#ddd6fe", "border":"#c084fc"},
    "blue": {"bg":"#bfdbfe", "window":"#dbeafe", "header":"#93c5fd", "chat":"#eff6ff", "side":"#c7d2fe", "border":"#60a5fa"},
    "green": {"bg":"#bbf7d0", "window":"#dcfce7", "header":"#86efac", "chat":"#f0fdf4", "side":"#bbf7d0", "border":"#4ade80"},
    "orange": {"bg":"#ffedd5", "window":"#fff7ed", "header":"#fdba74", "chat":"#fff7ed", "side":"#fed7aa", "border":"#fb923c"},
}
C = COLORES[st.session_state.tema]

def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""
dumiluv_b64 = img_to_base64("dumiluv.png")

# --- CSS COZY ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@700&display=swap');
.stApp {{ background: {C['bg']}; }}
header, footer, #MainMenu {{visibility:hidden;}}
.block-container {{max-width: 1100px; padding-top: 0.5rem;}}
.dumi-window {{ background: {C['window']}; border: 3px solid #222; border-radius: 18px; box-shadow: 8px 8px 0px #222; overflow:hidden; }}
.dumi-header {{ background: {C['header']}; border-bottom: 3px solid #222; padding: 12px 16px; display:flex; justify-content:space-between; align-items:center; font-family:'Press Start 2P'; font-size:11px; }}
.dumi-body {{ display:grid; grid-template-columns: 165px 1fr 220px; min-height: 600px; }}
.dumi-left {{ background:{C['window']}; border-right:3px solid #222; padding:12px; text-align:center; }}
.dumi-center {{ background:{C['chat']}; padding:14px; }}
.dumi-right {{ background:{C['side']}; border-left:3px solid #222; padding:10px; }}
.history-title {{ background:{C['header']}; border:2px solid #222; border-radius:10px; padding:8px; text-align:center; font-family:'Press Start 2P'; font-size:9px; margin-bottom:10px; }}
.history-item {{ background:white; border:2px solid #222; border-radius:10px; padding:8px; margin-bottom:8px; font-size:12px; box-shadow:2px 2px 0 #222; }}
.btn-pixel {{ border:2px solid #222; border-radius:10px; padding:6px; background:white; box-shadow:2px 2px 0 #222; cursor:pointer; font-size:14px; width:100%; margin-bottom:6px; }}
</style>
""", unsafe_allow_html=True)

# --- API KEY ---
api_key = st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    with st.sidebar:
        api_key = st.text_input("Groq API Key:", type="password")
if not api_key:
    st.stop()
client = Groq(api_key=api_key)

# Inicializar sistema
if len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role":"system","content":f"Eres Dumiluv, tutora kawaii en español. Nombre usuario: {st.session_state.nombre}. PROHIBIDO LaTeX ($, \\). Escribe x^2, C2H6 + O2. Balancea reacciones: 2 C2H6 + 7 O2 -> 4 CO2 + 6 H2O. Sé dulce 💜"}]

# --- VENTANA ---
col_h1, col_h2 = st.columns([6,1])
with col_h1:
    st.markdown(f"""
    <div class="dumi-window">
      <div class="dumi-header"><div>⭐ Dumiluv ✨</div><div>AI Assistant - Online 💗</div></div>
      <div class="dumi-body">
        <div class="dumi-left">
          <img src="data:image/png;base64,{dumiluv_b64}" style="width:120px;" />
          <div style="font-family:'Press Start 2P'; font-size:8px; margin-top:8px;">AI Assistant<br>Online 💗</div>
          <div style="margin-top:15px; background:white; border:2px solid #222; border-radius:12px; padding:8px; font-size:12px;">Hola {st.session_state.nombre or 'tú'} 💜</div>
        </div>
        <div class="dumi-center">
    """, unsafe_allow_html=True)
    
    # CHAT DENTRO
    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    st.markdown("</div>", unsafe_allow_html=True)

    # PANEL DERECHO CON BOTONES
    with st.container():
        st.markdown(f"""
        <div class="dumi-right">
          <div class="history-title">Controles</div>
        """, unsafe_allow_html=True)
    
    # Aquí van los botones reales de Streamlit
    if st.button(f"{'🔊 Voz ON' if st.session_state.voz_activa else '🔇 Voz OFF'}", use_container_width=True):
        st.session_state.voz_activa = not st.session_state.voz_activa
        st.rerun()
    
    if st.button("🎨 Cambiar Tema", use_container_width=True):
        # ciclo de temas
        orden = ["purple","blue","green","orange"]
        idx = orden.index(st.session_state.tema)
        st.session_state.tema = orden[(idx+1)%len(orden)]
        st.rerun()

    # Botones de tema específicos si quieres elegir
    with st.expander("Elegir color"):
        if st.button("💜 Rosa (original)", use_container_width=True):
            st.session_state.tema="purple"; st.rerun()
        if st.button("💙 Azul", use_container_width=True):
            st.session_state.tema="blue"; st.rerun()
        if st.button("💚 Verde", use_container_width=True):
            st.session_state.tema="green"; st.rerun()
        if st.button("🧡 Naranja", use_container_width=True):
            st.session_state.tema="orange"; st.rerun()

    if st.button("👤 Perfil / Guardar Sesión", use_container_width=True):
        st.session_state.show_perfil = not st.session_state.get("show_perfil", False)

    if st.session_state.get("show_perfil", False):
        nuevo_nombre = st.text_input("Tu nombre", value=st.session_state.nombre)
        if st.button("Guardar perfil"):
            st.session_state.nombre = nuevo_nombre
            st.success(f"Guardado como {nuevo_nombre} 💜")
    
    st.markdown("""
          <div style="margin-top:12px;"><div class="history-title">Chat History</div></div>
          <div class="history-item">💬 2024-05-15: Cozy Games</div>
          <div class="history-item">💬 2024-05-14: Plant care</div>
          <div class="history-item">💬 2024-05-13: Story time</div>
          <div class="history-item">💬 2024-05-12: Mood check</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# --- INPUT ---
prompt = st.chat_input(f"Type a message, {st.session_state.nombre or 'tú'}...")

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        ph = st.empty()
        full = ""
        comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, stream=True)
        for chunk in comp:
            c = chunk.choices[0].delta.content or ""
            full += c
            ph.markdown(full + "▌")
        ph.markdown(full)

        # VOZ
        if st.session_state.voz_activa:
            try:
                tts = gTTS(text=full[:400], lang='es', slow=False) # solo 400 chars para que no tarde
                tts.save("voz.mp3")
                st.audio("voz.mp3", autoplay=True)
            except Exception as e:
                st.error(f"No se pudo generar voz: {e}")

    st.session_state.messages.append({"role":"assistant","content":full})
    st.rerun()
