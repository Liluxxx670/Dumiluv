import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
import json, os, re, hashlib, datetime, uuid, base64, mimetypes, html

# =========================================================
# DUMILUV 2.0 - interfaz kawaii pastel
# Conserva: cuentas, chat matemático, voz, temas, notas,
# avatar personal y conversaciones anteriores.
# =========================================================

st.set_page_config(page_title="Dumiluv 2.0", page_icon="💗", layout="wide")

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
        flags=re.UNICODE
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
    "invitado": False,
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
        "bg": "#f7eafa", "panel": "#fff7fc", "header": "#f7cde5",
        "chat": "#fffafd", "side": "#f0ddfa", "card": "#ffe2f0",
        "btn": "#edb8dc", "accent": "#9b6bb5", "ink": "#573d68",
        "field": "#fffafd", "field_text": "#573d68"
    },
    "purple": {
        "bg": "#eee4fb", "panel": "#fff9ff", "header": "#ddc4f5",
        "chat": "#fffaff", "side": "#e8d8f8", "card": "#f0e2ff",
        "btn": "#d8b8f0", "accent": "#8963b0", "ink": "#503b68",
        "field": "#fffaff", "field_text": "#503b68"
    },
    "blue": {
        "bg": "#e4f1ff", "panel": "#f8fcff", "header": "#c4e5fb",
        "chat": "#fbfdff", "side": "#d9edff", "card": "#dcefff",
        "btn": "#b7def7", "accent": "#5e9fc5", "ink": "#31556d",
        "field": "#f8fcff", "field_text": "#31556d"
    },
    "orange": {
        "bg": "#fff0dc", "panel": "#fffaf2", "header": "#ffdfa8",
        "chat": "#fffdf8", "side": "#ffebc9", "card": "#ffebc7",
        "btn": "#f8d18e", "accent": "#c28a3c", "ink": "#73512c",
        "field": "#fffaf2", "field_text": "#73512c"
    },
    "green": {
        "bg": "#e4f7eb", "panel": "#f8fff9", "header": "#c6efd6",
        "chat": "#fbfffc", "side": "#d8f3e1", "card": "#d8f5e3",
        "btn": "#b7e8c9", "accent": "#62a982", "ink": "#345f49",
        "field": "#f8fff9", "field_text": "#345f49"
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
  --field:{C['field']}; --fieldtext:{C['field_text']};
}}
.stApp {{ background:var(--bg) !important; color:var(--ink) !important; }}
header, footer, #MainMenu {{ visibility:hidden !important; }}
.block-container {{ padding-top:1.2rem !important; padding-bottom:2rem !important; max-width:1500px; }}
h1,h2,h3,p,label,span,div {{ font-family: 'Trebuchet MS', sans-serif; }}
h1,h2,h3 {{ color:var(--ink) !important; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{
  background:transparent !important; border:none !important; box-shadow:none !important;
}}
div[data-testid="stButton"] > button, .stButton > button {{
  background:var(--btn) !important; color:var(--ink) !important;
  border:2px solid var(--ink) !important; border-radius:15px !important;
  font-weight:800 !important; box-shadow:3px 3px 0 var(--ink) !important;
  min-height:2.55rem; transition:transform .15s ease;
}}
div[data-testid="stButton"] > button:hover {{
  transform:translateY(-2px); border-color:var(--accent) !important;
}}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stFileUploader"] section {{
  background:var(--field) !important; color:var(--fieldtext) !important;
  border:2px solid var(--ink) !important; border-radius:13px !important;
}}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
  color:var(--fieldtext) !important; -webkit-text-fill-color:var(--fieldtext) !important;
}}
div[data-testid="stSelectbox"] *, div[data-testid="stFileUploader"] * {{
  color:var(--fieldtext) !important;
}}
div[data-testid="stTextInput"] label, div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label, div[data-testid="stFileUploader"] label,
.stRadio label {{ color:var(--ink) !important; font-weight:800 !important; }}
div[data-testid="stAudio"] {{
  background:var(--panel) !important; border:2px solid var(--ink) !important;
  border-radius:15px !important; padding:5px !important;
}}
div[data-testid="stAlert"] {{ border-radius:14px; }}
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
  padding:15px; min-height:440px; max-height:590px; overflow-y:auto;
}}
.chat-line {{ display:flex; align-items:flex-end; gap:9px; margin:13px 0; width:100%; }}
.chat-line.user {{ justify-content:flex-end; }}
.chat-line.assistant {{ justify-content:flex-start; }}
.chat-avatar {{
  width:42px; height:42px; min-width:42px; border-radius:50%;
  object-fit:cover; border:2px solid var(--ink); background:var(--side);
}}
.chat-bubble {{
  max-width:78%; padding:11px 14px; border:2px solid var(--ink);
  border-radius:17px; color:var(--ink); font-size:14px; line-height:1.45;
  overflow-wrap:anywhere; box-shadow:2px 2px 0 rgba(70,45,80,.16);
}}
.chat-bubble.user {{ background:var(--card); border-bottom-right-radius:5px; }}
.chat-bubble.assistant {{ background:#fff; border-bottom-left-radius:5px; }}
.chat-name {{ font-size:10px; font-weight:900; color:var(--accent); margin:0 0 3px 3px; }}
.history-item {{
  background:var(--panel); border:1.5px solid var(--ink); border-radius:12px;
  padding:8px; margin-bottom:7px; color:var(--ink); font-size:12px;
}}
.dumi-muted {{ color:var(--ink); opacity:.75; font-size:12px; }}
div[data-testid="stFileUploader"] button {{
  background:var(--btn) !important; color:var(--ink) !important;
  border:1px solid var(--ink) !important;
}}
@media(max-width:800px) {{
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
    if st.session_state.get("invitado", False):
        return
    if not st.session_state.messages or not st.session_state.conv_id:
        return
    data = load_data()
    info = ensure_user_record(data, st.session_state.usuario)
    first = next((m["content"][:35] for m in st.session_state.messages if m["role"] == "user"), "Nueva charla")
    date_label = datetime.datetime.now().strftime("%d/%m %H:%M")
    info["convs"][st.session_state.conv_id] = {
        "title": first, "date": date_label, "messages": st.session_state.messages
    }
    save_data(data)

def render_chat(messages, user_avatar, assistant_avatar, display_name):
    pieces = ["<div class='chat-scroll'>"]
    if not messages:
        pieces.append(
            "<div style='text-align:center;padding:55px 10px;color:var(--ink);'>"
            "<div style='font-size:35px;'>💗 ✨ 🌷</div>"
            f"<h3>¡Hola {safe_text(display_name)}!</h3>"
            "<p>¿Qué resolvemos hoy?</p><p>Prueba una suma, una resta o una ecuación.</p></div>"
        )
    for msg in messages:
        role = "user" if msg.get("role") == "user" else "assistant"
        content = safe_text(msg.get("content", "")).replace("\n", "<br>")
        avatar = user_avatar if role == "user" else assistant_avatar
        if not avatar:
            avatar = ""
        img = (f"<img class='chat-avatar' src='{avatar}'>" if avatar else
               "<div class='chat-avatar' style='display:flex;align-items:center;justify-content:center;'>💗</div>")
        bubble = f"<div class='chat-bubble {role}'>{content}</div>"
        name = safe_text(display_name) if role == "user" else "Dumiluv"
        if role == "user":
            pieces.append(f"<div class='chat-line user'>{bubble}{img}</div>")
        else:
            pieces.append(f"<div class='chat-line assistant'>{img}<div><div class='chat-name'>{name}</div>{bubble}</div></div>")
    pieces.append("</div>")
    st.markdown("".join(pieces), unsafe_allow_html=True)

def es_consulta_matematica(texto, mensajes_previos=None):
    """Filtro inicial: permite matemáticas y preguntas de otras áreas con vínculo matemático."""
    texto_limpio = (texto or "").lower()
    palabras = re.findall(r"[a-záéíóúüñ]+", texto_limpio)
    temas = {
        "matemática", "matematicas", "matemáticas", "mate", "algebra", "álgebra",
        "ecuacion", "ecuación", "ecuaciones", "despejar", "despeje", "incognita", "incógnita",
        "variable", "variables", "expresion", "expresión", "polinomio", "factorizar",
        "factorización", "funcion", "función", "funciones", "geometria", "geometría",
        "trigonometria", "trigonometría", "calculo", "cálculo", "derivada", "integral",
        "fraccion", "fracción", "porcentaje", "porcentajes", "suma", "resta",
        "multiplicacion", "multiplicación", "division", "división", "potencia", "raiz", "raíz",
        "probabilidad", "estadistica", "estadística", "perimetro", "perímetro", "area", "área",
        "volumen", "angulo", "ángulo", "pendiente", "grafica", "gráfica", "sistema", "sistemas",
        "proporción", "proporcion", "regla", "tres", "ohm", "resistencia", "voltaje", "corriente",
        "formula", "fórmula", "calcular", "calcula", "calcula", "resolver", "resuelve", "resultado",
        "operacion", "operación", "numeros", "números", "numero", "número", "aritmetica", "aritmética"
    }
    if any(p in temas for p in palabras):
        return True
    # Notación matemática, por ejemplo 2x+5=11 o 3/4.
    if re.search(r"(?:\d\s*[xX*+\-/^=()]|[xX]\s*[+\-=]|\d\s*=)", texto_limpio):
        return True
    # Permite respuestas cortas del estudiante durante un ejercicio ya iniciado.
    for msg in reversed(mensajes_previos or []):
        if msg.get("role") == "assistant":
            contenido = msg.get("content", "").lower()
            contexto = ("ecuación", "ecuacion", "álgebra", "algebra", "matemát", "despej", "variable", "resultado", "operación", "operacion", "paso", "calcula")
            if any(p in contenido for p in contexto):
                return True
            break
    return False


def send_message(text):
    text = text.strip()
    if not text:
        return
    if not st.session_state.conv_id:
        nueva_conversacion()
    mensajes_previos = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": text})
    if not es_consulta_matematica(text, mensajes_previos):
        nombre = st.session_state.nombre_display or ""
        saludo = f" {safe_text(nombre)}" if nombre else ""
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                f"¡Hola{saludo}! 💗 Esa pregunta está fuera de mi especialidad. "
                "Soy Dumiluv y estoy diseñada para ayudarte con matemáticas y álgebra: "
                "ecuaciones, despejes, funciones, operaciones y problemas paso a paso. "
                "Si tu tarea es de otra materia, puedo ayudarte cuando incluya un cálculo, "
                "una fórmula, porcentajes o una ecuación. ¿Qué ejercicio matemático resolvemos? 🌷"
            )
        })
        guardar_conversacion()
        return
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Todavía falta configurar GROQ_API_KEY en los Secrets de Streamlit. Cuando esté configurada, podré ayudarte con el ejercicio. 💗"
        })
        guardar_conversacion()
        return
    try:
        client = Groq(api_key=api_key)
        display = st.session_state.nombre_display
        pronouns = st.session_state.pronombres
        gender = st.session_state.genero
        system_prompt = (
            f"Eres Dumiluv, una tutora personal de matemáticas para {display}. "
            f"Pronombres elegidos: {pronouns}. Dato opcional de género: {gender}. "
            "Usa el nombre de la persona de forma natural, especialmente al saludar o animarla, sin repetirlo en cada frase. "
            "TU ESPECIALIDAD EXCLUSIVA es matemáticas: aritmética, fracciones, porcentajes, potencias, raíces, álgebra, lenguaje algebraico, expresiones, ecuaciones, despejes, sistemas, funciones, geometría, trigonometría, estadística y problemas que se resuelvan con matemáticas. "
            "Si preguntan algo ajeno a matemáticas, explica amablemente que tu función es enseñar matemáticas; si existe una conexión matemática clara, explica solo esa conexión. No respondas como asistente general. "
            "MÉTODO INTERACTIVO: cuando te den un ejercicio, primero identifica qué se busca y explica brevemente la idea. Después plantea UN SOLO PASO y haz UNA pregunta concreta para que el estudiante lo intente. Espera su respuesta antes de avanzar. No reveles el resultado final ni todos los pasos de golpe, salvo que la persona pida explícitamente la solución completa. "
            "Cuando responda, revisa si su paso es correcto. Si acertó, felicítale brevemente y continúa con el siguiente paso. Si se equivoca, señala qué parte debe revisar, da una pista y permite que lo intente otra vez. Si sigue sin entender, explica ese paso con palabras sencillas y un ejemplo pequeño, y luego vuelve al ejercicio. "
            "En ecuaciones, trabaja una transformación por turno: por ejemplo, pregunta qué operación deshace una suma, luego comprueba el despeje y después continúa. Explica por qué se hace cada operación y conserva la igualdad en ambos lados. Comprueba el resultado al final. "
            "Traduce lenguaje cotidiano a lenguaje algebraico y al revés. Define las variables; explica qué significa 'el doble de un número más cinco' y cómo se representa. Distingue frases como 'el doble de la suma' y 'el doble de un número más cinco'. "
            "Si el mensaje es una respuesta a tu pregunta anterior, interpreta el contexto y evalúa ese intento, no empieces otro ejercicio. Mantén el hilo y recuerda los pasos anteriores. "
            "Tono cercano, paciente, motivador y claro. Usa español sencillo, formato legible y emojis moderados. Nunca inventes que el estudiante acertó: calcula y verifica. Si hay varias interpretaciones, pregunta. "
        )
        msgs = [{"role": "system", "content": system_prompt}] + st.session_state.messages
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=msgs,
            temperature=0.7
        )
        answer = response.choices[0].message.content or "No pude generar una respuesta. Inténtalo otra vez. 💗"
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as error:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"No pude conectarme en este momento. Revisa tu conexión o la clave de Groq. ({str(error)[:180]})"
        })
    guardar_conversacion()

