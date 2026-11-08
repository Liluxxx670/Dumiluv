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
def clean_for_voice(text):
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    t = t.replace("*", "").replace("#", "").replace("_", "")
    return t[:280]

if "tema" not in st.session_state: st.session_state.tema = "purple"
if "usuario" not in st.session_state: st.session_state.usuario = ""
if "nombre_display" not in st.session_state: st.session_state.nombre_display = ""
if "show_ajustes" not in st.session_state: st.session_state.show_ajustes = False
if "voz_activa" not in st.session_state: st.session_state.voz_activa = True
if "show_notas" not in st.session_state: st.session_state.show_notas = False
if "conv_id" not in st.session_state: st.session_state.conv_id = None
if "messages" not in st.session_state: st.session_state.messages = []
if "notas_pages" not in st.session_state: st.session_state.notas_pages = [{"id":"1","title":"Hoja 1","text":""}]
if "notas_idx" not in st.session_state: st.session_state.notas_idx = 0
if "input_text" not in st.session_state: st.session_state.input_text = ""

TEMAS = {
    "purple": {"bg": "#c7a8f0", "window": "#f9d6e8", "header": "#ffc2dd", "chat": "#ffe6f0", "side": "#e8d5ff", "card": "#ffd6eb", "btn":"#f9a8d4", "strong":"#7c3aed"},
    "blue": {"bg": "#a9d0ff", "window": "#d6ecff", "header": "#7dd3fc", "chat": "#e0f2fe", "side": "#c7e5ff", "card": "#bae6fd", "btn":"#7dd3fc", "strong":"#0ea5e9"},
    "orange": {"bg": "#ffcf8a", "window": "#fff0c7", "header": "#fcd34d", "chat": "#fef3c7", "side": "#ffe7a8", "card": "#fde68a", "btn":"#fcd34d", "strong":"#d97706"},
    "green": {"bg": "#a0e9b0", "window": "#d1fae5", "header": "#6ee7b7", "chat": "#d1fae5", "side": "#b9f5d0", "card": "#a7f3d0", "btn":"#6ee7b7", "strong":"#059669"},
}
C = TEMAS[st.session_state.tema]

