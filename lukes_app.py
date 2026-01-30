import json
import os
import random
import time
import datetime
import streamlit as st
import base64
import re
import gspread
from google.oauth2.service_account import Credentials # <--- NEW MODERN LIBRARY

# ==========================================
#       PART 0: CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="The Bank",
    page_icon="💋",
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 1. FORCE LIGHT BACKGROUND */
    .stApp { background-color: #E5E5E5 !important; color: #000000 !important; }
    
    /* 2. SIDEBAR STYLING */
    section[data-testid="stSidebar"] { background-color: #3B4432 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #FFFFFF !important; }

    /* 3. CHAT BUBBLES */
    .chat-container {
        background-color: #4A0404; 
        border-radius: 12px; padding: 15px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 2px solid #220000;
    }
    [data-testid="stChatMessage"] { background-color: #2D2D2D !important; border: 1px solid #444; padding: 10px; border-radius: 10px; }
    [data-testid="stChatMessage"] p { color: #FFFFFF !important; }

    /* 4. BUTTONS */
    div.stButton > button {
        width: 100%; height: 55px !important; min-height: 55px !important;
        border-radius: 8px; border: 1px solid #ccc; font-weight: 600; font-size: 16px;
        background-color: #FFFFFF; color: #333333; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 5px;
    }
    div.stButton > button:hover { border-color: #FF4B4B; color: #FF4B4B; }

    /* 5. BANNER SIZING */
    .banner-container { width: 100%; max-height: 180px; overflow: hidden; border-radius: 12px; border: 2px solid #333; position: relative; margin-bottom: 15px; }
    .banner-container img { width: 100%; height: 100%; object-fit: cover; }

    /* 6. MOBILE FIXES */
    [data-testid="stHeader"] { background: transparent !important; visibility: visible !important; }
    [data-testid="collapsedControl"] { color: #000000 !important; display: block !important; }
    .stAppDeployButton, [data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
#       PART 2: DATA ENGINE (GOOGLE SHEETS - FIXED)
# ==========================================
SHEET_NAME = "BankOfPaigeDB"

def get_sheet():
    # Use the Modern Google Auth (Fixes "Seekable Bit Stream" error)
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Create credentials from the Streamlit secrets
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=scope
    )
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def load_data():
    default_data = {
        "tickets": 0, "tank_balance": 0.0, "tank_goal": 10000.0, 
        "house_fund": 0.0, "wallet_balance": 0.0, "bridge_fund": 0.0,
        "inventory": [], "history_log": [], "ledger": [],
        "chat_log": [], "streak": 0, "last_login": ""
    }
    try:
        sheet = get_sheet()
        # We store the ENTIRE database in Cell A1 as a JSON string
        val = sheet.acell('A1').value
        if val:
            data = json.loads(val)
            # Merge defaults in case we added new features
            for k, v in default_data.items():
                if k not in data: data[k] = v
            return data
        else:
            return default_data
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return default_data

def save_data(data):
    try:
        sheet = get_sheet()
        json_str = json.dumps(data)
        # Use update_acell for safer writing
        sheet.update_acell('A1', json_str)
    except Exception as e:
        st.error(f"Save Failed: {e}")

if "data" not in st.session_state: st.session_state.data = load_data()
if "history" not in st.session_state: 
    st.session_state.history = [{"type": "chat", "role": "assistant", "content": "Systems Online. 💋"}]
if "turn_state" not in st.session_state: st.session_state.turn_state = "WALLET_CHECK"

# ==========================================
#       PART 3: HELPER FUNCTIONS
# ==========================================
def add_chat(role, content):
    if "history" not in st.session_state: st.session_state.history = []
    st.session_state.history.append({"type": "chat", "role": role, "content": content})

def type_out(text):
    if st.session_state.history and st.session_state.history[-1].get('content', '').strip() == text.strip(): return 
    with st.chat_message("assistant", avatar="paige.png"): st.write(text)
    add_chat("assistant", text)

def simulate_thinking(seconds=None):
    if seconds is None: seconds = random.uniform(1.0, 2.0)
    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Paige is thinking..."): time.sleep(seconds)

def show_media(path, delay=1.0):
    if st.session_state.history and st.session_state.history[-1].get("path") == path: return
    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Uploading..."): time.sleep(delay)
        if os.path.exists(path):
            if path.lower().endswith(('.mp4', '.mov', '.webm')): st.video(path)
            else: st.image(path, width=300)
    if os.path.exists(path):
        st.session_state.history.append({"type": "media", "role": "assistant", "path": path, "kind": "image"})

def log_event(text):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if "chat_log" not in st.session_state.data: st.session_state.data["chat_log"] = []
    st.session_state.data["chat_log"].append(f"[{ts}] ACTION: {text}")
    save_data(st.session_state.data)

def log_money(amount, note, category="income"):
    if "ledger" not in st.session_state.data: st.session_state.data["ledger"] = []
    entry = {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "amount": amount, "note": note, "category": category}
    st.session_state.data["ledger"].insert(0, entry)
    log_event(f"MONEY: {note} (${amount})")
    save_data(st.session_state.data)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: data = f.read()
    return base64.b64encode(data).decode()

def spend_waterfall(amount, category):
    if amount <= 0: return "Zero? Okay."
    remaining = amount
    if st.session_state.data['wallet_balance'] >= remaining:
        st.session_state.data['wallet_balance'] -= remaining
        log_money(amount, category, "expense")
        return f"💸 Paid ${amount:.2f} for {category} from Wallet."
    paid = st.session_state.data['wallet_balance']
    remaining -= paid
    st.session_state.data['wallet_balance'] = 0.0
    if st.session_state.data['tank_balance'] >= remaining:
        st.session_state.data['tank_balance'] -= remaining
        log_money(amount, category, "expense")
        return f"⚠️ Wallet empty. Took ${remaining:.2f} from Tank."
    st.session_state.data['tank_balance'] = 0.0
    st.session_state.data['house_fund'] -= remaining 
    log_money(amount, category, "expense")
    return f"🛑 TANK EMPTY. Took ${remaining:.2f} from HOUSE FUND."

def check_decision(key, title):
    data = st.session_state.get(key, {})
    if data.get("stage") == "DECISION":
        st.subheader(f"🎉 You Won: {title}")
        c1, c2 = st.columns(2)
        if c1.button("🔥 Use Now"):
            log_event(f"CLAIMED NOW: {title}")
            st.session_state[key]["stage"] = 0
            st.rerun()
        if c2.button("🎒 Save for Later"):
            log_event(f"SAVED: {title}")
            st.session_state.data["inventory"].append(title)
            save_data(st.session_state.data)
            st.session_state.turn_state = "PRIZE_DONE"
            del st.session_state[key]
            st.rerun()
        return True
    return False

def enter_state(state, role, text): type_out(text)

# --- SMART BANKER BRAIN (CHAT LOGIC) ---
def smart_banker(text):
    text = text.lower()
    amount = 0.0
    match = re.search(r'\$?(\d+(\.\d{2})?)', text)
    if match: amount = float(match.group(1))
    
    if amount == 0 and any(x in text for x in ["spent", "add", "transfer", "move"]):
        return "I need a number, pet. 'Spent 20', 'Added 50'."

    # 1. SPENDING
    if any(x in text for x in ["spent", "bought", "cost", "paid", "expense"]):
        if st.session_state.data['wallet_balance'] >= amount:
            st.session_state.data['wallet_balance'] -= amount
            log_money(amount, f"Quick Spend: {text}", "expense")
            return f"💸 **-${amount:.2f}** deducted. You better have bought something for me."
        else:
            remaining = amount - st.session_state.data['wallet_balance']
            st.session_state.data['wallet_balance'] = 0
            if st.session_state.data['tank_balance'] >= remaining:
                st.session_state.data['tank_balance'] -= remaining
                log_money(amount, f"Overdraft: {text}", "expense")
                return f"⚠️ Wallet empty. I took **${remaining:.2f}** from the Tank."
            else: return "❌ You're broke. Access denied."

    # 2. SIDE HUSTLE (TIERED)
    elif any(x in text for x in ["side", "tips", "found", "sold", "won", "add"]):
        st.session_state.data['wallet_balance'] += amount
        if amount >= 150: tix = 100
        elif amount >= 100: tix = 50
        elif amount >= 50: tix = 25
        else: tix = 15
        st.session_state.data["tickets"] += tix
        save_data(st.session_state.data)
        log_money(amount, "Quick Income", "income")
        return f"💰 **+${amount:.2f}** added. Good boy. (+{tix} Tickets)."

    # 3. PAYCHECK
    elif "paycheck" in text:
        bills = 350 + 50 + 100 
        safe = amount - bills
        if safe < 0: return "Check too small for bills. Work harder."
        st.session_state.data["wallet_balance"] += safe
        st.session_state.data["house_fund"] += 100
        st.session_state.data["bridge_fund"] += 50
        if amount >= 600: tix = 100
        elif amount >= 500: tix = 50
        else: tix = 25
        st.session_state.data["tickets"] += tix
        save_data(st.session_state.data)
        log_money(amount, "Paycheck (Chat)", "income")
        return f"💰 Paycheck processed. Bills paid. (+{tix} Tickets). Safe spend: **${safe:.2f}**."

    # 4. TANK
    elif "tank" in text:
        if "to" in text and "wallet" in text:
            if st.session_state.data["tank_balance"] >= amount:
                st.session_state.data["tank_balance"] -= amount
                st.session_state.data["wallet_balance"] += amount
                log_money(amount, "Tank -> Wallet", "transfer")
                return f"🛡️ Moved **${amount:.2f}** to Wallet."
            else: return "Not enough in Tank."
        elif "add" in text or "fill" in text:
            st.session_state.data["tank_balance"] += amount
            st.session_state.data["tickets"] += 10
            save_data(st.session_state.data)
            log_money(amount, "Added to Tank", "income")
            return f"🛡️ Locked **${amount:.2f}** into the Tank. (+10 Tickets)."

    return "I didn't catch that. Say 'Spent 20', 'Added 50', or 'Tank to Wallet 10'."

# ==========================================
#       PART 5: SIDEBAR
# ==========================================
with st.sidebar:
    st.image("my_banner2.JPG" if os.path.exists("my_banner2.JPG") else "my_banner2.jpg", use_container_width=True)
    
    if st.button("🔄 RELOAD DATA (SYNC)"):
        st.session_state.data = load_data()
        st.rerun()
        
    st.write("---")
    st.markdown("""<style>[data-testid="stSidebar"] [data-testid="stMetricValue"] {color: #FFFFFF !important;}</style>""", unsafe_allow_html=True)
    st.metric("💳 Wallet", f"${st.session_state.data['wallet_balance']:,.2f}")
    st.metric("🛡️ Tank", f"${st.session_state.data['tank_balance']:,.2f}")
    st.metric("🏠 House", f"${st.session_state.data['house_fund']:,.2f}")
    st.metric("🎟️ Tickets", st.session_state.data['tickets'])
    st.write("---")
    with st.expander("🔐 Admin Panel"):
        with st.form("admin_form"):
            code = st.text_input("Passcode", type="password")
            submit = st.form_submit_button("Unlock")
            if submit and code == "1234":
                st.session_state.admin_unlocked = True
                st.success("Unlocked!")
        if st.session_state.get("admin_unlocked"):
            if st.button("🕵️ VIEW SPY LOGS"):
                st.session_state.turn_state = "ADMIN_SPY_MODE"; st.rerun()
            if st.button("🔴 RESET ALL DATA"):
                st.session_state.data = {
                    "tickets": 0, "tank_balance": 0.0, "tank_goal": 10000.0, 
                    "house_fund": 0.0, "wallet_balance": 0.0, "bridge_fund": 0.0,
                    "inventory": [], "history_log": [], "ledger": [],
                    "chat_log": [], "streak": 0, "last_login": ""
                }
                save_data(st.session_state.data)
                st.success("Wiped.")
                time.sleep(1)
                st.rerun()

# ==========================================
#       PART 6: MAIN INTERFACE
# ==========================================
if st.session_state.turn_state == "WALLET_CHECK":
    if os.path.exists("top_banner_blank.jpg"):
        img_base64 = get_base64_of_bin_file("top_banner_blank.jpg")
        real_tickets = st.session_state.data["tickets"]
        banner_html = f"""<div class="banner-container"><img src="data:image/jpeg;base64,{img_base64}"><div style="position: absolute; top: 30%; right: 25%; transform: translate(50%, -50%); font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 24px; color: #FFFFFF; text-shadow: 2px 2px 4px #000000;">🎟️ {real_tickets}</div></div>"""
        st.markdown(banner_html, unsafe_allow_html=True)

if st.session_state.turn_state not in ["ADMIN_SPY_MODE", "SPIN_BRONZE", "SPIN_SILVER", "SPIN_GOLD"]:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    history_view = [h for h in st.session_state.history if h["type"] in ["chat", "media"]]
    for item in history_view[-3:]: 
        if item["type"] == "chat":
            name = "Paige" if item["role"] == "assistant" else "You"
            st.markdown(f"**{name}:** {item['content']}")
        elif item["type"] == "media":
             if os.path.exists(item["path"]): st.image(item["path"], width=300)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
#       PART 7: LOGIC & LAYOUT
# ==========================================
if st.session_state.turn_state == "WALLET_CHECK":
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏦 THE BANK"): st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()
    with c2:
        lbl = "🎰 CASINO OPEN" if st.session_state.data["tickets"] > 0 else "🎰 CASINO CLOSED"
        if st.button(lbl):
            if st.session_state.data["tickets"] > 0: st.session_state.turn_state = "CHOOSE_TIER"; st.rerun()
            else: type_out("You need tickets first.")
    st.markdown("###")
    q1, q2, q3 = st.columns(3)
    if q1.button("💋 Quicky"): st.session_state.turn_state = "THE_QUICKIE"; st.rerun()
    if q2.button("🛍️ Store"): st.session_state.turn_state = "THE_STORE"; st.rerun()
    if q3.button("📝 Ledger"): st.session_state.turn_state = "VIEW_LEDGER"; st.rerun()
    
    user_input = st.chat_input("Talk to Paige (e.g. 'Spent 20', 'Added 50')")
    if user_input:
        type_out(f"You: {user_input}")
        response = smart_banker(user_input)
        type_out(response)
        st.rerun()
    
    st.markdown("---")
    if st.button("💾 SAVE & END SESSION"):
        save_data(st.session_state.data)
        st.success("Session Saved. You may close the app.")

elif st.session_state.turn_state == "THE_BANK_MENU":
    st.subheader("🏦 Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Wallet", f"${st.session_state.data['wallet_balance']:.0f}")
    c2.metric("Tank", f"${st.session_state.data['tank_balance']:.0f}")
    c3.metric("House", f"${st.session_state.data['house_fund']:.0f}")
    st.write("---")
    
    user_input = st.chat_input("Talk to Paige (e.g. 'Spent 20', 'Added 50')")
    if user_input:
        type_out(f"You: {user_input}")
        response = smart_banker(user_input)
        type_out(response)
        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        st.caption("INCOME")
        if st.button("💵 Paycheck"): st.session_state.turn_state = "INPUT_PAYCHECK"; st.rerun()
        if st.button("💰 Side Hustle"): st.session_state.turn_state = "INPUT_SIDE_HUSTLE"; st.rerun()
        if st.button("🕒 Dayforce"): st.session_state.turn_state = "INPUT_DAILY"; st.rerun()
    with c2:
        st.caption("SPEND & SAVE")
        if st.button("🛡️ Manage Tank"): st.session_state.turn_state = "MANAGE_FUNDS"; st.rerun()
        if st.button("🛍️ The Store"): st.session_state.turn_state = "THE_STORE"; st.rerun()
        if st.button("🗺️ Money Map"): st.graphviz_chart("""digraph{rankdir=LR; Pay->Wallet; Day->Tank; Tank->Wallet; Tank->House}""")
    st.markdown("###")
    if st.button("⬅️ Home"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "ADMIN_SPY_MODE":
    st.subheader("🕵️ Spy Log")
    logs = st.session_state.data.get("chat_log", [])
    if logs:
        for log in reversed(logs): st.text(log); st.divider()
    else: st.info("No logs.")
    if st.button("Clear Logs"): st.session_state.data["chat_log"] = []; save_data(st.session_state.data); st.rerun()
    if st.button("Back"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "INPUT_PAYCHECK":
    st.subheader("💰 Process Paycheck")
    amount = st.number_input("Check Amount ($)", step=10.0)
    with st.expander("Adjust Deductions"):
        bills = st.number_input("Bills", value=350.0)
        blackout = st.number_input("Blackout", value=50.0)
        save = st.number_input("Savings", value=100.0)
    rem = amount - (bills + blackout + save)
    st.info(f"To Wallet: ${rem:.2f}")
    if st.button("Process"):
        st.session_state.data["bridge_fund"] += blackout
        st.session_state.data["house_fund"] += save
        st.session_state.data["wallet_balance"] += rem
        tix = 100 if amount >= 600 else 25
        st.session_state.data["tickets"] += tix
        log_money(amount, "Paycheck", "income")
        save_data(st.session_state.data)
        type_out(f"Processed. ${rem:.2f} added to wallet.")
        st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()
    if st.button("Back"): st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()

elif st.session_state.turn_state == "INPUT_DAILY":
    st.subheader("🕒 Dayforce")
    amt = st.number_input("Amount ($)", step=5.0)
    if st.button("Add"):
        st.session_state.data["tank_balance"] += amt
        st.session_state.data["tickets"] += 10
        log_money(amt, "Dayforce", "income")
        save_data(st.session_state.data)
        type_out("Added to Tank."); st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()
    if st.button("Back"): st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()

elif st.session_state.turn_state == "INPUT_SIDE_HUSTLE":
    st.subheader("💰 Side Hustle")
    amt = st.number_input("Amount ($)", step=5.0)
    if st.button("Add"):
        st.session_state.data["wallet_balance"] += amt
        if amt >= 150: tix = 100
        elif amt >= 100: tix = 50
        elif amt >= 50: tix = 25
        else: tix = 15
        st.session_state.data["tickets"] += tix
        log_money(amt, "Side Hustle", "income")
        save_data(st.session_state.data)
        type_out("Added to Wallet."); st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()
    if st.button("Back"): st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()

elif st.session_state.turn_state == "MANAGE_FUNDS":
    st.subheader("🛡️ Manage Tank")
    st.info(f"In Tank: ${st.session_state.data['tank_balance']:.2f}")
    move = st.number_input("Amount ($)", step=10.0)
    c1, c2 = st.columns(2)
    if c1.button("To Wallet"):
        if move <= st.session_state.data['tank_balance']:
            st.session_state.data['tank_balance'] -= move
            st.session_state.data['wallet_balance'] += move
            save_data(st.session_state.data)
            type_out("Moved to Wallet."); st.rerun()
    if c2.button("To Savings"):
        if move <= st.session_state.data['tank_balance']:
            st.session_state.data['tank_balance'] -= move
            st.session_state.data['house_fund'] += move
            save_data(st.session_state.data)
            type_out("Moved to Savings."); st.rerun()
    if st.button("Back"): st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()

elif st.session_state.turn_state == "THE_STORE":
    st.subheader("🛍️ Store")
    st.caption(f"Wallet: ${st.session_state.data['wallet_balance']:.2f}")
    cost = st.number_input("Cost ($)", step=1.0)
    c1, c2, c3 = st.columns(3)
    if c1.button("Food"): type_out(spend_waterfall(cost, "Food")); st.rerun()
    if c2.button("Gas"): type_out(spend_waterfall(cost, "Gas")); st.rerun()
    if c3.button("Bill"): type_out(spend_waterfall(cost, "Bill")); st.rerun()
    if st.button("Back"): st.session_state.turn_state = "THE_BANK_MENU"; st.rerun()

elif st.session_state.turn_state == "THE_QUICKIE":
    st.subheader("💋 Quicky")
    if st.button("Claim"):
        st.session_state.data["tickets"] += 5
        save_data(st.session_state.data)
        st.balloons(); type_out("Claimed 5 Tickets.")
    if st.button("Back"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "VIEW_LEDGER":
    st.subheader("📜 Ledger")
    for i in st.session_state.data["ledger"][:8]: st.text(f"{i['date']} | ${i['amount']} | {i['note']}")
    if st.button("Back"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

# ==========================================
#       CASINO LOGIC (WITH SIDE IMAGE)
# ==========================================
elif st.session_state.turn_state == "CHOOSE_TIER":
    st.subheader("🎰 Casino")
    st.metric("Tickets", st.session_state.data["tickets"])
    c1, c2, c3 = st.columns(3)
    if c1.button("Bronze (25)"):
        if st.session_state.data["tickets"] >= 25: 
            st.session_state.data["tickets"] -= 25
            save_data(st.session_state.data)
            st.session_state.turn_state = "SPIN_BRONZE"
            st.rerun()
    if c2.button("Silver (50)"):
        if st.session_state.data["tickets"] >= 50: 
            st.session_state.data["tickets"] -= 50
            save_data(st.session_state.data)
            st.session_state.turn_state = "SPIN_SILVER"
            st.rerun()
    if c3.button("Gold (100)"):
        if st.session_state.data["tickets"] >= 100: 
            st.session_state.data["tickets"] -= 100
            save_data(st.session_state.data)
            st.session_state.turn_state = "SPIN_GOLD"
            st.rerun()
    if st.button("Exit"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "SPIN_BRONZE":
    # Layout: Wheel (Left) - Image (Right)
    col_main, col_img = st.columns([2.5, 1.5]) 
    
    with col_main:
        components.iframe("https://spinthewheel.app/tmDneZ0rCW", height=500)
        c1, c2 = st.columns(2)
        if c1.button("Bend Over"): log_event("Won: Bend Over"); st.session_state.turn_state="PRIZE_BEND_OVER"; st.rerun()
        if c2.button("Flash Me"): log_event("Won: Flash Me"); st.session_state.turn_state="PRIZE_FLASH_ME"; st.rerun()
        c3, c4 = st.columns(2)
        if c3.button("Jackoff Pass"): log_event("Won: Jackoff Pass"); st.session_state.turn_state="PRIZE_JACKOFF_PASS"; st.rerun()
        if c4.button("Shower Show"): log_event("Won: Shower Show"); st.session_state.turn_state="PRIZE_SHOWER_SHOW"; st.rerun()
        
    with col_img:
        # Side Image
        if os.path.exists("wheelspin.JPG"):
            st.image("wheelspin.JPG", use_container_width=True)
        else:
            st.warning("Upload wheelspin.JPG")

elif st.session_state.turn_state == "SPIN_SILVER":
    col_main, col_img = st.columns([2.5, 1.5])
    
    with col_main:
        components.iframe("https://spinthewheel.app/1RLMB3g88K", height=500)
        c1, c2, c3 = st.columns(3)
        if c1.button("Toy Pic"): log_event("Won: Toy Pic"); st.session_state.turn_state="PRIZE_TOY_PIC"; st.rerun()
        if c2.button("Lick Pussy"): log_event("Won: Lick Pussy"); st.session_state.turn_state="PRIZE_LICK_PUSSY"; st.rerun()
        if c3.button("Nude Pic"): log_event("Won: Nude Pic"); st.session_state.turn_state="PRIZE_NUDE_PIC"; st.rerun()
        c4, c5, c6 = st.columns(3)
        if c4.button("Tongue Tease"): log_event("Won: Tongue Tease"); st.session_state.turn_state="PRIZE_TONGUE_TEASE"; st.rerun()
        if c5.button("Road Head"): log_event("Won: Road Head"); st.session_state.turn_state="PRIZE_ROAD_HEAD"; st.rerun()
        if c6.button("Plug Tease"): log_event("Won: Plug Tease"); st.session_state.turn_state="PRIZE_PLUG_TEASE"; st.rerun()

    with col_img:
        if os.path.exists("wheelspin.JPG"):
            st.image("wheelspin.JPG", use_container_width=True)

elif st.session_state.turn_state == "SPIN_GOLD":
    col_main, col_img = st.columns([2.5, 1.5])
    
    with col_main:
        components.iframe("https://spinthewheel.app/JIRFjfR66x", height=500)
        c1, c2, c3 = st.columns(3)
        if c1.button("All 3 Holes"): log_event("Won: All 3 Holes"); st.session_state.turn_state="PRIZE_ALL_3_HOLES"; st.rerun()
        if c2.button("Upside Down"): log_event("Won: Upside Down"); st.session_state.turn_state="PRIZE_UPSIDE_DOWN_THROAT_FUCK"; st.rerun()
        if c3.button("Flashback"): log_event("Won: Flashback"); st.session_state.turn_state="PRIZE_FLASHBACK"; st.rerun()
        c4, c5 = st.columns(2)
        if c4.button("Anal Fuck"): log_event("Won: Anal Fuck"); st.session_state.turn_state="PRIZE_ANAL_FUCK"; st.rerun()
        if c5.button("Doggy Style"): log_event("Won: Doggy Style"); st.session_state.turn_state="PRIZE_DOGGY_STYLE_READY"; st.rerun()

    with col_img:
        if os.path.exists("wheelspin.JPG"):
            st.image("wheelspin.JPG", use_container_width=True)
            
# ==========================================
#       PRIZE SCRIPTS 
# ======================================
# --- NUDE PIC PRIZE ---
elif st.session_state.turn_state == "PRIZE_NUDE_PIC":
    # 1. Init Data (Start at DECISION phase)
    if "nude_pic" not in st.session_state:
        st.session_state.nude_pic = {"stage": "DECISION", "focus": None}
    
    # 2. DECISION CHECK
    if check_decision("nude_pic", "Custom Nude Pic"):
        pass

    # 3. GAME LOGIC
    else:
        data = st.session_state.nude_pic
        
        # ── STAGE 0: Intro ──
        if data["stage"] == 0:
            type_out("You've won, your very own photo of me... which ever part you want to see...😈")
            
            simulate_thinking(2.0)
            show_media("nude_1.jpg")
            
            type_out("I'm gonna tease you so fucking slow and nasty with every inch of my body…")
            simulate_thinking(2.0)
            type_out("until you're throbbing and begging to fuck me dead.")
            type_out("Ready to collect your reward, daddy? Which piece of your slutty prize do you want to torture yourself with?")

            # Buttons
            c1, c2, c3 = st.columns(3)
            if c1.button("Tits"):
                data["focus"] = "TITS"
                data["stage"] = 1
                st.rerun()
            if c2.button("Ass"):
                data["focus"] = "TIGHT ASS"
                data["stage"] = 1
                st.rerun()
            if c3.button("Pussy"):
                data["focus"] = "WET PUSSY"
                data["stage"] = 1
                st.rerun()

        # ── STAGE 1: The Tease ──
        elif data["stage"] == 1:
            if data["focus"] == "TITS":
                type_out("Tits? Are you sure, daddy?")
                simulate_thinking(2.0)
                show_media("nude_6.jpg")
                if st.button("enough teasing, show me your tits"):
                    data["stage"] = 2
                    st.rerun()

            elif data["focus"] == "TIGHT ASS":
                type_out("Ass? Are you sure, daddy?")
                simulate_thinking(2.0)
                show_media("nude_4.jpg")
                if st.button("Let me see it"):
                    data["stage"] = 2
                    st.rerun()

            elif data["focus"] == "WET PUSSY":
                type_out("This little Pussy....Are you sure, daddy?")
                simulate_thinking(2.0)
                show_media("nude_2.jpg") 
                if st.button("Pull them down already"):
                    data["stage"] = 2
                    st.rerun()

        # ── STAGE 2: The Reveal ──
        elif data["stage"] == 2:
            simulate_thinking(2.0)

            if data["focus"] == "TITS":
                show_media("Nude_7.jpg")
                type_out("They would look so much better around your hard cock, huh?")
            
            elif data["focus"] == "TIGHT ASS":
                show_media("nude_5.jpg")
                type_out("All bare, spread, tight little holes all wet and ready....maybe next spin, they'll get fucked. 🍑")

            elif data["focus"] == "WET PUSSY":
                show_media("nude_3.jpg")
                type_out("wet and dripping...now")

            if st.button("That's enough for now… claim this prize now?"):
                del st.session_state.nude_pic
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()
                
# --- LICK MY PUSSY PRIZE ---
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    if "lick_pussy" not in st.session_state:
        st.session_state.lick_pussy = {
            "stage": "DECISION", 
            "position": None, 
            "tease_level": 0
        }

    if check_decision("lick_pussy", "Lick My Pussy"):
        pass
    else:
        data = st.session_state.lick_pussy

        # -------- STAGE 0: Intro & Choice --------
        if data["stage"] == 0:
            type_out("hey daddy… 💕")
            simulate_thinking(1.5)
            type_out("guess what you just won…")
            type_out("your tongue…")
            simulate_thinking(2.0)
            type_out("on this needy little pussy… all night if you want 😈")
            show_media("lick_it.jpeg")

            simulate_thinking(2.2)
            type_out("look how puffy and wet she already is… just from thinking about your mouth")
            type_out("I’ve been edging myself waiting for you… but I stopped right before")
            type_out("now I’m throbbing so bad… aching for your tongue to finish me 💦")
            type_out("so… how do you wanna taste it first, baby? tell me exactly how…")

            positions = [
                "From behind… face buried deep between my cheeks while I push back on your tongue 🍑",
                "Me on my back… thighs squeezing your head, fingers tangled in your hair pulling you deeper 🛏️",
                "I lower myself onto your face… grinding slow, using your mouth like my personal toy 😏",
                "Standing over you… one leg up, dripping straight down onto your waiting tongue 👅"
            ]
            data["position"] = st.radio(
                "How should I give you this pussy, daddy?",
                positions,
                key="lick_position_choice"
            )

            if st.button("I’m dripping just waiting for your choice… 👅", key="lick_start"):
                data["stage"] = 1
                data["tease_level"] = 0
                st.rerun()

        # -------- STAGE 1: The Act --------
        elif data["stage"] == 1:
            pos_text = data['position'].split('…')[0].strip()
            type_out(f"oh fuck… **{pos_text}**? 🥵")
            type_out("you picked the one that’s gonna make me lose it…")

            if "behind" in data["position"].lower():
                show_media("from_behind.jpeg")
                type_out("ass up high… cheeks spread… pussy glistening right in your face")
                type_out("I can feel your hot breath teasing my clit already…")
                type_out("start sooo slow baby… trace the outside of my lips… barely touching… make me squirm")
                type_out("mmmmm… yes… now the tip of your tongue… flick my hole lightly…")

            elif "back" in data["position"].lower() or "lay" in data["position"].lower():
                show_media("front_eat.jpeg")
                type_out("legs spread wide… knees by my ears… pussy swollen and begging")
                type_out("I grab your hair… pull your face right in until your nose is pressed against me")
                type_out("long flat licks… bottom to top… dragging over my clit every time…")
                type_out("fuck… my hips are bucking already… don’t you dare stop…")

            elif "face" in data["position"].lower() or "lower" in data["position"].lower():
                show_media("face_sit.jpeg")
                type_out("lowering myself down slow… feeling your nose brush my clit")
                type_out("I rock my hips… smearing my slick all over your lips… your chin…")
                type_out("you love being smothered in this wet pussy don’t you? my good little seat 😈")
                type_out("tongue out flat… let me ride it deep… use you like my favorite toy")

            elif "stand" in data["position"].lower():
                show_media("standing_pussy.jpeg")
                type_out("standing over you… one foot up… lips parted so you see every pink inch")
                type_out("watch a thick drop slide down my thigh… falls right onto your tongue")
                type_out("catch it baby… then lick upward slow… chase it back to my dripping hole")

            # --- CLIMAX SEQUENCE ---
            simulate_thinking(2.0)
            type_out("god I’m trembling…")
            type_out("circle my clit with just the tip… tiny little flicks… so light it drives me crazy")
            type_out("now suck it gently… then flick fast… then slow again… edge me until I’m begging")
            
            if st.button("I’m right fucking there… make me squirt all over you daddy 💦", key="lick_climax"):
                show_media("Cumming1.jpeg")
                type_out("ohhh fuck—yesyesyes—I’m cumming—I’m squirting everywhereeee 💦💦💦")
                type_out("my thighs shaking… pussy pulsing hard on your tongue… you’re drinking every gush")
                type_out("look at your face… soaked… dripping… you made such a filthy mess of me 😩")
                type_out("prize complete baby… but now I need your cock so bad…")

                if st.button("Come fuck your messy girl now? 🍆", key="lick_finish"):
                    st.session_state.pop("lick_pussy", None)
                    st.session_state.turn_state = "PRIZE_DONE"
                    st.rerun()

            # Global exit
            if st.button("🎰 The Exit - Save the rest for later?", key="lick_exit_global"):
                st.session_state.pop("lick_pussy", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

# --- ANAL FUCK PRIZE ---
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    # 1. Init Data
    if "anal_fuck" not in st.session_state:
        st.session_state.anal_fuck = {
            "stage": "DECISION", 
            "position": None, 
            "substage": 0
        }

    # 2. Check Decision
    if check_decision("anal_fuck", "Anal Fuck"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.anal_fuck

        # ── STAGE 0: Confession & Tease Buildup ──
        if data["stage"] == 0:
            type_out("Daddy… you fucking won **Anal Fuck** 😩🍑 My greedy little asshole is already soaked thinking about it.")
            simulate_thinking(2.0)
            
            type_out("So… I have a filthy confession…")
            show_media("anal_opening1.JPG")
            
            type_out("I’ve been such a dirty slut all morning… playing with my tight little ass, shoving fingers in deep, getting it sloppy and ready for your thick cock.")
            
            type_out("Fingering it slow at first… then faster… curling them just right so I’m whimpering your name into the pillow…")
            show_media("anal_opening2.JPG")
            
            type_out("Stretching my greedy hole wide enough to take every brutal inch of you without mercy… god, it’s already pulsing just thinking about you wrecking it.")
            
            type_out("Ass arched high like a bitch in heat… cheeks spread wide… that tiny pink pucker twitching and winking, literally begging for you to ruin it, daddy.")
            show_media("anal_opening3.JPG")

            type_out("So when I saw you won 'Anal Fuck' my cunt dripped instantly. This desperate little asshole has been trained all morning just for you.")
            type_out("How do you want to start destroying this needy, pre-stretched fuckhole, daddy? Pick your position and fucking ruin me…")
            
            show_media("anal_opening4.JPG")

            c1, c2 = st.columns(2)
            if c1.button("Missionary – legs hooked over your shoulders…"):
                data["position"] = "missionary"
                data["stage"] = 1
                data["substage"] = 0
                st.rerun()

            if c2.button("Doggy – ass up high, full view"):
                data["position"] = "doggy"
                data["stage"] = 1
                data["substage"] = 0
                st.rerun()

        # ── STAGE 1: The Action (Branching Paths) ──
        elif data["stage"] == 1:
            
            # --- MISSIONARY PATH ---
            if data["position"] == "missionary":
                
                if data["substage"] == 0:
                    type_out("Like this, Daddy? Legs pinned back… ass presented… hole already winking at your fat cock…")
                    show_media("anal_opening6.jpeg")
                    if st.button("Fuck ya show me more – stretch me wide"):
                        data["substage"] = 1
                        st.rerun()
                
                elif data["substage"] == 1:
                    type_out("Ohhh fuck yes… that thick head popping past my rim… filling my slutty ass so deep… pound it, Daddy, make me your anal bitch.")
                    show_media("anal_opening7.jpeg")
                    if st.button("Fuck it, I'm gonna cum – ruin my hole"):
                        data["substage"] = 2
                        st.rerun()
                
                elif data["substage"] == 2:
                    type_out("Oh god—yes—Daddy—thank you for wrecking my tight little ass… I’m cumming so hard around your cock… fill me, please…")
                    show_media("anal_opening8.jpeg")
                    
                    simulate_thinking(2.0)
                    type_out("Look at that filthy mess… your hot cum oozing out of my gaped, ruined hole while my legs are still shaking… fuck, Daddy, you bred my ass so good…")
                    # Note: Using the doggy last image here as requested in original script
                    show_media("anal_oppening_doggystyle_last.JPG")

                    if st.button("Prize complete – back to casino"):
                        st.session_state.pop("anal_fuck", None)
                        st.session_state.turn_state = "PRIZE_DONE"
                        st.rerun()

            # --- DOGGY PATH ---
            elif data["position"] == "doggy":
                
                if data["substage"] == 0:
                    type_out("Like this, Daddy? Ass up, face down… hole already stretched and dripping… ready to be used like your personal fucktoy.")
                    show_media("anal_opening_doggystyle1.JPG")
                    if st.button("Show me more – spread me wider"):
                        data["substage"] = 1
                        st.rerun()

                elif data["substage"] == 1:
                    type_out("Mmm you perv… look at this greedy asshole, already gaping a little… begging for your cock to split it open again.")
                    show_media("anal_opening_doggystyle3.JPG")
                    if st.button("Touch it – finger my ruined hole first"):
                        data["substage"] = 2
                        st.rerun()

                elif data["substage"] == 2:
                    show_media("anal_opening_doggystyle2.JPG")
                    if st.button("Fuck it – destroy me"):
                        data["substage"] = 3
                        st.rerun()

                elif data["substage"] == 3:
                    show_media("anal_opening_doggystyle4.JPG")
                    type_out("That’s it, Daddy—slam that fat cock balls-deep—fuck my stretched asshole like the dirty cum-dump I am.")
                    show_media("anal_opening_doggystyle5.JPEG")
                    if st.button("FUCK IT I’m cumming – breed my ass"):
                        data["substage"] = 4
                        st.rerun()

                elif data["substage"] == 4:
                    simulate_thinking(2.0)
                    show_media("anal_oppening_doggystyle_last.JPG")
                    type_out("Oh fuck yes… pulling out slow… watching your thick ropes drip down my cheeks and leak out of my gaping, ruined hole… you fucking owned this ass, Daddy…")
                    show_media("anal_opening_doggystyle10.JPG")
                    
                    if st.button("Prize complete – back to casino"):
                        st.session_state.pop("anal_fuck", None)
                        st.session_state.turn_state = "PRIZE_DONE"
                        st.rerun()

        # Global Exit
        if st.button("🎰 The Exit - Save the rest for later?"):
            st.session_state.pop("anal_fuck", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
# --- BEND OVER PRIZE ---
elif st.session_state.turn_state == "PRIZE_BEND_OVER":
    # 1. Init Data
    if "bend_over" not in st.session_state:
        st.session_state.bend_over = {"stage": "DECISION"}
    
    # 2. Check Decision
    if check_decision("bend_over", "Bend Over"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.bend_over

        # ── Stage 0: Intro ──
        if data.get("stage") == 0:
            type_out("You've won Bend Over!")
            simulate_thinking(2.0)
            type_out("Let me just walk you through how this actually goes down so you know exactly what you've won 😈")
            
            if st.button("Ok what are the rules?"):
                data["stage"] = 1
                st.rerun()

        # ── Stage 1: The Rules ──
        elif data["stage"] == 1:
            type_out("Ok you dirty perv. Rules are simple and filthy:")
            type_out("Whenever you say \"Bend over\" out loud or text it.")
            simulate_thinking(2.5)
            type_out("The second those words hit—I stop whatever the fuck I'm doing. Drop it. Bend over right there for a full 60 seconds.")
            type_out("Hands planted, ass popped high, back arched deep, legs spread a little so you get the view.")
            type_out("In that minute you get to do anything except fuck me.")
            
            if st.button("Like what?"):
                data["stage"] = 2
                st.rerun()

        # ── Stage 2: Allowed Actions ──
        elif data["stage"] == 2:
            type_out("Grab, spank, spread, tease my pussy with your fingers or cockhead (rubbing only—no sliding in), pinch whatever you can reach, grind against me, whisper how much of a desperate slut I am… whatever makes you hard.")
            simulate_thinking(3.0)
            type_out("But no penetration. No dick inside. Not even a little.")
            type_out("Timer dings at 60? Everything stops. I stand up. Pussy throbbing, maybe dripping.")
            
            if st.button("Can I have an example?"):
                data["stage"] = 3
                st.rerun()

        # ── Stage 3: The Scenario ──
        elif data["stage"] == 3:
            type_out("Imagine I’m in the bedroom doing laundry, sorting clothes on the bed like a good girl.")
            type_out("Wearing your black hoodie (barely covers my ass), those tight black booty shorts wedged up between my cheeks, no panties underneath.")
            
            if st.button("I need visuals"):
                data["stage"] = 4
                st.rerun()

        # ── Stage 4: Visuals Part 1 ──
        elif data["stage"] == 4:
            type_out("You would. Here you go..")
            simulate_thinking(2.0)
            show_media("laundry1.jpg")
            
            type_out("As I was saying.. Imagine I’m in the bedroom doing laundry, sorting clothes on the bed like a good girl")
            type_out("You walk in from work, see me like that, drop your bag… and just say it.")
            
            if st.button("Bend over."):
                data["stage"] = 5
                st.rerun()

        # ── Stage 5: The Command & Reaction ──
        elif data["stage"] == 5:
            type_out("Thasts right.")
            simulate_thinking(1.5)
            type_out("I freeze. Stop folding mid-shirt. Turn slow. Plant both hands on the bed. Arch my back hard. Pop my hips out. Ass up high… exactly like this.")
            
            simulate_thinking(2.5)
            show_media("laundry3.jpg")
            
            type_out("See? Instant. Obedient.")
            type_out("60 seconds starts ticking the moment you say it.")
            type_out("I stay frozen like that—ass presented, shorts hugging every inch, pussy already getting wet just from knowing you're staring.")
            type_out("You step up behind me… and the clock is running. What are you doing to me in those 60 seconds, baby?")
            
            if st.button("What can I do?"):
                data["stage"] = 6
                st.rerun()

        # ── Stage 6: The Finale ──
        elif data["stage"] == 6:
            type_out("Spreading my cheeks wide and blowing cool air on my slit?")
            type_out("Rubbing your cock slow between my thighs so I feel how hard you are without getting any?")
            type_out("Giving me slow, stinging spanks till my ass jiggles and turns pink?")
            type_out("Teasing my clit through the fabric with one finger till the shorts are soaked?")
            type_out("Or just gripping my hips and grinding against me while telling me how pathetic I look begging without you even fucking me?")
            
            simulate_thinking(3.0)
            type_out("The real question is...what will you do?")
            show_media("laundry4.jpg")
            
            # Finish Buttons
            if st.button("Prize Complete – I know what I'm doing next time"):
                st.session_state.pop("bend_over", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # Global Exit Button (Always available)
        if st.button("🎰 The Exit - Save this prize for later"):
            st.session_state.pop("bend_over", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- PRIZE: FLASH ME ---
elif st.session_state.turn_state == "PRIZE_FLASH_ME":
    if "flash_me" not in st.session_state:
        st.session_state.flash_me = {"stage": "DECISION"}

    if check_decision("flash_me", "Flash Me"):
        pass
    else:
        enter_state("PRIZE_FLASH_ME", "assistant", "Fuck yes baby… you just won “Flash Me” 😈 Congrats, winner!")
        if st.button("I’m pretty sure I know what this means…"):
            add_chat("user", "I’m pretty sure I know what this means…")
            st.session_state.turn_state = "PRIZE_FLASH_TWIST"
            st.rerun()

# --- FLASH TWIST ---
elif st.session_state.turn_state == "PRIZE_FLASH_TWIST":
    enter_state("PRIZE_FLASH_TWIST", "assistant", "Mmm… maybe not exactly what you're thinking, dirty boy. There's a naughty little twist tonight.")
    if st.button("Oh, yeah?"):
        add_chat("user", "Oh, yeah?")
        type_out("Just say the word… or give me that hungry nod… and I'll yank my top up fast and flash you these perky tits right in your face.")
        type_out("OR… should I climb onto your lap while you're gaming, hike up this little skirt, spread my thighs just enough, and give you a quick, dripping peek of my bare, soaked pussy?")
        type_out("Your prize, daddy… which filthy flash do you want first? Tell your slut what you crave 🥵 Want a preview?")
        st.session_state.turn_state = "PRIZE_FLASH_CHOICE"
        st.rerun()

# --- FLASH CHOICE ---
elif st.session_state.turn_state == "PRIZE_FLASH_CHOICE":
    enter_state("PRIZE_FLASH_CHOICE", "assistant", "Come on baby… pick your poison. Which part of me are you throbbing to see flashed right now?")
    c1, c2 = st.columns(2)
    
    if c1.button("Show me your tits"):
        add_chat("user", "Show me your tits.")
        show_media("Nude_7.jpg", 3.0)
        type_out("There they are daddy… quick little flash of these soft, bouncy tits just for you. Nipples already hard thinking about your mouth on them 😏")
        type_out("Let me know when you're ready for the real thing… I’ll let you suck them all night if you win again.")
        st.session_state.pop("flash_me", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
    
    if c2.button("Show me your pussy"):
        add_chat("user", "Show me your pussy.")
        show_media("flash_pussy1.jpg", 3.0)
        type_out("Mmm fuck… here’s your sneak peek, winner. My pussy’s already glistening and swollen, dripping just from teasing you like this 🍑💦")
        type_out("No touching yet… but imagine sliding inside when you finally get the full prize. Let me know when you want to see — and taste — what's waiting underneath.")
        st.session_state.pop("flash_me", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_DONE":
    enter_state("PRIZE_DONE", "assistant", "Prize complete 😈 Ready to spin again, or are you still recovering from that one?")
    
# --- JACKOFF PASS ---
elif st.session_state.turn_state == "PRIZE_JACKOFF_PASS":
    if "jackoff_pass" not in st.session_state:
        st.session_state.jackoff_pass = {"stage": "DECISION"}

    if check_decision("jackoff_pass", "Jackoff Pass"):
        pass
    else:
        type_out("Mmm fuck yes baby… you just won the **Jackoff Pass** 😈 Your special prize: I give you full permission to stroke that thick cock while I tease the absolute shit out of you.")
        simulate_thinking(2.0)
        type_out("No guilt, no holding back — I want you pumping hard, edging, leaking precum, imagining every filthy thing you’d do to me while I describe it in detail.")
        add_narrator("Your slutty girlfriend Paige is gonna make this so fucking hard for you… literally.")
        simulate_thinking(2.0)
        show_media("jackoff3.jpeg") 
        type_out("Rule #1: You can’t cum until I say so. Edge for me like a good boy.")
        type_out("Rule #2: Tell me exactly what you’re doing to that dick while you’re doing it… I want every dirty detail.")
    
        if st.button("Fuck… ready to play with yourself for me?"):
            st.session_state.turn_state = "PRIZE_JACKOFF_FUN"
            st.rerun()

# --- JACKOFF FUN ---
elif st.session_state.turn_state == "PRIZE_JACKOFF_FUN":
    type_out("God I’m already so wet just thinking about you stroking to me… let’s make this nasty. Pick how you want your jackoff session to go, daddy.")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("Just talk dirty to me while I stroke"):
            add_chat("user", "Just talk dirty to me while I stroke")
            simulate_thinking(2)
            type_out("Mmm perfect… keep that hand moving slow and tight around your cock while I whisper how bad I want it inside me. Imagine my tight wet pussy gripping you, milking every drop… Edge it baby — get right to the brink then stop. Tell me how close you are… fuck I love when you’re throbbing and desperate for your Paige 🥵")
            st.session_state.pop("jackoff_pass", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
    with c2:
        if st.button("Tease me with a recap of all my prizes while I cum"):
            add_chat("user", "Tease me with a recap of all my prizes while I cum")
            simulate_thinking(2)
            type_out("Oh you greedy boy… want me to remind you of every filthy prize you’ve won so far while you pump that dick?")
            type_out("Remember when I bent over and showed you my dripping pussy… or when I flashed these tits and that soaked cunt under my skirt… all that was just for you, winner.")
            type_out("Here’s a little visual reminder of what you own… all these prizes waiting for your cock.")
            simulate_thinking(2.0)
            show_media("Jackkoff1.jpeg") 
            simulate_thinking(2)
            type_out("Cum for me now baby… shoot that load thinking about fucking your dirty little prize in person next time. I’m touching myself watching you lose it 😈")
            add_narrator("Good boy… you earned every drop.")
            st.session_state.pop("jackoff_pass", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("Steam is rising… your naughty little prize is about to get wet and slippery for you 😈")
    type_out("Mmm daddy… you won the Shower Show. Time to watch your girlfriend soap up every inch of this body — slowly, teasingly, while I think about your cock the whole time. One rule: no touching.")
    simulate_thinking(2.0)
    show_media("shower_water.jpg")  
    tease_level = st.radio(
        "How nasty do you want this shower to get, baby?",
        ["Slow and sensual tease – make you throb watching me lather up",
         "Full filthy show – watch me put my fingers...."],
        key="shower_tease_level"
    )
    if st.button("Start the show… I'm already dripping"):
        st.session_state.shower_choice = tease_level
        st.session_state.turn_state = "PRIZE_SHOWER_ACTION"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_SHOWER_ACTION":
    simulate_thinking(2.0)
    show_media("shower_finger.jpeg")  
    if st.session_state.shower_choice == "Slow and sensual tease – make you throb watching me lather up":
        type_out("Mmm… nice and slow just like you like. Watch my hands glide over these wet tits, circling my hard nipples… down my stomach to my slippery pussy. I'm so fucking turned on knowing you're staring — my clit is throbbing under the suds, baby. Imagine your tongue there instead…")
    else:
        type_out("Fuck yes… full filthy mode for my winner. Hands all over – squeezing these soapy tits, pinching my nipples hard while I moan your name. Now spreading my legs under the water, fingers sliding between my wet lips, rubbing my swollen clit fast… God I'm dripping more than the shower. Wish this was your cock pounding me against the wall right now 🥵")
    type_out("Show's almost over… but I’ve got one last treat when I step out. What do you want as your post-shower reward, daddy?")
    
    after_choice = st.radio("Pick your final prize piece:", ["take the towel and dry me off completely", "lick all the water off my pussy"])
    if st.button("End the shower"):
        simulate_thinking(2.0)
        show_media("shower_towel3.jpeg")  
        if "take the towel" in after_choice:
            type_out("Mmm… pat me down slow – towel sliding over my wet tits, between my thighs, teasing those sensitive spots. Still dripping… still thinking about you fucking me dry. Save that hard cock for next time, baby.")
            simulate_thinking(2.0)
            show_media("shower_towel1.jpeg")
        elif "lick all" in after_choice:
            type_out("There it goes… towel on the floor. Full naked, skin still glistening, nipples hard from the cool air. Turn around – ass still wet, pussy, needs drying. get to licking 😏")
            simulate_thinking(2.0)
            show_media("naked_shower.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- ALL 3 HOLES (CLAIM ALL THREE – SMOOTH FLOW) ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    # 1. Init Data
    if "all_3_holes" not in st.session_state:
        st.session_state.all_3_holes = {
            "current_hole": None,           # which hole he's claiming right now
            "claimed": {"pussy": False, "ass": False, "mouth": False},
            "step": "intro",                # intro → choose_tool → action → next
            "tool": None                    # "dick" or "toy"
        }

    # 2. Check Decision
    if check_decision("all_3_holes", "All 3 Holes"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.all_3_holes

        # ── Intro Story (only shown once) ──
        if data["step"] == "intro":
            type_out("Baby… you actually fucking did it.")
            simulate_thinking(2.0)
            type_out("Three years in your mom’s house… every penny youve tried to save to get us out of here. Every late night, every side job, every time you said no to going out… it was all for us. For our own place. Well get there soon enough baby.")
            
            show_media("3_holes_opening.jfif")
            
            type_out("I’m at home right now while you’re at work… legs spread, fingers teasing myself, getting ready to give you the ultimate thank-you.")
            type_out("Tonight, when you walk through **our** door… you get **all three** of my tight, needy holes. One after another… until I’m shaking and dripping for you.")
            type_out("Ready to start claiming them, love? Let’s go slow… which one do you want first?")

            c1, c2, c3 = st.columns(3)
            
            if c1.button("Pussy first… I want to feel how wet our future made me"):
                data["current_hole"] = "pussy"
                data["step"] = "choose_tool"
                st.rerun()
            
            if c2.button("Ass first… I’ve been stretching it all day for our new bedroom"):
                data["current_hole"] = "ass"
                data["step"] = "choose_tool"
                st.rerun()
            
            if c3.button("Mouth first… so I can drop to my knees the second you get home"):
                data["current_hole"] = "mouth"
                data["step"] = "choose_tool"
                st.rerun()

        # ── Choose Tool for Current Hole ──
        elif data["step"] == "choose_tool":
            
            if data["current_hole"] == "ass":
                type_out(f"Mmm… my tight little asshole first? God yes… I’ve been fingering it slow all day, getting it slick just for you.")
                show_media("3_holes_opening_ass1.jfif")
                type_out("How do you want to take it tonight?")
            elif data["current_hole"] == "pussy":
                type_out(f"My pussy first? Ohhh yes… it’s already dripping down my thighs thinking about you coming home to our place.")
                show_media("3_holes_opening_pussy1.jfif")
                type_out("What do you want to fuck it with?")
            else:  # mouth
                type_out(f"My mouth first? Mmm… I’m already on my knees in my head, lips parted, waiting to taste you.")
                show_media("3_holes_opening_mouth_choice1.jpeg")
                type_out("How do you want to use it?")
            
            c1, c2 = st.columns(2)
            if c1.button("Your cock… I want to feel you deep"):
                data["tool"] = "dick"
                data["step"] = "action"
                st.rerun()
            
            if c2.button("A toy… tease me until I’m begging for the real thing"):
                data["tool"] = "toy"
                data["step"] = "action"
                st.rerun()

        # ── Action / Claim for Current Hole ──
        elif data["step"] == "action":
            hole = data["current_hole"]
            tool = data["tool"]
            
            # --- DICK PATH ---
            if tool == "dick":
                if hole == "ass":
                    type_out("That’s right baby… fuck this little ass with that thick cock… stretch me wide, make me moan your name.")
                    show_media("3_holes_opening_ass_dick_choice1.jfif")
                    type_out("You gonna cum for me? Fill my tight hole?")
                    
                    if st.button("Cumming – breed my ass"):
                        show_media("3_holes_opening_ass_dick_cum1.jfif")
                        type_out("Oh fuck yes… feel me clenching… milking every hot drop deep inside…")
                        data["claimed"]["ass"] = True
                        data["step"] = "next"
                        st.rerun()

                elif hole == "pussy":
                    type_out("Fuck that little pussy, baby… pound it deep, make it grip you so tight.")
                    show_media("3_holes_opening_pussy_dick_fucking1.jfif")
                    type_out("You gonna cum inside me?")
                    
                    if st.button("Fill my Pussy Up"):
                        show_media("3_holes_opening_pussy_dick_cum1.jfif")
                        type_out("Mmm yes… feel my pussy pulsing… taking every thick spurt…")
                        data["claimed"]["pussy"] = True
                        data["step"] = "next"
                        st.rerun()

                elif hole == "mouth":
                    show_media("3_holes_opening_mouth2.jfif")
                    type_out("Let me suck that cock… shove it down my throat… thank you for every dollar you saved.")
                    
                    if st.button("Fuck I’m cumming – down my throat"):
                        show_media("3_holes_mouth_dick1.jfif")
                        type_out("Mmm… swallowing every hot rope… throat working around you…")
                        data["claimed"]["mouth"] = True
                        data["step"] = "next"
                        st.rerun()

            # --- TOY PATH ---
            elif tool == "toy":
                if hole == "ass":
                    type_out("Ohhh… you want to see me squirm while you fuck me with a toy?")
                    show_media("3_holes_opening_ass_toy1.jfif")
                    
                    if st.button("Fuck it – edge me hard"):
                        type_out("Oh god… that thick toy stretching my ass… I’m shaking, dripping, so close…")
                        data["claimed"]["ass"] = True
                        data["step"] = "next"
                        st.rerun()

                elif hole == "pussy":
                    type_out("You want to tease my pussy with a toy… make me desperate for your cock?")
                    show_media("3_holes_opening_pussy_toy_fucking1.jfif")
                    
                    if st.button("Tease – edge me"):
                        type_out("Ohhh my god… I’m gonna cum… please hurry home…")
                        # Add sub-step for nested button fix
                        data["substage"] = 1 
                        st.rerun()
                        
                    if data.get("substage") == 1:
                        if st.button("Make me cum"):
                            show_media("3_holes_opening_toy_mouth_pussy.jfif")
                            type_out("Fuuuck… cumming so hard around the toy… pussy gushing…")
                            data["claimed"]["pussy"] = True
                            data["step"] = "next"
                            data["substage"] = 0 # reset
                            st.rerun()

                elif hole == "mouth":
                    type_out("Shove that toy in my mouth… fuck it like you’ll fuck me later.")
                    show_media("3_holes_mouth_toy1.jpeg")
                    
                    if st.button("Finish"):
                        data["claimed"]["mouth"] = True
                        data["step"] = "next"
                        st.rerun()

        # ── STAGE: Next Hole or Finish ──
        elif data["step"] == "next":
            remaining = [h for h in ["pussy", "ass", "mouth"] if not data["claimed"][h]]
            
            if remaining:
                type_out("Mmm… one hole down… I’m still trembling. Which one next, baby?")
                
                # Dynamic columns based on remaining
                cols = st.columns(len(remaining))
                for i, hole in enumerate(remaining):
                    if cols[i].button(f"Next: my {hole}"):
                        data["current_hole"] = hole
                        data["step"] = "choose_tool"
                        st.rerun()
            else:
                # All claimed – finish
                simulate_thinking(3.0)
                type_out("Ohhh fuck baby… you just claimed all three… I’m shaking, leaking, completely yours.")
                type_out("Three years of saving… and now we’re so close to our own place. To nights like this whenever we want.")
                type_out("I’m still at home… dripping… waiting for you. Come home soon, Daddy.")
                
                if st.button("Prize complete – back to casino (I’ll stay ready for you)"):
                    st.session_state.pop("all_3_holes", None)
                    st.session_state.turn_state = "PRIZE_DONE"
                    st.rerun()

# --- UPSIDE DOWN THROAT FUCK PRIZE ---
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN_THROAT_FUCK":
    # 1. Init Data
    if "upside_throat_fuck" not in st.session_state:
        st.session_state.upside_throat_fuck = {"stage": 0}
    
    data = st.session_state.upside_throat_fuck

    # ── Stage 0: Intro & The Choice ──
    if data["stage"] == 0:
        type_out("Okay baby, you've fucking leveled up. Upside-down throat fuck.")
        type_out("I'm pretty sure you already know exactly how this filthy setup works…")

        c1, c2 = st.columns(2)
        
        # Option 1: Save & Exit
        if c1.button("I do, thanks (save & exit)"):
            st.session_state.data["inventory"].append("Upside Down Throat Fuck")
            save_data(st.session_state.data)
            type_out("Saved for later. Good self control, daddy.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
        # Option 2: Play the scene
        if c2.button("I do… but I love it when you talk filthy about it"):
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: The Description ──
    elif data["stage"] == 1:
        type_out("Ohhh, since you want me to get nasty and spell out every dirty detail… because you get off so hard when I talk like a complete slut… fine. I'll tell you everything.")
        
        simulate_thinking(2.5)
        type_out("I’m lying on my back right at the edge of the bed, head dangling off upside-down, mouth forced wide open like a hungry little cocksleeve. Throat perfectly lined up, ready to be used as your personal fuck-pipe.")

        simulate_thinking(2.0)
        type_out("Let me guess… you want the nasty pictures too, don’t you? Wanna see what a messy, drooling wreck I become for you?")

        if st.button("Fuck yes, show me the pictures"):
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: The Visuals ──
    elif data["stage"] == 2:
        show_media("upside_down_1.jpeg")
        
        type_out("My blonde hair hangs down toward the floor like a cheap curtain. Green eyes staring up at you, already watering a little in anticipation. My whole naked body laid out like an offering—tits heaving, legs spread, cunt already glistening and twitching while you get to ruin my throat.")

        show_media("upside_down_3.jpeg")

        type_out("You press that thick cock against my lips… then slowly feed it in. Past my tongue. Past my tonsils. All the way down my upside-down throat until my nose is mashed against your balls and I’m choking on you.")

        simulate_thinking(3.0)
        type_out("Slow at first… then you start really fucking my face. Long, full strokes that make my throat bulge visibly. Gagging wetly around every thrust. Thick ropes of drool and spit pouring up my face, over my eyes, into my hair—gravity turning me into your sloppy, slobbering mess.")

        show_media("upside_down_4.jpg")

        type_out("And while you’re balls-deep in my gagging throat, your hands get to play with whatever the fuck they want:")

        if st.button("Like what?"):
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: The Hands & Finale ──
    elif data["stage"] == 3:
        type_out("Shove two or three fingers knuckle-deep in my soaked cunt, curling hard against that spot that makes me cum...")
        type_out("Rub vicious little circles on my swollen clit until my hips jerk and grind against nothing...")
        type_out("Tease my nipples until I whimper around your cock...")
        type_out("Slide a slick finger (or two) straight into my tight asshole, stretching me open while you choke me with dick...")

        show_media("upside_down_5.jpg")
        type_out("—whatever makes me clench harder around your dick.")

        simulate_thinking(2.0)
        type_out("No time limit.")
        type_out("You decide how fast, how deep. You can go slow and make me suffer every inch…")
        type_out("I stay right there—head hanging, throat open, body presented—until you’re done dumping load after load…")
        
        show_media("upside_down_6.jpg")

        c1, c2 = st.columns(2)
        
        if c1.button("Save for later"):
            st.session_state.data["inventory"].append("Upside Down Throat Fuck")
            save_data(st.session_state.data)
            type_out("Smart. I'll be waiting on the edge of the bed whenever you're ready.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
        if c2.button("Use this NOW"):
            # Redeem immediately
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.data["history_log"].append(f"{ts} - REDEEMED: Upside Down Throat Fuck")
            save_data(st.session_state.data)
            
            type_out("Then come get it, daddy. I'm already in position. 😈")
            st.session_state.pop("upside_throat_fuck", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()


# --- TONGUE TEASE ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    if "tongue_tease" not in st.session_state:
        st.session_state.tongue_tease = {"stage": "DECISION", "edging_level": 0, "begged": False, "impatient": False}
    if check_decision("tongue_tease", "Tongue Tease"): pass
    else:
        data = st.session_state.tongue_tease
        if data["stage"] == 0:
            type_out("Mmm daddy… you won the **Tongue Tease** prize 😈")
            type_out("This is where your girlfriend is gonna kneel between your legs and worship just the tip of that thick cock with my tongue and lips… nothing else, while you stroke the rest yourself.")
            show_media("grok_video_2026-01-18-13-54-56.mp4")
            type_out("Rules are simple: I only tease the head — slow licks, soft sucks, swirling around the tip. You stroke the shaft, edge yourself, but you don't cum until I say. Beg nicely… or rush me and see what happens.")
            c1, c2 = st.columns([1, 3])
            if c1.button("Yes baby, I'll obey"): data["stage"] = 1; st.rerun()
            if c2.button("Fuck the rules… "): data["impatient"] = True; data["stage"] = 1; st.rerun()
        elif data["stage"] == 1:
            show_media("tongue_tease_tip12.JPG")
            type_out("Look at this cock… already leaking for me. I lean in close, hot breath on the tip.") 
            show_media("tongue_tease_tip66.JPG")
            type_out("My tongue flicks out, slow circle around the head, tasting your precum… then a soft kiss right on the slit.")
            show_media("tongue_tease_tip11.JPG")
            type_out("Mmm… do you like that? Keep stroking slow while I tease…")
            show_media("tongue_tease_tip10.JPG")
            if st.button("Please baby… more tongue, I'm begging"): data["begged"] = True; data["edging_level"] += 2; data["stage"] = 2; st.rerun()
            if st.button("Suck it harder… stop teasing"): data["impatient"] = True; data["edging_level"] += 1; data["stage"] = 2; st.rerun()
        elif data["stage"] == 2:
            simulate_thinking(2.0)
            show_media("tongue_tease_tip2.JPG")
            type_out("I wrap my lips around the tip only… gentle suck, gentle tongue swirling")
            add_narrator("Her eyes stay locked on yours, watching every twitch of your cock as you stroke.")
            simulate_thinking(2.0)
            show_media("tongue_tease_tip1.JPG")
            reason = "because you begged so sweetly like a good boy" if data["begged"] else "because you're being impatient and greedy"
            type_out(f"I'm being extra mean with the tease {reason}… just the tip, baby.")
            c1, c2, c3 = st.columns(3)
            if c1.button("Fuck… please swirl faster, I need it"): data["edging_level"] += 2; data["stage"] = 3; st.rerun()
            if c2.button("Keep it slow… I'm trying to hold on"): data["edging_level"] += 1; data["stage"] = 3; st.rerun()
            if c3.button("Suck the whole head… I'm losing it"): data["impatient"] = True; data["edging_level"] += 3; data["stage"] = 3; st.rerun()
        elif data["stage"] == 3:
            type_out("God you're throbbing so hard… tip swollen, leaking nonstop.")
            simulate_thinking(2.0)
            show_media("tongue_tease_tip7.JPG")
            type_out("I flick faster, suck the head softly like a lollipop, tasting every drop you give me.")
            add_narrator("Your hand is pumping the shaft… balls tight, so close but not allowed yet.")
            if data["impatient"]: type_out("Since you keep rushing… I pull back just enough to deny you the warmth for a few seconds. Bad boy.")
            c1, c2, c3 = st.columns(3)
            if c1.button("Please please… let me cum, I'm begging"): data["begged"] = True; data["edging_level"] += 4; data["stage"] = 4; st.rerun()
            if c2.button("Hold the edge… keep teasing me"): data["edging_level"] += 2; data["stage"] = 4; st.rerun()
            if c3.button("Fuck this… I'm cumming now"): data["stage"] = "ruin"; st.rerun()
        elif data["stage"] == 4:
            simulate_thinking(2.0)
            show_media("tongue_tease_tip5.JPG")
            if data["edging_level"] >= 5 or data["begged"]:
                type_out("You've been such a good boy… edging so hard for my tongue.")
                type_out("Stroke faster now… I'm sucking the tip hard, tongue swirling like crazy.")
                if st.button("Cum for me… give me that load on my tongue"):
                    simulate_thinking(2.0)
                    show_media("tongue_tease_tip5.JPG")
                    type_out("Yes daddy! You explode — hot ropes shooting across my tongue, lips, chin… I lap it all up greedily.")
                    add_narrator("She moans softly, savoring every drop, eyes sparkling with satisfaction.")
                    if st.button("Best prize ever… thank you baby"): del st.session_state.tongue_tease; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
            else:
                type_out("Not yet… you're not desperate enough.")
                type_out("I pull my mouth away completely… no more tongue until you beg properly.")
                show_media("tongue_tease_tip8.JPG")
                type_out("Edge denied. Better luck next time, baby.")
                add_narrator("She smirks, licking her lips, leaving you throbbing and unfinished.")
                if st.button("Fuck… I accept the denial"): del st.session_state.tongue_tease; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
        elif data["stage"] == "ruin":
            type_out("Oh no you don't… you tried to rush and cum without permission.")
            type_out("I pull off right as you start pulsing — ruining it completely.")
            simulate_thinking(2.0)
            show_media("ruined.jpg")
            type_out("Look at that weak little dribble… all that buildup wasted. Next time obey the tease.")
            if st.button("Sorry baby… I'll be good next time"): del st.session_state.tongue_tease; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ROAD HEAD PRIZE ---
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    if "road_head" not in st.session_state: st.session_state.road_head = {"stage": "DECISION", "risk_level": "medium", "control": "you"}
    if check_decision("road_head", "Road Head"): pass
    else:
        data = st.session_state.road_head
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Road Head**")
            type_out("Fuck typing… 😈")
            type_out("Fuck yes baby… you just won **Road Head** 😈")
            simulate_thinking(2.2)
            type_out("Your dirty little girlfriend is gonna suck your cock the whole drive home… exactly 3 full songs on the playlist.")
            simulate_thinking(2.4)
            type_out("I’ll start when the first beat drops… tease you slow, then deepthroat you through every chorus… finish you right as the last song fades.")
            type_out("Buckle up, daddy… how risky do you want this drive to feel?")
            cols = st.columns(3)
            if cols[0].button("Low risk – quiet back roads, no traffic, just us", key="low_risk"): data["risk_level"] = "low"; data["stage"] = 1; st.rerun()
            if cols[1].button("Medium risk – some cars around, windows tinted dark", key="med_risk"): data["risk_level"] = "medium"; data["stage"] = 1; st.rerun()
            if cols[2].button("High risk – highway, passing trucks, windows cracked a bit", key="high_risk"): data["risk_level"] = "high"; data["stage"] = 1; st.rerun()
        elif data["stage"] == 1:
            risk_desc = {
                "low": "quiet back roads… empty streets… just the hum of the engine and my mouth on you… super safe but still so fucking hot",
                "medium": "some traffic… cars passing now and then… windows tinted dark… heart pounding every time someone gets close",
                "high": "busy highway… trucks rolling beside us… windows cracked just enough… anyone could glance over and catch me slurping your cock"
            }[data["risk_level"]]
            simulate_thinking(2.0)
            type_out(f"Engine’s running… playlist queued… 3 songs, no stopping. {risk_desc}")
            simulate_thinking(2.3)
            type_out("I lean over the console… unzip you sooo slow… pull your hard cock out… already throbbing and leaking for my mouth 🥵")
            show_media("car2.jpeg")
            type_out("You drive… I suck. Who controls the pace, daddy?")
            c1, c2 = st.columns(2)
            if c1.button("You control – grab my hair and fuck my mouth while you steer", key="you_control"): data["control"] = "you"; data["stage"] = 2; st.rerun()
            if c2.button("I control – I tease and deepthroat at my own filthy rhythm", key="me_control"): data["control"] = "me"; data["stage"] = 2; st.rerun()
        elif data["stage"] == 2:
            if data["control"] == "you":
                simulate_thinking(2.1)
                type_out("Your hand tangled in my hair… guiding me down hard… forcing your cock deep into my throat while you keep one eye on the road.")
                simulate_thinking(2.4)
                type_out("I gag a little… drool running down your shaft… but I take every inch, humming around you as the first song builds.")
            else:
                simulate_thinking(2.2)
                type_out("I take full control… slow wet licks up the shaft… then swallowing you whole, bobbing to the beat of the music.")
                simulate_thinking(2.5)
                type_out("My tongue swirls the head between verses… sucking hard on every chorus… making you throb while you try not to swerve.")
            show_media("car3.png")
            type_out("Song 2 starting… fuck you’re so close already aren’t you?")
            if data["risk_level"] == "high":
                simulate_thinking(2.6)
                type_out("Truck right beside us… driver could look down any second and see my lips stretched around your cock. I don’t stop — I suck harder.")
            elif data["risk_level"] == "medium":
                simulate_thinking(2.4)
                type_out("Car pulling up at the light… I slow just enough to tease… lips sealed tight around the tip… eyes up at you like a good girl.")
            show_media("car4.jpg")
            type_out("Last song… you’re throbbing so hard in my mouth. What do we do, daddy?")
            c1, c2 = st.columns(2) 
            if c1.button("Risky finish – cum in my mouth while driving", key="risky_finish"): data["stage"] = "risky_finish"; st.rerun()
            if c2.button("Edge home – no cumming until we’re in the driveway", key="edge_home"): data["stage"] = "edge_home"; st.rerun()
        elif data["stage"] == "risky_finish":
            simulate_thinking(2.2)
            type_out("No pulling over… I deepthroat you through the final chorus, throat milking every pulse as you cum hard.")
            simulate_thinking(2.6)
            type_out("You grip the wheel tight, moaning loud… shooting thick ropes straight down my throat while cars zoom by… risky as fuck and so fucking hot.")
            st.session_state.pop("road_head", None); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
        elif data["stage"] == "edge_home":
            simulate_thinking(2.3)
            type_out("No cumming yet… I tease just the tip the rest of the way home… keeping you rock-hard and leaking.")
            simulate_thinking(2.4)
            type_out("We pull into the driveway… your cock still throbbing in my mouth… now you get the full finish inside. Saved every drop for the bedroom, daddy 🍆")
            st.session_state.pop("road_head", None); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
        if st.button("🎰 The Exit - Save the road head for the next drive?", key="road_exit_global"):
            st.session_state.pop("road_head", None); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- PLUG TEASE PRIZE ---
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    if "plug_tease" not in st.session_state: st.session_state.plug_tease = {"stage": "DECISION", "stretch_level": None, "tease_level": 0, "show_reward": False}
    if check_decision("plug_tease", "Plug Tease"): pass
    else:
        data = st.session_state.plug_tease
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Plug Tease**")
            show_media("plug_tease_preview.jpeg")
            type_out("Mmm daddy… you won the **Plug Tease** tonight 😈")
            simulate_thinking(2.2)
            type_out("Your filthy little girlfriend is gonna lube up a nice thick butt plug…")
            simulate_thinking(2.4)
            type_out("and wear it for you… all day while you're at work… feeling it stretch and fill my tight ass the whole time…")
            type_out("I'll be walking around, sitting, bending over… every little move reminding me of you…")
            simulate_thinking(2.5)
            type_out("How stretched do you want your girl when you finally get home? 🥵")
            show_media("plug_tease_3.jpeg")
            c1, c2, c3 = st.columns(3)
            if c1.button("Barely stretched\nPut it in 1 hour before I get off", key="barely"): data["stretch_level"] = "barely"; data["stage"] = 1; st.rerun()
            if c2.button("Halfway stretched\nPut it in at lunch time", key="halfway"): data["stretch_level"] = "halfway"; data["stage"] = 1; st.rerun()
            if c3.button("Fully stretched\nPut it in NOW and keep it until you get home", key="full"): data["stretch_level"] = "full"; data["stage"] = 1; st.rerun()
        elif data["stage"] == 1:
            show_media("plug_tease_4.jpeg")
            simulate_thinking(1.9)
            type_out(f"**{data['stretch_level'].capitalize()}** it is… you're so mean to me daddy 😩")
            simulate_thinking(2.3)
            type_out("I'm lubing it up right now… cold and slick… circling my little hole…")
            simulate_thinking(2.6)
            type_out("Here it goes… slow… stretching me open… fuck it feels so good…")
            if data["stretch_level"] == "barely": type_out("Only putting it in an hour before I leave work… just enough to tease… keep me needy all day…")
            elif data["stretch_level"] == "halfway": type_out("Putting it in at lunch… gonna feel every inch for the rest of the afternoon… squirming in my chair…")
            elif data["stretch_level"] == "full": type_out("Putting it in NOW… deep… full… gonna wear it the whole time until you get home… clenching around it thinking of you…")
            simulate_thinking(2.8)
            type_out("Do you want a little preview of your final reward when you finally get home and pull it out…? 👀")
            if st.button("Show me the reward view 😈", key="show_reward"): data["show_reward"] = True; data["stage"] = 2; st.rerun()
            if st.button("Save the reward for when you get home…", key="save_reward"): data["stage"] = 2; st.rerun()
        elif data["stage"] == 2:
            if data["show_reward"]:
                show_media("plug_teasereward.jpeg")
                simulate_thinking(2.4)
                type_out("This is what you'll see when you walk in… ass plugged, spread, dripping… waiting for you to take it out and replace it with something much bigger 🍆")
                simulate_thinking(2.3)
                type_out("I've been stretched and filled for you all day… now I'm aching for the real thing…")
            else:
                simulate_thinking(2.1)
                type_out("Okay… I'll keep this reward hidden until you're here to see it in person…")
                simulate_thinking(2.5)
                type_out("Just imagine how gaped and ready it'll be after wearing it so long…")
            simulate_thinking(2.2)
            type_out("Plug tease complete, daddy… but now I need you to come home and wreck this stretched little hole 💦")
            if st.button("Prize complete – come claim your girl now?", key="plug_finish"): st.session_state.pop("plug_tease", None); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
        if st.button("🎰 The Exit - Save some stretching for later?", key="plug_exit_global"): st.session_state.pop("plug_tease", None); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- TOY PIC PRIZE ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    if "toy_pic" not in st.session_state: st.session_state.toy_pic = {"stage": "DECISION", "focus": None, "subchoice": None, "plug_keep": None, "mood": "teasing"}
    if check_decision("toy_pic", "Toy Pic"): pass
    else:
        data = st.session_state.toy_pic
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Toy Pic**")
            type_out("Oh fuck baby… you won the **Toy Pic** tease 😈 Your filthy little girlfriend is gonna play with a nice toy just for you.")
            show_media("toy_butt_in5.jpeg")
            simulate_thinking(2.2)
            type_out("Ready to watch me fuck myself daddy?")
            show_media("toy_pic.jpeg")
            focuses = ["Ass", "Pussy", "Mouth"]
            data["focus"] = st.radio("which hole do you want me to tease with this toy first?", focuses, key="toy_hole_choice")
            if st.button("Show me 😈", key="toy_start"): data["stage"] = 1; st.rerun()
        elif data["stage"] == 1:
            if data["focus"] == "Ass":
                type_out("This ass?")
                show_media("in_this_ass.jpg")
                simulate_thinking(1.8)
                type_out("You wanna see my tiny asshole stretched and filled with what?")
                subchoices = ["Plug", "Toy"]
                data["subchoice"] = st.radio("Choose your weapon:", subchoices, key="ass_fill_choice")
                if st.button("Stretch me", key="ass_fill_confirm"): data["stage"] = 2; st.rerun()
            elif data["focus"] == "Pussy":
                type_out("In my pussy?")
                type_out("Now teasing my pussy with the tip… just a little getting so wet for you…")
                show_media("toy_ass3.jpeg")
                simulate_thinking(2.4)
                type_out("There daddy… toy sliding deep into my pussy, lips stretched around it, dripping everywhere. God it feels so good thinking of your cock")
                show_media("plug_pussy1.jpg")
                if st.button("Bonus for being a good boy", key="pussy_bonus"): data["stage"] = 3; st.rerun()
            elif data["focus"] == "Mouth":
                type_out("Stretching out my mouth")
                show_media("toy_in_mouth.jpg")
                if st.button("Bonus for being a good boy", key="mouth_bonus"): data["stage"] = 3; st.rerun()
        elif data["stage"] == 2 and data["focus"] == "Ass":
            if data["subchoice"] == "Plug":
                show_media("tease_in_ass_plug.jpg")
                show_media("plug_in1.jpeg")
                type_out("Plug in ass, should I keep it there for you to take out?")
                keep_options = ["Keep it.   imma wreck that hole when I get home", "Take it out for now"]
                data["plug_keep"] = st.radio("Your choice daddy:", keep_options, key="plug_keep_choice")
                if st.button("Confirm", key="plug_final"): data["stage"] = 3; st.rerun()
            elif data["subchoice"] == "Toy":
                show_media("tease_in_ass.jpeg")
                show_media("vibe_in_ass.jpg")
                type_out("There you go daDdy… toy sliding deep into my ass stretched around it, dripping everywhere. God it feels so good thinking of your cock instead")
                show_media("all_3_4.jpeg")
                if st.button("Bonus for being a good boy", key="toy_ass_bonus"): data["stage"] = 3; st.rerun()
        elif data["stage"] == 3:
            show_media("toy_in_mouth_ass.jpg")
            type_out("Bonus... For being a good boy")
            if st.button("Toy prize complete – now fuck me for real?", key="toy_finish"): st.session_state.pop("toy_pic", None); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
        if st.button("🎰 The Exit - Claim prize now or later", key="toy_exit_global"): st.session_state.pop("toy_pic", None); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- DOGGY STYLE READY PRIZE ---
elif st.session_state.turn_state == "PRIZE_DOGGY_STYLE_READY":
    # 1. Init Data
    if "doggy_ready" not in st.session_state:
        st.session_state.doggy_ready = {
            "stage": "DECISION", 
            "substage": 0
        }

    # 2. Check Decision
    if check_decision("doggy_ready", "Doggy Style Ready"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.doggy_ready

        # ── STAGE 0: Intro & Tease ──
        if data["stage"] == 0:
            type_out("Daddy… you won **Doggy Style Ready** 😩🍑")
            simulate_thinking(2.0)
            
            type_out("This is the prize where, the moment you whisper 'doggy style ready'… I become yours completely. No hesitation. Just raw, aching need.")
            
            type_out("I’ll drop to all fours… ass arched high, back dipped low, pussy already slick and swollen… pre-lubed, pulsing, waiting for you to slide in deep from behind.")
            type_out("My body fully exposed… thighs trembling… dripping for your thick cock to claim every inch. How does that sound, Daddy? Let me guess… you want to see it?")
            
            show_media("doggy_ready_opening2.jpeg")

            if st.button("Of course I do – show me how you prepare"):
                data["stage"] = 1
                data["substage"] = 0
                st.rerun()

        # ── STAGE 1: The Ritual (Bathroom & Oiling) ──
        elif data["stage"] == 1:
            
            if data["substage"] == 0:
                type_out("You’re such a visual creature… fine, I’ll paint every filthy detail for you.")
                type_out("You catch me bending over… or your eyes just lock on my ass like they always do… and then you say it…")
                
                if st.button("Doggy style ready", key="say_doggy_ready"):
                    data["substage"] = 1
                    st.rerun()

            elif data["substage"] == 1:
                type_out("Those words hit me like a spark… my pussy clenches hard, instantly wet. I grab the lube and hurry to the bathroom, heart pounding, thighs already slick.")
                show_media("doggy_ready_opening3.jpeg")
                
                type_out("In there… I pour warm oil over my swollen lips… let it drip down my crack… fingers gliding in slow circles, coating every inch of my tight pussy and ass until I’m glistening and ready to take you deep.")
                type_out("(Yes, Daddy… I come pre-oiled for this one… my holes aching, slippery, desperate to feel you stretch me open.)")
                
                if st.button("What position do you get into for me?"):
                    data["substage"] = 2
                    st.rerun()

            elif data["substage"] == 2:
                type_out("Don’t play innocent… you know I was going to show you anyway.")
                show_media("doggy_ready_opening4.jpeg")
                
                type_out("I crawl onto the bed… knees wide… back arched like I’m offering myself completely… ass lifted high, cheeks parted just enough so you can see my oiled pussy glistening, lips puffy and parted, asshole winking softly.")
                type_out("Every breath makes me tremble… dripping down my thighs… clit throbbing… waiting for you to walk in and take what’s yours.")
                
                if st.button("Walk in… see me like this"):
                    data["stage"] = 2
                    data["substage"] = 0
                    st.rerun()

        # ── STAGE 2: The Final Reveal ──
        elif data["stage"] == 2:
            show_media("doggy_ready_opening5.jpeg")
            
            type_out("There I am… oiled and glistening… ass presented high, pussy dripping, body quivering with need… no words, just me on all fours like your perfect, obedient prize.")
            type_out("Hopefully you won’t be cruel and leave me here for hours… edging myself senseless… clit swollen… holes clenching around nothing… silently begging for your cock to finally fill me.")
            
            type_out("So… what are you going to do now that I’m doggy style ready, dripping, and aching for you, Daddy?")
            
            if st.button("Prize complete – back to casino"):
                st.session_state.pop("doggy_ready", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

# --- FLASHBACK PRIZE (TIME TRAVEL) ---
elif st.session_state.turn_state == "PRIZE_FLASHBACK":
    # 1. Init Data
    if "flashback" not in st.session_state:
        st.session_state.flashback = {
            "stage": "PRE_INTRO",
            "substage": 0,
            "mode": None,  # "home_24" or "hotel_10"
            "outfit": None
        }

    # 2. Check Decision
    if check_decision("flashback", "Flashback"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.flashback

        # ── PRE-INTRO: Time Travel Choice ──
        if data["stage"] == "PRE_INTRO":
            type_out("****SLOW CLAP**** You've won the ultimate prize, the jackpot: “FLASHBACK”.")
            simulate_thinking(3.0)
            
            type_out("You see… I've been thinking about us. Eight years ago we were wild, broke… Speed hits, bong rips, coffee staring at galaxies till sunrise…")
            
            # COFFEE GALAXY
            show_media(random.choice([
                "coffee_gallaxy1.jfif", "coffee_gallaxy2.jfif", "coffee_gallaxy3.jfif", 
                "coffee_gallaxy4.jfif", "coffee_gallaxy5.jpg"
            ]))
            
            type_out("What if we time travel back? Just for a bit. Pretend it's then — no drift, no bills, just us.")
            type_out("What do you say? You wanna take a trip back, with me?")
            
            # INVITE
            show_media(random.choice([
                "flashback_invite1.jfif", "flashback_invite2.jfif", "flashback_invite3.jfif"
            ]))
            
            c1, c2 = st.columns(2)
            if c1.button("Time travel at home in our room — 24 full hours"):
                data["mode"] = "home_24"; data["stage"] = "INTRO"; st.rerun()
            if c2.button("Time travel in a hotel — 10 intense hours"):
                data["mode"] = "hotel_10"; data["stage"] = "INTRO"; st.rerun()

        # ── STAGE: INTRO (branches based on mode) ──
        if data["stage"] == "INTRO":
            
            # === HOME MODE ===
            if data["mode"] == "home_24":
                type_out("Home it is — our room, 24 hours straight. Door locked, world off.")
                type_out("When you come home, I’ll be right there to greet you… pants down, shirt up, mouth wide, tongue out.")
                
                # HOME INTRO
                show_media(random.choice(["slave_day_opening1.jfif", "slave_day_opening2.jfif"]))
                
                type_out("So tell me, what would you have done to me 8 years ago?")
                c1, c2, c3 = st.columns(3)
                if c1.button("Go take a shower (Shower Tease)"):
                    data["stage"] = "SHOWER_TEASE"; st.rerun()
                if c2.button("Stick fingers in me (Rough Greeting)"):
                    data["stage"] = "ROUGH_GREETING"; st.rerun()
                if c3.button("Guide me to shower (In Shower)"):
                    data["stage"] = "IN_SHOWER"; st.rerun()

            # === HOTEL MODE ===
            else:  
                # Substage 0: Pick Outfit
                if data["substage"] == 0:
                    type_out("Hotel escape — 10 hours in a cheap room. I'm waiting for you… but first, you dress me up.")
                    
                    # DRESS UP TEASER
                    show_media(random.choice(["dress_me_up1.jfif", "dress_me_up2.jfif"]))
                    
                    c1, c2, c3 = st.columns(3)
                    if c1.button("Pink and Pretty — mini dress"):
                        data["outfit"] = "pink_dress"
                        type_out("You pick the pink and pretty — tight mini dress, barely covering my ass.")
                        show_media(random.choice([
                            "flashback_hotel_pink_dress1.jfif", "flashback_hotel_pink_dress2.jfif", 
                            "flashback_hotel_pink_dress3.jfif", "flashback_hotel_pink_dress4.jfif"
                        ]))
                        data["substage"] = 1; st.rerun()
                        
                    if c2.button("Black skirt — school girl style"):
                        data["outfit"] = "black_skirt"
                        type_out("All black and naughty, easy access skirt. 'Your naughty schoolgirl waiting.'")
                        show_media(random.choice(["flashback_hotel_black_skirt1.jfif", "flashback_hotel_black_skirt2.jfif"]))
                        data["substage"] = 1; st.rerun()
                        
                    if c3.button("Just black lace lingerie + choker"):
                        data["outfit"] = "lace_only"
                        type_out("Black lace lingerie — sheer bra and panties. 'Just lace and me.'")
                        show_media(random.choice([
                            "flashback_hotel_lace1.jfif", "flashback_hotel_lace2.jfif", 
                            "flashback_hotel_lace3.jfif", "flashback_hotel_lace4.jfif"
                        ]))
                        data["substage"] = 1; st.rerun()

                # Substage 1: The Reveal & Choice
                elif data["substage"] == 1:
                    type_out("Dressed up and pretty… I spread on the hotel bed. 'Door opens? Come claim your dolled-up girl.'")
                    
                    # HOTEL BED POSE
                    show_media(random.choice([
                        "flashback_hotel_bed_pose1.jfif", "flashback_hotel_bed_pose2.jfif", 
                        "flashback_hotel_bed_pose3.jfif"
                    ]))
                    
                    type_out("So tell me, possessive boy… what are you doing the second you walk in?")
                    c1, c2, c3 = st.columns(3)
                    if c1.button("Ignore me first (Shower Tease)"):
                        data["stage"] = "SHOWER_TEASE"; st.rerun()
                    if c2.button("Claim me now (Rough Greeting)"):
                        data["stage"] = "ROUGH_GREETING"; st.rerun()
                    if c3.button("Drag me to shower (In Shower)"):
                        data["stage"] = "IN_SHOWER"; st.rerun()

        # ── PATH: SHOWER TEASE ──
        elif data["stage"] == "SHOWER_TEASE":
            if data["substage"] == 0:
                type_out("Oh fuck yes… knees on tile, pants tangled. Stay frozen till you decide I've earned it.")
                
                # SHOWER TEASE OUTSIDE
                show_media(random.choice(["slave_day_outsideshower1.jfif", "slave_day_outsideshower2.jfif"]))
                
                simulate_thinking(2.0)
                type_out("Hurry back… or don't. I'm throbbing imagining you in there.")
                if st.button("Finish shower & open the door"):
                    data["substage"] = 1; st.rerun()
            
            elif data["substage"] == 1:
                type_out("Mouth wide, eyes closed. Ready… 'fuck my face when you're done teasing.'")
                c1, c2 = st.columns(2)
                if c1.button("Strip & join me in shower"):
                    data["stage"] = "SHOWER_TIME"; st.rerun()
                if c2.button("Take me to bed — start the all-nighter"):
                    data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()

        # ── PATH: ROUGH GREETING ──
        elif data["stage"] == "ROUGH_GREETING":
            if data["substage"] == 0:
                type_out("Door flies open. Fingers slam deep in my cunt, hand stuffing my mouth.")
                
                # ROUGH FINGERING
                show_media(random.choice([
                    "slave_day_introfinger5.jfif", "slave_day_intro_plug.jfif", 
                    "slave_day_introfinger4.jfif", "slave_day_introfinger2.jfif"
                ]))
                
                type_out("Finger-fuck me stupid. Muffled 'don't stop… fuck me dead…'")
                if st.button("Make me cum & clean your fingers"):
                    data["substage"] = 1; st.rerun()
            
            elif data["substage"] == 1:
                type_out("Pussy twitching, clit throbbing… wrecked already. What's next?")
                c1, c2, c3 = st.columns(3)
                if c1.button("Take me to shower"):
                    data["stage"] = "IN_SHOWER"; data["substage"] = 0; st.rerun()
                if c2.button("Watch porn on the couch"):
                    data["stage"] = "PORN_WATCH"; data["substage"] = 0; st.rerun()
                if c3.button("Gaming on the couch"):
                    data["stage"] = "GAMING"; data["substage"] = 0; st.rerun()

        # ── PATH: PORN_WATCH ──
        elif data["stage"] == "PORN_WATCH":
            if data["substage"] == 0:
                type_out("You flop on the couch, porn playing loud. I crawl over, pet outfit hugging me tight.")
                
                # PORN COUCH
                show_media(random.choice([
                    "flashback_porn_couch1.jfif", "flashback_porn_couch2.jfif", 
                    "flashback_porn_couch3.jfif", "flashback_porn_couch4.jfif", "flashback_porn_couch5.jfif"
                ]))
                
                type_out("I mirror the action... deeper sucks, sloppy bobs, tongue swirling.")
                c1, c2 = st.columns(2)
                if c1.button("Take your kitten to bed"):
                    data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()
                if c2.button("Keep watching — finish in my mouth"):
                    type_out("You let the scene play out… I suck harder when the on-screen girl cums.")
                    if st.button("Head to all-nighter"):
                        data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()

        # ── PATH: GAMING ──
        elif data["stage"] == "GAMING":
            if data["substage"] == 0:
                type_out("You flop on the couch, racing game loading. What do you want your wild girl wearing?")
                # Removed "Choice" image as requested
                c1, c2 = st.columns(2)
                if c1.button("Pet outfit — collar, ears, tail plug"):
                    data["substage"] = "pet_outfit"; st.rerun()
                if c2.button("Nothing at all — completely bare"):
                    data["substage"] = "nude"; st.rerun()

            elif data["substage"] == "pet_outfit":
                type_out("Pet outfit it is — collar jingling softly, tail plug snug in my ass.")
                # GAMING PET
                show_media(random.choice(["slave_day_gaming_pet1.jfif", "slave_day_gaming_pet2.jfif", "slave_day_gaming_pet3.jfif"]))
                type_out("Kitten licks up your shaft till you're rock hard, then take you warm and wet into my mouth.")
                c1, c2 = st.columns(2)
                if c1.button("Take your kitten to bed"):
                    data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()
                if c2.button("Keep playing — finish in my mouth"):
                    type_out("You finish the race… I suck harder on your victory lap, bell jingling.")
                    if st.button("Head to all-nighter"):
                        data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()

            elif data["substage"] == "nude":
                type_out("Nothing at all — completely bare. Just me, naked and needy, crawling over.")
                # GAMING NUDE
                show_media(random.choice([
                    "flashback_gaming_nude1.jfif", "flashback_gaming_nude2.jfif", 
                    "flashback_gaming_nude3.jfif", "flashback_gaming_nude4.jfif"
                ]))
                type_out("Skin on skin, tits brushing your legs as I unzip slow...")
                c1, c2 = st.columns(2)
                if c1.button("Take your naked girl to bed"):
                    data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()
                if c2.button("Keep playing — finish in my mouth"):
                    type_out("You finish the race… I suck harder on your victory lap.")
                    if st.button("Head to all-nighter"):
                        data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()

        # ── PATH: IN_SHOWER ──
        elif data["stage"] == "IN_SHOWER":
            if data["substage"] == 0:
                type_out("You step under hot water. I kneel outside tile — naked, mouth open.")
                show_media("slave_day_intro1.jfif")
                if st.button("Done showering? Decide my fate"):
                    data["substage"] = 1; st.rerun()
            elif data["substage"] == 1:
                type_out("Push me off, let me drool on my tits… then back to soaping.")
                c1, c2 = st.columns(2)
                if c1.button("Strip & wash your girl"):
                    data["stage"] = "SHOWER_TIME"; st.rerun()
                if c2.button("Dry off & Bedtime"):
                    data["stage"] = "BEDTIME"; st.rerun()

        # ── PATH: SHOWER_TIME ──
        elif data["stage"] == "SHOWER_TIME":
            type_out("You turn off the water briefly. 'Strip. All the way. Now.'")
            show_media("slave_day_wash.jfif")
            type_out("Hands everywhere — lathering my breasts until nipples are rock-hard.")
            if st.button("Dry off (My tongue is the towel)"):
                data["stage"] = "DRY_OFF"; st.rerun()

        # ── PATH: DRY_OFF ──
        elif data["stage"] == "DRY_OFF":
            type_out("No towel for your cock. Just my tongue.")
            show_media("slave_day_sexy_outfit1.jfif")
            type_out("I kneel again, licking every drop of water off your shaft.")
            if st.button("Take me to bed"):
                data["stage"] = "BEDTIME"; st.rerun()

        # ── PATH: BEDTIME ──
        elif data["stage"] == "BEDTIME":
            type_out("You lead me to bedroom. Naked, ass swaying.")
            # Reuse hotel bed pose for consistency if needed, or specific bedtime pic
            show_media(random.choice(["flashback_hotel_bed_pose1.jfif", "flashback_hotel_bed_pose2.jfif", "flashback_hotel_bed_pose3.jfif"]))
            type_out("Slide under covers, pull me close. All night. Whenever you stir needy.")
            if st.button("Tell me about tomorrow"):
                data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()

        # ── PATH: ALL_NIGHTER ──
        elif data["stage"] == "ALL_NIGHTER":
            if data["substage"] == 0:
                type_out("We're back — eight years ago. Speed hit done, buzz sparking.")
                
                # ALL NIGHTER / BED POSE
                show_media(random.choice([
                    "flashback_hotel_bed_pose1.jfif", "flashback_hotel_bed_pose2.jfif", 
                    "flashback_hotel_bed_pose3.jfif"
                ]))
                
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("Bong Rip"): data["substage"] = "bong"; st.rerun()
                if c2.button("Coffee Universe"): data["substage"] = "coffee"; st.rerun()
                if c3.button("Fuck my face"): data["substage"] = "quick"; st.rerun()
                if c4.button("Plastic Sheets"): data["stage"] = "PLASTIC_SHEETS"; data["substage"] = 0; st.rerun()

            elif data["substage"] == "bong":
                type_out("Pack it, hand it over. I rip deep, hold, exhale slow.")
                c1, c2 = st.columns(2)
                if c1.button("Coffee Universe"): data["substage"] = "coffee"; st.rerun()
                if c2.button("Use me now"): data["substage"] = "play_menu"; st.rerun()

            elif data["substage"] == "coffee":
                type_out("Mugs in hand — coffee hot, cream swirling.")
                c1, c2 = st.columns(2)
                if c1.button("Bong to keep rolling"): data["substage"] = "bong"; st.rerun()
                if c2.button("Use your girl now"): data["substage"] = "play_menu"; st.rerun()

            elif data["substage"] == "play_menu":
                type_out("Buzz electric… want your wild girl?")
                c1, c2, c3 = st.columns(3)
                if c1.button("Fuck my face"): data["substage"] = "quick"; st.rerun()
                if c2.button("Pet Game"): data["substage"] = "pet"; st.rerun()
                if c3.button("DP"): data["substage"] = "dp"; st.rerun()

            elif data["substage"] == "quick":
                type_out("Knees already, mouth wide — 'fuck my face, babe…'")
                show_media("flash_fingers_mouth1.jfif") # QUICK MOUTH
                type_out("Grip hair, pound throat deep.")
                if st.button("Back to choices"): data["substage"] = 0; st.rerun()
                if st.button("End Flashback"): st.session_state.pop("flashback", None); st.session_state.turn_state="PRIZE_DONE"; st.rerun()

            elif data["substage"] == "pet":
                type_out("Leash clips, tug — crawling with high-tingle sass.")
                if st.button("Back to choices"): data["substage"] = 0; st.rerun()
                if st.button("End Flashback"): st.session_state.pop("flashback", None); st.session_state.turn_state="PRIZE_DONE"; st.rerun()

            elif data["substage"] == "dp":
                type_out("Upside-down off bed. 'Fuck my face slow first… then wreck me.'")
                # SLOW DP
                show_media(random.choice(["slave_day_fuck_toys1.jfif", "flash_toys1.jfif", "flash_fuck1.jfif"]))
                if st.button("Back to choices"): data["substage"] = 0; st.rerun()
                if st.button("End Flashback"): st.session_state.pop("flashback", None); st.session_state.turn_state="PRIZE_DONE"; st.rerun()

        # ── PLASTIC SHEETS ──
        elif data["stage"] == "PLASTIC_SHEETS":
            if data["substage"] == 0:
                type_out("Oh fuck yes — plastic sheets time. Dollar-store special.")
                show_media(random.choice(["flashback_plastic_oil7.jfif", "flashback_plastic_oil9.jfif", "flashback_plastic_oil11.jfif"]))
                
                c1, c2, c3 = st.columns(3)
                if c1.button("Fuck my face (Oil dripping)"):
                    type_out("You straddle my chest — oil slick on my tits.")
                    if st.button("Finish & Loop"): data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()
                if c2.button("DP me slippery"):
                    type_out("You bend me over — plastic crinkling.")
                    if st.button("Finish & Loop"): data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()
                if c3.button("Pet slide"):
                    type_out("Leash clips — I crawl slippery on plastic.")
                    if st.button("Finish & Loop"): data["stage"] = "ALL_NIGHTER"; data["substage"] = 0; st.rerun()

     
        # Global Exit
        if st.button("🎰 End Flashback - Save for later?", key="flashback_save_exit_btn"):
            st.session_state.pop("flashback", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
    # Large, obvious buttons for next steps
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Direct link back to Casino Floor
        if st.button("🎰 SPIN AGAIN"): 
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()
            
    with c2:
        if st.button("🏦 Back to Bank"): 
            st.session_state.turn_state = "WALLET_CHECK"
            st.rerun()
            
    with c3:
        if st.button("💾 Save & Logout"): 
            save_data(st.session_state.data)
            st.session_state.history = []
            st.session_state.turn_state = "WALLET_CHECK"
            st.rerun()






























































