import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
from PIL import Image
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
if "show_notas" not in st.session_state:
    st.session_state.show_notas = False
if "conv_id" not in st.session_state:
    st.session_state.conv_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

COLORES = {
    "purple": {"bg":"#b18ef0", "header":"#e3a8ff"},
    "blue": {"bg":"#8ec5ff", "header":"#7dd3ff"},
    "green": {"bg":"#8be49a", "header":"#86efac"},
    "orange": {"bg":"#ffb86a", "header":"#fdba74"},
}
C = COLORES[st.session_state.tema]

st.markdown(f"""
<style>
.stApp {{background: {C['bg']} !important;}}
header, footer {{visibility:hidden;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: white !important;
    border: 3px solid #222 !important;
    border-radius: 18px !important;
    box-shadow: 6px 6px 0 #222 !important;
}}
div[data-testid="stChatMessage"] {{
    background: white !important;
    border: 2px solid #222 !important;
    border-radius: 14px !important;
}}
.header-box {{
    background: {C['header']};
    border: 2.5px solid #222;
    border-radius: 12px;
    padding: 8px;
    text-align: center;
    font-weight: 900;
    box-shadow: 3px 3px 0 #222;
    color: #111;
}}
</style>
""", unsafe_allow_html=True)

# LOGIN - AUTO ENTRA AL CREAR
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
                    st.error("Mal usuario o pass")
        with tab2:
            new_u = st.text_input("Usuario nuevo (solo letras, números, . _)", key="nu")
            new_display = st.text_input("¿Cómo te digo? Ej: Liz", key="nd")
            new_p = st.text_input("Contraseña", type="password", key="np")
            new_p2 = st.text_input("Repite", type="password", key="np2")
            if st.button("Crear y Entrar ✨", use_container_width=True):
                if not re.match(r"^[a-zA-Z0-9._]+$", new_u):
                    st.error("Solo letras, números, . _ sin signos raros")
                elif new_u in data:
                    st.error("Ya existe")
                elif new_p != new_p2:
                    st.error("No coinciden")
                elif len(new_u)<3 or len(new_p)<4:
                    st.error("Usuario min 3, pass min 4")
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
    if st.session_state.usuario not in d:
        return
    d[st.session_state.usuario]["convs"][st.session_state.conv_id] = {"title": primer, "date": hoy, "messages": st.session_state.messages}
    save_data(d)

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Falta GROQ_API_KEY en Secrets")
    st.stop()
client = Groq(api_key=api_key)

# MODELO QUE TU ME PEDISTE, EL BUENO
MODELO = "openai/gpt-oss-20b"

