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

# ==========================================
#       PART 2: ENGINE (Random Logic)
# ==========================================
class ExitPlanEngine:
    def __init__(self):
        self.db = DataManager()
        self.data = self.db.load_data()

    def get_random_prize(self, tier):
        if tier == "BRONZE":
            return random.choice(["Bend Over", "Flash", "Dick Rub"])
        if tier == "SILVER":
            return random.choice(["Massage", "Shower Show", "Toy Pic", "Lick My Pussy"])
        if tier == "GOLD":
            return random.choice(["Upside Down BJ", "Blindfold BJ", "Anal Fuck", "All 3 Holes", "Road Head", "Slave Day"])
        return "Nothing"

# ==========================================
#       PART 3: SETUP & STYLING
# ==========================================
st.set_page_config(page_title="Casino Chat", page_icon="🎰", layout="wide")

# Fix for Stale State
if 'engine' not in st.session_state or not hasattr(st.session_state.engine, 'get_random_prize'):
    st.session_state.engine = ExitPlanEngine()

if "casino_history" not in st.session_state:
    st.session_state.casino_history = [{"role": "assistant", "content": "Welcome to the Casino, Daddy. Do you have the tickets to play?"}]
if "turn_state" not in st.session_state: st.session_state.turn_state = "IDLE" 
if "current_prize" not in st.session_state: st.session_state.current_prize = None

# --- NEW CSS FOR WHITE BUBBLES ---
st.markdown("""
    <style>
    /* Dark App Background */
    .stApp { background-color: #0E1117; }
    
    /* CHAT BUBBLES: White Background, Black Text */
    div[data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Force Text inside bubbles to be Black */
    div[data-testid="stChatMessage"] p {
        color: #000000 !important;
        font-family: sans-serif;
        font-size: 16px;
    }

    /* Buttons */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; min-height: 45px; }
    
    /* Metrics */
    div[data-testid="stMetric"] { background-color: #262730; color: white; border: 1px solid #444; padding: 10px; border-radius: 10px; }
    div[data-testid="stMetric"] label { color: #FAFAFA; }
    </style>
    """, unsafe_allow_html=True)

# Helper to add chat with delay (Simulates typing)
def add_chat(role, content, image=None, delay=True):
    if role == "user":
        st.session_state.casino_history.append({"role": "user", "content": content})
    else:
        if delay:
            with st.spinner("Paige is typing..."):
                time.sleep(1.2) 
        msg = {"role": "assistant", "content": content}
        if image: msg["image"] = image
        st.session_state.casino_history.append(msg)

# ==========================================
#       PART 4: THE CASINO INTERFACE
# ==========================================
st.title("🎰 The Casino")

d = st.session_state.engine.db.load_data()

# TOP BAR
col_tick, col_reset = st.columns([3, 1])
with col_tick:
    st.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
with col_reset:
    if st.button("Reset Tickets"):
        st.session_state.engine.data["ticket_balance"] = 500
        st.session_state.engine.db.save_data(st.session_state.engine.data)
        st.session_state.casino_history = [{"role": "assistant", "content": "Tickets reset."}]
        st.session_state.turn_state = "IDLE"
        st.rerun()

st.divider()

# CHAT LOG (With Avatars)
chat_container = st.container()
with chat_container:
    for msg in st.session_state.casino_history:
        # Determine Avatar
        avatar_img = "paige.png" if msg["role"] == "assistant" else "😎"
        
        # Check if file exists to prevent errors
        if avatar_img == "paige.png" and not os.path.exists("paige.png"):
            avatar_img = "💋" # Fallback if image missing

        with st.chat_message(msg["role"], avatar=avatar_img):
            st.markdown(msg["content"])
            if "image" in msg and msg["image"]:
                if os.path.exists(msg["image"]):
                    st.image(msg["image"])
                else:
                    st.warning(f"[Image not found: {msg['image']}]")

st.markdown("---")

# ==========================================
#       PART 5: INTERACTIVE BUTTONS
# ==========================================

# --- 1. IDLE STATE ---
if st.session_state.turn_state == "IDLE":
    c1, c2, c3 = st.columns(3)
    if c1.button("🥉 BRONZE (25)"):
        if d["ticket_balance"] >= 25:
            add_chat("user", "Spin Bronze.", delay=False)
            st.session_state.turn_state = "CONFIRM_BRONZE"
            st.rerun()
    if c2.button("🥈 SILVER (50)"):
        if d["ticket_balance"] >= 50:
            add_chat("user", "Spin Silver.", delay=False)
            st.session_state.turn_state = "CONFIRM_SILVER"
            st.rerun()
    if c3.button("👑 GOLD (100)"):
        if d["ticket_balance"] >= 100:
            add_chat("user", "Spin Gold.", delay=False)
            st.session_state.turn_state = "CONFIRM_GOLD"
            st.rerun()