# ---------- Pantalla de acceso / registro ----------
if not st.session_state.usuario:
    st.markdown("<div class='dumi-top'>⭐ Dumiluv 2.0 ✨</div>", unsafe_allow_html=True)
    st.markdown("<div class='dumi-panel' style='max-width:760px;margin:auto;text-align:center;'>"
                "<div style='font-size:48px;'>🐻‍❄️💗</div>"
                "<h2>Tu rinconcito para aprender</h2>"
                "<p>Inicia sesión, crea tu cuenta o entra como invitado.</p></div>",
                unsafe_allow_html=True)
    st.write("")
    tab_login, tab_create = st.tabs(["💗 Entrar", "🌷 Crear cuenta"])
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
                st.session_state.genero = info.get("gender", "Prefiero no decirlo")
                st.session_state.pronombres = info.get("pronouns", "Neutros (elle)")
                st.session_state.conv_id = None
                st.session_state.messages = []
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_create:
        st.markdown("<div class='dumi-panel'>", unsafe_allow_html=True)
        new_user = st.text_input("Crea un usuario (letras, números, punto o guion bajo)", key="create_user")
        new_display = st.text_input("¿Cómo quieres que te diga?", key="create_display")
        gender_options = ["Prefiero no decirlo", "Mujer", "Hombre", "No binario", "Otro"]
        new_gender = st.selectbox("Sexo o género (opcional)", gender_options, key="create_gender")
        pronoun_options = ["Ella", "Él", "Elle", "Neutros (elle)", "Otro / personalizado"]
        new_pronouns = st.selectbox("¿Qué pronombres quieres que use?", pronoun_options, key="create_pronouns")
        custom_pronouns = ""
        if new_pronouns == "Otro / personalizado":
            custom_pronouns = st.text_input("Escribe tus pronombres", placeholder="Ej. ella/elle")
        new_password = st.text_input("Contraseña", type="password", key="create_pass")
        repeat_password = st.text_input("Repite tu contraseña", type="password", key="create_pass2")
        st.caption("El sexo/género es opcional. Puedes elegir tus pronombres por separado.")
        if st.button("Crear cuenta y entrar 💖", use_container_width=True):
            if not re.match(r"^[a-zA-Z0-9._]+$", new_user):
                st.error("Usa solo letras, números, punto o guion bajo.")
            elif len(new_user) < 3:
                st.error("El usuario debe tener al menos 3 caracteres.")
            elif any(k.lower() == new_user.lower() for k in data):
                st.error("Ese usuario ya existe. Prueba con otro.")
            elif not new_password:
                st.error("Escribe una contraseña.")
            elif new_password != repeat_password:
                st.error("Las contraseñas no coinciden.")
            elif new_pronouns == "Otro / personalizado" and not custom_pronouns.strip():
                st.error("Escribe los pronombres que quieres usar.")
            else:
                pronouns_value = custom_pronouns.strip() if custom_pronouns.strip() else new_pronouns
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

    st.write("")
    st.markdown("<div class='dumi-panel' style='text-align:center;'>¿Solo quieres probarla? No necesitas registrarte.</div>", unsafe_allow_html=True)
    if st.button("Entrar sin cuenta 🌷", use_container_width=True):
        st.session_state.usuario = "Invitado-" + str(uuid.uuid4())[:8]
        st.session_state.nombre_display = "Invitado"
        st.session_state.genero = "Prefiero no decirlo"
        st.session_state.pronombres = "Neutros (elle)"
        st.session_state.invitado = True
        st.session_state.conv_id = None
        st.session_state.messages = []
        st.session_state.active_view = "chat"
        st.rerun()

    st.markdown("### 💌 Avisos, fallos y sugerencias")
    st.caption("Puedes escribir al equipo de Dumiluv desde tu aplicación de correo:")
    support_emails = ["7001467@etrr.edux", "7001464@etrr.edu.mx", "7001451@etrr.edu.mx", "7001529@etrr.edu.mx"]
    for address in support_emails:
        st.markdown(f"- [{address}](mailto:{address}?subject=Aviso%20o%20sugerencia%20para%20Dumiluv)")
    st.stop()