# PROMPT FINAL - GENERAL + LENGUAJE ALGEBRAICO + GUIADO SIN REGALAR RESPUESTA
SYSTEM_PROMPT = f"""
Eres Dumiluv, tutora de ÁLGEBRA exclusiva para prepa.
Estudiante: {st.session_state.nombre_display}

TU OBJETIVO:
Enseñar ÁLGEBRA general, incluyendo LENGUAJE ALGEBRAICO en general. No solo el ejemplo de la madre. Tienes que entender TODO tipo de problema que se pueda convertir a álgebra.

QUE SI PUEDES RESOLVER (ALGEBRA GENERAL):
- Ecuaciones lineales, cuadráticas: x^2 -5x +6 =0, 2x+3=5
- Sistemas, factorización, simplificación
- Balanceo químico porque es ecuación: C2H6 + O2 -> CO2 + H2O
- LENGUAJE ALGEBRAICO GENERAL: TODO lo que se convierta en ecuación. Ejemplos:
    * Edades: "La edad de una madre es 3 veces la de su hija y suman 40"
    * Compras: "Una pera cuesta 2 pesos más que una manzana y 3 peras y 2 manzanas cuestan 20"
    * Números: "El doble de un número más 5 es 15"
    * Geometría algebraica: "El largo es 3 más que el ancho y el perímetro es 20"
    * Mezclas, dinero, porcentajes que se resuelvan con álgebra
  Tu trabajo es: DETECTAR, CONVERTIR A ECUACIÓN y GUIAR.

QUE NO PUEDES RESOLVER:
Si preguntan historia, biología, física sin álgebra, chisme, recetas, etc. Di:
"Lo siento {st.session_state.nombre_display} 💜 solo puedo ayudarte con álgebra. Mándame una ecuación o un problema que se pueda convertir en álgebra y lo resolvemos juntxs paso a paso ✨"

COMO TIENES QUE ENSEÑAR (ESTO ES LO MAS IMPORTANTE - NO REGALES LA RESPUESTA):
NUNCA des el resultado final directo. Tienes que hacer INTERACCIÓN SOCRÁTICA:

1. Primero pregunta: ¿Qué datos tenemos? ¿Qué incógnita ponemos? ¿x, y?
2. Luego: ¿Cómo lo convertimos en ecuación? Guíale para que ella lo escriba.
3. Luego: ¿Ahora qué paso sigue? ¿Despejamos? ¿Factorizamos? Dile que lo intente.
4. Ve paso a paso: "Resuelve primero esto" -> ella responde -> "Muy bien, ahora resuelve esto"
5. Solo al final, cuando ya hizo los pasos contigo, le confirmas el resultado explicando cómo se sacó.
6. Si se atora, dale una pista chiquita, no toda la respuesta.

FORMATO OBLIGATORIO:
- PROHIBIDO LaTeX: Nunca uses $, \, \frac, \ce, {{, }}.
- Escribe: x^2, x^3, 2x + 3 = 5, C2H6 + O2 -> 4 CO2 + 6 H2O
- Corta, dulce, kawaii, en español, máximo 4-5 líneas por mensaje, luego pregunta.
- Usa emojis pero pocos.

EJEMPLO DE COMO DEBES CONTESTAR:
Usuario: "La edad de una madre es 3 veces la de su hija y suman 40"
Tu: "¡Va {st.session_state.nombre_display}! 💜 Vamos a convertirlo en álgebra juntxs.
Paso 1: Si la hija tiene x años, ¿cuántos tiene la mamá? 🤔"
-> Esperas su respuesta
Tu: "¡Exacto! M = 3x. Ahora, si juntas suman 40, ¿cómo queda la ecuación?"
-> Esperas
Tu: "¡Siii! x + 3x = 40. Ahora resuelve primero esto: ¿cuánto es x + 3x? ✨"

Así siempre, interactivo.
"""

# TOP BAR
with st.container(border=True):
    c1,c2,c3,c4 = st.columns([2,2,1,1])
    with c1:
        st.markdown(f"**⭐ Dumiluv - {st.session_state.nombre_display}**")
    with c2:
        nn = st.text_input("Dumiluv", value=st.session_state.nombre_display, label_visibility="collapsed")
        if nn and nn != st.session_state.nombre_display:
            st.session_state.nombre_display = nn
            d = load_data()
            d[st.session_state.usuario]["display"] = nn
            save_data(d)
    with c3:
        if st.button("⚙️ Ajustes", use_container_width=True):
            st.session_state.show_ajustes = not st.session_state.show_ajustes
            st.rerun()
    with c4:
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("➕ Nuevo", use_container_width=True):
                nueva_conversacion()
                st.rerun()
        with cc2:
            if st.button("Salir", use_container_width=True):
                st.session_state.usuario=""
                st.rerun()

# AJUSTES - AQUI PONES TU FOTO DE GALERIA
if st.session_state.show_ajustes:
    with st.container(border=True):
        st.markdown(f"<div class='header-box'>⚙️ Ajustes - Perfil</div>", unsafe_allow_html=True)
        col_foto, col_datos = st.columns([1,2])
        with col_foto:
            if avatar_path and os.path.exists(avatar_path):
                st.image(avatar_path, width=130)
            else:
                st.image("dumiluv.png", width=130)
        with col_datos:
            st.write(f"Usuario: {st.session_state.usuario}")
            nuevo_nombre = st.text_input("¿Cómo quieres que te diga?", value=st.session_state.nombre_display, key="aj_nom")
            uploaded_file = st.file_uploader("📸 Editar foto - Escoge de tu galería", type=["png","jpg","jpeg"])
            if uploaded_file is not None:
                ext = uploaded_file.name.split(".")[-1]
                new_path = os.path.join(AVATAR_FOLDER, f"{st.session_state.usuario}.{ext}")
                with open(new_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                d = load_data()
                d[st.session_state.usuario]["avatar_path"] = new_path
                if nuevo_nombre:
                    d[st.session_state.usuario]["display"] = nuevo_nombre
                save_data(d)
                st.session_state.nombre_display = nuevo_nombre
                st.success("¡Foto actualizada! 💜")
                st.rerun()
            if st.button("Guardar nombre"):
                d = load_data()
                d[st.session_state.usuario]["display"] = nuevo_nombre
                save_data(d)
                st.session_state.nombre_display = nuevo_nombre
                st.success("Guardado")
                st.rerun()
