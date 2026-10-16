import streamlit as st
import sqlite3
import hashlib


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="User Authentication & CRUD",
    page_icon="🔐",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

DATABASE = "database.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT
        )
    """)

    conn.commit()
    conn.close()


create_tables()


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =========================================================
# SIGN UP
# =========================================================

def create_user(username, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        password = hash_password(password)

        cursor.execute("""
            INSERT INTO users
            (username, email, password)
            VALUES (?, ?, ?)
        """, (
            username,
            email,
            password
        ))

        conn.commit()

        return True, "Account created successfully!"

    except sqlite3.IntegrityError:

        return False, "Username or email already exists."

    finally:

        conn.close()


# =========================================================
# LOGIN
# =========================================================

def check_login(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    password = hash_password(password)

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
        AND password = ?
    """, (
        username,
        password
    ))

    user = cursor.fetchone()

    conn.close()

    return user


# =========================================================
# CREATE RECORD
# =========================================================

def create_record(username, title, description, category):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO records
        (username, title, description, category)
        VALUES (?, ?, ?, ?)
    """, (
        username,
        title,
        description,
        category
    ))

    conn.commit()
    conn.close()


# =========================================================
# READ RECORDS
# =========================================================

def get_records(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, category
        FROM records
        WHERE username = ?
        ORDER BY id DESC
    """, (username,))

    records = cursor.fetchall()

    conn.close()

    return records


# =========================================================
# UPDATE RECORD
# =========================================================

def update_record(
    record_id,
    title,
    description,
    category
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE records
        SET title = ?,
            description = ?,
            category = ?
        WHERE id = ?
    """, (
        title,
        description,
        category,
        record_id
    ))

    conn.commit()
    conn.close()


# =========================================================
# DELETE RECORD
# =========================================================

def delete_record(record_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM records
        WHERE id = ?
    """, (record_id,))

    conn.commit()
    conn.close()


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "username" not in st.session_state:

    st.session_state.username = ""


# =========================================================
# LOGIN / SIGNUP PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title("🔐 User Authentication System")

    st.write(
        "Create an account or login to access your dashboard."
    )

    st.divider()

    login_tab, signup_tab = st.tabs([
        "🔑 Login",
        "📝 Sign Up"
    ])


    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader("Login")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if username == "" or password == "":

                st.warning(
                    "Please enter username and password."
                )

            else:

                user = check_login(
                    username,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.username = username

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password."
                    )


    # =====================================================
    # SIGN UP
    # =====================================================

    with signup_tab:

        st.subheader("Create Account")

        new_username = st.text_input(
            "Username",
            key="signup_username"
        )

        new_email = st.text_input(
            "Email",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if (
                new_username == ""
                or new_email == ""
                or new_password == ""
            ):

                st.warning(
                    "Please fill all fields."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, message = create_user(
                    new_username,
                    new_email,
                    new_password
                )

                if success:

                    st.success(message)

                    st.info(
                        "Now go to the Login tab."
                    )

                else:

                    st.error(message)


# =========================================================
# DASHBOARD
# =========================================================

else:

    username = st.session_state.username


    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.title("📊 Dashboard")

        st.write(
            f"Welcome, **{username}** 👋"
        )

        st.divider()

        menu = st.radio(
            "Select Operation",
            [
                "🏠 Home",
                "➕ Create",
                "📖 Read",
                "✏️ Update",
                "🗑️ Delete"
            ]
        )

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.username = ""

            st.rerun()


    # =====================================================
    # HOME
    # =====================================================

    if menu == "🏠 Home":

        st.title("🏠 Dashboard")

        st.subheader(
            f"Hello {username}! 👋"
        )

        records = get_records(username)

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Records",
                len(records)
            )

        with col2:

            st.metric(
                "Account",
                "Active"
            )

        with col3:

            st.metric(
                "CRUD",
                "Enabled"
            )

        st.divider()

        st.info(
            "Use the sidebar to manage your records."
        )


    # =====================================================
    # CREATE
    # =====================================================

    elif menu == "➕ Create":

        st.title("➕ Create New Record")

        title = st.text_input(
            "Title"
        )

        description = st.text_area(
            "Description"
        )

        category = st.selectbox(
            "Category",
            [
                "Personal",
                "College",
                "Work",
                "Project",
                "Other"
            ]
        )

        if st.button(
            "Create Record",
            type="primary"
        ):

            if title == "":

                st.warning(
                    "Please enter a title."
                )

            else:

                create_record(
                    username,
                    title,
                    description,
                    category
                )

                st.success(
                    "Record created successfully!"
                )

                st.rerun()


    # =====================================================
    # READ
    # =====================================================

    elif menu == "📖 Read":

        st.title("📖 View Records")

        records = get_records(username)

        if len(records) == 0:

            st.info(
                "No records found."
            )

        else:

            for record in records:

                record_id = record[0]
                title = record[1]
                description = record[2]
                category = record[3]

                with st.expander(
                    f"#{record_id} - {title}"
                ):

                    st.write(
                        f"**Description:** {description}"
                    )

                    st.write(
                        f"**Category:** {category}"
                    )


    # =====================================================
    # UPDATE
    # =====================================================

    elif menu == "✏️ Update":

        st.title("✏️ Update Record")

        records = get_records(username)

        if len(records) == 0:

            st.info(
                "No records available."
            )

        else:

            record_names = [
                f"{r[0]} - {r[1]}"
                for r in records
            ]

            selected_record = st.selectbox(
                "Select Record",
                record_names
            )

            selected_id = int(
                selected_record.split(" - ")[0]
            )

            selected_data = None

            for record in records:

                if record[0] == selected_id:

                    selected_data = record
                    break


            new_title = st.text_input(
                "Title",
                value=selected_data[1]
            )

            new_description = st.text_area(
                "Description",
                value=selected_data[2] or ""
            )

            categories = [
                "Personal",
                "College",
                "Work",
                "Project",
                "Other"
            ]

            if selected_data[3] in categories:

                category_index = categories.index(
                    selected_data[3]
                )

            else:

                category_index = 0


            new_category = st.selectbox(
                "Category",
                categories,
                index=category_index
            )


            if st.button(
                "Update Record",
                type="primary"
            ):

                update_record(
                    selected_id,
                    new_title,
                    new_description,
                    new_category
                )

                st.success(
                    "Record updated successfully!"
                )

                st.rerun()


    # =====================================================
    # DELETE
    # =====================================================

    elif menu == "🗑️ Delete":

        st.title("🗑️ Delete Record")

        records = get_records(username)

        if len(records) == 0:

            st.info(
                "No records available."
            )

        else:

            record_names = [
                f"{r[0]} - {r[1]}"
                for r in records
            ]

            selected_record = st.selectbox(
                "Select Record",
                record_names
            )

            selected_id = int(
                selected_record.split(" - ")[0]
            )

            st.warning(
                "⚠️ This record will be permanently deleted."
            )

            if st.button(
                "Delete Record",
                type="primary"
            ):

                delete_record(
                    selected_id
                )

                st.success(
                    "Record deleted successfully!"
                )

                st.rerun()