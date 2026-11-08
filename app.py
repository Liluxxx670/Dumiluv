import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
import json, os, re, hashlib, datetime, uuid, base64, mimetypes, html

# =========================================================
# DUMILUV 2.0 -interfaz kawaii pastel
# Conserva: cuentas, chat matemático, voz, temas, notas,
# avatar personal y conversaciones anteriores.
# =========================================================

st.set_page_con

g(page_title="Dumiluv 2.0", page_icon="💗", layout="wide")

USERS_FILE = "users.json"
AVATAR_FOLDER = "avatars"
os.makedirs(AVATAR_FOLDER, exist_ok=True)

# ---------- Datos y utilidades ----------
def load_data():
if os.path.exists(USERS_FILE):
try:
with open(USERS_FILE, "r", encoding="utf-8") as f:
data = json.load(f)
return data if isinstance(data, dict) else {}
except (json.JSONDecodeError, OSError):
return {}
return {}

def save_data(data):
with open(USERS_FILE, "w", encoding="utf-8") as f:
json.dump(data, f, ensure_ascii=False, indent=2)

def hash_pass(password):
return hashlib.sha256(password.encode("utf-8")).hexdigest()

def safe_text(value):
return html.escape(str(value or ""))

def image_data_uri(path):
if not path or not os.path.exists(path):
return ""
try:
mime = mimetypes.guess_type(path)[0] or "image/png"
with open(path, "rb") as f:
encoded = base64.b64encode(f.read()).decode("ascii")
return f"data:{mime};base64,{encoded}"
except OSError:
return ""

def strip_emojis_for_voice(text):
"""Quita emojis solo de la versión hablada; el chat conserva el texto original."""
# Rangos Unicode habituales de emojis, pictogramas, banderas y selectores.
emoji_pattern = re.compile(
"["
"\U0001F1E0-\U0001F1FF"
"\U0001F300-\U0001F5FF"
"\U0001F600-\U0001F64F"
"\U0001F680-\U0001F6FF"
"\U0001F700-\U0001F77F"
"\U0001F780-\U0001F7FF"
"\U0001F800-\U0001F8FF"
"\U0001F900-\U0001F9FF"
"\U0001FA00-\U0001FAFF"
"\U00002600-\U000026FF"
"\U00002700-\U000027BF"
"]+",
ags=re.UNICODE
)
cleaned = emoji_pattern.sub("", str(text))
cleaned = re.sub(r"[\uFE0E\uFE0F\u200D]", "", cleaned)
cleaned = re.sub(r"\s+", " ", cleaned).strip()
return cleaned[:280]

def ensure_user_record(data, username):
    data.setdefault(username, {})
    data[username].setdefault("display", username)
    data[username].setdefault("avatar_path", "")
    data[username].setdefault("gender", "Prefiero no decirlo")
    data[username].setdefault("pronouns", "Neutros (elle)")
    data[username].setdefault("convs", {})
    return data[username]

# ---------- Estado de sesión ----------
defaults = {
"tema": "pink",
"usuario": "",
"nombre_display": "",
"genero": "Prefiero no decirlo",
"pronombres": "Neutros (elle)",
"show_ajustes": False,
"voz_activa": True,
"show_notas": False,
"conv_id": None,
"messages": [],
"notas_pages": [{"id": "1", "title": "Hoja 1", "text": ""}],
"notas_idx": 0,
"active_view": "chat",
"history_loaded": False,
}
for key, value in defaults.items():
if key not in st.session_state:
st.session_state[key] = value

