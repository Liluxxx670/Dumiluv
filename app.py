import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
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
    st.session_state.voz_activa = True
if "show_notas" not in st.session_state:
    st.session_state.show_notas = False
if "conv_id" not in st.session_state:
    st.session_state.conv_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

TEMAS = {
    "purple": {"bg": "#c7a8f0", "window": "#f9d6e8", "header": "#ffc2dd", "chat": "#ffe6f0", "side": "#e8d5ff", "card": "#ffd6eb"},
    "blue": {"bg": "#a9d0ff", "window": "#d6ecff", "header": "#7dd3fc", "chat": "#e0f2fe", "side": "#c7e5ff", "card": "#bae6fd"},
    "orange": {"bg": "#ffcf8a", "window": "#fff0c7", "header": "#fcd34d", "chat": "#fef3c7", "side": "#ffe7a8", "card": "#fde68a"},
    "green": {"bg": "#a0e9b0", "window": "#d1fae5", "header": "#6ee7b7", "chat": "#d1fae5", "side": "#b9f5d0", "card": "#a7f3d0"},
}
C = TEMAS[st.session_state.tema]
ROSITA = "#f9a8d4"

st.markdown(f"""
<style>
.stApp {{background: {C['bg']} !important;}}
header, footer {{visibility:hidden;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{background: transparent !important; border: none !important; box-shadow: none !important;}}
div[data-testid="stChatMessage"] {{background: white !important; border: 2.5px solid #4a2c5e !important; border-radius: 16px !important; box-shadow: 3px 3px 0 #4a2c5e !important;}}
div[data-testid="stChatMessage"] p {{color: #000000 !important; font-weight: 600;}}
div[data-testid="stButton"] > button {{background: {ROSITA} !important; color: #000000 !important; border: 3px solid #4a2c5e !important; border-radius: 12px !important; font-weight: 900 !important; box-shadow: 3px 3px 0 #4a2c5e !important;}}
div[data-testid="stButton"] > button * {{color: #000000 !important;}}
div[data-testid="stChatInput"] {{background: white !important; border: 3px solid #4a2c5e !important; border-radius: 18px !important; box-shadow: 4px 4px 0 #4a2c5e !important;}}
</style>
""", unsafe_allow_html=True)

if not st.session_state.usuario:
    st.markdown(f"<div style='background:{C['window']}; border:4px solid #4a2c5e; border-radius:20px; padding:20px; text-align:center; font-weight:900; box-shadow:6px 6px 0 #4a2c5e; color:#4a2c5e;'>⭐ Dumiluv - Entrar ✨</div>", unsafe_allow_html=True)
    with st.container():
        tab1, tab2 = st.tabs(["Entrar", "Crear"])
        data = load_data()
        with tab1:
            u = st.text_input("Usuario", key="lu")
            p = st.text_input("Contrasena", type="password", key="lp")
            if st.button("Entrar", use_container_width=True):
                if u in data and data[u].get("pass") == hash_pass(p):
                    st.session_state.usuario = u
                    st.session_state.nombre_display = data[u].get("display", u)
                    st.session_state.conv_id = None
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Mal usuario")
        with tab2:
            new_u = st.text_input("Usuario nuevo", key="nu")
            new_display = st.text_input("Como te digo?", key="nd")
            new_p = st.text_input("Contrasena", type="password", key="np")
            new_p2 = st.text_input("Repite", type="password", key="np2")
            if st.button("Crear y Entrar", use_container_width=True):
                if not re.match(r"^[a-zA-Z0-9._]+$", new_u):
                    st.error("Solo letras, numeros, . _")
                elif new_u in data:
                    st.error("Ya existe")
                elif new_p != new_p2:
                    st.error("No coinciden")
                else:
                    data[new_u] = {"pass": hash_pass(new_p), "display": new_display or new_u, "avatar_path": "", "convs": {}}
                    save_data(data)
                    st.session_state.usuario = new_u
                    st.session_state.nombre_display = new_display or new_u
                    st.rerun()
    st.stop()

data = load_data()
if st.session_state.usuario not in data:
    data[st.session_state.usuario] = {"pass": "", "display": st.session_state.usuario, "avatar_path": "", "convs": {}}
