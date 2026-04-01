import streamlit as st
import database as db
import pandas as pd
import datetime
import plotly.express as px

def show_public_dashboard(login_callback):
    # Custom CSS to reduce top padding and align header
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
    """, unsafe_allow_html=True)

    # Layout: Header Section
    header_col1, header_col2, header_col3 = st.columns([1.2, 7.3, 1.5])
    
    with header_col1:
        st.image("logo_UNG.png", width=160)
        
    with header_col2:
        st.markdown("""
            <div style="display: flex; flex-direction: column; justify-content: center; height: 160px;">
                <h3 style="text-align: left; margin: 0; margin-top: -10px; font-weight: 800; color: #2c3e50; font-size: 30px;">UNIVERSITAS NEGERI GORONTALO</h3>
                <h1 style="text-align: center; margin-top: 5px; font-weight: 600; color: #2c3e50; font-size: 24px; letter-spacing: 1px;">SISTEM PEMINJAMAN LABORATORIUM</h1>
            </div>
        """, unsafe_allow_html=True)

    with header_col3:
        st.write("") 
        st.write("")
        st.write("")
        if st.button("🔐 Login", help="Masuk sebagai Staff atau Mahasiswa", use_container_width=True):
            login_callback()
            
    st.markdown("---")
    
    st.subheader("Jadwal Peminjaman Laboratorium")
    st.caption(f"Tanggal Hari Ini: {datetime.date.today().strftime('%d %B %Y')}")

    # Get data
    df = db.get_all_bookings()
    
    # Filter out rejected bookings
    if 'status' in df.columns:
        df = df[df['status'] != 'DITOLAK']
    
    # Filter for today and next 30 days (1 bulan)
    today = datetime.date.today()
    max_date = today + datetime.timedelta(days=31)
    
    # Ensure start_date and end_date are date objects
    df['start_date'] = pd.to_datetime(df['start_date']).dt.date
    df['end_date'] = pd.to_datetime(df['end_date']).dt.date
    
    # Display logic for 1 month
    # We show bookings where the rental period falls within [today, max_date]
    mask = (df['end_date'] >= today) & (df['start_date'] <= max_date)
    df_month = df.loc[mask].copy()

    if df_month.empty:
        st.info("Belum ada jadwal peminjaman untuk 1 bulan ke depan.")
    else:
        st.markdown("### 📅 Jadwal 1 Bulan ke Depan")
        
        df_month = df_month.sort_values(by=["start_date", "start_time"])
        
        def highlight_status(val):
            color = '#d4edda' if val == 'DISETUJUI' else '#fff3cd' if val == 'MENUNGGU' else '#f8d7da'
            return f'background-color: {color}'

        # Format full name, if not available use username
        if 'full_name' in df_month.columns:
            df_month['Peminjam'] = df_month['full_name'].fillna(df_month['username'])
        else:
            df_month['Peminjam'] = df_month['username']

        public_df = df_month[['start_date', 'end_date', 'start_time', 'end_time', 'lab_name', 'mata_kuliah', 'Peminjam', 'status']]
        public_df.columns = ['Tgl Mulai', 'Tgl Selesai', 'Jam Mulai', 'Jam Selesai', 'Laboratorium', 'Mata Kuliah', 'Peminjam', 'Status']
        
        st.dataframe(
            public_df.style.applymap(highlight_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )
        st.markdown("---")