THEMES = {
    "pink": {
        "bg": "#f7eafa",
        "panel": "#f7dffc",
        "header": "#f7cde5",
        "chat": "#fffafd",
        "side": "#f0ddfa",
        "card": "#fce2f0",
        "btn": "#edb8dc",
        "accent": "#9b6bb5",
        "ink": "#573d68",
        "field": "#fdf6fc",
        "field_text": "#573d68"
    },

    "purple": {
        "bg": "#eee4fb",
        "panel": "#e8d8f8",
        "header": "#ddc4f5",
        "chat": "#faf7ff",
        "side": "#e8d8f8",
        "card": "#f0e2fa",
        "btn": "#d6b5ed",
        "accent": "#9565bd",
        "ink": "#51366b",
        "field": "#faf7ff",
        "field_text": "#51366b"
    },

    "blue": {
        "bg": "#e5f2ff",
        "panel": "#d5eaff",
        "header": "#b9dcff",
        "chat": "#f8fcff",
        "side": "#d5eaff",
        "card": "#e1f0ff",
        "btn": "#afd5fa",
        "accent": "#659bc9",
        "ink": "#355878",
        "field": "#f8fcff",
        "field_text": "#355878"
    },

    "green": {
        "bg": "#e6f7ed",
        "panel": "#d5f0df",
        "header": "#bce8ce",
        "chat": "#f8fffa",
        "side": "#d5f0df",
        "card": "#e0f5e7",
        "btn": "#aee0bf",
        "accent": "#65a77c",
        "ink": "#345e43",
        "field": "#f8fffa",
        "field_text": "#345e43"
    }
}

C = THEMES.get(st.session_state.tema, THEMES["pink"])

# ---------- Estilos ----------
st.markdown(f"""
<style>
:root {{
--bg:{C['bg']}; --panel:{C['panel']}; --header:{C['header']};
--chat:{C['chat']}; --side:{C['side']}; --card:{C['card']};
--btn:{C['btn']}; --accent:{C['accent']}; --ink:{C['ink']};
--
eld:{C['

eld']}; --

eldtext:{C['

eld_text']};

}}
.stApp {{ background:var(--bg)!important; color:var(--ink)!important; }}
header, footer, #MainMenu {{ visibility:hidden !important; }}

.block-container {{ padding-top:1.2rem !important; padding-bottom:2rem !important; max-
width:1500px; }}

h1,h2,h3,p,label,span,div {{font-family: 'Trebuchet MS', sans-serif; }}

h1,h2,h3 {{ color:var(--ink)!important; }}
div[data-testid="stVerticalBlockBorderWrapper"]{{
background:transparent !important; border:none !important; box-shadow:none !important
;
}}
div[data-testid="stButton"] > button, .stButton > button {{
background:var(--btn)!important; color:var(--ink)!important;
border:2px solid var(--ink)!important; border-radius:15px !important;
font-weight:800 !important; box-shadow:3px 3px 0 var(--ink)!important;
min-height:2.55rem; transition:transform .15s ease;
}}
div[data-testid="stButton"] > button:hover {{
transform:translateY(-2px); border-color:var(--accent)!important;
}}
div[data-testid="stTextInput"]input,
div[data-testid="stTextArea"]textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stFileUploader"] section {{
background:var(--

eld)!important; color:var(--

eldtext)!important;
border:2px solid var(--ink)!important; border-radius:13px !important;
}}
div[data-testid="stTextInput"]input, div[data-testid="stTextArea"]textarea {{
color:var(--

eldtext)!important; -webkit-text-

ll-color:var(--

eldtext)!important;

}}
div[data-testid="stSelectbox"] *, div[data-testid="stFileUploader"] * {{
color:var(--

eldtext)!important;

}}
div[data-testid="stTextInput"]label, div[data-testid="stTextArea"]label,
div[data-testid="stSelectbox"]label, div[data-testid="stFileUploader"]label,
.stRadio label {{ color:var(--ink)!important; font-weight:800 !important; }}
div[data-testid="stAudio"]{{
background:var(--panel)!important; border:2px solid var(--ink)!important;
border-radius:15px !important; padding:5px !important;
}}
div[data-testid="stAlert"]{{ border-radius:14px; }}
.dumi-top {{
background:linear-gradient(100deg,var(--header),var(--side));
border:2px solid var(--ink); border-radius:20px; padding:13px 18px;

box-shadow:4px 4px 0 var(--ink); text-align:center; color:var(--ink);
font-size:23px; font-weight:900; margin-bottom:15px;
}}
.dumi-panel {{
background:var(--panel); border:2px solid var(--ink); border-radius:20px;
box-shadow:4px 4px 0 var(--ink); padding:13px; color:var(--ink);
}}
.dumi-side {{
background:var(--side); border:2px solid var(--ink); border-radius:20px;
box-shadow:4px 4px 0 var(--ink); padding:13px; text-align:center;
}}
.dumi-section {{
background:var(--header); border:2px solid var(--ink); border-radius:14px;
padding:9px; color:var(--ink); text-align:center; font-weight:900;
margin-bottom:10px;
}}
.chat-scroll {{
background:var(--chat); border:2px solid var(--ink); border-radius:18px;
padding:15px; min-height:440px; max-height:590px; over

ow-y:auto;

}}
.chat-line {{ display:

ex; align-items:

ex-end; gap:9px; margin:13px 0; width:100%; }}

.chat-line.user {{justify-content:

ex-end; }}
.chat-line.assistant {{justify-content:

ex-start; }}

.chat-avatar {{
width:42px; height:42px; min-width:42px; border-radius:50%;
object-

t:cover; border:2px solid var(--ink); background:var(--side);

}}
.chat-bubble {{
max-width:78%; padding:11px 14px; border:2px solid var(--ink);
border-radius:17px; color:var(--ink); font-size:14px; line-height:1.45;
over
ow-wrap:anywhere; box-shadow:2px 2px 0 rgba(70,45,80,.16);
}}
.chat-bubble.user {{ background:var(--card); border-bottom-right-radius:5px; }}
.chat-bubble.assistant {{ background:#

f; border-bottom-left-radius:5px; }}

.chat-name {{font-size:10px; font-weight:900; color:var(--accent); margin:0 0 3px 3px; }}
.history-item {{
background:var(--panel); border:1.5px solid var(--ink); border-radius:12px;
padding:8px; margin-bottom:7px; color:var(--ink); font-size:12px;

}}
.dumi-muted {{ color:var(--ink); opacity:.75; font-size:12px; }}
div[data-testid="stFileUploader"] button {{
background:var(--btn)!important; color:var(--ink)!important;
border:1px solid var(--ink)!important;
}}
@media(max-width:800px){{
.block-container {{ padding-left: .8rem !important; padding-right:.8rem !important; }}
.chat-scroll {{ min-height:360px; }}
.chat-bubble {{ max-width:82%; font-size:13px; }}
}}
</style>
""", unsafe_allow_html=True)

