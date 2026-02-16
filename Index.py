
# cd /Users/CarmenJuanLlamas/Desktop/Bolitas_Python/
# pip install st-gsheets-connection
# streamlit run Index.py

import streamlit as st
import pandas as pd
import random
import os
import time
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE PANTALLA
# ==========================================
st.set_page_config(page_title="Experimento CIR", layout="centered")

# Inicializamos las variables si no existen
if 'paso' not in st.session_state:
    st.session_state.paso = 'CONFIG'
    st.session_state.aciertos = []
    st.session_state.trial_actual = 0
    st.session_state.feedback = None 
    st.session_state.mostrar_estimulo = True # Nueva variable para el tiempo

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
    if os.path.exists(ruta):
        st.image(ruta, use_container_width=True)

def guardar_local(datos):
    df = pd.DataFrame([datos])
    nombre_archivo = "resultados_locales.csv"
    df.to_csv(nombre_archivo, mode='a', header=not os.path.exists(nombre_archivo), index=False)
    st.info(f"Datos guardados en tu computadora: {nombre_archivo}")

# ==========================================
# 3. FLUJO DEL EXPERIMENTO
# ==========================================

# --- PANTALLA 1: CONFIGURACIÓN ---
if st.session_state.paso == 'CONFIG':
    st.title("Configuración Inicial")
    gen = st.radio("Seleccione Género:", ('W', 'M'))
    idioma = st.selectbox("Seleccione Idioma:", ['Spanish', 'English', 'Russian'])
    if st.button("Siguiente"):
        st.session_state.genero = gen
        st.session_state.lang_code = {'Spanish':'ES', 'English':'EN', 'Russian':'RU'}[idioma]
        #st.session_state.exp_type = 1 if gen == 'W' else random.choice([1, 5])
	# sólo experimentos 1 y 3 para cualquier sexo
        st.session_state.exp_type = random.choice([1, 3])
        st.session_state.paso = 'INSTRUCCIONES'
        st.rerun()

# --- PANTALLA 2: INSTRUCCIONES ---
elif st.session_state.paso == 'INSTRUCCIONES':
    mostrar_imagen('Static_Exp', st.session_state.lang_code)
    if st.button("Comenzar"):
        st.session_state.paso = 'FASE_ESTATICA'
        st.rerun()

# --- PANTALLA 3: FASE ESTÁTICA (CON CRONÓMETRO 1.5s) ---
elif st.session_state.paso == 'FASE_ESTATICA':
    
    # ¿Hay feedback? (OK / X)
    if st.session_state.feedback:
        if st.session_state.feedback == "OK":
            st.markdown("<h1 style='text-align: center; color: green; font-size: 150px;'>OK</h1>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='text-align: center; color: red; font-size: 150px;'>X</h1>", unsafe_allow_html=True)
        time.sleep(1.0)
        st.session_state.feedback = None
        st.session_state.mostrar_estimulo = True # Reset para el próximo ensayo
        st.rerun()

    st.write(f"Ensayo: {st.session_state.trial_actual + 1} / 80")
    
    if 'curr_ind' not in st.session_state:
        st.session_state.curr_ind = random.choice([1, 2, 3])
    
    ind = st.session_state.curr_ind
    pos_x = {1: "15%", 2: "50%", 3: "85%"}[ind]

    # ESPACIO PARA EL DIBUJO
    dibujo = st.empty()

    if st.session_state.mostrar_estimulo:
        # 1. MOSTRAR Círculo Rojo 1.5 segundos
        dibujo.markdown(f"""
            <div style="position: relative; height: 300px; background: #333; border-radius: 15px;">
                <div style="position: absolute; bottom: 20px; left: 50%; width: 40px; height: 40px; background: #00ff00; border-radius: 50%; transform: translateX(-50%);"></div>
                <div style="position: absolute; top: 40px; left: {pos_x}; width: 40px; height: 40px; background: red; border-radius: 50%; transform: translateX(-50%);"></div>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(1.5) # TIEMPO DE VISUALIZACIÓN
        st.session_state.mostrar_estimulo = False
        st.rerun()
    else:
        # 2. EL CÍRCULO ROJO DESAPARECE Y APARECEN BOTONES
        dibujo.markdown(f"""
            <div style="position: relative; height: 300px; background: #333; border-radius: 15px;">
                <div style="position: absolute; bottom: 20px; left: 50%; width: 40px; height: 40px; background: #00ff00; border-radius: 50%; transform: translateX(-50%);"></div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            up = st.button("⬆️ CHOCARÁN", use_container_width=True)
        with col2:
            down = st.button("⬇️ NO CHOCARÁN", use_container_width=True)

        if up or down:
            respuesta = "Up" if up else "Down"
            acierto = (respuesta == "Up" and ind == 2) or (respuesta == "Down" and ind != 2)
            st.session_state.aciertos.append(1 if acierto else 0)
            st.session_state.feedback = "OK" if acierto else "X"
            st.session_state.trial_actual += 1
            del st.session_state.curr_ind
            if st.session_state.trial_actual >= 80:
                st.session_state.paso = 'CUESTIONARIO'
            st.rerun()

# --- PANTALLA 4: CUESTIONARIO ---
elif st.session_state.paso == 'CUESTIONARIO':
    mostrar_imagen('Quest', st.session_state.lang_code)
    regla = st.text_area("Escribe la regla detectada:")
    if st.button("Finalizar"):
        datos = {
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Genero": st.session_state.genero,
            "Aciertos": sum(st.session_state.aciertos),
            "Regla": regla
        }
        guardar_local(datos)
        st.session_state.paso = 'FIN'
        st.rerun()

elif st.session_state.paso == 'FIN':
    mostrar_imagen('Good_Bye', st.session_state.lang_code)
    st.balloons()