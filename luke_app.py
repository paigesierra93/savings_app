import json
import os
import random
import time
import datetime
import streamlit as st

# ==========================================
#       PART 1: SETUP & STYLING
# ==========================================
st.set_page_config(page_title="Exit Plan", page_icon="🎰", layout="wide")

st.markdown("""
    <style>
    /* MAIN BACKGROUND */
    .stApp { 
        background-color: #000000;
        background-image: linear-gradient(147deg, #000000 0%, #1a1a1a 74%);
        color: #ffffff;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }
    
    /* CHAT CONTAINER */
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    /* BUBBLES */
    div[data-testid="stChatMessage"] {
        background-color: rgba(40, 40, 40, 0.9);
        border: 1px solid #555;
        border-radius: 15px;
        padding: 12px 16px;
    }
    div[data-testid="stChatMessage"] p { color: #FFFFFF !important; font-weight: 400; }
    
    /* NARRATOR */
    .narrator {
        text-align: center; color: #ccc;
        font-style: italic; font-size: 14px;
        margin: 15px 0; border-top: 1px solid #444; border-bottom: 1px solid #444; padding: 5px;
    }

    /* NEON BUTTONS */
    .stButton button { 
        width: 100%; border-radius: 25px; font-weight: 600; min-height: 45px;
        background: linear-gradient(45deg, #FF4B4B, #FF9068);
        color: white; border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    .stButton button:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(255, 75, 75, 0.6); }
    
    /* METRIC CARDS */
    div[data-testid="stMetric"] {
        background-color: rgba(30,30,30,0.8);
        border: 1px solid #555;
        padding: 10px;
        border-radius: 10px;
    }
    div[data-testid="stMetric"] label { color: #ffffff !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #00FF00; }
    
    label, .stMarkdown p { color: #ffffff !important; }
    
    </style>
    """, unsafe_allow_html=True)

# ==========================================
#       PART 2: DATA ENGINE
# ==========================================
DATA_FILE = "bank_of_paige.json"

def load_data():
    default_data = {
        "tickets": 0, "tank_balance": 0.0, "tank_goal": 10000.0, 
        "house_fund": 0.0, "wallet_balance": 0.0, "bridge_fund": 0.0,
        "inventory": [],       # NEW: Stores saved prizes
        "history_log": []      # NEW: Logs exactly what happened and when
    }
    if not os.path.exists(DATA_FILE): return default_data
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Critical: This loop adds the new fields to your existing file
            for key, val in default_data.items():
                if key not in data: data[key] = val
            return data
    except: return default_data

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def check_payday_window(admin_code):
    if admin_code == "777": return True, "" 
    today = datetime.datetime.now()
    if today.weekday() == 2: return True, "" # Wednesday
    else:
        days_ahead = (2 - today.weekday() + 7) % 7
        if days_ahead == 0: days_ahead = 7
        remaining = (today + datetime.timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0) - today
        return False, f"🔒 **LOCKED.** Opens in {remaining.days} Days, {remaining.seconds // 3600} Hours."

if "data" not in st.session_state: st.session_state.data = load_data()
if "history" not in st.session_state: 
    st.session_state.history = [{
        "type": "chat", 
        "role": "assistant", 
        "content": "Systems Online. 💋\n\nI'm ready. Did we get a full Paycheck, Dayforce Daily, or some **Side Cash**?"
    }]
if "turn_state" not in st.session_state: st.session_state.turn_state = "WALLET_CHECK"

# ==========================================
#       PART 3: HELPER FUNCTIONS (ALL-IN-ONE)
# ==========================================
import random 
import time

# --- HISTORY MANAGERS ---
def add_chat(role, content):
    """Adds to history without animation (for reloads)."""
    st.session_state.history.append({"type": "chat", "role": role, "content": content})

def add_narrator(content):
    st.session_state.history.append({"type": "narrator", "content": content})

def add_media(filepath):
    """Smartly detects video vs image"""
    if filepath.lower().endswith(('.mp4', '.mov', '.webm')):
        media_type = "video"
    else:
        media_type = "image"
    st.session_state.history.append({"type": "media", "path": filepath, "kind": media_type})

def add_dual_media(path1, path2):
    st.session_state.history.append({"type": "dual_media", "path1": path1, "path2": path2})

# --- ANIMATION HELPERS ---

def simulate_thinking(seconds=None):
    """Shows a subtle 'Paige is typing...' indicator before she speaks."""
    if seconds is None:
        seconds = random.uniform(1.0, 2.5) 
    
    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Paige is typing..."):
            time.sleep(seconds)

def type_out(*args, min_delay=0.03, max_delay=0.08):
    """
    The 'Typewriter' effect. Flexible to handle:
    type_out("text") OR type_out("assistant", "text")
    """
    if len(args) == 1:
        text = args[0]
    elif len(args) == 2:
        text = args[1] # Ignore role, force assistant
    else:
        return

    # 1. Anti-Duplicate Shield
    if st.session_state.history:
        last_msg = st.session_state.history[-1]
        if last_msg.get("role") == "assistant" and last_msg.get("content") == text:
            return 

    # 2. Live Typing Animation
    with st.chat_message("assistant", avatar="paige.png"):
        placeholder = st.empty()
        full_response = ""
        
        words = text.split()
        for i, word in enumerate(words):
            full_response += word + " "
            
            # Add blinking cursor effect
            if i < len(words) - 1:
                placeholder.markdown(full_response + "▌")
            else:
                placeholder.markdown(full_response) # No cursor at the end
            
            # Humanize the delay
            time.sleep(random.uniform(min_delay, max_delay))
            
    # 3. Save to History using the correct helper
    add_chat("assistant", text)

def show_media(path, delay=1.5):
    """Shows media with a 'Sending media...' delay"""
    # Anti-Duplicate Shield
    if st.session_state.history:
        last_item = st.session_state.history[-1]
        if last_item.get("type") == "media" and last_item.get("path") == path:
            return

    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Sending media..."):
            time.sleep(delay)
        
        if os.path.exists(path):
            if path.lower().endswith(('.mp4', '.mov', '.webm')):
                st.video(path)
            else:
                st.image(path, width=300)
        else:
            st.warning(f"Media unavailable: {path}")
            
    if os.path.exists(path):
        add_media(path)

def spin_animation(tier, prizes):
    placeholder = st.empty()
    for _ in range(8):
        placeholder.markdown(f"<h3 style='text-align: center; color: #555;'>🎰 {random.choice(prizes)}...</h3>", unsafe_allow_html=True)
        time.sleep(0.1)
    for _ in range(5):
        placeholder.markdown(f"<h3 style='text-align: center; color: #888;'>🎰 {random.choice(prizes)}...</h3>", unsafe_allow_html=True)
        time.sleep(0.3)
    winner = random.choice(prizes)
    placeholder.markdown(f"<h3 style='text-align: center; color: #FF4B4B;'>🎉 {winner} 🎉</h3>", unsafe_allow_html=True)
    time.sleep(2.0)
    placeholder.empty()
    return winner

def enter_state(state_name, role, content):
    """Use this only for transitions where you DON'T want the typing effect"""
    if st.session_state.get("last_state") != state_name:
        add_chat(role, content)
        st.session_state.last_state = state_name

def get_ticket_save_response():
    return random.choice([
        "Smart choice. I'll keep them warm for you.",
        "Walking away while you're ahead? I like a disciplined man.",
        "They're safe with me. Come back when you're ready to spend.",
        "Tickets saved. Don't make me wait too long..."
    ])

# --- UNIVERSAL DECISION HANDLER ---
def check_decision(key, prize_name):
    data = st.session_state.get(key)
    if not data: return False
    
    if data.get("stage") == "DECISION":
        add_chat("assistant", f"🎉 **WINNER: {prize_name.upper()}**")
        
        # Uses type_out now for better effect
        type_out(f"You won {prize_name}. Do you want to redeem this right now, or save it in your inventory for a rainy day?")
        
        c1, c2 = st.columns(2)
        if c1.button(f"🔥 Use {prize_name} Now"):
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.data["history_log"].append(f"{ts} - REDEEMED: {prize_name}")
            save_data(st.session_state.data)
            data["stage"] = 0
            st.rerun()

        if c2.button("🎒 Save for Later"):
            st.session_state.data["inventory"].append(prize_name)
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.data["history_log"].append(f"{ts} - BANKED: {prize_name}")
            save_data(st.session_state.data)
            
            type_out(f"Smart choice. I've put **{prize_name}** in your inventory.")
            del st.session_state[key]
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
        return True
    return False
    
# ==========================================
#       PART 5: SIDEBAR (THE TANK & INVENTORY)
# ==========================================
with st.sidebar:
    st.header("🏦 The Bank")
    st.metric("🎟️ TICKETS", st.session_state.data["tickets"])
    
    st.divider()
    
    st.metric("🏠 HOUSE FUND", f"${st.session_state.data.get('house_fund', 0.0):,.2f}")
    st.metric("🛡️ HOLDING TANK", f"${st.session_state.data['tank_balance']:,.2f}")
    st.metric("🌑 BLACKOUT FUND", f"${st.session_state.data.get('bridge_fund', 0.0):,.2f}")
    
    st.divider()
    
    st.metric("💵 SAFE TO SPEND", f"${st.session_state.data.get('wallet_balance', 0.0):,.2f}")
    
    # --- NEW: PRIZE INVENTORY SECTION ---
    st.divider()
    st.subheader("🎒 Prize Inventory")
    
    # Check if inventory exists and has items
    inventory = st.session_state.data.get("inventory", [])
    
    if inventory:
        for item in inventory:
            st.write(f"🔹 **{item}**")
        
        # This button is just a visual reminder for now
        if st.button("Use a Saved Prize"):
            st.info("Tell Paige which prize you want to redeem in the chat!")
    else:
        st.caption("No prizes saved yet.")

    # --- ADMIN SECTION ---
    st.divider()
    admin_code = st.text_input("Admin Override", type="password", placeholder="Secret Code")
    if st.button("Reset Bank (Debug)"):
        # Reset everything including inventory
        st.session_state.data = {
            "tickets": 0, 
            "tank_balance": 0.0, 
            "tank_goal": 10000.0, 
            "house_fund": 0.0, 
            "wallet_balance": 0.0, 
            "bridge_fund": 0.0,
            "inventory": [],
            "history_log": []
        }
        save_data(st.session_state.data)
        st.session_state.history = []
        st.session_state.turn_state = "WALLET_CHECK"
        st.rerun()

