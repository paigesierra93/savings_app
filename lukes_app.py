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
        "house_fund": 0.0, "wallet_balance": 0.0, "bridge_fund": 0.0
    }
    if not os.path.exists(DATA_FILE): return default_data
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
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
#       PART 3: HELPER FUNCTIONS (SMART MEDIA)
# ==========================================
def add_chat(role, content):
    st.session_state.history.append({"type": "chat", "role": role, "content": content})

def add_narrator(content):
    st.session_state.history.append({"type": "narrator", "content": content})

# FIXED: Auto-detects if it is a video or image
def add_media(filepath):
    if filepath.lower().endswith(('.mp4', '.mov', '.webm')):
        media_type = "video"
    else:
        media_type = "image"
    st.session_state.history.append({"type": "media", "path": filepath, "kind": media_type})

def add_dual_media(path1, path2):
    st.session_state.history.append({"type": "dual_media", "path1": path1, "path2": path2})

def simulate_typing(seconds=1.5):
    with st.chat_message("assistant", avatar="paige.png"):
        placeholder = st.empty()
        placeholder.caption("💬 *Paige is typing...*")
        time.sleep(seconds)
        placeholder.empty()

def simulate_loading(seconds=1.5):
    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Processing..."):
            time.sleep(seconds)

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
    if st.session_state.get("last_state") != state_name:
        add_chat(role, content)
        st.session_state.last_state = state_name

def type_out(text, delay=0.04):
    # Anti-Duplicate Shield
    if st.session_state.history and st.session_state.history[-1].get("content") == text:
        return

    with st.chat_message("assistant", avatar="paige.png"):
        placeholder = st.empty()
        rendered = ""
        for word in text.split(" "):
            rendered += word + " "
            placeholder.markdown(rendered)
            time.sleep(delay)
    
    add_chat("assistant", text)

# FIXED: Checks file extension before displaying
def show_media(path, delay=2.5):
    # Anti-Duplicate Shield
    if st.session_state.history:
        last_item = st.session_state.history[-1]
        if last_item.get("type") == "media" and last_item.get("path") == path:
            return

    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Loading..."):
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


# ==========================================
#       PART 5: SIDEBAR (THE TANK)
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
    st.divider()
    admin_code = st.text_input("Admin Override", type="password", placeholder="Secret Code")
    if st.button("Reset Bank (Debug)"):
        st.session_state.data = {"tickets": 0, "tank_balance": 0.0, "tank_goal": 10000.0, "house_fund": 0.0, "wallet_balance": 0.0, "bridge_fund": 0.0}
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
    add_chat("user", user_msg)
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
    is_open, lock_msg = check_payday_window(admin_code)
    if is_open:
        if c1.button("💰 Full Paycheck"): st.session_state.turn_state="INPUT_PAYCHECK"; st.rerun()
    else: c1.warning(lock_msg)
    if c2.button("📱 Daily Dayforce"): st.session_state.turn_state="INPUT_DAILY"; st.rerun()
    if c3.button("💸 Side Hustle"): st.session_state.turn_state="INPUT_SIDE_HUSTLE"; st.rerun()
    if c4.button("🏦 Manage Funds"): st.session_state.turn_state="MANAGE_FUNDS"; st.rerun()

elif st.session_state.turn_state == "INPUT_SIDE_HUSTLE":
    st.subheader("💸 Side Hustle Input")
    side_amount = st.number_input("Side Income Amount ($):", min_value=0.0, step=5.0)
    if st.button("Process Extra Cash"):
        add_chat("user", f"Side Hustle: ${side_amount}")
        split = side_amount / 2
        st.session_state.data["tank_balance"] += split
        st.session_state.data["wallet_balance"] += split
        if side_amount >= 150: tickets=125
        elif side_amount >= 110: tickets=60
        elif side_amount >= 70: tickets=35
        elif side_amount >= 40: tickets=15
        else: tickets=0
        st.session_state.data["tickets"] += tickets
        save_data(st.session_state.data)
        msg = f"**Side Hustle:** ${side_amount:.2f}\n🛡️ Tank: ${split:.2f}\n💰 Wallet: ${split:.2f}\n🎟️ **TICKETS:** {tickets}"
        add_chat("assistant", msg)
        st.session_state.turn_state = "CHOOSE_TIER"
        st.rerun()

elif st.session_state.turn_state == "INPUT_PAYCHECK":
    st.subheader("💰 Full Paycheck")
    check_amount = st.number_input("Enter Total:", min_value=0.0, step=10.0)
    if st.button("Process Paycheck"):
        add_chat("user", f"Paycheck is ${check_amount}")
        safe_spend = check_amount - (200.0 + 80.0 + 100.0 + 50.0)
        st.session_state.data["bridge_fund"] += 50.0
        st.session_state.data["wallet_balance"] = safe_spend 
        if check_amount >= 601: tickets=100
        elif check_amount >= 501: tickets=50
        elif check_amount >= 450: tickets=25
        else: tickets=0
        st.session_state.data["tickets"] += tickets
        save_data(st.session_state.data)
        if safe_spend < 0: add_chat("assistant", f"⚠️ **SHORTAGE:** -${abs(safe_spend):.2f}.")
        else:
            add_chat("assistant", f"✅ **PROCESSED**\n💰 **SAFE TO SPEND:** ${safe_spend:.2f}\n🎟️ **TICKETS:** {tickets}")
            if tickets > 0: st.session_state.turn_state="CHOOSE_TIER"
            else: st.session_state.turn_state="CHECK_FAIL"
        st.rerun()

elif st.session_state.turn_state == "INPUT_DAILY":
    st.subheader("📱 Daily Dayforce")
    daily_amount = st.number_input("Available ($):", min_value=0.0, step=5.0)
    if st.button("Process Daily"):
        add_chat("user", f"Dayforce: ${daily_amount}")
        if daily_amount < 40.0: add_chat("assistant", f"⚠️ **Warning:** Not enough for Gas & House.")
        else:
            safe_spend = daily_amount - 10.0 - 30.0
            st.session_state.data["tank_balance"] += 30.0
            st.session_state.data["wallet_balance"] += safe_spend
            save_data(st.session_state.data)
            add_chat("assistant", f"**Strategy:**\nShielded $30 (House) + $10 (Gas).\n🍔 **SAFE TO SPEND:** ${safe_spend:.2f}")
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()

