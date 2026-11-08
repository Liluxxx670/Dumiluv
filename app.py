import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
import json, os, re, hashlib, datetime, uuid

st.set_page_config(page_title="Dumiluv", page_icon="💗", layout="wide")

USERS_FILE = "users.json"
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
if "voz_activa" not in st.session_state:
    st.session_state.voz_activa = False
if "show_notas" not in st.session_state:
    st.session_state.show_notas = False
if "conv_id" not in st.session_state:
    st.session_state.conv_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

COLORES = {
    "purple": {"bg":"#c4a3e6", "bg_dark":"#a87de0", "header":"#d896ff"},
    "blue": {"bg":"#9ec8ff", "bg_dark":"#6aa8ff", "header":"#60a5fa"},
    "green": {"bg":"#8ee8a3", "bg_dark":"#5bd67d", "header":"#4ade80"},
    "orange": {"bg":"#ffcc8a", "bg_dark":"#ffb259", "header":"#fb923c"},
}
C = COLORES[st.session_state.tema]

st.markdown(f"""
<style>
.stApp {{
    background: {C['bg_dark']} !important;
    background-image: radial-gradient({C['bg']} 2px, transparent 2px);
    background-size: 28px 28px;
}}
header, footer {{visibility:hidden;}}
* {{ color: #111 !important; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: white !important;
    border: 3px solid #222 !important;
    border-radius: 16px !important;
    box-shadow: 7px 7px 0 #222 !important;
}}
div[data-testid="stChatMessage"] {{
    background: white !important;
    border: 2.5px solid #222 !important;
    border-radius: 14px !important;
    box-shadow: 4px 4px 0 #222 !important;
}}
div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {{
    background: {C['header']} !important;
    color: #111 !important;
    border: 2.5px solid #222 !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    box-shadow: 4px 4px 0 #222 !important;
}}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
    background: white !important;
    color: #111 !important;
    border: 2.5px solid #222 !important;
}}
.header-gamer {{
    background:{C['header']};
    border:2.5px solid #222;
    border-radius:12px;
    padding:10px;
    text-align:center;
    font-weight:900;
    font-size:11px;
    box-shadow: 3px 3px 0 #222;
}}
</style>
""", unsafe_allow_html=True)

# LOGIN - AUTO ENTRA AL CREAR
if not st.session_state.usuario:
    st.markdown(f"<div class='header-gamer'>⭐ Dumiluv - Entrar ✨</div>", unsafe_allow_html=True)
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
            new_u = st.text_input("Usuario nuevo (letras, números, . _)", key="nu")
            new_display = st.text_input("¿Cómo te digo? Ej: Liz", key="nd")
            new_p = st.text_input("Contraseña", type="password", key="np")
            new_p2 = st.text_input("Repite", type="password", key="np2")
            if st.button("Crear y Entrar ✨", use_container_width=True):
                if not re.match(r"^[a-zA-Z0-9._]+$", new_u):
                    st.error("Sin signos raros")
                elif new_u in data:
                    st.error("Ya existe")
                elif new_p != new_p2:
                    st.error("No coinciden")
                elif len(new_u)<3 or len(new_p)<4:
                    st.error("Min 3 y 4")
                else:
                    data[new_u] = {"pass": hash_pass(new_p), "display": new_display or new_u, "convs": {}}
                    save_data(data)
                    st.session_state.usuario = new_u
                    st.session_state.nombre_display = new_display or new_u
                    st.session_state.conv_id = None
                    st.session_state.messages = []
                    st.rerun()
    st.stop()

# CARGAR DATA
data = load_data()
user_data = data.get(st.session_state.usuario, {"display": st.session_state.nombre_display, "convs": {}})
convs = user_data.get("convs", {})

def nueva_conversacion():
    cid = str(uuid.uuid4())[:8]
    st.session_state.conv_id = cid
    st.session_state.messages = []
    return cid

def guardar_conversacion():
    if not st.session_state.messages or not st.session_state.conv_id:
        return
    # titulo = primer mensaje del usuario
    primer_user = next((m["content"][:30] for m in st.session_state.messages if m["role"]=="user"), "Nueva charla")
    hoy = datetime.datetime.now().strftime("%d/%m %H:%M")
    data = load_data()
    if st.session_state.usuario not in data:
        data[st.session_state.usuario] = {"pass": "", "display": st.session_state.nombre_display, "convs": {}}
    data[st.session_state.usuario]["convs"][st.session_state.conv_id] = {
        "title": primer_user,
        "date": hoy,
        "messages": st.session_state.messages
    }
    save_data(data)

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Falta GROQ_API_KEY")
    st.stop()
client = Groq(api_key=api_key)

# NO USAMOS LLAMA - USAMOS GEMMA QUE SI SIRVE
MODELO = "gemma2-9b-it"

# HEADER
with st.container(border=True):
    c1,c2,c3,c4 = st.columns([2,2,1,1])
    with c1:
        st.markdown(f"**⭐ Dumiluv - {st.session_state.nombre_display}**")
    with c2:
        nn = st.text_input("Te digo:", value=st.session_state.nombre_display, label_visibility="collapsed")
        if nn and nn != st.session_state.nombre_display:
            st.session_state.nombre_display = nn
            d = load_data()
            d[st.session_state.usuario]["display"] = nn
            save_data(d)
    with c3:
        if st.button("➕ Nuevo chat", use_container_width=True):
            nueva_conversacion()
            st.rerun()
    with c4:
        if st.button("Salir", use_container_width=True):
            st.session_state.usuario=""
            st.rerun()

col_izq, col_centro, col_der = st.columns([1, 2.3, 1])

