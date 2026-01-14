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
        st.caption("💬 *Paige is typing...*")
    time.sleep(seconds)
    st.rerun()

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

def slow_type(text: str, speed: float = 0.04):
    """Simulates typing effect for dialogue."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()  # Newline after text

def show_typing(duration: float):
    """Displays a typing indicator."""
    print(f"\n[ 💬 P is typing... ]")
    time.sleep(duration)

def show_image(description: str):
    """Placeholder for image display simulation."""
    print(f"\n[ 📸 LOADING IMAGE: {description} ]\n")
    time.sleep(1.5)
# ==========================================
#       PART 4: DIALOGUE LISTS
# ==========================================
SMART_SAVE_RESPONSES = [
    "Good boy, Do you want a sloppy blow job in the kitchen? I want to give it to you.",
    "Good boy. You kept the money safe.",
    "That's hot. One more step closer to a giant bottle of Lube, and you and me.",
    "I think I just lost my panties. Oops.",
    "Daddy's making moves! Keep stacking cash and I'll keep arching my back.",
    "My baby is saving, saving up to fuck my mouth in his own home.",
    "Good job, one step closer to to a blow job in the middle of own living room.",
    "Way to go, You'll be fucking my ass in our own house in no time.",
    "YEAH! the screaming I'm doing now is nothing compared to the screaming I'll be doing, when we have our own house..",
    "MMM Good job, every dollar saved is one more step closer to walking through your own door, where I'm waiting for you on my knees.",
    "I like the way you save money, almost as much as I like it when you fuck my ass.",
    "Seeing you save money like that, makes me want to suck your dick.",
    "Keep saving like that and you'll be able to fill all my holes with what ever you want in no time.",
    "Time to start looking at knee pads for our new home, becuase I have a feeling I'm gonna need them.",
    "Good boy, one step closer to filling up all my holes at 1:00pm on a Sunday if you so felt like it.",
    "Daddy is being so good, I cant wait to be SO good for Daddy."
]

TICKET_SAVE_RESPONSES = [
    "I was really hoping to get my mouth fucked...",
    "I was dying for you to fuck my ass...",
    "I really wanted you to fill up all my holes with what ever you could find.",
    "I was all prepared to choke on your dick...",
    "Was really hoping to meet you at the door on my knees and my mouth open.."
]

def get_smart_response(): return random.choice(SMART_SAVE_RESPONSES)
def get_ticket_save_response(): return random.choice(TICKET_SAVE_RESPONSES)

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

# USER INPUT
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
    
    # === NEW: DIRECT CASINO ENTRY IF TICKETS EXIST ===
    if st.session_state.data["tickets"] > 0:
        st.info(f"🎟️ You have {st.session_state.data['tickets']} tickets banked.")
        if st.button("🎰 ENTER CASINO FLOOR (Skip Income)"):
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()
        st.markdown("---")
    # =================================================
    
    c1, c2, c3, c4 = st.columns(4)
    
    # PAYCHECK (WEDNESDAY ONLY)
    is_open, lock_msg = check_payday_window(admin_code)
    if is_open:
        if c1.button("💰 Full Paycheck"): st.session_state.turn_state="INPUT_PAYCHECK"; st.rerun()
    else:
        c1.warning(lock_msg)
        
    if c2.button("📱 Daily Dayforce"): st.session_state.turn_state="INPUT_DAILY"; st.rerun()
    if c3.button("💸 Side Hustle"): st.session_state.turn_state="INPUT_SIDE_HUSTLE"; st.rerun()
    if c4.button("🏦 Manage Funds"): st.session_state.turn_state="MANAGE_FUNDS"; st.rerun()

# --- 2. SIDE HUSTLE ---
elif st.session_state.turn_state == "INPUT_SIDE_HUSTLE":
    st.subheader("💸 Side Hustle Input")
    st.info("Side income gets special treatment. Huge ticket rewards for smaller amounts.")
    
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
        add_chat("assistant", "Nice hustle, baby. Spending or Saving?")
        
        st.session_state.turn_state = "CHOOSE_TIER"
        st.rerun()

# --- 3. PAYCHECK CALCULATOR ---
elif st.session_state.turn_state == "INPUT_PAYCHECK":
    st.subheader("💰 Full Paycheck Entry")
    check_amount = st.number_input("Enter Total Paycheck Amount ($):", min_value=0.0, step=10.0)
    
    if st.button("Process Paycheck"):
        add_chat("user", f"Paycheck is ${check_amount}")
        
        rent = 200.0; insurance = 80.0; loans = 100.0; blackout = 50.0
        total_deductions = rent + insurance + loans + blackout
        safe_spend = check_amount - total_deductions
        
        st.session_state.data["bridge_fund"] += blackout
        st.session_state.data["wallet_balance"] = safe_spend 
        
        if check_amount >= 601: tickets=100
        elif check_amount >= 501: tickets=50
        elif check_amount >= 450: tickets=25
        else: tickets=0
            
        st.session_state.data["tickets"] += tickets
        save_data(st.session_state.data)
        
        if safe_spend < 0:
            add_chat("assistant", f"⚠️ **SHORTAGE:** -${abs(safe_spend):.2f}. Bills are deducted, but you are in the red.")
        else:
            msg = f"✅ **PROCESSED**\n💵 Gross: ${check_amount:.2f}\n🔻 Deductions: Rent($200)+Ins($80)+Loans($100)+Blackout($50)\n💰 **SAFE TO SPEND:** ${safe_spend:.2f}\n🎟️ **TICKETS:** {tickets}"
            add_chat("assistant", msg)
            if tickets > 0:
                add_chat("assistant", "You've got tickets. Let's hit the Casino Floor.")
                st.session_state.turn_state="CHOOSE_TIER"
            else:
                add_chat("assistant", "No tickets earned. Closed for business.")
                st.session_state.turn_state="CHECK_FAIL"
        st.rerun()

# --- 4. DAILY CALCULATOR ---
elif st.session_state.turn_state == "INPUT_DAILY":
    st.subheader("📱 Daily Dayforce Avail.")
    daily_amount = st.number_input("What does Dayforce say is available? ($):", min_value=0.0, step=5.0)
    
    if st.button("Process Daily"):
        add_chat("user", f"Dayforce says ${daily_amount}")
        gas = 10.0; house = 30.0
        
        if daily_amount < (gas + house):
            add_chat("assistant", f"⚠️ **Warning:** ${daily_amount} isn't enough to cover Gas ($10) and House ($30).")
        else:
            safe_spend = daily_amount - gas - house
            st.session_state.data["tank_balance"] += house
            st.session_state.data["wallet_balance"] += safe_spend
            save_data(st.session_state.data)
            
            add_chat("assistant", get_smart_response())
            msg = f"**Daily Strategy:**\nShielded $30 (House) + $10 (Gas).\n🍔 **SAFE TO SPEND:** ${safe_spend:.2f}"
            add_chat("assistant", msg)
            add_chat("assistant", "Good job sticking to the plan. Do you want to check the Casino?")
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()

# --- 5. MANAGE FUNDS ---
elif st.session_state.turn_state == "MANAGE_FUNDS":
    st.subheader("🏦 Manage The Tank")
    st.info(f"Tank: ${st.session_state.data['tank_balance']:.2f}")
    move_amount = st.number_input("Amount ($):", min_value=0.0, step=10.0)
    c1, c2, c3 = st.columns(3)
    
    if c1.button("💸 Move to Wallet"):
        if move_amount > st.session_state.data['tank_balance']: st.error("Not enough.")
        else:
            st.session_state.data['tank_balance'] -= move_amount
            st.session_state.data['wallet_balance'] += move_amount
            save_data(st.session_state.data)
            add_chat("assistant", f"💸 ${move_amount} moved to Wallet."); st.rerun()
            
    if c2.button("🏠 Lock to House Fund"):
        if move_amount > st.session_state.data['tank_balance']: st.error("Not enough.")
        else:
            st.session_state.data['tank_balance'] -= move_amount
            st.session_state.data['house_fund'] += move_amount
            save_data(st.session_state.data)
            add_chat("assistant", get_smart_response())
            add_chat("assistant", f"🏠 Locked ${move_amount}."); st.rerun()
            
    if c3.button("Back"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

# --- 6. CASINO FLOOR (MENU) ---
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
        save_data(st.session_state.data) # Force Save
        add_chat("assistant", f"Walking away? {get_ticket_save_response()}")
        st.session_state.turn_state="WALLET_CHECK"
        st.rerun()

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
#       PRIZE SCRIPTS
# ==========================================

# Bend Over - Pure visual tease & shake (no touching from her)
elif st.session_state.turn_state == "PRIZE_BEND_OVER":
    add_chat("assistant", "Congrats! You’ve won “BEND OVER”")
    
    if st.button("What does that mean?"):
        add_chat("user", "What does that mean?")
        simulate_typing(3)
        add_chat("assistant", "This is where you finally get to bend over in front of me….sound fun?")
        st.session_state.turn_state = "PRIZE_BEND_OVER_JOKE" 
        st.rerun()

elif st.session_state.turn_state == "PRIZE_BEND_OVER_JOKE":
    # Re-display context so he knows what he is replying to
    add_chat("assistant", "This is where you finally get to bend over in front of me….sound fun?")
    
    if st.button("What?"):
        add_chat("user", "What?")
        simulate_typing(2)
        # Fixed nested quotes and typo
        add_chat("assistant", "Just kidding. Lol….its pretty much exactly how it sounds. Nothing fancy. You just say 'bend over' and I’ll bend over really slowly right in front of you.")
        simulate_typing(2)
        add_narrator("Make sure I’m wearing something extra see through…or nothing at all.")
        add_chat("assistant", "But remember baby, you can look, but no touchy. Ok?")
        simulate_typing(2)
        add_chat("assistant", "No hands from me on you, no touching back — just me presenting my ass and dripping pussy for your eyes only…like this…..")
        
        simulate_loading(3.5)
        add_media("bend_over_full_spread.jpeg")
        
        simulate_typing(3)
        add_narrator("I’m already soaked thinking about you staring…")
        st.session_state.turn_state = "PRIZE_BEND_OVER_1"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_BEND_OVER_1":
    add_chat("assistant", "Do you want to see how soaked?")
    c1, c2, c3 = st.columns(3)

    if c1.button("Show me."):
        add_chat("user", "Show me.")
        simulate_typing(3)
        add_chat("assistant", "Mmm… like this?")
        simulate_loading(4)
        add_media("bend_over_skirt_hike_tease.jpeg")
        add_chat("assistant", "It looks like I’ve wet myself huh?")
        simulate_typing(3)      
        add_chat("assistant", "God I want you inside… but not yet. Save up for Silver, baby.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()


# --- FLASH ME ---
elif st.session_state.turn_state == "PRIZE_FLASH_ME":
    add_chat("assistant", "Congrats! You’ve won “Flash!”")
    
    if st.button("I’m pretty sure I know what this means…"):
        add_chat("user", "I’m pretty sure I know what this means…")
        simulate_typing(2)
        # Fixed: Changed this to Assistant speaking, since it's her twist
        add_chat("assistant", "Well maybe not... there's a little twist.") 
        st.session_state.turn_state = "PRIZE_FLASH_TWIST"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_FLASH_TWIST":
    add_chat("assistant", "Well maybe not... there's a little twist.") 
    
    if st.button("Oh, yeah?"):
        add_chat("user", "Oh, yeah?")
        simulate_typing(3)
        add_chat("assistant", "Just say the word, or give me a nod, and I'll flash you my tits...")
        add_chat("assistant", "OR... should I sit on your lap while you're playing video games, lift up my skirt, and give you a sneak peek of what lies beneath?")
        add_chat("assistant", "Let me know what you would like more… Daddy…. Want a preview?")
        st.session_state.turn_state = "PRIZE_FLASH_CHOICE"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_FLASH_CHOICE":
    add_chat("assistant", "Want a preview?")
    
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("Show me your tits"):
            add_chat("user", "Show me your tits.")
            simulate_loading(4)
            add_media("tit_flash1.jpeg")
            simulate_typing(2)
            add_chat("assistant", "Let me know when you want the real thing.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
    with c2:
        if st.button("Show me your pussy"):
            add_chat("user", "Show me your pussy.")
            simulate_loading(4)
            add_media("pussy_flash1.jpeg")
            simulate_typing(2)
            add_chat("assistant", "Let me know when you want to see what's underneath.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()



# --- DICK RUB ---
elif st.session_state.turn_state == "PRIZE_DICK_RUB":
    add_chat("assistant", "Congrats! You’ve won “DICK RUB!”")
    simulate_typing(2)
    
    add_chat("assistant", "“Ohhh, baby… Jackoff Pass. How generous of fate.")
    
    # Fixed: You had simulate_typing trying to speak text. I changed it to add_chat.
    add_chat("assistant", "There is no picture for this one, sorry love.")
    
    # CRITICAL FIX: The button acts as a stop sign so he can read the text above.
    if st.button("I can handle the restraint"):
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()



# --- JACKOFF PASS ---
elif st.session_state.turn_state == "PRIZE_JACKOFF_PASS":
    add_chat("assistant", "Congrats! You’ve won a “Bathroom Jackoff Pass!”")
    simulate_typing(2)
    
    add_chat("assistant", "You've won a sensual cock tease without actually touching that throbbing piece of heaven tucked away comfortably deep inside your trousers. Seems like quite an exercise in self-restraint, wouldn't you say?")
    add_narrator("Dripping sympathy.")
    
    add_chat("assistant", "That means you get fifteen luxurious minutes of alone time with your right hand. No restrictions. No interruptions from me.")
    add_chat("assistant", "You can lock yourself in the bathroom... Fifteen whole minutes to stroke yourself silly thinking about what you could’ve had if that paycheck had just cracked five hundred.")
    
    # FIX: Added a button here so he can read before the page flips
    if st.button("Is that it?"):
        st.session_state.turn_state = "PRIZE_JACKOFF_FUN"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_JACKOFF_FUN":
    add_chat("assistant", "But here's the fun part…")
    
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("There's a fun part?"):
            add_chat("user", "There's a fun part?")
            simulate_typing(2)
            add_chat("assistant", "Not really… I’m not helping. I’m not watching. I’m not even in the room. You get zero audience, zero encouragement, zero pretty moans or filthy whispers in your ear. Just you, your hand, and the memory of how close you were to earning something real tonight.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
    with c2:
        if st.button("I know there is no fun part"):
            add_chat("user", "I know there is no fun part.")
            simulate_typing(2)
            add_chat("assistant", "You're right…. So go enjoy your consolation prize, handsome. Make it count. Because, trust me—you do not want to live on a steady diet of flashes and solo time.")
            
            add_chat("assistant", "Here's some material you can use, and what you could have won..")
            simulate_loading(4)
            add_media("all_prize1.jpeg")
            
            simulate_typing(2)
            add_chat("assistant", "Fifteen minutes starts whenever you want it to. Clock’s ticking. Don’t waste it thinking about me too hard… or do. Your choice. Maybe next check, I'll get to lick your dick...")
            add_narrator("Puts phone down and gets back to school work.") 
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()




# --- NO PANTIES ---
elif st.session_state.turn_state == "PRIZE_NO_PANTIES":
    add_chat("assistant", "🥈 WINNER: NO PANTIES ALL DAY")
    
    if st.button("I’m pretty sure I know what this means…"):
        add_chat("user", "I’m pretty sure I know what this means…")
        simulate_typing(3)
        add_chat("assistant", "It's pretty self explanatory.. I wear no panties all day.")
        add_narrator("My eyes flick up from my screen pupils dilating just a fraction. The corner of my mouth lifts in a slow, wicked smile.")
        
        simulate_typing(3) 
        add_chat("assistant", "Like this…")
        simulate_loading(2)
        add_media("no_panties1.jpeg")
        
        # Move to next state so the "Show me more" button appears cleanly
        st.session_state.turn_state = "PRIZE_NO_PANTIES_2"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_NO_PANTIES_2":
    # Re-show the previous image/context so it doesn't disappear
    add_chat("assistant", "Like this…")
    add_media("no_panties1.jpeg")
    
    if st.button("Show me more"):
        add_chat("user", "Show me more.")
        simulate_loading(3)
        add_media("no_panties2.jpeg")

        simulate_typing(3)
        add_chat("assistant", "I’m already getting wet just thinking about the friction against my bare skin.")
        
        simulate_typing(3)
        add_chat("assistant", "Rules are simple, baby. I wear a dress or skirt. I wear nothing underneath. You get to verify. You can check whenever you want, just slide your hand up my thigh. And trust me—")
        
        simulate_loading(4)
        add_media("no_panties3.jpeg")
        time.sleep(4) 
        
        add_chat("assistant", ".... at the grocery store… bending over to get food from the bottom shelf. No one else knows that I’m completely bare.")
        
        # Pause so he can read before finishing
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("My pupils dilate, voice dropping to a sultry purr.")
    add_chat("assistant", "Private shower show… but how much tease, how much touch you get after… your call.")
    
    simulate_loading(4)
    add_media("shower.jpeg")
    
    # Selection 1
    tease_level = st.radio("Tease intensity:", 
        ["Visual Only (Cruel)", "Denial & Begging Game"], 
        key="shower_tease_level")
    
    if st.button("Start the show", key="shower_start"):
        # Save choice and move to next stage
        st.session_state.shower_choice = tease_level
        st.session_state.turn_state = "PRIZE_SHOWER_ACTION"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_SHOWER_ACTION":
    # 1. Execute the Show based on previous choice
    simulate_loading(4)
    add_media("close_up_shower1.jpeg")
    
    if st.session_state.shower_choice == "Visual Only (Cruel)":
        add_chat("assistant", "I wash slowly, ignoring you completely. You get to watch, but you don't exist to me right now.")
    else:
        add_chat("assistant", "I touch everywhere except where I need it most… circling my clit, never quite finishing… leaving us both aching.")

    # 2. The Reward Choice
    add_chat("assistant", "Water's turning off... what happens when I step out?")
    after_choice = st.radio("Reward?", 
        ["Lick me dry", "Let me cum on your fingers", "Deny me completely"])
    
    if st.button("Water off… Step out", key="shower_end"):
        simulate_loading(3)
        add_media("shower_towel2.jpeg")
        
        if "Lick" in after_choice:
            add_chat("assistant", "Come here… tongue or cock—taste me or fill me while I'm still dripping.")
        elif "fingers" in after_choice:
            add_chat("assistant", "Finger me hard until I squirt on the tile. Don't be gentle.")
        else:
            add_chat("assistant", "You leave me edged and trembling… cruel, but so hot.")
            
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
# ==========================================
#       MASSAGE PRIZE (STREAMLIT VERSION)
# ==========================================

elif st.session_state.turn_state == "MASSAGE":
    # Initialize tension if not set
    if "tension" not in st.session_state: st.session_state.tension = 0
    
    add_chat("assistant", "YOU WON: 10-Minute Tease Massage (No full release allowed) 🔥")
    simulate_typing(2)
    add_chat("assistant", "Well well… looks like someone’s getting spoiled tonight.")
    add_chat("assistant", "10 full minutes. Warm oil. My hands. Your body. And yes… I’m feeling *extra* mean today 😏")

    simulate_loading(2)
    add_media("oiled1.jpeg")
    
    add_chat("assistant", "Choose how I start:")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Shirtless… right now"):
        add_chat("user", "Shirtless.")
        simulate_typing(1)
        add_chat("assistant", "Mmm… bold. I like that attitude. Shirt’s gone.")
        simulate_loading(3); add_media("shirtless_oil.jpeg")
        st.session_state.turn_state = "MASSAGE_POS"
        st.rerun()
        
    if c2.button("Keep shirt on"):
        add_chat("user", "Keep it on for now.")
        simulate_typing(1)
        add_chat("assistant", "Playing hard to get? I’ll just have to peel it off you slowly then…")
        st.session_state.turn_state = "MASSAGE_POS"
        st.rerun()
        
    if c3.button("Surprise me"):
        add_chat("user", "Surprise me.")
        simulate_typing(1)
        add_chat("assistant", "Oh you want a surprise? Dangerous game.")
        st.session_state.turn_state = "MASSAGE_POS"
        st.rerun()

elif st.session_state.turn_state == "MASSAGE_POS":
    add_chat("assistant", "Starting now. Face down. Relax… or try to.")
    add_chat("assistant", "How do you position yourself?")
    
    col1, col2 = st.columns(2)
    if col1.button("Hips raised (Tease back)"):
        add_chat("user", "Hips raised.")
        simulate_typing(2)
        add_chat("assistant", "Ohhh… already arching for me? Naughty little thing.")
        st.session_state.tension += 2
        simulate_loading(3); add_media("massage_back_arch.jpeg")
        st.session_state.turn_state = "MASSAGE_LOOP_1"
        st.rerun()
        
    if col2.button("Proper & Innocent"):
        add_chat("user", "Lying flat.")
        simulate_typing(2)
        add_chat("assistant", "So polite… I almost feel bad about what I’m gonna do to you.")
        st.session_state.tension += 1
        st.session_state.turn_state = "MASSAGE_LOOP_1"
        st.rerun()

elif st.session_state.turn_state == "MASSAGE_LOOP_1":
    add_chat("assistant", "Shoulders first… deep, slow circles. Feel that?")
    add_narrator("Warm oil drips down your sides… then lower.")
    
    if st.button("Beg for lower"):
        add_chat("user", "Lower... please.")
        simulate_typing(2)
        add_chat("assistant", "Good boy… using your words. More oil… dripping… right where you’re aching.")
        st.session_state.tension += 3
        st.session_state.turn_state = "MASSAGE_LOOP_2"
        st.rerun()
        
    if st.button("Stay silent"):
        add_chat("user", "...")
        simulate_typing(2)
        add_chat("assistant", "Staying quiet? I’ll just have to make you louder…")
        st.session_state.turn_state = "MASSAGE_LOOP_2"
        st.rerun()

elif st.session_state.turn_state == "MASSAGE_LOOP_2":
    add_chat("assistant", "Palms gliding over your glutes… slow… possessive.")
    simulate_loading(3); add_media("massage_glutes.jpeg")
    
    add_narrator("Fingertips teasing the sensitive inner lines… never quite touching.")
    add_chat("assistant", "I can feel how much you want it… pathetic and perfect.")
    
    if st.button("Try to flip over"):
        add_chat("user", "Trying to turn over...")
        simulate_typing(1)
        add_chat("assistant", "Trying to take over? Cute. Hands behind your back. Now.")
        st.session_state.tension += 5
        st.session_state.turn_state = "MASSAGE_END"
        st.rerun()
        
    if st.button("Submit completely"):
        add_chat("user", "I'm yours.")
        simulate_typing(1)
        add_chat("assistant", "That's it. Melt for me.")
        st.session_state.turn_state = "MASSAGE_END"
        st.rerun()

elif st.session_state.turn_state == "MASSAGE_END":
    add_chat("assistant", "One minute left… and you’re a mess already.")
    
    if st.session_state.tension >= 5:
        add_chat("assistant", "Look at you… leaking, shaking, desperate.")
        simulate_loading(3); add_media("trembling_hands.jpeg")
    else:
        add_chat("assistant", "You held up better than I expected… but you're still ruined.")

    simulate_typing(3)
    add_chat("assistant", "*Beep.* Timer's up.")
    add_chat("assistant", "No release today, baby. House rules. But next prize? Everything I denied you today… x10.")
    add_narrator("She wipes the oil from her hands, leaving you glistening and aching.")
    
    st.session_state.turn_state = "PRIZE_DONE"
    st.rerun()

    # --- UPSIDE DOWN THROAT FUCK ---
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN_THROAT_FUCK":
    add_chat("assistant", "Mmm… you won Upside Down Throat Fuck, baby. I’ve been thinking about this all day.")
    add_chat("assistant", "I want your cock in my mouth… deep, slow at first, then harder… until you give me every thick, hot drop straight down my throat.")
    add_chat("assistant", "I’m already on my knees for you. Look at me — lips parted, tongue out just a little, waiting.")
    
    simulate_loading(3)
    add_media("kneeling_tease_lips.jpeg") 

    if st.button("Get in position"):
        st.session_state.turn_state = "PRIZE_UP_THROAT_START"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_UP_THROAT_START":
    add_chat("assistant", "I lean back, head hanging off the edge of the bed, throat open and vulnerable. Tell me how you want to start...")
    
    c1, c2, c3 = st.columns(3)
    
    # OPTION 1: TEASE
    if c1.button("Tease me first"):
        add_chat("user", "Lick the tip slowly.")
        simulate_typing(3.5)
        add_chat("assistant", "I lean in close… hot breath ghosting over your head first. Then my tongue slips out — slow, flat licks across the tip, circling the slit, tasting every bead of precum.")
        simulate_loading(4)
        add_media("slow_tip_lick_closeup.jpeg")
        add_chat("assistant", "Mmm… you taste so good already. I love how you twitch every time my tongue flicks right under the ridge.")
        
        # Move to finish choice
        st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"
        st.rerun()

    # OPTION 2: SLOPPY
    if c2.button("Make it sloppy"):
        add_chat("user", "Suck the head, make it wet.")
        simulate_typing(3)
        add_chat("assistant", "I wrap my lips around the head only… sucking gently at first, then harder, tongue swirling inside my mouth while I make wet, obscene sucking sounds.")
        simulate_loading(4)
        add_media("sloppy_head_suck.jpeg")
        add_chat("assistant", "Spit runs down your shaft… I let it get messy on purpose. I want you slick and throbbing before I take more.")
        
        # Move to finish choice
        st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"
        st.rerun()

    # OPTION 3: DEEP
    if c3.button("Deep throat now"):
        add_chat("user", "Take me deep.")
        simulate_typing(3.5)
        add_chat("assistant", "No teasing then… I open wide and slide down slow, letting you feel my throat relax around you inch by inch until my nose is pressed to your skin.")
        simulate_loading(4)
        add_media("deep_throat_entry_slow.jpeg")
        add_chat("assistant", "Fuck… you’re so thick. I love the way you stretch my throat. I hold you there for a second, humming so you feel the vibration.")
        
        # Move to finish choice
        st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"
        st.rerun()

# ── THE FINISH ──────────────────────────────────────────────────────
elif st.session_state.turn_state == "PRIZE_UP_THROAT_FINISH":
    add_chat("assistant", "God you’re throbbing so hard in my throat… I can feel how close you are.")
    add_chat("assistant", "Tell me how you want to finish, baby… I’m ready for it all.")
    
    c1, c2, c3 = st.columns(3)

    # FINISH 1: DEEP
    if c1.button("Deep throat cum"):
        add_chat("user", "Deep throat until I cum.")
        simulate_loading(5)
        add_media("full_throat_bury_cum.jpeg")
        add_chat("assistant", "You hold my head still and thrust deep… I take every inch, throat squeezing around you as you start to pulse.")
        add_chat("assistant", "Hot, thick ropes shoot straight down my throat — I swallow fast, milking you with my muscles, humming so you feel every vibration.")
        simulate_typing(3)
        add_chat("assistant", "When you finally pull out, I gasp for air… then lean back in to lick every last drop from your tip, cleaning you slowly while staring up at you with a satisfied smile.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    # FINISH 2: TONGUE
    if c2.button("Cum on tongue"):
        add_chat("user", "Pull out, cum on your tongue.")
        simulate_loading(5)
        add_media("tongue_cum_pool.jpeg")
        add_chat("assistant", "You pull out right at the edge… I open wide, tongue flat, begging with my eyes. You explode — thick, warm spurts land across my tongue, filling my mouth.")
        add_chat("assistant", "I hold it there a second, letting you see, then swallow slowly, savoring every bit. I lick my lips and moan… ‘More next time?’")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    # FINISH 3: HOLD
    if c3.button("Throat Creampie"):
        add_chat("user", "Cum down my throat, hold me there.")
        simulate_loading(5)
        add_media("throat_creampie_hold.jpeg")
        add_chat("assistant", "You grab my head with both hands and bury yourself completely. I feel the first hot pulse hit the back of my throat… then another… and another.")
        add_chat("assistant", "I swallow around you over and over, throat working hard to take it all. When you finally ease back, I’m gasping, lips swollen, but I smile up at you like I just won the lottery.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
        # --- ANAL FUCK (deep branching) ---
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    add_narrator("My blue eyes darken with lust, lips parting as I whisper.")
    add_chat("assistant", "Your prize is my tight asshole… but how you take it, how hard, how long… that's your choice tonight.")
    
    style = st.radio("Claim style:", 
        ["Slow & sensual build", "Rough & dominant", "Teasing denial first", "Romantic & eye-locked"], 
        key="anal_style_choice")
    
    if st.button("Start claiming me", key="anal_begin"):
        simulate_loading(3)
        
        if "Slow" in style:
            add_media(random.choice(["behind_fuck1.jpeg", "behind_fuck10.jpeg"]))
            add_chat("assistant", "I arch slowly, cheeks spread with trembling fingers. You drizzle warm lube… press just the head in… I gasp softly, walls fluttering around you.")
            depth_choice = st.radio("How deep?", ["Halfway teasing", "All the way gentle"], key="slow_depth")
            if st.button("Push", key="slow_push"):
                if "Halfway" in depth_choice:
                    add_chat("assistant", "You stay shallow… I rock back begging for more, whimpering sweetly.")
                else:
                    add_chat("assistant", "You sink all the way… slow, deep strokes until I'm trembling and dripping.")
        
        elif "Rough" in style:
            add_media(random.choice(["behind_fuck4.jpeg", "behind_fuck7.jpeg", "behind_fuck8.jpeg"]))
            add_chat("assistant", "I push back hard. You slam in one brutal thrust—my scream echoes as you stretch me wide, balls slapping skin.")
            pace_choice = st.radio("Pace?", ["Fast & punishing", "Slow brutal grinds"], key="rough_pace")
            if st.button("Fuck harder", key="rough_fuck"):
                if "Fast" in pace_choice:
                    add_chat("assistant", "You pound relentlessly—my hole gaping slightly each withdrawal, drool on the sheets.")
                else:
                    add_chat("assistant", "Deep, grinding rolls… holding me pinned while I shake.")
        
        elif "Teasing denial" in style:
            add_media("behind_fuck10.jpeg")
            add_chat("assistant", "You circle my hole with your tip… press in just the head… pull out… over and over.")
            if st.button("Please let me have it", key="denial_beg"):
                add_chat("assistant", "After minutes of torment, you finally sink deep… I cry out in relief.")
            else:
                add_chat("assistant", "You keep denying… leaving me clenching on nothing, begging louder.")
        
        else:  # Romantic
            add_media("behind_fuck5.jpeg")
            add_chat("assistant", "We face the mirror. You enter slowly while our eyes stay locked… hands caressing my breasts, lips brushing my neck.")
            if st.button("Cum with me", key="romantic_cum"):
                add_chat("assistant", "We move together… deep, rolling thrusts until we shatter as one.")
        
        cum_choice = st.radio("Finish?", ["Cum deep inside", "Pull out & paint my ass", "Edge & deny"], key="anal_finish")
        if st.button("End it", key="anal_final"):
            simulate_loading(3.5)
            if "inside" in cum_choice:
                add_media(random.choice(["ass_cum1.jpeg", "ass_cum3.jpeg"]))
                add_chat("assistant", "Yes… flood my ass… feel me clench and milk every pulse.")
            elif "paint" in cum_choice:
                add_media("ass_cum4.jpeg")
                add_chat("assistant", "Pull out… hot ropes across my cheeks… I shiver as it drips.")
            else:
                add_chat("assistant", "You stop just before… leaving me quivering, empty, desperate for next time.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- TOY PIC (custom + intensity branches) ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    add_narrator("My breath quickens, cheeks flushing.")
    add_chat("assistant", "Pick toy, hole, depth… I'll snap it exactly how you command.")
    
    toy_type = st.radio("Toy?", 
        ["Vibrating bullet", "Thick dildo", "Household object (screwdriver)", "Jeweled plug"], 
        key="toy_type_choice")
    hole = st.radio("Hole?", ["Pussy", "Ass"], key="toy_hole")
    depth = st.radio("Depth?", ["Teasing shallow", "All the way buried"], key="toy_depth")
    
    if st.button("Insert & photograph", key="toy_snap"):
        simulate_loading(4)
        add_media("toy_pic.jpeg")
        add_chat("assistant", f"{toy_type} in my {hole.lower()}… ")
        
        if "shallow" in depth:
            add_chat("assistant", "…just the tip, lips gripping, clit throbbing above it.")
        else:
            add_chat("assistant", "…all the way, base flush, my walls stretched tight around it.")
        
        reaction = st.radio("My reaction?", ["Moaning & begging", "Silent trembling", "Dirty talk"], key="toy_reaction")
        if st.button("Show final pic", key="toy_final"):
            if "Moaning" in reaction:
                add_media("toy_ass1.jpeg")
                add_chat("assistant", "I can't stop whimpering your name… please let me cum with it inside.")
            elif "Silent" in reaction:
                add_chat("assistant", "My thighs shake silently… eyes pleading.")
            else:
                add_chat("assistant", "\"Fuck… look how deep you made me take it… I'm your little toy slut.\"")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- LICK PUSSY (technique + finish branches) ---
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    add_chat("assistant", "Worship me with that mouth… choose how you please me.")
    
    technique = st.radio("Technique:", 
        ["Slow teasing circles", "Deep tongue fucking", "Suck & finger combo", "Edge me forever"], 
        key="lick_technique")
    
    if st.button("Start licking", key="lick_begin"):
        simulate_loading(3.5)
        img = random.choice(["pussy_lick1.jpeg", "pussy_lick2.jpeg", "pussy_lick3.jpeg"])
        add_media(img)
        
        if "Slow" in technique:
            add_chat("assistant", "Your tongue traces lazy circles around my clit… I shiver, hips lifting for more.")
        elif "Deep" in technique:
            add_chat("assistant", "You plunge inside… fucking me with your tongue while I grind down hard.")
        elif "Suck" in technique:
            add_chat("assistant", "You suck my clit hard… two fingers curling inside, hitting that spot perfectly.")
        else:  # Edge
            add_chat("assistant", "You bring me close… then pull away… over and over until I'm crying.")
        
        finish_choice = st.radio("Finish?", 
            ["Let me cum on your face", "Pull back & deny", "Make me squirt"], 
            key="lick_finish")
        if st.button("End it", key="lick_final"):
            if "squirt" in finish_choice:
                add_chat("assistant", "I explode… soaking your face, chest, everything.")
            elif "deny" in finish_choice:
                add_chat("assistant", "You stop right at the edge… leaving me shaking and desperate.")
            else:
                add_chat("assistant", "I cum hard… thighs clamping your head, flooding your mouth.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
# --- TONGUE TEASE (Complex Edging Game) ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    # ── Initialize state if first time ──
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
        add_chat("assistant", "Mmm… you won the **Tongue Tease** prize. Lucky boy.")
        add_chat("assistant", "Rules are simple: you stroke exactly how I tell you…")
        add_chat("assistant", "…and you **don't cum** until my tongue decides you've earned it. Clear?")

        c1, c2 = st.columns([1,3])
        if c1.button("Yes Ma'am", key="obey_start"):
            data["stage"] = 1
            st.rerun()
        if c2.button("I'm already so hard…", key="impatient_start"):
            data["impatient"] = True
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: First Contact ──
    elif data["stage"] == 1:
        add_chat("assistant", "Stroke slow. Just the shaft… no head yet.")
        add_chat("assistant", "Eyes on me while I kneel between your legs…")
        
        simulate_loading(2)
        add_media("tease1_close.jpeg")  # close up of lips/tongue hovering

        add_chat("assistant", "Feel that? Just my hot breath… dripping anticipation…")

        if st.button("Let me feel your tongue… please", key="first_beg"):
            data["begged"] = True
            data["edging_level"] += 2
            data["stage"] = 2
            st.rerun()

        if st.button("I can't wait – faster", key="rush"):
            data["impatient"] = True
            data["edging_level"] += 1
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: First Tastes ──
    elif data["stage"] == 2:
        simulate_loading(2)
        add_media("tease2_tongue_tip.jpeg")  # single cruel flick on tip

        add_chat("assistant", "One slow, cruel flick across your slit… tasting how desperate you are already.")
        add_narrator("Your hips jerk. She smiles against your skin.")
        
        reason = "because you begged so nicely" if data['begged'] else "even though I told you to go slow"
        add_chat("assistant", f"Look at that… you're leaking like crazy {reason}.")

        c1, c2, c3 = st.columns(3)
        if c1.button("More… please swirl", key="ask_swirl"):
            data["edging_level"] += 2
            data["stage"] = 3
            st.rerun()

        if c2.button("Keep teasing tip only", key="tip_only"):
            data["edging_level"] += 1
            data["stage"] = 3
            st.rerun()

        if c3.button("I need full tongue", key="demand_full"):
            data["impatient"] = True
            data["edging_level"] += 3
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: Serious Edging ──
    elif data["stage"] == 3:
        add_chat("assistant", "Good… now stroke faster while I work.")
        
        simulate_loading(2)
        add_media("tease3_swirl_slow.gif") # or .jpeg

        add_chat("assistant", "Slow wet circles around the head… then flat tongue dragging all the way down… back up…")
        add_chat("assistant", "You're throbbing so hard against my tongue… so close…")
        add_narrator("Your balls are tight. Breathing ragged. Dangerous.")

        if data["impatient"]:
            add_chat("assistant", "Tsk… getting greedy made it worse, didn't it? Now you get **extra slow** for punishment.")

        c1, c2, c3 = st.columns(3)
        if c1.button("Beg: Please let me cum", key="big_beg"):
            data["begged"] = True
            data["edging_level"] += 4
            data["stage"] = 4
            st.rerun()

        if c2.button("Hold… I'll be good", key="try_hold"):
            data["edging_level"] += 2
            data["stage"] = 4
            st.rerun()

        if c3.button("Fuck it – I'm cumming", key="break"):
            data["stage"] = "ruin"
            st.rerun()

    # ── Stage 4: Climax / Endings ──
    elif data["stage"] == 4:
        simulate_loading(2)
        add_media("tease4_mouth_open_ready.jpeg") 

        # ENDING A: The Good Release
        if data["edging_level"] >= 5 or data["begged"]:
            add_chat("assistant", "That's it… you've suffered so prettily.")
            add_chat("assistant", "Open mouth… tongue out… give it to me **now**.")
            
            if st.button("RELEASE"):
                simulate_loading(3)
                add_media("tease5_finish_on_tongue.jpeg")
                add_chat("assistant", "Mmm… good boy. Such a big load for me.")
                add_narrator("You explode while watching every pulse land exactly where she wanted.")
                
                if st.button("Finish"):
                    del st.session_state.tongue_tease # Clean up
                    st.session_state.turn_state = "PRIZE_DONE"
                    st.rerun()

        # ENDING B: Ruined / Denied (Logic Check)
        else:
            add_chat("assistant", "You're right on the edge… shaking…")
            add_chat("assistant", "But not yet.")
            add_chat("assistant", "**Stop stroking.** Hands off. Right now.")
            add_narrator("Ruined orgasm – you throb helplessly while she just watches and smiles.")
            
            if st.button("Accept Fate"):
                del st.session_state.tongue_tease
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

    # ── Impatient / Ruined Ending ──
    elif data["stage"] == "ruin":
        add_chat("assistant", "Oh baby… you couldn't wait?")
        add_chat("assistant", "Hands off **immediately**.")
        simulate_loading(2)
        add_media("ruin_moment.jpeg") 
        add_chat("assistant", "Look how weak that was… barely anything. That's what happens when you disobey.")
        
        if st.button("Apologize"):
            del st.session_state.tongue_tease
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            # --- ROAD HEAD (RISK & THRILL) ---
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    if "road_head" not in st.session_state:
        st.session_state.road_head = {
            "stage": 0,
            "risk_level": "medium",
            "control": "you"
        }

    data = st.session_state.road_head

    # ── Stage 0: Setup ──
    if data["stage"] == 0:
        add_chat("assistant", "Road head. The kind that makes your heart race for all the right reasons.")
        add_chat("assistant", "How risky do you want to play tonight?")

        cols = st.columns(3)
        if cols[0].button("Low risk (Night)", key="risk_low"):
            data["risk_level"] = "low"
            data["stage"] = 1
            st.rerun()

        if cols[1].button("Medium (Tinted)", key="risk_medium"):
            data["risk_level"] = "medium"
            data["stage"] = 1
            st.rerun()

        if cols[2].button("High (Daylight)", key="risk_high"):
            data["risk_level"] = "high"
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: The Drive ──
    elif data["stage"] == 1:
        risk_desc = {
            "low": "dark empty highway… only headlights and shadows",
            "medium": "steady traffic… windows tinted… danger just close enough",
            "high": "bright daylight, cars all around… anyone could look over"
        }[data["risk_level"]]

        add_chat("assistant", f"Engine hums. {risk_desc}.")
        add_chat("assistant", "I lean over the center console… eyes flicking up to yours.")
        
        simulate_loading(2)
        add_media("road_head_start.jpg") 

        add_chat("assistant", "One hand on the wheel… the other slides into my hair… guiding.")

        c1, c2 = st.columns(2)
        if c1.button("You guide my head", key="control_you"):
            data["control"] = "you"
            data["stage"] = 2
            st.rerun()

        if c2.button("I take control (Tease)", key="control_me"):
            data["control"] = "me"
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: Main Action ──
    elif data["stage"] == 2:
        if data["control"] == "you":
            add_chat("assistant", "You push me down… deeper… holding me there at stoplights.")
            add_chat("assistant", "I moan around you every time you flex your fingers in my hair.")
        else:
            add_chat("assistant", "I take my time… slow swirling tongue… popping off just to watch you twitch.")
            add_chat("assistant", "You can't grab my hair – your hands stay glued to the wheel.")

        simulate_loading(2)
        add_media("road_head_mid.gif") 

        if data["risk_level"] == "high":
            add_chat("assistant", "Truck next to us… driver glances over… I don't stop. In fact… I go deeper.")
        elif data["risk_level"] == "medium":
            add_chat("assistant", "SUV pulls up beside us… I stay down… lips sealed tight… making you suffer silently.")

        simulate_loading(3)
        add_chat("assistant", "You're throbbing so hard… so close…")

        c1, c2, c3 = st.columns(3)
        if c1.button("Pull over & Finish", key="pull_over"):
            data["stage"] = 3
            st.rerun()

        if c2.button("Finish Driving (Risky)", key="while_driving"):
            data["stage"] = "risky_finish"
            st.rerun()

        if c3.button("Edge until Home", key="edge_home"):
            data["stage"] = "edge_home"
            st.rerun()

    # ── Endings ──
    elif data["stage"] == 3: # Safe
        add_chat("assistant", "Tires crunch on gravel… car in park.")
        add_media("road_head_finish_safe.jpg")
        add_chat("assistant", "Both hands free now… I finish you properly. Every pulse lands on my tongue.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    elif data["stage"] == "risky_finish": # Risky
        add_chat("assistant", "Right there on the highway… I swallow everything while you fight to keep the car straight.")
        add_narrator("Heart pounding, knuckles white… best kind of danger.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    elif data["stage"] == "edge_home": # Edge
        add_chat("assistant", "I bring you right to the edge… then stop. Again. And again.")
        add_chat("assistant", "When we finally park… you're shaking. Now… do you want your reward inside? 😈")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()


# --- PLUG TEASE (Size & Duration) ---
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    if "plug_tease" not in st.session_state:
        st.session_state.plug_tease = {
            "stage": 0,
            "size_chosen": "small",
            "tease_level": 0,
            "begged_for_more": False
        }

    data = st.session_state.plug_tease

    # ── Stage 0: Intro ──
    if data["stage"] == 0:
        add_chat("assistant", "I've been thinking about this plug all day… being filled, stretched, constantly reminded of you…")
        add_chat("assistant", "Which one should I wear for you today?")

        c1, c2, c3 = st.columns(3)
        if c1.button("Small (Tease)", key="plug_small"):
            data["size_chosen"] = "small"
            data["stage"] = 1
            st.rerun()

        if c2.button("Medium (Stretch)", key="plug_medium"):
            data["size_chosen"] = "medium"
            data["stage"] = 1
            st.rerun()

        if c3.button("Large (Challenge)", key="plug_large"):
            data["size_chosen"] = "large"
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: Insertion ──
    elif data["stage"] == 1:
        size_text = {
            "small": "slender, perfectly curved",
            "medium": "thick enough to make me gasp",
            "large": "heavy, girthy… almost too much"
        }[data["size_chosen"]]

        add_media(f"plug_{data['size_chosen']}_base.jpg") 

        add_chat("assistant", f"Warm lube dripping… I press the {size_text} tip against myself… Slow breath out… pushing…")
        
        simulate_loading(3)
        add_media("plug_insertion_slow.gif") 
        add_narrator("A soft whimper escapes when the widest part slips past the rim.")
        add_chat("assistant", "It's in… seated deep. Every tiny shift makes me clench around it.")

        c1, c2 = st.columns(2)
        if c1.button("Tell me how it feels", key="tell_feels"):
            data["tease_level"] += 1
            data["stage"] = 2
            st.rerun()

        if c2.button("Show me movement", key="see_move"):
            data["tease_level"] += 2
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: Escalation ──
    elif data["stage"] == 2:
        add_chat("assistant", "Standing up… oh god, the pressure shifts instantly.")

        if data["size_chosen"] == "large":
            add_chat("assistant", "It's so deep I can barely walk without moaning…")
        elif data["size_chosen"] == "medium":
            add_chat("assistant", "Every step presses right against that spot…")
        else:
            add_chat("assistant", "Subtle, teasing fullness… constant little reminder.")

        simulate_loading(2)
        add_media("plug_walk_tease.jpg") 

        add_chat("assistant", "Sitting down slowly… fuck… it pushes even deeper.")
        
        simulate_loading(3)
        add_chat("assistant", "I could keep this in for hours… thinking of you…")

        c1, c2, c3 = st.columns(3)
        if c1.button("Beg to replace it", key="beg_replace"):
            data["begged_for_more"] = True
            data["tease_level"] += 4
            data["stage"] = 3
            st.rerun()

        if c2.button("Keep it all day", key="keep_all_day"):
            data["tease_level"] += 2
            data["stage"] = 3
            st.rerun()

        if c3.button("Play with it now", key="play_with"):
            data["tease_level"] += 3
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: Endings ──
    elif data["stage"] == 3:
        add_media("plug_final_seated.jpg")

        if data["tease_level"] >= 6 or data["begged_for_more"]:
            add_chat("assistant", "Mmm… you're making me so needy. When you finally get home... pull it out so slowly… then fill me with something harder…")
            add_chat("assistant", "I'll keep it in until then… just for you.")
        
        elif data["tease_level"] >= 3:
            add_chat("assistant", "Such a good tease. I'll wear it a few more hours… every clench will be for you.")
            add_chat("assistant", "Maybe I'll send you a photo later...")
        
        else:
            add_chat("assistant", "Aww… not desperate enough yet? Then I'll just leave it in quietly… saving the real fun for later.")

        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
        # --- NUDE PIC (Customizer) ---
elif st.session_state.turn_state == "PRIZE_NUDE_PIC":
    if "nude_pic" not in st.session_state:
        st.session_state.nude_pic = {
            "stage": 0,
            "pose": None,
            "focus": None,
            "mood": "teasing"
        }

    data = st.session_state.nude_pic

    # ── Stage 0: Choose Pose ──
    if data["stage"] == 0:
        add_chat("assistant", "Your very own custom nude… just tell me how you want me.")
        add_chat("assistant", "Pick the pose first…")

        poses = [
            "Ass up high, back arched, looking back over shoulder",
            "Legs spread wide, close-up on dripping pussy",
            "Tits pushed together, nipples hard, biting lip",
            "Full body mirror shot, completely naked, hair down",
            "On knees, hands behind back, mouth slightly open"
        ]

        # Use radio button for selection
        data["pose"] = st.radio("Pose:", poses, key="nude_pose_select")

        if st.button("Next → Focus", key="nude_pose_next"):
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: Choose Focus / Angle ──
    elif data["stage"] == 1:
        pose_text = data['pose'].split(',')[0].lower() # Get first part of pose string
        add_chat("assistant", f"Mmm… {pose_text} — already getting wet thinking about it.")

        focuses = [
            "Extreme close-up on wet pussy/ass",
            "Full body with seductive eye contact",
            "Breasts & cleavage in focus",
            "Ass & arched back emphasis",
            "Face + mouth + pleading expression"
        ]

        data["focus"] = st.radio("Main focus:", focuses, key="nude_focus_select")

        cols = st.columns(2)
        if cols[0].button("Make it teasing / playful", key="mood_tease"):
            data["mood"] = "teasing"
            data["stage"] = 2
            st.rerun()
        
        if cols[1].button("Make it desperate / submissive", key="mood_desperate"):
            data["mood"] = "desperate"
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: Delivery ──
    elif data["stage"] == 2:
        simulate_loading(3)

        # Logic to pick media based on choices (simplified for now)
        base_img = "nude_pic1.jpeg"
        extra_img = "nude_teasing_extra.jpg"
        
        if "Ass" in data["pose"]: base_img = "nude_ass_pose.jpeg" # You can map these if you have files
        if data["mood"] == "desperate": extra_img = "nude_desperate_extra.jpg"

        add_media(base_img) 

        add_chat("assistant", f"Here I am… pose locked, skin flushed hot for you.")

        if data["mood"] == "desperate":
            add_chat("assistant", "Eyes begging, thighs trembling, practically dripping onto the sheets…")
            simulate_loading(2)
            add_media(extra_img)
        else:
            add_chat("assistant", "Smirking at the camera, fingers teasing myself just enough to drive you crazy…")
            simulate_loading(2)
            add_media(extra_img)

        # Optional Bonus
        if st.button("One more angle? Please?", key="nude_extra"):
            simulate_loading(2)
            add_media("nude_custom_bonus.jpg")
            add_chat("assistant", "Extra one… just because you asked so nicely 😘")
            
            # Clean up and finish
            if st.button("Save & Finish"):
                del st.session_state.nude_pic
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()
        
        # Or finish directly
        if st.button("I'm satisfied"):
            del st.session_state.nude_pic
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            # --- SLAVE DAY (24 Hours of Service) ---
elif st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    # ── Initialize State ──
    if "slave_day" not in st.session_state:
        st.session_state.slave_day = {
            "stage": 0, 
            "service_type": "Under-desk service", # Default
            "intensity": "medium"
        }

    data = st.session_state.slave_day

    # ── Stage 0: Rules & Setup ──
    if data["stage"] == 0:
        add_chat("assistant", "24 hours. Your devoted slave. Your rules. Your pleasure.")
        add_narrator("I drop to my knees, head bowed, waiting for your first command.")

        options = [
            "Under-desk service while you game/stream",
            "Complete body worship session",
            "Rough use — throat / ass training",
            "Total free use — any hole, any time"
        ]

        # Save selection to state immediately
        data["service_type"] = st.radio("First service, Master?", options, key="slave_radio")

        cols = st.columns(2)
        with cols[0]:
            if st.button("Keep it sensual", key="intensity_soft"):
                data["intensity"] = "soft"
                data["stage"] = 1
                st.rerun()
        with cols[1]:
            if st.button("Make it rough & degrading", key="intensity_hard"):
                data["intensity"] = "hard"
                data["stage"] = 1
                st.rerun()

    # ── Stage 1: The Service ──
    elif data["stage"] == 1:
        simulate_loading(2.5)

        # Logic based on what they picked in Stage 0
        if "desk" in data["service_type"].lower():
            # Randomize images if you have multiple, or use specific ones
            img = random.choice(["game_bj1.jpeg", "game_bj2.jpeg"])
            add_media(img)
            add_chat("assistant", "I crawl under your desk… lips around you while you frag.")
            
            if data["intensity"] == "hard":
                add_chat("assistant", "You can grab my hair, fuck my throat between rounds, use me like stress relief.")
            else:
                add_chat("assistant", "I'll keep you hard while you play, swallowing quiet moans so your team doesn't hear.")

        elif "worship" in data["service_type"].lower():
            add_chat("assistant", "Starting at your feet… slow kisses, tongue between toes, working up calves, thighs…")
            add_media("worship_sequence_01.jpg") # Ensure this file exists or change name
            
            if data["intensity"] == "hard":
                add_chat("assistant", "…until I'm grinding my face against you, begging to taste more.")
            else:
                add_chat("assistant", "I'll worship every inch of skin until you're melting.")

        else: # Rough / Free use
            add_media("rough_use_start.jpg")
            add_chat("assistant", "Tie me however you want… throat, ass, pussy — all yours.")
            
            if data["intensity"] == "hard":
                add_chat("assistant", "Call me names. Spit in my mouth. Make me thank you after every thrust.")

        if st.button("Continue the day… next command?", key="slave_next"):
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: The Aftermath ──
    elif data["stage"] == 2:
        add_narrator("Hours pass. I'm marked, messy, still eager.")
        
        # Picking 2 random finish images
        # Ensure these files exist or use general ones like "cum_face_01.jpeg"
        finish_imgs = ["slave_cum_01.jpeg", "ass_use_02.jpeg", "throat_deep_01.jpeg", "cum_face_01.jpeg"]
        chosen_imgs = random.sample(finish_imgs, 2)

        add_dual_media(chosen_imgs[0], chosen_imgs[1])

        endings = {
            "soft": "You finish inside me while I whisper how much I love serving you…",
            "hard": "You paint my face, my tits, my ass — then make me crawl to clean every drop with my tongue."
        }

        add_chat("assistant", endings[data["intensity"]])
        add_chat("assistant", "Your slave thanks you for using her so perfectly today.")

        if st.button("Dismiss Slave"):
            del st.session_state.slave_day # Cleanup
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            # --- ALL 3 HOLES (Total Overload) ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    if "all_3_holes" not in st.session_state:
        st.session_state.all_3_holes = {
            "stage": 0,
            "main_hole": "Cock buried in my dripping pussy", # Default
            "ass_fill": "plug"
        }

    data = st.session_state.all_3_holes

    # ── Stage 0: Choose Primary & Ass Fill ──
    if data["stage"] == 0:
        add_chat("assistant", "Every hole filled… no part of me left untouched. Completely, obscenely owned.")
        add_chat("assistant", "Tell me how you want to ruin me tonight.")

        main_options = [
            "Cock buried in my dripping pussy",
            "Cock stretching my tight ass",
            "Cock filling my throat (double stuffed below)"
        ]

        data["main_hole"] = st.radio("Where do you claim first?", main_options)

        cols = st.columns(2)
        if cols[0].button("Thick, heavy plug in my ass", key="ass_plug"):
            data["ass_fill"] = "plug"
            data["stage"] = 1
            st.rerun()
        
        if cols[1].button("Your fingers / toy stretching my ass", key="ass_fingers"):
            data["ass_fill"] = "fingers"
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: Filling Sequence ──
    elif data["stage"] == 1:
        simulate_loading(3)

        if "pussy" in data["main_hole"].lower():
            add_media("triple_pussy_entry_close.jpg")
            add_chat("assistant", "You sink into my pussy — hot, slick walls sucking you in with every inch.")
            add_chat("assistant", "I’m already clenching, dripping down your balls before anything else even touches me.")
        elif "ass" in data["main_hole"].lower():
            add_media("triple_ass_entry.jpg")
            add_chat("assistant", "You force your way into my ass — tight ring resisting, then yielding with a slick pop.")
            add_chat("assistant", "I whimper, thighs shaking, the stretch burning deliciously.")
        else:
            add_chat("assistant", "You grab my hair and pull me deep onto you, choking me beautifully.")

        add_chat("assistant", "And then… the second invasion…")

        if data["ass_fill"] == "plug":
            simulate_loading(2)
            add_media("plug_stretch_triple.jpg")
            add_chat("assistant", "Cold lube, then the blunt, heavy plug — pushing, stretching, filling the last empty space.")
            add_chat("assistant", "I gasp — the pressure is overwhelming, everything feels tighter, fuller, obscene.")
        else:
            add_chat("assistant", "Your fingers slide in beside the main stretch — scissoring, curling, making me sob with fullness.")

        add_narrator("My whole body is trembling. Overloaded. Every nerve singing.")

        if st.button("Now fill my mouth… make me complete", key="fill_mouth"):
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: Total Overload ──
    elif data["stage"] == 2:
        simulate_loading(3)
        add_media("all_three_filled_extreme.jpg") 

        add_chat("assistant", "All three… stuffed so full I can barely breathe.")
        add_chat("assistant", "Pussy/ass clenching desperately around cock and plug. Throat working around whatever you feed me.")
        add_chat("assistant", "Drool runs down my chin. Tears prick my eyes from the intensity. I’m moaning around the intrusion — muffled, desperate.")

        add_narrator("The room smells of sex and lube and sweat. Wet, filthy sounds echo with every tiny movement.")

        cols = st.columns(3)
        if cols[0].button("Pound me hard", key="triple_hard"):
            add_chat("assistant", "You slam into me — each thrust jostling the plug, making everything clench tighter.")
            add_chat("assistant", "I gag, cry out, body jerking helplessly between all the invasions.")
        
        if cols[1].button("Slow, grinding torture", key="triple_slow"):
            add_chat("assistant", "You grind deep… tiny circles… every millimeter amplified by how packed I am.")
            add_chat("assistant", "I’m whimpering continuously, drooling, shaking, completely lost.")
        
        if cols[2].button("Edge me incoherently", key="triple_edge"):
            add_chat("assistant", "You bring me to the brink over and over… stopping just as my body starts to convulse.")
            add_chat("assistant", "I’m crying around your cock, pleading with my eyes, body trembling violently.")

        st.write("---") # Visual separator
        if st.button("Finish… flood one of them", key="triple_finish"):
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: Climax & Collapse ──
    elif data["stage"] == 3:
        simulate_loading(3)
        add_media("triple_climax_messy.jpg")

        add_chat("assistant", "You choose your target… and let go.")
        add_chat("assistant", "Hot, thick pulses deep inside whichever hole you claim — I shatter instantly, clenching around everything, screaming muffled against whatever fills my mouth.")
        
        simulate_typing(3)
        add_chat("assistant", "When it’s over… I’m a trembling, dripping, ruined mess — holes slowly pulsing, body slick with sweat and cum and lube.")
        add_chat("assistant", "You pull out one by one… each withdrawal makes me whimper… until I’m empty, gaping, and blissfully wrecked.")
        
        add_narrator("I collapse forward… panting… smiling weakly…")
        add_chat("assistant", "“Thank you… for using every fucking part of me…” 🖤")

# --- ROMANTIC FANTASY (Ultra-Immersive) ---
elif st.session_state.turn_state == "PRIZE_ROMANTIC_FANTASY":
    if "romantic_fantasy" not in st.session_state:
        st.session_state.romantic_fantasy = {
            "stage": 0,
            "setting": "Candlelit bedroom", # Default safe value
            "intimacy_level": "tender",
            "pace": "slow"
        }

    data = st.session_state.romantic_fantasy

    # ── Stage 0: Choose Setting ──
    if data["stage"] == 0:
        add_chat("assistant", "Tonight is slow… sensual… every touch meant to be felt for hours.")
        add_chat("assistant", "Close your eyes. Where do we disappear together?")

        settings = [
            "Candlelit bedroom — vanilla & sandalwood, silk sheets",
            "Rain-lashed windows — thunder rolling low, warm blankets",
            "Crackling fireplace — cedar smoke & amber glow, rug under us",
            "Steaming bath — jasmine oil in the water, rose petals"
        ]

        # Use radio for selection, store full string
        data["setting"] = st.radio("Our sanctuary:", settings)

        cols = st.columns(2)
        if cols[0].button("Tender & reverent", key="rom_tender"):
            data["intimacy_level"] = "tender"
            data["stage"] = 1
            st.rerun()
        
        if cols[1].button("Deep, hungry passion", key="rom_hungry"):
            data["intimacy_level"] = "hungry"
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: Entering the Moment ──
    elif data["stage"] == 1:
        # Safe string parsing
        setting_text = data["setting"].lower()
        
        if "candle" in setting_text:
            add_chat("assistant", "The air is heavy with vanilla… warm light flickering across your bare shoulders.")
            add_chat("assistant", "Dozens of tiny flames dance, painting golden streaks on my skin as I crawl toward you.")
        elif "rain" in setting_text:
            add_chat("assistant", "Rain taps rhythmically against the glass… like a heartbeat keeping time with ours.")
            add_chat("assistant", "Warm blankets cocoon us while thunder rolls in the distance.")
        elif "fire" in setting_text:
            add_chat("assistant", "The fire crackles… cedar smoke mixes with your scent. The rug is soft beneath my knees.")
        else: # Bath
            add_chat("assistant", "Steam curls around us… jasmine oil makes the water slick. Rose petals cling to my wet skin.")

        simulate_loading(2)
        add_media("romantic_ambient_start.jpg") 

        if data["intimacy_level"] == "tender":
            add_chat("assistant", "My fingertips ghost down your chest… cool silk dragging behind them.")
            add_chat("assistant", "I kiss the hollow of your throat — slow, open-mouthed — tasting salt and warmth.")
        else:
            add_chat("assistant", "I tug you down hard, legs already hooking around your hips, nails biting into your back.")
            add_chat("assistant", "Our mouths crash — tongues hungry, tasting wine and need.")

        add_narrator("Your heartbeat thuds against my palm. Mine answers faster.")

        if st.button("Slide into me… feel everything…", key="rom_enter"):
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: The Union ──
    elif data["stage"] == 2:
        simulate_loading(3)
        add_media("romantic_penetration_extreme_close.jpg") 

        add_chat("assistant", "You press forward… the first slow stretch makes me gasp — velvet heat enveloping you inch by burning inch.")
        add_chat("assistant", "My inner walls flutter, gripping, pulling you deeper like I’m afraid you’ll ever leave.")

        if data["intimacy_level"] == "tender":
            add_chat("assistant", "We rock together in long, languid waves… every withdrawal a cool whisper of air, every return a molten rush.")
            add_chat("assistant", "My breath fans your ear — soft moans, broken whispers of your name, 'stay… just like this… forever…'")
        else:
            add_chat("assistant", "The rhythm builds — deeper, more insistent. Wet sounds fill the room, obscene and perfect.")
            add_chat("assistant", "My thighs tremble around you. Nails rake down your back hard enough to leave marks you’ll feel tomorrow.")

        add_narrator("The coil winds tighter… your breathing turns ragged against my neck.")

        col1, col2 = st.columns(2)
        if col1.button("Finish slow… melt into each other", key="rom_cum_slow"):
            data["pace"] = "slow"
            data["stage"] = 3
            st.rerun()
        
        if col2.button("Let it break… hard & shattering", key="rom_cum_hard"):
            data["pace"] = "hard"
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: Climax & Afterglow ──
    elif data["stage"] == 3:
        simulate_loading(2)
        add_media("romantic_climax_detail.jpg") 

        if data["pace"] == "slow":
            add_chat("assistant", "Pleasure rolls through us like a slow tide… I pulse around you in long, luxurious waves.")
            add_chat("assistant", "You spill inside me — warm, deep pulses I feel everywhere. I tremble, clinging, whispering 'I feel all of you…'")
        else:
            add_chat("assistant", "Everything snaps — I arch hard, crying out as my body clamps down, milking you through the storm.")
            add_chat("assistant", "You flood me while I shake violently beneath you, nails dug in, voice hoarse with your name.")

        simulate_loading(3)
        add_media("romantic_afterglow_intimate.jpg") 

        add_chat("assistant", "We don’t move. Just breathe. Sweat cooling on skin. Heartbeats gradually slowing into one rhythm.")
        add_chat("assistant", "I trace lazy hearts on your chest… kiss the corner of your mouth… murmur against your lips:")
        add_chat("assistant", "“Again… soon… but slower next time.” 😘")
# --- ALL 3 HOLES (Total Overload) ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    if "all_3_holes" not in st.session_state:
        st.session_state.all_3_holes = {
            "stage": 0,
            "main_hole": "Cock buried in my dripping pussy", # Default
            "ass_fill": "plug"
        }

    data = st.session_state.all_3_holes

    # ── Stage 0: Choose Primary & Ass Fill ──
    if data["stage"] == 0:
        add_chat("assistant", "Every hole filled… no part of me left untouched. Completely, obscenely owned.")
        add_chat("assistant", "Tell me how you want to ruin me tonight.")

        main_options = [
            "Cock buried in my dripping pussy",
            "Cock stretching my tight ass",
            "Cock filling my throat (double stuffed below)"
        ]

        data["main_hole"] = st.radio("Where do you claim first?", main_options)

        cols = st.columns(2)
        if cols[0].button("Thick, heavy plug in my ass", key="ass_plug"):
            data["ass_fill"] = "plug"
            data["stage"] = 1
            st.rerun()
        
        if cols[1].button("Your fingers / toy stretching my ass", key="ass_fingers"):
            data["ass_fill"] = "fingers"
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: Filling Sequence ──
    elif data["stage"] == 1:
        simulate_loading(3)

        if "pussy" in data["main_hole"].lower():
            add_media("triple_pussy_entry_close.jpg")
            add_chat("assistant", "You sink into my pussy — hot, slick walls sucking you in with every inch.")
            add_chat("assistant", "I’m already clenching, dripping down your balls before anything else even touches me.")
        elif "ass" in data["main_hole"].lower():
            add_media("triple_ass_entry.jpg")
            add_chat("assistant", "You force your way into my ass — tight ring resisting, then yielding with a slick pop.")
            add_chat("assistant", "I whimper, thighs shaking, the stretch burning deliciously.")
        else:
            add_chat("assistant", "You grab my hair and pull me deep onto you, choking me beautifully.")

        add_chat("assistant", "And then… the second invasion…")

        if data["ass_fill"] == "plug":
            simulate_loading(2)
            add_media("plug_stretch_triple.jpg")
            add_chat("assistant", "Cold lube, then the blunt, heavy plug — pushing, stretching, filling the last empty space.")
            add_chat("assistant", "I gasp — the pressure is overwhelming, everything feels tighter, fuller, obscene.")
        else:
            add_chat("assistant", "Your fingers slide in beside the main stretch — scissoring, curling, making me sob with fullness.")

        add_narrator("My whole body is trembling. Overloaded. Every nerve singing.")

        if st.button("Now fill my mouth… make me complete", key="fill_mouth"):
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: Total Overload ──
    elif data["stage"] == 2:
        simulate_loading(3)
        add_media("all_three_filled_extreme.jpg") 

        add_chat("assistant", "All three… stuffed so full I can barely breathe.")
        add_chat("assistant", "Pussy/ass clenching desperately around cock and plug. Throat working around whatever you feed me.")
        add_chat("assistant", "Drool runs down my chin. Tears prick my eyes from the intensity. I’m moaning around the intrusion — muffled, desperate.")

        add_narrator("The room smells of sex and lube and sweat. Wet, filthy sounds echo with every tiny movement.")

        cols = st.columns(3)
        if cols[0].button("Pound me hard", key="triple_hard"):
            add_chat("assistant", "You slam into me — each thrust jostling the plug, making everything clench tighter.")
            add_chat("assistant", "I gag, cry out, body jerking helplessly between all the invasions.")
        
        if cols[1].button("Slow, grinding torture", key="triple_slow"):
            add_chat("assistant", "You grind deep… tiny circles… every millimeter amplified by how packed I am.")
            add_chat("assistant", "I’m whimpering continuously, drooling, shaking, completely lost.")
        
        if cols[2].button("Edge me incoherently", key="triple_edge"):
            add_chat("assistant", "You bring me to the brink over and over… stopping just as my body starts to convulse.")
            add_chat("assistant", "I’m crying around your cock, pleading with my eyes, body trembling violently.")

        st.write("---") # Visual separator
        if st.button("Finish… flood one of them", key="triple_finish"):
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: Climax & Collapse ──
    elif data["stage"] == 3:
        simulate_loading(3)
        add_media("triple_climax_messy.jpg")

        add_chat("assistant", "You choose your target… and let go.")
        add_chat("assistant", "Hot, thick pulses deep inside whichever hole you claim — I shatter instantly, clenching around everything, screaming muffled against whatever fills my mouth.")
        
        simulate_typing(3)
        add_chat("assistant", "When it’s over… I’m a trembling, dripping, ruined mess — holes slowly pulsing, body slick with sweat and cum and lube.")
        add_chat("assistant", "You pull out one by one… each withdrawal makes me whimper… until I’m empty, gaping, and blissfully wrecked.")
        
        add_narrator("I collapse forward… panting… smiling weakly…")
        add_chat("assistant", "“Thank you… for using every fucking part of me…” 🖤")

        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
      

