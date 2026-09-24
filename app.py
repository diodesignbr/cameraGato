import streamlit as st
import cv2
from onvif import ONVIFCamera
import threading
import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# Configurações da Câmara
CAMERA_IP = "192.168.0.94"
CAMERA_PORT = 80
USERNAME = "diomartins83@gmail.com"
PASSWORD = "Mlp0nko9!"

STREAM_HD = f"rtsp://{USERNAME}:{PASSWORD}@{CAMERA_IP}:554/0/av0"
STREAM_SD = f"rtsp://{USERNAME}:{PASSWORD}@{CAMERA_IP}:554/0/av1"

st.set_page_config(page_title="Monitor IP Web", page_icon="📷", layout="centered")

st.title("📷 Painel de Controlo - Câmara IP")

# Inicializar estado da sessão no Streamlit
if "quality" not in st.session_state:
    st.session_state.quality = "HD"
if "zoom" not in st.session_state:
    st.session_state.zoom = 1.0

# Conexão ONVIF para PTZ
@st.cache_resource
def conectar_onvif():
    try:
        mycam = ONVIFCamera(CAMERA_IP, CAMERA_PORT, USERNAME, PASSWORD)
        ptz = mycam.create_ptz_service()
        media = mycam.create_media_service()
        token = media.GetProfiles()[0].token
        return ptz, token
    except Exception as e:
        return None, None

ptz, token = conectar_onvif()

def mover_ptz(pan, tilt):
    if ptz and token:
        try:
            req = ptz.create_type('ContinuousMove')
            req.ProfileToken = token
            req.Velocity = {'PanTilt': {'x': pan, 'y': tilt}}
            ptz.ContinuousMove(req)
        except Exception:
            pass

def parar_ptz():
    if ptz and token:
        try:
            req = ptz.create_type('Stop')
            req.ProfileToken = token
            req.PanTilt = True
            req.Zoom = True
            ptz.Stop(req)
        except Exception:
            pass

# --- CONTROLOS DA INTERFACE WEB ---
col_q1, col_q2 = st.columns(2)
with col_q1:
    if st.button("📡 Alternar para HD"):
        st.session_state.quality = "HD"
with col_q2:
    if st.button("📡 Alternar para SD"):
        st.session_state.quality = "SD"

st.write(f"Modo atual: **{st.session_state.quality}**")

# Secção de Direção PTZ (Grid em Streamlit)
st.markdown("### Controlo PTZ")
col1, col2, col3 = st.columns(3)

with col2:
    if st.button("▲ Cima"):
        mover_ptz(0.0, 0.5)

col_l, col_s, col_r = st.columns(3)
with col_l:
    if st.button("◀ Esquerda"):
        mover_ptz(-0.5, 0.0)
with col_s:
    if st.button("■ Parar"):
        parar_ptz()
with col_r:
    if st.button("▶ Direita"):
        mover_ptz(0.5, 0.0)

with col2:
    if st.button("▼ Baixo"):
        mover_ptz(0.0, -0.5)

# --- CAPTURA DE VÍDEO ---
stream_url = STREAM_HD if st.session_state.quality == "HD" else STREAM_SD
cap = cv2.VideoCapture(stream_url)

ret, frame = cap.read()
if ret:
    # Converter BGR para RGB para exibição correta no Streamlit
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    st.image(frame_rgb, channels="RGB", use_container_width=True)
else:
    st.error("Não foi possível ligar ao fluxo de vídeo da câmara. Verifique se o IP está acessível na mesma rede.")

cap.release()