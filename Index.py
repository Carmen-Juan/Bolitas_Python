
# cd /Users/CarmenJuanLlamas/Desktop/Bolitas_Python/
# pip install st-gsheets-connection
# streamlit run Index.py
# git init
# git add Index.py
# git commit -m "Finalizando conexion con gsheets"
# git push origin main
# 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
# https://bolitaspython.streamlit.app
# https://docs.google.com/spreadsheets/d/1bAFWEitjrv7HXjD03t9kmXhGPwd1NOZoZGvtLBM5JMk/edit?gid=438199380#gid=438199380
# open -e .streamlit/secrets.toml

import streamlit as st
import pandas as pd
import random
import os
import time
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection


# ==========================================
# 1. CONFIGURACIÓN DE PANTALLA
# ==========================================
st.set_page_config(page_title="Experimento CIR", layout="wide", initial_sidebar_state="collapsed")

# CSS CORREGIDO:
# 1. He aumentado 'padding-top' en .block-container para bajar todo el contenido.
# 2. He añadido 'margin-top' a la etiqueta img para dar aire extra a las fotos.
st.markdown("""
    <style>
    /* Ajuste global: Aumentado el padding superior de 1rem a 6rem para bajar todo */
    .block-container {
        padding-top: 6rem !important;
        padding-bottom: 0rem !important;
        max-height: 100vh;
        overflow: hidden;
    }
    
    /* Imagen dinámica: Se adapta al alto de tu navegador Mac */
    /* Añadido margin-top para separar del techo */
    img {
        max-height: 45vh !important; 
        width: auto !important;
        margin: 20px auto !important; 
        display: block;
        object-fit: contain;
    }

    /* Botones centrados y grandes */
    div.stButton > button {
        width: 100%;
        height: 60px !important;
        font-size: 20px !important;
        background-color: #28a745 !important;
        color: white !important;
    }

    /* Cuadro de texto del cuestionario */
    .stTextArea textarea {
        height: 80px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES ---
if 'paso' not in st.session_state:
    st.session_state.paso = 'LOGIN'
    st.session_state.autenticado = False
    st.session_state.aciertos = []
    st.session_state.trial_actual = 0
    st.session_state.feedback = None 
    st.session_state.mostrar_estimulo = True
    
# ==========================================
# 2. FUNCIONES
# ==========================================
def mostrar_imagen(nombre_tipo, lang_code):
    nombres = {
        'Static_Exp': f"Static_{lang_code}_Exp5.png",
        'Quest': f"Static_Quest_{lang_code}_3.png",
        'Good_Bye': f"Good_Bye_{lang_code}_3.png"
    }
    archivo = nombres.get(nombre_tipo)
    ruta = f"Images_3/{archivo}"
    
    # Verificación simple para no romper si falta la imagen
    if os.path.exists(ruta):
        st.image(ruta, use_container_width=True)
    else:
        st.warning(f"Imagen no encontrada: {ruta}")

def guardar_local(datos):
    """Guarda en un CSV local por si falla Google Sheets"""
    df = pd.DataFrame([datos])
    nombre_archivo = "resultados_locales.csv"
    df.to_csv(nombre_archivo, mode='a', header=not os.path.exists(nombre_archivo), index=False)
    st.info(f"Aviso: Datos guardados localmente (CSV). Error de conexión.")

def guardar_en_gsheets(datos):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        try:
            existing_data = conn.read(ttl=0)
            if existing_data is None:
                existing_data = pd.DataFrame()
        except Exception as e:
            # Si falla al leer, que nos diga por qué en pantalla
            st.warning(f"Aviso al leer: {e}")
            existing_data = pd.DataFrame()

        new_data = pd.DataFrame([datos])
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        
        conn.update(data=updated_data)
        st.success("¡Datos enviados correctamente!")
        
    except Exception as e:
        # ESTA ES LA PARTE IMPORTANTE:
        # Si hay un fallo de permisos o de clave, saldrá en ROJO en la app
        st.error(f"FALLO CRÍTICO DE CONEXIÓN: {e}")
        guardar_local(datos)
        

# ==========================================
# 3. FLUJO DEL EXPERIMENTO
# ==========================================

# --- PANTALLA 0: LOGIN ---
if st.session_state.paso == 'LOGIN':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Espaciador extra por si acaso
        st.write("") 
        st.markdown("<h2 style='text-align: center;'>Acceso Restringido</h2>", unsafe_allow_html=True)
        
        # El campo de contraseña
        password = st.text_input("Introduce la contraseña para comenzar:", type="password")
        
        if st.button("Entrar"):
            if password == "Capibara":  # <--- NUEVA CONTRASEÑA
                st.session_state.autenticado = True
                st.session_state.paso = 'CONFIG'
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()
    
# PANTALLA 1 (CONFIGURACIÓN)
if st.session_state.paso == 'CONFIG':
    st.title("Configuración Inicial")
    gen = st.radio("Seleccione Género:", ('W', 'M'))
    idioma = st.selectbox("Seleccione Idioma:", ['Spanish', 'English'])
    if st.button("Siguiente"):
        st.session_state.genero = gen
        st.session_state.lang_code = {'Spanish':'ES', 'English':'EN'}[idioma]
        st.session_state.exp_type = random.choice([1, 3])
        st.session_state.paso = 'INSTRUCCIONES'
        st.rerun()


# --- PANTALLA 2: INSTRUCCIONES ---
elif st.session_state.paso == 'INSTRUCCIONES':
    # Usamos columnas para que la imagen no ocupe todo el ancho y se vea completa
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mostrar_imagen('Static_Exp', st.session_state.lang_code)
        
        if st.button("¡ENTENDIDO, EMPEZAR!"):
            st.session_state.paso = 'FASE_ESTATICA'
            st.rerun()

    # Script de tecla
    components.html("""
        <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            const btn = Array.from(doc.querySelectorAll('button')).find(el => el.innerText.includes('ENTENDIDO'));
            if (btn) btn.click();
        });
        </script>
    """, height=0)

# PANTALLA 3 (ZONA DE JUEGO AMPLIADA Y BLANCA)
elif st.session_state.paso == 'FASE_ESTATICA':
    
    if st.session_state.feedback:
        color = "green" if st.session_state.feedback == "OK" else "red"
        # Ajustado margin-top aquí también para el feedback
        st.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 250px; margin-top: 150px;'>{st.session_state.feedback}</h1>", unsafe_allow_html=True)
        time.sleep(1.0)
        st.session_state.feedback = None
        st.session_state.mostrar_estimulo = True 
        st.rerun()

    if 'curr_ind' not in st.session_state:
        st.session_state.curr_ind = random.choice([1, 2, 3])
    
    ind = st.session_state.curr_ind
    # Ajustamos el ancho: las bolitas laterales ahora están más separadas (10% y 90%)
    pos_x = {1: "10%", 2: "50%", 3: "90%"}[ind]

    dibujo = st.empty()

    # Lienzo de juego: Blanco, muy alto (700px) y ocupando todo el ancho
    if st.session_state.mostrar_estimulo:
        dibujo.markdown(f"""
            <div style="position: relative; height: 700px; background: white; border: 1px solid #f0f0f0; width: 100%; border-radius: 20px;">
                <div style="position: absolute; bottom: 60px; left: 50%; width: 80px; height: 80px; background: #00FF00; border-radius: 50%; transform: translateX(-50%); box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></div>
                <div style="position: absolute; top: 60px; left: {pos_x}; width: 80px; height: 80px; background: #FF0000; border-radius: 50%; transform: translateX(-50%); box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></div>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1.5) 
        st.session_state.mostrar_estimulo = False
        st.rerun()
    else:
        # Solo queda la bola verde para responder
        dibujo.markdown(f"""
            <div style="position: relative; height: 700px; background: white; border: 1px solid #f0f0f0; width: 100%; border-radius: 20px;">
                <div style="position: absolute; bottom: 60px; left: 50%; width: 80px; height: 80px; background: #00FF00; border-radius: 50%; transform: translateX(-50%);"></div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            up = st.button("⬆️", use_container_width=True)
        with col2:
            down = st.button("⬇️", use_container_width=True)

        if up or down:
            respuesta = "Up" if up else "Down"
            acierto = (respuesta == "Up" and ind == 2) or (respuesta == "Down" and ind != 2)
            st.session_state.aciertos.append(1 if acierto else 0)
            st.session_state.feedback = "OK" if acierto else "X"
            st.session_state.trial_actual += 1
            del st.session_state.curr_ind
            
            # Cambia este 3 por el número real de ensayos que quieras
            if st.session_state.trial_actual >= 3: 
                st.session_state.paso = 'CUESTIONARIO'
            st.rerun()

# --- PANTALLA 4: CUESTIONARIO ---
elif st.session_state.paso == 'CUESTIONARIO':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mostrar_imagen('Quest', st.session_state.lang_code)
        
        st.markdown("<h4 style='text-align: center;'>Escribe la regla detectada:</h4>", unsafe_allow_html=True)
        regla = st.text_area("", label_visibility="collapsed")
        
        # Al pulsar el botón, creamos los datos y enviamos
        if st.button("FINALIZAR Y ENVIAR"):
            datos_finales = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Genero": st.session_state.genero,
                #"Experimento": st.session_state.exp_type,
                "Aciertos": sum(st.session_state.aciertos),
                "Regla": regla
                #"Regla_Estática": regla,
                #"Regla_Dinámica": "nada"
            }
            # LLAMADA A LA FUNCIÓN QUE FALTABA
            guardar_en_gsheets(datos_finales)
            
            st.session_state.paso = 'FIN'
            st.rerun()
            

# --- PANTALLA 5: DESPEDIDA ---
elif st.session_state.paso == 'FIN':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mostrar_imagen('Good_Bye', st.session_state.lang_code)
        st.markdown("<h2 style='text-align: center;'>¡Gracias por jugar!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Presiona <b>H</b> para volver al inicio</p>", unsafe_allow_html=True)

    # Creamos un botón invisible o un checkbox oculto que Streamlit detecte
    # Si 'volver' cambia a True, reiniciamos.
    if st.checkbox("Logica_H", key="hidden_h", label_visibility="collapsed"):
        st.session_state.clear()
        st.session_state.paso = 'LOGIN'
        st.rerun()

    # JS que busca el checkbox oculto y le hace click
    components.html("""
        <script>
        const doc = window.parent.document;
        const handleKeyDown = (e) => {
            if (e.key.toLowerCase() === 'h') {
                // Buscamos el input del checkbox oculto
                const checkbox = doc.querySelector('input[aria-label="Logica_H"]');
                if (checkbox) checkbox.click();
            }
        };
        doc.addEventListener('keydown', handleKeyDown);
        </script>
    """, height=0)