# ---------- Funciones de conversación ----------
def nueva_conversacion():
st.session_state.conv_id = str(uuid.uuid4())[:8]
st.session_state.messages = []
st.session_state.history_loaded = True

def guardar_conversacion():
if not st.session_state.messages or not st.session_state.conv_id:
return
data = load_data()
info = ensure_user_record(data, st.session_state.usuario)
rst = next(
    (m["content"][:35]for m in
     st.session_state.messages if m["role"] == "user"),
    "Nueva charla"
)

date_label =
datetime.datetime.now().strftime("%d/%m %H:%M")
info["convs"][st.session_state.conv_id] = {
"title":rst, 
    "date": date_label, 
    "messages": st.session_state.messages

}
save_data(data)

def render_chat(messages, user_avatar, assistant_avatar, display_name):
pieces = ["<div class='chat-scroll'>"]
if not messages:
pieces.append(
    "<div style='text-align:center;padding:55px 10px;color:var(--ink);'>"
    "<div style='font-size:35px;'>💗✨🌷</div>"
    f"<h3>¡Hola {safe_text(display_name)}!</h3>"
    "<p>¿Qué resolvemos hoy?</p>"
    "<p>Prueba una suma, una resta o una ecuación.</p>"
    "</div>"
)
for msg in messages:
role = "user" if msg.get("role") == "user" else "assistant"
content = safe_text(msg.get("content", "")).replace("\n", "<br>")
avatar = user_avatar if role == "user" else assistant_avatar
if not avatar:
avatar = ""
img = (
    f"<img class='chat-avatar' src='{avatar}'>"
    if avatar
    else "<div class='chat-avatar' style='display:flex;align-items:center;justify-content:center;'>💗</div>"
)
r;'>💗</div>")
bubble = f"<div class='chat-bubble {role}'>{content}</div>"
name = safe_text(display_name)if role == "user" else "Dumiluv"
if role == "user":
pieces.append(f"<div class='chat-line user'>{bubble}{img}</div>")
else:
pieces.append(f"<div class='chat-line assistant'>{img}<div><div class='chat-name'>
{name}</div>{bubble}</div></div>")
pieces.append("</div>")
st.markdown("".join(pieces), unsafe_allow_html=True)

def send_message(text):
text = text.strip()
if not text:
return
if not st.session_state.conv_id:
nueva_conversacion()
st.session_state.messages.append({"role": "user", "content": text})
api_key = st.secrets.get("GROQ_API_KEY", "")
if not api_key:
st.session_state.messages.append({
"role": "assistant",
"content": "Todavía falta con

gurar GROQ_API_KEY en los Secrets de Streamlit. Cuan

do esté con

gurada, podré ayudarte con el ejercicio. 💗"

})

guardar_conversacion()
return
try:
client = Groq(api_key=api_key)
display = st.session_state.nombre_display
pronouns = st.session_state.pronombres
gender = st.session_state.genero
system_prompt = (
f"Eres Dumiluv, tutora kawaii de matemáticas para {display}. "
f"La persona indicó género/sexo: {gender}; sus pronombres elegidos son: {pronouns
}. "
"Respeta siempre sus pronombres y no hagas suposiciones adicionales. "
"Aceptas matemáticas: sumas, restas, multiplicaciones, divisiones, álgebra, ecuacion
es y problemas. "
"Guía paso a paso y explica por qué con analogías sencillas. "
"No des solo el resultado sin explicación. Si pide pista, da una pista y una pregunta se
ncilla. "
"Usa un tono amable, claro y breve. Puedes incluir emojis en el texto."
)
msgs = [{"role": "system", "content": system_prompt}] + st.session_state.messages
response = client.chat.completions.create(
model="openai/gpt-oss-20b",
messages=msgs,
temperature=0.7
)
answer = response.choices[0].message.content or "No pude generar una respuesta. I
nténtalo otra vez. 💗"
st.session_state.messages.append({"role": "assistant", "content": answer})
except Exception as error:
st.session_state.messages.append({
"role": "assistant",
"content": f"No pude conectarme en este momento. Revisa tu conexión o la clave de
Groq. ({str(error)[:180]})"
})
guardar_conversacion()

