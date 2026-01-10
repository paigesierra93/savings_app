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
#       PART 2: ENGINE (Content Logic)
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

    # CENTRALIZED PRIZE DATA
    def get_prize_details(self, prize_name):
        details = {
            "Massage": {
                "desc": "Her fingertips trace lazy circles between your shoulder blades, applying just enough pressure to make your muscles unwind... but never straying lower. Her breath is warm against your ear. 'Can you be a good boy now? Or save for later?'",
                "img": None,
                "use_text": "**And if you reach back even once? Her nails dig in lightly. Massage over.**"
            },
            "Shower Show": {
                "desc": "Steam curls around her as she steps under the shower spray. She glances over her shoulder at you through the fogged glass, slowly dragging her hands down her soap-slicked body. 'Watch close... because these ten minutes are all you get.'",
                "img": "shower.png",
                "use_text": "**She turns, letting the suds slide down her stomach between her thighs. And remember... no touching.**"
            },
            "Toy Pic": {
                "desc": "The screen displays a freshly taken photo—her lips stretched obscenely around a thick vibrator, saliva glistening at the corners of her mouth. Her sharp eyes lock onto yours, pupils dilated with arousal.",
                "img": "toy_pic.png",
                "use_text": "**Say the word... and I’ll give you a real show.**"
            },
            "Lick My Pussy": {
                "desc": "She pulls down her panties with deliberate slowness, her thighs parting as she hooks one leg over your shoulder. She reaches downwards sliding two fingers deep with a wet gasp. 'I'm excited aren't you?'",
                "img": "lick_my_pussy.png",
                "use_text": "**And Daddy? Don’t stop until I scream.**"
            },
            "default": {
                "desc": "She looks at you with a smirk. 'You know exactly what this is. Do you want it now, or are you saving it for a special occasion?'",
                "img": None,
                "use_text": "**Good boy. Get ready.**"
            }
        }
        return details.get(prize_name, details["default"])

# ==========================================
#       PART 3: SETUP & STYLING
# ==========================================
st.set_page_config(page_title="Casino Chat", page_icon="🎰", layout="wide")

# Initialize Engine
if 'engine' not in st.session_state or not hasattr(st.session_state.engine, 'get_prize_details'):
    st.session_state.engine = ExitPlanEngine()

# State Management
if "casino_history" not in st.session_state:
    st.session_state.casino_history = [{"role": "assistant", "content": "Welcome to the Casino, Daddy. Do you have the tickets to play?"}]
if "turn_state" not in st.session_state: st.session_state.turn_state = "IDLE" 
if "current_prize" not in st.session_state: st.session_state.current_prize = None

