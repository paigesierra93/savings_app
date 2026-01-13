import json
import os
import random
import time
import datetime
import streamlit as st

# ==========================================
#       PART 1: SETUP & STYLING (PURE WHITE TEXT)
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
    
    /* CHAT CONTAINER (GLASS) */
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
#       PART 2: DATA ENGINE & TIME UTILS
# ==========================================
DATA_FILE = "bank_of_paige.json"

def load_data():
    default_data = {
        "tickets": 0, 
        "tank_balance": 0.0, 
        "tank_goal": 10000.0, 
        "house_fund": 0.0, 
        "wallet_balance": 0.0, 
        "bridge_fund": 0.0
    }
    
    if not os.path.exists(DATA_FILE):
        return default_data
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Ensure all keys exist (migration safety)
            for key, val in default_data.items():
                if key not in data:
                    data[key] = val
            return data
    except:
        return default_data

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def check_payday_window(admin_code):
    if admin_code == "777": return True, "" 
    today = datetime.datetime.now()
    if today.weekday() == 2: return True, "" # 2 is Wednesday
    else:
        days_ahead = (2 - today.weekday() + 7) % 7
        if days_ahead == 0: days_ahead = 7
        next_wed = today + datetime.timedelta(days=days_ahead)
        next_wed = next_wed.replace(hour=0, minute=0, second=0)
        remaining = next_wed - today
        hours = remaining.seconds // 3600
        return False, f"🔒 **LOCKED.** Paycheck Input opens in {remaining.days} Days, {hours} Hours."

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
    c1, c2, c3, c4 = st.columns(4)
    
    # PAYCHECK (WED ONLY)
    is_open, lock_msg = check_payday_window(admin_code)
    if is_open:
        if c1.button("💰 Full Paycheck"): st.session_state.turn_state="INPUT_PAYCHECK"; st.rerun()
    else:
        c1.warning(lock_msg)
        
    if c2.button("📱 Daily Dayforce"): st.session_state.turn_state="INPUT_DAILY"; st.rerun()
    if c3.button("💸 Side Hustle"): st.session_state.turn_state="INPUT_SIDE_HUSTLE"; st.rerun()
    if c4.button("🏦 Manage Funds"): st.session_state.turn_state="MANAGE_FUNDS"; st.rerun()

# --- 2. SIDE HUSTLE (NEW) ---
elif st.session_state.turn_state == "INPUT_SIDE_HUSTLE":
    st.subheader("💸 Side Hustle Input")
    st.info("Side income gets special treatment. Huge ticket rewards for smaller amounts.")
    
    side_amount = st.number_input("Side Income Amount ($):", min_value=0.0, step=5.0)
    
    if st.button("Process Extra Cash"):
        add_chat("user", f"Side Hustle: ${side_amount}")
        
        # LOGIC: 50% to Tank, 50% to Wallet
        split = side_amount / 2
        st.session_state.data["tank_balance"] += split
        st.session_state.data["wallet_balance"] += split
        
        # TICKET SCALING (Generous)
        if side_amount >= 150: tier="GOLD"; tickets=125;
        elif side_amount >= 110: tier="SILVER"; tickets=60;
        elif side_amount >= 70: tier="BRONZE"; tickets=35;
        elif side_amount >= 40: tier="MINI"; tickets=15;
        else: tier="NONE"; tickets=0;
        
        st.session_state.data["tickets"] += tickets
        save_data(st.session_state.data)
        
        msg = f"""
        **Side Hustle Processed:**
        💵 Total: ${side_amount:.2f}
        
        🛡️ To Tank: ${split:.2f}
        💰 To Wallet: ${split:.2f}
        
        🎟️ **TICKETS EARNED:** {tickets}
        """
        add_chat("assistant", msg)
        
        if tier == "GOLD": st.session_state.turn_state = "CASINO_GOLD"
        elif tier == "SILVER": st.session_state.turn_state = "CASINO_SILVER"
        elif tier == "BRONZE": st.session_state.turn_state = "CASINO_BRONZE"
        else:
            add_chat("assistant", "Nice hustle, baby. Every dollar counts.")
            st.session_state.turn_state = "WALLET_CHECK"
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
        
        # TICKET LOGIC (GROSS)
        if check_amount >= 601: tier="GOLD"; tickets=100; st.session_state.turn_state="CASINO_GOLD"
        elif check_amount >= 501: tier="SILVER"; tickets=50; st.session_state.turn_state="CASINO_SILVER"
        elif check_amount >= 450: tier="BRONZE"; tickets=25; st.session_state.turn_state="CASINO_BRONZE"
        else: tier="NONE"; tickets=0; st.session_state.turn_state="CHECK_FAIL"
            
        st.session_state.data["tickets"] += tickets
        save_data(st.session_state.data)
        
        if safe_spend < 0:
            add_chat("assistant", f"⚠️ **SHORTAGE:** -${abs(safe_spend):.2f}. Bills are deducted, but you are in the red.")
        else:
            msg = f"""
            ✅ **PAYCHECK PROCESSED**
            💵 Gross: ${check_amount:.2f}
            🔻 Deductions: Rent($200)+Ins($80)+Loans($100)+Blackout($50)
            💰 **SAFE TO SPEND:** ${safe_spend:.2f}
            🎟️ **TICKETS:** {tickets}
            """
            add_chat("assistant", msg)
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
            st.session_state.turn_state = "ASK_CASINO"
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