st.markdown(f"""
<style>
.stApp {{background: {C["bg"]} !important;}}
header, footer, #MainMenu {{visibility:hidden !important; display:none !important;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{background: transparent !important; border: none !important; box-shadow: none !important;}}
.stButton > button, div[data-testid="stButton"] > button {{background: {C["btn"]} !important; color: #000000 !important; border: 3px solid #4a2c5e !important; border-radius: 12px !important; font-weight: 900 !important; box-shadow: 3px 3px 0 #4a2c5e !important;}}
.stButton > button * {{color: #000000 !important;}}
div[data-testid="stTextInput"] > div, div[data-testid="stTextArea"] > div, div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] > div, div[data-baseweb="select"], div[data-testid="stFileUploader"] > div {{background: white !important; border: 3px solid #4a2c5e !important; border-radius: 12px !important; box-shadow: 3px 3px 0 #4a2c5e !important; color: #000000 !important;}}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] *, div[data-testid="stFileUploader"] * {{color: #000000 !important; font-weight: 800 !important; font-size: 14px !important;}}
div[data-testid="stTextInput"] label, div[data-testid="stTextArea"] label, div[data-testid="stSelectbox"] label, div[data-testid="stFileUploader"] label {{color: #000000 !important; font-weight: 900 !important;}}
div[data-testid="stAudio"] {{background: white !important; border: 3px solid #4a2c5e !important; border-radius: 14px !important; box-shadow: 3px 3px 0 #4a2c5e !important; padding: 5px !important;}}
audio {{width: 100%; border-radius: 10px;}}
.chat-container {{background: white; border: 3px solid #4a2c5e; border-radius: 16px; padding: 12px; min-height: 380px; max-height: 420px; overflow-y: auto;}}
.chat-row {{display:flex; width:100%; margin-bottom:10px;}}
.chat-row.user {{justify-content: flex-end;}}
.chat-row.assistant {{justify-content: flex-start;}}
.bubble {{max-width: 75%; padding: 10px 14px; border-radius: 18px; border: 2.5px solid #4a2c5e; box-shadow: 2px 2px 0 #4a2c5e; font-weight: 700; color: #000000; word-wrap: break-word; line-height: 1.35; font-size: 13.5px;}}
.bubble.user {{background: {C["card"]} ; border-bottom-right-radius: 4px;}}
.bubble.assistant {{background: #ffffff; border-bottom-left-radius: 4px;}}
.bubble b {{color: {C["strong"]} !important; font-weight: 900 !important;}}
.input-rosa {{background: white; border: 3px solid #4a2c5e; border-radius: 14px; padding: 6px; box-shadow: 3px 3px 0 #4a2c5e;}}
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
            if st.button("Entrar ✨", use_container_width=True):
                found = None
                for k in data.keys():
                    if k.lower() == u.lower():
                        found = k
                        break
                if found and data[found].get("pass") == hash_pass(p):
                    st.session_state.usuario = found
                    st.session_state.nombre_display = data[found].get("display", found)
                    st.session_state.conv_id = None
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Usuario no existe")
        with tab2:
            new_u = st.text_input("Usuario nuevo (unico)", key="nu")
            new_display = st.text_input("Como te digo?", key="nd")
            new_p = st.text_input("Contrasena", type="password", key="np")
            new_p2 = st.text_input("Repite", type="password", key="np2")
            if st.button("Crear y Entrar 💖", use_container_width=True):
                if not re.match(r"^[a-zA-Z0-9._]+$", new_u):
                    st.error("Solo letras, numeros, . _")
                elif any(k.lower() == new_u.lower() for k in data.keys()):
                    st.error("Ese usuario ya existe! Elige otro 💜")
                elif len(new_u) < 3:
                    st.error("Usuario muy cortito")
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

nombre = st.session_state.nombre_display
SYSTEM_PROMPT = "Eres Dumiluv, tutora kawaii de MATEMATICAS para " + nombre + ". Aceptas TODO de matematicas: 4+67, sumas, restas, multiplicaciones, divisiones, algebra, ecuaciones, problemas. Solo rechaza si es NO matematico. NUNCA des resultado directo. Guia paso a paso. SIEMPRE explica el POR QUE con analogia simple. Ejemplo 3x + x = 4x POR QUE es como 3 manzanas + 1 manzana. Si dice NOSE, PISTA, AYUDA: responde Pista: ... Por que: ... Pregunta facil: ... No uses asteriscos. Escribe x^2, 4x=40. Max 5 lineas, kawaii."

with st.container():
    st.markdown(f"<div style='background:{C['header']}; border:4px solid #4a2c5e; border-radius:18px; padding:10px; text-align:center; font-weight:900; box-shadow:5px 5px 0 #4a2c5e; color:#4a2c5e;'>Dumiluv - {nombre} 💜</div>", unsafe_allow_html=True)
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
        st.markdown("<div style='background:white; border:3px solid #4a2c5e; border-radius:14px; padding:12px; box-shadow:4px 4px 0 #4a2c5e;'><b style='color:#000;'>Ajustes - Temas 💜</b></div>", unsafe_allow_html=True)
        st.write("")
        if os.path.exists("dumiluv.png"):
            st.image("dumiluv.png", width=120)
        nuevo_nombre = st.text_input("Como te digo?", value=st.session_state.nombre_display, key="aj_nom")
        sel = st.selectbox("Color tema", ["purple","blue","orange","green"], index=["purple","blue","orange","green"].index(st.session_state.tema), key="aj_col")
        if sel != st.session_state.tema:
            st.session_state.tema = sel
            st.rerun()
        up = st.file_uploader("Foto de galeria", type=["png","jpg","jpeg"], key="aj_foto")
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
        if st.button("Guardar nombre", key="aj_save"):
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
        st.markdown(f"<p style='color:#000; font-weight:900; font-size:13px;'>AI Assistant - Online<br>{nombre}</p>", unsafe_allow_html=True)
        if avatar_path and os.path.exists(avatar_path):
            st.image(avatar_path, width=80)
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("<div style='background:white; border:3px solid #4a2c5e; border-radius:12px; padding:8px; box-shadow:3px 3px 0 #4a2c5e;'><p style='color:#000; font-size:11px; font-weight:800; margin:0;'>Si falla:<br>7001467@etrr.edu.mx<br>7001464@etrr.edu.mx<br>7001451@etrr.edu.mx<br>7001529@etrr.edu.mx</p></div>", unsafe_allow_html=True)

with center:
    if st.session_state.show_notas:
        with st.container():
            st.markdown(f"<div style='background:white; border:3px solid #4a2c5e; border-radius:14px; padding:10px; box-shadow:4px 4px 0 #4a2c5e; margin-bottom:8px;'><b style='color:#000;'>📒 Libretita - {len(st.session_state.notas_pages)} hojas</b></div>", unsafe_allow_html=True)
            col_n1, col_n2, col_n3 = st.columns([2,1,1])
            with col_n1:
                titulos = [p["title"] for p in st.session_state.notas_pages]
                sel_page = st.selectbox("Hoja", titulos, index=st.session_state.notas_idx, key="sel_hoja2")
                st.session_state.notas_idx = titulos.index(sel_page)
            with col_n2:
                if st.button("Nueva hoja", use_container_width=True, key="btn_new2"):
                    nid = str(len(st.session_state.notas_pages)+1)
                    st.session_state.notas_pages.append({"id":nid,"title":f"Hoja {nid}","text":""})
                    st.session_state.notas_idx = len(st.session_state.notas_pages)-1
                    st.rerun()
            with col_n3:
                if st.button("Borrar hoja", use_container_width=True, key="btn_del2"):
                    if len(st.session_state.notas_pages) > 1:
                        st.session_state.notas_pages.pop(st.session_state.notas_idx)
                        st.session_state.notas_idx = max(0, st.session_state.notas_idx-1)
                        st.rerun()
            current = st.session_state.notas_pages[st.session_state.notas_idx]
            current["text"] = st.text_area("Escribe aqui", value=current["text"], height=120, key=f"txt_{current['id']}", placeholder="Escribe tus apuntes...")
            st.write("")
            modo = st.radio("Herramienta dibujo", ["Lapiz", "Borrador"], horizontal=True, label_visibility="collapsed", key=f"modo_{current['id']}")
            sc = "#111" if "Lapiz" in modo else "#ffffff"
            sw = 3 if "Lapiz" in modo else 20
            st_canvas(stroke_width=sw, stroke_color=sc, background_color="#fff", height=180, drawing_mode="freedraw", key=f"c_{current['id']}")
            if st.button("Cerrar libretita", key="btn_close2"):
                st.session_state.show_notas = False
                st.rerun()

    st.markdown(f"<div style='background:{C['chat']}; border:4px solid #4a2c5e; border-radius:18px; padding:12px; box-shadow:6px 6px 0 #4a2c5e;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{C['header']}; border:3px solid #4a2c5e; border-radius:14px; padding:8px; text-align:center; font-weight:900; color:#4a2c5e; margin-bottom:10px;'>Dumiluv 💜</div>", unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(f"<div class='chat-container'><p style='color:#000; text-align:center; font-weight:800;'>Hola {nombre}! Que resolvemos hoy? 💖<br><br>Prueba 4+67 o cualquier matematica</p></div>", unsafe_allow_html=True)
        st.write("")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("Probar: 4+67", key="e4_new", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"4+67"})
                st.rerun()
            if st.button("Madre e hija 40", key="e2_new", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"La edad de una madre es 3 veces la de su hija y juntas suman 40"})
                st.rerun()
        with cc2:
            if st.button("x^2 -5x +6 =0", key="e1_new", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"x^2 -5x +6 =0"})
                st.rerun()
            if st.button("Pera y manzana", key="e3_new", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"Una pera cuesta 2 mas que una manzana y 3 peras y 2 manzanas cuestan 20"})
                st.rerun()
    else:
        chat_html = "<div class='chat-container'>"
        for m in st.session_state.messages:
            role_class = "user" if m["role"]=="user" else "assistant"
            content = m["content"].replace("<","&lt;").replace(">","&gt;")
            content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            content = content.replace("\n", "<br>")
            chat_html += f'<div class="chat-row {role_class}"><div class="bubble {role_class}">{content}</div></div>'
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        if st.session_state.messages[-1]["role"] == "assistant" and st.session_state.voz_activa:
            try:
                texto_limpio = clean_for_voice(st.session_state.messages[-1]["content"])
                tts = gTTS(text=texto_limpio, lang='es', tld='com.mx', slow=False)
                tts.save("voz_temp.mp3")
                st.audio("voz_temp.mp3", autoplay=True)
            except:
                pass

    st.write("")
    st.markdown("<div class='input-rosa'>", unsafe_allow_html=True)
    col_in1, col_in2 = st.columns([4,1])
    with col_in1:
        user_input = st.text_input("Tu respuesta", value=st.session_state.input_text, placeholder="Escribe aqui... 💖", label_visibility="collapsed", key="main_input")
    with col_in2:
        if st.button("Enviar 💜", use_container_width=True, key="send_btn"):
            if user_input.strip():
                if not st.session_state.conv_id:
                    nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":user_input.strip()})
                st.session_state.input_text = ""
                try:
                    msgs = [{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.messages
                    comp = client.chat.completions.create(model=MODELO, messages=msgs, temperature=0.7)
                    full = comp.choices[0].message.content.replace("$","").replace("**","")
                    st.session_state.messages.append({"role":"assistant","content":full})
                    guardar_conversacion()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    with st.container():
        st.markdown(f"<div style='background:{C['header']}; border:3px solid #4a2c5e; border-radius:14px; padding:8px; text-align:center; font-weight:900; color:#4a2c5e; box-shadow:3px 3px 0 #4a2c5e; margin-bottom:8px;'>Chat History</div>", unsafe_allow_html=True)
        if not convs:
            st.markdown("<div style='background:white; border:2.5px solid #4a2c5e; border-radius:12px; padding:10px; text-align:center; box-shadow:3px 3px 0 #4a2c5e;'><p style='color:#000; font-size:12px; font-weight:800;'>En blanco</p></div>", unsafe_allow_html=True)
        else:
            for cid, cdata in sorted(convs.items(), key=lambda x: x[1].get("date",""), reverse=True)[:8]:
                if st.button(f"{cdata['date']} {cdata['title'][:20]}", key=f"h_{cid}", use_container_width=True):
                    st.session_state.conv_id = cid
                    st.session_state.messages = cdata["messages"]
                    st.rerun()