if "convs" not in data[st.session_state.usuario]:
    data[st.session_state.usuario]["convs"] = {}
    save_data(data)

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
    if "convs" not in d[st.session_state.usuario]:
        d[st.session_state.usuario]["convs"] = {}
    d[st.session_state.usuario]["convs"][st.session_state.conv_id] = {"title": primer, "date": hoy, "messages": st.session_state.messages}
    save_data(d)

api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)
MODELO = "openai/gpt-oss-20b"

SYSTEM_PROMPT = f"""
Eres Dumiluv, tutora de ALGEBRA para {st.session_state.nombre_display}.
NUNCA des respuesta directa. Si dice 4+4 no digas 8. Guia.
Si dice NOSE, NO SE, PISTA, AYUDA, EXPLICAME: Dale pista + explicacion chiquita + pregunta mas facil. Ejemplo: Si manzana es x, pera que cuesta 2 mas es x+2, entonces 3 peras es 3(x+2). Y 2 manzanas como queda?
Solo algebra. Si no es algebra di: Lo siento {st.session_state.nombre_display} solo puedo ayudarte con algebra.
PROHIBIDO LaTeX: escribe x^2, C2H6 + O2 -> 4 CO2 + 6 H2O. Nunca $. Corta kawaii.
"""

with st.container():
    st.markdown(f"<div style='background:{C['header']}; border:4px solid #4a2c5e; border-radius:18px; padding:10px; text-align:center; font-weight:900; box-shadow:5px 5px 0 #4a2c5e; color:#4a2c5e;'>Dumiluv - {st.session_state.nombre_display}</div>", unsafe_allow_html=True)
    st.write("")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        if st.button("Ajustes", use_container_width=True):
            st.session_state.show_ajustes = not st.session_state.show_ajustes
            st.rerun()
    with c2:
        if st.button("Nuevo", use_container_width=True):
            nueva_conversacion()
            st.rerun()
    with c3:
        if st.button("Notas", use_container_width=True):
            st.session_state.show_notas = not st.session_state.show_notas
            st.rerun()
    with c4:
        if st.button("Voz ON" if st.session_state.voz_activa else "Voz OFF", use_container_width=True):
            st.session_state.voz_activa = not st.session_state.voz_activa
            st.rerun()
    with c5:
        if st.button("Salir", use_container_width=True):
            st.session_state.usuario=""
            st.rerun()

if st.session_state.show_ajustes:
    with st.container():
        st.markdown("<div style='background:white; border:3px solid #4a2c5e; border-radius:14px; padding:12px; box-shadow:4px 4px 0 #4a2c5e;'><b>Ajustes - Temas</b></div>", unsafe_allow_html=True)
        if os.path.exists("dumiluv.png"):
            st.image("dumiluv.png", width=120)
        nuevo_nombre = st.text_input("Como te digo?", value=st.session_state.nombre_display)
        sel = st.selectbox("Color tema", ["purple","blue","orange","green"], index=["purple","blue","orange","green"].index(st.session_state.tema))
        if sel != st.session_state.tema:
            st.session_state.tema = sel
            st.rerun()
        up = st.file_uploader("Foto galeria", type=["png","jpg","jpeg"])
        if up:
            ext = up.name.split(".")[-1]
            path = os.path.join(AVATAR_FOLDER, f"{st.session_state.usuario}.{ext}")
            with open(path, "wb") as f:
                f.write(up.getbuffer())
            d = load_data()
            d[st.session_state.usuario]["avatar_path"] = path
            d[st.session_state.usuario]["display"] = nuevo_nombre
            save_data(d)
            st.session_state.nombre_display = nuevo_nombre
            st.rerun()
        if st.button("Guardar nombre"):
            d = load_data()
            d[st.session_state.usuario]["display"] = nuevo_nombre
            save_data(d)
            st.session_state.nombre_display = nuevo_nombre
            st.rerun()

left, center, right = st.columns([1, 2.2, 1])

with left:
    with st.container():
        st.markdown(f"<div style='background:{C['side']}; border:4px solid #4a2c5e; border-radius:18px; padding:12px; box-shadow:5px 5px 0 #4a2c5e; text-align:center;'>", unsafe_allow_html=True)
        if os.path.exists("dumiluv.png"):
            st.image("dumiluv.png", use_container_width=True)
        else:
            st.markdown("<div style='font-size:70px; text-align:center;'>💜</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#000; font-weight
