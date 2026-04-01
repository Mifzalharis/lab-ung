import streamlit as st
import database as db
import pandas as pd
import datetime
import modules.utils as utils

def show_dashboard(user_info):
    st.title(f"👋 Dashboard {user_info['role']}")
    
    tab1, tab2 = st.tabs(["📅 Buat Peminjaman", "📜 Riwayat Peminjaman"])
    
    with tab1:
        st.subheader("Form Peminjaman Laboratorium")
        
        # 1. Pilih Prodi (Auto-filled or selection)
        # 1. Program Studi (Otomatis dari Akun)
        prodi = user_info['prodi']
        st.info(f"📍 Program Studi: **{prodi}**")
        
        # 2. Pilih Lab
        labs_df = db.get_labs()
        # Create a dictionary to map name -> id
        lab_dict = dict(zip(labs_df.name, labs_df.id))
        selected_lab_name = st.selectbox("Pilih Ruang Laboratorium", list(lab_dict.keys()))
        selected_lab_id = lab_dict[selected_lab_name]
        
        # 3. Detail Mata Kuliah & Dosen
        col1, col2 = st.columns(2)
        with col1:
            matkul_options = [
                "Ergonomi dan Perancangan Kerja 2",
                "Perencanaan dan Pengedalian Produksi",
                "Elektronika Industri",
                "Simulasi Komputer",
                "Statistika",
                "Fisika Dasar",
                "Gambar Teknik Mesin",
                "Statistika Terapan Pendidikan"
            ]
            matkul = st.selectbox("Mata Kuliah", matkul_options)
            
            kelas = st.selectbox("Kelas", ["A", "B", "C"])
            today = datetime.date.today()
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("Tanggal Mulai", min_value=today)
            with col_d2:
                end_date = st.date_input("Tanggal Selesai", min_value=start_date)
        with col2:
            lecturers_df = db.get_lecturers()
            lecturer_dict = dict(zip(lecturers_df.name, lecturers_df.id))
            dosen_name = st.selectbox("Dosen Pengampu", list(lecturer_dict.keys()))
            dosen_id = lecturer_dict[dosen_name]
            
            time_slots = [
                "08.00 - 10.00",
                "10.00 - 12.00",
                "13.00 - 15.00",
                "15.00 - 17.00"
            ]
            selected_time = st.selectbox("Jam Praktikum", time_slots)
            

            
        if st.button("🚀 Ajukan Peminjaman"):
            durasi = (end_date - start_date).days + 1
            if not matkul or not dosen_id:
                st.warning("Mohon lengkapi data Mata Kuliah dan Dosen!")
            elif durasi > 31:
                st.error(f"Durasi peminjaman maksimal adalah 1 Bulan (31 Hari). Anda memilih {durasi} hari.")
            else:
                success, msg = db.create_booking(
                    user_info['username'], 
                    selected_lab_id, 
                    matkul, 
                    kelas,
                    dosen_id,
                    prodi, 
                    start_date,
                    end_date,
                    selected_time
                )
                if success:
                    st.success(msg)
                    st.toast(msg, icon='✅')
                else:
                    st.error(msg)
                    
    with tab2:
        st.subheader("Riwayat Peminjaman Saya")
        df = db.get_user_bookings(user_info['username'])
        
        if not df.empty:
            # Styling status
            def color_status(val):
                color = 'orange' if val == 'MENUNGGU' else 'green' if val == 'DISETUJUI' else 'red'
                return f'color: {color}; font-weight: bold'

            display_df = df[['start_date', 'end_date', 'start_time', 'lab_name', 'mata_kuliah', 'status']].copy()
            display_df.rename(columns={
                'start_date': 'Mulai', 
                'end_date': 'Selesai', 
                'start_time': 'Jam', 
                'lab_name': 'Lab', 
                'mata_kuliah': 'Mata Kuliah', 
                'status': 'Status'
            }, inplace=True)
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Show download button if any approved
            approved_bookings = df[df['status'] == 'DISETUJUI']
            if not approved_bookings.empty:
                st.markdown("### 📥 Unduh Bukti Peminjaman")
                for index, row in approved_bookings.iterrows():
                    pdf_bytes = utils.generate_pdf(row)
                    
                    if pdf_bytes:
                        st.download_button(
                            label=f"📄 Bukti - {row['mata_kuliah']} ({row['start_date']} s/d {row['end_date']})",
                            data=pdf_bytes,
                            file_name=f"bukti_peminjaman_{row['id']}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Gagal membuat PDF. Pastikan Microsoft Word terinstall di server/komputer ini.")
        else:
            st.info("Belum ada riwayat peminjaman.")
