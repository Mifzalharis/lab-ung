import streamlit as st
import database as db
import time
import datetime

def login_page(cookie_manager):
    st.markdown("## 🔐 Login System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            user = db.login_user(username, password)
            if user:
                # Set Session Cookie (No expiry = Cleared when browser closes)
                cookie_manager.set("lab_session_final", username)
                
                st.success(f"Selamat datang, {user['full_name']}!")
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = user
                time.sleep(1)
                st.rerun()
            else:
                st.error("Username atau password salah!")

def logout(cookie_manager):
    cookie_manager.delete("lab_session_final")
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = None
    st.session_state['logout_cooldown'] = True
    st.rerun()