# --- 2. CONFIRM STATE ---
elif "CONFIRM" in st.session_state.turn_state:
    st.info("Confirm Spin?")
    c1, c2 = st.columns(2)
    if c1.button("SPIN IT!"):
        if "GOLD" in st.session_state.turn_state: cost=100; tier="GOLD"
        elif "SILVER" in st.session_state.turn_state: cost=50; tier="SILVER"
        else: cost=25; tier="BRONZE"
        
        st.session_state.engine.data["ticket_balance"] -= cost
        st.session_state.engine.db.save_data(st.session_state.engine.data)
        
        prize = st.session_state.engine.get_random_prize(tier)
        st.session_state.current_prize = prize
        
        if tier == "SILVER": intro = f"🥈 **SILVER WINNER:** {prize}."
        elif tier == "GOLD": intro = f"👑 **JACKPOT:** {prize}!"
        else: intro = f"🥉 **BRONZE:** {prize}."
        
        add_chat("assistant", intro, delay=True)
        st.session_state.turn_state = f"PRIZE_{prize.replace(' ','_').upper()}"
        st.rerun()

    if c2.button("Cancel"):
        st.session_state.turn_state = "IDLE"; st.rerun()

# ==========================================
#       PART 6: YOUR SPECIFIC PRIZES
# ==========================================

# --- PRIZE: MASSAGE ---
elif st.session_state.turn_state == "PRIZE_MASSAGE":
    st.caption("Option: Massage")
    if st.button("Want me to tell you more??"):
        add_chat("user", "Tell me more...")
        add_chat("assistant", "Her fingertips trace lazy circles between your shoulder blades, applying just enough pressure to make your muscles unwind—but never straying lower, never letting you touch. Mmm.... Her breath is warm against your ear as she leans in, her nipples brushing your spine teasingly. Can you be a good boy now? Or save for later?", delay=True)
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use Now.")
        add_chat("assistant", "**And if you reach back even once? Her nails dig in lightly. Massage over.**", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save for later.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- PRIZE: SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    st.caption("Option: Shower Show")
    if st.button("Want me to tell you more??"):
        add_chat("user", "Tell me more.")
        add_chat("assistant", "Steam curls around her as she steps under the shower spray... Her fingers circle her nipples, twisting them gently as she moans—just loud enough for you to hear over the water. Watch close... because these ten minutes are all you get..", delay=True)
        st.rerun()

    if st.button("Wana see?"):
        add_chat("user", "Show me.")
        add_chat("assistant", "Here...", image="shower.png", delay=True)
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use now.")
        add_chat("assistant", "**She turns, letting the suds slide down her stomach between her thighs. And remember... no touching**", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- PRIZE: TOY PIC ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    st.caption("Option: Toy Pic")
    if st.button("Want me to tell you more??"):
        add_chat("user", "Tell me more.")
        add_chat("assistant", "The screen displays a freshly taken photo—her lips stretched obscenely around a thick vibrator, saliva glistening at the corners of her mouth...", delay=True)
        st.rerun()

    if st.button("Wana see?"):
        add_chat("user", "Show me.")
        add_chat("assistant", "Mmm... this one’s going straight to your inbox, Daddy. Her voice is hoarse from the abuse, but her grin is triumphant as she pulls the toy free with a lewd pop. Or should I make it worse?", image="toy_pic.png", delay=True)
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use now.")
        add_chat("assistant", "**Say the word... and I’ll give you a real show**", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- PRIZE: LICK MY PUSSY ---
elif st.session_state.turn_state == "PRIZE_LICK_MY_PUSSY":
    st.caption("Option: Oral")
    if st.button("Want me to tell you more??"):
        add_chat("user", "Tell me more.")
        add_chat("assistant", "She pulls down her panties with deliberate slowness... She reaches downwards sliding two fingers deep with a wet gasp, curling them upward exposing her clit inches from your mouth.. Im excited arnt you?", delay=True)
        st.rerun()

    if st.button("Wana see?"):
        add_chat("user", "Show me.")
        add_chat("assistant", "Look...", image="lick_my_pussy.png", delay=True)
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use now.")
        add_chat("assistant", "**And Daddy? Don’t stop until I scream**", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- GENERIC HANDLER FOR OTHER PRIZES ---
elif "PRIZE_" in st.session_state.turn_state:
    st.caption("Select an option:")
    c1, c2 = st.columns(2)
    if c1.button("Use Now / Today"):
        add_chat("user", "I want it now.")
        add_chat("assistant", "Good boy. Get ready.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save for Later"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# Close Button
if st.button("Close / Skip"):
    st.session_state.turn_state = "IDLE"; st.rerun()
