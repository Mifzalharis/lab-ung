import streamlit as st
import database as db
import pandas as pd

def show_admin_dashboard(user_info):
    st.title("🛡️ Dashboard Admin")
    
    tab1, tab2, tab3 = st.tabs(["⏳ Perlu Persetujuan", "📊 Semua Jadwal", "👥 Manajemen User"])
    
    df = db.get_all_bookings()
    
    with tab1:
        st.subheader("Peminjaman Menunggu Persetujuan")
        pending_bookings = df[df['status'] == 'MENUNGGU']
        
        if not pending_bookings.empty:
            for index, row in pending_bookings.iterrows():
                with st.expander(f"{row['start_date']} s/d {row['end_date']} | {row['lab_name']} - {row['username']}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Matkul:** {row['mata_kuliah']}")
                        st.write(f"**Jam:** {row['start_time']} - {row['end_time']}")
                        st.write(f"**Dosen:** {row['dosen_pengampu']}")
                    with col2:
                        if st.button("✅ Terima", key=f"acc_{row['id']}"):
                            db.update_booking_status(row['id'], 'DISETUJUI')
                            st.success("Disetujui!")
                            st.rerun()
                    with col3:
                        if st.button("❌ Tolak", key=f"rej_{row['id']}"):
                            db.update_booking_status(row['id'], 'DITOLAK')
                            st.error("Ditolak!")
                            st.rerun()
        else:
            st.info("Tidak ada peminjaman yang menunggu persetujuan.")
            
    with tab2:
        st.subheader("Jadwal Laboratorium Lengkap")
        st.dataframe(df, use_container_width=True)
        
    with tab3:
        st.subheader("Kelola Akun Pengguna")
        
        # --- Add / Edit Form ---
        
        # State for editing
        if 'edit_user_data' not in st.session_state:
            st.session_state['edit_user_data'] = None
            
        with st.expander("➕ Tambah / Edit User", expanded=True):
            is_edit = st.session_state['edit_user_data'] is not None
            edit_data = st.session_state['edit_user_data']
            
            form_title = f"Edit User: {edit_data['username']}" if is_edit else "Tambah User Baru"
            st.markdown(f"**{form_title}**")
            
            with st.form("user_form"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    new_username = st.text_input("Username (NIM)", value=edit_data['username'] if is_edit else "", disabled=is_edit)
                    new_fullname = st.text_input("Nama Lengkap", value=edit_data['full_name'] if is_edit else "")
                with col_u2:
                    new_role = st.selectbox("Role", ["Mahasiswa"], index=0)
                    prodi_options = ["Teknik Industri", "Pendidikan Teknik Mesin", "Umum"]
                    
                    # Handle existing prodi selection
                    default_prodi_index = 0
                    if is_edit and edit_data['prodi'] in prodi_options:
                        default_prodi_index = prodi_options.index(edit_data['prodi'])
                    
                    new_prodi = st.selectbox("Program Studi", prodi_options, index=default_prodi_index)
                
                new_password = st.text_input("Password (Biarkan kosong untuk Default: NIM)", type="password")
                
                submitted = st.form_submit_button("Simpan Data")
                
                if submitted:
                    if not new_username or not new_fullname:
                        st.error("Username dan Nama Lengkap wajib diisi!")
                    else:
                        if is_edit:
                            success, msg = db.edit_user(new_username, new_password, new_role, new_fullname, new_prodi)
                        else:
                            # Auto-set password to NIM if empty
                            final_password = new_password if new_password else new_username
                            success, msg = db.add_user(new_username, final_password, new_role, new_fullname, new_prodi)
                        
                        if success:
                            st.success(msg)
                            st.session_state['edit_user_data'] = None # Reset edit state
                            st.rerun()
                        elif msg:
                            st.error(msg)
                            
            if is_edit:
                if st.button("Batal Edit"):
                    st.session_state['edit_user_data'] = None
                    st.rerun()

        # --- User List ---
        st.write("---")
        st.markdown("### Daftar Pengguna")
        
        users_df = db.get_all_users(role_filter='Mahasiswa')
        
        # Custom display with actions
        for index, row in users_df.iterrows():
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 1, 1])
                c1.write(f"**{row['username']}**")
                c2.write(row['full_name'])
                c3.write(f"{row['role']} - {row['prodi']}")
                
                with c4:
                    if st.button("✏️", key=f"edit_{row['username']}", help="Edit User"):
                        st.session_state['edit_user_data'] = row.to_dict()
                        st.rerun()
                with c5:
                    if st.button("🗑️", key=f"del_{row['username']}", help="Hapus User"):
                         if st.button(f"Yakin hapus {row['username']}?", key=f"confirm_{row['username']}"): # Double confirm trick
                             pass # Logic handled below slightly differently for cleaner UI, but let's stick to direct action for now
                         
                         # Direct delete for simplicity requested
                         success, msg = db.delete_user(row['username'])
                         if success:
                             st.success(msg)
                             st.rerun()
                         else:
                             st.error(msg)
                st.divider()
