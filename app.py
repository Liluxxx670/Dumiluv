import streamlit as st
from groq import Groq
from gtts import gTTS
import json, os, re, hashlib, datetime, uuid

st.set_page_config(page_title="Dumiluv", page_icon="💗", layout="wide")

USERS_FILE = "users.json"
AVATAR_FOLDER = "avatars"
os.makedirs(AVATAR_FOLDER, exist_ok=True)

def load_data():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}
def save_data(d):
    with open(USERS_FILE, "w") as f:
        json.dump(d, f)
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

if "tema" not in st.session_state:
    st.session_state.tema = "purple"
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "nombre_display" not in st.session_state:
    st.session_state.nombre_display = ""
if "show_ajustes" not in st.session_state:
    st.session_state.show_ajustes = False
if "voz_activa" not in st.session_state:
    st.session_state.voz_activa = False
if "conv_id" not in st.session_state:
    st.session_state.conv_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# COLORES QUE ME PEDISTE EN EL AUDIO
# Fondo más oscuro, secciones más claritas, barrita rosita pastel
BG_OSCURO = "#7c4ed4" # fondo morado oscuro
SECCION_CLARA = "#f3e8ff" # cuadraditos claritos para que resalten
ROSITA_PASTEL = "#f9a8d4" # barrita de arriba rosita pastel
MORADITO_BOTON = "#e9a5ff" # botones moraditos

st.markdown(f"""
<style>
.stApp {{
    background: {BG_OSCURO} !important;
    background-image: radial-gradient(#9f7aea 2px, transparent 2px);
    background-size: 28px 28px;
}}
header, footer {{visibility:hidden;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {SECCION_CLARA} !important;
    border: 3px solid #222 !important;
    border-radius: 18px !important;
    box-shadow: 6px 6px 0 #222 !important;
}}
/* BOTONES ROSITA PASTEL - YA NO NEGROS */
div[data-testid="stButton"] button {{
    background: {ROSITA_PASTEL} !important;
    color: #4c1d95 !important;
    border: 2.5px solid #222 !important;
    border-radius: 14px !important;
    font-weight: 900 !important;
    box-shadow: 4px 4px 0 #222 !important;
}}
div[data-testid="stButton"] button:hover {{
    background: #fbcfe8 !important;
}}
.header-box {{
    background: {MORADITO_BOTON};
    border: 2.5px solid #222;
    border-radius: 12px;
    padding: 8px;
    text-align: center;
    font-weight: 900;
    box-shadow: 3px 3px 0 #222;
    color: #4c1d95;
}}
.top-bar {{
    background: {ROSITA_PASTEL} !important;
    border: 2.5px solid #222;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 5px 5px 0 #222;
}}
</style>
""", unsafe_allow_html=True)

if not st.session_state.usuario:
    st.markdown(f"<div class='header-box'>⭐ Dumiluv - Entrar ✨</div>", unsafe_allow_html=True)
    with st.container(border=True):
        tab1, tab2 = st.tabs(["🔐 Entrar", "✨ Crear"])
        data = load_data()
        with tab1:
            u = st.text_input("Usuario", key="lu")
            p = st.text_input("Contraseña", type="password", key="lp")
            if st.button("Entrar 💜", use_container_width=True):
                if u in data and data[u]["pass"] == hash_pass(p):
                    st.session_state.usuario = u
                    st.session_state.nombre_display = data[u].get("display", u)
                    st.session_state.conv_id = None
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Mal")
        with tab2:
            new_u = st.text_input("Usuario nuevo", key="nu")
            new_display = st.text_input("¿Cómo te digo?", key="nd")
            new_p = st.text_input("Contraseña", type="password", key="np")
            new_p2 = st.text_input("Repite", type="password", key="np2")
            if st.button("Crear y Entrar ✨", use_container_width=True):
                if not re.match(r"^[a-zA-Z0-9._]+$", new_u):
                    st.error("Solo letras, números, . _")
                elif new_u in data:
                    st.error("Ya existe")
                elif new_p != new_p2:
                    st.error("No coinciden")
                else:
                    data[new_u] = {"pass": hash_pass(new_p), "display": new_display or new_u, "avatar_path": "", "convs": {}}
                    save_data(data)
                    st.session_state.usuario = new_u
                    st.session_state.nombre_display = new_display or new_u
                    st.session_state.conv_id = None
                    st.session_state.messages = []
                    st.rerun()
    st.stop()

data = load_data()
user_info = data.get(st.session_state.usuario, {})
convs = user_info.get("convs", {})
avatar_path = user_info.get("avatar_path", "")

def nueva_conversacion():
    cid = str(uuid.uuid4())[:8]
    st.session_state.conv_id = cid
    st.session_state.messages = []
    return cid

def guardar_conversacion():
    if not st.session_state.messages or not st.session_state.conv_id:
        return
    primer = next((m["content"][:30] for m in st.session_state.messages if m["role"]=="user"), "Nueva charla")
    hoy = datetime.datetime.now().strftime("%d/%m %H:%M")
    d = load_data()
    d[st.session_state.usuario]["convs"][st.session_state.conv_id] = {"title": primer, "date": hoy, "messages": st.session_state.messages}
    save_data(d)

api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)
MODELO = "openai/gpt-oss-20b"

