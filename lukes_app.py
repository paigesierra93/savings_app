import json
import os
import random
import time
import streamlit as st
from datetime import datetime

# ==========================================
#       PART 1: DATA MANAGER
# ==========================================
class DataManager:
    def __init__(self):
        self.filename = "exit_plan_data.json"
    
    def load_data(self):
        defaults = { "ticket_balance": 500, "history": [] }
        if not os.path.exists(self.filename): return defaults
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "ticket_balance" not in data: data["ticket_balance"] = 500
                return data
        except: return defaults

    def save_data(self, data):
        with open(self.filename, 'w') as f: json.dump(data, f)

    def log_event(self, data, event_type, desc, value=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {"time": timestamp, "type": event_type, "desc": desc, "val": value}
        if "history" not in data: data["history"] = []
        data["history"].append(entry)
        self.save_data(data)

# ==========================================
#       PART 2: ENGINE (Prize Text)
# ==========================================
class ExitPlanEngine:
    def __init__(self):
        self.db = DataManager()
        self.data = self.db.load_data()

    # --- PRIZE DESCRIPTIONS ---
    def get_description(self, prize_name):
        # SILVER
        if prize_name == "Massage":
            return "Her fingertips trace lazy circles between your shoulder blades, applying just enough pressure to make your muscles unwind—but never straying lower, never letting you touch. Mmm.... Her breath is warm against your ear as she leans in, her nipples brushing your spine teasingly. Can you be a good boy now? Or save for later?"
        if prize_name == "Shower Show":
            return "Steam curls around her as she steps under the shower spray, her back arching under the hot water. She glances over her shoulder at you through the fogged glass, her lips curling into a smirk as she slowly drags her hands down her soap-slicked body. Her fingers circle her nipples, twisting them gently as she moans—just loud enough for you to hear over the water."
        if prize_name == "Toy Pic":
            return "The screen displays a freshly taken photo—her lips stretched obscenely around a thick vibrator, saliva glistening at the corners of her mouth. Her sharp eyes lock onto yours, pupils dilated with arousal, as she wiggles the toy deeper into her throat for the next shot."
        if prize_name == "Lick My Pussy":
            return "She pulls down her panties with deliberate slowness, her thighs parting as she hooks one leg over your shoulder. Her fingers trail through your hair, her leg pulling you in closer. She reaches downwards sliding two fingers deep with a wet gasp, curling them upward exposing her clit inches from your mouth.. Im excited arnt you?"
        
        # GOLD
        if prize_name == "Upside Down BJ": return "I'll hang off the bed upside down, gravity helping me take you deeper than ever before. Mouth open, waiting."
        if prize_name == "Blindfold BJ": return "First I blindfold you. Then I tease you. You won't know when I'm going to touch you, or how deep I'll take it."
        if prize_name == "Anal Fuck": return "You get to fill my ass. I'll prep with the plug right now. Two rounds."
        if prize_name == "All 3 Holes": return "Mouth, Pussy, Ass. 20 Minutes on the clock. You choose the rotation."
        if prize_name == "Road Head": return "Three songs on the radio. My head in your lap while you drive. Push me down if we hit a red light."
        if prize_name == "Slave Day": return "For 8 hours, I am your property. Use me however you want."
        
        # BRONZE
        return "Just a quick tease. Don't get too excited."

    def get_image_file(self, prize_name):
        if prize_name == "Shower Show": return "shower.png"
        if prize_name == "Toy Pic": return "toy_pic.png"
        if prize_name == "Lick My Pussy": return "lick_my_pussy.png"
        return None

    def get_random_prize(self, tier):
        if tier == "BRONZE":
            p = ["Bend Over", "Flash", "Dick Rub"]
            return random.choice(p)
        if tier == "SILVER":
            p = ["Massage", "Shower Show", "Toy Pic", "Lick My Pussy"]
            return random.choice(p)
        if tier == "GOLD":
            p = ["Upside Down BJ", "Blindfold BJ", "Anal Fuck", "All 3 Holes", "Road Head", "Slave Day"]
            return random.choice(p)

# ==========================================
#       PART 3: UI SETUP
# ==========================================
st.set_page_config(page_title="Casino Chat", page_icon="🎰", layout="wide")

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine()

# Initialize Chat History for Casino
if "casino_history" not in st.session_state:
    st.session_state.casino_history = [{"role": "assistant", "content": "Welcome to the Casino, Daddy. Do you have the tickets to play?"}]

# Track state of the current turn
if "turn_state" not in st.session_state: st.session_state.turn_state = "IDLE" 
if "current_prize" not in st.session_state: st.session_state.current_prize = None

# Styling
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stButton button { width: 100%; border-radius: 5px; font-weight: bold; height: 50px; }
    div[data-testid="stMetric"] { background-color: #262730; border: 1px solid #444; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Helper to add message with delay
def add_chat(role, content, image=None, delay=True):
    # 1. Add User message instantly
    if role == "user":
        st.session_state.casino_history.append({"role": "user", "content": content})
    
    # 2. Add Assistant message with artificial delay
    else:
        if delay:
            with st.spinner("Paige is typing..."):
                time.sleep(1.5) # The "Real Chat" delay
        
        msg = {"role": "assistant", "content": content}
        if image: msg["image"] = image
        st.session_state.casino_history.append(msg)

# ==========================================
#       PART 4: THE CASINO PAGE
# ==========================================
st.title("🎰 The Casino Chat")

d = st.session_state.engine.db.load_data()

# 1. TOP BAR (Tickets)
col_tick, col_reset = st.columns([3, 1])
with col_tick:
    st.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
with col_reset:
    if st.button("Reset (Debug)"):
        st.session_state.engine.data["ticket_balance"] = 500
        st.session_state.engine.db.save_data(st.session_state.engine.data)
        st.session_state.casino_history = [{"role": "assistant", "content": "Tickets reset. Ready to play?"}]
        st.session_state.turn_state = "IDLE"
        st.rerun()

st.divider()

# 2. CHAT HISTORY DISPLAY
chat_container = st.container()
with chat_container:
    for msg in st.session_state.casino_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg and msg["image"]:
                try:
                    st.image(msg["image"])
                except:
                    st.error(f"Image not found: {msg['image']}")

# 3. INTERACTIVE AREA (Bottom Buttons)
st.markdown("---")
# We use a placeholder logic to determine which buttons to show based on state

# --- STATE: IDLE (Choose Wheel) ---
if st.session_state.turn_state == "IDLE":
    c1, c2, c3 = st.columns(3)
    if c1.button("🥉 BRONZE (25)"):
        if d["ticket_balance"] >= 25:
            add_chat("user", "I want to spin the Bronze Wheel.")
            st.session_state.turn_state = "CONFIRM_BRONZE"
            st.rerun()
        else: st.error("Not enough tickets!")
        
    if c2.button("🥈 SILVER (50)"):
        if d["ticket_balance"] >= 50:
            add_chat("user", "I want to spin the Silver Wheel.")
            st.session_state.turn_state = "CONFIRM_SILVER"
            st.rerun()
        else: st.error("Not enough tickets!")
        
    if c3.button("👑 GOLD (100)"):
        if d["ticket_balance"] >= 100:
            add_chat("user", "I want to spin the Gold Wheel.")
            st.session_state.turn_state = "CONFIRM_GOLD"
            st.rerun()
        else: st.error("Not enough tickets!")

# --- STATE: CONFIRM SPIN ---
elif "CONFIRM" in st.session_state.turn_state:
    st.info("Are you sure?")
    c1, c2 = st.columns(2)
    if c1.button("Yes, Spin it!"):
        # Determine Cost
        if "GOLD" in st.session_state.turn_state: cost=100; tier="GOLD"
        elif "SILVER" in st.session_state.turn_state: cost=50; tier="SILVER"
        else: cost=25; tier="BRONZE"
        
        # Deduct
        st.session_state.engine.data["ticket_balance"] -= cost
        st.session_state.engine.db.save_data(st.session_state.engine.data)
        
        # Pick Prize
        prize = st.session_state.engine.get_random_prize(tier)
        st.session_state.current_prize = prize
        
        # Add to Chat
        add_chat("assistant", f"🎰 **WINNER:** {prize}!", delay=True)
        st.session_state.turn_state = "PRIZE_WON"
        st.rerun()
        
    if c2.button("Cancel"):
        add_chat("user", "Nevermind.")
        add_chat("assistant", "Tease. Let me know when you're ready.")
        st.session_state.turn_state = "IDLE"
        st.rerun()

# --- STATE: PRIZE WON (Options) ---
elif st.session_state.turn_state == "PRIZE_WON":
    c1, c2, c3 = st.columns(3)
    
    # Option A: Tell me more
    if c1.button("Tell me more..."):
        add_chat("user", "Tell me more about it...")
        desc = st.session_state.engine.get_description(st.session_state.current_prize)
        add_chat("assistant", desc, delay=True)
        st.session_state.turn_state = "DESCRIBED"
        st.rerun()
        
    # Option B: Use Now
    if c2.button("Use Now"):
        add_chat("user", "I want to claim this right now.")
        add_chat("assistant", "Good boy. Get ready...", delay=True)
        st.session_state.turn_state = "IDLE"
        st.rerun()
        
    # Option C: Save
    if c3.button("Save for Later"):
        add_chat("user", "I'll save this for later.")
        add_chat("assistant", "Saved. Just don't wait too long.", delay=True)
        st.session_state.turn_state = "IDLE"
        st.rerun()

# --- STATE: DESCRIBED (Can show image or Use) ---
elif st.session_state.turn_state == "DESCRIBED":
    # Check if there is an image for this prize
    img_file = st.session_state.engine.get_image_file(st.session_state.current_prize)
    
    cols = st.columns(3)
    
    # 1. Show Image (if available)
    if img_file:
        if cols[0].button("Wanna see?"):
            add_chat("user", "Show me.")
            add_chat("assistant", "Here...", image=img_file, delay=True)
            # Stay in DESCRIBED state so they can still click Use/Save
            st.rerun()
    else:
        cols[0].write("*(No image for this prize)*")

    # 2. Use Now
    if cols[1].button("Use Now"):
        add_chat("user", "Let's do this.")
        add_chat("assistant", "Finally. Come here.", delay=True)
        st.session_state.turn_state = "IDLE"
        st.rerun()

    # 3. Save
    if cols[2].button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Logged.", delay=True)
        st.session_state.turn_state = "IDLE"
        st.rerun()