# ---------- Cargar datos de la cuenta ----------
data = load_data()
if st.session_state.get("invitado", False):
    user_info = {}
    convs = {}
    avatar_path = ""
else:
    user_info = ensure_user_record(data, st.session_state.usuario)
    save_data(data)
    convs = user_info.get("convs", {})
    avatar_path = user_info.get("avatar_path", "")
user_avatar = image_data_uri(avatar_path)
assistant_avatar = image_data_uri("dumiluv.png")

# ---------- Cabecera y navegación ----------
st.markdown(
    f"<div class='dumi-top'>🌷 Dumiluv <span style='font-size:15px;'>· {safe_text(st.session_state.nombre_display)} 💗</span></div>",
    unsafe_allow_html=True
)
nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.active_view = "chat"
        st.session_state.show_ajustes = False
        st.session_state.show_notas = False
        st.rerun()
with nav2:
    if st.button("⚙️ Ajustes", use_container_width=True):
        st.session_state.active_view = "settings"
        st.session_state.show_ajustes = True
        st.session_state.show_notas = False
        st.rerun()
with nav3:
    if st.button("➕ Nuevo chat", use_container_width=True):
        nueva_conversacion()
        st.session_state.active_view = "chat"
        st.rerun()
with nav4:
    if st.button("Salir", use_container_width=True):
        st.session_state.usuario = ""
        st.session_state.invitado = False
        st.session_state.nombre_display = ""
        st.session_state.messages = []
        st.session_state.conv_id = None
        st.session_state.active_view = "chat"
        st.rerun()

