import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
import json, os, re, hashlib, base64
from PIL import Image

st.set_page_config(page_title="Dumiluv", page_icon="💗", layout="wide")

USERS_FILE = "users.json"
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

if "tema" not in st.session_state:
    st.session_state.tema = "purple"
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "voz_activa" not in st.session_state:
    st.session_state.voz_activa = False
if "show_notas" not in st.session_state:
    st.session_state.show_notas = False
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content":"Eres Dumiluv, tutora de ALGEBRA y MATES de prepa en español. Solo ayudas con álgebra, ecuaciones, derivadas, Newton, química de balanceo. PROHIBIDO LaTeX ($, \\). Escribe x^2. Balancea. No des la respuesta directa, guía paso a paso. Sé dulce 💜"}]
if "historial" not in st.session_state:
    st.session_state.historial = []

COLORES = {
    "purple": {"bg":"#e9d5ff", "header":"#c084fc", "header_text":"#1a0033", "chat":"#faf5ff", "user_color":"#a855f7"},
    "blue": {"bg":"#bfdbfe", "header":"#3b82f6", "header_text":"#0a1e40", "chat":"#eff6ff", "user_color":"#3b82f6"},
    "green": {"bg":"#bbf7d0", "header":"#22c55e", "header_text":"#052e13", "chat":"#f0fdf4", "user_color":"#22c55e"},
    "orange": {"bg":"#ffedd5", "header":"#f97316", "header_text":"#3d1600", "chat":"#fff7ed", "user_color":"#f97316"},
}
C = COLORES[st.session_state.tema]

# Avatares
def get_avatar_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# Crear avatar usuario genérico (bolita con persona) si no hay
dumi_avatar = "dumiluv.png"

st.markdown(f"""
<style>
.stApp {{background:{C['bg']};}}
header, footer {{visibility:hidden;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: white;
    border: 3px solid #222 !important;
    border-radius: 18px !important;
    box-shadow: 6px 6px 0 #222 !important;
}}
/* INPUT EN BLANCO CLARO */
div[data-testid="stTextInput"] input {{
    background: white !important;
    color: #222 !important;
    border: 2px solid #222 !important;
    border-radius: 12px !important;
}}
div[data-testid="stForm"] {{
    background: white !important;
}}
.header-box {{
    background:{C['header']};
    color:{C['header_text']} !important;
    border:2px solid #222;
    border-radius:12px;
    padding:8px;
    text-align:center;
    font-weight:900;
}}
/* Chat avatar */
div[data-testid="stChatMessageAvatar"] {{
    background: white;
    border: 2px solid #222;
}}
</style>
""", unsafe_allow_html=True)

# LOGIN
if not st.session_state.usuario:
    st.markdown(f"<div class='header-box'>⭐ Dumiluv - Crear Usuario / Iniciar Sesión ✨</div>", unsafe_allow_html=True)
    with st.container(border=True):
        tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "✨ Crear Usuario"])
        users = load_users()
        with tab1:
            u = st.text_input("Usuario", key="login_u")
            p = st.text_input("Contraseña", type="password", key="login_p")
            if st.button("Entrar 💜", use_container_width=True):
                if u in users and users[u]["pass"] == hash_pass(p):
                    st.session_state.usuario = u
                    st.session_state.messages = [{"role":"system","content":f"Eres Dumiluv. Usuario: {u}. Solo álgebra/mates. PROHIBIDO LaTeX. Guía no des respuesta directa. Sé dulce 💜"}]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        with tab2:
            st.caption("Solo letras, números, punto . y guión _ (sin signos raros)")
            new_u = st.text_input("Nuevo usuario", key="new_u", placeholder="lili.cox")
            new_p = st.text_input("Nueva contraseña", type="password", key="new_p")
            new_p2 = st.text_input("Repite contraseña", type="password", key="new_p2")
            if st.button("Crear cuenta ✨", use_container_width=True):
                if not re.match(r"^[a-zA-Z0-9._]+$", new_u):
                    st.error("Solo letras, números, punto y guión bajo.")
                elif new_u in users:
                    st.error(f"El usuario '{new_u}' ya existe.")
                elif len(new_u) < 3:
                    st.error("Mínimo 3 caracteres")
                elif new_p != new_p2:
                    st.error("Las contraseñas no coinciden")
                elif len(new_p) < 4:
                    st.error("Mínimo 4 caracteres")
                else:
                    users[new_u] = {"pass": hash_pass(new_p)}
                    save_users(users)
                    st.success(f"Usuario {new_u} creado! Inicia sesión 💜")
    st.stop()

api_key = st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    st.error("Falta GROQ_API_KEY en Secrets")
    st.stop()
client = Groq(api_key=api_key)
MODELO_GROQ = "llama3-8b-8192"

# HEADER
with st.container(border=True):
    c1, c2 = st.columns([3,1])
    with c1:
        st.markdown(f"**⭐ Dumiluv ✨ - Hola {st.session_state.usuario}**")
    with c2:
        if st.button("Cerrar sesión"):
            st.session_state.usuario = ""
            st.rerun()

col_izq, col_centro, col_der = st.columns([1, 2.2, 1])

