"""
auth.py — User Authentication for SmartEstate AI
"""
import json
import os
import streamlit as st
import hashlib
from datetime import datetime

USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.json")


def _load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_email(email: str):
    users = _load_users()
    for u in users:
        if u["email"].lower() == email.lower():
            return u
    return None


def get_user_by_id(user_id: str):
    users = _load_users()
    for u in users:
        if u["id"] == user_id:
            return u
    return None


def login(email: str, password: str):
    """Returns user dict if login valid, else None."""
    users = _load_users()
    for u in users:
        if u["email"].lower() == email.lower():
            # Support both plain text (legacy) and hashed passwords
            if u["password"] == password or u["password"] == _hash_password(password):
                return u
    return None


def register(name: str, email: str, phone: str, password: str, role: str = "owner"):
    """Register new user. Returns (success: bool, message: str)"""
    users = _load_users()
    if any(u["email"].lower() == email.lower() for u in users):
        return False, "Email already registered!"
    if any(u["phone"] == phone for u in users):
        return False, "Phone number already registered!"
    new_user = {
        "id": f"user_{len(users)+1:03d}_{int(datetime.now().timestamp())}",
        "name": name,
        "email": email,
        "phone": phone,
        "password": _hash_password(password),
        "role": role,
        "kyc_verified": False,
        "whatsapp": phone,
        "wishlist": [],
        "saved_searches": [],
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "active": True
    }
    users.append(new_user)
    _save_users(users)
    return True, "Account created successfully!"


def update_wishlist(user_id: str, prop_id: str, add: bool = True):
    """Add or remove property from wishlist."""
    users = _load_users()
    for u in users:
        if u["id"] == user_id:
            if add and prop_id not in u["wishlist"]:
                u["wishlist"].append(prop_id)
            elif not add and prop_id in u["wishlist"]:
                u["wishlist"].remove(prop_id)
    _save_users(users)


def get_wishlist(user_id: str):
    """Get wishlist property IDs for user."""
    user = get_user_by_id(user_id)
    return user.get("wishlist", []) if user else []


def update_user_profile(user_id: str, updates: dict):
    users = _load_users()
    for u in users:
        if u["id"] == user_id:
            for k, v in updates.items():
                u[k] = v
    _save_users(users)


def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def require_login():
    """Show login prompt if not logged in. Returns True if logged in."""
    if not is_logged_in():
        st.warning("🔐 Please login to access this feature.")
        if st.button("Go to Login", key="goto_login_btn"):
            st.session_state["show_login"] = True
        return False
    return True


def show_login_form():
    """Render a compact login/signup form. Returns user dict on success."""
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if not email or not password:
                    st.error("Please fill all fields.")
                else:
                    user = login(email.strip(), password.strip())
                    if user:
                        st.session_state["user"] = user
                        st.success(f"Welcome back, {user['name']}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

    with tab2:
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email", key="signup_email")
            phone = st.text_input("Phone", placeholder="10-digit mobile number")
            role = st.selectbox("I am a", ["owner", "agent", "buyer"])
            password = st.text_input("Password", type="password", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not all([name, email, phone, password, confirm_pass]):
                    st.error("Please fill all fields.")
                elif password != confirm_pass:
                    st.error("Passwords do not match.")
                elif len(phone) != 10 or not phone.isdigit():
                    st.error("Enter valid 10-digit phone number.")
                else:
                    ok, msg = register(name.strip(), email.strip(), phone.strip(), password, role)
                    if ok:
                        user = login(email.strip(), password)
                        st.session_state["user"] = user
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
