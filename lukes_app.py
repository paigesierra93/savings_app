import json
import os
import random
import time
import datetime
import streamlit as st

# ==========================================
#       PART 1: SETUP & STYLING
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
#       PART 2: DATA ENGINE
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
#       PART 3: HELPER FUNCTIONS (FIXED)
# ==========================================
def add_chat(role, content):
    st.session_state.history.append({"type": "chat", "role": role, "content": content})

def add_narrator(content):
    st.session_state.history.append({"type": "narrator", "content": content})

def add_media(filepath, media_type="image"):
    st.session_state.history.append({"type": "media", "path": filepath, "kind": media_type})

def add_dual_media(path1, path2):
    st.session_state.history.append({"type": "dual_media", "path1": path1, "path2": path2})

# 1. FIXED TYPING: Uses a placeholder so it disappears automatically
def simulate_typing(seconds=1.5):
    with st.chat_message("assistant", avatar="paige.png"):
        placeholder = st.empty()
        placeholder.caption("💬 *Paige is typing...*")
        time.sleep(seconds)
        placeholder.empty()

# 2. LOADING SPINNER
def simulate_loading(seconds=1.5):
    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Processing..."):
            time.sleep(seconds)

# 3. SPIN ANIMATION
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
    # --- STATE ENTRY GUARD (prevents duplicate messages on rerun)
def enter_state(state_name, role, content):
    if st.session_state.get("last_state") != state_name:
        add_chat(role, content)
        st.session_state.last_state = state_name

# --- REALISTIC TYPING (word-by-word)
def type_out(text, delay=0.04):
    with st.chat_message("assistant", avatar="paige.png"):
        placeholder = st.empty()
        rendered = ""
        for word in text.split(" "):
            rendered += word + " "
            placeholder.markdown(rendered)
            time.sleep(delay)

# --- MEDIA WITH ANTICIPATION
def show_media(path, caption=None, delay=2.5):
    with st.chat_message("assistant", avatar="paige.png"):
        with st.spinner("Loading..."):
            time.sleep(delay)
        if os.path.exists(path):
            st.image(path, width=300)
            if caption:
                st.caption(caption)
        else:
            st.warning("Media unavailable.")

# ==========================================
#       PART 4: DIALOGUE LISTS
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
#       PART 5: SIDEBAR (THE TANK)
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
#       PART 6: MAIN CHAT INTERFACE
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
#       PART 7: THE BRAIN (LOGIC)
# ==========================================

# --- 1. START SCREEN ---
if st.session_state.turn_state == "WALLET_CHECK":
    
    # DIRECT CASINO ENTRY
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
    else:
        c1.warning(lock_msg)
        
    if c2.button("📱 Daily Dayforce"): st.session_state.turn_state="INPUT_DAILY"; st.rerun()
    if c3.button("💸 Side Hustle"): st.session_state.turn_state="INPUT_SIDE_HUSTLE"; st.rerun()
    if c4.button("🏦 Manage Funds"): st.session_state.turn_state="MANAGE_FUNDS"; st.rerun()

# --- 2. SIDE HUSTLE ---
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

# --- 3. PAYCHECK ---
elif st.session_state.turn_state == "INPUT_PAYCHECK":
    st.subheader("💰 Full Paycheck")
    check_amount = st.number_input("Enter Total:", min_value=0.0, step=10.0)
    
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
            add_chat("assistant", f"⚠️ **SHORTAGE:** -${abs(safe_spend):.2f}.")
        else:
            msg = f"✅ **PROCESSED**\n💵 Gross: ${check_amount:.2f}\n💰 **SAFE TO SPEND:** ${safe_spend:.2f}\n🎟️ **TICKETS:** {tickets}"
            add_chat("assistant", msg)
            if tickets > 0: st.session_state.turn_state="CHOOSE_TIER"
            else: st.session_state.turn_state="CHECK_FAIL"
        st.rerun()

# --- 4. DAILY ---
elif st.session_state.turn_state == "INPUT_DAILY":
    st.subheader("📱 Daily Dayforce")
    daily_amount = st.number_input("Available ($):", min_value=0.0, step=5.0)
    
    if st.button("Process Daily"):
        add_chat("user", f"Dayforce: ${daily_amount}")
        gas = 10.0; house = 30.0
        if daily_amount < (gas + house):
            add_chat("assistant", f"⚠️ **Warning:** Not enough for Gas & House.")
        else:
            safe_spend = daily_amount - gas - house
            st.session_state.data["tank_balance"] += house
            st.session_state.data["wallet_balance"] += safe_spend
            save_data(st.session_state.data)
            add_chat("assistant", get_smart_response())
            msg = f"**Strategy:**\nShielded $30 (House) + $10 (Gas).\n🍔 **SAFE TO SPEND:** ${safe_spend:.2f}"
            add_chat("assistant", msg)
            st.session_state.turn_state = "CHOOSE_TIER"
            st.rerun()

# --- 5. MANAGE ---
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