with col_izq:
    with st.container(border=True):
        st.image("dumiluv.png", use_container_width=True)
        st.markdown(f"<p style='text-align:center; font-weight:900;'>AI Assistant<br>Online 💗</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown("""
        <div style='font-size:11px; font-weight:900; color:#222;'>
        💜 ¿Falla?<br><br>
        📧 <b>7001467@etrr.edu.mx</b><br>
        📧 <b>7001464@etrr.edu.mx</b><br>
        📧 <b>7001451@etrr.edu.mx</b><br>
        📧 <b>7001529@etrr.edu.mx</b>
        </div>
        """, unsafe_allow_html=True)

with col_centro:
    with st.container(border=True):
        st.markdown(f"<div class='header-box'>💬 Chat con Dumiluv</div>", unsafe_allow_html=True)
        
        if len([m for m in st.session_state.messages if m["role"]!="system"]) == 0:
            st.write(f"Hola {st.session_state.usuario} 💗 ¿Qué vamos a aprender hoy?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📐 x² -5x +6 =0", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":"x² -5x +6 =0"})
                    st.rerun()
                if st.button("⚛️ 2da Ley de Newton", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":"Explícame la 2da Ley de Newton"})
                    st.rerun()
            with c2:
                if st.button("🧪 C2H6 + O2 -> CO2 + H2O", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":"C2H6 + O2 -> CO2 + H2O balancéala"})
                    st.rerun()
                if st.button("📈 ¿Qué es una derivada?", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":"¿Qué es una derivada?"})
                    st.rerun()
        
        chat_box = st.container(height=380)
        with chat_box:
            for m in st.session_state.messages:
                if m["role"] != "system":
                    # AVATARES CAMBIADOS
                    if m["role"] == "assistant":
                        avatar = dumi_avatar # Tu Dumiluv rosita
                    else:
                        avatar = None # luego ponemos icono personalizado
                    with st.chat_message(m["role"], avatar=avatar if m["role"]=="assistant" else "🧑"):
                        st.markdown(m["content"])
        
        # INPUT BLANCO
        with st.form("form_chat", clear_on_submit=True):
            prompt = st.text_input("Escribe...", placeholder="Type a message, Lili...", label_visibility="collapsed")
            col_env, col_nota = st.columns([3,1])
            with col_env:
                enviar = st.form_submit_button("Enviar 💜", use_container_width=True)
            with col_nota:
                nota_btn = st.form_submit_button("📝 Notas", use_container_width=True)
        
        if nota_btn:
            st.session_state.show_notas = not st.session_state.show_notas
        
        # LIBRETITA PARA RESOLVER
        if st.session_state.show_notas:
            st.markdown(f"<div class='header-box'>📓 Tu libretita para resolver - Escribe y dibuja</div>", unsafe_allow_html=True)
            st.caption("Aquí puedes resolver la operación, la IA te guía pero tú lo haces 💜")
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=3,
                stroke_color=C['user_color'],
                background_color="#ffffff",
                background_image=None,
                update_streamlit=True,
                height=300,
                drawing_mode="freedraw",
                key="canvas",
            )
            nota_text = st.text_area("Tus apuntes:", placeholder="Escribe aquí tus pasos: x² -5x +6 = (x-2)(x-3)...")
            if st.button("Limpiar libretita"):
                st.rerun()

        if enviar and prompt:
            st.session_state.messages.append({"role":"user","content":prompt})
            titulo = prompt[:25] + ("..." if len(prompt)>25 else "")
            if titulo not in st.session_state.historial:
                st.session_state.historial.insert(0, titulo)
            try:
                comp = client.chat.completions.create(model=MODELO_GROQ, messages=st.session_state.messages)
                full = comp.choices[0].message.content
                st.session_state.messages.append({"role":"assistant","content":full})
                if st.session_state.voz_activa:
                    try:
                        tts = gTTS(text=full[:400], lang='es')
                        tts.save("voz.mp3")
                        st.audio("voz.mp3", autoplay=True)
                    except:
                        pass
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with col_der:
    with st.container(border=True):
        st.markdown(f"<div class='header-box'>Controles</div>", unsafe_allow_html=True)
        if st.button(f"{'🔊 Voz ON' if st.session_state.voz_activa else '🔇 Voz OFF'}", use_container_width=True):
            st.session_state.voz_activa = not st.session_state.voz_activa
            st.rerun()
        tema_sel = st.selectbox("Color", ["purple","blue","green","orange"], index=["purple","blue","green","orange"].index(st.session_state.tema))
        if tema_sel != st.session_state.tema:
            st.session_state.tema = tema_sel
            st.rerun()
        st.divider()
        st.markdown(f"<div class='header-box'>Chat History</div>", unsafe_allow_html=True)
        if len(st.session_state.historial) == 0:
            st.markdown("<div style='background:white; border:2px dashed #999; border-radius:10px; padding:20px; text-align:center;'><b style='font-weight:900; color:#222;'>En blanco</b><br>Aquí aparecerán tus chats</div>", unsafe_allow_html=True)
        else:
            for h in st.session_state.historial[:8]:
                st.markdown(f"<div style='background:white; border:2px solid #222; border-radius:10px; padding:8px; margin-bottom:8px;'><b style='font-weight:900; color:#111;'>💬 {h}</b></div>", unsafe_allow_html=True)
