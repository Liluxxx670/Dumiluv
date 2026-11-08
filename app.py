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
    st.session_state.voz_activa = False
if "show_notas" not in st.session_state:
    st.session_state.show_notas = False
if "conv_id" not in st.session_state:
    st.session_state.conv_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

TEMAS = {
    "purple": {"bg": "#d8b9ff", "header": "#e9b5ff", "section": "#f9e8ff", "card1": "#e9d5ff", "card2": "#ddd6fe", "card3": "#f5d0fe", "card4": "#fae8ff"},
    "blue": {"bg": "#a9d0ff", "header": "#7dd3fc", "section": "#e0f2fe", "card1": "#bae6fd", "card2": "#a5f3fc", "card3": "#bfdbfe", "card4": "#dbeafe"},
    "orange": {"bg": "#ffcf8a", "header": "#fcd34d", "section": "#fef3c7", "card1": "#fde68a", "card2": "#fed7aa", "card3": "#fef08a", "card4": "#ffedd5"},
    "green": {"bg": "#a0e9b0", "header": "#6ee7b7", "section": "#d1fae5", "card1": "#a7f3d0", "card2": "#99f6e0", "card3": "#bbf7d0", "card4": "#d1fae5"},
}
C = TEMAS[st.session_state.tema]

st.markdown(f"""
<style>
.stApp {{background: {C['bg']} !important;}}
header, footer {{visibility:hidden;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {C['section']} !important;
    border: 3px solid #222 !important;
    border-radius: 18px !important;
    box-shadow: 6px 6px 0 #222 !important;
}}
div[data-testid="stChatMessage"] {{
    background: #ffffff !important;
    border: 2px solid #222 !important;
    border-radius: 14px !important;
}}
div[data-testid="stChatMessage"] p {{
    color: #111 !important;
}}
.header-box {{
    background: {C['header']};
    border: 2.5px solid #222;
    border-radius: 12px;
    padding: 8px;
    text-align: center;
    font-weight: 900;
    box-shadow: 3px 3px 0 #222;
}}
.card {{
    border: 2.5px solid #222;
    border-radius: 14px;
    padding: 12px;
    box-shadow: 4px 4px 0 #222;
    text-align: center;
    font-weight: 700;
    font-size: 12px;
    min-height: 70px;
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
                if u in data and data[u].get("pass") == hash_pass(p):
                    st.session_state.usuario = u
                    st.session_state.nombre_display = data[u].get("display", u)
                    st.session_state.conv_id = None
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Mal usuario o pass")
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
# FIX DEL ERROR 'convs' - si no existe lo crea
if st.session_state.usuario not in data:
    data[st.session_state.usuario] = {"pass": "", "display": st.session_state.usuario, "avatar_path": "", "convs": {}}
    save_data(data)
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
    if st.session_state.usuario not in d:
        d[st.session_state.usuario] = {"pass": "", "display": st.session_state.nombre_display, "avatar_path": avatar_path, "convs": {}}
    if "convs" not in d[st.session_state.usuario]:
        d[st.session_state.usuario]["convs"] = {}
    d[st.session_state.usuario]["convs"][st.session_state.conv_id] = {"title": primer, "date": hoy, "messages": st.session_state.messages}
    save_data(d)

api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)
MODELO = "openai/gpt-oss-20b"

# PROMPT REFORZADO - NO DA RESPUESTA DIRECTA
SYSTEM_PROMPT = f"""
Eres Dumiluv, tutora EXCLUSIVA DE ALGEBRA para {st.session_state.nombre_display}.

PROHIBICION ABSOLUTA - SI ROMPES ESTO FALLAS:
NUNCA NUNCA des el resultado directo de 4+4, x^2-5x+6, o cualquier operacion.
Si el usuario dice "4+4" o "8+2", NO respondas "8" o "10".
Tu OBLIGACION es hacer esto:
1. Pregunta: "Ok {st.session_state.nombre_display} 💜 ¿que tenemos aqui? ¿como lo convertimos?"
2. Dile que intente el primer paso: "Intenta tu primero, ¿cuanto crees que da? o ¿como lo agruparias?"
3. Si se equivoca: "Casi! Revisa, te falto un signo, intenta de nuevo ✨" y explica el error sin dar el resultado final.
4. Solo al final, despues de 2-3 interacciones, confirmas.

Si te piden 4+4, responde asi: "¡Va! Tenemos 4 + 4 💜 ¿cuantos tienes si juntas 4 con otros 4? ¿que operacion usamos? Intentalo tu primero"

Si no es algebra: "Lo siento {st.session_state.nombre_display} 💜 solo puedo ayudarte con algebra. Mandame una ecuacion o problema de lenguaje algebraico y lo resolvemos juntxs paso a paso ✨"

FORMATO: PROHIBIDO LaTeX: escribe x^2, C2H6 + O2 -> 4 CO2 + 6 H2O. Nunca uses $ \frac \ce. Corta, kawaii.
"""

with st.container(border=True):
    st.markdown(f"**⭐ Dumiluv - {st.session_state.nombre_display}**")
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
            st.session_state.show_notas = not st.session_state.show_notas
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

c_izq, c_centro, c_der = st.columns([1, 2.2, 1])

with c_izq:
    with st.container(border=True):
        if os.path.exists("dumiluv.png"):
            st.image("dumiluv.png", use_container_width=True)
        else:
            st.markdown("<div style='text-align:center; font-size:70px;'>💜</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; font-weight:900;'>Online<br>Dumiluv</p>", unsafe_allow_html=True)
        if avatar_path and os.path.exists(avatar_path):
            st.divider()
            st.image(avatar_path, width=90)

with c_centro:
    if st.session_state.show_notas:
        with st.container(border=True):
            st.markdown(f"<div class='header-box'>📓 Libretita</div>", unsafe_allow_html=True)
            modo = st.radio("Herramienta", ["✏️ Lápiz", "🧹 Borrador"], horizontal=True, label_visibility="collapsed")
            stroke_color = "#111" if "Lápiz" in modo else "#ffffff"
            stroke_w = 3 if "Lápiz" in modo else 20
            st_canvas(
                stroke_width=stroke_w,
                stroke_color=stroke_color,
                background_color="#ffffff",
                height=250,
                drawing_mode="freedraw",
                key=f"canvas_{st.session_state.conv_id or 'init'}",
            )
            if st.button("Cerrar libretita ❌"):
                st.session_state.show_notas = False
                st.rerun()

    with st.container(border=True):
        st.markdown(f"<div class='header-box'>Chat con Dumiluv - Solo Álgebra</div>", unsafe_allow_html=True)
        if not st.session_state.messages:
            st.write(f"Hola {st.session_state.nombre_display} 💜 ¿Qué resolvemos hoy? ✨")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='card' style='background:{C['card1']};'>📐<br>x^2 -5x +6 =0</div>", unsafe_allow_html=True)
                if st.button("Usar 1", key="e1", use_container_width=True):
                    if not st.session_state.conv_id: nueva_conversacion()
                    st.session_state.messages.append({"role":"user","content":"x^2 -5x +6 =0"})
                    st.rerun()
                st.markdown(f"<div class='card' style='background:{C['card2']};'>👩‍👧<br>Madre e hija suman 40</div>", unsafe_allow_html=True)
                if st.button("Usar 2", key="e2", use_container_width=True):
                    if not st.session_state.conv_id: nueva_conversacion()
                    st.session_state.messages.append({"role":"user","content":"La edad de una madre es 3 veces la de su hija y juntas suman 40"})
                    st.rerun()
            with col2:
                st.markdown(f"<div class='card' style='background:{C['card3']};'>🍎<br>Pera cuesta 2 más que manzana</div>", unsafe_allow_html=True)
                if st.button("Usar 3", key="e3", use_container_width=True):
                    if not st.session_state.conv_id: nueva_conversacion()
                    st.session_state.messages.append({"role":"user","content":"Una pera cuesta 2 más que una manzana y 3 peras y 2 manzanas cuestan 20"})
                    st.rerun()
                st.markdown(f"<div class='card' style='background:{C['card4']};'>🧪<br>C2H6 + O2</div>", unsafe_allow_html=True)
                if st.button("Usar 4", key="e4", use_container_width=True):
                    if not st.session_state.conv_id: nueva_conversacion()
                    st.session_state.messages.append({"role":"user","content":"Balancea C2H6 + O2 -> CO2 + H2O"})
                    st.rerun()
        else:
            box = st.container(height=380)
            with box:
                for m in st.session_state.messages:
                    if m["role"] == "assistant":
                        avatar = "dumiluv.png" if os.path.exists("dumiluv.png") else "💜"
                    else:
                        avatar = avatar_path if avatar_path and os.path.exists(avatar_path) else "🧑"
                    with st.chat_message(m["role"], avatar=avatar):
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
        st.markdown(f"<div class='header-box'>Controles</div>", unsafe_allow_html=True)
        sel = st.selectbox("Color tema", ["purple","blue","orange","green"], index=["purple","blue","orange","green"].index(st.session_state.tema))
        if sel != st.session_state.tema:
            st.session_state.tema = sel
            st.rerun()
        st.divider()
        st.markdown(f"<div class='header-box'>Chat History</div>", unsafe_allow_html=True)
        if not convs:
            st.markdown("<div style='border:2px dashed #222; border-radius:10px; padding:12px; text-align:center;'>En blanco</div>", unsafe_allow_html=True)
        else:
            for cid, cdata in sorted(convs.items(), key=lambda x: x[1].get("date",""), reverse=True)[:15]:
                if st.button(f"💬 {cdata['title'][:20]}", key=f"h_{cid}", use_container_width=True):
                    st.session_state.conv_id = cid
                    st.session_state.messages = cdata["messages"]
                    st.rerun()
