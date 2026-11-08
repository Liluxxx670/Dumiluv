import streamlit as st
from groq import Groq
from gtts import gTTS
import os

st.set_page_config(page_title="Dumiluv", page_icon="💗", layout="wide")

# ESTADOS
if "tema" not in st.session_state:
    st.session_state.tema = "orange" # tu foto es naranja, lo dejo así como lo tenías
if "nombre" not in st.session_state:
    st.session_state.nombre = ""
if "email" not in st.session_state:
    st.session_state.email = ""
if "voz_activa" not in st.session_state:
    st.session_state.voz_activa = False
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content":"Eres Dumiluv, tutora kawaii de prepa en español. PROHIBIDO LaTeX. Escribe x^2, C2H6 + O2. Balancea reacciones. Sé dulce 💜"}]

COLORES = {
    "purple": {"bg":"#e9d5ff", "header":"#f0abfc", "chat":"#fce7ff", "side":"#ddd6fe", "border":"#c084fc"},
    "blue": {"bg":"#bfdbfe", "header":"#93c5fd", "chat":"#eff6ff", "side":"#c7d2fe", "border":"#60a5fa"},
    "green": {"bg":"#bbf7d0", "header":"#86efac", "chat":"#f0fdf4", "side":"#bbf7d0", "border":"#4ade80"},
    "orange": {"bg":"#ffedd5", "header":"#f7c978", "chat":"#fff7ed", "side":"#ffedd5", "border":"#fb923c"},
}
C = COLORES[st.session_state.tema]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@700&display=swap');
.stApp {{background: {C['bg']};}}
header, footer {{visibility:hidden;}}
.block-container {{max-width:1150px; padding-top:1rem;}}
.main-box {{background:white; border:3px solid #222; border-radius:18px; box-shadow:8px 8px 0 #222; overflow:hidden;}}
.header-box {{background:{C['header']}; border-bottom:3px solid #222; padding:12px 18px; display:flex; justify-content:space-between; font-family:'Press Start 2P'; font-size:11px;}}
.chat-history-b {{font-weight:900 !important; color:#222 !important;}}
.email-box {{background:#fdf4ff; border:2px solid #222; border-radius:12px; padding:10px; font-size:11px; text-align:left;}}
.email-box a {{color:#6a0dad; font-weight:bold; word-break:break-all;}}
div[data-testid="stChatInput"] {{display:none;}}
</style>
""", unsafe_allow_html=True)

# API KEY - USA EL BUENO
api_key = st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    api_key = st.text_input("Pon tu GROQ_API_KEY en Secrets", type="password")
if not api_key:
    st.stop()

client = Groq(api_key=api_key)

# LOGIN GMAIL
if not st.session_state.email:
    st.markdown(f"<div class='main-box'><div class='header-box'>⭐ Dumiluv - Iniciar Sesión ✨</div><div style='padding:30px; text-align:center;'>", unsafe_allow_html=True)
    st.write("### 💜 Inicia sesión para guardar tu progreso")
    email = st.text_input("Tu Gmail:", placeholder="ejemplo@gmail.com")
    nombre = st.text_input("¿Cómo te llamas?", placeholder="Lili")
    if st.button("Entrar a Dumiluv 💗"):
        if "@gmail.com" in email or "@" in email:
            st.session_state.email = email
            st.session_state.nombre = nombre
            st.rerun()
        else:
            st.error("Pon un correo válido")
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# VENTANA PRINCIPAL
st.markdown(f"""
<div class="main-box">
  <div class="header-box">
    <div>⭐ Dumiluv ✨</div>
    <div>AI Assistant - Online 💗 - {st.session_state.email}</div>
  </div>
</div>
""", unsafe_allow_html=True)

col_izq, col_centro, col_der = st.columns([1.1, 2.4, 1.1], gap="small")

with col_izq:
    st.markdown("<div class='main-box' style='padding:12px; text-align:center; min-height:620px;'>", unsafe_allow_html=True)
    st.image("dumiluv.png", use_container_width=True)
    st.markdown(f"<div style='font-family:Press Start 2P; font-size:7px; margin-top:8px;'>AI Assistant<br>Online 💗<br>{st.session_state.nombre}</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div class="email-box">
    <b>💜 ¿Ocurrió alguna falla? 💜</b><br><br>
    📧 <a href="mailto:7001467@etrr.edu.mx">7001467@etrr.edu.mx</a><br>
    📧 <a href="mailto:7001464@etrr.edu.mx">7001464@etrr.edu.mx</a><br>
    📧 <a href="mailto:7001451@etrr.edu.mx">7001451@etrr.edu.mx</a><br>
    📧 <a href="mailto:7001529@etrr.edu.mx">7001529@etrr.edu.mx</a>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Cerrar sesión"):
        st.session_state.email = ""
        st.session_state.nombre = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_centro:
    st.markdown(f"<div class='main-box' style='background:{C['chat']}; padding:12px; min-height:620px; display:flex; flex-direction:column;'>", unsafe_allow_html=True)
    
    # CHAT ADENTRO
    chat_container = st.container(height=480)
    with chat_container:
        for m in st.session_state.messages:
            if m["role"] != "system":
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])
    
    # INPUT ADENTRO DEL RECUADRO
    with st.form("chat_form", clear_on_submit=True):
        prompt = st.text_input(f"Type a message, {st.session_state.nombre}...", placeholder=f"Type a message, {st.session_state.nombre}...")
        enviar = st.form_submit_button("Enviar 💜", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    if enviar and prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                ph = st.empty()
                full = ""
                try:
                    # MODELO QUE SI SIRVE
                    comp = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=st.session_state.messages,
                        stream=True
                    )
                    for chunk in comp:
                        c = chunk.choices[0].delta.content or ""
                        full += c
                        ph.markdown(full + "▌")
                    ph.markdown(full)
                    if st.session_state.voz_activa and full:
                        try:
                            tts = gTTS(text=full[:350], lang='es', slow=False)
                            tts.save("voz.mp3")
                            st.audio("voz.mp3", autoplay=True)
                        except:
                            pass
                except Exception as e:
                    ph.markdown(f"❌ Error: {e} - Revisa tu GROQ_API_KEY")
                    full = f"Error: {e}"
        
        st.session_state.messages.append({"role":"assistant","content":full})
        st.rerun()

with col_der:
    st.markdown(f"<div class='main-box' style='background:{C['side']}; padding:10px; min-height:620px;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{C['header']}; border:2px solid #222; border-radius:10px; padding:8px; text-align:center; font-family:Press Start 2P; font-size:8px;'>Controles</div>", unsafe_allow_html=True)
    
    if st.button(f"{'🔊 Voz ON' if st.session_state.voz_activa else '🔇 Voz OFF'}", use_container_width=True):
        st.session_state.voz_activa = not st.session_state.voz_activa
        st.rerun()
    
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    sel = st.selectbox("Tema", ["orange","purple","blue","green"], index=["orange","purple","blue","green"].index(st.session_state.tema))
    if sel != st.session_state.tema:
        st.session_state.tema = sel
        st.rerun()

    st.divider()
    st.markdown(f"<div style='background:{C['header']}; border:2px solid #222; border-radius:10px; padding:8px; text-align:center; font-family:Press Start 2P; font-size:8px;'>Chat History</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='margin-top:10px;'>
      <div style='background:white; border:2px solid #222; border-radius:10px; padding:8px; margin-bottom:8px; box-shadow:2px 2px 0 #222;'><b style='font-weight:900;'>💬 2024-05-15: Cozy Games</b></div>
      <div style='background:white; border:2px solid #222; border-radius:10px; padding:8px; margin-bottom:8px; box-shadow:2px 2px 0 #222;'><b style='font-weight:900;'>💬 2024-05-14: Plant care</b></div>
      <div style='background:white; border:2px solid #222; border-radius:10px; padding:8px; margin-bottom:8px; box-shadow:2px 2px 0 #222;'><b style='font-weight:900;'>💬 2024-05-13: Story time</b></div>
      <div style='background:white; border:2px solid #222; border-radius:10px; padding:8px; margin-bottom:8px; box-shadow:2px 2px 0 #222;'><b style='font-weight:900;'>💬 2024-05-12: Mood check</b></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

