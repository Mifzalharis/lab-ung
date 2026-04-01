import streamlit as st
import database as db

def show_master_dashboard(user_info):
    st.title("👑 Dashboard Master")
    
    st.subheader("Kelola Semua Akun Admin Laboratorium")
    
    # --- Add / Edit Form ---
    
    # State for editing
    if 'edit_master_data' not in st.session_state:
        st.session_state['edit_master_data'] = None
        
    with st.expander("➕ Tambah / Edit User", expanded=True):
        is_edit = st.session_state['edit_master_data'] is not None
        edit_data = st.session_state['edit_master_data']
        
        form_title = f"Edit User: {edit_data['username']}" if is_edit else "Tambah User Baru"
        st.markdown(f"**{form_title}**")
        
        with st.form("master_user_form"):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                new_username = st.text_input("Username (NIP)", value=edit_data['username'] if is_edit else "", disabled=is_edit)
                new_fullname = st.text_input("Nama Lengkap", value=edit_data['full_name'] if is_edit else "")
            with col_u2:
                new_role = st.selectbox("Role", ["Laboran"], index=0)
                new_prodi = st.selectbox("Divisi", ["Laboran"], index=0)
            
            new_password = st.text_input("Password (Biarkan kosong untuk Default: NIP)", type="password")
            
            submitted = st.form_submit_button("Simpan Data")
            
            if submitted:
                if not new_username or not new_fullname:
                    st.error("Username dan Nama Lengkap wajib diisi!")
                else:
                    if is_edit:
                        success, msg = db.edit_user(new_username, new_password, new_role, new_fullname, new_prodi)
                    else:
                        # Auto-set password to NIP if empty
                        final_password = new_password if new_password else new_username
                        success, msg = db.add_user(new_username, final_password, new_role, new_fullname, new_prodi)
                    
                    if success:
                        st.success(msg)
                        st.session_state['edit_master_data'] = None # Reset edit state
                        st.rerun()
                    elif msg:
                        st.error(msg)
                        
        if is_edit:
            if st.button("Batal Edit"):
                st.session_state['edit_master_data'] = None
                st.rerun()

    # --- User List ---
    st.write("---")
    st.markdown("### Daftar Admin Laboratorium")
    
    # Master only manages Laboran
    users_df = db.get_all_users(role_filter='Laboran')
    
    # Custom display with actions
    for index, row in users_df.iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 1, 1])
            c1.write(f"**{row['username']}**")
            c2.write(row['full_name'])
            
            # Styling for role to make it clear who is who
            role_color = "red" if row['role'] == "Master" else ("green" if row['role'] == "Laboran" else "blue")
            c3.markdown(f"<span style='color: {role_color}; font-weight: bold;'>{row['role']}</span> - {row['prodi']}", unsafe_allow_html=True)
            
            with c4:
                if st.button("✏️", key=f"mas_edit_{row['username']}", help="Edit User"):
                    st.session_state['edit_master_data'] = row.to_dict()
                    st.rerun()
            with c5:
                if st.button("🗑️", key=f"mas_del_{row['username']}", help="Hapus User"):
                     if st.button(f"Yakin hapus {row['username']}?", key=f"mas_confirm_{row['username']}"): 
                         pass 
                     
                     success, msg = db.delete_user(row['username'])
                     if success:
                         st.success(msg)
                         st.rerun()
                     else:
                         st.error(msg)
            st.divider()