SYSTEM_PROMPT = f"""
Eres Dumiluv, tutora de ALGEBRA exclusiva.
Estudiante: {st.session_state.nombre_display}
SOLO ALGEBRA y lenguaje algebraico general.
Si no es algebra di: Lo siento {st.session_state.nombre_display} 💜 solo algebra.
PROHIBIDO LaTeX: escribe x^2, C2H6 + O2 -> 4 CO2 + 6 H2O.
NO REGALES RESPUESTA: guia paso a paso.
"""

# BARRA DE ARRIBA ROSITA PASTEL - YA NO NEGRA
with st.container(border=True):
    st.markdown(f"<div class='top-bar'>⭐ <b>Dumiluv - {st.session_state.nombre_display}</b></div>", unsafe_allow_html=True)
    st.write("")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("⚙️ Ajustes", use_container_width=True):
            st.session_state.show_ajustes = not st.session_state.show_ajustes
            st.rerun()
    with col2:
        if st.button("➕ Nuevo chat", use_container_width=True):
            nueva_conversacion()
            st.rerun()
    with col3:
        if st.button("📝 Notas", use_container_width=True):
            st.session_state.show_notas = not getattr(st.session_state, 'show_notas', False)
            st.rerun()
    with col4:
        if st.button(f"{'🔊 Voz ON' if st.session_state.voz_activa else '🔇 Voz OFF'}", use_container_width=True):
            st.session_state.voz_activa = not st.session_state.voz_activa
            st.rerun()
    with col5:
        if st.button("Salir", use_container_width=True):
            st.session_state.usuario=""
            st.rerun()

if st.session_state.show_ajustes:
    with st.container(border=True):
        st.markdown(f"<div class='header-box'>⚙️ Ajustes - Tu Perfil</div>", unsafe_allow_html=True)
        if os.path.exists("dumiluv.png"):
            st.image("dumiluv.png", width=120)
        nuevo_nombre = st.text_input("¿Cómo quieres que te diga?", value=st.session_state.nombre_display)
        uploaded = st.file_uploader("📸 Editar foto - Galería", type=["png","jpg","jpeg"])
        if uploaded:
            ext = uploaded.name.split(".")[-1]
            path = os.path.join(AVATAR_FOLDER, f"{st.session_state.usuario}.{ext}")
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())
            d = load_data()
            d[st.session_state.usuario]["avatar_path"] = path
            d[st.session_state.usuario]["display"] = nuevo_nombre
            save_data(d)
            st.session_state.nombre_display = nuevo_nombre
            st.success("Foto guardada 💜")
            st.rerun()
        if st.button("Guardar nombre"):
            d = load_data()
            d[st.session_state.usuario]["display"] = nuevo_nombre
            save_data(d)
            st.session_state.nombre_display = nuevo_nombre
            st.rerun()
        if st.button("Cerrar Ajustes"):
            st.session_state.show_ajustes = False
            st.rerun()

c_izq, c_centro, c_der = st.columns([1, 2, 1])

with c_izq:
    with st.container(border=True):
        if os.path.exists("dumiluv.png"):
            st.image("dumiluv.png", use_container_width=True)
        else:
            st.markdown("<div style='text-align:center; font-size:70px;'>💜</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; font-weight:900;'>Online<br>{st.session_state.nombre_display}</p>", unsafe_allow_html=True)
        if avatar_path and os.path.exists(avatar_path):
            st.divider()
            st.write("Tú:")
            st.image(avatar_path, width=90)
        st.divider()
        st.markdown("**💜 Fallas?**<br>7001467@etrr.edu.mx<br>7001464@etrr.edu.mx<br>7001451@etrr.edu.mx<br>7001529@etrr.edu.mx", unsafe_allow_html=True)

with c_centro:
    with st.container(border=True):
        st.markdown("<div class='header-box'>Chat con Dumiluv - Solo Álgebra</div>", unsafe_allow_html=True)
        box = st.container(height=400)
        with box:
            if not st.session_state.messages:
                st.write(f"Hola {st.session_state.nombre_display} 💜 Mándame una ecuación o problema de lenguaje algebraico ✨")
            else:
                for m in st.session_state.messages:
                    with st.chat_message(m["role"]):
                        st.markdown(m["content"])

    with st.container(border=True):
        prompt = st.chat_input("Type a message...")
        if prompt:
            if not st.session_state.conv_id:
                nueva_conversacion()
            st.session_state.messages.append({"role":"user","content":prompt})
            try:
                msgs = [{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.messages
                comp = client.chat.completions.create(model=MODELO, messages=msgs, temperature=0.6)
                full = comp.choices[0].message.content.replace("$","")
                st.session_state.messages.append({"role":"assistant","content":full})
                guardar_conversacion()
                if st.session_state.voz_activa:
                    try:
                        tts = gTTS(text=full[:350], lang='es')
                        tts.save("voz.mp3")
                        st.audio("voz.mp3", autoplay=True)
                    except:
                        pass
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with c_der:
    with st.container(border=True):
        st.markdown("<div class='header-box'>Chat History</div>", unsafe_allow_html=True)
        if not convs:
            st.markdown("<div style='border:2px dashed #222; border-radius:10px; padding:12px; text-align:center;'>En blanco</div>", unsafe_allow_html=True)
        else:
            for cid, cdata in sorted(convs.items(), key=lambda x: x[1].get("date",""), reverse=True)[:15]:
                if st.button(f"💬 {cdata['title'][:20]}", key=f"h_{cid}", use_container_width=True):
                    st.session_state.conv_id = cid
                    st.session_state.messages = cdata["messages"]
                    st.rerun()
                st.caption(cdata["date"])
