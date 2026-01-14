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
        prizes = ["Bend Over", "Flash Me", "Dick Rub", "Jackoff Pass"]
        win = spin_animation("Bronze", prizes)
        add_chat("assistant", f"🥉 WINNER: **{win}**")
        st.session_state.turn_state = f"PRIZE_{win.replace(' ','_').upper()}"
        st.rerun()
    else: st.error("Not enough tickets"); st.session_state.turn_state="CHOOSE_TIER"; st.rerun()

elif st.session_state.turn_state == "SPIN_SILVER":
    if st.session_state.data["tickets"] >= 50:
        st.session_state.data["tickets"] -= 50; save_data(st.session_state.data)
        prizes = ["Massage", "Shower Show", "Toy Pic", "Lick Pussy", "Nude Pic", "Tongue Tease", "No Panties", "Road Head", "Plug Tease"]
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
    add_narrator("My eyes lock on yours through the screen, pupils widening with heat as a slow, wicked smile spreads across my lips.")
    add_chat("assistant", "A steamy shower show just for you? Oh honey, this is going to leave you throbbing.")
    
    if st.button("Lay out the rules", key="shower_rules"):
        simulate_typing(2.5)
        add_chat("assistant", "You sit on the tub's edge—no touching me until every drop is rinsed off. But you can stroke yourself while you watch.")
        add_chat("assistant", "The glass fogs with hot steam... water pounds my skin, soap bubbles sliding over my full breasts, down my stomach, teasing between my thighs.")
        simulate_loading(3)
        add_media("shower.jpeg")  # Tease the steamy view
        add_narrator("I press my palms to the glass, arching so you see the rivulets tracing my curves.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Watch me lather up slowly", key="shower_lather"):
                simulate_loading(3.5)
                add_media("shower_video1.mp4", "video")
                add_chat("assistant", "Fingers glide over slick nipples... dip lower, circling my clit until my breath fogs the glass more. See how swollen and needy I am?")
        with col2:
            if st.button("Beg me to let you in", key="shower_beg"):
                add_chat("assistant", "Not quite yet... but keep watching. When the water stops, your tongue can replace the towel.")
        
        if st.button("End the tease—dry me off", key="shower_end"):
            add_narrator("I turn off the faucet, water still dripping from my lashes and nipples.")
            add_chat("assistant", "Come here... lick every bead off my skin, starting wherever you crave most.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- TOY PIC ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    add_narrator("My breath hitches, eyes sparkling with filthy anticipation.")
    add_chat("assistant", "Custom toy pic time. You pick the toy, the hole, the angle—I snap it dripping and ready.")
    
    if st.button("Choose your weapon", key="toy_choose"):
        choices = [
            "Vibrating bullet buzzing deep in my tight ass",
            "Thick ridged dildo stretching my pussy wide",
            "Household screwdriver handle plunging in",
            "Jeweled plug filling my ass completely"
        ]
        selected = st.radio("What do you want me to stuff inside?", choices, key="toy_selection")
        
        if st.button("Snap & show", key="toy_snap"):
            simulate_loading(3)
            add_media("toy_pic.jpeg")
            add_chat("assistant", f"Here it is... {selected.lower()}. My lips gripping it tight, juices glistening down my thighs.")
            add_narrator("I push it deeper for the camera, a soft whimper escaping as it hits just right.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- LICK PUSSY ---
elif st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    add_chat("assistant", "Time to worship me with that talented mouth of yours.")
    add_narrator("I'm already slick and aching just imagining your tongue.")
    
    if st.button("Teach me how you like it", key="lick_teach"):
        add_chat("assistant", "Kneel. Start with feather-light kisses on my thighs... then long, slow drags of your tongue along my folds.")
        add_chat("assistant", "Swirl around my clit, suck it gently... then fuck me with your tongue, tasting every drop of how wet you make me.")
        simulate_typing(2)
        if st.button("Show the view", key="lick_view"):
            simulate_loading(3)
            img = random.choice(["pussy_lick1.jpeg", "pussy_lick2.jpeg", "pussy_lick3.jpeg"])
            add_media(img)
            add_chat("assistant", "I'll ride your face hard, thighs squeezing, until I cum all over your chin and tongue.")
            add_narrator("My fingers twist in your hair, holding you exactly where I need you.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- TONGUE TEASE ---
elif st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    add_chat("assistant", "Stroke that cock slow for me... edge yourself. No cumming until I say.")
    
    if st.button("Start the tease", key="tease_start"):
        add_media("tease1.jpeg")
        add_chat("assistant", "My hot breath ghosts over your swollen head... tongue hovering so close you feel the wetness.")
        add_narrator("Just one cruel flick across the tip, tasting your pre-cum.")
        
        if st.button("More tongue?", key="tease_more"):
            add_chat("assistant", "Keep stroking... watch me swirl slow circles around the head, then drag flat down the shaft.")
            simulate_loading(3)
            add_media("tease2.jpeg")
            add_chat("assistant", "You're leaking for me... so close. Beg, and I'll let you explode right on my waiting tongue.")
            time.sleep(2)
            add_media("jerking1.jpeg")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- NO PANTIES ---
elif st.session_state.turn_state == "PRIZE_NO_PANTIES":
    add_chat("assistant", "Short skirt, bare underneath. You get full access to verify... anytime.")
    
    if st.button("Take me shopping", key="nopanties_shop"):
        add_chat("assistant", "Grocery aisle... I bend for the lowest shelf, skirt riding up, cool air kissing my naked, dripping pussy.")
        simulate_loading(3)
        add_media("exposed2.jpeg")
        add_chat("assistant", "Every step rubs my thighs together, slickness building. By checkout, I'm soaked and desperate.")
        
        if st.button("Lift for proof", key="nopanties_proof"):
            simulate_loading(3)
            add_media("exposed1.jpeg")
            add_narrator("I flash you discreetly—glistening, swollen, all yours.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# --- PLUG TEASE ---
elif st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    add_narrator("This has been on my mind for days... the constant reminder.")
    
    if st.button("Watch the insertion", key="plug_insert"):
        add_chat("assistant", "Warm oil coats my hole... I ease the plug in inch by inch, biting my lip to stifle the moan.")
        simulate_loading(3)
        add_media("plug3.jfif")
        add_chat("assistant", "It's seated deep now. Every sway of my hips, every sit, makes me clench around it, thinking of you.")
        simulate_loading(3)
        add_media("plug2.jfif")
        add_chat("assistant", "When you get home, pull it out slow... then replace it with whatever you crave.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- ROAD HEAD ---
elif st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    add_chat("assistant", "Road head—the risky, heart-pounding kind.")
    add_narrator("Excitement dances in my eyes like danger.")
    
    if st.button("Feel the thrill", key="road_thrill"):
        add_chat("assistant", "One hand on the wheel, the other guiding my head. I take you deep while cars zoom by.")
        add_chat("assistant", "The risk... knowing one glance from another driver could catch my lips wrapped around you.")
        simulate_loading(3)
        add_media("road_head.jpeg")
        simulate_loading(3)
        add_media("road_head_video.mp4", "video")
        add_chat("assistant", "Swallow you at stoplights... make you grip the wheel tighter as I work you to the edge.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- NUDE PIC ---
elif st.session_state.turn_state == "PRIZE_NUDE_PIC":
    add_chat("assistant", "Your personal nude—custom pose, custom focus, all for you.")
    
    if st.button("Design it", key="nude_design"):
        poses = ["Ass arched high in the air", "Legs wide, close-up on my wet pussy", "Tits pressed together and squeezed", "Full-body mirror shot, hair cascading"]
        selected = st.radio("How should I pose for you?", poses, key="nude_selection")
        
        if st.button("Send the proof", key="nude_send"):
            simulate_loading(3)
            add_media("nude_pic1.jpeg")
            add_chat("assistant", f"Here you go... {selected.lower()}. Skin flushed, eyes begging, perfectly lit just for your pleasure.")
            st.session_state.turn_state = "PRIZE_DONE"
            st.rerun()

# ==========================================
#       PART 9: GOLD PRIZES
# ==========================================# --- ANAL FUCK ---
elif st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    add_narrator("My blue eyes sparkle with wicked delight as I lean in close, voice dropping to a husky whisper.")
    add_chat("assistant", "Your prize? You get to claim my tight little asshole... slowly at first, then pounding deep until you fill me with every hot drop.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tease me first", key="anal_tease"):
            simulate_loading(1.5)
            add_media(random.choice(["behind_fuck1.jpeg", "behind_fuck10.jpeg"]))
            add_chat("assistant", "Mmm... watch me arch my back, spreading my cheeks for you. Feel how warm and ready I am?")
            st.session_state.anal_progress = "teased"
            st.rerun()
    
    with col2:
        if st.button("Take me now", key="anal_now") or st.session_state.get("anal_progress") == "teased":
            simulate_loading(2)
            img = random.choice(["behind_fuck4.jpeg", "behind_fuck7.jpeg", "behind_fuck5.jpeg"])
            add_media(img)
            add_chat("assistant", "I drop to all fours, ass high, quivering in anticipation. Your thick cock presses against my puckered hole... push in, Daddy. Stretch me open.")
            add_narrator("My moans fill the room as you slide deeper, inch by throbbing inch.")
            
            if st.button("Cum inside me", key="anal_cum"):
                simulate_loading(2.5)
                cum_img = random.choice(["ass_cum1.jpeg", "ass_cum3.jpeg", "ass_cum4.jpeg"])
                add_media(cum_img)
                add_chat("assistant", "Yes! Flood my ass with your hot cum... I can feel it pulsing, leaking out around you as I clench and milk every last drop.")
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

# --- SLAVE DAY ---
elif st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    add_chat("assistant", "For a full day, I'm your devoted slave... your every filthy whim is my command.")
    
    if st.button("Tell me more", key="slave_more"):
        add_narrator("I kneel gracefully before you, eyes upturned with eager submission.")
        choices = [
            "Gaming session with under-desk service",
            "Full body worship while you relax",
            "Rough anal or throat training"
        ]
        choice = st.radio("What do you desire first, Master?", choices, key="slave_choice")
        
        if st.button("Begin", key="slave_begin"):
            simulate_loading(2)
            if "Gaming" in choice:
                img = random.choice(["game_bj1.jpeg", "game_bj2.jpeg"])
                add_media(img)
                add_chat("assistant", "I crawl between your legs while you play... lips wrapping around you, sucking slow and deep as you rack up kills.")
                simulate_loading(3)
                add_media("slave_video1.mp4", "video")  # assuming video plays looped tease
            elif "worship" in choice.lower():
                add_chat("assistant", "I massage, lick, and adore every inch... starting at your feet and working my way up.")
            else:
                add_chat("assistant", "Tie me up? Use my throat or ass however rough you want...")
            
            if st.button("More? Anything goes...", key="slave_any"):
                add_narrator("My lips curl into a naughty smile.")
                big_list = ["slave1.jpeg", "blowjob6.jpeg", "behind_fuck8.jpeg", "bj_cum2.jpeg", "ass_cum3.jpeg"]
                add_dual_media(random.choice(big_list), random.choice(big_list))
                add_chat("assistant", "Fuck any hole, cum wherever... just remember: if you make a mess of your slave, you clean her up with your tongue.")
                st.session_state.turn_state = "PRIZE_DONE"
                st.rerun()

# --- CREAMPIE CLAIMING ---
elif st.session_state.turn_state == "PRIZE_CREAMPIE_CLAIMING":
    add_chat("assistant", "You own every dripping creampie today. Pick your hole... and fill it until I'm overflowing.")
    
    if st.button("Tell me more", key="creampie_more"):
        cols = st.columns(3)
        holes = ["Pussy", "Ass", "Mouth"]
        for i, hole in enumerate(holes):
            with cols[i]:
                if st.button(hole, key=f"creampie_{hole.lower()}"):
                    simulate_loading(2)
                    add_media("dripping_cum1.jpeg")
                    add_chat("assistant", f"Yes... {hole.lower()} it is. Pound me deep, breed me full. Watch your thick load leak out as I quiver.")
                    add_narrator("I spread wider, begging with my body.")
                    st.session_state.turn_state = "PRIZE_DONE"
                    st.rerun()

# --- UPSIDE DOWN THROAT FUCK ---
elif st.session_state.turn_state == "PRIZE_UPSIDE_DOWN_THROAT_FUCK":
    add_narrator("I pull off your cock with a wet pop, lips glossy and swollen, gasping for air.")
    add_chat("assistant", "Upside down throat fuck? Fuck yes, Daddy... use my mouth like a toy.")
    
    if st.button("Show me how", key="throat_show"):
        add_narrator("I flip onto the bed, head hanging off the edge, throat perfectly aligned for you.")
        simulate_loading(1.8)
        add_media("throat_fuck1.jpeg")
        add_chat("assistant", "Slide in slow... feel my throat flutter and squeeze around every inch. Deeper... make me gag and drool for you.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- DOGGY STYLE READY ---
elif st.session_state.turn_state == "PRIZE_DOGGY_STYLE_READY":
    add_narrator("Heat floods my cheeks as I hold the pose, ass arched high, waiting.")
    
    if st.button("Tell me more", key="doggy_more"):
        add_chat("assistant", "I'm staying right here on my knees, cheeks spread, pussy glistening and ready for you.")
        simulate_loading(2)
        add_media("doggy_style3.jpeg")
        add_chat("assistant", "Will you slam in raw and deep right now... or tease me first with your tongue?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Fuck me now", key="doggy_now"):
                add_media("doggy_style2.jpeg")
                add_chat("assistant", "Yes! Ram it in... make me scream your name.")
        with col2:
            if st.button("Tease first", key="doggy_tease"):
                add_chat("assistant", "Your tongue circles my clit... I push back, desperate for more.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- ROMANTIC FANTASY ---
elif st.session_state.turn_state == "PRIZE_ROMANTIC_FANTASY":
    add_chat("assistant", "Slow, deep, intimate... just us, lost in each other.")
    
    if st.button("Paint the scene", key="romantic_paint"):
        add_chat("assistant", "I pull you down onto silk sheets, legs wrapping around you as you slide in inch by inch.")
        add_narrator("Our eyes lock, breaths mingling, hands roaming with tender hunger.")
        add_chat("assistant", "Lazy, rolling thrusts... building that perfect heat until we shatter together, whispering sweet filth.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

# --- ALL 3 HOLES ---
elif st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    add_chat("assistant", "All three holes at once? Mmm... creativity required, but I'm game.")
    
    if st.button("Explain how", key="3holes_explain"):
        simulate_loading(2.5)
        add_media("chose_video1.jpeg")
        add_chat("assistant", "Your cock deep in my pussy... a thick plug stretching my ass... my own fingers circling and plunging into my mouth, tasting myself.")
        simulate_loading(2)
        add_media("3_holes1.jpeg")
        add_narrator("I moan around my fingers, body trembling as you're everywhere at once.")
        time.sleep(1.5)
        add_media("3_holes2.jpeg")
        add_chat("assistant", "Overwhelm me... use me completely.")
        st.session_state.turn_state = "PRIZE_DONE"
        st.rerun()

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
        save_data(st.session_state.data)
        add_chat("assistant", f"Saved. {get_ticket_save_response()}")
        st.session_state.turn_state="WALLET_CHECK"; st.rerun()