elif st.session_state.turn_state == "MANAGE_FUNDS":
    st.subheader("🏦 The Tank")
    st.info(f"Tank: ${st.session_state.data['tank_balance']:.2f}")
    move_amount = st.number_input("Amount ($):", min_value=0.0, step=10.0)
    c1, c2, c3 = st.columns(3)
    if c1.button("💸 Move to Wallet"):
        if move_amount > st.session_state.data['tank_balance']: st.error("Not enough.")
        else:
            st.session_state.data['tank_balance'] -= move_amount
            st.session_state.data['wallet_balance'] += move_amount
            save_data(st.session_state.data)
            add_chat("assistant", f"💸 Moved ${move_amount} to Wallet."); st.rerun()
    if c2.button("🏠 Lock to House"):
        if move_amount > st.session_state.data['tank_balance']: st.error("Not enough.")
        else:
            st.session_state.data['tank_balance'] -= move_amount
            st.session_state.data['house_fund'] += move_amount
            save_data(st.session_state.data)
            add_chat("assistant", f"🏠 Locked ${move_amount}."); st.rerun()
    if c3.button("Back"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "CHOOSE_TIER":
    tix = st.session_state.data["tickets"]
    st.subheader(f"🎰 Casino Floor (Balance: {tix} Tickets)")
    c1, c2, c3 = st.columns(3)
    if tix >= 25:
        if c1.button("🥉 Spin Bronze (25)"): st.session_state.turn_state="SPIN_BRONZE"; st.rerun()
    else: c1.warning("🥉 Bronze: Need 25")
    if tix >= 50:
        if c2.button("🥈 Spin Silver (50)"): st.session_state.turn_state="SPIN_SILVER"; st.rerun()
    else: c2.warning("🥈 Silver: Need 50")
    if tix >= 100:
        if c3.button("👑 Spin Gold (100)"): st.session_state.turn_state="SPIN_GOLD"; st.rerun()
    else: c3.warning("👑 Gold: Need 100")
    st.divider()
    if st.button("Save Tickets & Exit"):
        save_data(st.session_state.data)
        add_chat("assistant", f"Walking away? {get_ticket_save_response()}")
        st.session_state.turn_state="WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "CHECK_FAIL":
    add_chat("assistant", "Check too low. Try harder.")
    if st.button("Return"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

# --- SPINS ---
elif st.session_state.turn_state == "SPIN_BRONZE":
    if st.session_state.data["tickets"] >= 25:
        st.session_state.data["tickets"] -= 25; save_data(st.session_state.data)
        prizes = ["Bend Over", "Flash Me", "Jackoff Pass", "Shower Show"]
        win = spin_animation("Bronze", prizes)
        add_chat("assistant", f"🥉 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

elif st.session_state.turn_state == "SPIN_SILVER":
    if st.session_state.data["tickets"] >= 50:
        st.session_state.data["tickets"] -= 50; save_data(st.session_state.data)
        prizes = ["Toy Pic", "Lick Pussy", "Nude Pic", "Tongue Tease", "Road Head", "Plug Tease"]
        win = spin_animation("Silver", prizes)
        add_chat("assistant", f"🥈 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

elif st.session_state.turn_state == "SPIN_GOLD":
    if st.session_state.data["tickets"] >= 100:
        st.session_state.data["tickets"] -= 100; save_data(st.session_state.data)
        prizes = ["Anal Fuck", "All 3 Holes", "Slave Day", "Upside Down", "Doggy Style Ready"]
        win = spin_animation("Gold", prizes)
        add_chat("assistant", f"👑 JACKPOT: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()
# ==========================================
#       PRIZE SCRIPTS
# ======================================
# --- NUDE PIC PRIZE ---
elif st.session_state.turn_state == "PRIZE_NUDE_PIC":
    # 1. Init Data
    if "nude_pic" not in st.session_state:
        st.session_state.nude_pic = {"stage": 0, "focus": None}
    data = st.session_state.nude_pic

    # ── STAGE 0: Intro ──
    if data["stage"] == 0:
        add_chat("assistant", "You've won, your very own photo of me... which ever part you want to see...😈")
        
        simulate_loading(3)
        show_media("nude_1.jpg")
        
        # Typing effect with pauses
        type_out("I'm gonna tease you so fucking slow and nasty with every inch of my body…")
        time.sleep(3.0) # Explicit Pause
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

    # ── STAGE 1: The Tease (Specific Branch) ──
    elif data["stage"] == 1:
        
        # TITS PATH
        if data["focus"] == "TITS":
            add_chat("assistant", "Tits? Are you sure, daddy?")
            simulate_loading(4)
            show_media("nude_6.jpg")
            if st.button("enough teasing, show me your tits"):
                data["stage"] = 2
                st.rerun()

        # ASS PATH
        elif data["focus"] == "TIGHT ASS":
            add_chat("assistant", "Ass? Are you sure, daddy?")
            simulate_loading(4)
            show_media("nude_4.jpg")
            if st.button("Let me see it"):
                data["stage"] = 2
                st.rerun()

        # PUSSY PATH
        elif data["focus"] == "WET PUSSY":
            add_chat("assistant", "This little Pussy....Are you sure, daddy?")
            simulate_loading(4)
            show_media("nude_2.jpg") # Teaser before the spread
            if st.button("Pull them down already"):
                data["stage"] = 2
                st.rerun()

    # ── STAGE 2: The Reveal ──
    elif data["stage"] == 2:
        simulate_loading(5)

        if data["focus"] == "TITS":
            show_media("Nude_7.jpg")
            add_chat("assistant", "They would look so much better around your hard cock, huh?")
        
        elif data["focus"] == "TIGHT ASS":
            show_media("nude_5.jpg")
            add_chat("assistant", "All bare, spread, tight little holes all wet and ready....maybe next spin, they'll get fucked. 🍑")

        elif data["focus"] == "WET PUSSY":
            show_media("nude_3.jpg")
            add_chat("assistant", "wet and dripping...now")

        # Exit Button
        if st.button("That's enough for now… claim this prize now?"):
            del st.session_state.nude_pic
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun() 
# LICK MY PUSSY PRIZE - Explicitly typed-out typing indicators + ultra-teasing
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    if "lick_pussy" not in st.session_state:
        st.session_state.lick_pussy = {
            "stage": 0,
            "position": None,
            "tease_level": 0
        }
    data = st.session_state.lick_pussy

    def show_typing(text="typing...", duration=1.8):
        """Show explicit typing text with delay"""
        placeholder = st.empty()
        placeholder.markdown(f"**{text}** 💬")
        time.sleep(duration)
        placeholder.empty()

    # -------- STAGE 0 - Slow intro with spelled-out typing --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Lick My Pussy**")

        show_typing("typing...", 1.6)
        add_chat("assistant", "hey daddy… 💕")

        show_typing("Paige is typing...", 2.0)
        add_chat("assistant", "guess what you just won…")

        show_typing("mm typing… 🫦", 1.9)
        add_chat("assistant", "your tongue…")

        show_typing("typing… so wet already", 2.3)
        add_chat("assistant", "on this needy little pussy… all night if you want 😈")
        add_media("lick_it.jpeg")

        show_typing("Paige is typing…", 2.5)
        add_chat("assistant", "look how puffy and wet she already is… just from thinking about your mouth")

        show_typing("typing... edging myself", 2.2)
        add_chat("assistant", "I’ve been edging myself waiting for you… but I stopped right before")

        show_typing("fuck typing…", 2.4)
        add_chat("assistant", "now I’m throbbing so bad… aching for your tongue to finish me 💦")

        show_typing("tell me daddy…", 2.1)
        add_chat("assistant", "so… how do you wanna taste it first, baby? tell me exactly how…")

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

    # -------- STAGE 1 - Position reveal + heavy teasing with explicit typing --------
    elif data["stage"] == 1:
        show_typing(f"oh fuck… {data['position'].split('…')[0].strip()}?", 2.0)
        add_chat("assistant", f"oh fuck… **{data['position'].split('…')[0].strip()}**? 🥵")

        show_typing("typing… gonna lose it", 1.7)
        add_chat("assistant", "you picked the one that’s gonna make me lose it…")

        if "behind" in data["position"].lower():
            show_typing("ass up typing…", 2.2)
            add_media("from_behind.jpeg")
            show_typing("Paige is typing…", 2.4)
            add_chat("assistant", "ass up high… cheeks spread… pussy glistening right in your face")
            show_typing("breath on me…", 2.3)
            add_chat("assistant", "I can feel your hot breath teasing my clit already…")
            show_typing("slow baby…", 2.6)
            add_chat("assistant", "start sooo slow baby… trace the outside of my lips… barely touching… make me squirm")
            show_typing("mmm typing…", 2.5)
            add_chat("assistant", "mmmmm… yes… now the tip of your tongue… flick my hole lightly…")

        elif "back" in data["position"].lower() or "lay" in data["position"].lower():
            show_typing("legs wide…", 2.1)
            add_media("front_eat.jpeg")
            show_typing("typing… pull me in", 2.5)
            add_chat("assistant", "legs spread wide… knees by my ears… pussy swollen and begging")
            show_typing("hair pulling…", 2.3)
            add_chat("assistant", "I grab your hair… pull your face right in until your nose is pressed against me")
            show_typing("long licks…", 2.4)
            add_chat("assistant", "long flat licks… bottom to top… dragging over my clit every time…")
            show_typing("hips bucking…", 2.2)
            add_chat("assistant", "fuck… my hips are bucking already… don’t you dare stop…")

        elif "face" in data["position"].lower() or "sit" in data["position"].lower():
            show_typing("lowering…", 2.3)
            add_media("face_sit.jpeg")
            show_typing("grinding typing…", 2.6)
            add_chat("assistant", "lowering myself down slow… feeling your nose brush my clit")
            show_typing("smearing…", 2.4)
            add_chat("assistant", "I rock my hips… smearing my slick all over your lips… your chin…")
            show_typing("my seat…", 2.5)
            add_chat("assistant", "you love being smothered in this wet pussy don’t you? my good little seat 😈")
            show_typing("ride it…", 2.3)
            add_chat("assistant", "tongue out flat… let me ride it deep… use you like my favorite toy")

        elif "stand" in data["position"].lower():
            show_typing("standing over…", 2.2)
            add_media("standing_pussy.jpeg")
            show_typing("drip…", 2.5)
            add_chat("assistant", "standing over you… one foot up… lips parted so you see every pink inch")
            show_typing("drop falling…", 2.4)
            add_chat("assistant", "watch a thick drop slide down my thigh… falls right onto your tongue")
            show_typing("chase it…", 2.6)
            add_chat("assistant", "catch it baby… then lick upward slow… chase it back to my dripping hole")

        # Extra teasing layers with explicit typing
        show_typing("trembling…", 3.0)
        add_chat("assistant", "god I’m trembling…")

        show_typing("tiny flicks…", 2.4)
        add_chat("assistant", "circle my clit with just the tip… tiny little flicks… so light it drives me crazy")

        show_typing("edge me…", 2.7)
        add_chat("assistant", "now suck it gently… then flick fast… then slow again… edge me until I’m begging")

        show_typing("right there…", 3.2)
        if st.button("I’m right fucking there… make me squirt all over you daddy 💦", key="lick_climax"):
            show_typing("cumming…", 1.9)
            add_media("Cumming1.jpeg")
            show_typing("yesyesyes…", 2.3)
            add_chat("assistant", "ohhh fuck—yesyesyes—I’m cumming—I’m squirting everywhereeee 💦💦💦")
            show_typing("soaking you…", 2.5)
            add_chat("assistant", "my thighs shaking… pussy pulsing hard on your tongue… you’re drinking every gush")
            show_typing("messy face…", 2.4)
            add_chat("assistant", "look at your face… soaked… dripping… you made such a filthy mess of me 😩")

            show_typing("need cock…", 2.6)
            add_chat("assistant", "prize complete baby… but now I need your cock so bad…")

            if st.button("Come fuck your messy girl now? 🍆", key="lick_finish"):
                st.session_state.pop("lick_pussy", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

    # Global exit
    if st.button("🎰 The Exit - Save the rest for later?", key="lick_exit_global"):
        st.session_state.pop("lick_pussy", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# ANAL FUCK PRIZE - Enhanced interactive with full position choice, detailed teasing, and loading delays
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    if "anal_fuck" not in st.session_state:
        st.session_state.anal_fuck = {
            "stage": 0,
            "current_position": None,
            "lube_level": "normal",
            "substage": 0,
            "used_positions": []
        }
    data = st.session_state.anal_fuck

    def show_typing(text="typing...", duration=1.8):
        placeholder = st.empty()
        placeholder.markdown(f"**{text}** 💬")
        time.sleep(duration)
        placeholder.empty()

    def load_picture(image_name, delay=2.5):
        """Simulate realistic loading with spinner before displaying"""
        with st.spinner("Loading your filthy pic... 🍑"):
            time.sleep(delay)
        add_media(image_name)

    # -------- STAGE 0 - Intro + Tease + First Position Choice --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Anal Fuck**")

        show_typing("mm typing… ass throbbing", 1.7)
        add_chat("assistant", "Daddy… you won **Anal Fuck** 😩🍑")

        show_typing("Paige is typing… so needy", 2.4)
        add_chat("assistant", "I've been playing with my ass all morning… fingering it slow… stretching it just enough to take your thick cock without mercy.")

        show_typing("tease view…", 2.1)
        load_picture("ass_high_teasing.jpeg", 3.2)
        add_chat("assistant", "Ass arched high… cheeks spread… tiny hole already twitching and begging for you to ruin it…")

        show_typing("first position?", 2.6)
        add_chat("assistant", "How do you want to start destroying this tight little ass, daddy? Choose your opening position…")

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
        show_typing("yes daddy…", 1.9)

        if data["current_position"] == "surprise":
            surprise_pos = ["reverse", "doggy", "missionary"][len(data["used_positions"]) % 3]
            data["current_position"] = surprise_pos
            add_chat("assistant", f"Mmm surprise! Starting with **{surprise_pos.capitalize()}**… gonna make it extra dirty for you 😈")

        pos_desc = {
            "reverse": "Straddling you reverse… lowering my ass inch by inch… cheeks spreading wide as I sink down onto your cock.",
            "doggy": "Face buried in the pillow, ass high… you grip my hips tight and slam in deep from behind.",
            "missionary": "Legs hooked over your shoulders… staring into your eyes while you push in slow and deep."
        }[data["current_position"]]

        add_chat("assistant", pos_desc)

        show_typing("lube or raw…?", 2.3)
        add_chat("assistant", "How do you want my ass to feel when you first slide in?")
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
        show_typing("stretching me…", 2.0)

        if data["current_position"] == "reverse":
            load_picture("ass_fucked3.jpeg", 3.3)
            add_chat("assistant", "Reverse cowgirl… my ass bouncing hard… cheeks slapping against your thighs… riding you deep and slow then fast.")
        elif data["current_position"] == "doggy":
            load_picture("ass_fucked5.jpeg", 3.1)
            add_chat("assistant", "Doggy close-up… your cock buried balls-deep… stretching my hole wide with every brutal thrust.")
            load_picture("side_view_doggy.jpeg", 3.0)
            add_chat("assistant", "Side view… perfect arch… ass rippling with every slam… moaning like a desperate slut.")
        elif data["current_position"] == "missionary":
            load_picture("missionary_ass.jpg", 3.2)
            add_chat("assistant", "Missionary… legs pinned back… watching your face while you pound my ass slow and deep.")
            load_picture("ass_fucked_missionary.jpeg", 3.0)
            add_chat("assistant", "Close-up… my hole gripping you tight… clenching hard every time you bottom out.")

        if data["lube_level"] == "raw":
            add_chat("assistant", "Raw and rough… burning stretch… whimpering with every inch you force in… but fuck it feels so good.")
        elif data["lube_level"] == "lots":
            add_chat("assistant", "So slick… sliding in and out effortlessly… but my ass still squeezes you like a vice.")

        load_picture("holding_ass_open.jpeg", 3.4)
        add_chat("assistant", "Split panel… hands spreading my cheeks as wide as possible… showing how gaped and pink you've made my hole…")

        show_typing("more daddy…", 2.7)
        add_chat("assistant", "Don't stop… fuck me harder… make my ass yours…")

        c1, c2, c3 = st.columns(3)
        if c1.button("Switch position – I need a new angle", key="switch_position"):
            data["used_positions"].append(data["current_position"])
            data["stage"] = 3
            st.rerun()
        if c2.button("Go harder & deeper – make me scream", key="harder"):
            add_chat("assistant", "Yes… pounding mercilessly… ass bouncing wildly… tears in my eyes from how deep and rough you are 😭🍆")
            data["substage"] += 1
            st.rerun()
        if c3.button("Cum in my ass – fill me completely", key="finish_anal"):
            data["stage"] = 4
            st.rerun()

    # -------- STAGE 3 - Position Switch (Full Choice) --------
    elif data["stage"] == 3:
        show_typing("switching now…", 2.2)
        add_chat("assistant", "Mmm… let's change it up… which position do you want to fuck my ass in next?")

        positions = ["reverse", "doggy", "missionary"]
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
        show_typing("I'm so close…", 2.3)
        load_picture("anal mission_closeup.jpg", 3.1)
        add_chat("assistant", "Ass clenching tight around you… milking every inch… begging for your hot load deep inside…")

        load_picture("anal_squirt.jpeg", 3.3)
        add_chat("assistant", "Fuck—I'm squirting hard from my pussy while you destroy my ass… whole body shaking uncontrollably…")

        show_typing("cumming inside…", 2.9)
        load_picture("creampie_ass_fucking.jpg", 3.2)
        add_chat("assistant", "You slam balls-deep one last time… exploding… pumping thick, hot ropes of cum straight into my ass…")

        load_picture("creampie_ass.jpg", 3.0)
        add_chat("assistant", "Pulling out slow… your cum starts leaking from my stretched hole… dripping down my cheeks…")

        load_picture("creampie_ass.jpeg", 3.1)
        load_picture("cummed_ass.jpeg", 3.0)
        load_picture("cream_pie_ass13.jpg", 3.2)
        add_chat("assistant", "Multiple angles… my ruined ass overflowing with your load… gaping, creamy, completely filled and marked as yours 🍑💦")

        show_typing("all yours daddy…", 2.6)
        add_chat("assistant", "Anal prize complete… my ass is dripping your cum… sore, stretched, and still pulsing for more whenever you want 😩")

        if st.button("Anal Fuck complete – come claim this ass again soon?", key="anal_finish"):
            st.session_state.pop("anal_fuck", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

    # Global exit
    if st.button("🎰 The Exit - Save the rest of this ass for later?", key="anal_exit_global"):
        st.session_state.pop("anal_fuck", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
#--- BEND OVER ---
elif st.session_state.turn_state == "PRIZE_BEND_OVER":
    # ✅ FIXED: Combined text into one single string
    enter_state(
        "PRIZE_BEND_OVER",
        "assistant",
        "You know what that means, you have to bend over right when i say so anywhere, anytime. Hahaha, just fucking with you… you know exactly what it means, you dirty birdy.\n\n"
        "When you say 'bend over' and your slutty girlfriend slowly presents her ass and dripping pussy, no matter what I might be doing."
    )
    simulate_loading(3)
    add_media("explain_bendover.jpg")
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

elif st.session_state.turn_state == "PRIZE_BEND_OVER_REVEAL":
    show_media("grocery_bendover.jpeg")
    add_narrator("Fuck… I'm already so soaked just knowing you're staring at my holes like this…")
    
    if st.button("At home?"):
        simulate_loading(3)
        add_media("Bendover1.mp4")
        # FIX 2: Added state transition so the app moves forward
        st.session_state.turn_state = "PRIZE_BEND_OVER_1"
        st.rerun()

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
        show_media("grok_video_2026-01-17-20-02-13.mp4", delay=3)
        type_out("Look at that mess… my pussy's literally dripping down my thighs because of you.")
        type_out(
            "God I’m throbbing so bad… I want your thick cock splitting me open right now… "
            "but nope. Not yet. You gotta save all that cum for Silver, baby. Edge for me like a good boy."
        )
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()


# --- PRIZE: FLASH ME ---
# FIX 3: Changed 'if' to 'elif' to keep the logic chain intact
elif st.session_state.turn_state == "PRIZE_FLASH_ME":
    enter_state(
        "PRIZE_FLASH_ME",
        "assistant",
        "Fuck yes baby… you just won “Flash Me” 😈 Congrats, winner!"
    )
    if st.button("I’m pretty sure I know what this means…"):
        add_chat("user", "I’m pretty sure I know what this means…")
        st.session_state.turn_state = "PRIZE_FLASH_TWIST"
        st.rerun()

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

elif st.session_state.turn_state == "PRIZE_FLASH_CHOICE":
    enter_state(
        "PRIZE_FLASH_CHOICE",
        "assistant",
        "Come on baby… pick your poison. Which part of me are you throbbing to see flashed right now?"
    )
    c1, c2 = st.columns(2)
    if c1.button("Show me your tits"):
        add_chat("user", "Show me your tits.")
        show_media("Nude_7.jpg", delay=3)
        type_out(
            "There they are daddy… quick little flash of these soft, bouncy tits just for you. "
            "Nipples already hard thinking about your mouth on them 😏"
        )
        type_out(
            "Let me know when you're ready for the real thing… I’ll let you suck them all night if you win again."
        )
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
    if c2.button("Show me your pussy"):
        add_chat("user", "Show me your pussy.")
        show_media("flash_pussy1.jpg", delay=3)
        type_out(
            "Mmm fuck… here’s your sneak peek, winner. My pussy’s already glistening and swollen, "
            "dripping just from teasing you like this 🍑💦"
        )
        type_out(
            "No touching yet… but imagine sliding inside when you finally get the full prize. "
            "Let me know when you want to see — and taste — what's waiting underneath."
        )
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
    add_chat("assistant", "Mmm fuck yes baby… you just won the **Jackoff Pass** 😈 Your special prize: I give you full permission to stroke that thick cock while I tease the absolute shit out of you.")
    simulate_typing(4)
    
    add_chat("assistant", "No guilt, no holding back — I want you pumping hard, edging, leaking precum, imagining every filthy thing you’d do to me while I describe it in detail.")
    add_narrator("Your slutty girlfriend Paige is gonna make this so fucking hard for you… literally.")

    simulate_loading(4)
    add_media("jackoff3.jpeg")
    add_chat("assistant", "Rule #1: You can’t cum until I say so. Edge for me like a good boy.")
    add_chat("assistant", "Rule #2: Tell me exactly what you’re doing to that dick while you’re doing it… I want every dirty detail.")
   
    if st.button("Fuck… ready to play with yourself for me?"):
        st.session_state.turn_state = "PRIZE_JACKOFF_FUN"
        st.rerun()
elif st.session_state.turn_state == "PRIZE_JACKOFF_FUN":
    add_chat("assistant", "God I’m already so wet just thinking about you stroking to me… let’s make this nasty. Pick how you want your jackoff session to go, daddy.")
   
    c1, c2 = st.columns(2)
   
    with c1:
        if st.button("Just talk dirty to me while I stroke"):
            add_chat("user", "Just talk dirty to me while I stroke")
            simulate_typing(2)
            add_chat("assistant", "Mmm perfect… keep that hand moving slow and tight around your cock while I whisper how bad I want it inside me. "
                                 "Imagine my tight wet pussy gripping you, milking every drop… I’m fingering myself right now thinking about you exploding for me. "
                                 "Edge it baby — get right to the brink then stop. Tell me how close you are… fuck I love when you’re throbbing and desperate for your Paige 🥵")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
           
    with c2:
        if st.button("Tease me with a recap of all my prizes while I cum"):
            add_chat("user", "Tease me with a recap of all my prizes while I cum")
            simulate_typing(2)
            add_chat("assistant", "Oh you greedy boy… want me to remind you of every filthy prize you’ve won so far while you pump that dick?")
            add_chat("assistant", "Remember when I bent over and showed you my dripping pussy… or when I flashed these tits and that soaked cunt under my skirt… "
                                 "all that was just for you, winner. Now stroke faster — picture sliding into every hole I teased you with.")
            add_chat("assistant", "Here’s a little visual reminder of what you own… all these prizes waiting for your cock.")
            simulate_loading(4)
            add_media("Jackkoff1.jpeg")  # Replaced placeholder
            simulate_typing(2)
            add_chat("assistant", "Cum for me now baby… shoot that load thinking about fucking your dirty little prize in person next time. "
                                 "I’m touching myself watching you lose it 😈")
            add_narrator("Good boy… you earned every drop.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
# --- SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("Steam is rising… your naughty little prize is about to get wet and slippery for you 😈")
    add_chat("assistant", "Mmm daddy… you won the Shower Show. Time to watch your girlfriend soap up every inch of this body — slowly, teasingly, while I think about your cock the whole time. One rule: no touching.")
   
    simulate_loading(4)
    add_media("shower_water.jpg")  # Replaced placeholder
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
    simulate_loading(4)
    add_media("shower_finger.jpeg")  # Replaced placeholder
   
    if st.session_state.shower_choice == "Slow and sensual tease – make you throb watching me lather up":
        add_chat("assistant", "Mmm… nice and slow just like you like. Watch my hands glide over these wet tits, circling my hard nipples… down my stomach to my slippery pussy. "
                             "I'm so fucking turned on knowing you're staring — my clit is throbbing under the suds, baby. Imagine your tongue there instead…")
    else:
        add_chat("assistant", "Fuck yes… full filthy mode for my winner. Hands all over – squeezing these soapy tits, pinching my nipples hard while I moan your name. "
                             "Now spreading my legs under the water, fingers sliding between my wet lips, rubbing my swollen clit fast… God I'm dripping more than the shower. "
                             "Wish this was your cock pounding me against the wall right now 🥵")
    add_chat("assistant", "Show's almost over… but I’ve got one last treat when I step out. What do you want as your post-shower reward, daddy?")
    after_choice = st.radio(
        "Pick your final prize piece:",
        ["take the towel and dry me off completely",
         "lick all the water off my pussy"]
    )
   
    if st.button("End the shower"):
        simulate_loading(3)
        add_media("shower_towel3.jpeg")  # Replaced placeholder
       
        if "take the towel" in after_choice:
            add_chat("assistant", "Mmm… pat me down slow – towel sliding over my wet tits, between my thighs, teasing those sensitive spots. "
                                 "Still dripping… still thinking about you fucking me dry. Save that hard cock for next time, baby.")
            simulate_loading(4)
            add_media("shower_towel1.jpeg")
        elif "lick all" in after_choice:
            add_chat("assistant", "There it goes… towel on the floor. Full naked, skin still glistening, nipples hard from the cool air. "
                                 "Turn around – ass still wet, pussy, needs drying. get to licking 😏")
            simulate_loading(4)
            add_media("naked_shower.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
# MASSAGE PRIZE ---
elif st.session_state.turn_state == "MASSAGE":
    if "tension" not in st.session_state:
        st.session_state.tension = 0
   
    add_chat("assistant", "Fuck yes baby… you won the **Massage Prize** 😈 Your naughty girlfriend Paige is gonna give you the hottest backwards rub ever. Lie face-down on the bed, naked or in boxers… let me straddle your thighs and oil up that strong back.")
    simulate_typing(2)
    add_chat("assistant", "I’m in tiny shorts and a tight top, tits barely contained, hands slick with warm oil. This is gonna be slow, deep, teasing… making you rock-hard while I whisper all the dirty things I want you to do to me later.")
    add_chat("assistant", "No flipping over, no touching me back — just you throbbing under my touch, leaking precum, while I get dripping wet from feeling you get so hard for me. Ready, daddy?")
    simulate_loading(2)
    add_media("example_massage_oil.jpg")  # Replaced placeholder
   
    add_chat("assistant", "Where do you want your slutty masseuse to start rubbing first?")
   
    c1, c2, c3 = st.columns(3)
    if c1.button("Shoulders & upper back – nice and relaxing"):
        add_chat("user", "Shoulders & upper back – nice and relaxing")
        simulate_typing(1)
        add_chat("assistant", "Mmm… fingers digging into your shoulders, working down your spine, pressing my soft tits against your back as I lean in close. You’re already getting so hard underneath… I can feel it.")
        simulate_loading(3)
        add_media("example_massage1.jpg")  # Replaced placeholder
        st.session_state.turn_state = "MASSAGE_POS"
        st.rerun()
       
    if c2.button("Lower back – deep and slow"):
        add_chat("user", "Lower back – deep and slow")
        simulate_typing(1)
        add_chat("assistant", "Oh fuck… thumbs pressing into your lower back, sliding slow and firm. I’m rocking my hips a little on your thighs, letting you feel how soaked my shorts are getting just from rubbing you.")
        st.session_state.turn_state = "MASSAGE_POS"
        st.rerun()
       
    if c3.button("Thighs – outer and inner, get me closer"):
        add_chat("user", "Thighs – outer and inner, get me closer")
        simulate_typing(1)
        add_chat("assistant", "God yes… hands gripping your strong thighs, kneading the muscles, sliding up higher on the insides. Every stroke makes your cock twitch against the bed… I’m biting my lip, pussy throbbing for you.")
        st.session_state.turn_state = "MASSAGE_POS"
        st.rerun()
elif st.session_state.turn_state == "MASSAGE_POS":
    add_chat("assistant", "Mmm… you’re getting so tense in the best way, baby. How do you want me positioned while I keep rubbing you deeper?")
    add_chat("assistant", "Tell me how close you want your dirty little masseuse to get…")
   
    col1, col2 = st.columns(2)
    if col1.button("Lean in close – tits pressed on your back"):
        add_chat("user", "Lean in close – tits pressed on your back")
        simulate_typing(2)
        add_chat("assistant", "Like this? I’m leaning forward, soft tits squishing against your oiled back, nipples hard through my top, while my hands glide down your sides. Every breath I take makes you feel how turned on I am.")
        st.session_state.tension += 2
        simulate_loading(3)
        add_media("example_massage_back.jpg")  # Replaced placeholder
        st.session_state.turn_state = "MASSAGE_LOOP_1"
        st.rerun()
       
    if col2.button("Stay straddled – hips rocking lightly"):
        add_chat("user", "Stay straddled – hips rocking lightly")
        simulate_typing(2)
        add_chat("assistant", "Perfect… staying straddled on your thighs, rocking my hips slow, letting you feel my wet heat through my shorts while my hands work your muscles. Your cock is so fucking hard now… leaking for me.")
        st.session_state.tension += 1
        st.session_state.turn_state = "MASSAGE_LOOP_1"
        st.rerun()
elif st.session_state.turn_state == "MASSAGE_LOOP_1":
    add_chat("assistant", "Your dick is throbbing against the bed… every time I press down you twitch harder.")
    add_narrator("Her breathing is heavy… she’s grinding subtly on your thighs, whispering filthy promises.")
   
    if st.button("Beg me to rub harder / longer"):
        add_chat("user", "Beg me to rub harder / longer")
        simulate_typing(2)
        add_chat("assistant", "Please baby… harder… keep those strong hands on me longer… I’m dripping so much thinking about your cock sliding inside me after this.")
        st.session_state.tension += 3
        st.session_state.turn_state = "MASSAGE_LOOP_2"
        st.rerun()
       
    if st.button("Stay silent – just throb and take it"):
        add_chat("user", "Stay silent – just throb and take it")
        simulate_typing(2)
        add_chat("assistant", "*soft moans from me*… I’m pressing my tits harder against you, rocking faster, feeling your cock pulse under me. You’re so close to the edge… good boy.")
        st.session_state.turn_state = "MASSAGE_LOOP_2"
        st.rerun()
elif st.session_state.turn_state == "MASSAGE_LOOP_2":
    add_chat("assistant", "Fuck… your whole body is tense, cock dripping precum onto the sheets… I’m so wet from making you this hard.")
    simulate_loading(3)
    add_media("example_massage_glutes.jpg")  # Replaced placeholder
   
    add_narrator("She’s practically humping your thighs now… whispering how bad she wants you.")
    add_chat("assistant", "You gonna beg me to let you flip and take me… or stay prone and edge like a good boy?")
    if st.button("Beg to flip over – need release"):
        add_chat("user", "Beg to flip over – need release")
        simulate_typing(1)
        add_chat("assistant", "Mmm… I know you’re dying to flip and fuck me, but not this time. Next win, I promise. For now, just throb and leak while I grind one last time.")
        st.session_state.tension += 5
        st.session_state.turn_state = "MASSAGE_END"
        st.rerun()
       
    if st.button("Submit – stay prone and edge"):
        add_chat("user", "Submit – stay prone and edge")
        simulate_typing(1)
        add_chat("assistant", "Perfect… staying right here, my soaked shorts grinding on your thighs, tits on your back, hands teasing your muscles. No cumming… just endless hard throbbing for your Paige.")
        st.session_state.turn_state = "MASSAGE_END"
        st.rerun()
elif st.session_state.turn_state == "MASSAGE_END":
    add_chat("assistant", "God baby… that backwards rub left you rock-hard and aching. I’m dripping too…")
   
    if st.session_state.tension >= 5:
        add_chat("assistant", "You’re trembling, cock leaking so much… I almost made you cum just from the tease. You edged like a champ – next prize, I’ll ride you until you explode inside me.")
        simulate_loading(3)
        add_media("example_massage_tremble.jpg")  # Replaced placeholder
    else:
        add_chat("assistant", "Still so hard and denied… perfect. I love feeling you throb under my hands, saving all that cum for me.")
    simulate_typing(3)
    add_chat("assistant", "Massage over… but I’m still wet and ready whenever you win big again.")
    add_chat("assistant", "Rule reminder: No cumming from the rub – all that load belongs to your girlfriend next time.")
    add_narrator("She leans down, kisses your shoulder, then slips off… leaving you hard, oiled, and desperate.")
   
    st.session_state.turn_state = "PRIZE_DONE"
    st.rerun()
   
# ALL 3 HOLES (Total Overload) ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    if "all_3_holes" not in st.session_state:
        st.session_state.all_3_holes = {
            "stage": 0,
            "filled": {"pussy": False, "ass": False, "mouth": False},
            "first_hole": None
        }
    data = st.session_state.all_3_holes

    # ── Stage 0: Pick FIRST hole to fill with cock ──
    if data["stage"] == 0:
        add_chat("assistant", "Fuck yes daddy… you won the **ultimate filthy prize**: All 3 Holes Total Overload 😈")
        add_chat("assistant", "Your nasty little cumdump is completely yours to ruin. Every hole gets wrecked tonight.")
        add_chat("assistant", "Pick which hole your thick cock destroys **first**…")

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
        simulate_loading(2)

        if data["first_hole"] == "pussy":
            add_media("mkh5dpc060z62y.jpeg")
            add_chat("assistant", "Like this daddy? Your fat cock slamming balls-deep into my greedy pussy, stretching me wide… fuck ya?")
            add_chat("assistant", "I'm already dripping down your balls, begging for the rest…")

        elif data["first_hole"] == "ass":
            add_media("inmyass.jpeg")
            add_chat("assistant", "This little hole baby? Your cock forcing its way into my tight ass, tearing me open raw… fuck ya?")
            add_chat("assistant", "I'm moaning like a desperate whore, pushing back for more…")

        else:  # mouth
            add_media("dick_tease16.jpeg")
            add_chat("assistant", "Like this? Shoving your cock down my slutty throat, making me gag and drool everywhere… fuck ya?")
            add_chat("assistant", "Tears running, spit dripping… ready for you to wreck the other holes now…")

        remaining = [h for h in ["pussy", "ass", "mouth"] if not data["filled"][h]]

        if remaining:
            add_chat("assistant", "Now give me the next one, daddy… which hole gets ruined next?")
            cols = st.columns(len(remaining))
            for i, hole in enumerate(remaining):
                label = f"{'Cunt' if hole=='pussy' else 'Ass' if hole=='ass' else 'Mouth/Throat'}"
                if cols[i].button(f"Fill my {label} next"):
                    data["filled"][hole] = True
                    data["stage"] = 2 if len([v for v in data["filled"].values() if v]) == 2 else 1
                    st.rerun()
        else:
            data["stage"] = 3
            st.rerun()

    # ── Stage 2: Second hole filled (transition) ──
    elif data["stage"] == 2:
        simulate_loading(2)
        add_chat("assistant", "Fuuuck… two holes stuffed already. I'm shaking, leaking, completely owned…")
        add_chat("assistant", "One more daddy… fill that last filthy hole and make me your total 3-hole wreck.")
        # Quick teaser of the last hole
        last_hole = next(h for h,v in data["filled"].items() if not v)
        if last_hole == "pussy":
            add_media("mkh5dpc060z62y.jpeg")
        elif last_hole == "ass":
            add_media("inmyass.jpeg")
        else:
            add_media("dick_tease16.jpeg")
        if st.button("Fuck ya – complete all 3 holes now"):
            data["filled"][last_hole] = True
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: All holes filled + close-up inspection ──
    elif data["stage"] == 3:
        simulate_loading(3)
        add_media("all_3_4.jpeg")  # or your best triple-filled image
        add_chat("assistant", "Holy shit… all three holes completely fucking destroyed. I'm a drooling, trembling, overstuffed mess.")
        add_chat("assistant", "Look at what you did to your little cumslut daddy… inspect your work.")

        cols = st.columns(3)

        with cols[0]:
            if st.button("Let me see your pussy filled"):
                add_media("mkjdh9exrj9kdr.jpeg")
                add_chat("assistant", "Look at this wrecked cunt… stretched, swollen, dripping your cum or my squirt everywhere.")

        with cols[1]:
            if st.button("Let me see your mouth filled"):
                add_media("dick_tease8.jpeg")
                add_chat("assistant", "Throat raw, lips swollen, spit and precum running down my chin… total face-fuck ruin.")

        with cols[2]:
            if st.button("Let me see your ass dripping"):
                add_media("3holesasscum.jpeg")
                add_chat("assistant", "Ass gaped and leaking, cum oozing out while I clench around nothing… you fucking broke it.")

        st.write("---")
        if st.button("Finish & Collapse – I'm done daddy"):
            simulate_loading(3)
            add_chat("assistant", "Cumming so fucking hard… body convulsing, holes pulsing, squirting and shaking apart.")
            add_chat("assistant", "You've ruined me completely… your perfect overloaded fucktoy.")
            add_narrator("She collapses in a sweaty, cum-soaked heap, holes still twitching, blissed-out smile.")
            add_chat("assistant", "Prize complete. Come cuddle your broken little whore now… or use me again whenever you want 😈")
            del st.session_state.all_3_holes
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
# ROMANTIC FANTASY ---
elif st.session_state.turn_state == "PRIZE_ROMANTIC_FANTASY":
    if "romantic_fantasy" not in st.session_state:
        st.session_state.romantic_fantasy = {
            "stage": 0,
            "setting": "bedroom",
            "intensity": "soft",
            "ending": "slow"
        }
    data = st.session_state.romantic_fantasy
    # ── Stage 0: Setting ──
    if data["stage"] == 0:
        add_chat("assistant", "Baby… you won the **Romantic Fantasy** prize tonight 💕 No rush, no games… just you and me, lost in pure love and passion.")
        add_chat("assistant", "Let me take you somewhere beautiful in our minds… where every touch feels like forever. Where do you want our fantasy to unfold?")
        settings = [
            "Candlelit bedroom at home – soft sheets, rose petals, just us",
            "Secluded beach at sunset – waves crashing, warm sand, golden light",
            "Luxury hotel suite – champagne, city lights, elegant and intimate",
            "Cozy cabin in the woods – fireplace, blankets, snowy night outside"
        ]
        data["setting"] = st.radio("Choose our romantic escape:", settings)
        c1, c2 = st.columns(2)
        if c1.button("Soft & tender – gentle, loving, slow"):
            data["intensity"] = "soft"
            data["stage"] = 1
            st.rerun()
        if c2.button("Passionate & intense – deeper, more urgent desire"):
            data["intensity"] = "hard"
            data["stage"] = 1
            st.rerun()
    # ── Stage 1: Entry ──
    elif data["stage"] == 1:
        add_chat("assistant", f"Mmm… {data['setting']}. I can already feel it… the air warm, the world fading away until it's only us.")
        simulate_loading(2)
        add_media("example_rom_ambient.jpg")  # Replaced placeholder
        if data["intensity"] == "soft":
            add_chat("assistant", "I step close, my hands gently cupping your face… our eyes lock, hearts racing. I kiss you so softly, lips brushing like a promise.")
        else:
            add_chat("assistant", "I pull you to me urgently, fingers in your hair, kissing you deeply, tongues dancing, bodies pressing tight with need.")
        add_narrator("Our breaths mingle… slow, heated, full of unspoken love.")
        if st.button("Take me… make this fantasy real"):
            data["stage"] = 2
            st.rerun()
    # ── Stage 2: Union ──
    elif data["stage"] == 2:
        simulate_loading(3)
        add_media("example_rom_union.jpg")  # Replaced placeholder
        add_chat("assistant", "You ease me down onto the sheets/sand/bed… our bodies align perfectly, skin on skin.")
        add_chat("assistant", "I wrap my legs around you as you slide inside me slowly… deeply… filling me completely. Every thrust feels like home.")
        add_narrator("Time stops… just the rhythm of our hearts, soft moans, whispers of 'I love you' between kisses.")
        c1, c2 = st.columns(2)
        if c1.button("Slow & loving – savor every moment"):
            data["ending"] = "slow"
            data["stage"] = 3
            st.rerun()
        if c2.button("Build to intense passion – lose ourselves"):
            data["ending"] = "hard"
            data["stage"] = 3
            st.rerun()
    # ── Stage 3: Afterglow ──
    elif data["stage"] == 3:
        simulate_loading(2)
        add_media("example_rom_climax.jpg")  # Replaced placeholder
        add_chat("assistant", "We move together perfectly… building higher, breath quickening, until we shatter in each other's arms… waves of pleasure crashing over us.")
        simulate_loading(3)
        add_media("example_rom_after.jpg")  # Replaced placeholder
        add_chat("assistant", "We stay like this… bodies still joined, hearts beating as one. I trace your face, whispering how much I love you.")
        add_chat("assistant", "Thank you for making this fantasy feel so real, my love… you're my everything.")
        add_chat("assistant", "This prize isn't over until we're ready… stay here with me forever? 💕")
        del st.session_state.romantic_fantasy  # Reset instead of undefined function
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# UPSIDE DOWN THROAT FUCK PRIZE - Ultra-teasing, interactive with typing indicators & loading
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN":
    if "Upside" not in st.session_state:
        st.session_state.upside_down = {
            "stage": 0,
            "intensity": "slow",  # slow, medium, rough
            "substage": 0
        }
    data = st.session_state.upside_down

    def show_typing(text="typing...", duration=1.8):
        placeholder = st.empty()
        placeholder.markdown(f"**{text}** 💬")
        time.sleep(duration)
        placeholder.empty()

    def load_picture(image_name, delay=2.5):
        """Simulate realistic loading with spinner"""
        with st.spinner("Loading your filthy throat pic... 😈"):
            time.sleep(delay)
        add_media(image_name)

    # -------- STAGE 0 - Intro + Tease + Intensity Choice --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Upside Down Throat Fuck**")

        show_typing("mm typing… throat ready", 1.7)
        add_chat("assistant", "Daddy… you won **Upside Down Throat Fuck** 😩💦")

        show_typing("Paige is typing… head hanging", 2.3)
        add_chat("assistant", "I'm laying on the edge of the bed… head hanging off… throat perfectly aligned for you to fuck my mouth like a toy… my full body exposed and helpless for you.")

        show_typing("teasing alone…", 2.1)
        load_picture("upside_alone.jpg", 3.2)
        add_chat("assistant", "Look at me… naked, legs spread, waiting… head dangling… mouth open… ready to be used.")

        show_typing("how rough?", 2.5)
        add_chat("assistant", "How hard do you want to fuck this upside-down throat, daddy? Choose your intensity…")

        c1, c2, c3 = st.columns(3)
        if c1.button("Slow & Deep\nTease my throat first", key="slow_throat"):
            data["intensity"] = "slow"
            data["stage"] = 1
            st.rerun()
        if c2.button("Medium Pace\nSteady fucking", key="medium_throat"):
            data["intensity"] = "medium"
            data["stage"] = 1
            st.rerun()
        if c3.button("Rough & Merciless\nMake me gag & drool", key="rough_throat"):
            data["intensity"] = "rough"
            data["stage"] = 1
            st.rerun()

    # -------- STAGE 1 - Setup & Entry --------
    elif data["stage"] == 1:
        show_typing("laying down now…", 1.9)
        add_chat("assistant", "I'm on my back… head hanging off the bed… throat straight… mouth wide open… full body on display for you.")

        load_picture("upside_tease.jpg", 3.0)
        add_chat("assistant", "Teasing you… tongue out… eyes up… begging silently for your cock.")

        show_typing("first entry…", 2.4)
        if data["intensity"] == "slow":
            load_picture("deep_throat_entry_slow31.jpg", 3.3)
            load_picture("deep_throat_entry_slow1.jpg", 3.2)
            add_chat("assistant", "Slow… you slide in gently… inch by inch… letting my throat stretch around you… feeling every flutter.")
        elif data["intensity"] == "medium":
            load_picture("upside_downcloseup.jpg", 3.1)
            add_chat("assistant", "Steady… pushing in deeper… filling my throat… holding for a second before pulling back.")
        elif data["intensity"] == "rough":
            load_picture("upside_closeup.jpg", 3.4)
            add_chat("assistant", "Rough… you slam in hard… making me gag instantly… drool pouring down my upside-down face.")

        show_typing("full view…", 2.6)
        load_picture("upside_fromside1.jpg", 3.0)
        add_chat("assistant", "Side view… my body arched… tits up… legs spread… completely exposed while you use my throat.")

        show_typing("from behind…", 2.3)
        load_picture("upside_frombehind1.jpg", 3.2)
        add_chat("assistant", "From behind angle… ass in the air… pussy dripping… head hanging… perfect view of you fucking my face.")

        show_typing("keep going daddy…", 2.7)
        add_chat("assistant", "Fuck my throat harder… make me choke… use me like your personal upside-down toy…")

        c1, c2 = st.columns(2)
        if c1.button("Go harder – make me gag more", key="harder_throat"):
            data["intensity"] = "rough"
            add_chat("assistant", "Yes… slamming deeper… drool everywhere… mascara running… throat bulging with every thrust 😭")
            data["substage"] += 1
            st.rerun()
        if c2.button("Finish down my throat – cum now", key="finish_throat"):
            data["stage"] = 2
            st.rerun()

    # -------- STAGE 2 - Climax & Finish --------
    elif data["stage"] == 2:
        show_typing("so deep…", 2.2)
        load_picture("upside_downcloseup.jpg", 3.1)
        add_chat("assistant", "Throat stretched wide… your cock buried to the balls… pulsing against my tongue…")

        show_typing("cumming…", 2.8)
        add_chat("assistant", "You thrust one last time… exploding… thick hot ropes shooting straight down my upside-down throat…")

        show_typing("swallowing…", 2.5)
        add_chat("assistant", "I swallow every drop… gagging but taking it all… cum leaking from the corners of my mouth… dripping down my face…")

        show_typing("aftermath…", 2.6)
        load_picture("upside_closeup.jpg", 3.0)
        add_chat("assistant", "Pulling out slow… strings of spit and cum connecting your cock to my lips… my face messy… throat raw…")

        show_typing("all yours…", 2.4)
        add_chat("assistant", "Upside Down Throat Fuck complete, daddy… my throat is yours… sore, filled, and ready for more whenever you want 💦")

        if st.button("Throat prize complete – come use my mouth again soon?", key="throat_finish"):
            st.session_state.pop("upside_throat", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

    # Global exit
    if st.button("🎰 The Exit - Save the rest of this throat for later?", key="throat_exit_global"):
        st.session_state.pop("upside_down", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
       
#--- TONGUE TEASE (Complex Edging Game) ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    if "tongue_tease" not in st.session_state:
        st.session_state.tongue_tease = {
            "stage": 0,
            "edging_level": 0,
            "begged": False,
            "impatient": False
        }
    data = st.session_state.tongue_tease

    # ── Stage 0: Intro ──
    if data["stage"] == 0:
        add_chat("assistant", "Mmm daddy… you won the **Tongue Tease** prize 😈")
        add_chat("assistant", "This is where your girlfriend is gonna kneel between your legs and worship just the tip of that thick cock with my tongue and lips… nothing else, while you stroke the rest yourself.")
        
        show_media("grok_video_2026-01-18-13-54-56.mp4")
        
        add_chat("assistant", "Rules are simple: I only tease the head — slow licks, soft sucks, swirling around the tip. You stroke the shaft, edge yourself, but you don't cum until I say. Beg nicely… or rush me and see what happens.")
        
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
        add_media("dick_tease_open1.jpg")
        add_chat("assistant", "Look at this cock… already leaking for me. I lean in close, hot breath on the tip.") 
        show_media("tongue_set3_pic4.jpg")
        
        add_chat("assistant", "My tongue flicks out, slow circle around the head, tasting your precum… then a soft kiss right on the slit.")
        show_media("tongue_set3_pic3.jpg")
        
        add_chat("assistant", "Mmm… do you like that? Keep stroking slow while I tease…")
        add_media("tease_open1.jpg")
        
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
        simulate_loading(2)
        show_media("tongue_set3_pic2.jpg")
        
        add_chat("assistant", "I wrap my lips around the tip only… gentle suck, gentle tongue swirling")
        add_narrator("Her eyes stay locked on yours, watching every twitch of your cock as you stroke.")
        simulate_loading(4)
        add_media("mkk3e2l0boxeuo(1).jpg")
                
        reason = "because you begged so sweetly like a good boy" if data["begged"] else "because you're being impatient and greedy"
        add_chat("assistant", f"I'm being extra mean with the tease {reason}… just the tip, baby.")
        
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
        add_chat("assistant", "God you're throbbing so hard… tip swollen, leaking nonstop.")
        simulate_loading(2)
        show_media("dick_tease8.jpg")
        
        add_chat("assistant", "I flick faster, suck the head softly like a lollipop, tasting every drop you give me.")
        add_narrator("Your hand is pumping the shaft… balls tight, so close but not allowed yet.")
        
        if data["impatient"]:
            add_chat("assistant", "Since you keep rushing… I pull back just enough to deny you the warmth for a few seconds. Bad boy.")
        
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
        simulate_loading(2)
        show_media("dick_tease5.jpeg")
        
        if data["edging_level"] >= 5 or data["begged"]:
            add_chat("assistant", "You've been such a good boy… edging so hard for my tongue.")
            add_chat("assistant", "Stroke faster now… I'm sucking the tip hard, tongue swirling like crazy.")
            
            if st.button("Cum for me… give me that load on my tongue"):
                simulate_loading(3)
                show_media("dick_tease8.jpeg")
                add_chat("assistant", "Yes daddy! You explode — hot ropes shooting across my tongue, lips, chin… I lap it all up greedily.")
                add_narrator("She moans softly, savoring every drop, eyes sparkling with satisfaction.")
                
                if st.button("Best prize ever… thank you baby"):
                    del st.session_state.tongue_tease
                    st.session_state.turn_state = "PRIZE_DONE"
                    st.rerun()
        else:
            add_chat("assistant", "Not yet… you're not desperate enough.")
            add_chat("assistant", "I pull my mouth away completely… no more tongue until you beg properly.")
            
            show_media("dick_tease7.jpg")
            add_chat("assistant", "Edge denied. Better luck next time, baby.")
            add_narrator("She smirks, licking her lips, leaving you throbbing and unfinished.")
            
            if st.button("Fuck… I accept the denial"):
                del st.session_state.tongue_tease
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

    # ── Ruined Orgasm Branch ──
    elif data["stage"] == "ruin":
        add_chat("assistant", "Oh no you don't… you tried to rush and cum without permission.")
        add_chat("assistant", "I pull off right as you start pulsing — ruining it completely.")
        
        simulate_loading(2)
        show_media("ruined.jpg")
        
        add_chat("assistant", "Look at that weak little dribble… all that buildup wasted. Next time obey the tease.")
        
        if st.button("Sorry baby… I'll be good next time"):
            del st.session_state.tongue_tease
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# ROAD HEAD PRIZE - Ultra-teasing, natural convo flow with typing indicators
# (Stage 3 / Pull-over safe finish removed as requested)
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    if "road_head" not in st.session_state:
        st.session_state.road_head = {
            "stage": 0,
            "risk_level": "medium",
            "control": "you"
        }
    data = st.session_state.road_head

    def show_typing(text="typing...", duration=1.8):
        placeholder = st.empty()
        placeholder.markdown(f"**{text}** 💬")
        time.sleep(duration)
        placeholder.empty()

    # -------- STAGE 0 - Slow, filthy intro + risk choice --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Road Head**")

        show_typing("fuck typing… 😈", 1.7)
        add_chat("assistant", "Fuck yes baby… you just won **Road Head** 😈")

        show_typing("Paige is typing… so bad", 2.2)
        add_chat("assistant", "Your dirty little girlfriend is gonna suck your cock the whole drive home… exactly 3 full songs on the playlist.")

        show_typing("mm typing… already hard?", 2.4)
        add_chat("assistant", "I’ll start when the first beat drops… tease you slow, then deepthroat you through every chorus… finish you right as the last song fades.")

        show_typing("risky as fuck…", 2.1)
        add_chat("assistant", "Buckle up, daddy… how risky do you want this drive to feel?")

        show_typing("choose baby…", 2.3)
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

        show_typing("engine on…", 2.0)
        add_chat("assistant", f"Engine’s running… playlist queued… 3 songs, no stopping. {risk_desc}")

        show_typing("leaning over…", 2.3)
        add_chat("assistant", "I lean over the console… unzip you sooo slow… pull your hard cock out… already throbbing and leaking for my mouth 🥵")

        show_typing("first taste…", 2.5)
        add_media("car2.jpeg")
        add_chat("assistant", "You drive… I suck. Who controls the pace, daddy?")

        show_typing("tell me…", 2.2)
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
            show_typing("your hand…", 2.1)
            add_chat("assistant", "Your hand tangled in my hair… guiding me down hard… forcing your cock deep into my throat while you keep one eye on the road.")
            show_typing("gagging typing…", 2.4)
            add_chat("assistant", "I gag a little… drool running down your shaft… but I take every inch, humming around you as the first song builds.")
        else:
            show_typing("my rhythm…", 2.2)
            add_chat("assistant", "I take full control… slow wet licks up the shaft… then swallowing you whole, bobbing to the beat of the music.")
            show_typing("tongue play…", 2.5)
            add_chat("assistant", "My tongue swirls the head between verses… sucking hard on every chorus… making you throb while you try not to swerve.")

        show_typing("mid drive…", 2.3)
        add_media("car3.png")
        add_chat("assistant", "Song 2 starting… fuck you’re so close already aren’t you?")

        if data["risk_level"] == "high":
            show_typing("truck alert…", 2.6)
            add_chat("assistant", "Truck right beside us… driver could look down any second and see my lips stretched around your cock. I don’t stop — I suck harder.")
        elif data["risk_level"] == "medium":
            show_typing("car next to us…", 2.4)
            add_chat("assistant", "Car pulling up at the light… I slow just enough to tease… lips sealed tight around the tip… eyes up at you like a good girl.")

        show_typing("almost there…", 2.8)
        add_media("car4.jpg")
        add_chat("assistant", "Last song… you’re throbbing so hard in my mouth. What do we do, daddy?")

        c1, c2 = st.columns(2)  # Only two options now (removed pull-over)
        if c1.button("Risky finish – cum in my mouth while driving", key="risky_finish"):
            data["stage"] = "risky_finish"
            st.rerun()
        if c2.button("Edge home – no cumming until we’re in the driveway", key="edge_home"):
            data["stage"] = "edge_home"
            st.rerun()

    # -------- ENDINGS (No safe pull-over anymore) --------
    elif data["stage"] == "risky_finish":
        show_typing("no stopping…", 2.2)
        add_chat("assistant", "No pulling over… I deepthroat you through the final chorus, throat milking every pulse as you cum hard.")
        show_typing("so risky…", 2.6)
        add_chat("assistant", "You grip the wheel tight, moaning loud… shooting thick ropes straight down my throat while cars zoom by… risky as fuck and so fucking hot.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    elif data["stage"] == "edge_home":
        show_typing("teasing more…", 2.3)
        add_chat("assistant", "No cumming yet… I tease just the tip the rest of the way home… keeping you rock-hard and leaking.")
        show_typing("home now…", 2.4)
        add_chat("assistant", "We pull into the driveway… your cock still throbbing in my mouth… now you get the full finish inside. Saved every drop for the bedroom, daddy 🍆")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    # Global exit
    if st.button("🎰 The Exit - Save the road head for the next drive?", key="road_exit_global"):
        st.session_state.pop("road_head", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
        
# PLUG TEASE PRIZE - Ultra-teasing, natural convo flow with typing indicators
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    if "plug_tease" not in st.session_state:
        st.session_state.plug_tease = {
            "stage": 0,
            "stretch_level": None,  # "barely", "halfway", "full"
            "tease_level": 0,
            "show_reward": False
        }
    data = st.session_state.plug_tease

    def show_typing(text="typing...", duration=1.8):
        placeholder = st.empty()
        placeholder.markdown(f"**{text}** 💬")
        time.sleep(duration)
        placeholder.empty()

    # -------- STAGE 0 - Slow, filthy intro + stretch choice --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Plug Tease**")
        add_media("plug_tease_preview.jpeg")
        show_typing("mm typing… 🫦", 1.7)
        add_chat("assistant", "Mmm daddy… you won the **Plug Tease** tonight 😈")

        show_typing("Paige is typing… so naughty", 2.2)
        add_chat("assistant", "Your filthy little girlfriend is gonna lube up a nice thick butt plug…")

        show_typing("stretching already…", 2.4)
        add_chat("assistant", "and wear it for you… all day while you're at work… feeling it stretch and fill my tight ass the whole time…")

        show_typing("fuck typing…", 2.1)
        add_chat("assistant", "I'll be walking around, sitting, bending over… every little move reminding me of you…")

        show_typing("how stretched do you want me, baby?", 2.5)
        add_chat("assistant", "How stretched do you want your girl when you finally get home? 🥵")
        add_media("plug_tease_3.jpeg")
        
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
        add_media("plug_tease_4.jpeg")
        show_typing("oh fuck yes…", 1.9)
        add_chat("assistant", f"**{data['stretch_level'].capitalize()}** it is… you're so mean to me daddy 😩")

        show_typing("lube typing…", 2.3)
        add_chat("assistant", "I'm lubing it up right now… cold and slick… circling my little hole…")

        show_typing("pushing…", 2.6)
        add_chat("assistant", "Here it goes… slow… stretching me open… fuck it feels so good…")

        if data["stretch_level"] == "barely":
            show_typing("just the tip…", 2.4)
            add_chat("assistant", "Only putting it in an hour before I leave work… just enough to tease… keep me needy all day…")
        elif data["stretch_level"] == "halfway":
            show_typing("halfway in…", 2.5)
            add_chat("assistant", "Putting it in at lunch… gonna feel every inch for the rest of the afternoon… squirming in my chair…")
        elif data["stretch_level"] == "full":
            show_typing("all the way…", 2.7)
            add_chat("assistant", "Putting it in NOW… deep… full… gonna wear it the whole time until you get home… clenching around it thinking of you…")
            
        show_typing("reward tease…", 2.8)
        add_chat("assistant", "Do you want a little preview of your final reward when you finally get home and pull it out…? 👀")

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
            show_typing("here it comes…", 2.0)
            add_media("plug_teasereward.jpeg")
            show_typing("fuck typing…", 2.4)
            add_chat("assistant", "This is what you'll see when you walk in… ass plugged, spread, dripping… waiting for you to take it out and replace it with something much bigger 🍆")

            show_typing("so ready…", 2.3)
            add_chat("assistant", "I've been stretched and filled for you all day… now I'm aching for the real thing…")

        else:
            show_typing("saving it…", 2.1)
            add_chat("assistant", "Okay… I'll keep this reward hidden until you're here to see it in person…")
            show_typing("teasing more…", 2.5)
            add_chat("assistant", "Just imagine how gaped and ready it'll be after wearing it so long…")

        show_typing("prize done…", 2.2)
        add_chat("assistant", "Plug tease complete, daddy… but now I need you to come home and wreck this stretched little hole 💦")

        if st.button("Prize complete – come claim your girl now?", key="plug_finish"):
            st.session_state.pop("plug_tease", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

    # Global exit button
    if st.button("🎰 The Exit - Save some stretching for later?", key="plug_exit_global"):
        st.session_state.pop("plug_tease", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# TOY PIC - Branching version based on user's provided flow
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    if "toy_pic" not in st.session_state:
        st.session_state.toy_pic = {
            "stage": 0,
            "focus": None,
            "subchoice": None,   # for ass branch (Plug vs Toy)
            "plug_keep": None,
            "mood": "teasing"
        }
    data = st.session_state.toy_pic

    # -------- STAGE 0 - Intro + First choice: Which hole? --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Toy Pic**")
        
        add_chat("assistant", "Oh fuck baby… you won the **Toy Pic** tease 😈 Your filthy little girlfriend is gonna play with a nice toy just for you.")
        add_media("toy_butt_in5.jpeg")
        
        add_chat("assistant", "Ready to watch me fuck myself daddy?")
        add_media("toy_pic.jpeg")
        
        focuses = ["Ass", "Pusssy", "Mouth"]
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
            add_chat("assistant", "This ass?")
            add_media("in_this_ass.jpg")
            
            add_chat("assistant", "You wanna see my tiny asshole stretched and filled with what?")
            
            subchoices = ["Plug", "Toy"]
            data["subchoice"] = st.radio(
                "Choose your weapon:",
                subchoices,
                key="ass_fill_choice"
            )
            
            if st.button("Stretch me", key="ass_fill_confirm"):
                data["stage"] = 2
                st.rerun()

        elif data["focus"] == "Pusssy":
            add_chat("assistant", "In my pussy?")
            add_chat("assistant", "Now teasing my pussy with the tip… just a little getting so wet for you…")
            add_media("toy_ass3.jpeg")
            
            add_chat("assistant", "There daddy… toy sliding deep into my pussy, lips stretched around it, dripping everywhere. God it feels so good thinking of your cock")
            add_media("plug_pussy1.jpg")
            
            if st.button("Bonus for being a good boy", key="pussy_bonus"):
                data["stage"] = 3
                st.rerun()

        elif data["focus"] == "Mouth":
            add_chat("assistant", "Stretching out my mouth")
            add_media("toy_in_mouth.jpg")
            
            if st.button("Bonus for being a good boy", key="mouth_bonus"):
                data["stage"] = 3
                st.rerun()

    # -------- STAGE 2 - Ass sub-branch (Plug or Toy) --------
    elif data["stage"] == 2 and data["focus"] == "Ass":
        if data["subchoice"] == "Plug":
            add_media("tease_in_ass_plug.jpg")
            add_media("plug_in1.jpeg")
            
            add_chat("assistant", "Plug in ass, should I keep it there for you to take out?")
            
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
            add_media("tease_in_ass.jpeg")
            add_media("vibe_in_ass.jpg")
            
            add_chat("assistant", "There you go daDdy… toy sliding deep into my ass stretched around it, dripping everywhere. God it feels so good thinking of your cock instead")
            add_media("all_3_4.jpeg")
            
            if st.button("Bonus for being a good boy", key="toy_ass_bonus"):
                data["stage"] = 3
                st.rerun()

    # -------- STAGE 3 - Bonus / Final picture --------
    elif data["stage"] == 3:
        add_media("toy_in_mouth_ass.jpg")
        add_chat("assistant", "Bonus\nFor being a good boy")
        
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
    if "anal_prize" not in st.session_state:
        st.session_state.anal_prize = {
            "stage": 0,
            "prep_level": "slow", # slow / medium / rough
            "position": "doggy", # doggy / missionary / riding
            "intensity": "teasing"
        }
    data = st.session_state.anal_prize
    # ── Stage 0: Introduction & Prep Choice ──
    if data["stage"] == 0:
        add_chat("assistant", "Oh baby… you won the **Anal Fuck** prize tonight 🔥")
        add_chat("assistant", "I’ve been thinking about this… feeling you stretch my tight little ass, owning it completely.")
        add_chat("assistant", "How do you want to take me? Gentle warmup… or straight to claiming what’s yours?")
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
        simulate_loading(3)
        add_media("ass_fucked1.jpg")
        if data["prep_level"] == "slow":
            add_chat("assistant", "Warm lube drips slowly down my crack… so slick and shiny.")
            add_chat("assistant", "Your fingers circle my tight rim, teasing… then one slips in gently.")
            add_chat("assistant", "I moan low and soft, pushing back, letting you open me up inch by careful inch…")
        elif data["prep_level"] == "medium":
            add_chat("assistant", "Thick lube coats everything… then two fingers push in at once.")
            add_chat("assistant", "The stretch burns so good… I gasp, rocking back, already hungry for more.")
        else: # rough
            add_chat("assistant", "No teasing tonight… lube poured straight on, then two fingers shoved deep.")
            add_chat("assistant", "I cry out — sharp and needy — ass clenching tight around you as you stretch me fast and dirty.")
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
        simulate_loading(4)
        add_media("ass_fucked9.jpg")
        add_chat("assistant", "You line up… thick head pressing against my slick, ready hole…")
        if data["prep_level"] == "slow":
            add_chat("assistant", "…and ease in so slowly… every ridge stretching me open again, filling me so deep I lose my breath.")
            add_chat("assistant", "I whimper long and shaky, ass fluttering around you.")
        elif data["prep_level"] == "medium":
            add_chat("assistant", "You slide in steady… one smooth, deep stroke until your hips slap against me.")
            add_chat("assistant", "Fuck… so full… I’m trembling, clenching hard around every thick inch.")
        else: # rough
            add_chat("assistant", "No patience — you slam in hard, burying yourself to the hilt in one brutal thrust.")
            add_chat("assistant", "I scream into the sheets — pain and pleasure exploding — ass gripping you like it never wants to let go.")
        add_chat("assistant", "Then you start fucking me…")
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
        add_media("ass_fucked9.jpg")
        if data["intensity"] == "slow":
            add_chat("assistant", "Long, deliberate thrusts… pulling almost out, then sinking back in so deep.")
            add_chat("assistant", "I’m moaning constantly… ass fluttering, begging with my body for you to stay inside.")
        elif data["intensity"] == "medium":
            add_chat("assistant", "The rhythm builds… wet slapping filling the room, my ass bouncing with every thrust.")
            add_chat("assistant", "I grip the sheets, pushing back, taking you harder, deeper… completely lost.")
        else: # hard
            add_chat("assistant", "You fuck me mercilessly — hard, fast, relentless. Skin slapping loud. Body jolting.")
            add_chat("assistant", "I scream your name, ass clenching so tight it hurts so fucking good… owned.")
        add_narrator("You’re throbbing hard… right on the edge…")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cum deep inside my ass… fill me up", key="cum_inside"):
                add_chat("assistant", "You bury yourself balls-deep one last time… and explode.")
                add_chat("assistant", "Hot, thick pulses flood my ass… I shudder hard, milking every drop while shaking beneath you.")
                add_chat("assistant", "When you pull out slow… I’m gaping, leaking your cum… ruined and grinning like your greedy little slut.")
        with col2:
            if st.button("Pull out & cum on my ass", key="cum_on"):
                add_chat("assistant", "You pull out right at the edge… stroking fast… then paint my stretched, red ass with thick ropes.")
                add_chat("assistant", "I moan at the warm splashes… reaching back to smear it around like filthy lotion.")
        add_chat("assistant", "God… my ass is throbbing, sensitive, completely marked by you. Best prize ever. 😈")
        if st.button("End Session"):
            del st.session_state.anal_prize
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# DOGGYSTYLE READY PRIZE - Ultra-teasing, interactive with typing indicators & loading
elif st.session_state.turn_state == "PRIZE_DOGGY_STYLE_READY":
    if "doggy_style_ready" not in st.session_state:
        st.session_state.doggy_style_ready = {
            "stage": 0,
            "tease_level": "panties_on",  # panties_on, panties_off, fucked
            "substage": 0
        }
    data = st.session_state.doggy_style_ready

    def show_typing(text="typing...", duration=1.8):
        placeholder = st.empty()
        placeholder.markdown(f"**{text}** 💬")
        time.sleep(duration)
        placeholder.empty()

    def load_picture(image_name, delay=2.5):
        """Simulate realistic loading with spinner"""
        with st.spinner("Loading your filthy doggy pic... 🍑"):
            time.sleep(delay)
        add_media(image_name)

    # -------- STAGE 0 - Intro + Tease + Starting Tease Level --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Doggy style Ready**")

        show_typing("mm typing… ass up", 1.7)
        add_chat("assistant", "Daddy… you won **Doggy style Ready** 😩🍑")

        show_typing("Paige is typing… presenting", 2.3)
        add_chat("assistant", "I'm on all fours… ass high… back arched… waiting for you to come take me from behind… full body exposed and dripping for your cock.")

        show_typing("teasing first…", 2.1)
        load_picture("dogg_style_tease.jpg", 3.2)
        add_chat("assistant", "Look at this view… ass up high… cheeks spread just enough… pussy already glistening… ready to be claimed.")

        show_typing("how do you want to start?", 2.5)
        add_chat("assistant", "How should I tease you before you fuck me doggy, daddy? Choose how exposed you want me…")

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
        show_typing("on my knees…", 1.9)
        add_chat("assistant", "I'm on all fours… ass presented perfectly… waiting for your hands… your cock… your everything.")

        if data["tease_level"] == "grab":
            load_picture("dogg_style_grab.jpg", 3.3)
            add_chat("assistant", "You grab my hips hard… fingers digging in… pulling me back… panties still covering… teasing the outline of my pussy through the fabric.")
            show_typing("rubbing…", 2.4)
            add_chat("assistant", "I push back against your grip… moaning… panties getting soaked… begging you to pull them aside…")

        elif data["tease_level"] == "panties_on":
            load_picture("dogg_style_tease_panties.jpg", 3.1)
            add_chat("assistant", "Panties still on… you trace the edge… pulling them tight… fabric wedged between my lips… making me whimper.")
            load_picture("dogg_style_tease_panties3.jpg", 3.0)
            add_chat("assistant", "Another angle… ass arched higher… panties stretched… pussy outline so clear… dripping through the thin material.")

        elif data["tease_level"] == "panties_off":
            load_picture("dogg_style_tease_panties_fucked.jpg", 3.4)
            add_chat("assistant", "Panties yanked aside… or completely off… my pussy and ass fully exposed… hole twitching… ready for you to slam in.")

        show_typing("ready for more…", 2.6)
        add_chat("assistant", "Fuck me doggy daddy… slide in slow or pound hard… make me scream into the pillow…")

        c1, c2 = st.columns(2)
        if c1.button("Tease longer – keep the panties on & edge me", key="longer_tease"):
            data["tease_level"] = "panties_on"
            add_chat("assistant", "Yes… keep teasing… rubbing my clit through the fabric… making me soak them more… edging me stupid 😭")
            data["substage"] += 1
            st.rerun()
        if c2.button("Fuck me now – panties off & pound", key="fuck_now"):
            data["stage"] = 2
            st.rerun()

    # -------- STAGE 2 - Full Fucking & Climax --------
    elif data["stage"] == 2:
        show_typing("inside me…", 2.2)
        load_picture("dogg_style_tease_panties_fucked.jpg", 3.3)
        add_chat("assistant", "You finally slam in… panties ripped aside… cock stretching my pussy deep… ass bouncing with every thrust.")

        show_typing("pounding hard…", 2.8)
        add_chat("assistant", "Gripping my hips… pulling me back onto you… full force… my moans muffled in the sheets… ass rippling…")

        show_typing("close up…", 2.5)
        add_chat("assistant", "You go deeper… harder… making my whole body shake… pussy clenching tight around you…")

        show_typing("cumming soon…", 2.6)
        add_chat("assistant", "I'm right there daddy… fuck me through it… fill me up…")

        load_picture("dogg_style_grab.jpg", 3.1)
        add_chat("assistant", "Final grip… you hold me tight… exploding deep inside… hot cum flooding my pussy… dripping down my thighs…")

        show_typing("aftermath…", 2.4)
        add_chat("assistant", "Doggystyle Ready prize complete… ass still up… pussy dripping your cum… body trembling… waiting for round two whenever you want 🍑💦")

        if st.button("Doggy style prize complete – come take me again soon?", key="dogg_finish"):
            st.session_state.pop("doggy_style_ready", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

    # Global exit
    if st.button("🎰 The Exit - Save this doggy ass for later?", key="dogg_exit_global"):
        st.session_state.pop("doggy_style_ready", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
                    
# SLAVE DAY PRIZE - HIGHLY INTERACTIVE with substages, choices, and progression
elif st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    if "slave_day" not in st.session_state:
        st.session_state.slave_day = {
            "stage": 0,
            "service_choice": None,
            "substage": 0,
            "punishment_points": 0,  # increases if "misbehave"
            "used_holes": []  # tracks which holes used for doll path
        }
    data = st.session_state.slave_day

    def show_typing(text="typing...", duration=1.8):
        placeholder = st.empty()
        placeholder.markdown(f"**{text}** 💬")
        time.sleep(duration)
        placeholder.empty()

    # -------- STAGE 0 - Intro + First Service Choice --------
    if data["stage"] == 0:
        st.markdown("🏦 The Bank  \nAdmin Override  \n🎰 The Exit  \n\n🥈 **WINNER: Slave Day**")

        show_typing("mm typing… your property", 1.7)
        add_chat("assistant", "… you’ve won **Slave Day** 🖤😩")

        show_typing("Paige is typing… no limits", 2.4)
        add_chat("assistant", "Im completely yours for the entire day… body, mouth, holes… all for your pleasure. No safewords. No refusals.")

        show_typing("kneeling already…", 2.2)
        add_chat("assistant", "I’m stripped and ready… waiting for your first desire. How do you want your little slut?")

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
        show_typing("yes Master…", 1.9)

        if data["service_choice"] == "door":
            if data["substage"] == 0:
                add_chat("assistant", "Door opens… I’m on my knees right there, pants down, no panties, mouth wide, tongue out, hands behind back.")
                add_media("slave14.jpeg")
                add_chat("assistant", "You step in… I crawl forward, unzip you with my teeth… take your cock straight to the back of my throat.")
                add_media("slave66.jpeg")
                add_chat("assistant", "Mascara already running… gagging quietly… drool dripping on the floor… welcome home, my love.")
                data["substage"] = 1
                st.rerun()

            elif data["substage"] == 1:
                add_chat("assistant", "You grab my hair… fuck my face harder… I choke, eyes watering… throat bulging.")
                add_media("full_throat_bury_cum.jpg")
                add_chat("assistant", "You hold me down… unload thick ropes straight down my throat… I swallow every drop, not spilling a single one.")
                add_chat("assistant", "What next? Keep me on my knees or drag me deeper into the house?")
                c1, c2 = st.columns(2)
                if c1.button("Keep on knees – more throat training", key="more_throat"):
                    data["substage"] = 2
                    st.rerun()
                if c2.button("Move to floor- bend over", key="move_floor"):
                    data["stage"] = 2
                    st.rerun()

        elif data["service_choice"] == "gaming":
            if data["substage"] == 0:
                add_chat("assistant", "You sit… I before you…pants down, ass up, no panties… lips wrap around your cock instantly.")
                add_media("gaming1.jpg")
                add_chat("assistant", "Your POV… slow deep bobs… tongue flat against the underside… keeping perfectly quiet.")
                data["substage"] = 1
                st.rerun()

            elif data["substage"] == 1:
                add_media("gaming3.jpg")
                add_chat("assistant", "Mid-game… I speed up on your wins, slow on losses. throat milking you between rounds.")
                add_media("slave66.jpeg")
                add_chat("assistant", "Hours later… mascara streaked… jaw aching… but I never stop… swallowing load after load.")
                add_chat("assistant", "You’re in a ranked match… do I edge you or make you cum now?")
                c1, c2 = st.columns(2)
                if c1.button("Edge me – keep me throbbing for hours", key="edge_gaming"):
                    data["punishment_points"] += 1  # teasing Master
                    add_chat("assistant", "Yes Master… I slow to torturous licks… edging you painfully… whimpering softly, like a pet.")
                    data["substage"] = 2
                    st.rerun()
                if c2.button("Make me cum now – fill my throat mid-game", key="cum_gaming"):
                    add_chat("assistant", "I deepthroat hard… you explode down my throat while you clutch the phone… I swallow it all.")
                    data["stage"] = 2
                    st.rerun()

        elif data["service_choice"] == "fantasy":
            if data["substage"] == 0:
                add_chat("assistant", "I'm your living fantasy … naked, plugged, ready for any use.")
                add_media("slave11.jpeg")
                add_chat("assistant", "Legs spread wide… thick plug stretching my ass… waiting for you to decide which hole first.")
                data["substage"] = 1
                st.rerun()

            elif data["substage"] == 1:
                add_chat("assistant", "You pull the plug… slam into my ass… then switch to pussy… then back… using me your own slut.")
                add_media("slave13.jpeg")
                add_media("slave77.jpeg")
                add_chat("assistant", "Doggy anal… then standing pussy fuck… tied and helpless.")
                add_media("slave99.jpeg")
                add_chat("assistant", "Squatting on your cock… gravity forcing every inch… moaning like a good slave.")
                add_media("slave88.jpeg")
                add_chat("assistant", "Which hole next? Or should I be punished for moaning too loud?")
                c1, c2, c3 = st.columns(3)
                if c1.button("Ass again – deeper", key="ass_again"):
                    data["used_holes"].append("ass")
                    add_chat("assistant", "Yes… stretch my ass more… more...")
                    data["substage"] = 2
                    st.rerun()
                if c2.button("Pussy – fill me up", key="pussy_fill"):
                    data["used_holes"].append("pussy")
                    add_chat("assistant", "Pound my pussy raw. ..")
                    data["substage"] = 2
                    st.rerun()
                if c3.button("Punish me – spank,  choke", key="punish"):
                    data["punishment_points"] += 2
                    add_chat("assistant", "Thank you for correcting your slave… I deserve it… do it again.")
                    data["substage"] = 2
                    st.rerun()

            elif data["substage"] == 2:
                add_media("slave44.jpeg")
                add_chat("assistant", "End of day… naked, tied spread-eagle… looking delirious… eyes rolled back… completely fucked-out and dripping.")
                add_media("slave55.jpeg")
                add_media("slave90.jpeg")
                add_chat("assistant", "Your slave is marked, sore, ruined… thank you for fucking me. all day.")

        # Final interactive close
        show_typing("end of service…", 2.6)
        add_chat("assistant", "Slave Day complete… your toy is exhausted but still yours whenever you want 🖤")
        if data["punishment_points"] > 2:
            add_chat("assistant", "…and I've earned punishment tomorrow for being such a needy slut.")

        if st.button("End Slave Day – your slave awaits tomorrow’s orders", key="slave_finish_interactive"):
            st.session_state.pop("slave_day", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

    # Global exit
    if st.button("🎰 The Exit - Pause my slavery for now?", key="slave_exit_interactive"):
        st.session_state.pop("slave_day", None)
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
# ... (Your last prize script ends above this) ...

# ==========================================
#       ENDING & CLEANUP
# ==========================================
# CRITICAL: This line must be touching the LEFT edge. Do NOT indent it.
elif st.session_state.turn_state == "PRIZE_DONE":
    st.success("✅ Session Complete. Prize Claimed & Saved.")
    
    # Create 3 Columns for the buttons you asked for
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














































