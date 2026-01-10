import json
import os
import random
import streamlit as st
from datetime import datetime

# ==========================================
#       PART 1: DATA MANAGER
# ==========================================
class DataManager:
    def __init__(self):
        self.filename = "exit_plan_data.json"
    
    def load_data(self):
        defaults = {
            "ticket_balance": 500, # Start rich for testing
            "history": [] 
        }
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
#       PART 2: ENGINE
# ==========================================
class ExitPlanEngine:
    def __init__(self):
        self.db = DataManager()
        self.data = self.db.load_data()

    def get_bronze_prize(self):
        prizes = {
            "Bend Over": "Look no touch.", 
            "Flash": "Quick flash.", 
            "Dick Rub": "Rub while driving."
        }
        k = random.choice(list(prizes.keys()))
        return k, prizes[k]

    def get_silver_prize(self):
        # EXACT KEYS for the logic below
        prizes = {
            "Massage": "10 min massage.", 
            "Shower Show": "Watch me shower.", 
            "Toy Pic": "Pic with toy.", 
            "Lick My Pussy": "Oral until I cum."
        }
        k = random.choice(list(prizes.keys()))
        return k, prizes[k]
        
    def get_gold_prize(self):
        return random.choice(["Upside Down BJ", "Blindfold BJ", "Anal Fuck", "All 3 Holes", "Road Head", "Slave Day"])

