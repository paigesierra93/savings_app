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
#       PART 3: HELPER FUNCTIONS
# ==========================================
def add_chat(role, content):
    st.session_state.history.append({"type": "chat", "role": role, "content": content})

def add_narrator(content):
    st.session_state.history.append({"type": "narrator", "content": content})

def add_media(filepath, media_type="image"):
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

def get_smart_response(): 
    return random.choice([
        "Good boy. You kept the money safe.",
        "Daddy's making moves! Keep stacking cash.",
        "My baby is saving to fuck my mouth in his own home.",
        "Good job, one step closer to a blow job in the living room."
    ])

def get_ticket_save_response():
    return random.choice([
        "I was really hoping to get my mouth fucked...",
        "I was dying for you to fuck my ass...",
        "Was really hoping to meet you at the door on my knees..."
    ])

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
        prizes = ["Bend Over", "Flash Me", "Dick Rub", "Jackoff Pass", "No Panties", "Shower Show"]
        win = spin_animation("Bronze", prizes)
        add_chat("assistant", f"🥉 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

elif st.session_state.turn_state == "SPIN_SILVER":
    if st.session_state.data["tickets"] >= 50:
        st.session_state.data["tickets"] -= 50; save_data(st.session_state.data)
        prizes = ["Massage", "Toy Pic", "Lick Pussy", "Nude Pic", "Tongue Tease", "Road Head", "Plug Tease"]
        win = spin_animation("Silver", prizes)
        add_chat("assistant", f"🥈 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

elif st.session_state.turn_state == "SPIN_GOLD":
    if st.session_state.data["tickets"] >= 100:
        st.session_state.data["tickets"] -= 100; save_data(st.session_state.data)
        prizes = ["Anal Fuck", "All 3 Holes", "Slave Day", "Creampie Claiming", "Upside Down Throat Fuck", "Romantic Fantasy", "Doggy Style Ready"]
        win = spin_animation("Gold", prizes)
        add_chat("assistant", f"👑 JACKPOT: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

# ==========================================
#       PRIZE SCRIPTS (EXTENDED CUT)
# ==========================================

# --- BEND OVER ---
elif st.session_state.turn_state == "PRIZE_BEND_OVER":
    add_chat("assistant", "Congrats! You’ve won “BEND OVER”")
    if st.button("What does that mean?"):
        add_chat("user", "What does that mean?")
        simulate_typing(3)
        add_chat("assistant", "This is where you finally get to bend over in front of me….sound fun?")
        st.session_state.turn_state = "PRIZE_BEND_OVER_JOKE"; st.rerun()

elif st.session_state.turn_state == "PRIZE_BEND_OVER_JOKE":
    add_chat("assistant", "This is where you finally get to bend over in front of me….sound fun?")
    if st.button("What?"):
        add_chat("user", "What?")
        simulate_typing(2)
        add_chat("assistant", "Just kidding. Lol….its pretty much exactly how it sounds. Nothing fancy. You just say 'bend over' and I’ll bend over really slowly right in front of you.")
        simulate_typing(2)
        add_narrator("Make sure I’m wearing something extra see through…or nothing at all.")
        add_chat("assistant", "But remember baby, you can look, but no touchy. Ok?")
        simulate_loading(3.5); add_media("bend_over_full_spread.jpeg")
        st.session_state.turn_state = "PRIZE_BEND_OVER_1"; st.rerun()

elif st.session_state.turn_state == "PRIZE_BEND_OVER_1":
    if st.button("Show me."):
        add_chat("user", "Show me.")
        simulate_typing(3)
        add_chat("assistant", "Mmm… like this?")
        simulate_loading(4); add_media("bend_over_skirt_hike_tease.jpeg")
        add_chat("assistant", "It looks like I’ve wet myself huh?")
        simulate_typing(3)      
        add_chat("assistant", "God I want you inside… but not yet. Save up for Silver, baby.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- FLASH ME ---
elif st.session_state.turn_state == "PRIZE_FLASH_ME":
    add_chat("assistant", "Congrats! You’ve won “Flash!”")
    if st.button("I’m pretty sure I know what this means…"):
        add_chat("user", "I’m pretty sure I know what this means…")
        simulate_typing(2)
        add_chat("assistant", "Well maybe not... there's a little twist.") 
        st.session_state.turn_state = "PRIZE_FLASH_TWIST"; st.rerun()

elif st.session_state.turn_state == "PRIZE_FLASH_TWIST":
    add_chat("assistant", "Well maybe not... there's a little twist.") 
    if st.button("Oh, yeah?"):
        add_chat("user", "Oh, yeah?")
        simulate_typing(3)
        add_chat("assistant", "Just say the word, or give me a nod, and I'll flash you my tits... OR... should I sit on your lap?")
        st.session_state.turn_state = "PRIZE_FLASH_CHOICE"; st.rerun()

elif st.session_state.turn_state == "PRIZE_FLASH_CHOICE":
    c1, c2 = st.columns(2)
    if c1.button("Show me your tits"):
        add_chat("user", "Show me your tits.")
        simulate_loading(4); add_media("tit_flash1.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
    if c2.button("Show me your pussy"):
        add_chat("user", "Show me your pussy.")
        simulate_loading(4); add_media("pussy_flash1.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- DICK RUB ---
elif st.session_state.turn_state == "PRIZE_DICK_RUB":
    add_chat("assistant", "Congrats! You’ve won “DICK RUB!”")
    simulate_typing(2)
    add_chat("assistant", "A sensual cock tease without actually touching that throbbing piece of heaven.")
    if st.button("I can handle the restraint"):
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- JACKOFF PASS ---
elif st.session_state.turn_state == "PRIZE_JACKOFF_PASS":
    add_chat("assistant", "Congrats! You’ve won a “Bathroom Jackoff Pass!”")
    simulate_typing(2)
    add_chat("assistant", "That means you get fifteen luxurious minutes of alone time.")
    if st.button("Is that it?"):
        st.session_state.turn_state = "PRIZE_JACKOFF_FUN"; st.rerun()

elif st.session_state.turn_state == "PRIZE_JACKOFF_FUN":
    add_chat("assistant", "But here's the fun part…")
    c1, c2 = st.columns(2)
    if c1.button("There's a fun part?"):
        add_chat("assistant", "Not really… I’m not helping. I’m not watching.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
    if c2.button("I know there is no fun part"):
        add_chat("assistant", "You're right…. Here's what you could have won..")
        simulate_loading(4); add_media("all_prize1.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- NO PANTIES ---
elif st.session_state.turn_state == "PRIZE_NO_PANTIES":
    add_chat("assistant", "🥈 WINNER: NO PANTIES ALL DAY")
    if st.button("Explain..."):
        simulate_typing(3)
        add_chat("assistant", "It's pretty self explanatory.. I wear no panties all day.")
        simulate_loading(2); add_media("no_panties1.jpeg")
        st.session_state.turn_state = "PRIZE_NO_PANTIES_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_NO_PANTIES_2":
    if st.button("Show me more"):
        simulate_loading(3); add_media("no_panties2.jpeg")
        simulate_typing(3)
        add_chat("assistant", "Rules are simple, baby. You get to verify.")
        simulate_loading(4); add_media("no_panties3.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("My pupils dilate, voice dropping to a sultry purr.")
    add_chat("assistant", "Private shower show… but how much tease, how much touch you get after… your call.")
    simulate_loading(4); add_media("shower.jpeg")
    
    tease_level = st.radio("Tease intensity:", ["Visual Only (Cruel)", "Denial & Begging Game"], key="shower_tease_level")
    if st.button("Start the show", key="shower_start"):
        st.session_state.shower_choice = tease_level
        st.session_state.turn_state = "PRIZE_SHOWER_ACTION"; st.rerun()

elif st.session_state.turn_state == "PRIZE_SHOWER_ACTION":
    simulate_loading(4); add_media("close_up_shower1.jpeg")
    if st.session_state.shower_choice == "Visual Only (Cruel)":
        add_chat("assistant", "I wash slowly, ignoring you completely.")
    else:
        add_chat("assistant", "I touch everywhere except where I need it most…")

    add_chat("assistant", "Water's turning off... what happens when I step out?")
    after_choice = st.radio("Reward?", ["Lick me dry", "Let me cum on your fingers", "Deny me completely"])
    
    if st.button("Water off… Step out", key="shower_end"):
        simulate_loading(3); add_media("shower_towel2.jpeg")
        if "Lick" in after_choice: add_chat("assistant", "Come here… tongue or cock.")
        elif "fingers" in after_choice: add_chat("assistant", "Finger me hard until I squirt.")
        else: add_chat("assistant", "You leave me edged and trembling… cruel.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- MASSAGE (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_MASSAGE":
    if "tension" not in st.session_state: st.session_state.tension = 0
    add_chat("assistant", "YOU WON: 10-Minute Tease Massage (No full release allowed) 🔥")
    simulate_typing(2)
    add_chat("assistant", "Well well… looks like someone’s getting spoiled tonight. 10 full minutes. Warm oil.")
    simulate_loading(2); add_media("oiled1.jpeg")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Shirtless… right now"):
        simulate_loading(3); add_media("shirtless_oil.jpeg")
        st.session_state.turn_state = "MASSAGE_POS"; st.rerun()
    if c2.button("Keep shirt on"):
        add_chat("assistant", "Playing hard to get? I’ll just have to peel it off you slowly then…")
        st.session_state.turn_state = "MASSAGE_POS"; st.rerun()
    if c3.button("Surprise me"):
        add_chat("assistant", "Oh you want a surprise? Dangerous game.")
        st.session_state.turn_state = "MASSAGE_POS"; st.rerun()

elif st.session_state.turn_state == "MASSAGE_POS":
    add_chat("assistant", "Starting now. Face down. Relax… or try to.")
    c1, c2 = st.columns(2)
    if c1.button("Hips raised"):
        st.session_state.tension += 2
        simulate_loading(3); add_media("massage_back_arch.jpeg")
        st.session_state.turn_state = "MASSAGE_LOOP_1"; st.rerun()
    if c2.button("Lying flat"):
        st.session_state.tension += 1
        st.session_state.turn_state = "MASSAGE_LOOP_1"; st.rerun()

elif st.session_state.turn_state == "MASSAGE_LOOP_1":
    add_chat("assistant", "Shoulders first… deep, slow circles. Feel that?")
    add_narrator("Warm oil drips down your sides… then lower.")
    if st.button("Beg for lower"):
        add_chat("assistant", "Good boy… using your words. More oil… dripping… right where you’re aching.")
        st.session_state.turn_state = "MASSAGE_END"; st.rerun()
    if st.button("Stay silent"):
        add_chat("assistant", "Staying quiet? I’ll just have to make you louder…")
        st.session_state.turn_state = "MASSAGE_END"; st.rerun()

elif st.session_state.turn_state == "MASSAGE_END":
    add_chat("assistant", "One minute left… and you’re a mess already.")
    simulate_loading(3); add_media("trembling_hands.jpeg")
    simulate_typing(3)
    add_chat("assistant", "*Beep.* Timer's up. No release today, baby. House rules.")
    st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- TONGUE TEASE (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    if "tongue_tease" not in st.session_state:
        st.session_state.tongue_tease = {"stage": 0, "edging_level": 0, "begged": False, "impatient": False}
    data = st.session_state.tongue_tease

    if data["stage"] == 0:
        add_chat("assistant", "Rules are simple: you stroke exactly how I tell you… and you **don't cum** until I say so.")
        c1, c2 = st.columns([1,3])
        if c1.button("Yes Ma'am", key="obey_start"): data["stage"] = 1; st.rerun()
        if c2.button("I'm already so hard…", key="impatient_start"): data["impatient"] = True; data["stage"] = 1; st.rerun()

    elif data["stage"] == 1:
        simulate_loading(2); add_media("tease1_close.jpeg")
        add_chat("assistant", "Feel that? Just my hot breath… dripping anticipation…")
        if st.button("Let me feel your tongue", key="first_beg"): data["begged"] = True; data["edging_level"] += 2; data["stage"] = 2; st.rerun()
        if st.button("I can't wait – faster", key="rush"): data["impatient"] = True; data["edging_level"] += 1; data["stage"] = 2; st.rerun()

    elif data["stage"] == 2:
        simulate_loading(2); add_media("tease2_tongue_tip.jpeg")
        add_chat("assistant", "One slow, cruel flick across your slit… tasting how desperate you are.")
        c1, c2, c3 = st.columns(3)
        if c1.button("More… please swirl", key="ask_swirl"): data["edging_level"] += 2; data["stage"] = 3; st.rerun()
        if c2.button("Keep teasing tip", key="tip_only"): data["edging_level"] += 1; data["stage"] = 3; st.rerun()
        if c3.button("Need full tongue", key="demand_full"): data["impatient"] = True; data["edging_level"] += 3; data["stage"] = 3; st.rerun()

    elif data["stage"] == 3:
        add_chat("assistant", "Good… now stroke faster while I work.")
        simulate_loading(2); add_media("tease3_swirl_slow.gif")
        c1, c2, c3 = st.columns(3)
        if c1.button("Beg: Please let me cum", key="big_beg"): data["begged"] = True; data["edging_level"] += 4; data["stage"] = 4; st.rerun()
        if c2.button("Hold… I'll be good", key="try_hold"): data["edging_level"] += 2; data["stage"] = 4; st.rerun()
        if c3.button("Fuck it – I'm cumming", key="break"): data["stage"] = "ruin"; st.rerun()

    elif data["stage"] == 4:
        simulate_loading(2); add_media("tease4_mouth_open_ready.jpeg")
        if data["edging_level"] >= 5 or data["begged"]:
            add_chat("assistant", "That's it… you've suffered so prettily. Open mouth… tongue out… give it to me **now**.")
            if st.button("RELEASE"):
                simulate_loading(3); add_media("tease5_finish_on_tongue.jpeg")
                add_chat("assistant", "Mmm… good boy. Such a big load for me.")
                if st.button("Finish"): del st.session_state.tongue_tease; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
        else:
            add_chat("assistant", "**Stop stroking.** Hands off. Ruined orgasm.")
            if st.button("Accept Fate"): del st.session_state.tongue_tease; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

    elif data["stage"] == "ruin":
        add_media("ruin_moment.jpeg"); add_chat("assistant", "Look how weak that was. That's what happens when you disobey.")
        if st.button("Apologize"): del st.session_state.tongue_tease; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ROAD HEAD (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    if "road_head" not in st.session_state: st.session_state.road_head = {"stage": 0, "risk_level": "medium", "control": "you"}
    data = st.session_state.road_head

    if data["stage"] == 0:
        add_chat("assistant", "Road head. How risky do you want to play tonight?")
        cols = st.columns(3)
        if cols[0].button("Low risk", key="risk_low"): data["risk_level"] = "low"; data["stage"] = 1; st.rerun()
        if cols[1].button("Medium", key="risk_medium"): data["risk_level"] = "medium"; data["stage"] = 1; st.rerun()
        if cols[2].button("High", key="risk_high"): data["risk_level"] = "high"; data["stage"] = 1; st.rerun()

    elif data["stage"] == 1:
        add_chat("assistant", "Engine hums. I lean over the center console… eyes flicking up to yours.")
        simulate_loading(2); add_media("road_head_start.jpg") 
        c1, c2 = st.columns(2)
        if c1.button("You guide my head", key="control_you"): data["control"] = "you"; data["stage"] = 2; st.rerun()
        if c2.button("I take control (Tease)", key="control_me"): data["control"] = "me"; data["stage"] = 2; st.rerun()

    elif data["stage"] == 2:
        simulate_loading(2); add_media("road_head_mid.gif") 
        if data["risk_level"] == "high": add_chat("assistant", "Truck next to us… driver glances over… I don't stop.")
        add_chat("assistant", "You're throbbing so hard… so close…")
        c1, c2, c3 = st.columns(3)
        if c1.button("Pull over & Finish", key="pull_over"): data["stage"] = 3; st.rerun()
        if c2.button("Finish Driving (Risky)", key="while_driving"): data["stage"] = "risky_finish"; st.rerun()
        if c3.button("Edge until Home", key="edge_home"): data["stage"] = "edge_home"; st.rerun()

    elif data["stage"] == 3:
        add_media("road_head_finish_safe.jpg"); add_chat("assistant", "Tires crunch on gravel… car in park. Both hands free now… I finish you properly.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
    elif data["stage"] == "risky_finish":
        add_chat("assistant", "Right there on the highway… I swallow everything while you fight to keep the car straight.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
    elif data["stage"] == "edge_home":
        add_chat("assistant", "I bring you right to the edge… then stop. Again. And again.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- PLUG TEASE (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    if "plug_tease" not in st.session_state: st.session_state.plug_tease = {"stage": 0, "size_chosen": "small", "tease_level": 0}
    data = st.session_state.plug_tease

    if data["stage"] == 0:
        add_chat("assistant", "Thinking about being filled… Which one should I wear for you today?")
        c1, c2, c3 = st.columns(3)
        if c1.button("Small", key="plug_small"): data["size_chosen"] = "small"; data["stage"] = 1; st.rerun()
        if c2.button("Medium", key="plug_medium"): data["size_chosen"] = "medium"; data["stage"] = 1; st.rerun()
        if c3.button("Large", key="plug_large"): data["size_chosen"] = "large"; data["stage"] = 1; st.rerun()

    elif data["stage"] == 1:
        simulate_loading(3); add_media("plug_insertion_slow.gif") 
        add_chat("assistant", "It's in… seated deep. Every tiny shift makes me clench around it.")
        c1, c2 = st.columns(2)
        if c1.button("Tell me how it feels", key="tell_feels"): data["tease_level"] += 1; data["stage"] = 2; st.rerun()
        if c2.button("Show me movement", key="see_move"): data["tease_level"] += 2; data["stage"] = 2; st.rerun()

    elif data["stage"] == 2:
        simulate_loading(2); add_media("plug_walk_tease.jpg") 
        add_chat("assistant", "Standing up… oh god, the pressure shifts instantly.")
        c1, c2, c3 = st.columns(3)
        if c1.button("Beg to replace it", key="beg_replace"): data["tease_level"] += 4; data["stage"] = 3; st.rerun()
        if c2.button("Keep it all day", key="keep_all_day"): data["tease_level"] += 2; data["stage"] = 3; st.rerun()
        if c3.button("Play with it now", key="play_with"): data["tease_level"] += 3; data["stage"] = 3; st.rerun()

    elif data["stage"] == 3:
        add_media("plug_final_seated.jpg")
        if data["tease_level"] >= 6: add_chat("assistant", "Mmm… when you get home... pull it out so slowly… then fill me.")
        else: add_chat("assistant", "I'll just leave it in quietly… saving the real fun for later.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- NUDE PIC (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_NUDE_PIC":
    if "nude_pic" not in st.session_state: st.session_state.nude_pic = {"stage": 0, "pose": None, "mood": "teasing"}
    data = st.session_state.nude_pic

    if data["stage"] == 0:
        add_chat("assistant", "Your very own custom nude… Pick the pose first…")
        poses = ["Ass up high", "Legs spread wide", "Tits pushed together", "Full body mirror", "On knees"]
        data["pose"] = st.radio("Pose:", poses, key="nude_pose_select")
        if st.button("Next → Focus", key="nude_pose_next"): data["stage"] = 1; st.rerun()

    elif data["stage"] == 1:
        cols = st.columns(2)
        if cols[0].button("Teasing / Playful", key="mood_tease"): data["mood"] = "teasing"; data["stage"] = 2; st.rerun()
        if cols[1].button("Desperate / Submissive", key="mood_desperate"): data["mood"] = "desperate"; data["stage"] = 2; st.rerun()

    elif data["stage"] == 2:
        simulate_loading(3); add_media("nude_pic1.jpeg")
        add_chat("assistant", f"Here I am… {data['pose'].split(',')[0].lower()}, skin flushed hot for you.")
        if data["mood"] == "desperate":
            simulate_loading(2); add_media("nude_desperate_extra.jpg")
            add_chat("assistant", "Eyes begging, thighs trembling, practically dripping...")
        else:
            simulate_loading(2); add_media("nude_teasing_extra.jpg")
            add_chat("assistant", "Smirking at the camera, fingers teasing myself...")
        
        if st.button("Save & Finish"): del st.session_state.nude_pic; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- SLAVE DAY (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    if "slave_day" not in st.session_state: st.session_state.slave_day = {"stage": 0, "service_type": "Under-desk", "intensity": "medium"}
    data = st.session_state.slave_day

    if data["stage"] == 0:
        add_chat("assistant", "24 hours. Your devoted slave. Your rules.")
        options = ["Under-desk service", "Complete body worship", "Rough use", "Total free use"]
        data["service_type"] = st.radio("First service, Master?", options, key="slave_radio")
        cols = st.columns(2)
        if cols[0].button("Sensual", key="int_soft"): data["intensity"] = "soft"; data["stage"] = 1; st.rerun()
        if cols[1].button("Rough", key="int_hard"): data["intensity"] = "hard"; data["stage"] = 1; st.rerun()

    elif data["stage"] == 1:
        simulate_loading(2.5)
        if "desk" in data["service_type"].lower():
            add_media("game_bj1.jpeg"); add_chat("assistant", "I crawl under your desk… lips around you while you frag.")
        elif "worship" in data["service_type"].lower():
            add_media("worship_sequence_01.jpg"); add_chat("assistant", "Starting at your feet… slow kisses, tongue between toes…")
        else:
            add_media("rough_use_start.jpg"); add_chat("assistant", "Tie me however you want… throat, ass, pussy — all yours.")
        if st.button("Continue...", key="slave_next"): data["stage"] = 2; st.rerun()

    elif data["stage"] == 2:
        add_narrator("Hours pass. I'm marked, messy, still eager.")
        add_chat("assistant", "Your slave thanks you for using her so perfectly today.")
        if st.button("Dismiss Slave"): del st.session_state.slave_day; st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ROMANTIC FANTASY (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_ROMANTIC_FANTASY":
    if "romantic_fantasy" not in st.session_state: st.session_state.romantic_fantasy = {"stage": 0, "setting": "Candlelit bedroom", "pace": "slow"}
    data = st.session_state.romantic_fantasy

    if data["stage"] == 0:
        add_chat("assistant", "Tonight is slow… sensual… every touch meant to be felt for hours.")
        settings = ["Candlelit bedroom", "Rain-lashed windows", "Crackling fireplace", "Steaming bath"]
        data["setting"] = st.radio("Our sanctuary:", settings)
        if st.button("Enter Fantasy", key="rom_enter"): data["stage"] = 1; st.rerun()

    elif data["stage"] == 1:
        simulate_loading(2); add_media("romantic_ambient_start.jpg") 
        add_chat("assistant", f"The air is heavy... {data['setting'].lower()}... warm light flickering.")
        add_chat("assistant", "You press forward… the first slow stretch makes me gasp.")
        c1, c2 = st.columns(2)
        if c1.button("Finish slow", key="rom_cum_slow"): data["pace"] = "slow"; data["stage"] = 2; st.rerun()
        if c2.button("Break hard", key="rom_cum_hard"): data["pace"] = "hard"; data["stage"] = 2; st.rerun()

    elif data["stage"] == 2:
        simulate_loading(2); add_media("romantic_climax_detail.jpg") 
        if data["pace"] == "slow": add_chat("assistant", "Pleasure rolls through us like a slow tide…")
        else: add_chat("assistant", "Everything snaps — I arch hard, crying out as my body clamps down.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ALL 3 HOLES (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    if "all_3_holes" not in st.session_state: st.session_state.all_3_holes = {"stage": 0, "main_hole": "Pussy", "ass_fill": "plug"}
    data = st.session_state.all_3_holes

    if data["stage"] == 0:
        add_chat("assistant", "Every hole filled… Tell me how you want to ruin me.")
        data["main_hole"] = st.radio("Where do you claim first?", ["Pussy", "Ass", "Throat"])
        c1, c2 = st.columns(2)
        if c1.button("Plug in Ass", key="ass_plug"): data["ass_fill"] = "plug"; data["stage"] = 1; st.rerun()
        if c2.button("Fingers in Ass", key="ass_fingers"): data["ass_fill"] = "fingers"; data["stage"] = 1; st.rerun()

    elif data["stage"] == 1:
        simulate_loading(3)
        add_chat("assistant", f"You sink into my {data['main_hole'].lower()}... and then the second invasion...")
        if data["ass_fill"] == "plug": add_media("plug_stretch_triple.jpg"); add_chat("assistant", "Cold lube, then the blunt, heavy plug.")
        else: add_chat("assistant", "Your fingers slide in beside the main stretch.")
        if st.button("Fill mouth too", key="fill_mouth"): data["stage"] = 2; st.rerun()

    elif data["stage"] == 2:
        simulate_loading(3); add_media("all_three_filled_extreme.jpg") 
        add_chat("assistant", "All three… stuffed so full I can barely breathe.")
        if st.button("Finish… flood one", key="triple_finish"):
            simulate_loading(3); add_media("triple_climax_messy.jpg")
            add_chat("assistant", "You choose your target… and let go. I collapse forward… blissfully wrecked.")
            st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- UPSIDE DOWN THROAT (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN_THROAT_FUCK":
    add_chat("assistant", "Mmm… Upside Down Throat Fuck. I’ve been thinking about this all day.")
    simulate_loading(3); add_media("kneeling_tease_lips.jpeg") 
    if st.button("Get in position"): st.session_state.turn_state = "PRIZE_UP_THROAT_START"; st.rerun()

elif st.session_state.turn_state == "PRIZE_UP_THROAT_START":
    add_chat("assistant", "I lean back, head hanging off the edge. Tell me how you want to start...")
    c1, c2, c3 = st.columns(3)
    if c1.button("Tease first"): simulate_loading(4); add_media("slow_tip_lick_closeup.jpeg"); st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"; st.rerun()
    if c2.button("Make it sloppy"): simulate_loading(4); add_media("sloppy_head_suck.jpeg"); st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"; st.rerun()
    if c3.button("Deep now"): simulate_loading(4); add_media("deep_throat_entry_slow.jpeg"); st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"; st.rerun()

elif st.session_state.turn_state == "PRIZE_UP_THROAT_FINISH":
    add_chat("assistant", "God you’re throbbing so hard in my throat… Finish me.")
    c1, c2, c3 = st.columns(3)
    if c1.button("Deep throat cum"): simulate_loading(5); add_media("full_throat_bury_cum.jpeg"); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
    if c2.button("Cum on tongue"): simulate_loading(5); add_media("tongue_cum_pool.jpeg"); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()
    if c3.button("Throat Creampie"): simulate_loading(5); add_media("throat_creampie_hold.jpeg"); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ANAL FUCK (EXTENDED) ---
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    add_chat("assistant", "Your prize is my tight asshole… but how you take it is your choice tonight.")
    style = st.radio("Claim style:", ["Slow & sensual build", "Rough & dominant", "Teasing denial first"], key="anal_style_choice")
    if st.button("Start claiming me", key="anal_begin"):
        simulate_loading(3)
        if "Slow" in style: add_media("behind_fuck1.jpeg"); add_chat("assistant", "I arch slowly... You sink all the way… slow, deep strokes.")
        elif "Rough" in style: add_media("behind_fuck4.jpeg"); add_chat("assistant", "You slam in one brutal thrust—my scream echoes as you stretch me wide.")
        else: add_media("behind_fuck10.jpeg"); add_chat("assistant", "You circle my hole with your tip… denying me.")
        st.session_state.turn_state = "PRIZE_ANAL_FINISH"; st.rerun()

elif st.session_state.turn_state == "PRIZE_ANAL_FINISH":
    cum_choice = st.radio("Finish?", ["Cum deep inside", "Pull out & paint my ass", "Edge & deny"], key="anal_finish")
    if st.button("End it", key="anal_final"):
        simulate_loading(3.5)
        if "inside" in cum_choice: add_media("ass_cum1.jpeg"); add_chat("assistant", "Yes… flood my ass… feel me clench and milk every pulse.")
        elif "paint" in cum_choice: add_media("ass_cum4.jpeg"); add_chat("assistant", "Pull out… hot ropes across my cheeks… I shiver as it drips.")
        else: add_chat("assistant", "You stop just before… leaving me quivering, empty.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- TOY PIC ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    add_chat("assistant", "Pick toy, hole, depth… I'll snap it exactly how you command.")
    toy_type = st.radio("Toy?", ["Vibrating bullet", "Thick dildo", "Household object"], key="toy_type_choice")
    hole = st.radio("Hole?", ["Pussy", "Ass"], key="toy_hole")
    if st.button("Insert & photograph", key="toy_snap"):
        simulate_loading(4); add_media("toy_pic.jpeg")
        add_chat("assistant", f"{toy_type} in my {hole.lower()}… all the way deep.")
        if st.button("Show final pic", key="toy_final"): add_media("toy_ass1.jpeg"); st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- LICK PUSSY ---
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    add_chat("assistant", "Worship me with that mouth…")
    if st.button("Start licking", key="lick_start"):
        simulate_loading(3); add_media("pussy_lick1.jpeg")
        add_chat("assistant", "Your tongue traces lazy circles around my clit… I shiver.")
        if st.button("Make me cum", key="lick_cum"):
            add_chat("assistant", "I explode… soaking your face, chest, everything.")
            st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- DOGGY STYLE ---
elif st.session_state.turn_state == "PRIZE_DOGGY_STYLE_READY":
    add_chat("assistant", "I'm staying right here on my knees, cheeks spread.")
    simulate_loading(2); add_media("doggy_style3.jpeg")
    if st.button("Fuck me now", key="doggy_now"):
        add_media("doggy_style2.jpeg"); add_chat("assistant", "Yes! Ram it in... make me scream your name.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# ==========================================
#       ENDING & CLEANUP
# ==========================================
elif st.session_state.turn_state == "PRIZE_DONE":
    st.success("Session Complete. Prizes Saved.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Return to Bank"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()
    with col2:
        if st.button("Logout"): st.session_state.history = []; st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

else:
    st.error(f"Error: Undefined state '{st.session_state.turn_state}'")
    if st.button("Reset App"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()
