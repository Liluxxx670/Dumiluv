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

TEMAS = {
    "purple": {"bg": "#c7a8f0", "window": "#f9d6e8", "header": "#ffc2dd", "chat": "#ffe6f0", "side": "#e8d5ff", "card": "#ffd6eb", "btn":"#f9a8d4", "strong":"#7c3aed"},
    "blue": {"bg": "#a9d0ff", "window": "#d6ecff", "header": "#7dd3fc", "chat": "#e0f2fe", "side": "#c7e5ff", "card": "#bae6fd", "btn":"#7dd3fc", "strong":"#0ea5e9"},
    "orange": {"bg": "#ffcf8a", "window": "#fff0c7", "header": "#fcd34d", "chat": "#fef3c7", "side": "#ffe7a8", "card": "#fde68a", "btn":"#fcd34d", "strong":"#d97706"},
    "green": {"bg": "#a0e9b0", "window": "#d1fae5", "header": "#6ee7b7", "chat": "#d1fae5", "side": "#b9f5d0", "card": "#a7f3d0", "btn":"#6ee7b7", "strong":"#059669"},
}
C = TEMAS[st.session_state.tema]

st.markdown("""
<style>
.stApp {background: %s !important;}
header, footer {visibility:hidden;}
div[data-testid="stVerticalBlockBorderWrapper"] {background: transparent !important; border: none !important; box-shadow: none !important;}

/* BOTONES - combinan con tema, nada negro */
div[data-testid="stButton"] > button, button[kind="primary"], button[kind="secondary"] {
    background: %s !important;
    color: #000000 !important;
    border: 3px solid #4a2c5e !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    box-shadow: 3px 3px 0 #4a2c5e !important;
}
div[data-testid="stButton"] > button * {color: #000000 !important;}

/* QUITAR NEGRO DE TODO: chat input, audio, file uploader, selectbox, text input, textarea */
div[data-testid="stChatInput"] {
    background: %s !important;
    border: 3px solid #4a2c5e !important;
    border-radius: 18px !important;
    box-shadow: 4px 4px 0 #4a2c5e !important;
}
div[data-testid="stChatInput"] textarea {
    background: white !important;
    color: #000000 !important;
    font-weight: 800 !important;
    font-size: 15px !important;
}
div[data-testid="stAudio"] {
    background: white !important;
    border: 2.5px solid #4a2c5e !important;
    border-radius: 12px !important;
    box-shadow: 3px 3px 0 #4a2c5e !important;
}
div[data-testid="stFileUploader"] {
    background: white !important;
    border: 3px solid #4a2c5e !important;
    border-radius: 14px !important;
    box-shadow: 3px 3px 0 #4a2c5e !important;
}
div[data-testid="stFileUploader"] * {
    color: #000000 !important;
    font-weight: 800 !important;
}
div[data-testid="stSelectbox"] > div, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: white !important;
    border: 2.5px solid #4a2c5e !important;
    border-radius: 10px !important;
}
div[data-testid="stSelectbox"] * {
    color: #000000 !important;
    font-weight: 800 !important;
}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
    background: white !important;
    border: 2.5px solid #4a2c5e !important;
    border-radius: 10px !important;
    color: #000000 !important;
    font-weight: 800 !important;
    font-size: 15px !important;
}
div[data-testid="stTextInput"] label, div[data-testid="stTextArea"] label, div[data-testid="stSelectbox"] label, div[data-testid="stFileUploader"] label {
    color: #000000 !important;
    font-weight: 900 !important;
    font-size: 14px !important;
}

/* BUBBLES WHATSAPP - dentro del recuadro */
.chat-row {display:flex; width:100%%; margin-bottom:10px;}
.chat-row.user {justify-content: flex-end;}
.chat-row.assistant {justify-content: flex-start;}
.bubble {
    max-width: 75%%;
    padding: 10px 14px;
    border-radius: 18px;
    border: 2.5px solid #4a2c5e;
    box-shadow: 3px 3px 0 #4a2c5e;
    font-weight: 700;
    color: #000000;
    word-wrap: break-word;
    line-height: 1.4;
    font-size: 14px;
}
.bubble.user {background: %s; border-bottom-right-radius: 4px;}
.bubble.assistant {background: white; border-bottom-left-radius: 4px;}
.bubble b {color: %s !important; font-weight: 900 !important;}
</style>
""" % (C['bg'], C['btn'], C['btn'], C['card'], C['strong']), unsafe_allow_html=True)