# ==========================================
#       PART 3: APP UI
# ==========================================
st.set_page_config(page_title="Casino Test", page_icon="🎰", layout="wide")

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine()
if "casino_stage" not in st.session_state: st.session_state.casino_stage = "IDLE" 
if "current_prize" not in st.session_state: st.session_state.current_prize = None
if "advisor_log" not in st.session_state: st.session_state.advisor_log = []

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stButton button { width: 100%; border-radius: 5px; font-weight: bold; }
    div[data-testid="stMetric"] { background-color: #262730; border: 1px solid #444; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- THE CASINO ---
st.title("🎰 The Casino (Hardcoded Media)")

d = st.session_state.engine.db.load_data()
col_a, col_b = st.columns([1, 3])
with col_a:
    st.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
    if st.button("Reset Tickets to 500"):
        st.session_state.engine.data["ticket_balance"] = 500
        st.session_state.engine.db.save_data(st.session_state.engine.data)
        st.rerun()

with col_b:
    # 1. WHEEL SELECTION
    if st.session_state.casino_stage == "IDLE":
        c1, c2, c3 = st.columns(3)
        if c1.button("🥉 BRONZE (25)"): 
            st.session_state.casino_stage = "CONFIRM_BRONZE" if d["ticket_balance"] >= 25 else st.session_state.casino_stage
            st.rerun()
        if c2.button("🥈 SILVER (50)"): 
            st.session_state.casino_stage = "CONFIRM_SILVER" if d["ticket_balance"] >= 50 else st.session_state.casino_stage
            st.rerun()
        if c3.button("👑 GOLD (100)"): 
            st.session_state.casino_stage = "CONFIRM_GOLD" if d["ticket_balance"] >= 100 else st.session_state.casino_stage
            st.rerun()

    # 2. SPINNING
    elif "CONFIRM" in st.session_state.casino_stage:
        st.warning(f"Spin {st.session_state.casino_stage.split('_')[1]} Wheel?")
        if st.button("SPIN IT!"):
            cost = 100 if "GOLD" in st.session_state.casino_stage else 50 if "SILVER" in st.session_state.casino_stage else 25
            st.session_state.engine.data["ticket_balance"] -= cost
            
            if cost == 100:
                pname = st.session_state.engine.get_gold_prize()
                st.session_state.current_prize = {"name": pname}
                st.session_state.casino_stage = "RESULT_GOLD"
            elif cost == 50:
                name, desc = st.session_state.engine.get_silver_prize()
                st.session_state.current_prize = {"name": name, "desc": desc}
                st.session_state.casino_stage = "RESULT_SILVER"
            else:
                name, desc = st.session_state.engine.get_bronze_prize()
                st.session_state.current_prize = {"name": name, "desc": desc}
                st.session_state.casino_stage = "RESULT_BRONZE"
            
            st.session_state.engine.db.log_event(st.session_state.engine.data, "CASINO", f"Won {st.session_state.current_prize['name']}", f"-{cost} Tix")
            win_msg = f"🎰 **CASINO WINNER:** {st.session_state.current_prize['name']}\n(Cost: {cost} tickets)"
            st.session_state.advisor_log.append({"role": "assistant", "content": win_msg})
            st.rerun()
            
        if st.button("Cancel"): st.session_state.casino_stage = "IDLE"; st.rerun()

    # 3. RESULT: BRONZE
    elif st.session_state.casino_stage == "RESULT_BRONZE":
        st.success(f"🏆 {st.session_state.current_prize['name']}")
        st.markdown(st.session_state.current_prize['desc'])
        if st.button("Done"): st.session_state.casino_stage = "IDLE"; st.rerun()

    # 4. RESULT: SILVER (WITH IMAGES)
    elif st.session_state.casino_stage == "RESULT_SILVER":
        prize = st.session_state.current_prize['name']
        st.success(f"🥈 SILVER WINNER: {prize}")

        if prize == "Massage":
            st.markdown("Ten minutes of me working you over, Daddy")
            if st.button("Want me to tell you more??"): 
                st.info("Her fingertips trace lazy circles between your shoulder blades, applying just enough pressure to make your muscles unwind—but never straying lower, never letting you touch. Mmm.... Her breath is warm against your ear as she leans in, her nipples brushing your spine teasingly. Can you be a good boy now? Or save for later?")
            
            c1, c2 = st.columns(2)
            if c1.button("USE NOW"): 
                st.info("**And if you reach back even once? Her nails dig in lightly. Massage over.**")
                if st.button("Finish"): st.session_state.casino_stage = "IDLE"; st.rerun()
            if c2.button("Save"): 
                st.info("Saved.")
                st.session_state.casino_stage = "IDLE"; st.rerun()

        elif prize == "Shower Show":
            st.markdown("Front row seat, Daddy, of watching me get all soapy in the shower… but no touching.")
            if st.button("Want me to tell you more??"): 
                st.info("Steam curls around her as she steps under the shower spray, her back arching under the hot water. She glances over her shoulder at you through the fogged glass, her lips curling into a smirk as she slowly drags her hands down her soap-slicked body. Her fingers circle her nipples, twisting them gently as she moans—just loud enough for you to hear over the water.")
            
            # SHOW IMAGE
            if st.button("Wanna see?"):
                 st.image("shower.png") 

            c1, c2 = st.columns(2)
            if c1.button("USE NOW"): 
                st.info("**She turns, letting the suds slide down her stomach between her thighs. And remember... no touching**")
                if st.button("Finish"): st.session_state.casino_stage = "IDLE"; st.rerun()
            if c2.button("Save"): 
                st.info("Saved.")
                st.session_state.casino_stage = "IDLE"; st.rerun()

        elif prize == "Toy Pic":
            st.markdown("Congrats Daddy youve won a dirty picture with a a toy of your choice… what will it be?")
            if st.button("Want me to tell you more??"): 
                st.info("The screen displays a freshly taken photo—her lips stretched obscenely around a thick vibrator, saliva glistening at the corners of her mouth. Her sharp eyes lock onto yours, pupils dilated with arousal.")

            # SHOW IMAGE
            if st.button("Wanna see?"):
                 st.image("toy_pic.png")
                 st.write("Mmm... this one’s going straight to your inbox, Daddy.")

            c1, c2 = st.columns(2)
            if c1.button("USE NOW"): 
                st.info("**Say the word... and I’ll give you a real show**")
                if st.button("Finish"): st.session_state.casino_stage = "IDLE"; st.rerun()
            if c2.button("Save"): 
                st.info("Saved.")
                st.session_state.casino_stage = "IDLE"; st.rerun()

        elif prize == "Lick My Pussy":
            st.markdown("Congrats Daddy. You get to lick my little pussy.")
            if st.button("Want me to tell you more??"): 
                st.info("She pulls down her panties with deliberate slowness, her thighs parting as she hooks one leg over your shoulder. Her fingers trail through your hair, her leg pulling you in closer.")
            
            # SHOW IMAGE
            if st.button("Wanna see?"):
                 st.image("lick_my_pussy.png")

            c1, c2 = st.columns(2)
            if c1.button("USE NOW"): 
                st.info("**And Daddy? Don’t stop until I scream**")
                if st.button("Finish"): st.session_state.casino_stage = "IDLE"; st.rerun()
            if c2.button("Save"): 
                st.info("Saved.")
                st.session_state.casino_stage = "IDLE"; st.rerun()
        
        if st.button("Close / Skip"): st.session_state.casino_stage = "IDLE"; st.rerun()

    # 5. RESULT: GOLD
    elif st.session_state.casino_stage == "RESULT_GOLD":
        prize = st.session_state.current_prize['name']
        st.success(f"👑 JACKPOT: {prize}")
        
        if prize == "Upside Down BJ":
            st.write("Me upside down taking your dick down my throat... Today or Save it?")
            c1, c2 = st.columns(2)
            if c1.button("Today"): st.info("**Paige:** Ill be waitng mouth open."); st.session_state.casino_stage = "IDLE"
            if c2.button("Save"): st.info("**Paige:** Saved."); st.session_state.casino_stage = "IDLE"

        elif prize == "Blindfold BJ":
            st.markdown("**BLINDFOLD BJ**: First I blindfold you, then I tease you.")
            c1, c2 = st.columns(2)
            if c1.button("Me (User)"): st.info("**Paige:** Get ready."); st.session_state.casino_stage = "IDLE"
            if c2.button("You (Paige)"): st.info("**Paige:** Ill be on my knees."); st.session_state.casino_stage = "IDLE"

        elif prize == "Anal Fuck":
            st.write("**Paige:** Fuck my ass until you fill it up, twice.")
            if st.button("Claim"): st.info("**Paige:** Plug going in now."); st.session_state.casino_stage = "IDLE"

        elif prize == "All 3 Holes":
            st.markdown("**ALL 3 HOLES**: Mouth, Pussy, Ass. 20 Mins.")
            c1, c2 = st.columns(2)
            if c1.button("Tonight"): st.info("See you tonight."); st.session_state.casino_stage = "IDLE"
            if c2.button("Later"): st.info("Saved."); st.session_state.casino_stage = "IDLE"

        elif prize == "Road Head":
            st.write("**Paige:** Road head for 3 songs.")
            if st.button("Claim"): st.info("**Paige:** Push my head down."); st.session_state.casino_stage = "IDLE"

        elif prize == "Slave Day":
            st.markdown("**SLAVE FOR A DAY**: I do anything you want for 8 hours.")
            if st.button("Today?"): st.info("I am yours."); st.session_state.casino_stage = "IDLE"
            if st.button("Save"): st.session_state.casino_stage = "IDLE"

        if st.button("Close"): st.session_state.casino_stage = "IDLE"; st.rerun()

st.divider()
st.subheader("Recent Wins")
if st.session_state.advisor_log:
    for m in st.session_state.advisor_log[-3:]:
        st.text(m["content"])