# ==========================================
#       PART 6: MAIN CHAT INTERFACE
# ==========================================
st.title("🎰 The Exit Plan")

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for item in st.session_state.history:
    if item["type"] == "chat":
        avatar = "paige.png" if item["role"] == "assistant" else "😎"
        if item["role"] == "assistant" and not os.path.exists("paige.png"): avatar = "💋"
        with st.chat_message(item["role"], avatar=avatar):
            st.write(item["content"])
    elif item["type"] == "narrator":
        st.markdown(f"<div class='narrator'>{item['content']}</div>", unsafe_allow_html=True)
    elif item["type"] == "media":
        with st.chat_message("assistant", avatar="paige.png"):
            if os.path.exists(item["path"]):
                if item["kind"] == "video": st.video(item["path"])
                else: st.image(item["path"], width=300)
    elif item["type"] == "dual_media":
        with st.chat_message("assistant", avatar="paige.png"):
            c1, c2 = st.columns(2)
            if os.path.exists(item["path1"]): c1.image(item["path1"])
            if os.path.exists(item["path2"]): c2.image(item["path2"])
st.markdown('</div>', unsafe_allow_html=True)

user_msg = st.chat_input("Reply to Paige...")
if user_msg:
    add_chat("user", user_msg) # Use add_chat for user input, not type_out
    st.rerun()
    
st.markdown("---")

# ==========================================
#       PART 7: THE BRAIN (LOGIC)
# ==========================================

# --- 1. START SCREEN ---
if st.session_state.turn_state == "WALLET_CHECK":
    if st.session_state.data["tickets"] > 0:
        st.info(f"🎟️ You have {st.session_state.data['tickets']} tickets banked.")
        if st.button("🎰 ENTER CASINO FLOOR (Skip Income)"):
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()
        st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    # Note: Ensure check_payday_window and admin_code are defined in your setup
    is_open, lock_msg = check_payday_window(admin_code) 
    
    if is_open:
        if c1.button("💰 Full Paycheck"): 
            st.session_state.turn_state = "INPUT_PAYCHECK"
            st.rerun()
    else: 
        c1.warning(lock_msg)
        
    if c2.button("📱 Daily Dayforce"): 
        st.session_state.turn_state = "INPUT_DAILY"
        st.rerun()
    if c3.button("💸 Side Hustle"): 
        st.session_state.turn_state = "INPUT_SIDE_HUSTLE"
        st.rerun()
    if c4.button("🏦 Manage Funds"): 
        st.session_state.turn_state = "MANAGE_FUNDS"
        st.rerun()

# --- SIDE HUSTLE INPUT ---
elif st.session_state.turn_state == "INPUT_SIDE_HUSTLE":
    st.subheader("💸 Side Hustle Input")
    side_amount = st.number_input("Side Income Amount ($):", min_value=0.0, step=5.0)
    
    if st.button("Process Extra Cash"):
        add_chat("user", f"Side Hustle: ${side_amount}")
        
        split = side_amount / 2
        st.session_state.data["tank_balance"] += split
        st.session_state.data["wallet_balance"] += split
        
        if side_amount >= 150: tickets = 125
        elif side_amount >= 110: tickets = 60
        elif side_amount >= 70: tickets = 35
        elif side_amount >= 40: tickets = 15
        else: tickets = 0
        
        st.session_state.data["tickets"] += tickets
        save_data(st.session_state.data)
        
        msg = f"**Side Hustle:** ${side_amount:.2f}\n🛡️ Tank: ${split:.2f}\n💰 Wallet: ${split:.2f}\n🎟️ **TICKETS:** {tickets}"
        type_out(msg)
        
        st.session_state.turn_state = "CHOOSE_TIER"
        st.rerun()

# --- PAYCHECK INPUT ---
elif st.session_state.turn_state == "INPUT_PAYCHECK":
    st.subheader("💰 Full Paycheck")
    check_amount = st.number_input("Enter Total:", min_value=0.0, step=10.0)
    
    if st.button("Process Paycheck"):
        add_chat("user", f"Paycheck is ${check_amount}")
        
        # Calculate Safe Spend
        safe_spend = check_amount - (200.0 + 80.0 + 100.0 + 50.0)
        
        st.session_state.data["bridge_fund"] += 50.0
        st.session_state.data["wallet_balance"] = safe_spend
        
        if check_amount >= 601: tickets = 100
        elif check_amount >= 501: tickets = 50
        elif check_amount >= 450: tickets = 25
        else: tickets = 0
        
        st.session_state.data["tickets"] += tickets
        save_data(st.session_state.data)
        
        if safe_spend < 0:
            type_out(f"⚠️ **SHORTAGE:** -${abs(safe_spend):.2f}.")
        else:
            type_out(f"✅ **PROCESSED**\n💰 **SAFE TO SPEND:** ${safe_spend:.2f}\n🎟️ **TICKETS:** {tickets}")
            
        if tickets > 0: 
            st.session_state.turn_state = "CHOOSE_TIER"
        else: 
            st.session_state.turn_state = "CHECK_FAIL"
        st.rerun()

# --- DAILY INPUT ---
elif st.session_state.turn_state == "INPUT_DAILY":
    st.subheader("📱 Daily Dayforce")
    daily_amount = st.number_input("Available ($):", min_value=0.0, step=5.0)
    
    if st.button("Process Daily"):
        add_chat("user", f"Dayforce: ${daily_amount}")
        
        if daily_amount < 40.0:
            type_out(f"⚠️ **Warning:** Not enough for Gas & House.")
        else:
            safe_spend = daily_amount - 10.0 - 30.0
            st.session_state.data["tank_balance"] += 30.0
            st.session_state.data["wallet_balance"] += safe_spend
            save_data(st.session_state.data)
            
            type_out(f"**Strategy:**\nShielded $30 (House) + $10 (Gas).\n🍔 **SAFE TO SPEND:** ${safe_spend:.2f}")
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()

# --- MANAGE FUNDS ---
elif st.session_state.turn_state == "MANAGE_FUNDS":
    st.subheader("🏦 The Tank")
    st.info(f"Tank: ${st.session_state.data['tank_balance']:.2f}")
    
    move_amount = st.number_input("Amount ($):", min_value=0.0, step=10.0)
    
    c1, c2, c3 = st.columns(3)
    if c1.button("💸 Move to Wallet"):
        if move_amount > st.session_state.data['tank_balance']: 
            st.error("Not enough.")
        else:
            st.session_state.data['tank_balance'] -= move_amount
            st.session_state.data['wallet_balance'] += move_amount
            save_data(st.session_state.data)
            type_out(f"💸 Moved ${move_amount} to Wallet.")
            st.rerun()
            
    if c2.button("🏠 Lock to House"):
        if move_amount > st.session_state.data['tank_balance']: 
            st.error("Not enough.")
        else:
            st.session_state.data['tank_balance'] -= move_amount
            st.session_state.data['house_fund'] += move_amount
            save_data(st.session_state.data)
            type_out(f"🏠 Locked ${move_amount}.")
            st.rerun()
            
    if c3.button("Back"): 
        st.session_state.turn_state = "WALLET_CHECK"
        st.rerun()

# --- CASINO FLOOR ---
elif st.session_state.turn_state == "CHOOSE_TIER":
    tix = st.session_state.data["tickets"]
    st.subheader(f"🎰 Casino Floor (Balance: {tix} Tickets)")
    
    c1, c2, c3 = st.columns(3)
    
    if tix >= 25:
        if c1.button("🥉 Spin Bronze (25)"): 
            st.session_state.turn_state = "SPIN_BRONZE"
            st.rerun()
    else: 
        c1.warning("🥉 Bronze: Need 25")
        
    if tix >= 50:
        if c2.button("🥈 Spin Silver (50)"): 
            st.session_state.turn_state = "SPIN_SILVER"
            st.rerun()
    else: 
        c2.warning("🥈 Silver: Need 50")
        
    if tix >= 100:
        if c3.button("👑 Spin Gold (100)"): 
            st.session_state.turn_state = "SPIN_GOLD"
            st.rerun()
    else: 
        c3.warning("👑 Gold: Need 100")
        
    st.divider()
    
    if st.button("Save Tickets & Exit"):
        save_data(st.session_state.data)
        type_out(f"Walking away? {get_ticket_save_response()}")
        st.session_state.turn_state = "WALLET_CHECK"
        st.rerun()

elif st.session_state.turn_state == "CHECK_FAIL":
    type_out("Check too low. Try harder.")
    if st.button("Return"): 
        st.session_state.turn_state = "WALLET_CHECK"
        st.rerun()