if not st.session_state.usuario:
    st.markdown("<div style='background:%s; border:4px solid #4a2c5e; border-radius:20px; padding:20px; text-align:center; font-weight:900; box-shadow:6px 6px 0 #4a2c5e; color:#4a2c5e;'>⭐ Dumiluv - Entrar ✨</div>" % C['window'], unsafe_allow_html=True)
    with st.container():
        tab1, tab2 = st.tabs(["Entrar", "Crear"])
        data = load_data()
        with tab1:
            u = st.text_input("Usuario", key="lu")
            p = st.text_input("Contrasena", type="password", key="lp")
            if st.button("Entrar ✨", use_container_width=True):
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
            if st.button("Crear y Entrar 💖", use_container_width=True):
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

SYSTEM_PROMPT = """
Eres Dumiluv, tutora de MATEMATICAS kawaii para %s. Ayudas en TODO tipo de matematicas: aritmetica, algebra, geometria, ecuaciones, problemas de texto, fracciones, porcentajes, todo lo que sea numeros.

NUNCA rechaces un problema matematico. 4+67, 2+2, 100/5, todo lo resuelves guiando.
Solo rechaza si es claramente NO matematico (ej: historia, ingles, chismes).

TU FORMA DE ENSENAR - SOCRATICA CON POR QUE:
1. NUNCA des resultado final directo. Guia paso a paso.
2. SIEMPRE explica el POR QUE de cada operacion. Ej: "Sumamos 3x + x = 4x POR QUE? Porque ambos tienen x, es como 3 manzanas + 1 manzana = 4 manzanas" / "Dividimos entre 4 POR QUE? Porque 4x significa 4 veces x, para saber cuanto vale 1 sola x tienes que repartir en 4 partes iguales"
3. Si usuario dice NOSE, PISTA, AYUDA, EXPLICAME: responde asi:
   **Pista**
   (pista corta)
   **Pequeña explicacion del por que**
   (explica el por que matematico con analogia simple)
   **Pregunta mas facil para ti**
   (pregunta que le haga calcular algo chiquito)

4. Usa negritas para titulos, seran de color fuerte.

Ejemplo para 4+67:
No digas "71" directo. Di: "Vamos juntas! 4+67, primero junta las unidades: 7+4=? Cuando tengas eso, le sumas las decenas... Cuanto te da 7+4?"

Solo matematicas. Si es no matematico di: Lo siento %s, solo puedo ayudarte con matematicas, pero con mucho amor!
Escribe x^2, x + 3x = 4x, 4x=40. Nunca uses $.
Corta, kawaii, max 6 lineas.
""" % (st.session_state.nombre_display, st.session_state.nombre_display)

with st.container():
    st.markdown("<div style='background:%s; border:4px solid #4a2c5e; border-radius:18px; padding:10px; text-align:center; font-weight:900; box-shadow:5px 5px 0 #4a2c5e; color:#4a2c5e;'>Dumiluv - %s</div>" % (C['header'], st.session_state.nombre_display), unsafe_allow_html=True)
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
        nuevo_nombre = st.text_input("Como te digo?", value=st.session_state.nombre_display)
        sel = st.selectbox("Color tema", ["purple","blue","orange","green"], index=["purple","blue","orange","green"].index(st.session_state.tema))
        if sel != st.session_state.tema:
            st.session_state.tema = sel
            st.rerun()
        up = st.file_uploader("Foto de galeria", type=["png","jpg","jpeg"])
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
        st.markdown("<div style='background:%s; border:4px solid #4a2c5e; border-radius:18px; padding:12px; box-shadow:5px 5px 0 #4a2c5e; text-align:center;'>" % C['side'], unsafe_allow_html=True)
        if os.path.exists("dumiluv.png"):
            st.image("dumiluv.png", use_container_width=True)
        else:
            st.markdown("<div style='font-size:70px; text-align:center;'>💜</div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#000; font-weight:900; font-size:13px;'>AI Assistant - Online<br>%s</p>" % st.session_state.nombre_display, unsafe_allow_html=True)
        if avatar_path and os.path.exists(avatar_path):
            st.image(avatar_path, width=80)
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("<div style='background:white; border:3px solid #4a2c5e; border-radius:12px; padding:8px; box-shadow:3px 3px 0 #4a2c5e;'><p style='color:#000; font-size:11px; font-weight:800; margin:0;'>Si falla:<br>7001467@etrr.edu.mx<br>7001464@etrr.edu.mx<br>7001451@etrr.edu.mx<br>7001529@etrr.edu.mx</p></div>", unsafe_allow_html=True)