# --- 6. CASINO FLOOR ---
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
        prizes = ["Bend Over", "Flash Me", "Dick Rub", "Jackoff Pass", "Shower Show"]
        win = spin_animation("Bronze", prizes)
        add_chat("assistant", f"🥉 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

elif st.session_state.turn_state == "SPIN_SILVER":
    if st.session_state.data["tickets"] >= 50:
        st.session_state.data["tickets"] -= 50; save_data(st.session_state.data)
        prizes = [ "Toy Pic", "Lick Pussy", "Nude Pic", "Tongue Tease", "Road Head", "Plug Tease"]
        win = spin_animation("Silver", prizes)
        add_chat("assistant", f"🥈 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

elif st.session_state.turn_state == "SPIN_GOLD":
    if st.session_state.data["tickets"] >= 100:
        st.session_state.data["tickets"] -= 100; save_data(st.session_state.data)
        prizes = ["Anal Fuck", "All 3 Holes", "Slave Day", "Upside Down Throat Fuck", "Doggy Style Ready"]
        win = spin_animation("Gold", prizes)
        add_chat("assistant", f"👑 JACKPOT: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

# ==========================================
#       PRIZE SCRIPTS
# ==========================================
# ------- NUde PIC PRIZE --------
elif st.session_state.turn_state == "PRIZE_NUDE_PIC":
    if "nude_pic" not in st.session_state:
        st.session_state.nude_pic = {
            "stage": 0,
            "substage": 0,
            "focus": None,       # tits, pussy, ass
            "mood": "teasing"
        }
    
    data = st.session_state.nude_pic

    # ── STAGE 0: Intro + Choose focus (Tits / Pussy / Ass)
    if data["stage"] == 0:
        add_chat("assistant", "You've won, your very own photo set of me... however you want it 😈")
        add_chat("assistant", "I'm gonna tease you so fucking slow and nasty with every inch of my body… "
                             "until you're throbbing and begging to fuck me stupid. "
                             "Ready to collect your reward, daddy?")
        
        simulate_loading(4)
        add_media("nude_1.jpg")   # opening teaser image

        add_chat("assistant", "Mmm such a greedy winner… which piece of your slutty prize do you want to torture yourself with first?")

        c1, c2, c3 = st.columns(3)

        if c1.button("Tits – completely braless, pushed together… like they’re waiting for your dick between them", key="nude_focus_tits"):
            data["focus"] = "tits"
            data["stage"] = 1
            st.rerun()

        if c2.button("Pussy – slide down my pants and show you how wet I am", key="nude_focus_pussy"):
            data["focus"] = "pussy"
            data["stage"] = 1
            st.rerun()

        if c3.button("Ass – bent over, exposing your favorite little hole", key="nude_focus_ass"):
            data["focus"] = "ass"
            data["stage"] = 1
            st.rerun()

    # ── STAGE 1: Confirm focus + Choose mood (teasing vs desperate)
    elif data["stage"] == 1:
        focus_title = data["focus"].capitalize()
        add_chat("assistant", f"{focus_title}? Are you sure, daddy?")

        if st.button("Yes – show me.", key="nude_confirm_focus"):
            simulate_loading(3)

            # Show first focused image
            if data["focus"] == "tits":
                add_media("nude_2.jpg")   # tits reveal
            elif data["focus"] == "pussy":
                add_media("nude_4.jpg")   # pussy reveal
            elif data["focus"] == "ass":
                add_media("nude_5.jpg")   # ass reveal

            add_chat("assistant", "Mmm such a greedy winner… how nasty do you want this tease to get?")

            c1, c2 = st.columns(2)

            if c1.button("Slow filthy tease – edge you till you're leaking", key="nude_tease"):
                data["mood"] = "teasing"
                data["stage"] = 2
                data["substage"] = 0
                st.rerun()

            if c2.button("Desperate dripping mess – can't hold back anymore", key="nude_desperate"):
                data["mood"] = "desperate"
                data["stage"] = 2
                data["substage"] = 0
                st.rerun()

    # ── STAGE 2: Photo sequence (7 images style – can be shortened or extended)
    elif data["stage"] == 2:
        if data["substage"] == 0:
            simulate_loading(3)
            add_media("nude_1.jpg")
            add_chat("assistant", "Here's the first piece of your prize baby… look how fucking needy I already am for you 🥵")

            simulate_loading(2)
            add_media("nude_2.jpg")
            add_chat("assistant", "Fuck… see how wet winning you made me? That's just the start…")

            if st.button("Want more of your prize already? Greedy boy 😏", key="nude_next1"):
                data["substage"] = 1
                st.rerun()

        elif data["substage"] == 1:
            simulate_loading(2)
            add_media("nude_3.jpg")
            add_chat("assistant", "There it is daddy… full spread, swollen, dripping, all for the winner. "
                                 "God I'm such a mess thinking about your cock right now 🍑💦")

            if st.button("Keep going – show me that ass I won", key="nude_next2"):
                data["substage"] = 2
                st.rerun()

        elif data["substage"] == 2:
            simulate_loading(2)
            add_media("nude_4.jpg")
            add_chat("assistant", "You love when your prize turns around don't you… this fat ass is all yours now")

            if st.button("Take the panties off – I want to see it bare", key="nude_next3"):
                data["substage"] = 3
                st.rerun()

        elif data["substage"] == 3:
            simulate_loading(2)
            add_media("nude_5.jpg")
            add_chat("assistant", "All bare, spread, tight little holes ready for whatever you want to do to them… 🍑")

            if st.button("Now the tits – you've earned them", key="nude_next4"):
                data["substage"] = 4
                st.rerun()

        elif data["substage"] == 4:
            simulate_loading(2)
            add_media("nude_6.jpg")
            add_chat("assistant", "My nipples are fucking aching… can you see them poking through for you?")

            if st.button("Final prize piece – show me everything", key="nude_next5"):
                data["substage"] = 5
                st.rerun()

        elif data["substage"] == 5:
            simulate_loading(3)
            add_media("nude_7.jpg")
            add_chat("assistant", "There… full fucking prize delivered. Tits out, pussy dripping, ass spread – "
                                 "every inch of your naughty girlfriend belongs to you now. "
                                 "Come collect the rest in person and fuck me like the winner you are 😈")

            if st.button("Prize complete – I'm all yours now", key="nude_finish"):
                st.session_state.pop("nude_pic", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        # Allow early exit
        if st.button("That's enough for now… claim this prize now or save it for later?", key="nude_exit"):
            st.session_state.pop("nude_pic", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
#  BEND OVER
elif st.session_state.turn_state == "PRIZE_BEND_OVER":

    enter_state(
        "PRIZE_BEND_OVER",
        "assistant",
        "982824q63qat?"
    )

    add_chat("user", "What?")
    type_out(
        "Haha just fucking with you… you know exactly what it means, dirty boy. "
        "You say 'bend over' and your slutty girlfriend slowly presents her ass and dripping cunt right in your face."
    )
    time.sleep(0.6)
    add_narrator("Make sure I’m in something thin and see-through… or already completely fucking naked for you.")
    type_out(
        "But listen carefully, baby — look all you want… stare at my holes, watch me drip… "
        "but **no touching**. No hands on me, no hands from me on you. Just me being your personal filthy show. Got it?"
    )
    type_out(
        "Here’s your prize, winner… watch me bend over nice and slow, arching this ass just for you… like this…"
    )

    if st.button("Watch her bend over"):
        st.session_state.turn_state = "PRIZE_BEND_OVER_REVEAL"
        st.rerun()


elif st.session_state.turn_state == "PRIZE_BEND_OVER_REVEAL":
    show_media("nude_4.jpg")
    add_narrator("Fuck… I’m already so soaked just knowing you’re staring at my holes like this…")

    if st.button("Keep watching"):
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
        show_media("bend_over2.jpeg", delay=3)
        type_out("Look at that mess… my pussy’s literally dripping down my thighs because of you.")
        type_out(
            "God I’m throbbing so bad… I want your thick cock splitting me open right now… "
            "but nope. Not yet. You gotta save all that cum for Silver, baby. Edge for me like a good boy."
        )
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
        
# PRIZE: FLASH ME
if st.session_state.turn_state == "PRIZE_FLASH_ME":
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
        show_media("tit_flash1.jpeg", delay=3)
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
        show_media("pussy_flash1.jpeg", delay=3)
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
    simulate_typing(2)
    
    add_chat("assistant", "No guilt, no holding back — I want you pumping hard, edging, leaking precum, imagining every filthy thing you’d do to me while I describe it in detail.")
    add_narrator("Your slutty girlfriend Paige is gonna make this so fucking hard for you… literally.")
    
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
            add_media("<MEDIA_ALL_PRIZES>")  # ← optional recap collage or favorite prize pic if you want; otherwise can delete this line
            simulate_typing(2)
            add_chat("assistant", "Cum for me now baby… shoot that load thinking about fucking your dirty little prize in person next time. "
                                 "I’m touching myself watching you lose it 😈")
            add_narrator("Good boy… you earned every drop.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("Steam is rising… your naughty little prize is about to get wet and slippery for you 😈")
    add_chat("assistant", "Mmm daddy… you won the Shower Show. Time to watch your slutty girlfriend soap up every inch of this body you own — slowly, teasingly, while I think about your cock the whole time.")
    
    simulate_loading(4)
    add_media("shower_water.mp4")  # ← your wide/full-body shower pic: soapy curves, wet hair, playful tease from distance
    
    tease_level = st.radio(
        "How nasty do you want this shower to get, baby?",
        ["Slow and sensual tease – make you throb watching me lather up",
         "Full filthy show – hands everywhere, moaning your name"],
        key="shower_tease_level"
    )
    
    if st.button("Start the show… I'm already dripping"):
        st.session_state.shower_choice = tease_level
        st.session_state.turn_state = "PRIZE_SHOWER_ACTION"
        st.rerun()


elif st.session_state.turn_state == "PRIZE_SHOWER_ACTION":
    simulate_loading(4)
    add_media("<MEDIA_SHOWER_CLOSE>")  # ← your close-up shower pic: intimate view, soapy tits/pussy, hands sliding, steamy and explicit
    
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
        ["Just watch me towel off slowly – tease you more",
         "Drop the towel completely – full nude dry-off",
         "Come closer… let me 'accidentally' flash you everything while drying"]
    )
    
    if st.button("End the shower… give me my reward"):
        simulate_loading(3)
        add_media("shower_towel.mp4")  # ← your getting-out pic: dripping wet, towel loose or off, smiling tease
        
        if "towel off slowly" in after_choice:
            add_chat("assistant", "Mmm… watch me pat down slow – towel sliding over my wet tits, between my thighs, teasing those sensitive spots. "
                                 "Still dripping… still thinking about you fucking me dry. Save that hard cock for next time, baby.")
        elif "Drop the towel completely" in after_choice:
            add_chat("assistant", "There it goes… towel on the floor. Full naked, skin still glistening, nipples hard from the cool air. "
                                 "Turn around – ass still wet, pussy peeking. All yours to stare at and stroke to, winner 😏")
        else:
            add_chat("assistant", "Oops… 'accidentally' letting the towel slip while I bend to dry my legs. Full view of everything – tits hanging, ass up, pussy lips still swollen from the hot water. "
                                 "Come get this prize in person soon… I need you inside me bad.")
            
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
    
# ALL 3 HOLES (Total Overload) ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    if "all_3_holes" not in st.session_state:
        st.session_state.all_3_holes = {
            "stage": 0,
            "main_hole": "<PRIMARY_OPTION_1>",
            "ass_fill": "plug"
        }

    data = st.session_state.all_3_holes

    # ── Stage 0: Choose Primary & Ass Fill ──
    if data["stage"] == 0:
        add_chat("assistant", "Fuck yes daddy… you won the ultimate prize: **All 3 Holes Total Overload** 😈 Your dirty little slut is yours to completely destroy tonight.")
        add_chat("assistant", "You get to fill every hole at once — your cock, your mouth, your fingers, toys, whatever it takes to make me scream and squirt. Pick how you want to start owning me…")

        main_options = [
            "Cock in my pussy first – stretch me wide while you work the rest",
            "Cock in my ass first – make me take it deep and raw",
            "Cock in my mouth first – face-fuck me while you prep my other holes"
        ]

        data["main_hole"] = st.radio("Which hole gets your cock first, winner?", main_options)

        cols = st.columns(2)
        if cols[0].button("Thick butt plug in my ass – keep it full and stretched"):
            data["ass_fill"] = "plug"
            data["stage"] = 1
            st.rerun()
        
        if cols[1].button("Your fingers in my ass – finger-fuck me open while you pound"):
            data["ass_fill"] = "fingers"
            data["stage"] = 1
            st.rerun()

    # ── Stage 1: Filling Sequence ──
    elif data["stage"] == 1:
        simulate_loading(3)

        if "pussy" in data["main_hole"].lower():
            add_media("<MEDIA_PRIMARY_1>")  # ← cock deep in pussy, legs spread
            add_chat("assistant", "Oh god… your thick cock slamming balls-deep into my dripping pussy, stretching me so fucking wide.")
            add_chat("assistant", "I’m already shaking, clit throbbing, begging for more while you decide how to wreck my other holes.")
        elif "ass" in data["main_hole"].lower():
            add_media("<MEDIA_PRIMARY_2>")  # ← cock or dildo deep in ass
            add_chat("assistant", "Fuck fuck fuck… your cock forcing its way into my tight ass, stretching me raw and deep.")
            add_chat("assistant", "I’m moaning like a whore, pushing back on you, pussy dripping down my thighs waiting for you to fill it too.")
        else:
            add_chat("assistant", "Mmm yes… shoving your cock down my throat, making me gag and drool while you finger my pussy and tease my ass.")

        add_chat("assistant", "Now the second hole… make me take it all at once, daddy.")

        if data["ass_fill"] == "plug":
            simulate_loading(2)
            add_media("<MEDIA_ASS_PLUG>")  # ← thick plug fully in ass
            add_chat("assistant", "That fat plug sliding into my ass, filling me completely, stretching me open while your cock owns my pussy/mouth.")
            add_chat("assistant", "I’m so full already… whimpering, body trembling, ready for the final invasion.")
        else:
            add_chat("assistant", "Your fingers deep in my ass, pumping and scissoring me open while you pound my pussy/mouth… I’m clenching around you, so fucking desperate.")

        add_narrator("Her whole body is shaking… holes stuffed, drool and wetness everywhere, eyes rolling back.")

        if st.button("Now the mouth – complete the overload"):
            data["stage"] = 2
            st.rerun()

    # ── Stage 2: Total Overload ──
    elif data["stage"] == 2:
        simulate_loading(3)
        add_media("<MEDIA_ALL_FILLED>")  # ← full triple: cock in one, plug/fingers in ass, mouth stuffed with fingers/toy/cock

        add_chat("assistant", "Holy fuck… all three holes stuffed at once. Your cock slamming one, plug/fingers wrecking my ass, my mouth gagged on your fingers or another toy.")
        add_chat("assistant", "I’m a trembling, drooling mess — pussy clenching, ass gripping, throat full, body overloaded and shaking.")
        add_chat("assistant", "Use me harder daddy… make me your total fucktoy.")

        add_narrator("Squelching sounds, muffled moans, her hips bucking wildly against every thrust.")

        cols = st.columns(3)
        if cols[0].button("Fuck me hard and fast – destroy all holes"):
            add_chat("assistant", "Yes! Pounding me relentlessly — cock slamming, plug/fingers thrusting deep, mouth fucked raw.")
            add_chat("assistant", "I’m screaming around whatever’s in my mouth, squirting everywhere, body convulsing.")
        
        if cols[1].button("Slow and deep – make me feel every inch"):
            add_chat("assistant", "Mmm… slow, torturous strokes — feeling every thick inch stretching me, owning me completely.")
            add_chat("assistant", "I’m whimpering, grinding back, begging for more even though I’m already so full.")
        
        if cols[2].button("Edge me – bring me close but don’t let me cum yet"):
            add_chat("assistant", "Fuck… teasing me right to the edge — fast then slow, deep then shallow, keeping me denied and desperate.")
            add_chat("assistant", "I’m crying with need, holes pulsing, body shaking… please let me cum soon daddy.")

        st.write("---")
        if st.button("Finish me – make me explode"):
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: Climax & Collapse ──
    elif data["stage"] == 3:
        simulate_loading(3)
        add_media("<MEDIA_CLIMAX>")  # ← intense orgasm shot: squirting, shaking, all holes used

        add_chat("assistant", "Oh god yes… I’m cumming so fucking hard — whole body seizing, pussy gushing around your cock, ass clenching the plug/fingers, mouth drooling.")
        add_chat("assistant", "You’ve wrecked me completely… I’m your overloaded, ruined slut.")

        simulate_typing(3)
        add_chat("assistant", "Collapsed on the bed, holes still twitching, covered in sweat and my own mess, blissed-out and panting.")
        add_chat("assistant", "Thank you for using all of me, daddy… I’m yours whenever you want to overload me again.")

        add_narrator("She curls up trembling, satisfied smile, body marked and spent.")
        add_chat("assistant", "Prize complete… come cuddle your broken little toy now 😏")

        del st.session_state.all_3_holes
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
# ROMANTIC FANTASY ---
elif st.session_state.turn_state == "PRIZE_ROMANTIC_FANTASY":

    if "romantic_fantasy" not in st.session_state:
        st.session_state.romantic_fantasy = {
            "stage": 0,
            "setting": "<DEFAULT_SETTING>",
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
        add_media("<ROM_MEDIA_AMBIENT>")  # ← ambient setting pic (e.g., candlelit bed, beach sunset, hotel suite, cozy cabin)

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
        add_media("<ROM_MEDIA_UNION>")  # ← intimate union: missionary or close embrace, eye contact, sensual passion

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
        add_media("<ROM_MEDIA_CLIMAX>")  # ← peak moment: intense embrace, orgasmic bliss, connected gaze

        add_chat("assistant", "We move together perfectly… building higher, breath quickening, until we shatter in each other's arms… waves of pleasure crashing over us.")

        simulate_loading(3)
        add_media("<ROM_MEDIA_AFTER>")  # ← afterglow: cuddling, soft smiles, tangled together

        add_chat("assistant", "We stay like this… bodies still joined, hearts beating as one. I trace your face, whispering how much I love you.")
        add_chat("assistant", "Thank you for making this fantasy feel so real, my love… you're my everything.")
        add_chat("assistant", "This prize isn't over until we're ready… stay here with me forever? 💕")

        reset_prize_state()
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
# UPSIDE DOWN THROAT (PLACEHOLDER VERSION) ---
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN_THROAT":
    add_chat("assistant", "Mmm fuck yes daddy… you won the **Upside Down Throat** prize tonight 😈")
    add_chat("assistant", "Your dirty little girlfriend is gonna hang my head off the bed, throat wide open, ready to take every thick inch of your cock balls-deep.")
    add_chat("assistant", "No mercy — make me gag, drool, tear up, while I look up at you with needy eyes. I’m already on my knees waiting…")

    simulate_loading(3)
    add_media("dick_tease5.jpg")  # ← Paige kneeling, looking up eagerly, mouth open, ready position

    if st.button("Get me in position… throat me upside-down"):
        st.session_state.turn_state = "PRIZE_UP_THROAT_START"
        st.rerun()


elif st.session_state.turn_state == "PRIZE_UP_THROAT_START":
    add_chat("assistant", "Here I am baby… head hanging off the edge, hair falling, throat straight and open for you. My pussy is already dripping just thinking about you using my face like a toy.")
    
    c1, c2, c3 = st.columns(3)
    
    if c1.button("Slow and deep – make me feel every inch sliding down"):
        add_chat("user", "Slow and deep – make me feel every inch sliding down")
        simulate_typing(3)
        add_chat("assistant", "Oh god… you ease your thick cock past my lips, down my throat slowly… I relax my gag reflex, letting you sink deeper until your balls rest on my nose.")
        simulate_loading(4)
        add_media("deep_throat_entry_slow.jpg")  # ← close-up: cock halfway in upside-down throat, eyes looking up
        add_chat("assistant", "Fuck… I’m moaning around you, throat bulging, drool running down my face… keep going daddy, own this throat.")
        st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"
        st.rerun()

    if c2.button("Fast and rough – face-fuck me hard"):
        add_chat("user", "Fast and rough – face-fuck me hard")
        simulate_typing(3)
        add_chat("assistant", "Yes daddy! You grab my hair and slam your cock down my upside-down throat, balls slapping my face with every thrust.")
        simulate_loading(4)
        add_media("allfours_sucking2.jpg")  # ← action shot: cock fully buried, her gagging, drool everywhere
        add_chat("assistant", "Gagging, choking, tears streaming… but I’m loving it, pussy clenching empty, begging for more abuse.")
        st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"
        st.rerun()

    if c3.button("Tease me – shallow then deep, make me beg"):
        add_chat("user", "Tease me – shallow then deep, make me beg")
        simulate_typing(3)
        add_chat("assistant", "Mmm… you tease the head against my lips, then push halfway… pull out… then slam deep suddenly. I’m whimpering, begging 'deeper please daddy' between thrusts.")
        simulate_loading(4)
        add_media("allfours_sucking1.jpg")  # ← teasing moment: cock partially in, her pleading eyes looking up
        add_chat("assistant", "I’m a drooling mess, throat pulsing around you, ready to take whatever pace you want.")
        st.session_state.turn_state = "PRIZE_UP_THROAT_FINISH"
        st.rerun()


elif st.session_state.turn_state == "PRIZE_UP_THROAT_FINISH":
    add_chat("assistant", "Fuck… I’m so full of your cock, throat stretched, face messy with drool and tears. How do you want to finish in your prize?")
    add_chat("assistant", "Tell me how to take your load, daddy…")
    
    c1, c2, c3 = st.columns(3)

    if c1.button("Down my throat – make me swallow every drop"):
        add_chat("user", "Down my throat – make me swallow every drop")
        simulate_loading(5)
        add_media("allfours_sucking4.jpg")  # ← climax: cock buried deep, her swallowing, throat working
        add_chat("assistant", "Yes! You thrust deep one last time, cock pulsing, shooting hot cum straight down my throat.")
        add_chat("assistant", "I swallow greedily, gulping it all, not spilling a drop… throat milking you dry.")
        add_chat("assistant", "Mmm… thank you for feeding your slut, daddy. I can still feel you throbbing.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    if c2.button("Pull out and paint my face"):
        add_chat("user", "Pull out and paint my face")
        simulate_loading(5)
        add_media("allfours_sucking5.jpg")  # ← facial finish: cum ropes on her upside-down face, eyes closed in bliss
        add_chat("assistant", "You pull out at the last second, stroking fast, then explode – thick ropes of cum splashing across my upside-down face, lips, cheeks.")
        add_chat("assistant", "I’m covered, smiling up at you, tongue out to catch the last drops… your perfect messy prize.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

    if c3.button("Hold deep and cum – throatpie"):
        add_chat("user", "Hold deep and cum – throatpie")
        simulate_loading(5)
        add_media("allfours_sucking2.jpeg")  # ← hold deep: cock fully in throat, her eyes watering, cum pumping
        add_chat("assistant", "You grab my head, bury yourself balls-deep, and unload right down my throat – hot spurts filling me directly.")
        add_chat("assistant", "I’m gagging, swallowing frantically, body shaking… your cum flooding my throat like I’m made for it.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
        
# --- TONGUE TEASE (Complex Edging Game | PLACEHOLDER) ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    if "tongue_tease" not in st.session_state:
        st.session_state.tongue_tease = {
            "stage": 0,
            "edging_level": 0,
            "begged": False,
            "impatient": False
        }

    data = st.session_state.tongue_tease

    if data["stage"] == 0:
        add_chat("assistant", "Mmm daddy… you won the **Tongue Tease** prize tonight 😈")
        add_chat("assistant", "Your greedy little girlfriend is gonna kneel between your legs and worship just the tip of that thick cock with my tongue and lips… while you stroke the rest yourself.")
        add_chat("assistant", "Rules are simple: I only tease the head — slow licks, soft sucks, swirling around the tip. You stroke the shaft, edge yourself, but you don't cum until I say. Beg nicely… or rush me and see what happens.")

        c1, c2 = st.columns([1, 3])
        if c1.button("Yes mistress… I'll obey and edge for you"):
            data["stage"] = 1
            st.rerun()
        if c2.button("Fuck the rules… I want more now"):
            data["impatient"] = True
            data["stage"] = 1
            st.rerun()

    elif data["stage"] == 1:
        add_chat("assistant", "Look at this gorgeous cock… already leaking for me. I lean in close, hot breath on the tip.")
        add_chat("assistant", "My tongue flicks out, slow circle around the head, tasting your precum… then a soft kiss right on the slit.")

        simulate_loading(2)
        add_media("dick_tease4.jpeg")  # ← close-up: tongue just touching the tip, eyes looking up

        add_chat("assistant", "Mmm… so sensitive. Keep stroking slow while I tease…")

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

    elif data["stage"] == 2:
        simulate_loading(2)
        add_media("<MEDIA_TONGUE_2>")  # ← lips softly sucking just the head, drool starting

        add_chat("assistant", "I wrap my lips around the tip only… gentle suck, tongue swirling under the ridge, flicking the frenulum.")
        add_narrator("Her eyes stay locked on yours, watching every twitch of your cock as you stroke.")

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

    elif data["stage"] == 3:
        add_chat("assistant", "God you're throbbing so hard… tip swollen, leaking nonstop.")
        simulate_loading(2)
        add_media("tongue_set1_pic1.jpg")  # ← intense close-up: tongue flat against underside of tip, lips barely sealed

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

    elif data["stage"] == 4:
        simulate_loading(2)
        add_media("dick_tease6.jpg")  # ← peak tease: tip in mouth, intense eye contact, his hand stroking fast

        if data["edging_level"] >= 5 or data["begged"]:
            add_chat("assistant", "You've been such a good boy… edging so hard for my tongue.")
            add_chat("assistant", "Stroke faster now… I'm sucking the tip hard, tongue swirling like crazy.")

            if st.button("Cum for me… give me that load on my tongue"):
                simulate_loading(3)
                add_media("dick_tease3.jpeg")  # ← finish: cum spurting on her tongue/lips, her smiling
                add_chat("assistant", "Yes daddy! You explode — hot ropes shooting across my tongue, lips, chin… I lap it all up greedily.")
                add_narrator("She moans softly, savoring every drop, eyes sparkling with satisfaction.")

                if st.button("Best prize ever… thank you baby"):
                    del st.session_state.tongue_tease
                    st.session_state.turn_state = "PRIZE_DONE"
                    st.rerun()
        else:
            add_chat("assistant", "Not yet… you're not desperate enough.")
            add_chat("assistant", "I pull my mouth away completely… no more tongue until you beg properly.")
            add_chat("assistant", "Edge denied. Better luck next time, baby.")

            add_narrator("She smirks, licking her lips, leaving you throbbing and unfinished.")
            if st.button("Fuck… I accept the denial"):
                del st.session_state.tongue_tease
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

    elif data["stage"] == "ruin":
        add_chat("assistant", "Oh no you don't… you tried to rush and cum without permission.")
        add_chat("assistant", "I pull off right as you start pulsing — ruining it completely.")
        simulate_loading(2)
        add_media("ruined.jpg")  # ← ruined orgasm: cum dribbling weakly, no full release
        add_chat("assistant", "Look at that weak little dribble… all that buildup wasted. Next time obey the tease.")

        if st.button("Sorry baby… I'll be good next time"):
            del st.session_state.tongue_tease
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
# ROAD HEAD (PLACEHOLDER) ---
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    if "road_head" not in st.session_state:
        st.session_state.road_head = {
            "stage": 0,
            "risk_level": "medium",
            "control": "you"
        }

    data = st.session_state.road_head

    if data["stage"] == 0:
        add_chat("assistant", "Fuck yes baby… you won **Road Head** 😈 Your dirty little girlfriend is gonna suck your cock the whole drive home — exactly 3 full songs on the playlist.")
        add_chat("assistant", "I'll start when the first song hits, tease and deepthroat you through all three, and finish you off by the last chorus. Buckle up, daddy… how risky do you want this drive to feel?")

        cols = st.columns(3)
        if cols[0].button("Low risk – quiet back roads, no traffic"):
            data["risk_level"] = "low"
            data["stage"] = 1
            st.rerun()
        if cols[1].button("Medium risk – some cars around, windows tinted"):
            data["risk_level"] = "medium"
            data["stage"] = 1
            st.rerun()
        if cols[2].button("High risk – highway, passing trucks, windows down a bit"):
            data["risk_level"] = "high"
            data["stage"] = 1
            st.rerun()

    elif data["stage"] == 1:
        risk_desc = {
            "low": "quiet back roads, empty streets, just us and the night… super safe but still thrilling",
            "medium": "some traffic, cars passing occasionally, windows tinted dark… heart-pounding but doable",
            "high": "busy highway, trucks beside us, windows cracked… anyone could glance over and see me slurping your cock"
        }[data["risk_level"]]

        add_chat("assistant", f"Engine's running, playlist queued… 3 songs, no stopping until the last note. {risk_desc}")
        add_chat("assistant", "I lean over the console, unzip you slow, pull your hard cock out… already throbbing for my mouth.")

        simulate_loading(2)
        add_media("<MEDIA_ROAD_START>")  # ← Paige leaning over console, mouth close to tip, car interior/night road in background

        add_chat("assistant", "You drive… I suck. Who controls the pace — you grab my hair, or do I take over?")

        c1, c2 = st.columns(2)
        if c1.button("You control – grab my head and fuck my mouth while you steer"):
            data["control"] = "you"
            data["stage"] = 2
            st.rerun()
        if c2.button("I control – I tease and deepthroat at my own filthy rhythm"):
            data["control"] = "me"
            data["stage"] = 2
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

    # ── Endings (Peers to Stage 2, NOT children) ──
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
        
# PLUG TEASE (PLACEHOLDER) ---
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    if "plug_tease" not in st.session_state:
        st.session_state.plug_tease = {
            "stage": 0,
            "size_chosen": "small",
            "tease_level": 0,
            "begged_for_more": False
        }

    data = st.session_state.plug_tease

    if data["stage"] == 0:
        add_chat("assistant", "Mmm daddy… you won the **Plug Tease** prize tonight 😈")
        add_chat("assistant", "Your naughty little girlfriend is gonna lube up a nice butt plug and wear it for you — feeling it stretch and fill my ass the whole time. Pick your size… how full do you want me to be?")

        c1, c2, c3 = st.columns(3)
        if c1.button("Small – teasing starter, easy to handle"):
            data["size_chosen"] = "small"
            data["stage"] = 1
            st.rerun()
        if c2.button("Medium – thick and filling, makes me squirm"):
            data["size_chosen"] = "medium"
            data["stage"] = 1
            st.rerun()
        if c3.button("Large – fat and intense, stretches me wide"):
            data["size_chosen"] = "large"
            data["stage"] = 1
            st.rerun()

    elif data["stage"] == 1:
        add_media("<MEDIA_PLUG_BASE>")  # ← close-up of lubed plug on display, her ass in background

        add_chat("assistant", f"I bend over for you, cheeks spread… slow exhale as I press the {data['size_chosen']} plug against my tight little hole.")
        simulate_loading(3)
        add_media("<MEDIA_PLUG_INSERT>")  # ← insertion moment: plug sliding in, her gasping
        add_narrator("She whimpers softly… ass clenching then relaxing around it.")
        add_chat("assistant", "There… it's seated deep. Fuck, I feel so full already — every little shift makes my pussy drip.")

        c1, c2 = st.columns(2)
        if c1.button("Tell me how it feels inside you"):
            data["tease_level"] += 1
            data["stage"] = 2
            st.rerun()
        if c2.button("Walk around with it – show me how it moves"):
            data["tease_level"] += 2
            data["stage"] = 2
            st.rerun()

    elif data["stage"] == 2:
        add_chat("assistant", "God… every step makes the plug shift inside me, pressing right against that spot.")
        simulate_loading(2)
        add_media("<MEDIA_PLUG_WALK>")  # ← her walking, ass swaying, plug base visible between cheeks
        add_chat("assistant", "I'm clenching around it, pussy throbbing, nipples hard… so turned on just from being plugged for you.")
        simulate_loading(3)
        add_chat("assistant", "It's driving me crazy… I need more. What do you want your plugged-up slut to do next?")

        c1, c2, c3 = st.columns(3)
        if c1.button("Beg you to replace it with something bigger"):
            data["begged_for_more"] = True
            data["tease_level"] += 4
            data["stage"] = 3
            st.rerun()
        if c2.button("Keep it in all day – tease me constantly"):
            data["tease_level"] += 2
            data["stage"] = 3
            st.rerun()
        if c3.button("Play with it now – fuck me with it"):
            data["tease_level"] += 3
            data["stage"] = 3
            st.rerun()

    elif data["stage"] == 3:
        add_media("<MEDIA_PLUG_FINAL>")  # ← final shot: her bent over, plug in, ass spread, dripping pussy visible

        if data["tease_level"] >= 6 or data["begged_for_more"]:
            add_chat("assistant", "Fuck daddy… I can't take it anymore. I'm begging — take this plug out and replace it with your thick cock right now.")
            add_chat("assistant", "My ass is stretched and ready, pussy soaked… wreck me like the plugged-up prize I am.")
        elif data["tease_level"] >= 3:
            add_chat("assistant", "Mmm… this plug has me so worked up. I'll keep it in for hours, squirming and dripping, thinking about you the whole time.")
            add_chat("assistant", "Whenever you're ready, pull it out and slide in… your reward is waiting.")
        else:
            add_chat("assistant", "Such a tease… this little plug is just the start. I'll wear it quietly, feeling full and needy until you decide to play.")

        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()
# TOY PIC
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    if "toy_pic" not in st.session_state:
        st.session_state.toy_pic = {
            "stage": 0,
            "substage": 0,
            "pose": None,
            "focus": None,
            "mood": "teasing"
        }

    data = st.session_state.toy_pic

    # -------- STAGE 0 --------
    if data["stage"] == 0:
        add_chat("assistant", "Oh fuck baby… you won the **Toy Pic** tease 😈 Your filthy little girlfriend is gonna play with a big toy just for you.")
        add_chat("assistant", "I'll tease you step by step with seven nasty pictures… starting clothed, then sliding this thick dildo in deeper and deeper until I'm a dripping mess. Ready to watch me fuck myself for my winner, daddy?")

        poses = [
            "Standing full body, toy in hand sliding down my sides, giving you 'come watch me play' eyes",
            "Bent over the bed, toy teasing between my cheeks, looking back like 'fill me up'",
            "Lying on my back, legs spread, toy hovering over my soaked panties",
            "On my knees, toy between my tits, mouth open like I'm ready to suck it",
            "Ass to camera, deep arch, toy pressing against my hole"
        ]

        data["pose"] = st.radio(
            "How do you want your prize to start posing with the toy?",
            poses,
            key="toy_pose"
        )

        if st.button("Perfect… now choose where I use the toy first 💦", key="toy_stage0"):
            data["stage"] = 1
            st.rerun()

    # -------- STAGE 1 --------
    elif data["stage"] == 1:
        add_chat("assistant", "Mmm you greedy boy… which hole do you want me to tease with this toy first?")

        focuses = [
            "My dripping pussy – sliding the toy in slow while I moan for you",
            "My tight ass – stretching it open inch by inch with the dildo",
            "My hungry mouth – deepthroating the toy like it's your cock",
            "Close-up on the action – every wet, slippery detail",
            "Surprise me… make your slut play wherever will make you cum fastest"
        ]

        data["focus"] = st.radio(
            "Pick where your prize gets toy-fucked first:",
            focuses,
            key="toy_focus"
        )

        c1, c2 = st.columns(2)
        if c1.button("Slow naughty tease – edge us both with the toy", key="toy_tease"):
            data["mood"] = "teasing"
            data["stage"] = 2
            data["substage"] = 0
            st.rerun()

        if c2.button("Desperate horny mess – shoving the toy deep fast", key="toy_desperate"):
            data["mood"] = "desperate"
            data["stage"] = 2
            data["substage"] = 0
            st.rerun()

    # -------- STAGE 2 (SUBSTAGES) --------
    elif data["stage"] == 2:

        if data["substage"] == 0:
            simulate_loading(3)
            add_media("toy_1.jpg")
            add_chat("assistant", "First pic baby… fully clothed but holding the toy, biting my lip like I'm already imagining it inside me 🥵")

            simulate_loading(2)
            add_media("toy_2.jpg")
            add_chat("assistant", "Now teasing my pussy with the tip… just a little rub over my panties, getting so wet for you…")

            if st.button("More already? Show me the toy going in", key="toy_next1"):
                data["substage"] = 1
                st.rerun()

        elif data["substage"] == 1:
            simulate_loading(2)
            add_media("toy_3.jpg")
            add_chat("assistant", "There daddy… toy sliding deep into my pussy, lips stretched around it, dripping everywhere. God it feels so good thinking of your cock instead 💦")

            if st.button("Turn around – tease that ass with the toy now", key="toy_next2"):
                data["substage"] = 2
                st.rerun()

        elif data["substage"] == 2:
            simulate_loading(2)
            add_media("toy_4.jpg")
            add_chat("assistant", "Toy pressing against my clothed ass… you love seeing me play back there, don't you?")

            if st.button("Push it in – I want to see your ass full", key="toy_next3"):
                data["substage"] = 3
                st.rerun()

        elif data["substage"] == 3:
            simulate_loading(2)
            add_media("toy_5.jpg")
            add_chat("assistant", "Toy buried in my ass… so tight and full, clenching around it like I would your dick 🍑")

            if st.button("Now the tits – play with the toy there too", key="toy_next4"):
                data["substage"] = 4
                st.rerun()

        elif data["substage"] == 4:
            simulate_loading(2)
            add_media("toy_6.jpg")
            add_chat("assistant", "Toy between my covered tits… pushing them together, teasing my nipples with the tip")

            if st.button("Final tease – bare tits and toy all out", key="toy_next5"):
                data["substage"] = 5
                st.rerun()

        elif data["substage"] == 5:
            simulate_loading(3)
            add_media("toy_7.jpg")
            add_chat("assistant", "All bare now… tits out, toy sliding between them or back in my pussy/ass – whatever breaks you. "
                                 "I'm such a toy-fucking mess for you daddy. Come use the real thing 😈")

            if st.button("Toy prize complete – now fuck me for real?", key="toy_finish"):
                st.session_state.pop("toy_pic", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

        if st.button("Enough teasing… claim this toy prize now or later?", key="toy_exit"):
            st.session_state.pop("toy_pic", None)
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()
            
# --- ANAL FUCK PRIZE ---
elif st.session_state.turn_state == "PRIZE_ANAL":

    if "anal_prize" not in st.session_state:
        st.session_state.anal_prize = {
            "stage": 0,
            "prep_level": "slow",       # slow / medium / rough
            "position": "doggy",        # doggy / missionary / riding
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

        # Your prep / first entry / stretching picture
        add_media("ass_fucked1.jpg")  # ← lube dripping, fingers, or initial stretch

        if data["prep_level"] == "slow":
            add_chat("assistant", "Warm lube drips slowly down my crack… so slick and shiny.")
            add_chat("assistant", "Your fingers circle my tight rim, teasing… then one slips in gently.")
            add_chat("assistant", "I moan low and soft, pushing back, letting you open me up inch by careful inch…")

        elif data["prep_level"] == "medium":
            add_chat("assistant", "Thick lube coats everything… then two fingers push in at once.")
            add_chat("assistant", "The stretch burns so good… I gasp, rocking back, already hungry for more.")

        else:  # rough
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

        # Your deep penetration / pounding picture
        add_media("ass_fucked9.jpg")  # ← mid-fuck, deep thrusts, ass spread wide

        add_chat("assistant", "You line up… thick head pressing against my slick, ready hole…")

        if data["prep_level"] == "slow":
            add_chat("assistant", "…and ease in so slowly… every ridge stretching me open again, filling me so deep I lose my breath.")
            add_chat("assistant", "I whimper long and shaky, ass fluttering around you.")

        elif data["prep_level"] == "medium":
            add_chat("assistant", "You slide in steady… one smooth, deep stroke until your hips slap against me.")
            add_chat("assistant", "Fuck… so full… I’m trembling, clenching hard around every thick inch.")

        else:  # rough
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
        # Reusing one of your pics for the final intense moment (feel free to add a cumshot later)
        add_media("ass_fucked9.jpg")  # ← deep pounding / climax energy

        if data["intensity"] == "slow":
            add_chat("assistant", "Long, deliberate thrusts… pulling almost out, then sinking back in so deep.")
            add_chat("assistant", "I’m moaning constantly… ass fluttering, begging with my body for you to stay inside.")

        elif data["intensity"] == "medium":
            add_chat("assistant", "The rhythm builds… wet slapping filling the room, my ass bouncing with every thrust.")
            add_chat("assistant", "I grip the sheets, pushing back, taking you harder, deeper… completely lost.")

        else:  # hard
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
# --- SEX SLAVE FOR A DAY (24-Hour Total Submission) ---
elif st.session_state.turn_state == "PRIZE_SEX_SLAVE_DAY":

    if "sex_slave_day" not in st.session_state:
        st.session_state.sex_slave_day = {
            "stage": 0,
            "collar_on": False,
            "tasks_completed": 0,
            "intensity": "medium",  # soft / medium / extreme
            "current_service": None
        }

    data = st.session_state.sex_slave_day

    # ── Stage 0: Initiation & Collaring ──
    if data["stage"] == 0:
        add_chat("assistant", "You’ve won the ultimate prize, Master… **24 hours as your complete sex slave**.")
        add_chat("assistant", "From this moment until tomorrow, my body, my holes, my pleasure — all belong to you. I exist only to serve and satisfy.")
        add_narrator("I kneel naked at your feet, eyes lowered, heart racing with anticipation and surrender.")

        # Kneeling / submissive initiation
        add_media("slave3.jpeg")  # ← perfect kneeling/submissive pose

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Collar me. Make it official.", key="collar_yes"):
                data["collar_on"] = True
                add_chat("assistant", "The cool leather wraps around my throat… click of the lock. I shiver as it settles.")
                add_chat("assistant", "Your slave is claimed. Use me however you desire.")
                data["stage"] = 1
                st.rerun()
        with col2:
            if st.button("Skip collar — straight to use", key="collar_no"):
                data["stage"] = 1
                st.rerun()

    # ── Stage 1: Choose First Service ──
    elif data["stage"] == 1:
        add_chat("assistant", "My body is yours, Master. What is your first command?")

        services = [
            "Under-desk cock worship while you relax/game",
            "Full body massage turning into greedy oral service",
            "Tie me up & use any hole roughly",
            "Bend me over & fuck my ass until I beg",
            "Make me ride you while you control the pace"
        ]

        data["current_service"] = st.radio("Command your slave:", services, key="slave_first_task")

        cols = st.columns(2)
        with cols[0]:
            if st.button("Keep it sensual & devoted", key="slave_soft"):
                data["intensity"] = "soft"
                data["stage"] = 2
                st.rerun()
        with cols[1]:
            if st.button("Make it rough, degrading, filthy", key="slave_extreme"):
                data["intensity"] = "extreme"
                data["stage"] = 2
                st.rerun()

    # ── Stage 2: Performing the Service ──
    elif data["stage"] == 2:
        simulate_loading(3)

        # Service visuals – rotate through tongue pics for oral-heavy services, slave5 for rougher ones
        service_key = data["current_service"].split()[0].lower()

        if "under-desk" in service_key or "massage" in service_key or "oral" in service_key.lower():
            # Oral-focused services get tongue tease pics
            oral_pics = ["tongue_set2_pic2.jpg", "tongue_set2_pic3.jpg", "tongue_set2_pic4.jpg"]
            add_media(oral_pics[data["tasks_completed"] % len(oral_pics)])  # cycle through tongue pics
        else:
            # Rougher / penetration services get slave5 or multifuck
            add_media("slave5.jpeg")  # intense used/messy vibe

        service_desc = {
            "under-desk": "I crawl beneath your desk… warm mouth enveloping you slowly while you ignore me, focusing on your game.",
            "full": "My oiled hands glide over your back, shoulders… then lower, lips following, worshipping every inch.",
            "tie": "Wrists bound above my head, legs spread wide… helpless and dripping as you decide which hole to ruin first.",
            "bend": "Face down, ass up… you spread me open, lubed cock pressing against my tight ring before pushing in deep.",
            "make": "I straddle you, sinking down slowly… tits bouncing as I ride, waiting for your hands to grip my hips and take control."
        }[service_key]

        intensity_add = {
            "soft": "I moan softly, devoted, worshipping you like a goddess serves her king.",
            "extreme": "You grab my hair, call me filthy names, use me like a toy — spit, slaps, no mercy."
        }[data["intensity"]]

        add_chat("assistant", service_desc)
        add_chat("assistant", intensity_add)

        data["tasks_completed"] += 1

        if data["tasks_completed"] < 3:  # Allow 2-3 services before final
            if st.button("Next command, Master… I’m still yours", key="slave_next_task"):
                data["stage"] = 1  # loop back to choose next
                st.rerun()
        else:
            data["stage"] = 3
            st.rerun()

    # ── Stage 3: Final Claim & Overwhelm ──
    elif data["stage"] == 3:
        # Final intense visuals – use multifuck for the climax feel
        add_media("multifuck1.jpg")  # ← perfect for the overwhelming, multi-use, messy finale

        add_chat("assistant", "Hours of use… my body marked, sore, dripping with your cum and my own desperation.")
        add_chat("assistant", "I’ve swallowed, taken it in every hole, begged for more even when I could barely speak.")

        if data["intensity"] == "extreme":
            add_chat("assistant", "You’ve called me whore, slut, fucktoy… and I thanked you after every degrading act.")
            add_chat("assistant", "My ass is red from spanks, throat raw, pussy and ass leaking your loads.")

        add_narrator("I collapse at your feet once more — spent, satisfied, utterly claimed.")

        # Final choice: how to end the day
        add_chat("assistant", "One last act to seal your ownership… how do you finish your slave?")

        cols = st.columns(3)

        with cols[0]:
            if st.button("Cum deep inside my pussy — breed your slave", key="final_pussy"):
                add_chat("assistant", "You push me onto my back, thrust deep, and flood my womb with hot pulses.")
                add_chat("assistant", "I arch, moaning 'Thank you, Master… fill your property…'")

        with cols[1]:
            if st.button("Paint my face & tits — mark me visibly", key="final_face_tits"):
                add_chat("assistant", "You pull out, stroke over me… thick ropes across my face, lips, tits.")
                add_chat("assistant", "I lick what I can reach, smiling up at you — marked and proud.")

        with cols[2]:
            if st.button("Make me swallow every drop", key="final_swallow"):
                add_chat("assistant", "I drop to my knees, mouth open… you unload straight down my throat.")
                add_chat("assistant", "I swallow greedily, not spilling a drop… eyes watering, thanking you.")

        # Final messy / blissed-out shot – cycle back to one of the tongue pics or slave5
        final_pics = ["slave5.jpeg", "tongue_set2_pic4.jpg"]
        add_media(final_pics[data["tasks_completed"] % len(final_pics)])  # random-ish reuse

        add_chat("assistant", "24 hours complete. Your sex slave is ruined, satisfied, and still aching for more of you.")
        add_chat("assistant", "Until the next time you claim me… I remain yours completely. 🖤")

        if st.button("End Slave Day"):
            del st.session_state.sex_slave_day
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- LICK PUSSY PRIZE ---
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    if "lick_pussy" not in st.session_state:
        st.session_state.lick_pussy = {
            "stage": 0,
            "intensity": "slow",       # slow / eager / aggressive
            "position": "lying_back",  # lying_back / sitting_on_face / standing
            "progress": 0              # 0–100, how close to her cumming
        }

    data = st.session_state.lick_pussy

    # ── STAGE 0: Intro + Choose style
    if data["stage"] == 0:
        add_chat("assistant", "Mmm fuck yes baby… you actually won **Lick Pussy Until I Cum** 😈")
        add_chat("assistant", "Your prize is me spreading wide open for you… your tongue gets to worship this dripping little pussy until my thighs lock around your head and I squirt all over your face.")
        add_chat("assistant", "How do you want to eat your reward, daddy? Tell me how hungry you are…")

        c1, c2, c3 = st.columns(3)

        if c1.button("Slow & teasing – long licks, edge me forever", key="lick_slow"):
            data["intensity"] = "slow"
            data["stage"] = 1
            st.rerun()

        if c2.button("Eager & deep – tongue-fucking me like you’re starving", key="lick_eager"):
            data["intensity"] = "eager"
            data["stage"] = 1
            st.rerun()

        if c3.button("Aggressive – suck my clit hard, make me scream", key="lick_aggressive"):
            data["intensity"] = "aggressive"
            data["stage"] = 1
            st.rerun()

    # ── STAGE 1: Choose position
    elif data["stage"] == 1:
        add_chat("assistant", f"Ohhh… {data['intensity'].replace('_', ' ')} it is… fuck I’m already throbbing just thinking about your mouth on me.")

        simulate_loading(2.5)
        add_media("pussy_lick1.jpg")  # wide shot – her spreading legs / teasing panties aside

        add_chat("assistant", "Now tell me how you want me positioned while you devour your prize…")

        col1, col2, col3 = st.columns(3)

        if col1.button("Lying on my back – legs spread wide, you between them", key="pos_lying"):
            data["position"] = "lying_back"
            data["stage"] = 2
            st.rerun()

        if col2.button("Me sitting on your face – grinding down, smothering you", key="pos_smother"):
            data["position"] = "sitting_on_face"
            data["stage"] = 2
            st.rerun()

        if col3.button("Standing – you on your knees, me pulling your hair", key="pos_standing"):
            data["position"] = "standing"
            data["stage"] = 2
            st.rerun()

    # ── STAGE 2: The main eating sequence
    elif data["stage"] == 2:
        if data["progress"] == 0:
            simulate_loading(3.5)

            if data["position"] == "lying_back":
                add_media("pussy_lick2.jpg")  # her on back, legs up, you between
                add_chat("assistant", "I lie back, spread wide… hooking my legs over your shoulders so you can bury that tongue deep. Fuck… start slow baby, taste how wet winning made me.")
            elif data["position"] == "sitting_on_face":
                add_media("pussy_lick4.jpg")  # facesitting angle – her grinding down
                add_chat("assistant", "I climb on top, straddling your face… lowering my soaked pussy right onto your waiting mouth. Mmm… don’t you dare stop breathing until I cum.")
            else:  # standing
                add_media("pussy_lick6.jpg")  # standing over, hand in hair
                add_chat("assistant", "I stand over you, one leg up on the bed… grabbing your hair and pulling your face into my cunt. Eat it like you mean it, winner.")

            add_chat("assistant", "Your tongue feels so fucking good… keep going…")

            if st.button("Start licking… I’m ready", key="lick_begin"):
                data["progress"] = 25
                st.rerun()

        elif 25 <= data["progress"] < 50:
            simulate_loading(3)
            add_media("pussy_lick3.jpg")  # closer – tongue visible or clit focus
            add_chat("assistant", "Ohhh fuck… right there… circling my clit just like that… you’re making me drip down your chin already 🥵")

            if data["intensity"] == "slow":
                add_chat("assistant", "I’m trembling… trying to hold back… don’t speed up yet, edge me baby…")
            elif data["intensity"] == "eager":
                add_chat("assistant", "Deeper—fuck—shove that tongue inside me… yesyesyes…")
            else:  # aggressive
                add_chat("assistant", "Suck my clit harder—fuck—make it hurt so good…")

            if st.button("Keep going… don’t stop", key="lick_continue1"):
                data["progress"] = 50
                st.rerun()

        elif 50 <= data["progress"] < 80:
            simulate_loading(4)
            add_media("pussy_lick5.jpg")  # intense – thighs shaking, hand gripping sheets/hair

            if data["position"] == "sitting_on_face":
                add_chat("assistant", "I’m grinding harder now… smothering you… your nose buried in my pussy while I ride your tongue… fuck I’m so close…")
            else:
                add_chat("assistant", "My hips are bucking against your face… thighs starting to shake… you’re gonna make me cum so fucking hard…")

            if st.button("Push me over the edge…", key="lick_continue2"):
                data["progress"] = 100
                st.rerun()

        elif data["progress"] >= 100:
            simulate_loading(4.5)
            add_media("pussy_lick7.jpeg")  # climax shot – squirting / thighs clamped / blissed out

            add_chat("assistant", "FUCK—YES—right there—don’t stop—")
            add_chat("assistant", "Oh god… I’m cumming… I’m squirting all over your fucking face… thighs squeezing so tight… take it all daddy… drink me…")

            add_narrator("Her whole body convulses… wave after wave… soaking you, shaking, moaning your name until she finally collapses, panting.")

            add_chat("assistant", "Holy fuck… you ate me so good… my legs are still trembling…")

            if st.button("Prize complete – come up here and kiss me", key="lick_finish"):
                st.session_state.pop("lick_pussy", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

            if st.button("That’s enough for now… save some for later?", key="lick_exit_early"):
                st.session_state.pop("lick_pussy", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()
                
# --- DOGGY STYLE READY ---
elif st.session_state.turn_state == "PRIZE_DOGGY_STYLE_READY":
    if "doggy_prize" not in st.session_state:
        st.session_state.doggy_prize = {
            "stage": 0,
            "pace": "slow",       # slow / steady / pounding
            "view": "behind",     # behind / side / mirror
            "progress": 0         # 0 → tease → fucking → finish
        }

    data = st.session_state.doggy_prize

    # ── STAGE 0: Intro + Tease
    if data["stage"] == 0:
        add_chat("assistant", "Mmm fuck yes daddy… you won **Doggy Style Ready** 😈")
        add_chat("assistant", "Your dirty little girlfriend is already on all fours… ass up high, back arched deep, waiting for you to come claim what’s yours.")
        add_chat("assistant", "Look at this view… cheeks spread just enough so you can see how wet and ready that tight pussy is for you…")

        simulate_loading(3)
        add_media("doggy_tease1.jpg")   # ass up, looking back, panties pulled aside or off

        add_chat("assistant", "How do you want to take me first, winner? Tell me how you’re gonna fuck your prize…")

        c1, c2 = st.columns(2)

        if c1.button("Slow and deep – make me feel every thick inch sliding in", key="doggy_slow"):
            data["pace"] = "slow"
            data["stage"] = 1
            st.rerun()

        if c2.button("Hard and fast – pound me like you own this ass", key="doggy_hard"):
            data["pace"] = "pounding"
            data["stage"] = 1
            st.rerun()

    # ── STAGE 1: Position/View choice + Start
    elif data["stage"] == 1:
        add_chat("assistant", f"Ohhh… {data['pace']} it is… fuck, my pussy is already clenching just thinking about it.")

        simulate_loading(2.5)
        add_media("doggy_tease2.jpg")   # closer shot — arched back, wet glistening

        add_chat("assistant", "From which angle do you want to watch yourself ruin me?")

        col1, col2, col3 = st.columns(3)

        if col1.button("Straight from behind – full view of my ass bouncing", key="view_behind"):
            data["view"] = "behind"
            data["stage"] = 2
            st.rerun()

        if col2.button("Side profile – watch my tits swing and face moan", key="view_side"):
            data["view"] = "side"
            data["stage"] = 2
            st.rerun()

        if col3.button("In the mirror – so we can both watch every thrust", key="view_mirror"):
            data["view"] = "mirror"
            data["stage"] = 2
            st.rerun()

    # ── STAGE 2: The fucking sequence
    elif data["stage"] == 2:
        if data["progress"] == 0:
            simulate_loading(4)
            if data["view"] == "behind":
                add_media("doggy_behind1.jpg")   # deep view from rear, cock just entering
            elif data["view"] == "side":
                add_media("doggy_side1.jpg")     # side angle, tits swinging
            else:
                add_media("doggy_mirror1.jpg")   # mirror reflection, eye contact

            add_chat("assistant", "You grab my hips… line up… and push in slow… fuck… stretching me open inch by thick inch…")

            if st.button("Start fucking me now", key="doggy_begin"):
                data["progress"] = 50
                st.rerun()

        elif data["progress"] == 50:
            simulate_loading(4)
            if data["pace"] == "slow":
                add_media("doggy_slow2.jpg")   # deep, deliberate strokes
                add_chat("assistant", "Long… deep… strokes… pulling almost all the way out then sinking back in so you feel every flutter… I’m moaning low, pushing back to meet you…")
            else:
                add_media("doggy_pound2.jpg")  # fast slapping, ass rippling
                add_chat("assistant", "You’re pounding me hard now… skin slapping loud… my ass bouncing with every brutal thrust… fuck—yes—don’t stop…")

            add_chat("assistant", "I’m getting so close… grip my hair / spank me / tell me I’m your slut…")

            if st.button("Finish inside me… fill your prize", key="doggy_cum_inside"):
                simulate_loading(4.5)
                add_media("doggy_cumshot.jpg")   # creampie / pull out cum on ass
                add_chat("assistant", "Oh god yes—bury it deep—cum inside me—fill this pussy up… I’m cumming with you… clenching so tight around your cock…")
                add_narrator("Her whole body shakes… milking every drop… collapsing forward with a satisfied whimper.")
                data["progress"] = 100

            if st.button("Pull out and cum on my ass", key="doggy_cum_on"):
                simulate_loading(4.5)
                add_media("doggy_cum_on_ass.jpg")
                add_chat("assistant", "You pull out right at the edge… stroking fast… then explode—thick hot ropes painting my ass and lower back… I moan feeling it drip down…")
                add_narrator("She reaches back, smears it around like filthy lotion, grinning back at you.")
                data["progress"] = 100

        if data["progress"] == 100:
            add_chat("assistant", "Fuck… you wrecked me so good… my pussy is still pulsing… legs shaking…")
            add_chat("assistant", "Best prize ever, daddy. Come cuddle your fucked-out girlfriend now 😏")

            if st.button("Prize complete – back to casino", key="doggy_finish"):
                st.session_state.pop("doggy_prize", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

# --- DICK RUB PRIZE ---
elif st.session_state.turn_state == "PRIZE_DICK_RUB":
    if "dick_rub" not in st.session_state:
        st.session_state.dick_rub = {
            "stage": 0,
            "lube": "dry",         # dry / light oil / lots of spit
            "focus": "slow tease", # slow tease / fast stroke / grinding
            "finished": False
        }

    data = st.session_state.dick_rub

    # ── STAGE 0: Intro
    if data["stage"] == 0:
        add_chat("assistant", "Mmm… you won **Dick Rub** baby 😈")
        add_chat("assistant", "Your prize is me wrapping my soft little hand around that thick cock… stroking you nice and slow while I whisper filthy things in your ear… no sucking, no fucking—just pure, teasing hand action until you can’t take it anymore.")
        add_chat("assistant", "Look how hard you already are for me…")

        simulate_typing(2.5)
        add_media("dick_rub_tease.jpg")   # hand wrapped around base, looking up

        add_chat("assistant", "How slippery do you want your prize to get, daddy?")

        c1, c2, c3 = st.columns(3)

        if c1.button("Dry – just skin on skin, feel every ridge", key="rub_dry"):
            data["lube"] = "dry"
            data["stage"] = 1
            st.rerun()

        if c2.button("Light oil – slick and warm, gliding smooth", key="rub_oil"):
            data["lube"] = "light oil"
            data["stage"] = 1
            st.rerun()

        if c3.button("Lots of spit – messy, drooling all over your cock", key="rub_spit"):
            data["lube"] = "spit"
            data["stage"] = 1
            st.rerun()

    # ── STAGE 1: Main stroking + choice of style
    elif data["stage"] == 1:
        add_chat("assistant", f"Ohhh… {data['lube']} it is… fuck, this is gonna feel so good…")

        simulate_loading(3)
        if data["lube"] == "dry":
            add_media("dick_rub_dry.jpg")     # dry hand, tight grip
            add_chat("assistant", "My fingers wrap tight around you… no lube, just warm skin stroking up and down… feeling every vein throb under my palm…")
        elif data["lube"] == "light oil":
            add_media("dick_rub_oil.jpg")     # shiny, slick strokes
            add_chat("assistant", "I drizzle warm oil down your shaft… my hand glides so smooth and slick… twisting at the head every time I reach the top…")
        else:  # spit
            add_media("dick_rub_spit.jpg")    # messy, drool dripping
            add_chat("assistant", "I lean down… spit all over your cock… letting it drip down your balls… then stroke you messy and wet… hand making that filthy slick sound…")

        add_chat("assistant", "How do you want me to work this dick, winner?")

        col1, col2 = st.columns(2)

        if col1.button("Slow teasing strokes – edge you forever", key="rub_slow"):
            data["focus"] = "slow tease"
            data["stage"] = 2
            st.rerun()

        if col2.button("Fast and tight – make me cum quick", key="rub_fast"):
            data["focus"] = "fast"
            data["stage"] = 2
            st.rerun()

    # ── STAGE 2: Climax
    elif data["stage"] == 2:
        simulate_loading(4)

        if data["focus"] == "slow tease":
            add_media("dick_rub_edge.jpg")   # hand paused near head, precum dripping
            add_chat("assistant", "Slow… tight… strokes… stopping right when you start throbbing hard… edging you over and over… whispering how bad I want your load…")
            add_chat("assistant", "You’re leaking so much… begging me… fuck it’s hot…")

        else:
            add_media("dick_rub_fast.jpg")   # blurred hand motion, intense grip
            add_chat("assistant", "Fast now… hand flying up and down your slick cock… twisting at the head… milking you hard… cum for me daddy—give it to me…")

        if st.button("Cum for me… shoot it all over my hand / tits", key="rub_cum"):
            simulate_loading(3.5)
            add_media("dick_rub_cum.jpg")    # cum spurting over hand / chest
            add_chat("assistant", "Yes—fuck—there it is… thick hot ropes shooting out… covering my hand… dripping down my fingers… mmm I love how much you give me…")
            add_narrator("She licks a little off her fingers, smirking up at you, satisfied.")
            data["finished"] = True

        if data["finished"]:
            add_chat("assistant", "God… you came so hard… my hand is a sticky mess because of you…")
            add_chat("assistant", "Prize delivered 😏 Ready for the next spin, or you need a minute to recover?")

            if st.button("Prize complete – back to casino", key="rub_finish"):
                st.session_state.pop("dick_rub", None)
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

