import streamlit as st
from streamlit_option_menu import option_menu
import extra_streamlit_components as stx
import modules.auth as auth
import modules.dashboard as dashboard
import modules.admin as admin
import modules.master as master
import modules.public_dashboard as public_dashboard
import database as db

# Page Config
st.set_page_config(
    page_title="Sistem Peminjaman Laboratorium UNG",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Colorful & Interactive" look
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Center sidebar logo */
    [data-testid="stSidebar"] > div > div > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    .stButton>button {
        background-color: #4CAF50; 
        color: white; 
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #0d6efd;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None
if 'show_login' not in st.session_state:
    st.session_state['show_login'] = False

def main():
    # Cookie Manager Init
    cookie_manager = stx.CookieManager()

    # NOTE: User requested strict no-auto-login on startup. 
    # Persistence is disabled to ensure security and public-dashboard-first flow.

    if not st.session_state['logged_in']:
        if st.session_state['show_login']:
            if st.button("⬅️ Kembali ke Dashboard Publik"):
                st.session_state['show_login'] = False
                st.rerun()
            auth.login_page(cookie_manager)
        else:
            public_dashboard.show_public_dashboard(
                login_callback=lambda: st.session_state.update({'show_login': True})
            )
            if st.session_state.get('show_login'):
                st.rerun()
            
    else:
        user = st.session_state['user_info']
        
        # Sidebar Logo
        with st.sidebar:
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image("logo_UNG.png", use_container_width=True)
            
            st.write(f"Halo, **{user['full_name']}**")
            st.caption(f"Role: {user['role']}")
            
            menu_options = ["Dashboard", "Logout"]
            icons = ["house", "box-arrow-right"]
            
            selected = option_menu(
                menu_title="Menu Utama",
                options=menu_options,
                icons=icons,
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "#fafafa"},
                    "icon": {"color": "orange", "font-size": "20px"}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
        
        if selected == "Logout":
            auth.logout(cookie_manager)
        elif selected == "Dashboard":
            if user['role'] == 'Master':
                master.show_master_dashboard(user)
            elif user['role'] == 'Laboran':
                admin.show_admin_dashboard(user)
            else:
                dashboard.show_dashboard(user)

if __name__ == "__main__":
    main()