# ---------- Pantalla de acceso / registro ----------
if not st.session_state.usuario:

st.markdown("<div class='dumi-top'>⭐Dumiluv 2.0 ✨</div>", unsafe_allow_html=True
)
st.markdown("<div class='dumi-panel' style='max-width:760px;margin:auto;text-align:ce
nter;'>"
"<div style='font-size:48px;'>

💗</div>"
"<h2>Tu rinconcito para aprender</h2>"
"<p>Inicia sesión o crea tu cuenta para entrar a Dumiluv.</p></div>",
unsafe_allow_html=True)
st.write("")
tab_login, tab_create = st.tabs(["💗Entrar", "🌷Crear cuenta"])
data = load_data()

with tab_login:
st.markdown("<div class='dumi-panel'>", unsafe_allow_html=True)
username = st.text_input("Usuario", key="login_user")
password = st.text_input("Contraseña", type="password", key="login_pass")
if st.button("Entrar ✨", use_container_width=True):
found = next((k for k in data if k.lower() == username.lower()), None)
if found and data[found].get("pass") == hash_pass(password):
info = ensure_user_record(data, found)
save_data(data)
st.session_state.usuario = found
st.session_state.nombre_display = info.get("display", found)
st.session_state.genero = info.get("gender", "Pre

ero no decirlo")
st.session_state.pronombres = info.get("pronouns", "Neutros (elle)")
st.session_state.conv_id = None
st.session_state.messages = []
st.rerun()
else:
st.error("Usuario o contraseña incorrectos.")
st.markdown("</div>", unsafe_allow_html=True)

with tab_create:
st.markdown("<div class='dumi-panel'>", unsafe_allow_html=True)
new_user = st.text_input("Crea un usuario (letras, números, punto o guion bajo)", key="
create_user")
new_display = st.text_input("¿Cómo quieres que te diga?", key="create_display")
gender_options = ["Pre

ero no decirlo", "Mujer", "Hombre", "No binario", "Otro"]

new_gender = st.selectbox("Sexo o género (opcional)", gender_options, key="create_g
ender")
pronoun_options = ["Ella", "Él", "Elle", "Neutros (elle)", "Otro / personalizado"]
new_pronouns = st.selectbox("¿Qué pronombres quieres que use?", pronoun_options,
key="create_pronouns")
custom_pronouns = ""
if new_pronouns == "Otro / personalizado":
custom_pronouns = st.text_input("Escribe tus pronombres", placeholder="Ej. ella/elle
")
new_password = st.text_input("Contraseña", type="password", key="create_pass")
repeat_password = st.text_input("Repite tu contraseña", type="password", key="create
_pass2")
st.caption("El sexo/género es opcional. Puedes elegir tus pronombres por separado.")
if st.button("Crear cuenta y entrar 💖", use_container_width=True):
if not re.match(r"^[a-zA
Z0
9._]+$", new_user):

st.error("Usa solo letras, números, punto o guion bajo.")
elif len(new_user) < 3:
st.error("El usuario debe tener al menos 3 caracteres.")
elif any(k.lower() == new_user.lower()for k in data):
st.error("Ese usuario ya existe. Prueba con otro.")
elif not new_password:
st.error("Escribe una contraseña.")
elif new_password != repeat_password:
st.error("Las contraseñas no coinciden.")
elif new_pronouns == "Otro / personalizado" and not custom_pronouns.strip():
st.error("Escribe los pronombres que quieres usar.")
else:
pronouns_value = custom_pronouns.strip()if custom_pronouns.strip() else new_p
ronouns
data[new_user] = {
"pass": hash_pass(new_password),
"display": new_display.strip() or new_user,
"gender": new_gender,
"pronouns": pronouns_value,
"avatar_path": "",
"convs": {}
}
save_data(data)

st.session_state.usuario = new_user
st.session_state.nombre_display = new_display.strip() or new_user
st.session_state.genero = new_gender
st.session_state.pronombres = pronouns_value
st.session_state.conv_id = None
st.session_state.messages = []
st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
st.stop()

# ---------- Cargar datos de la cuenta ----------
data = load_data()
user_info = ensure_user_record(data, st.session_state.usuario)
save_data(data)
convs = user_info.get("convs", {})
avatar_path = user_info.get("avatar_path", "")
user_avatar = image_data_uri(avatar_path)
assistant_avatar = image_data_uri("dumiluv.png")

# ---------- Cabecera y navegación ----------
st.markdown(
f"<div class='dumi-top'>🌷Dumiluv <span style='font-size:15px;'>· {safe_text(st.sessio
n_state.nombre_display)}💗</span></div>",
unsafe_allow_html=True
)
nav1, nav2, nav3, nav4, nav5 = st.columns(5)
with nav1:
if st.button("💬Chat", use_container_width=True):
st.session_state.active_view = "chat"
st.session_state.show_ajustes = False
st.session_state.show_notas = False
st.rerun()
with nav2:
if st.button("⚙Ajustes", use_container_width=True):
st.session_state.active_view = "settings"
st.session_state.show_ajustes = True
st.session_state.show_notas = False
st.rerun()

with nav3:
if st.button("📒Notas", use_container_width=True):
st.session_state.active_view = "notes"
st.session_state.show_notas = True
st.session_state.show_ajustes = False
st.rerun()
with nav4:
if st.button("➕Nuevo chat", use_container_width=True):
nueva_conversacion()
st.session_state.active_view = "chat"
st.rerun()
with nav5:
if st.button("Salir", use_container_width=True):
st.session_state.usuario = ""
st.session_state.messages = []
st.session_state.conv_id = None
st.rerun()

# ---------- Ajustes ----------
if st.session_state.active_view == "settings":
st.markdown("<div class='dumi-panel'><div class='dumi-section'>⚙Ajustes de tu per
l

</div>", unsafe_allow_html=True)
st.write("")
a1, a2 = st.columns([1, 2])
with a1:
if assistant_avatar:
st.image("dumiluv.png", width=145)
else:
st.markdown("<div style='font-size:75px;text-align:center;'>💗</div>", unsafe_allow
_html=True)
with a2:
display_name = st.text_input("Cómo quieres que te diga", value=st.session_state.nom
bre_display, key="settings_display")
theme_names = ["pink", "purple", "blue", "orange", "green"]
theme_labels = {"pink":"Rosa pastel", "purple":"Lila", "blue":"Azul cielo", "orange":"Durazno"
, "green":"Verde menta"}
chosen_theme = st.selectbox(
"Color del tema",

theme_names,
index=theme_names.index(st.session_state.tema),
format_func=lambda x: theme_labels[x],
key="settings_theme"
)
gender_options = ["Pre

ero no decirlo", "Mujer", "Hombre", "No binario", "Otro"]

current_gender = st.session_state.genero if st.session_state.genero in gender_option
s else "Pre

ero no decirlo"
chosen_gender = st.selectbox("Sexo o género (opcional)", gender_options, index=gen
der_options.index(current_gender), key="settings_gender")
pronoun_options = ["Ella", "Él", "Elle", "Neutros (elle)", "Otro / personalizado"]
current_pronouns = st.session_state.pronombres if st.session_state.pronombres in pr
onoun_options else "Otro / personalizado"
chosen_pronouns = st.selectbox("Pronombres", pronoun_options, index=pronoun_opt
ions.index(current_pronouns), key="settings_pronouns")
custom = ""
if chosen_pronouns == "Otro / personalizado":
custom = st.text_input("Tus pronombres", value="" if current_pronouns != "Otro / per
sonalizado" else st.session_state.pronombres)
uploaded_avatar = st.

le_uploader("Foto de per

l", type=["png", "jpg", "jpeg"], key="pro
l

e_upload")
if st.button("Guardar cambios 💗", use_container_width=True):
st.session_state.nombre_display = display_name.strip() or st.session_state.usuario
st.session_state.tema = chosen_theme
st.session_state.genero = chosen_gender
st.session_state.pronombres = (custom.strip()if chosen_pronouns == "Otro / perso
nalizado" else chosen_pronouns)
d = load_data()
info = ensure_user_record(d, st.session_state.usuario)
info["display"] = st.session_state.nombre_display
info["gender"] = st.session_state.genero
info["pronouns"] = st.session_state.pronombres
if uploaded_avatar is not None:
ext = uploaded_avatar.name.rsplit(".", 1)[-1].lower()
path = os.path.join(AVATAR_FOLDER, f"{st.session_state.usuario}.{ext}")
with open(path, "wb") as f:
f.write(uploaded_avatar.getbu
er())

info["avatar_path"] = path

save_data(d)
st.success("¡Tus cambios se guardaron!")
st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ---------- Notas ----------
elif st.session_state.active_view == "notes":
st.markdown("<div class='dumi-panel'><div class='dumi-section'>📒Mi libretita</div>",
unsafe_allow_html=True)
titles = [p["title"]for p in st.session_state.notas_pages]
selected_title = st.selectbox("Elige una hoja", titles, index=min(st.session_state.notas_id
x, len(titles)-1))
st.session_state.notas_idx = titles.index(selected_title)
n1, n2 = st.columns(2)
with n1:
if st.button("➕Nueva hoja", use_container_width=True):
nid = str(uuid.uuid4())[:6]
st.session_state.notas_pages.append({"id": nid, "title": f"Hoja {len(st.session_state.n
otas_pages)+1}", "text": ""})
st.session_state.notas_idx = len(st.session_state.notas_pages)-1
st.rerun()
with n2:
if st.button("🗑Borrar hoja", use_container_width=True):
if len(st.session_state.notas_pages) > 1:
st.session_state.notas_pages.pop(st.session_state.notas_idx)
st.session_state.notas_idx = 0
st.rerun()
current_page = st.session_state.notas_pages[st.session_state.notas_idx]
current_page["text"] = st.text_area("Escribe tus apuntes", value=current_page["text"], hei
ght=150, key=f"note_{current_page['id']}")
st.caption("También puedes dibujar en el espacio de abajo.")
draw_mode = st.radio("Herramienta", ["Lápiz", "Borrador"], horizontal=True)
st_canvas(
stroke_width=3 if draw_mode == "Lápiz" else 18,
stroke_color="#4d3b59" if draw_mode == "Lápiz" else "#
",

background_color="#
",

height=220,
drawing_mode="freedraw",

key=f"canvas_{current_page['id']}"
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------- Chat ----------
else:
left, center, right = st.columns([1.05, 2.65, 1.05], gap="medium")

with left:
st.markdown("<div class='dumi-side'>", unsafe_allow_html=True)
if os.path.exists("dumiluv.png"):
st.image("dumiluv.png", use_container_width=True)
else:
st.markdown("<div style='font-size:85px;'>

</div>", unsafe_allow_html=True)
st.markdown(f"<h4 style='margin-bottom:0;color:var(--ink);'>Dumiluv</h4><p class='
dumi-muted'>Tu asistente de matemáticas ✨</p>", unsafe_allow_html=True)
if avatar_path and os.path.exists(avatar_path):
st.image(avatar_path, width=75)
st.markdown(f"<p style='font-weight:800;color:var(--ink);'>{safe_text(st.session_stat
e.nombre_display)}</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.write("")
st.markdown("<div class='dumi-panel'><b>💡Recuerda</b><p class='dumi-muted'>
Puedes preguntar paso a paso. ¡Aprender también puede ser divertido!</p></div>", unsaf
e_allow_html=True)

with center:
st.markdown("<div class='dumi-panel'>", unsafe_allow_html=True)
st.markdown("<div class='dumi-section'>💗Conversación</div>", unsafe_allow_html=
True)
render_chat(st.session_state.messages, user_avatar, assistant_avatar, st.session_stat
e.nombre_display)

if not st.session_state.messages:
st.write("")
st.caption("Prueba un ejercicio:")
ex1, ex2 = st.columns(2)
with ex1:

if st.button("4 + 67", use_container_width=True):
send_message("4+67")
st.rerun()
if st.button("Problema de edades", use_container_width=True):
send_message("La edad de una madre es 3 veces la de su hija y juntas suman 40

. ¿Cómo lo resuelvo?")
st.rerun()
with ex2:
if st.button("x2- 5x + 6 = 0", use_container_width=True):
send_message("x^2 - 5x + 6 = 0")
st.rerun()
if st.button("Pera y manzana", use_container_width=True):
send_message("Una pera cuesta 2 más que una manzana. Tres peras y dos manz

anas cuestan 20. ¿Cómo lo resuelvo?")

st.rerun()

st.write("")
input_col, send_col = st.columns([5, 1])
with input_col:
user_text = st.text_input("Mensaje", placeholder="Escribe un mensaje... 💗", label_vi
sibility="collapsed", key="chat_input")
with send_col:
if st.button("Enviar", use_container_width=True):
if user_text.strip():
send_message(user_text)
st.rerun()

voice_col1, voice_col2 = st.columns([1, 3])
with voice_col1:
if st.button("🔊Voz ON" if st.session_state.voz_activa else "🔇Voz OFF", use_contain
er_width=True):
st.session_state.voz_activa = not st.session_state.voz_activa
st.rerun()
with voice_col2:
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant
" and st.session_state.voz_activa:
spoken = strip_emojis_for_voice(st.session_state.messages[-1]["content"])
if spoken:

try:
tts = gTTS(text=spoken, lang="es", tld="com.mx", slow=False)
tts.save("voz_temp.mp3")
st.audio("voz_temp.mp3", autoplay=True)
except Exception:
st.caption("No se pudo generar el audio. Revisa tu conexión.")
st.markdown("</div>", unsafe_allow_html=True)

with right:
st.markdown("<div class='dumi-panel'>", unsafe_allow_html=True)
st.markdown("<div class='dumi-section'>🕘Chat History</div>", unsafe_allow_html=T
rue)
if st.button("+ Empezar conversación", use_container_width=True):
nueva_conversacion()
st.rerun()
saved_convs = sorted(
convs.items(),
key=lambda item: item[1].get("date", ""),
reverse=True
)
if not saved_convs:
st.markdown("<p class='dumi-muted'>Tus conversaciones guardadas aparecerán aq
uí.</p>", unsafe_allow_html=True)
for cid, conversation in saved_convs[:12]:
label = conversation.get("title", "Nueva charla")
date_label = conversation.get("date", "")
if st.button(f"💬{label[:24]} · {date_label}", key=f"history_{cid}", use_container_width
=True):
st.session_state.conv_id = cid
st.session_state.messages = conversation.get("messages", [])
st.session_state.active_view = "chat"
st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