# Styling
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    div[data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    div[data-testid="stChatMessage"] p {
        color: #000000 !important;
        font-family: sans-serif;
        font-size: 16px;
    }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; min-height: 45px; }
    div[data-testid="stMetric"] { background-color: #262730; color: white; border: 1px solid #444; padding: 10px; border-radius: 10px; }
    div[data-testid="stMetric"] label { color: #FAFAFA; }
    </style>
    """, unsafe_allow_html=True)

# Helper: Add Chat with Delay
def add_chat(role, content, image=None, delay=True):
    if role == "user":
        st.session_state.casino_history.append({"role": "user", "content": content})
    else:
        if delay:
            with st.spinner("Paige is typing..."):
                time.sleep(2.0) 
        msg = {"role": "assistant", "content": content}
        if image: msg["image"] = image
        st.session_state.casino_history.append(msg)

# ==========================================
#       PART 4: THE CASINO INTERFACE
# ==========================================
st.title("🎰 The Casino")
d = st.session_state.engine.db.load_data()

# Top Bar
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

# Chat Log
chat_container = st.container()
with chat_container:
    for msg in st.session_state.casino_history:
        avatar_img = "paige.png" if msg["role"] == "assistant" else "😎"
        if avatar_img == "paige.png" and not os.path.exists("paige.png"): avatar_img = "💋"
        
        with st.chat_message(msg["role"], avatar=avatar_img):
            st.markdown(msg["content"])
            if "image" in msg and msg["image"]:
                if os.path.exists(msg["image"]): st.image(msg["image"])
                else: st.warning(f"[Missing: {msg['image']}]")

st.markdown("---")

# ==========================================
#       PART 5: INTERACTIVE LOGIC
# ==========================================

# 1. IDLE (Spin Buttons)
if st.session_state.turn_state == "IDLE":
    c1, c2, c3 = st.columns(3)
    if c1.button("🥉 BRONZE (25)"):
        if d["ticket_balance"] >= 25:
            add_chat("user", "I want to spin Bronze.", delay=False)
            st.session_state.turn_state = "CONFIRM_BRONZE"
            st.rerun()
    if c2.button("🥈 SILVER (50)"):
        if d["ticket_balance"] >= 50:
            add_chat("user", "I want to spin Silver.", delay=False)
            st.session_state.turn_state = "CONFIRM_SILVER"
            st.rerun()
    if c3.button("👑 GOLD (100)"):
        if d["ticket_balance"] >= 100:
            add_chat("user", "I want to spin Gold.", delay=False)
            st.session_state.turn_state = "CONFIRM_GOLD"
            st.rerun()

# 2. CONFIRM SPIN
elif "CONFIRM" in st.session_state.turn_state:
    st.info("Are you sure?")
    c1, c2 = st.columns(2)
    if c1.button("SPIN IT!"):
        if "GOLD" in st.session_state.turn_state: cost=100; tier="GOLD"
        elif "SILVER" in st.session_state.turn_state: cost=50; tier="SILVER"
        else: cost=25; tier="BRONZE"
        
        # Deduct & Win
        st.session_state.engine.data["ticket_balance"] -= cost
        st.session_state.engine.db.save_data(st.session_state.engine.data)
        prize = st.session_state.engine.get_random_prize(tier)
        st.session_state.current_prize = prize
        
        # Announce
        if tier == "SILVER": intro = f"🥈 **SILVER WINNER:** {prize}."
        elif tier == "GOLD": intro = f"👑 **JACKPOT:** {prize}!"
        else: intro = f"🥉 **BRONZE:** {prize}."
        
        add_chat("assistant", intro, delay=True)
        # Move to Prize State
        st.session_state.turn_state = f"PRIZE_{prize.replace(' ','_').upper()}"
        st.rerun()

    if c2.button("Cancel"):
        st.session_state.turn_state = "IDLE"; st.rerun()

# ==========================================
#       PART 6: SPECIFIC PRIZE LOGIC
# ==========================================

# --- PRIZE: SLAVE DAY (3-Stage Reveal) ---
elif st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    st.caption("Option: Slave For A Day")
    
    # STAGE 1: Reveal
    if st.button("Tell me more??"):
        add_chat("user", "Tell me more...")
        
        part1 = "She turns in her chair, exposing spreading her legs and revealing she's not wearing any panties. With a wicked grin, her hand reaches down and behinds to circle her clit, you can see her pussy getting wetter - slow, deliberate, like a predator circling prey."
        
        # IMAGE 1
        add_chat("assistant", part1, image="slave_1.png", delay=True)
        st.session_state.turn_state = "PRIZE_SLAVE_DAY_STAGE2" 
        st.rerun()

elif st.session_state.turn_state == "PRIZE_SLAVE_DAY_STAGE2":
    # STAGE 2: Submission
    if st.button("What happens next?"):
        add_chat("user", "What happens next?")
        
        part2 = """24 hours, Daddy. She rolls down her pants to her knees, and kneels down on the floor in front of you. Her fingers reach behind her and unhook her bra, she removes it leaving her shirt up and exposing her breasts. That means *No* rules. No limits.
        \nShe puts 2 of her fingers in her mouth, far enough to make her self gag, tears flow from her eyes, running mascara down her face. Removing her spit soaked fingers from her mouth, Her hand snakes between her legs. She is now on her knees in front of you, pants pulled down exposing her ass and wet pussy.
        \nJust you... and every hole I’ve got. So. She spreads her legs, arching her back."""
        
        # IMAGE 2
        add_chat("assistant", part2, image="slave_2.png", delay=True)
        st.session_state.turn_state = "PRIZE_SLAVE_DAY_STAGE3" 
        st.rerun()

elif st.session_state.turn_state == "PRIZE_SLAVE_DAY_STAGE3":
    # STAGE 3: The Rules
    if st.button("What does that entail?"):
        add_chat("user", "What does that entail?")
        
        part3 = """Me waiting for you on the inside of this door just like this every time you walk in. No talking, no complaining, just eagerly waiting for your touch. Stick your dick in whatever hole you want too. 3 minutes, 10 minutes whatever, leave me on the edge and walk away. I'll be waiting.
        \nWant to play your video games, while I massage your dick in my mouth? No need to stop racing, I'll keep sucking. Want to give me a shower after you've filled up all of my holes like a dirty whore? Don't forget to lick me dry. I'm yours, your every wish.
        \nJust say it Daddy. Say you're gonna fuck me like your dirty little girl and leave me leaking your cum all day long."""
        
        # IMAGE 3
        add_chat("assistant", part3, image="slave_3.png", delay=True)
        st.session_state.turn_state = "PRIZE_SLAVE_DAY_FINAL" 
        st.rerun()

elif st.session_state.turn_state == "PRIZE_SLAVE_DAY_FINAL":
    # FINAL: Decision
    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "I'm using this now.")
        add_chat("assistant", "**I belong to you.**", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved. I'll be waiting.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()


# --- PRIZE: MASSAGE ---
elif st.session_state.turn_state == "PRIZE_MASSAGE":
    st.caption("Option: Massage")
    if st.button("Tell me more??"):
        add_chat("user", "Tell me more...")
        msg = st.session_state.engine.get_prize_details("Massage")
        add_chat("assistant", msg["desc"], delay=True)
        st.session_state.turn_state = "PRIZE_MASSAGE_FINAL"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_MASSAGE_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use Now.")
        msg = st.session_state.engine.get_prize_details("Massage")
        add_chat("assistant", msg["use_text"], delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save for later.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- PRIZE: SHOWER SHOW ---
elif st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    st.caption("Option: Shower Show")
    if st.button("Tell me more??"):
        add_chat("user", "Tell me more.")
        msg = st.session_state.engine.get_prize_details("Shower Show")
        add_chat("assistant", msg["desc"], delay=True)
        st.session_state.turn_state = "PRIZE_SHOWER_FINAL"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_SHOWER_FINAL":
    if st.button("Wana see?"):
        add_chat("user", "Show me.")
        add_chat("assistant", "Here...", image="shower.png", delay=True)
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use now.")
        msg = st.session_state.engine.get_prize_details("Shower Show")
        add_chat("assistant", msg["use_text"], delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- PRIZE: TOY PIC ---
elif st.session_state.turn_state == "PRIZE_TOY_PIC":
    st.caption("Option: Toy Pic")
    if st.button("Tell me more??"):
        add_chat("user", "Tell me more.")
        msg = st.session_state.engine.get_prize_details("Toy Pic")
        add_chat("assistant", msg["desc"], delay=True)
        st.session_state.turn_state = "PRIZE_TOY_FINAL"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_TOY_FINAL":
    if st.button("Wana see?"):
        add_chat("user", "Show me.")
        add_chat("assistant", "Mmm... straight to your inbox.", image="toy_pic.png", delay=True)
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use now.")
        msg = st.session_state.engine.get_prize_details("Toy Pic")
        add_chat("assistant", msg["use_text"], delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- PRIZE: LICK MY PUSSY ---
elif st.session_state.turn_state == "PRIZE_LICK_MY_PUSSY":
    st.caption("Option: Oral")
    if st.button("Tell me more??"):
        add_chat("user", "Tell me more.")
        msg = st.session_state.engine.get_prize_details("Lick My Pussy")
        add_chat("assistant", msg["desc"], delay=True)
        st.session_state.turn_state = "PRIZE_LICK_FINAL"
        st.rerun()

elif st.session_state.turn_state == "PRIZE_LICK_FINAL":
    if st.button("Wana see?"):
        add_chat("user", "Show me.")
        add_chat("assistant", "Look...", image="lick_my_pussy.png", delay=True)
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("USE NOW"):
        add_chat("user", "Use now.")
        msg = st.session_state.engine.get_prize_details("Lick My Pussy")
        add_chat("assistant", msg["use_text"], delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- GENERIC HANDLER FOR OTHER PRIZES ---
elif "PRIZE_" in st.session_state.turn_state:
    st.caption("Standard Prize Options:")
    if st.button("Tell me more??"):
        add_chat("user", "Tell me more.")
        prize_name = st.session_state.current_prize
        msg = st.session_state.engine.get_prize_details(prize_name)
        add_chat("assistant", msg["desc"], delay=True)
        st.session_state.turn_state = "PRIZE_GENERIC_FINAL" 
        st.rerun()

elif st.session_state.turn_state == "PRIZE_GENERIC_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("Use Now / Today"):
        add_chat("user", "I want it now.")
        add_chat("assistant", "**Good boy. Get ready.**", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save for Later"):
        add_chat("user", "Save it.")
        add_chat("assistant", "Saved.", delay=True)
        st.session_state.turn_state = "IDLE"; st.rerun()

# Close Button
if st.button("Close / Skip"):
    st.session_state.turn_state = "IDLE"; st.rerun()