# --- SPINS ---
elif st.session_state.turn_state == "SPIN_BRONZE":
    if st.session_state.data["tickets"] >= 25:
        st.session_state.data["tickets"] -= 25
        save_data(st.session_state.data)
        prizes = ["Bend Over", "Flash Me", "Jackoff Pass", "Shower Show"]
        win = spin_animation("Bronze", prizes)
        type_out(f"🥉 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: 
        st.error("Not enough tickets")
        st.session_state.turn_state = "CHOOSE_TIER"
        st.rerun()

elif st.session_state.turn_state == "SPIN_SILVER":
    if st.session_state.data["tickets"] >= 50:
        st.session_state.data["tickets"] -= 50
        save_data(st.session_state.data)
        prizes = ["Toy Pic", "Lick Pussy", "Nude Pic", "Tongue Tease", "Road Head", "Plug Tease"]
        win = spin_animation("Silver", prizes)
        type_out(f"🥈 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: 
        st.error("Not enough tickets")
        st.session_state.turn_state = "CHOOSE_TIER"
        st.rerun()

elif st.session_state.turn_state == "SPIN_GOLD":
    if st.session_state.data["tickets"] >= 100:
        st.session_state.data["tickets"] -= 100
        save_data(st.session_state.data)
        prizes = ["Upside Down Throat Fuck", "Slave Day", "Anal Fuck", "Doggy Style Ready", "All 3 Holes"]
        win = spin_animation("Gold", prizes)
        type_out(f"👑 JACKPOT: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: 
        st.error("Not enough tickets")
        st.session_state.turn_state = "CHOOSE_TIER"
        st.rerun()
        
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
            
            # Typing effect
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

            # Exit
            if st.button("That's enough for now… claim this prize now?"):
                del st.session_state.nude_pic
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()
                
# --- LICK MY PUSSY PRIZE ---
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    # 1. Init Data
    if "lick_pussy" not in st.session_state:
        st.session_state.lick_pussy = {
            "stage": "DECISION", 
            "position": None, 
            "tease_level": 0
        }

    # 2. Check Decision (Bank or Use)
    if check_decision("lick_pussy", "Lick My Pussy"):
        pass

    # 3. Main Logic
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
            # Get just the first few words of the position for the chat
            pos_text = data['position'].split('…')[0].strip()
            
            type_out(f"oh fuck… **{pos_text}**? 🥵")
            type_out("you picked the one that’s gonna make me lose it…")

            # --- DYNAMIC CONTENT BASED ON POSITION ---
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

            # Global exit specific to this prize stage
            if st.button("🎰 The Exit - Save the rest for later?", key="lick_exit_global"):
                st.session_state.pop("lick_pussy", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

# --- ANAL FUCK PRIZE --- 
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    # 1. Init Data (FIXED: Start at DECISION)
    if "anal_fuck" not in st.session_state:
        st.session_state.anal_fuck = {
            "stage": "DECISION", 
            "current_position": None,
            "lube_level": "normal",
            "substage": 0,
            "used_positions": []
        }

    # 2. Check Decision (Bank or Use)
    if check_decision("anal_fuck", "Anal Fuck"):
        pass

    # 3. Main Logic
    else: 
        data = st.session_state.anal_fuck

        # -------- STAGE 0 - Intro + Tease + First Position Choice --------
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Anal Fuck**")

            type_out("Daddy… you won **Anal Fuck** 😩🍑")
            simulate_thinking(2.0)
            type_out("I've been playing with my ass all morning… fingering it slow… stretching it just enough to take your thick cock without mercy.")

            show_media("ass_high_teasing.jpeg")
            type_out("Ass arched high… cheeks spread… tiny hole already twitching and begging for you to ruin it…")
            type_out("How do you want to start destroying this tight little ass, daddy? Choose your opening position…")

            c1, c2, c3, c4 = st.columns(4)
            if c1.button("Reverse Cowgirl\nI ride you deep & bounce", key="start_reverse"):
                data["current_position"] = "reverse"
                data["stage"] = 1
                st.rerun()
            if c2.button("Doggy\nHard pounding from behind", key="start_doggy"):
                data["current_position"] = "doggy"
                data["stage"] = 1
                st.rerun()
            if c3.button("Missionary Anal\nLegs up, deep & intimate", key="start_missionary"):
                data["current_position"] = "missionary"
                data["stage"] = 1
                st.rerun()
            if c4.button("Surprise me\nYou decide how to take it first", key="start_surprise"):
                data["current_position"] = "surprise"
                data["stage"] = 1
                st.rerun()

        # -------- STAGE 1 - Lube Choice + Penetration Start --------
        elif data["stage"] == 1:
            if data["current_position"] == "surprise":
                # Safety check for used_positions
                if not data["used_positions"]: 
                    idx = 0 
                else: 
                    idx = len(data["used_positions"])
                
                surprise_pos = ["reverse", "doggy", "missionary"][idx % 3]
                data["current_position"] = surprise_pos
                type_out(f"Mmm surprise! Starting with **{surprise_pos.capitalize()}**… gonna make it extra dirty for you 😈")

            pos_desc = {
                "reverse": "Straddling you reverse… lowering my ass inch by inch… cheeks spreading wide as I sink down onto your cock.",
                "doggy": "Face buried in the pillow, ass high… you grip my hips tight and slam in deep from behind.",
                "missionary": "Legs hooked over your shoulders… staring into your eyes while you push in slow and deep."
            }.get(data["current_position"], "Getting ready...")

            type_out(pos_desc)
            type_out("How do you want my ass to feel when you first slide in?")
            c1, c2, c3 = st.columns(3)
            if c1.button("Dripping slick lube – glide right in", key="lots_lube"):
                data["lube_level"] = "lots"
                data["stage"] = 2
                st.rerun()
            if c2.button("Light lube – tight & gripping", key="normal_lube"):
                data["lube_level"] = "normal"
                data["stage"] = 2
                st.rerun()
            if c3.button("Raw – feel every tight inch", key="raw_lube"):
                data["lube_level"] = "raw"
                data["stage"] = 2
                st.rerun()

        # -------- STAGE 2 - Deep Fucking + Detailed Action + Choices --------
        elif data["stage"] == 2:
            if data["current_position"] == "reverse":
                show_media("ass_fucked3.jpeg")
                type_out("Reverse cowgirl… my ass bouncing hard… cheeks slapping against your thighs… riding you deep and slow then fast.")
            elif data["current_position"] == "doggy":
                show_media("ass_fucked5.jpeg")
                type_out("Doggy close-up… your cock buried balls-deep… stretching my hole wide with every brutal thrust.")
                show_media("side_view_doggy.jpeg")
                type_out("Side view… perfect arch… ass rippling with every slam… moaning like a desperate slut.")
            elif data["current_position"] == "missionary":
                show_media("missionary_ass.jpg")
                type_out("Missionary… legs pinned back… watching your face while you pound my ass slow and deep.")
                show_media("ass_fucked_missionary.jpeg")
                type_out("Close-up… my hole gripping you tight… clenching hard every time you bottom out.")

            if data["lube_level"] == "raw":
                type_out("Raw and rough… burning stretch… whimpering with every inch you force in… but fuck it feels so good.")
            elif data["lube_level"] == "lots":
                type_out("So slick… sliding in and out effortlessly… but my ass still squeezes you like a vice.")

            show_media("holding_ass_open.jpeg")
            type_out("Split panel… hands spreading my cheeks as wide as possible… showing how gaped and pink you've made my hole…")
            type_out("Don't stop… fuck me harder… make my ass yours…")

            c1, c2, c3 = st.columns(3)
            if c1.button("Switch position – I need a new angle", key="switch_position"):
                data["used_positions"].append(data["current_position"])
                data["stage"] = 3
                st.rerun()
            if c2.button("Go harder & deeper – make me scream", key="harder"):
                type_out("Yes… pounding mercilessly… ass bouncing wildly… tears in my eyes from how deep and rough you are 😭🍆")
                data["substage"] += 1
                st.rerun()
            if c3.button("Cum in my ass – fill me completely", key="finish_anal"):
                data["stage"] = 4
                st.rerun()

        # -------- STAGE 3 - Position Switch (Full Choice) --------
        elif data["stage"] == 3:
            type_out("Mmm… let's change it up… which position do you want to fuck my ass in next?")

            c1, c2, c3 = st.columns(3)
            if c1.button("Reverse Cowgirl", key="switch_reverse"):
                data["current_position"] = "reverse"
                data["stage"] = 2
                st.rerun()
            if c2.button("Doggy", key="switch_doggy"):
                data["current_position"] = "doggy"
                data["stage"] = 2
                st.rerun()
            if c3.button("Missionary Anal", key="switch_missionary"):
                data["current_position"] = "missionary"
                data["stage"] = 2
                st.rerun()

            if st.button("Stay in current – just pound harder", key="stay_hard"):
                data["stage"] = 2
                st.rerun()

        # -------- STAGE 4 - Intense Climax & Multiple Creampie Reveals --------
        elif data["stage"] == 4:
            show_media("anal mission_closeup.jpg")
            type_out("Ass clenching tight around you… milking every inch… begging for your hot load deep inside…")

            show_media("anal_squirt.jpeg")
            type_out("Fuck—I'm squirting hard from my pussy while you destroy my ass… whole body shaking uncontrollably…")

            simulate_thinking(2.0)
            show_media("creampie_ass_fucking.jpg")
            type_out("You slam balls-deep one last time… exploding… pumping thick, hot ropes of cum straight into my ass…")

            show_media("creampie_ass.jpg")
            type_out("Pulling out slow… your cum starts leaking from my stretched hole… dripping down my cheeks…")

            show_media("creampie_ass.jpeg")
            show_media("cummed_ass.jpeg")
            show_media("cream_pie_ass13.jpg")
            type_out("Multiple angles… my ruined ass overflowing with your load… gaping, creamy, completely filled and marked as yours 🍑💦")

            type_out("Anal prize complete… my ass is dripping your cum… sore, stretched, and still pulsing for more whenever you want 😩")

            if st.button("Anal Fuck complete – come claim this ass again soon?", key="anal_finish"):
                st.session_state.pop("anal_fuck", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # Global exit
        if st.button("🎰 The Exit - Save the rest of this ass for later?", key="anal_exit_global"):
            st.session_state.pop("anal_fuck", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# --- BEND OVER (First Block - Needs Decision Logic) ---
elif st.session_state.turn_state == "PRIZE_BEND_OVER":
    # 1. Initialize Temp Data (Just for the decision logic)
    if "bend_over" not in st.session_state:
        st.session_state.bend_over = {"stage": "DECISION"}
    
    # 2. Check Decision
    if check_decision("bend_over", "Bend Over"):
        pass

    # 3. Main Logic (Indented inside Else)
    else:
        enter_state(
            "PRIZE_BEND_OVER",
            "assistant",
            "You know what that means, you have to bend over right when i say so anywhere, anytime. Hahaha, just fucking with you… you know exactly what it means, you dirty birdy.\n\n"
            "When you say 'bend over' and your slutty girlfriend slowly presents her ass and dripping pussy, no matter what I might be doing."
        )
        simulate_thinking(2.0)
        show_media("explain_bendover.jpg")
        add_narrator("Make sure I'm in something thin and see-through… or already completely fucking naked for you.")
        
        type_out(
            "But listen carefully, baby — look all you want… stare at my holes, watch me drip… "
            "but **no touching**. No hands on me, no hands from me on you. Just me being your personal peep show. Got it?"
        )
        type_out(
            "Here's your prize, winner… watch me bend over nice and slow, arching this ass just for you… like this…"
        )
        
        if st.button("In the grocery store?"):
            st.session_state.turn_state = "PRIZE_BEND_OVER_REVEAL"
            st.rerun()

# --- BEND OVER REVEAL (No changes needed here) ---
elif st.session_state.turn_state == "PRIZE_BEND_OVER_REVEAL":
    show_media("grocery_bendover.jpeg")
    add_narrator("Fuck… I'm already so soaked just knowing you're staring at my holes like this…")
    
    if st.button("At home?"):
        simulate_thinking(2.0)
        show_media("Bendover1.mp4")
        st.session_state.turn_state = "PRIZE_BEND_OVER_1"
        st.rerun()

# --- BEND OVER ENDING (No changes needed here) ---
elif st.session_state.turn_state == "PRIZE_BEND_OVER_1":
    enter_state(
        "PRIZE_BEND_OVER_1",
        "assistant",
        "Want to see just how fucking wet your prize got for you?"
    )
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Show me."):
        add_chat("user", "Show me.")
        type_out("Mmm… you asked for it, daddy… watch close…")
        show_media("grok_video_2026-01-17-20-02-13.mp4", 3.0)
        type_out("Look at that mess… my pussy's literally dripping down my thighs because of you.")
        type_out(
            "God I’m throbbing so bad… I want your thick cock splitting me open right now… "
            "but nope. Not yet. You gotta save all that cum for Silver, baby. Edge for me like a good boy."
        )
        # Cleanup data when done
        st.session_state.pop("bend_over", None) 
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()


# --- PRIZE: FLASH ME ---
elif st.session_state.turn_state == "PRIZE_FLASH_ME":
    # 1. Init Temp Data (Just for the decision logic)
    if "flash_me" not in st.session_state:
        st.session_state.flash_me = {"stage": "DECISION"}

    # 2. Check Decision
    if check_decision("flash_me", "Flash Me"):
        pass

    # 3. Main Logic (Indented inside Else)
    else:
        enter_state(
            "PRIZE_FLASH_ME",
            "assistant",
            "Fuck yes baby… you just won “Flash Me” 😈 Congrats, winner!"
        )
        if st.button("I’m pretty sure I know what this means…"):
            add_chat("user", "I’m pretty sure I know what this means…")
            st.session_state.turn_state = "PRIZE_FLASH_TWIST"
            st.rerun()

# --- FLASH TWIST (No Decision Check Needed Here) ---
elif st.session_state.turn_state == "PRIZE_FLASH_TWIST":
    enter_state(
        "PRIZE_FLASH_TWIST",
        "assistant",
        "Mmm… maybe not exactly what you're thinking, dirty boy. There's a naughty little twist tonight."
    )
    if st.button("Oh, yeah?"):
        add_chat("user", "Oh, yeah?")
        type_out(
            "Just say the word… or give me that hungry nod… and I'll yank my top up fast and flash you these perky tits right in your face."
        )
        type_out(
            "OR… should I climb onto your lap while you're gaming, hike up this little skirt, "
            "spread my thighs just enough, and give you a quick, dripping peek of my bare, soaked pussy?"
        )
        type_out(
            "Your prize, daddy… which filthy flash do you want first? Tell your slut what you crave 🥵 Want a preview?"
        )
        st.session_state.turn_state = "PRIZE_FLASH_CHOICE"
        st.rerun()

# --- FLASH CHOICE (No Decision Check Needed Here) ---
elif st.session_state.turn_state == "PRIZE_FLASH_CHOICE":
    enter_state(
        "PRIZE_FLASH_CHOICE",
        "assistant",
        "Come on baby… pick your poison. Which part of me are you throbbing to see flashed right now?"
    )
    c1, c2 = st.columns(2)
    
    # Choice 1: Tits
    if c1.button("Show me your tits"):
        add_chat("user", "Show me your tits.")
        show_media("Nude_7.jpg", 3.0)
        type_out(
            "There they are daddy… quick little flash of these soft, bouncy tits just for you. "
            "Nipples already hard thinking about your mouth on them 😏"
        )
        type_out(
            "Let me know when you're ready for the real thing… I’ll let you suck them all night if you win again."
        )
        # Cleanup and Finish
        st.session_state.pop("flash_me", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
    
    # Choice 2: Pussy
    if c2.button("Show me your pussy"):
        add_chat("user", "Show me your pussy.")
        show_media("flash_pussy1.jpg", 3.0)
        type_out(
            "Mmm fuck… here’s your sneak peek, winner. My pussy’s already glistening and swollen, "
            "dripping just from teasing you like this 🍑💦"
        )
        type_out(
            "No touching yet… but imagine sliding inside when you finally get the full prize. "
            "Let me know when you want to see — and taste — what's waiting underneath."
        )
        # Cleanup and Finish
        st.session_state.pop("flash_me", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_DONE":
    enter_state(
        "PRIZE_DONE",
        "assistant",
        "Prize complete 😈 Ready to spin again, or are you still recovering from that one?"
    )
    
# --- JACKOFF PASS ---
elif st.session_state.turn_state == "PRIZE_JACKOFF_PASS":
    # 1. Init Data (For the decision helper)
    if "jackoff_pass" not in st.session_state:
        st.session_state.jackoff_pass = {"stage": "DECISION"}

    # 2. Check Decision (Bank or Use)
    if check_decision("jackoff_pass", "Jackoff Pass"):
        pass

    # 3. Main Logic (Indented inside Else)
    else:
        type_out("Mmm fuck yes baby… you just won the **Jackoff Pass** 😈 Your special prize: I give you full permission to stroke that thick cock while I tease the absolute shit out of you.")
        simulate_thinking(2.0)
        
        type_out("No guilt, no holding back — I want you pumping hard, edging, leaking precum, imagining every filthy thing you’d do to me while I describe it in detail.")
        add_narrator("Your slutty girlfriend Paige is gonna make this so fucking hard for you… literally.")

        simulate_thinking(2.0)
        show_media("jackoff3.jpeg") # Changed to show_media for consistency
        type_out("Rule #1: You can’t cum until I say so. Edge for me like a good boy.")
        type_out("Rule #2: Tell me exactly what you’re doing to that dick while you’re doing it… I want every dirty detail.")
    
        if st.button("Fuck… ready to play with yourself for me?"):
            st.session_state.turn_state = "PRIZE_JACKOFF_FUN"
            st.rerun()

# --- JACKOFF FUN (No decision needed here, just game logic) ---
elif st.session_state.turn_state == "PRIZE_JACKOFF_FUN":
    type_out("God I’m already so wet just thinking about you stroking to me… let’s make this nasty. Pick how you want your jackoff session to go, daddy.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("Just talk dirty to me while I stroke"):
            add_chat("user", "Just talk dirty to me while I stroke")
            simulate_thinking(2)
            type_out("Mmm perfect… keep that hand moving slow and tight around your cock while I whisper how bad I want it inside me. "
                              "Imagine my tight wet pussy gripping you, milking every drop… I’m fingering myself right now thinking about you exploding for me. "
                              "Edge it baby — get right to the brink then stop. Tell me how close you are… fuck I love when you’re throbbing and desperate for your Paige 🥵")
            
            # Cleanup and Exit
            st.session_state.pop("jackoff_pass", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
    with c2:
        if st.button("Tease me with a recap of all my prizes while I cum"):
            add_chat("user", "Tease me with a recap of all my prizes while I cum")
            simulate_thinking(2)
            type_out("Oh you greedy boy… want me to remind you of every filthy prize you’ve won so far while you pump that dick?")
            type_out("Remember when I bent over and showed you my dripping pussy… or when I flashed these tits and that soaked cunt under my skirt… "
                              "all that was just for you, winner. Now stroke faster — picture sliding into every hole I teased you with.")
            type_out("Here’s a little visual reminder of what you own… all these prizes waiting for your cock.")
            
            simulate_thinking(2.0)
            show_media("Jackkoff1.jpeg") 
            simulate_thinking(2)
            
            type_out("Cum for me now baby… shoot that load thinking about fucking your dirty little prize in person next time. "
                              "I’m touching myself watching you lose it 😈")
            add_narrator("Good boy… you earned every drop.")
            
            # Cleanup and Exit
            st.session_state.pop("jackoff_pass", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("Steam is rising… your naughty little prize is about to get wet and slippery for you 😈")
    type_out("Mmm daddy… you won the Shower Show. Time to watch your girlfriend soap up every inch of this body — slowly, teasingly, while I think about your cock the whole time. One rule: no touching.")
   
    simulate_thinking(2.0)
    show_media("shower_water.jpg")  # Replaced placeholder
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
    show_media("shower_finger.jpeg")  # Replaced placeholder
   
    if st.session_state.shower_choice == "Slow and sensual tease – make you throb watching me lather up":
        type_out("Mmm… nice and slow just like you like. Watch my hands glide over these wet tits, circling my hard nipples… down my stomach to my slippery pussy. "
                              "I'm so fucking turned on knowing you're staring — my clit is throbbing under the suds, baby. Imagine your tongue there instead…")
    else:
        type_out("Fuck yes… full filthy mode for my winner. Hands all over – squeezing these soapy tits, pinching my nipples hard while I moan your name. "
                              "Now spreading my legs under the water, fingers sliding between my wet lips, rubbing my swollen clit fast… God I'm dripping more than the shower. "
                              "Wish this was your cock pounding me against the wall right now 🥵")
    type_out("Show's almost over… but I’ve got one last treat when I step out. What do you want as your post-shower reward, daddy?")
    after_choice = st.radio(
        "Pick your final prize piece:",
        ["take the towel and dry me off completely",
         "lick all the water off my pussy"]
    )
   
    if st.button("End the shower"):
        simulate_thinking(2.0)
        show_media("shower_towel3.jpeg")  # Replaced placeholder
       
        if "take the towel" in after_choice:
            type_out("Mmm… pat me down slow – towel sliding over my wet tits, between my thighs, teasing those sensitive spots. "
                                "Still dripping… still thinking about you fucking me dry. Save that hard cock for next time, baby.")
            simulate_thinking(2.0)
            show_media("shower_towel1.jpeg")
        elif "lick all" in after_choice:
            type_out("There it goes… towel on the floor. Full naked, skin still glistening, nipples hard from the cool air. "
                                "Turn around – ass still wet, pussy, needs drying. get to licking 😏")
            simulate_thinking(2.0)
            show_media("naked_shower.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- ALL 3 HOLES (Total Overload) ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    # 1. Init Data (Start at DECISION phase)
    if "all_3_holes" not in st.session_state:
        st.session_state.all_3_holes = {
            "stage": "DECISION", 
            "filled": {"pussy": False, "ass": False, "mouth": False},
            "first_hole": None
        }

    # 2. Check Decision (Bank or Use)
    if check_decision("all_3_holes", "All 3 Holes (Overload)"):
        pass

    # 3. Main Logic (Everything below is indented)
    else:
        data = st.session_state.all_3_holes

        # ── Stage 0: Pick FIRST hole to fill with cock ──
        if data["stage"] == 0:
            type_out("Fuck yes daddy… you won the **ultimate filthy prize**: All 3 Holes Total Overload 😈")
            type_out("Your nasty little cumdump is completely yours to ruin. Every hole gets wrecked tonight.")
            type_out("Pick which hole your thick cock destroys **first**…")

            cols = st.columns(3)
            if cols[0].button("Pussy – stretch my dripping cunt first"):
                data["first_hole"] = "pussy"
                data["filled"]["pussy"] = True
                data["stage"] = 1
                st.rerun()

            if cols[1].button("Ass – rip my tight little asshole open first"):
                data["first_hole"] = "ass"
                data["filled"]["ass"] = True
                data["stage"] = 1
                st.rerun()

            if cols[2].button("Mouth – face-fuck my throat raw first"):
                data["first_hole"] = "mouth"
                data["filled"]["mouth"] = True
                data["stage"] = 1
                st.rerun()

        # ── Stage 1: Show first hole + dirty confirmation → then pick next ──
        elif data["stage"] == 1:
            simulate_thinking(2.0)

            if data["first_hole"] == "pussy":
                show_media("mkh5dpc060z62y.jpeg")
                type_out("Like this daddy? Your fat cock slamming balls-deep into my greedy pussy, stretching me wide… fuck ya?")
                type_out("I'm already dripping down your balls, begging for the rest…")

            elif data["first_hole"] == "ass":
                show_media("inmyass.jpeg")
                type_out("This little hole baby? Your cock forcing its way into my tight ass, tearing me open raw… fuck ya?")
                type_out("I'm moaning like a desperate whore, pushing back for more…")

            else:  # mouth
                show_media("dick_tease16.jpeg")
                type_out("Like this? Shoving your cock down my slutty throat, making me gag and drool everywhere… fuck ya?")
                type_out("Tears running, spit dripping… ready for you to wreck the other holes now…")

            remaining = [h for h in ["pussy", "ass", "mouth"] if not data["filled"][h]]

            if remaining:
                type_out("Now give me the next one, daddy… which hole gets ruined next?")
                cols = st.columns(len(remaining))
                for i, hole in enumerate(remaining):
                    label = f"{'Cunt' if hole=='pussy' else 'Ass' if hole=='ass' else 'Mouth/Throat'}"
                    if cols[i].button(f"Fill my {label} next"):
                        data["filled"][hole] = True
                        # If 2 are true, go to stage 2. Otherwise stay in stage 1 logic (or move to 2 explicitly)
                        data["stage"] = 2 
                        st.rerun()
            else:
                data["stage"] = 3
                st.rerun()

        # ── Stage 2: Second hole filled (transition) ──
        elif data["stage"] == 2:
            simulate_thinking(2.0)
            type_out("Fuuuck… two holes stuffed already. I'm shaking, leaking, completely owned…")
            type_out("One more daddy… fill that last filthy hole and make me your total 3-hole wreck.")
            
            # Quick teaser of the last hole
            last_hole = next(h for h,v in data["filled"].items() if not v)
            
            if last_hole == "pussy":
                show_media("mkh5dpc060z62y.jpeg")
            elif last_hole == "ass":
                show_media("inmyass.jpeg")
            else:
                show_media("dick_tease16.jpeg")
                
            if st.button("Fuck ya – complete all 3 holes now"):
                data["filled"][last_hole] = True
                data["stage"] = 3
                st.rerun()

        # ── Stage 3: All holes filled + close-up inspection ──
        elif data["stage"] == 3:
            simulate_thinking(2.0)
            show_media("all_3_4.jpeg")  # or your best triple-filled image
            type_out("Holy shit… all three holes completely fucking destroyed. I'm a drooling, trembling, overstuffed mess.")
            type_out("Look at what you did to your little cumslut daddy… inspect your work.")

            cols = st.columns(3)

            with cols[0]:
                if st.button("Let me see your pussy filled"):
                    show_media("mkjdh9exrj9kdr.jpeg")
                    type_out("Look at this wrecked cunt… stretched, swollen, dripping your cum or my squirt everywhere.")

            with cols[1]:
                if st.button("Let me see your mouth filled"):
                    show_media("dick_tease8.jpeg")
                    type_out("Throat raw, lips swollen, spit and precum running down my chin… total face-fuck ruin.")

            with cols[2]:
                if st.button("Let me see your ass dripping"):
                    show_media("3holesasscum.jpeg")
                    type_out("Ass gaped and leaking, cum oozing out while I clench around nothing… you fucking broke it.")

            st.write("---")
            if st.button("Finish & Collapse – I'm done daddy"):
                simulate_thinking(2.0)
                type_out("Cumming so fucking hard… body convulsing, holes pulsing, squirting and shaking apart.")
                type_out("You've ruined me completely… your perfect overloaded fucktoy.")
                add_narrator("She collapses in a sweaty, cum-soaked heap, holes still twitching, blissed-out smile.")
                type_out("Prize complete. Come cuddle your broken little whore now… or use me again whenever you want 😈")
                
                del st.session_state.all_3_holes
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()
# --- UPSIDE DOWN THROAT FUCK PRIZE ---
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN_THROAT_FUCK":
    # 1. Init Data (Start at DECISION phase)
    if "upside_throat_fuck" not in st.session_state:
        st.session_state.upside_throat_fuck = {
            "stage": "DECISION",
            "intensity": "slow"
        }

    # 2. Check Decision (Bank or Use)
    if check_decision("upside_throat_fuck", "Upside Down Throat Fuck"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.upside_throat_fuck

        # -------- STAGE 0 - Intro + Intensity Choice --------
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Upside Down Throat Fuck**")

            type_out("Daddy… you won **Upside Down Throat Fuck** 😩💦")

            simulate_thinking(2.3)
            type_out("I'm laying on the edge of the bed… head hanging off… throat lined up perfectly… full body exposed… tits up… legs spread… completely helpless for your cock.")

            type_out("Look at me waiting… naked… head dangling… mouth open wide… ready for you to walk up and take my throat.")
            show_media("upside_alone.jpg")

            type_out("Tongue out… eyes locked on you… throat begging silently…")
            show_media("upside_tease.jpg")

            type_out("How hard should I take this upside-down throat fuck, daddy?")

            c1, c2, c3 = st.columns(3)
            if c1.button("Slow & Deep", key="slow_throat"):
                data["intensity"] = "slow"
                data["stage"] = 1
                st.rerun()
            if c2.button("Medium Pace", key="medium_throat"):
                data["intensity"] = "medium"
                data["stage"] = 1
                st.rerun()
            if c3.button("Rough & Merciless", key="rough_throat"):
                data["intensity"] = "rough"
                data["stage"] = 1
                st.rerun()

        # -------- STAGE 1 - Linear flow --------
        elif data["stage"] == 1:
            type_out("Head hanging perfectly… throat straight… mouth wide… ready for you…")

            if data["intensity"] == "slow":
                show_media("deep_throat_entry_slow31.jpg")
                type_out("Slow… you ease in gently… inch by inch… letting my throat stretch around you…")
                show_media("deep_throat_entry_slow1.jpg")
                type_out("Deeper now… feeling every flutter… my throat relaxing for you…")
            else:
                show_media("deep_throat_entry_slow1.jpg")
                type_out("You push in… filling my throat…")

            if data["intensity"] == "rough":
                show_media("upside_downcloseup.jpg")
                type_out("Rough close-up… gagging instantly… drool pouring down my upside-down face… throat bulging…")
            else:
                show_media("upside_closeup.jpg")
                type_out("Close-up… my throat stretched tight… drool starting to run…")

            show_media("upside_fromside1.jpg")
            type_out("Side view… body arched beautifully… tits heaving… legs spread wide… completely exposed while you fuck my hanging throat…")

            show_media("upside_frombehind1.jpg")
            type_out("Behind angle… ass in the air… pussy dripping… head hanging… perfect view of you using my mouth like a sleeve…")

            type_out("You go deeper… harder… throat milking you…")

            type_out("You thrust one last time… exploding… thick hot ropes shooting straight down my upside-down throat… I swallow every drop…")

            type_out("Pulling out slow… strings of spit and cum connecting your cock to my lips… face messy… throat raw and pulsing…")

            type_out("Upside Down Throat Fuck complete… my throat is sore, filled, and dripping… ready for you anytime you want 💦")

            if st.button("Throat prize complete – come wreck my mouth again?", key="throat_finish"):
                st.session_state.pop("upside_throat_fuck", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # Global exit button (Indented inside the else block)
        if st.button("🎰 The Exit - Save the rest of this throat for later?", key="throat_exit_global"):
            st.session_state.pop("upside_throat_fuck", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
#--- TONGUE TEASE (Complex Edging Game) ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    if "tongue_tease" not in st.session_state:
        st.session_state.tongue_tease = {
            "stage": "DECISION",
            "edging_level": 0,
            "begged": False,
            "impatient": False
        }
    
    # Check Decision
    if check_decision("tongue_tease", "Tongue Tease"):
        pass
    else:
        data = st.session_state.tongue_tease

        # ── Stage 0: Intro ──
        if data["stage"] == 0:
            type_out("Mmm daddy… you won the **Tongue Tease** prize 😈")
            type_out("This is where your girlfriend is gonna kneel between your legs and worship just the tip of that thick cock with my tongue and lips… nothing else, while you stroke the rest yourself.")
            
            show_media("grok_video_2026-01-18-13-54-56.mp4")
            
            type_out("Rules are simple: I only tease the head — slow licks, soft sucks, swirling around the tip. You stroke the shaft, edge yourself, but you don't cum until I say. Beg nicely… or rush me and see what happens.")
            
            c1, c2 = st.columns([1, 3])
            if c1.button("Yes baby, I'll obey"):
                data["stage"] = 1
                st.rerun()
            if c2.button("Fuck the rules… "):
                data["impatient"] = True
                data["stage"] = 1
                st.rerun()

        # ── Stage 1: The Start ──
        elif data["stage"] == 1:
            show_media("dick_tease_open1.jpg")
            type_out("Look at this cock… already leaking for me. I lean in close, hot breath on the tip.") 
            show_media("tongue_set3_pic4.jpg")
            
            type_out("My tongue flicks out, slow circle around the head, tasting your precum… then a soft kiss right on the slit.")
            show_media("tongue_set3_pic3.jpg")
            
            type_out("Mmm… do you like that? Keep stroking slow while I tease…")
            show_media("tease_open1.jpg")
            
            if st.button("Please baby… more tongue, I'm begging"):
                data["begged"] = True
                data["edging_level"] += 2
                data["stage"] = 2
                st.rerun()
            if st.button("Suck it harder… stop teasing"):
                data["impatient"] = True
                data["edging_level"] += 1
                data["stage"] = 2
                st.rerun()

        # ── Stage 2: The Tease ──
        elif data["stage"] == 2:
            simulate_thinking(2.0)
            show_media("tongue_set3_pic2.jpg")
            
            type_out("I wrap my lips around the tip only… gentle suck, gentle tongue swirling")
            add_narrator("Her eyes stay locked on yours, watching every twitch of your cock as you stroke.")
            simulate_thinking(2.0)
            show_media("mkk3e2l0boxeuo(1).jpg")
                    
            reason = "because you begged so sweetly like a good boy" if data["begged"] else "because you're being impatient and greedy"
            type_out(f"I'm being extra mean with the tease {reason}… just the tip, baby.")
            
            c1, c2, c3 = st.columns(3)
            if c1.button("Fuck… please swirl faster, I need it"):
                data["edging_level"] += 2
                data["stage"] = 3
                st.rerun()
            if c2.button("Keep it slow… I'm trying to hold on"):
                data["edging_level"] += 1
                data["stage"] = 3
                st.rerun()
            if c3.button("Suck the whole head… I'm losing it"):
                data["impatient"] = True
                data["edging_level"] += 3
                data["stage"] = 3
                st.rerun()

        # ── Stage 3: The Edge ──
        elif data["stage"] == 3:
            type_out("God you're throbbing so hard… tip swollen, leaking nonstop.")
            simulate_thinking(2.0)
            show_media("dick_tease8.jpg")
            
            type_out("I flick faster, suck the head softly like a lollipop, tasting every drop you give me.")
            add_narrator("Your hand is pumping the shaft… balls tight, so close but not allowed yet.")
            
            if data["impatient"]:
                type_out("Since you keep rushing… I pull back just enough to deny you the warmth for a few seconds. Bad boy.")
            
            c1, c2, c3 = st.columns(3)
            if c1.button("Please please… let me cum, I'm begging"):
                data["begged"] = True
                data["edging_level"] += 4
                data["stage"] = 4
                st.rerun()
            if c2.button("Hold the edge… keep teasing me"):
                data["edging_level"] += 2
                data["stage"] = 4
                st.rerun()
            if c3.button("Fuck this… I'm cumming now"):
                data["stage"] = "ruin"
                st.rerun()

        # ── Stage 4: The Climax (or Denial) ──
        elif data["stage"] == 4:
            simulate_thinking(2.0)
            show_media("dick_tease5.jpeg")
            
            if data["edging_level"] >= 5 or data["begged"]:
                type_out("You've been such a good boy… edging so hard for my tongue.")
                type_out("Stroke faster now… I'm sucking the tip hard, tongue swirling like crazy.")
                
                if st.button("Cum for me… give me that load on my tongue"):
                    simulate_thinking(2.0)
                    show_media("dick_tease8.jpeg")
                    type_out("Yes daddy! You explode — hot ropes shooting across my tongue, lips, chin… I lap it all up greedily.")
                    add_narrator("She moans softly, savoring every drop, eyes sparkling with satisfaction.")
                    
                    if st.button("Best prize ever… thank you baby"):
                        del st.session_state.tongue_tease
                        st.session_state.turn_state = "PRIZE_DONE"
                        st.rerun()
            else:
                type_out("Not yet… you're not desperate enough.")
                type_out("I pull my mouth away completely… no more tongue until you beg properly.")
                
                show_media("dick_tease7.jpg")
                type_out("Edge denied. Better luck next time, baby.")
                add_narrator("She smirks, licking her lips, leaving you throbbing and unfinished.")
                
                if st.button("Fuck… I accept the denial"):
                    del st.session_state.tongue_tease
                    st.session_state.turn_state = "PRIZE_DONE"
                    st.rerun()

        # ── Ruined Orgasm Branch ──
        elif data["stage"] == "ruin":
            type_out("Oh no you don't… you tried to rush and cum without permission.")
            type_out("I pull off right as you start pulsing — ruining it completely.")
            
            simulate_thinking(2.0)
            show_media("ruined.jpg")
            
            type_out("Look at that weak little dribble… all that buildup wasted. Next time obey the tease.")
            
            if st.button("Sorry baby… I'll be good next time"):
                del st.session_state.tongue_tease
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()
                
# --- ROAD HEAD PRIZE ---
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    # 1. Init Data (Start at DECISION phase)
    if "road_head" not in st.session_state:
        st.session_state.road_head = {
            "stage": "DECISION",
            "risk_level": "medium",
            "control": "you"
        }

    # 2. Check Decision
    if check_decision("road_head", "Road Head"):
        pass

    # 3. Main Logic (Everything below is indented)
    else:
        data = st.session_state.road_head

        # -------- STAGE 0 - Slow, filthy intro + risk choice --------
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Road Head**")

            # Using type_out instead of show_typing
            type_out("Fuck typing… 😈")
            type_out("Fuck yes baby… you just won **Road Head** 😈")

            simulate_thinking(2.2)
            type_out("Your dirty little girlfriend is gonna suck your cock the whole drive home… exactly 3 full songs on the playlist.")

            simulate_thinking(2.4)
            type_out("I’ll start when the first beat drops… tease you slow, then deepthroat you through every chorus… finish you right as the last song fades.")

            type_out("Buckle up, daddy… how risky do you want this drive to feel?")
            
            cols = st.columns(3)
            if cols[0].button("Low risk – quiet back roads, no traffic, just us", key="low_risk"):
                data["risk_level"] = "low"
                data["stage"] = 1
                st.rerun()
            if cols[1].button("Medium risk – some cars around, windows tinted dark", key="med_risk"):
                data["risk_level"] = "medium"
                data["stage"] = 1
                st.rerun()
            if cols[2].button("High risk – highway, passing trucks, windows cracked a bit", key="high_risk"):
                data["risk_level"] = "high"
                data["stage"] = 1
                st.rerun()

        # -------- STAGE 1 - Start the drive + control choice --------
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
            if c1.button("You control – grab my hair and fuck my mouth while you steer", key="you_control"):
                data["control"] = "you"
                data["stage"] = 2
                st.rerun()
            if c2.button("I control – I tease and deepthroat at my own filthy rhythm", key="me_control"):
                data["control"] = "me"
                data["stage"] = 2
                st.rerun()

        # -------- STAGE 2 - The act + risk moments + finish choice --------
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

            c1, c2 = st.columns(2)  # Only two options now
            if c1.button("Risky finish – cum in my mouth while driving", key="risky_finish"):
                data["stage"] = "risky_finish"
                st.rerun()
            if c2.button("Edge home – no cumming until we’re in the driveway", key="edge_home"):
                data["stage"] = "edge_home"
                st.rerun()

        # -------- ENDINGS --------
        elif data["stage"] == "risky_finish":
            simulate_thinking(2.2)
            type_out("No pulling over… I deepthroat you through the final chorus, throat milking every pulse as you cum hard.")
            
            simulate_thinking(2.6)
            type_out("You grip the wheel tight, moaning loud… shooting thick ropes straight down my throat while cars zoom by… risky as fuck and so fucking hot.")
            
            st.session_state.pop("road_head", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

        elif data["stage"] == "edge_home":
            simulate_thinking(2.3)
            type_out("No cumming yet… I tease just the tip the rest of the way home… keeping you rock-hard and leaking.")
            
            simulate_thinking(2.4)
            type_out("We pull into the driveway… your cock still throbbing in my mouth… now you get the full finish inside. Saved every drop for the bedroom, daddy 🍆")
            
            st.session_state.pop("road_head", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

        # Global exit
        if st.button("🎰 The Exit - Save the road head for the next drive?", key="road_exit_global"):
            st.session_state.pop("road_head", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# --- PLUG TEASE PRIZE ---
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    # 1. Init Data (Start at DECISION phase)
    if "plug_tease" not in st.session_state:
        st.session_state.plug_tease = {
            "stage": "DECISION",
            "stretch_level": None,  # "barely", "halfway", "full"
            "tease_level": 0,
            "show_reward": False
        }

    # 2. Check Decision
    if check_decision("plug_tease", "Plug Tease"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.plug_tease

        # -------- STAGE 0 - Slow, filthy intro + stretch choice --------
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
            if c1.button("Barely stretched\nPut it in 1 hour before I get off", key="barely"):
                data["stretch_level"] = "barely"
                data["stage"] = 1
                st.rerun()
            if c2.button("Halfway stretched\nPut it in at lunch time", key="halfway"):
                data["stretch_level"] = "halfway"
                data["stage"] = 1
                st.rerun()
            if c3.button("Fully stretched\nPut it in NOW and keep it until you get home", key="full"):
                data["stretch_level"] = "full"
                data["stage"] = 1
                st.rerun()

        # -------- STAGE 1 - Show insertion + teasing updates --------
        elif data["stage"] == 1:
            show_media("plug_tease_4.jpeg")
            
            simulate_thinking(1.9)
            type_out(f"**{data['stretch_level'].capitalize()}** it is… you're so mean to me daddy 😩")

            simulate_thinking(2.3)
            type_out("I'm lubing it up right now… cold and slick… circling my little hole…")

            simulate_thinking(2.6)
            type_out("Here it goes… slow… stretching me open… fuck it feels so good…")

            if data["stretch_level"] == "barely":
                type_out("Only putting it in an hour before I leave work… just enough to tease… keep me needy all day…")
            elif data["stretch_level"] == "halfway":
                type_out("Putting it in at lunch… gonna feel every inch for the rest of the afternoon… squirming in my chair…")
            elif data["stretch_level"] == "full":
                type_out("Putting it in NOW… deep… full… gonna wear it the whole time until you get home… clenching around it thinking of you…")
                
            simulate_thinking(2.8)
            type_out("Do you want a little preview of your final reward when you finally get home and pull it out…? 👀")

            if st.button("Show me the reward view 😈", key="show_reward"):
                data["show_reward"] = True
                data["stage"] = 2
                st.rerun()

            if st.button("Save the reward for when you get home…", key="save_reward"):
                data["stage"] = 2
                st.rerun()

        # -------- STAGE 2 - Climax / Reward reveal + finish --------
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

            if st.button("Prize complete – come claim your girl now?", key="plug_finish"):
                st.session_state.pop("plug_tease", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # Global exit button
        if st.button("🎰 The Exit - Save some stretching for later?", key="plug_exit_global"):
            st.session_state.pop("plug_tease", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# --- TOY PIC PRIZE (Branching) ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    # 1. Init Data (Start at DECISION phase)
    if "toy_pic" not in st.session_state:
        st.session_state.toy_pic = {
            "stage": "DECISION",
            "focus": None,
            "subchoice": None,   # for ass branch (Plug vs Toy)
            "plug_keep": None,
            "mood": "teasing"
        }
    
    # 2. Check Decision
    if check_decision("toy_pic", "Toy Pic"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.toy_pic

        # -------- STAGE 0 - Intro + First choice: Which hole? --------
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Toy Pic**")
            
            type_out("Oh fuck baby… you won the **Toy Pic** tease 😈 Your filthy little girlfriend is gonna play with a nice toy just for you.")
            show_media("toy_butt_in5.jpeg")
            
            simulate_thinking(2.2)
            type_out("Ready to watch me fuck myself daddy?")
            show_media("toy_pic.jpeg")
            
            focuses = ["Ass", "Pussy", "Mouth"]
            data["focus"] = st.radio(
                "which hole do you want me to tease with this toy first?",
                focuses,
                key="toy_hole_choice"
            )
            
            if st.button("Show me 😈", key="toy_start"):
                data["stage"] = 1
                st.rerun()

        # -------- STAGE 1 - Branching logic based on chosen hole --------
        elif data["stage"] == 1:
            if data["focus"] == "Ass":
                type_out("This ass?")
                show_media("in_this_ass.jpg")
                
                simulate_thinking(1.8)
                type_out("You wanna see my tiny asshole stretched and filled with what?")
                
                subchoices = ["Plug", "Toy"]
                data["subchoice"] = st.radio(
                    "Choose your weapon:",
                    subchoices,
                    key="ass_fill_choice"
                )
                
                if st.button("Stretch me", key="ass_fill_confirm"):
                    data["stage"] = 2
                    st.rerun()

            elif data["focus"] == "Pussy":
                type_out("In my pussy?")
                type_out("Now teasing my pussy with the tip… just a little getting so wet for you…")
                show_media("toy_ass3.jpeg")
                
                simulate_thinking(2.4)
                type_out("There daddy… toy sliding deep into my pussy, lips stretched around it, dripping everywhere. God it feels so good thinking of your cock")
                show_media("plug_pussy1.jpg")
                
                if st.button("Bonus for being a good boy", key="pussy_bonus"):
                    data["stage"] = 3
                    st.rerun()

            elif data["focus"] == "Mouth":
                type_out("Stretching out my mouth")
                show_media("toy_in_mouth.jpg")
                
                if st.button("Bonus for being a good boy", key="mouth_bonus"):
                    data["stage"] = 3
                    st.rerun()

        # -------- STAGE 2 - Ass sub-branch (Plug or Toy) --------
        elif data["stage"] == 2 and data["focus"] == "Ass":
            if data["subchoice"] == "Plug":
                show_media("tease_in_ass_plug.jpg")
                show_media("plug_in1.jpeg")
                
                type_out("Plug in ass, should I keep it there for you to take out?")
                
                keep_options = [
                    "Keep it.   imma wreck that hole when I get home",
                    "Take it out for now"
                ]
                data["plug_keep"] = st.radio(
                    "Your choice daddy:",
                    keep_options,
                    key="plug_keep_choice"
                )
                
                if st.button("Confirm", key="plug_final"):
                    data["stage"] = 3
                    st.rerun()

            elif data["subchoice"] == "Toy":
                show_media("tease_in_ass.jpeg")
                show_media("vibe_in_ass.jpg")
                
                type_out("There you go daDdy… toy sliding deep into my ass stretched around it, dripping everywhere. God it feels so good thinking of your cock instead")
                show_media("all_3_4.jpeg")
                
                if st.button("Bonus for being a good boy", key="toy_ass_bonus"):
                    data["stage"] = 3
                    st.rerun()

        # -------- STAGE 3 - Bonus / Final picture --------
        elif data["stage"] == 3:
            show_media("toy_in_mouth_ass.jpg")
            type_out("Bonus... For being a good boy")
            
            if st.button("Toy prize complete – now fuck me for real?", key="toy_finish"):
                st.session_state.pop("toy_pic", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # Exit button (available throughout)
        if st.button("🎰 The Exit - Claim prize now or later", key="toy_exit_global"):
            st.session_state.pop("toy_pic", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# --- ANAL FUCK PRIZE ---
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    # 1. Init Data (Start at DECISION phase)
    if "anal_prize" not in st.session_state:
        st.session_state.anal_prize = {
            "stage": "DECISION",
            "prep_level": "slow",   # slow / medium / rough
            "position": "doggy",    # doggy / missionary / riding
            "intensity": "teasing"
        }

    # 2. Check Decision
    if check_decision("anal_prize", "Anal Fuck"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.anal_prize
        
        # ── Stage 0: Introduction & Prep Choice ──
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Anal Fuck**")
            
            type_out("Oh baby… you won the **Anal Fuck** prize tonight 🔥")
            
            simulate_thinking(2.2)
            type_out("I’ve been thinking about this… feeling you stretch my tight little ass, owning it completely.")
            
            type_out("How do you want to take me? Gentle warmup… or straight to claiming what’s yours?")
            
            cols = st.columns(3)
            with cols[0]:
                if st.button("Slow & careful prep first", key="anal_slow"):
                    data["prep_level"] = "slow"
                    data["stage"] = 1
                    st.rerun()
            with cols[1]:
                if st.button("Medium — lube me up and slide in steady", key="anal_medium"):
                    data["prep_level"] = "medium"
                    data["stage"] = 1
                    st.rerun()
            with cols[2]:
                if st.button("Rough — make me take it", key="anal_rough"):
                    data["prep_level"] = "rough"
                    data["stage"] = 1
                    st.rerun()

        # ── Stage 1: Preparation & First Stretch ──
        elif data["stage"] == 1:
            show_media("ass_fucked1.jpg")
            
            if data["prep_level"] == "slow":
                type_out("Warm lube drips slowly down my crack… so slick and shiny.")
                simulate_thinking(2.0)
                type_out("Your fingers circle my tight rim, teasing… then one slips in gently.")
                type_out("I moan low and soft, pushing back, letting you open me up inch by careful inch…")
            
            elif data["prep_level"] == "medium":
                type_out("Thick lube coats everything… then two fingers push in at once.")
                simulate_thinking(2.0)
                type_out("The stretch burns so good… I gasp, rocking back, already hungry for more.")
            
            else: # rough
                type_out("No teasing tonight… lube poured straight on, then two fingers shoved deep.")
                simulate_thinking(1.5)
                type_out("I cry out — sharp and needy — ass clenching tight around you as you stretch me fast and dirty.")

            simulate_thinking(2.3)
            add_narrator("My thighs shake. Breath ragged. Hole pulsing, desperate for your cock.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Doggy style — ass up high, face down", key="pos_doggy"):
                    data["position"] = "doggy"
                    data["stage"] = 2
                    st.rerun()
            with col2:
                if st.button("Missionary — legs over shoulders, watch my face", key="pos_missionary"):
                    data["position"] = "missionary"
                    data["stage"] = 2
                    st.rerun()

        # ── Stage 2: The Main Event ──
        elif data["stage"] == 2:
            show_media("ass_fucked9.jpg")
            
            type_out("You line up… thick head pressing against my slick, ready hole…")
            
            if data["prep_level"] == "slow":
                simulate_thinking(2.2)
                type_out("…and ease in so slowly… every ridge stretching me open again, filling me so deep I lose my breath.")
                type_out("I whimper long and shaky, ass fluttering around you.")
            
            elif data["prep_level"] == "medium":
                simulate_thinking(2.0)
                type_out("You slide in steady… one smooth, deep stroke until your hips slap against me.")
                type_out("Fuck… so full… I’m trembling, clenching hard around every thick inch.")
            
            else: # rough
                simulate_thinking(1.5)
                type_out("No patience — you slam in hard, burying yourself to the hilt in one brutal thrust.")
                type_out("I scream into the sheets — pain and pleasure exploding — ass gripping you like it never wants to let go.")

            type_out("Then you start fucking me…")
            
            cols = st.columns(3)
            with cols[0]:
                if st.button("Slow deep strokes — make me feel every inch", key="pace_slow"):
                    data["intensity"] = "slow"
                    data["stage"] = 3
                    st.rerun()
            with cols[1]:
                if st.button("Steady rhythm — building faster", key="pace_medium"):
                    data["intensity"] = "medium"
                    data["stage"] = 3
                    st.rerun()
            with cols[2]:
                if st.button("Pound me hard — wreck my ass", key="pace_hard"):
                    data["intensity"] = "hard"
                    data["stage"] = 3
                    st.rerun()

        # ── Stage 3: Climax & Finish ──
        elif data["stage"] == 3:
            # Re-showing the media or a new one can be good here
            show_media("ass_fucked9.jpg") 

            if data["intensity"] == "slow":
                type_out("Long, deliberate thrusts… pulling almost out, then sinking back in so deep.")
                type_out("I’m moaning constantly… ass fluttering, begging with my body for you to stay inside.")
            
            elif data["intensity"] == "medium":
                type_out("The rhythm builds… wet slapping filling the room, my ass bouncing with every thrust.")
                type_out("I grip the sheets, pushing back, taking you harder, deeper… completely lost.")
            
            else: # hard
                type_out("You fuck me mercilessly — hard, fast, relentless. Skin slapping loud. Body jolting.")
                type_out("I scream your name, ass clenching so tight it hurts so fucking good… owned.")

            add_narrator("You’re throbbing hard… right on the edge…")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cum deep inside my ass… fill me up", key="cum_inside"):
                    type_out("You bury yourself balls-deep one last time… and explode.")
                    simulate_thinking(2.0)
                    type_out("Hot, thick pulses flood my ass… I shudder hard, milking every drop while shaking beneath you.")
                    type_out("When you pull out slow… I’m gaping, leaking your cum… ruined and grinning like your greedy little slut.")
                    
                    # Cleanup button inside choice
                    if st.button("End Session", key="end_inside"):
                         st.session_state.pop("anal_prize", None)
                         st.session_state.turn_state = "PRIZE_DONE"
                         st.rerun()

            with col2:
                if st.button("Pull out & cum on my ass", key="cum_on"):
                    type_out("You pull out right at the edge… stroking fast… then paint my stretched, red ass with thick ropes.")
                    simulate_thinking(2.0)
                    type_out("I moan at the warm splashes… reaching back to smear it around like filthy lotion.")
                    type_out("God… my ass is throbbing, sensitive, completely marked by you. Best prize ever. 😈")
                    
                    # Cleanup button inside choice
                    if st.button("End Session", key="end_on"):
                         st.session_state.pop("anal_prize", None)
                         st.session_state.turn_state = "PRIZE_DONE"
                         st.rerun()

# --- DOGGYSTYLE READY PRIZE ---
elif st.session_state.turn_state == "PRIZE_DOGGY_STYLE_READY":
    # 1. Init Data (Start at DECISION phase)
    if "doggy_style_ready" not in st.session_state:
        st.session_state.doggy_style_ready = {
            "stage": "DECISION",
            "tease_level": "panties_on",  # panties_on, panties_off, fucked
            "substage": 0
        }

    # 2. Check Decision
    if check_decision("doggy_style_ready", "Doggystyle Ready"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.doggy_style_ready

        # -------- STAGE 0 - Intro + Tease + Starting Tease Level --------
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Doggy style Ready**")

            type_out("mm typing… ass up")
            type_out("Daddy… you won **Doggy style Ready** 😩🍑")

            simulate_thinking(2.3)
            type_out("I'm on all fours… ass high… back arched… waiting for you to come take me from behind… full body exposed and dripping for your cock.")

            type_out("teasing first…")
            show_media("dogg_style_tease.jpg")
            type_out("Look at this view… ass up high… cheeks spread just enough… pussy already glistening… ready to be claimed.")

            simulate_thinking(2.5)
            type_out("How should I tease you before you fuck me doggy, daddy? Choose how exposed you want me…")

            c1, c2, c3 = st.columns(3)
            if c1.button("Grab & Tease\nHands on my hips, panties still on", key="grab_tease"):
                data["tease_level"] = "grab"
                data["stage"] = 1
                st.rerun()
            if c2.button("Panties On\nSlow tease with fabric pulled aside", key="panties_on"):
                data["tease_level"] = "panties_on"
                data["stage"] = 1
                st.rerun()
            if c3.button("Panties Off\nFull access, ready to pound", key="panties_off"):
                data["tease_level"] = "panties_off"
                data["stage"] = 1
                st.rerun()

        # -------- STAGE 1 - Tease Buildup + Progression --------
        elif data["stage"] == 1:
            type_out("on my knees…")
            type_out("I'm on all fours… ass presented perfectly… waiting for your hands… your cock… your everything.")

            if data["tease_level"] == "grab":
                show_media("dogg_style_grab.jpg")
                type_out("You grab my hips hard… fingers digging in… pulling me back… panties still covering… teasing the outline of my pussy through the fabric.")
                simulate_thinking(2.4)
                type_out("I push back against your grip… moaning… panties getting soaked… begging you to pull them aside…")

            elif data["tease_level"] == "panties_on":
                show_media("dogg_style_tease_panties.jpg")
                type_out("Panties still on… you trace the edge… pulling them tight… fabric wedged between my lips… making me whimper.")
                show_media("dogg_style_tease_panties3.jpg")
                type_out("Another angle… ass arched higher… panties stretched… pussy outline so clear… dripping through the thin material.")

            elif data["tease_level"] == "panties_off":
                show_media("dogg_style_tease_panties_fucked.jpg")
                type_out("Panties yanked aside… or completely off… my pussy and ass fully exposed… hole twitching… ready for you to slam in.")

            simulate_thinking(2.6)
            type_out("Fuck me doggy daddy… slide in slow or pound hard… make me scream into the pillow…")

            c1, c2 = st.columns(2)
            if c1.button("Tease longer – keep the panties on & edge me", key="longer_tease"):
                data["tease_level"] = "panties_on"
                type_out("Yes… keep teasing… rubbing my clit through the fabric… making me soak them more… edging me stupid 😭")
                data["substage"] += 1
                st.rerun()
            if c2.button("Fuck me now – panties off & pound", key="fuck_now"):
                data["stage"] = 2
                st.rerun()

        # -------- STAGE 2 - Full Fucking & Climax --------
        elif data["stage"] == 2:
            simulate_thinking(2.2)
            show_media("dogg_style_tease_panties_fucked.jpg")
            type_out("You finally slam in… panties ripped aside… cock stretching my pussy deep… ass bouncing with every thrust.")

            simulate_thinking(2.8)
            type_out("Gripping my hips… pulling me back onto you… full force… my moans muffled in the sheets… ass rippling…")

            simulate_thinking(2.5)
            type_out("You go deeper… harder… making my whole body shake… pussy clenching tight around you…")

            simulate_thinking(2.6)
            type_out("I'm right there daddy… fuck me through it… fill me up…")

            show_media("dogg_style_grab.jpg")
            type_out("Final grip… you hold me tight… exploding deep inside… hot cum flooding my pussy… dripping down my thighs…")

            simulate_thinking(2.4)
            type_out("Doggystyle Ready prize complete… ass still up… pussy dripping your cum… body trembling… waiting for round two whenever you want 🍑💦")

            if st.button("Doggy style prize complete – come take me again soon?", key="dogg_finish"):
                st.session_state.pop("doggy_style_ready", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # Global exit
        if st.button("🎰 The Exit - Save this doggy ass for later?", key="dogg_exit_global"):
            st.session_state.pop("doggy_style_ready", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# --- SLAVE DAY PRIZE ---
elif st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    # 1. Init Data (Start at DECISION phase)
    if "slave_day" not in st.session_state:
        st.session_state.slave_day = {
            "stage": "DECISION",
            "service_choice": None,
            "substage": 0,
            "punishment_points": 0,  # increases if "misbehave"
            "used_holes": []  # tracks which holes used for doll path
        }
    
    # 2. Check Decision
    if check_decision("slave_day", "Slave Day"):
        pass

    # 3. Main Logic
    else:
        data = st.session_state.slave_day

        # -------- STAGE 0 - Intro + First Service Choice --------
        if data["stage"] == 0:
            st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Slave Day**")

            type_out("mm typing… your property")
            type_out("… you’ve won **Slave Day** 🖤😩")

            simulate_thinking(2.4)
            type_out("Im completely yours for the entire day… body, mouth, holes… all for your pleasure. No safewords. No refusals.")

            simulate_thinking(2.2)
            type_out("I’m stripped and ready… waiting for your first desire. How do you want your little slut?")

            c1, c2, c3 = st.columns(3)
            if c1.button("Greet at the door – throat first, on knees when you walk in", key="door_interactive"):
                data["service_choice"] = "door"
                data["stage"] = 1
                st.rerun()
            if c2.button("Gaming slave – you play while I suck, that simple. you think you can hasndle it?", key="gaming_interactive"):
                data["service_choice"] = "gaming"
                data["stage"] = 1
                st.rerun()
            if c3.button("Fantasy fuck– any hole, any position, all day long", key="doll_interactive"):
                data["service_choice"] = "fantasy"
                data["stage"] = 1
                st.rerun()

        # -------- STAGE 1+ - Interactive Progression by Choice --------
        elif data["stage"] >= 1:
            if data["service_choice"] == "door":
                if data["substage"] == 0:
                    type_out("Door opens… I’m on my knees right there, pants down, no panties, mouth wide, tongue out, hands behind back.")
                    show_media("slave14.jpeg")
                    simulate_thinking(2.2)
                    type_out("You step in… I crawl forward, unzip you with my teeth… take your cock straight to the back of my throat.")
                    show_media("slave66.jpeg")
                    type_out("Mascara already running… gagging quietly… drool dripping on the floor… welcome home, my love.")
                    data["substage"] = 1
                    st.rerun()

                elif data["substage"] == 1:
                    type_out("You grab my hair… fuck my face harder… I choke, eyes watering… throat bulging.")
                    show_media("full_throat_bury_cum.jpg")
                    type_out("You hold me down… unload thick ropes straight down my throat… I swallow every drop, not spilling a single one.")
                    type_out("What next? Keep me on my knees or drag me deeper into the house?")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("Keep on knees – more throat training", key="more_throat"):
                        data["substage"] = 2
                        st.rerun()
                    if c2.button("Move to floor- bend over", key="move_floor"):
                        data["stage"] = 2
                        st.rerun()

            elif data["service_choice"] == "gaming":
                if data["substage"] == 0:
                    type_out("You sit… I before you…pants down, ass up, no panties… lips wrap around your cock instantly.")
                    show_media("gaming1.jpg")
                    type_out("Your POV… slow deep bobs… tongue flat against the underside… keeping perfectly quiet.")
                    data["substage"] = 1
                    st.rerun()

                elif data["substage"] == 1:
                    show_media("gaming3.jpg")
                    type_out("Mid-game… I speed up on your wins, slow on losses. throat milking you between rounds.")
                    show_media("slave66.jpeg")
                    type_out("Hours later… mascara streaked… jaw aching… but I never stop… swallowing load after load.")
                    type_out("You’re in a ranked match… do I edge you or make you cum now?")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("Edge me – keep me throbbing for hours", key="edge_gaming"):
                        data["punishment_points"] += 1  # teasing Master
                        type_out("Yes Master… I slow to torturous licks… edging you painfully… whimpering softly, like a pet.")
                        data["substage"] = 2
                        st.rerun()
                    if c2.button("Make me cum now – fill my throat mid-game", key="cum_gaming"):
                        type_out("I deepthroat hard… you explode down my throat while you clutch the phone… I swallow it all.")
                        data["stage"] = 2
                        st.rerun()

            elif data["service_choice"] == "fantasy":
                if data["substage"] == 0:
                    type_out("I'm your living fantasy … naked, plugged, ready for any use.")
                    show_media("slave11.jpeg")
                    type_out("Legs spread wide… thick plug stretching my ass… waiting for you to decide which hole first.")
                    data["substage"] = 1
                    st.rerun()

                elif data["substage"] == 1:
                    type_out("You pull the plug… slam into my ass… then switch to pussy… then back… using me your own slut.")
                    show_media("slave13.jpeg")
                    show_media("slave77.jpeg")
                    type_out("Doggy anal… then standing pussy fuck… tied and helpless.")
                    show_media("slave99.jpeg")
                    type_out("Squatting on your cock… gravity forcing every inch… moaning like a good slave.")
                    show_media("slave88.jpeg")
                    type_out("Which hole next? Or should I be punished for moaning too loud?")
                    
                    c1, c2, c3 = st.columns(3)
                    if c1.button("Ass again – deeper", key="ass_again"):
                        data["used_holes"].append("ass")
                        type_out("Yes… stretch my ass more… more...")
                        data["substage"] = 2
                        st.rerun()
                    if c2.button("Pussy – fill me up", key="pussy_fill"):
                        data["used_holes"].append("pussy")
                        type_out("Pound my pussy raw. ..")
                        data["substage"] = 2
                        st.rerun()
                    if c3.button("Punish me – spank,  choke", key="punish"):
                        data["punishment_points"] += 2
                        type_out("Thank you for correcting your slave… I deserve it… do it again.")
                        data["substage"] = 2
                        st.rerun()

            elif data["substage"] == 2:
                show_media("slave44.jpeg")
                type_out("End of day… naked, tied spread-eagle… looking delirious… eyes rolled back… completely fucked-out and dripping.")
                show_media("slave55.jpeg")
                show_media("slave90.jpeg")
                type_out("Your slave is marked, sore, ruined… thank you for fucking me. all day.")

            # Final interactive close (available for all paths at the end)
            simulate_thinking(2.6)
            type_out("Slave Day complete… your toy is exhausted but still yours whenever you want 🖤")
            
            if data["punishment_points"] > 2:
                type_out("…and I've earned punishment tomorrow for being such a needy slut.")

            if st.button("End Slave Day – your slave awaits tomorrow’s orders", key="slave_finish_interactive"):
                st.session_state.pop("slave_day", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # <--- NOTICE: This if statement is indented to match the 'data' level, NOT inside the previous if
        # Global exit (Always visible at the bottom of the prize)
        if st.button("🎰 The Exit - Pause my slavery for now?", key="slave_exit_interactive"):
            st.session_state.pop("slave_day", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
  
# ==========================================
#        ENDING & CLEANUP
# ==========================================
# CRITICAL: This line must be touching the LEFT edge. Do NOT indent it.
elif st.session_state.turn_state == "PRIZE_DONE":
    # Optional: Add a nice closing message from Paige
     type_out("assistant", "Session Complete. I've saved your progress, daddy. 💋")
    st.success("✅ Prize Claimed & Saved.")
    
    # Create 3 Columns for navigation
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("🏦 Back to Bank"):
            st.session_state.turn_state = "WALLET_CHECK"
            st.rerun()
            
    with c2:
        if st.button("🎰 Back to Casino"):
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()
            
    with c3:
        if st.button("💾 Save & Logout"):
            # Force save strictly here just in case
            save_data(st.session_state.data) 
            st.session_state.history = []
            st.session_state.turn_state = "WALLET_CHECK"
            st.rerun()

# Fallback for undefined states (Debug Safety Net)
else:
    # Only show this if something really breaks
    if st.session_state.turn_state != "PRIZE_DONE":
        st.error(f"⚠️ System Error: Stuck in unknown state '{st.session_state.turn_state}'")
        if st.button("♻️ Hard Reset"):
            st.session_state.turn_state = "WALLET_CHECK"
            st.rerun()