with center:
    if st.session_state.show_notas:
        with st.container():
            st.markdown("<div style='background:white; border:3px solid #4a2c5e; border-radius:14px; padding:10px; box-shadow:4px 4px 0 #4a2c5e; margin-bottom:8px;'><b style='color:#000;'>📒 Libretita - %d hojas</b></div>" % len(st.session_state.notas_pages), unsafe_allow_html=True)
            col_n1, col_n2, col_n3 = st.columns([2,1,1])
            with col_n1:
                titulos = [p["title"] for p in st.session_state.notas_pages]
                sel_page = st.selectbox("Hoja", titulos, index=st.session_state.notas_idx, key="sel_hoja")
                st.session_state.notas_idx = titulos.index(sel_page)
            with col_n2:
                if st.button("Nueva hoja", use_container_width=True, key="btn_new"):
                    nid = str(len(st.session_state.notas_pages)+1)
                    st.session_state.notas_pages.append({"id":nid,"title":"Hoja %s" % nid,"text":""})
                    st.session_state.notas_idx = len(st.session_state.notas_pages)-1
                    st.rerun()
            with col_n3:
                if st.button("Borrar hoja", use_container_width=True, key="btn_del"):
                    if len(st.session_state.notas_pages) > 1:
                        st.session_state.notas_pages.pop(st.session_state.notas_idx)
                        st.session_state.notas_idx = max(0, st.session_state.notas_idx-1)
                        st.rerun()
            current = st.session_state.notas_pages[st.session_state.notas_idx]
            current["text"] = st.text_area("Escribe aqui", value=current["text"], height=120, key="txt_%s" % current["id"], placeholder="Escribe tus apuntes...")
            st.write("")
            modo = st.radio("Herramienta dibujo", ["Lapiz", "Borrador"], horizontal=True, label_visibility="collapsed", key="modo_%s" % current["id"])
            sc = "#111" if "Lapiz" in modo else "#ffffff"
            sw = 3 if "Lapiz" in modo else 20
            st_canvas(stroke_width=sw, stroke_color=sc, background_color="#fff", height=180, drawing_mode="freedraw", key="c_%s" % current["id"])
            if st.button("Cerrar libretita", key="btn_close"):
                st.session_state.show_notas = False
                st.rerun()

    # AQUI ESTA EL RECUADRO ROSA GRANDOTE - TODO ADENTRO
    st.markdown("<div style='background:%s; border:4px solid #4a2c5e; border-radius:18px; padding:12px; box-shadow:6px 6px 0 #4a2c5e; min-height:500px;'>" % C['chat'], unsafe_allow_html=True)
    st.markdown("<div style='background:%s; border:3px solid #4a2c5e; border-radius:14px; padding:8px; text-align:center; font-weight:900; color:#4a2c5e; margin-bottom:12px;'>Dumiluv 💜</div>" % C['header'], unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("<p style='color:#000; text-align:center; font-weight:800;'>Hola %s Que resolvemos hoy? 💖</p>" % st.session_state.nombre_display, unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("<div style='background:%s; border:2.5px solid #4a2c5e; border-radius:12px; padding:8px; text-align:center; font-size:11px; font-weight:800; color:#000; box-shadow:3px 3px 0 #4a2c5e; margin-bottom:6px;'>x^2 -5x +6 =0</div>" % C['card'], unsafe_allow_html=True)
            if st.button("Usar 1", key="e1", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"x^2 -5x +6 =0"})
                st.rerun()
            st.markdown("<div style='background:%s; border:2.5px solid #4a2c5e; border-radius:12px; padding:8px; text-align:center; font-size:11px; font-weight:800; color:#000; box-shadow:3px 3px 0 #4a2c5e; margin-bottom:6px;'>Madre e hija 40</div>" % C['side'], unsafe_allow_html=True)
            if st.button("Usar 2", key="e2", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"La edad de una madre es 3 veces la de su hija y juntas suman 40"})
                st.rerun()
        with cc2:
            st.markdown("<div style='background:%s; border:2.5px solid #4a2c5e; border-radius:12px; padding:8px; text-align:center; font-size:11px; font-weight:800; color:#000; box-shadow:3px 3px 0 #4a2c5e; margin-bottom:6px;'>Pera 2 mas que manzana</div>" % C['side'], unsafe_allow_html=True)
            if st.button("Usar 3", key="e3", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"Una pera cuesta 2 mas que una manzana y 3 peras y 2 manzanas cuestan 20"})
                st.rerun()
            st.markdown("<div style='background:%s; border:2.5px solid #4a2c5e; border-radius:12px; padding:8px; text-align:center; font-size:11px; font-weight:800; color:#000; box-shadow:3px 3px 0 #4a2c5e; margin-bottom:6px;'>4+67</div>" % C['card'], unsafe_allow_html=True)
            if st.button("Usar 4", key="e4", use_container_width=True):
                if not st.session_state.conv_id: nueva_conversacion()
                st.session_state.messages.append({"role":"user","content":"4+67"})
                st.rerun()
    else:
        for m in st.session_state.messages:
            role_class = "user" if m["role"]=="user" else "assistant"
            content = m["content"].replace("<","&lt;").replace(">","&gt;")
            content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            content = content.replace("\n", "<br>")
            st.markdown('<div class="chat-row %s"><div class="bubble %s">%s</div></div>' % (role_class, role_class, content), unsafe_allow_html=True)
        if st.session_state.messages[-1]["role"] == "assistant" and st.session_state.voz_activa:
            try:
                tts = gTTS(text=st.session_state.messages[-1]["content"][:220], lang='es', tld='com.mx', slow=False)
                tts.save("voz_temp.mp3")
                st.audio("voz_temp.mp3", autoplay=True)
            except:
                pass

    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")
    prompt = st.chat_input("Escribe aqui... 💖")
    if prompt:
        if not st.session_state.conv_id:
            nueva_conversacion()
        st.session_state.messages.append({"role":"user","content":prompt})
        try:
            msgs = [{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.messages
            comp = client.chat.completions.create(model=MODELO, messages=msgs, temperature=0.7)
            full = comp.choices[0].message.content.replace("$","")
            st.session_state.messages.append({"role":"assistant","content":full})
            guardar_conversacion()
            st.rerun()
        except Exception as e:
            st.error("Error: %s" % e)

with right:
    with st.container():
        st.markdown("<div style='background:%s; border:3px solid #4a2c5e; border-radius:14px; padding:8px; text-align:center; font-weight:900; color:#4a2c5e; box-shadow:3px 3px 0 #4a2c5e; margin-bottom:8px;'>Chat History</div>" % C['header'], unsafe_allow_html=True)
        if not convs:
            st.markdown("<div style='background:white; border:2.5px solid #4a2c5e; border-radius:12px; padding:10px; text-align:center; box-shadow:3px 3px 0 #4a2c5e;'><p style='color:#000; font-size:12px; font-weight:800;'>En blanco</p></div>", unsafe_allow_html=True)
        else:
            for cid, cdata in sorted(convs.items(), key=lambda x: x[1].get("date",""), reverse=True)[:8]:
                if st.button("%s %s" % (cdata['date'], cdata['title'][:20]), key="h_%s" % cid, use_container_width=True):
                    st.session_state.conv_id = cid
                    st.session_state.messages = cdata["messages"]
                    st.rerun()