with col_izq:
    with st.container(border=True):
        st.image("dumiluv.png", width=90)
        st.markdown(f"<p style='text-align:center; font-weight:900; font-size:11px;'>Online 💗<br>{st.session_state.nombre_display}</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<b>💜 Fallas? Contacta:</b><br>📧 <b>7001467@etrr.edu.mx</b><br>📧 <b>7001464@etrr.edu.mx</b><br>📧 <b>7001451@etrr.edu.mx</b><br>📧 <b>7001529@etrr.edu.mx</b>", unsafe_allow_html=True)

with col_centro:
    with st.container(border=True):
        st.markdown(f"<div class='header-gamer'>💬 Chat con Dumiluv</div>", unsafe_allow_html=True)
        chat_box = st.container(height=380)
        with chat_box:
            if len(st.session_state.messages)==0:
                st.write(f"Hola {st.session_state.nombre_display} 💗 ¿Qué aprendemos hoy?")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("📐 x² -5x +6 =0", use_container_width=True):
                        if not st.session_state.conv_id:
                            nueva_conversacion()
                        st.session_state.messages.append({"role":"user","content":"x² -5x +6 =0"})
                        st.rerun()
                    if st.button("⚛️ 2da Ley Newton", use_container_width=True):
                        if not st.session_state.conv_id:
                            nueva_conversacion()
                        st.session_state.messages.append({"role":"user","content":"2da Ley Newton"})
                        st.rerun()
                with c2:
                    if st.button("🧪 C2H6 + O2", use_container_width=True):
                        if not st.session_state.conv_id:
                            nueva_conversacion()
                        st.session_state.messages.append({"role":"user","content":"C2H6 + O2 -> CO2 + H2O balancéala"})
                        st.rerun()
                    if st.button("📈 ¿Derivada?", use_container_width=True):
                        if not st.session_state.conv_id:
                            nueva_conversacion()
                        st.session_state.messages.append({"role":"user","content":"¿Qué es derivada?"})
                        st.rerun()
            else:
                for m in st.session_state.messages:
                    with st.chat_message(m["role"], avatar="dumiluv.png" if m["role"]=="assistant" else "🧑‍🎓"):
                        st.markdown(f"<b style='color:#111;'>{m['content']}</b>", unsafe_allow_html=True)

        with st.form("form_chat", clear_on_submit=True):
            prompt = st.text_input("Escribe...", placeholder="Type a message...", label_visibility="collapsed")
            c1,c2 = st.columns([3,1])
            with c1:
                enviar = st.form_submit_button("Enviar 💜", use_container_width=True)
            with c2:
                notas = st.form_submit_button("📝 Notas", use_container_width=True)

        if notas:
            st.session_state.show_notas = not st.session_state.show_notas
            st.rerun()

        if st.session_state.show_notas:
            st.markdown(f"<div class='header-gamer'>📓 Libretita</div>", unsafe_allow_html=True)
            modo = st.radio("Herramienta", ["✏️ Lápiz", "🧹 Borrador"], horizontal=True)
            stroke_color = "#111111" if "Lápiz" in modo else "#ffffff"
            stroke_w = 3 if "Lápiz" in modo else 20
            st_canvas(
                stroke_width=stroke_w,
                stroke_color=stroke_color,
                background_color="#ffffff",
                height=300,
                drawing_mode="freedraw",
                key=f"canvas_{st.session_state.conv_id}",
            )
            st.text_area("Apuntes:", placeholder="(x-2)(x-3)...")

        if enviar and prompt:
            if not st.session_state.conv_id:
                nueva_conversacion()
            st.session_state.messages.append({"role":"user","content":prompt})
            try:
                msgs = [{"role":"system","content":f"Eres Dumiluv, tutora algebra. Llama al usuario {st.session_state.nombre_display}. PROHIBIDO LaTeX. Guía no des respuesta directa."}] + st.session_state.messages
                comp = client.chat.completions.create(model=MODELO, messages=msgs)
                full = comp.choices[0].message.content
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

with col_der:
    with st.container(border=True):
        st.markdown(f"<div class='header-gamer'>Controles</div>", unsafe_allow_html=True)
        if st.button(f"{'🔊 Voz ON' if st.session_state.voz_activa else '🔇 Voz OFF'}", use_container_width=True):
            st.session_state.voz_activa = not st.session_state.voz_activa
            st.rerun()
        sel = st.selectbox("Color", ["purple","blue","green","orange"], index=["purple","blue","green","orange"].index(st.session_state.tema))
        if sel != st.session_state.tema:
            st.session_state.tema = sel
            st.rerun()
        st.divider()
        st.markdown(f"<div class='header-gamer'>Chat History</div>", unsafe_allow_html=True)
        if not convs:
            st.markdown("<div style='background:white; border:2px dashed #222; border-radius:10px; padding:15px; text-align:center;'><b>En blanco</b><br>Tus charlas aparecerán aquí</div>", unsafe_allow_html=True)
        else:
            # mostrar de más reciente a más antigua
            for cid, cdata in sorted(convs.items(), key=lambda x: x[1].get("date",""), reverse=True)[:15]:
                col_t, col_b = st.columns([3,1])
                with col_t:
                    if st.button(f"💬 {cdata['title'][:22]}", key=f"hist_{cid}", use_container_width=True):
                        st.session_state.conv_id = cid
                        st.session_state.messages = cdata["messages"]
                        st.rerun()
                    st.caption(cdata["date"])
                with col_b:
                    if st.button("🗑️", key=f"del_{cid}"):
                        d = load_data()
                        del d[st.session_state.usuario]["convs"][cid]
                        save_data(d)
                        if st.session_state.conv_id == cid:
                            st.session_state.conv_id = None
                            st.session_state.messages = []
                        st.rerun()