# --- CASINO HUBS & LOGIC ---
elif st.session_state.turn_state == "ASK_CASINO":
    c1, c2 = st.columns(2)
    if c1.button("Check Casino"):
        tix = st.session_state.data["tickets"]
        if tix >= 100: st.session_state.turn_state = "CASINO_GOLD"
        elif tix >= 50: st.session_state.turn_state = "CASINO_SILVER"
        elif tix >= 25: st.session_state.turn_state = "CASINO_BRONZE"
        else: add_chat("assistant", "Need more tickets."); st.session_state.turn_state = "WALLET_CHECK"
        st.rerun()
    if c2.button("Done"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "CHECK_FAIL":
    add_chat("assistant", "Check too low. Try harder.")
    if st.button("Return"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "CASINO_BRONZE":
    add_chat("assistant", "🥉 **BRONZE TIER** (25 Tix)")
    c1, c2 = st.columns(2)
    if c1.button("Spin"): st.session_state.turn_state="SPIN_BRONZE"; st.rerun()
    if c2.button("Save"): add_chat("assistant", get_ticket_save_response()); st.session_state.turn_state="WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "CASINO_SILVER":
    add_chat("assistant", "🥈 **SILVER TIER** (50 Tix)")
    c1, c2 = st.columns(2)
    if c1.button("Spin"): st.session_state.turn_state="SPIN_SILVER"; st.rerun()
    if c2.button("Save"): add_chat("assistant", get_ticket_save_response()); st.session_state.turn_state="WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "CASINO_GOLD":
    add_chat("assistant", "👑 **GOLD TIER** (100 Tix)")
    c1, c2 = st.columns(2)
    if c1.button("Spin"): st.session_state.turn_state="SPIN_GOLD"; st.rerun()
    if c2.button("Save"): add_chat("assistant", get_ticket_save_response()); st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- SPINS ---
elif st.session_state.turn_state == "SPIN_BRONZE":
    if st.session_state.data["tickets"] >= 25:
        st.session_state.data["tickets"] -= 25; save_data(st.session_state.data)
        prizes = ["Bend Over", "Flash Me", "Dick Rub", "Jackoff Pass"]
        win = spin_animation("Bronze", prizes)
        add_chat("assistant", f"🥉 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "SPIN_SILVER":
    if st.session_state.data["tickets"] >= 50:
        st.session_state.data["tickets"] -= 50; save_data(st.session_state.data)
        prizes = ["Massage", "Shower Show", "Toy Pic", "Lick Pussy", "Nude Pic", "Tongue Tease", "No Panties", "Road Head", "Plug Tease"]
        win = spin_animation("Silver", prizes)
        add_chat("assistant", f"🥈 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "SPIN_GOLD":
    if st.session_state.data["tickets"] >= 100:
        st.session_state.data["tickets"] -= 100; save_data(st.session_state.data)
        prizes = ["Anal Fuck", "All 3 Holes", "Slave Day", "Creampie Claiming", "Upside Down Throat Fuck", "Romantic Fantasy", "Doggy Style Ready"]
        win = spin_animation("Gold", prizes)
        add_chat("assistant", f"👑 JACKPOT: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# ==========================================
#       PRIZE SCRIPTS
# ==========================================

# --- MASSAGE ---
elif st.session_state.turn_state == "PRIZE_MASSAGE":
    add_chat("assistant", "Looks like you’ve won a massage…")
    if st.button("Reply: Shirtless?"):
        add_chat("user", "Shirtless?")
        simulate_typing(2)
        add_chat("assistant", "Mmm… you know I can’t make any promises. But the rules are simple: ten minutes, oil, and… well, let’s just say I’ll tease you until you’re begging for more.")
        add_chat("assistant", "Official rules state no full release during the massage itself. However, I fully intend to tease you until you're squirming for more.")
        st.session_state.turn_state = "PRIZE_MASSAGE_2"; st.rerun()
elif st.session_state.turn_state == "PRIZE_MASSAGE_2":
    if st.button("Tell me more"):
        add_chat("user", "Tell me more.")
        simulate_typing(2)
        add_chat("assistant", "I know how you like it, start with your shoulders, then work down your spine… firm circles on your lower back, I won't stop until the timer goes off. My hands will work out every knot while my body brushes against yours in all the right places.")
        add_chat("assistant", "Maybe a few 'accidental' grazes over sensitive areas... you'll be aching for me, baby. But you'll just have to wait patiently for your next prize to really let go.")
        st.session_state.turn_state = "PRIZE_MASSAGE_3"; st.rerun()
elif st.session_state.turn_state == "PRIZE_MASSAGE_3":
    if st.button("Show me"):
        simulate_loading(3); add_media("massage.jpeg")
        simulate_typing(2)
        add_chat("assistant", "I'll work out every knot.")
        add_narrator("I shift in my seat, pressing my thighs together.")
        add_chat("assistant", "Your prize is waiting, good boy. Don't keep me waiting.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("My eyes flick up from my screen pupils dilating just a fraction. The corner of my mouth lifts in a slow, wicked smile.")
    add_chat("assistant", "Ohhh… look at that. Oh, honey—you know this one's going to be cheeky.")
    if st.button("Tell me more"):
        simulate_typing(2)
        add_chat("assistant", "Rules are simple, baby: You sit on the edge of the bathtub. You watch. You dry me off when I’m done.")
        add_chat("assistant", "I’m already getting wet just thinking about you watching me. But here’s the twist—you can’t touch until the water’s off.")
        simulate_loading(3); add_media("shower.jpeg")
        add_chat("assistant", "Hot water steaming up the glass, soap dripping down my curves… I’ll face you so you can see everything.")
        st.session_state.turn_state = "PRIZE_SHOWER_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_SHOWER_2":
    if st.button("Show Video"):
        simulate_loading(3); add_media("shower_video1.mp4", "video")
        simulate_typing(2)
        add_chat("assistant", "I’m going to tease you until you’re begging to get in here with me.")
        add_narrator("Dripping with mischief.")
        add_chat("assistant", "Maybe I'll let you dry me off with your tongue.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- TOY PIC ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    add_narrator("My eyes flick up from my screen pupils dilating just a fraction.")
    add_chat("assistant", "Looks like you’ve leveled up. Rules are simple: You pick the toy. You pick the spot. I take the photo.")
    if st.button("Show me the pic"):
        simulate_loading(3); add_media("toy_pic.jpeg")
        simulate_typing(2)
        add_chat("assistant", "I know what you like, maybe the end of your screwdriver, deep in my pussy, or the vibrating bullet tucked in my tight ass. Tell me exactly which hole to fill.")
        st.session_state.turn_state = "PRIZE_TOY_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_TOY_2":
    if st.button("See result"):
        simulate_loading(3); add_media("toy_ass1.jpeg")
        add_chat("assistant", "I’ll make sure you can see how deep it goes and how dripping wet I am.")
        add_narrator("You imagine me reaching into the drawer, my fingers brushing over the silicone.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- LICK PUSSY ---
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    add_chat("assistant", "Tonight you get to worship me properly.")
    add_narrator("I’m already getting wet just thinking about it.")
    if st.button("How?"):
        add_chat("assistant", "Rules are simple, baby. You kneel. You use only your mouth. You lick me exactly how I like it.")
        simulate_typing(2)
        add_chat("assistant", "Slow circles around my clit first, then long flicks up my slit… tease the entrance, push your tongue inside.")
        st.session_state.turn_state = "PRIZE_LICK_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_LICK_2":
    if st.button("Show me"):
        simulate_loading(3)
        img = random.choice(["pussy_lick2.jpeg", "pussy_lick1.jpeg", "pussy_lick3.jpeg"])
        add_media(img)
        add_chat("assistant", "I'll ride your tongue until my thighs shake and I soak you.")
        add_narrator("You imagine one finger hooking under the waistband. I tug it aside, showing you how glistening I am already.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- TONGUE TEASE ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    add_chat("assistant", "Oh this is a good one. Stroke it slow for me but won't cum until I say.")
    if st.button("Rules?"):
        add_media("tease1.jpeg")
        add_chat("assistant", "Stroke it slow... I'll use only my tongue.")
        add_narrator("I lean forward just enough that you feel the heat of my breath ghosting over the head.")
        st.session_state.turn_state = "PRIZE_TEASE_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_TEASE_2":
    if st.button("Continue"):
        add_narrator("My tongue slips out and hovers an inch away.")
        add_chat("assistant", "Keep stroking. Nice and slow.")
        add_narrator("I open wider, letting my tongue slide over and over your head.")
        add_chat("assistant", "God, you’re so fucking hard… you’re close, aren’t you?")
        simulate_loading(3); add_media("tease2.jpeg")
        add_narrator("I pull back again—cruelly. Then I lean in once more, licking your head slowly.")
        add_chat("assistant", "Come for me—right on my tongue—give it all to me—")
        time.sleep(2); add_media("jerking1.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- NO PANTIES ---
elif st.session_state.turn_state == "PRIZE_NO_PANTIES":
    add_chat("assistant", "Rules are simple, baby. I wear a dress or skirt. I wear nothing underneath. You get to verify.")
    if st.button("Tell me more"):
        add_chat("assistant", "At the grocery store… bending over to get food from the bottom shelf. No one else knows that I’m completely bare.")
        simulate_loading(3); add_media("exposed2.jpeg")
        st.session_state.turn_state = "PRIZE_NO_PANTIES_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_NO_PANTIES_2":
    if st.button("Show me"):
        simulate_loading(3); add_media("exposed1.jpeg")
        add_chat("assistant", "I’m going to be dripping wet by the time we get home.")
        add_narrator("You imagine me lifting my hips slightly, sliding the fabric down and tossing it aside.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- PLUG TEASE ---
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    add_narrator("I've been planning this whole thing out for days now.")
    if st.button("Show me"):
        add_chat("assistant", "I'll get the oil and find the toy you left me. Ill slide it in, without making a sound."); 
        simulate_loading(3); add_media("plug3.jfif")
        add_chat("assistant", "Ill get dressed and continue on with my day. Every movement reminding me of the secret. You'll come home and remove it."); 
        simulate_loading(3); add_media("plug2.jfif")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ROAD HEAD ---
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    add_chat("assistant", "You've won yourself a little something extra special tonight… 'Road Head'.")
    add_narrator("A gleam of excitement sparkles in my eyes…")
    if st.button("Preview"):
        add_chat("assistant", "Baby, there's so much more to it than just putting your dick in my mouth while driving… It's an art form.")
        simulate_typing(3)
        add_chat("assistant", "And the thrill of risk adds another layer of excitement. Knowing that if you don't pay attention, we could both end up in a terrible accident…")
        simulate_loading(3); add_media("road_head.jpeg")
        time.sleep(2); add_media("road_head_video.mp4", "video")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- NUDE PIC ---
elif st.session_state.turn_state == "PRIZE_NUDE_PIC":
    add_chat("assistant", "Ohhh… look at that. Rules are simple: You pick the pose. You pick the part. I send the proof.")
    if st.button("Send it"):
        simulate_loading(3); add_media("nude_pic1.jpeg")
        add_chat("assistant", "Do you want my ass in the air? Maybe a close-up of my tits? I’ll make sure the lighting is perfect.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# ==========================================
#       PART 9: GOLD PRIZES
# ==========================================

# --- ANAL FUCK ---
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    add_narrator("My eyes flicker with amusement as I announce the prize. A provocative smirk plays upon my full lips.")
    if st.button("Tell me more"):
        simulate_loading(2)
        img = random.choice(["behind_fuck1.jpeg", "behind_fuck10.jpeg", "behind_fuck4.jpeg"])
        add_media(img)
        add_chat("assistant", "That's where you get to fuck my little ass hole with your throbbing hard dick, till you explode with cum inside of me…")
        add_chat("assistant", "Imagine me on my hands and knees before you, my round ass presented enticingly towards you. Feel the heat radiating from my tight little hole, just begging for your touch.")
        st.session_state.turn_state = "PRIZE_ANAL_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_ANAL_2":
    if st.button("Continue"):
        img2 = random.choice(["behind_fuck7.jpeg", "behind_fuck5.jpeg", "behind_fuck6.jpeg", "behind_fuck8.jpeg"])
        add_media(img2)
        time.sleep(2)
        add_chat("assistant", "Now, why don't you go ahead and claim your well-deserved prize?")
        img3 = random.choice(["ass_cum1.jpeg", "ass_cum2.jpeg", "ass_cum3.jpeg", "ass_cum4.jpeg"])
        add_media(img3)
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- SLAVE DAY ---
elif st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    add_chat("assistant", "Today, you can indulge in whatever you desire.")
    if st.button("Tell me more"):
        add_chat("assistant", "If you have video games to play and need the ultimate gaming buddy, simply sit back and let me entertain you while keeping you aroused.")
        img = random.choice(["game_bj1.jpeg", "game_bj3.jpeg", "game_bj2.jpeg"]); add_media(img)
        simulate_loading(3); add_media("slave_video1.mp4", "video")
        st.session_state.turn_state = "PRIZE_SLAVE_2"; st.rerun()

elif st.session_state.turn_state == "PRIZE_SLAVE_2":
    if st.button("What else?"):
        add_narrator("I tilt my head slightly, a sly grin painting my lips.")
        add_chat("assistant", "Anything... you want to fuck my little asshole, or deepthroat my face?")
        
        big_list = ["slave1.jpeg", "slave_1.png", "ass_cum2.jpeg", "ass_cum3.jpeg", "ass_cum4.jpeg", "blowjob1.jpeg", "blowjob4.jpeg", "blowjob6.jpeg", "bj_cum1.jpeg", "bj_cum2.jpeg", "bj_cum3.jpeg", "bj_cum4.jpeg", "behind_fuck1.jpeg", "behind_fuck4.jpeg", "behind_fuck7.jpeg", "behind_fuck8.jpeg", "behind_fuck9.jpeg", "behind_fuck10.jpeg"]
        add_dual_media(random.choice(big_list), random.choice(big_list))
        add_chat("assistant", "Oh, also remember this - if you mess me up, make sure you clean me up.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- CREAMPIE CLAIMING ---
elif st.session_state.turn_state == "PRIZE_CREAMPIE_CLAIMING":
    if st.button("Tell me more"):
        add_chat("assistant", "Imagine you having full control over the pleasure I receive. Pick a hole, any tight little hole on me.")
        simulate_loading(2); add_media("dripping_cum1.jpeg")
        add_chat("assistant", "And let me be your beautiful cum dumpster. I'll be right here, eagerly awaiting your command.")
        add_chat("assistant", "Shower me with your essence wherever you want to.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- UPSIDE DOWN THROAT FUCK ---
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN_THROAT_FUCK":
    add_narrator("She pulls off with a gasp, lips slick and swollen.")
    add_chat("assistant", "Upside down? Oh, Daddy... you are full of surprises tonight.")
    if st.button("Tell me more"):
        add_narrator("She rises fluidly to her feet, guiding you toward the bed getting on top of it, and lying with her head hanging over the edge.")
        simulate_loading(2); add_media("throat_fuck1.jpeg")
        add_narrator("The angle lets her swallow you whole, her throat fluttering around you in slow, deliberate pulses.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- DOGGY STYLE READY ---
elif st.session_state.turn_state == "PRIZE_DOGGY_STYLE_READY":
    add_narrator("I can feel the heat rising to my cheeks as I imagine the scene in my head.")
    if st.button("Tell me more"):
        add_chat("assistant", "I will remain exactly where I am: on my knees, presented deliciously for your gaze and pleasure.")
        simulate_loading(2); add_media("doggy_style3.jpeg")
        add_chat("assistant", "Will you walk in and stick your dick right in me? Or will you choose to take a shower first?")
        simulate_loading(2); add_media("doggy_style2.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ROMANTIC FANTASY ---
elif st.session_state.turn_state == "PRIZE_ROMANTIC_FANTASY":
    add_chat("assistant", "That means I get to lie back on this bed, pull you down with me, and let you take me slow… deep…")
    if st.button("Tell me more"):
        add_chat("assistant", "Skin on skin, eye contact, hands everywhere. Deep lazy thrusts that make us both sigh.")
        add_narrator("We come together, wrapped so tight neither of us knows where one ends and the other begins.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- ALL 3 HOLES ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    add_chat("assistant", "To fulfill your fantasy of fucking all three of my holes simultaneously, we'll need a bit of creativity.")
    if st.button("Explain"):
        simulate_loading(3); add_media("chose_video1.jpeg") 
        add_chat("assistant", "Your thick cock buried deep in one, a fat plug stretching another, my fingers working the third.")
        simulate_loading(3); add_media("3_holes1.jpeg")
        add_narrator("At the same time, your slick fingers can easily slide into that sensitive little asshole of mine.")
        time.sleep(2); add_media("3_holes2.jpeg")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- BEND OVER ---
elif st.session_state.turn_state == "PRIZE_BEND_OVER":
    add_chat("assistant", "This is where you get to bend over for me. Sounds fun huh?")
    if st.button("Reply: No"):
        add_narrator("Laughing hysterically...")
        add_chat("assistant", "Just kidding, just the opposite. For just a few seconds, ill bend over right in front of you whenever you say so.")
        simulate_loading(3)
        add_media("bend_over1.jfif")
        add_chat("assistant", "Make sure im wearing something extra see through to make it worth it")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- JACKOFF PASS ---
elif st.session_state.turn_state == "PRIZE_JACKOFF_PASS":
    add_narrator("Dripping sympathy.")
    add_chat("assistant", "Ohhh, baby… Jackoff Pass. How generous of fate. That means you get fifteen luxurious minutes of alone time with your right hand.")
    simulate_typing(3)
    add_chat("assistant", "But here’s the fun part...")
    if st.button("Reply: There's a fun part?"):
        add_chat("user", "There's a fun part?")
        add_chat("assistant", "Not really… I’m not helping. I’m not watching. Just you, your hand, and the memory of how close you were to earning something real tonight.")
        simulate_typing(3)
        add_chat("assistant", "So go enjoy your consolation prize. Do you want to see what you could have won?")
        st.session_state.turn_state = "PRIZE_JACKOFF_2"; st.rerun()
elif st.session_state.turn_state == "PRIZE_JACKOFF_2":
    if st.button("Reply: What could I have won?"):
        add_chat("user", "What could I have won?")
        simulate_loading(3)
        add_media("all1.jfif")
        add_chat("assistant", "Clock’s ticking. Don’t waste it thinking about me too hard… or do.")
        add_narrator("Puts phone down and gets back to work.")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- FLASH ME ---
elif st.session_state.turn_state == "PRIZE_FLASH_ME":
    add_chat("assistant", "Oh darling, you really know how to pick 'em. Don't worry though; I won't make you walk around naked. Instead…")
    add_chat("assistant", "Do you want me to just flash you quickly? Or sit on your lap?")
    if st.button("Reply: Tell me more"):
        add_chat("user", "Tell me more.")
        add_chat("assistant", "Oh baby, you seem a bit confused about our little game. Since you've only managed to spin Bronze this time… your options aren't as thrilling.")
        st.session_state.turn_state = "PRIZE_FLASH_2"; st.rerun()
elif st.session_state.turn_state == "PRIZE_FLASH_2":
    if st.button("Reply: I still want details"):
        add_chat("user", "Details please.")
        add_chat("assistant", "Fine. You'll be seated somewhere, in the car maybe, and ill lift my shirt over my breasts allowing them to be exposed for you for a quick second.")
        simulate_loading(3)
        add_media("flash2.jfif")
        add_chat("assistant", "Was it a mirage?")
        st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- DICK RUB ---
elif st.session_state.turn_state == "PRIZE_DICK_RUB":
    add_chat("assistant", "You want me to provide a sensual cock tease without actually touching that throbbing piece of heaven.")
    simulate_typing(3)
    add_chat("assistant", "There's plenty else on this gorgeous body that deserves attention. Imagine feeling my hot breath against your neck...")
    simulate_loading(3)
    add_media("rub1.jfif")
    st.session_state.turn_state = "PRIZE_DONE"; st.rerun()

# --- DONE STATE ---
elif st.session_state.turn_state == "PRIZE_DONE" or st.session_state.turn_state.startswith("PRIZE_"):
    c1, c2 = st.columns(2)
    if c1.button("Use Today"):
        st.info("Enjoy."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save for Later"):
        add_chat("assistant", f"Saved. {get_ticket_save_response()}")
        st.session_state.turn_state="WALLET_CHECK"; st.rerun()