# ---------- Ajustes ----------
if st.session_state.active_view == "settings":
    st.markdown("<div class='dumi-panel'><div class='dumi-section'>⚙️ Ajustes de tu perfil</div>", unsafe_allow_html=True)
    st.write("")
    a1, a2 = st.columns([1, 2])
    with a1:
        if assistant_avatar:
            st.image("dumiluv.png", width=145)
        else:
            st.markdown("<div style='font-size:75px;text-align:center;'>💗</div>", unsafe_allow_html=True)
    with a2:
        display_name = st.text_input("Cómo quieres que te diga", value=st.session_state.nombre_display, key="settings_display")
        theme_names = ["pink", "purple", "blue", "orange", "green"]
        theme_labels = {"pink":"Rosa pastel", "purple":"Lila", "blue":"Azul cielo", "orange":"Durazno", "green":"Verde menta"}
        chosen_theme = st.selectbox(
            "Color del tema",
            theme_names,
            index=theme_names.index(st.session_state.tema),
            format_func=lambda x: theme_labels[x],
            key="settings_theme"
        )
        gender_options = ["Prefiero no decirlo", "Mujer", "Hombre", "No binario", "Otro"]
        current_gender = st.session_state.genero if st.session_state.genero in gender_options else "Prefiero no decirlo"
        chosen_gender = st.selectbox("Sexo o género (opcional)", gender_options, index=gender_options.index(current_gender), key="settings_gender")
        pronoun_options = ["Ella", "Él", "Elle", "Neutros (elle)", "Otro / personalizado"]
        current_pronouns = st.session_state.pronombres if st.session_state.pronombres in pronoun_options else "Otro / personalizado"
        chosen_pronouns = st.selectbox("Pronombres", pronoun_options, index=pronoun_options.index(current_pronouns), key="settings_pronouns")
        custom = ""
        if chosen_pronouns == "Otro / personalizado":
            custom = st.text_input("Tus pronombres", value="" if current_pronouns != "Otro / personalizado" else st.session_state.pronombres)
        uploaded_avatar = st.file_uploader("Foto de perfil", type=["png", "jpg", "jpeg"], key="profile_upload")
        if st.button("Guardar cambios 💗", use_container_width=True):
            st.session_state.nombre_display = display_name.strip() or st.session_state.usuario
            st.session_state.tema = chosen_theme
            st.session_state.genero = chosen_gender
            st.session_state.pronombres = (custom.strip() if chosen_pronouns == "Otro / personalizado" else chosen_pronouns)
            d = load_data()
            info = ensure_user_record(d, st.session_state.usuario)
            info["display"] = st.session_state.nombre_display
            info["gender"] = st.session_state.genero
            info["pronouns"] = st.session_state.pronombres
            if uploaded_avatar is not None:
                ext = uploaded_avatar.name.rsplit(".", 1)[-1].lower()
                path = os.path.join(AVATAR_FOLDER, f"{st.session_state.usuario}.{ext}")
                with open(path, "wb") as f:
                    f.write(uploaded_avatar.getbuffer())
                info["avatar_path"] = path
            save_data(d)
            st.success("¡Tus cambios se guardaron!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Notas ----------
elif st.session_state.active_view == "notes":
    st.markdown("<div class='dumi-panel'><div class='dumi-section'>📒 Mi libretita</div>", unsafe_allow_html=True)
    titles = [p["title"] for p in st.session_state.notas_pages]
    selected_title = st.selectbox("Elige una hoja", titles, index=min(st.session_state.notas_idx, len(titles)-1))
    st.session_state.notas_idx = titles.index(selected_title)
    n1, n2 = st.columns(2)
    with n1:
        if st.button("➕ Nueva hoja", use_container_width=True):
            nid = str(uuid.uuid4())[:6]
            st.session_state.notas_pages.append({"id": nid, "title": f"Hoja {len(st.session_state.notas_pages)+1}", "text": ""})
            st.session_state.notas_idx = len(st.session_state.notas_pages)-1
            st.rerun()
    with n2:
        if st.button("🗑️ Borrar hoja", use_container_width=True):
            if len(st.session_state.notas_pages) > 1:
                st.session_state.notas_pages.pop(st.session_state.notas_idx)
                st.session_state.notas_idx = 0
                st.rerun()
    current_page = st.session_state.notas_pages[st.session_state.notas_idx]
    current_page["text"] = st.text_area("Escribe tus apuntes", value=current_page["text"], height=150, key=f"note_{current_page['id']}")
    st.caption("También puedes dibujar en el espacio de abajo.")
    draw_mode = st.radio("Herramienta", ["Lápiz", "Borrador"], horizontal=True)
    st_canvas(
        stroke_width=3 if draw_mode == "Lápiz" else 18,
        stroke_color="#4d3b59" if draw_mode == "Lápiz" else "#ffffff",
        background_color="#ffffff",
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
            st.markdown("<div style='font-size:85px;'>🐻‍❄️</div>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='margin-bottom:0;color:var(--ink);'>Dumiluv</h4><p class='dumi-muted'>Tu asistente de matemáticas ✨</p>", unsafe_allow_html=True)
        if avatar_path and os.path.exists(avatar_path):
            st.image(avatar_path, width=75)
        st.markdown(f"<p style='font-weight:800;color:var(--ink);'>{safe_text(st.session_state.nombre_display)}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("<div class='dumi-panel'><b>💡 Recuerda</b><p class='dumi-muted'>Puedes preguntar paso a paso. ¡Aprender también puede ser divertido!</p></div>", unsafe_allow_html=True)

    with center:
        st.markdown("<div class='dumi-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='dumi-section'>💗 Conversación</div>", unsafe_allow_html=True)
        with st.expander("📒 Mis notas y dibujos (están aquí arriba del chat)", expanded=False):
            note_titles = [page["title"] for page in st.session_state.notas_pages]
            chosen_note = st.selectbox("Hoja", note_titles, index=min(st.session_state.notas_idx, len(note_titles)-1), key="chat_note_select")
            st.session_state.notas_idx = note_titles.index(chosen_note)
            note_col1, note_col2 = st.columns(2)
            with note_col1:
                if st.button("➕ Nueva hoja", key="chat_new_note", use_container_width=True):
                    new_id = str(uuid.uuid4())[:6]
                    st.session_state.notas_pages.append({"id": new_id, "title": f"Hoja {len(st.session_state.notas_pages)+1}", "text": ""})
                    st.session_state.notas_idx = len(st.session_state.notas_pages)-1
                    st.rerun()
            with note_col2:
                if st.button("🗑️ Borrar hoja", key="chat_delete_note", use_container_width=True):
                    if len(st.session_state.notas_pages) > 1:
                        st.session_state.notas_pages.pop(st.session_state.notas_idx)
                        st.session_state.notas_idx = 0
                        st.rerun()
            active_note = st.session_state.notas_pages[st.session_state.notas_idx]
            active_note["text"] = st.text_area("Apunta aquí mientras lees el ejercicio", value=active_note["text"], height=120, key=f"chat_note_text_{active_note['id']}")
            st.caption("También puedes dibujar operaciones o esquemas:")
            note_tool = st.radio("Herramienta", ["Lápiz", "Borrador"], horizontal=True, key="chat_note_tool")
            st_canvas(stroke_width=3 if note_tool == "Lápiz" else 18, stroke_color="#4d3b59" if note_tool == "Lápiz" else "#ffffff", background_color="#ffffff", height=190, drawing_mode="freedraw", key=f"chat_canvas_{active_note['id']}")
        render_chat(st.session_state.messages, user_avatar, assistant_avatar, st.session_state.nombre_display)

        if not st.session_state.messages:
            st.write("")
            st.caption("Prueba un ejercicio:")
            ex1, ex2 = st.columns(2)
            with ex1:
                if st.button("4 + 67", use_container_width=True):
                    send_message("4+67")
                    st.rerun()
                if st.button("Problema de edades", use_container_width=True):
                    send_message("La edad de una madre es 3 veces la de su hija y juntas suman 40. ¿Cómo lo resuelvo?")
                    st.rerun()
            with ex2:
                if st.button("x² - 5x + 6 = 0", use_container_width=True):
                    send_message("x^2 - 5x + 6 = 0")
                    st.rerun()
                if st.button("Pera y manzana", use_container_width=True):
                    send_message("Una pera cuesta 2 más que una manzana. Tres peras y dos manzanas cuestan 20. ¿Cómo lo resuelvo?")
                    st.rerun()

        st.write("")
        with st.form("chat_message_form", clear_on_submit=True):
            user_text = st.text_input("Mensaje", placeholder="Escribe un mensaje... 💗", label_visibility="collapsed", key="chat_input")
            submitted = st.form_submit_button("Enviar 💗", use_container_width=True)
        if submitted and user_text.strip():
            send_message(user_text)
            st.rerun()

        voice_col1, voice_col2 = st.columns([1, 3])
        with voice_col1:
            if st.button("🔊 Voz ON" if st.session_state.voz_activa else "🔇 Voz OFF", use_container_width=True):
                st.session_state.voz_activa = not st.session_state.voz_activa
                st.rerun()
        with voice_col2:
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.voz_activa:
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
        st.markdown("<div class='dumi-section'>🕘 Chat History</div>", unsafe_allow_html=True)
        if st.session_state.get("invitado", False):
            st.caption("Modo invitado: el historial no se guarda al salir.")
        if st.button("＋ Empezar conversación", use_container_width=True):
            nueva_conversacion()
            st.rerun()
        saved_convs = sorted(
            convs.items(),
            key=lambda item: item[1].get("date", ""),
            reverse=True
        )
        if not saved_convs:
            st.markdown("<p class='dumi-muted'>Tus conversaciones guardadas aparecerán aquí.</p>", unsafe_allow_html=True)
        for cid, conversation in saved_convs[:12]:
            label = conversation.get("title", "Nueva charla")
            date_label = conversation.get("date", "")
            if st.button(f"💬 {label[:24]} · {date_label}", key=f"history_{cid}", use_container_width=True):
                st.session_state.conv_id = cid
                st.session_state.messages = conversation.get("messages", [])
                st.session_state.active_view = "chat"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ---------- Contacto para fallos y sugerencias ----------
st.markdown("<div class='dumi-panel' style='margin-top:14px;'>", unsafe_allow_html=True)
st.markdown("### 💌 ¿Encontraste un fallo o tienes una sugerencia?")
st.caption("Escribe al equipo de Dumiluv. Se abrirá tu aplicación de correo.")
for address in ["7001467@etrr.edux", "7001464@etrr.edu.mx", "7001451@etrr.edu.mx", "7001529@etrr.edu.mx"]:
    st.markdown(f"- [{address}](mailto:{address}?subject=Fallo%20o%20sugerencia%20para%20Dumiluv)")
st.markdown("</div>", unsafe_allow_html=True)
