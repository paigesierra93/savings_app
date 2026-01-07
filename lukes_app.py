import json
import os
import re
import random
import time
import requests
import google.generativeai as genai
import streamlit as st

# ==========================================
#       PART 0: UI STYLING
# ==========================================
def apply_styling():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #330000; }
        div[data-testid="stMetric"] {
            background-color: #262730; border: 1px solid #444; padding: 10px;
            border-radius: 10px; margin-bottom: 10px;
        }
        h1, h2, h3 { color: #FF4B4B !important; }
        .stButton button { width: 100%; border-radius: 5px; font-weight: bold; }
        div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
            font-size: 1.2rem;
        }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
#       PART 1: DATA MANAGER
# ==========================================
class DataManager:
    def __init__(self):
        self.filename = "exit_plan_data.json"
    def load_data(self):
        defaults = {
            "move_out_fund": 0.0, "ticket_balance": 0, "allowance_balance": 0.0,
            "daily_holding_tank": 0.0,
            "bills": {"Rent (Mom)": 200.00, "Insurance": 100.00, "Loans": 80.00}
        }
        if not os.path.exists(self.filename): return defaults
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for k, v in defaults.items():
                    if k not in data: data[k] = v
                return data
        except: return defaults
    def save_data(self, data):
        with open(self.filename, 'w') as f: json.dump(data, f)

# ==========================================
#       PART 2: THE BRAINS
# ==========================================
class GeminiBrain:
    def __init__(self, api_key):
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def ask(self, context):
        if not self.model: return "⚠️ Connect Google Key."
        try:
            prompt = f"Role: Strict Financial Wife 'Paige'. Context: {context}. Keep it short."
            return self.model.generate_content(prompt).text
        except: return "My brain hurts (Google blocked this)."

class HordeBrain:
    def __init__(self):
        self.api_key = "0000000000" # Anonymous Key

    def react(self, text):
        # We don't really need Horde for the hardcoded lines, 
        # but we keep the structure just in case.
        return text

# ==========================================
#       PART 3: THE ENGINE (LOGIC)
# ==========================================
class ExitPlanEngine:
    def __init__(self, gemini_key=None):
        self.gemini = GeminiBrain(gemini_key)
        self.db = DataManager()
        self.data = self.db.load_data()
        
        self.char_name = "Paige"

        # --- YOUR CUSTOM LISTS (HARDCODED) ---
        self.manual_mean = [
            "Alert: Your chances of getting to fuck my mouth just dropped to None.",
            "Keep spending like that and the only thing you're banging is your toe on the furniture.",
            "Oh, so I guess you dont actualy want to fuck my mouth when you come home from work?",
            "and here I thought you actually wanted to fuck my ass, on a Sunday at 1:00pm.",
            "****EYE ROLL**** Well, I wanted to suck your dick."
        ]
        
        self.manual_sexy = [
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
        
        self.fail_prizes = [
            "I was really hoping to get my mouth fucked",
            "I was dying for you to fuck my ass",
            "I really wanted you to fill up all my holes with what ever you could find.",
            "I was all prepared to choke on your dick",
            "Was really hoping to meet you at the door on my knees and my mouth open.."
        ]

    # --- FINANCE TAB LOGIC ---
    def process_finance(self, text):
        text = text.lower()
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        if match:
            amt = float(match.group())
            if any(w in text for w in ["check", "payday", "deposit"]): return self.payday(amt)
            if "spent" in text: return self.spending(amt)
        return self.gemini.ask(text)

    def payday(self, amt):
        # Determine Tickets based on check size
        tickets_added = 0
        sexy_msg = ""
        
        if amt >= 501: 
            tickets_added = 100
            sexy_msg = random.choice(self.manual_sexy)
        else: 
            tickets_added = 25
            sexy_msg = "Savin up those tickets for the deep throat blow job? I gotchu. My pussy is already wet thinking about it."

        self.data["ticket_balance"] += tickets_added
        
        # Math for house fund
        rem = amt - sum(self.data['bills'].values())
        if rem > 0: self.data['move_out_fund'] += rem
        self.db.save_data(self.data)
        
        return f"""
        💰 **PAYDAY: ${amt}**
        🎟️ **EARNED:** {tickets_added} Tickets
        (Total Tickets: {self.data['ticket_balance']})
        
        **{self.char_name}:**
        "{sexy_msg}"
        """

    def spending(self, amt):
        self.data["allowance_balance"] -= amt
        self.db.save_data(self.data)
        line = random.choice(self.manual_mean)
        return f"💸 **SPENT: ${amt}**\n\n**{self.char_name}:**\n{line}\n\n*Hopefully next paycheck I'll finally get my holes filled.*"

    # --- CASINO PRIZE DICTIONARIES ---
    def get_bronze_prize(self):
        prizes = {
            "Bend Over": "lucky you, youve won a bend over, ill bend over while your standing behind me (make sure im wearing sheer leggings that day)",
            "Kesha Music": "lucky you werelistenting to kesha next time im in the car.",
            "Flash Tits": "youve won a flash, ill show you my tits whenever you ask me too, right there. No questions asked.",
            "Dick Rub": "youve won a dick rub, not a hand job. While you drive, ill run by fingers over your dick for the duration of 2 songs.",
            "Dirty Pic": "youve won a dirty picture, any position. Just tell me what you want to see.",
            "Jackoff Pass": "uninterrupted jackoff time for you. Arnt you lucky."
        }
        k = random.choice(list(prizes.keys()))
        return k, prizes[k]

    def get_silver_prize(self):
        prizes = {
            "10 Min Massage": "lucky you, youve won ten minute backrub. I might be shirt less, i might not be. Well see..",
            "Shower Show": "youve won a front row seat to me getting all soapy in the shower, look bt no touching.",
            "Toy Pic": "youve won a a dirty photo, featuring a toy, in any position, any where. Want to see it in my mouth. Got it. Want a picture of my ass with a plug in it. Done.",
            "Nude Pic": "youve won a dirty picture, any position. Just tell me what you want to see.",
            "Lick Pussy": "lucky you, looks like you get lick my pussy until i cum. Im excited. Are you?"
        }
        k = random.choice(list(prizes.keys()))
        return k, prizes[k]
        
    def get_gold_prize(self):
        # Returns the KEY only, because Gold prizes are complex and interactive
        keys = ["Upside Down BJ", "Blindfold BJ", "Anal Fuck", "All 3 Holes", "Road Head", "Slave Day"]
        return random.choice(keys)

# ==========================================
#       PART 5: APP UI
# ==========================================
st.set_page_config(page_title="Exit Plan", page_icon="💋", layout="wide", initial_sidebar_state="collapsed")
apply_styling()

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine()
if "advisor_log" not in st.session_state: st.session_state.advisor_log = [{"role": "assistant", "content": "💋 **Financial Advisor Online.**"}]

# SESSION STATE FOR CASINO
if "casino_stage" not in st.session_state: st.session_state.casino_stage = "IDLE" 
if "current_prize" not in st.session_state: st.session_state.current_prize = None

# SIDEBAR
with st.sidebar:
    st.title("Settings")
    gemini_key = st.text_input("Google API Key", type="password")
    if gemini_key: st.session_state.engine.gemini = GeminiBrain(gemini_key)

# TABS
tab_office, tab_casino = st.tabs(["💼 **THE OFFICE**", "🎰 **THE CASINO**"])

# --- TAB 1: OFFICE ---
with tab_office:
    col1, col2 = st.columns([1, 1.5])
    with col1:
        d = st.session_state.engine.db.load_data()
        st.metric("🏠 HOUSE FUND", f"${d['move_out_fund']:.2f}")
        st.metric("😎 WALLET", f"${d['allowance_balance']:.2f}")
    with col2:
        for m in st.session_state.advisor_log:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Enter Check (e.g. 'Check 600') or Spending (e.g. 'Spent 20')..."):
            st.session_state.advisor_log.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            resp = st.session_state.engine.process_finance(prompt)
            st.session_state.advisor_log.append({"role": "assistant", "content": resp})
            st.rerun()

# --- TAB 2: CASINO ---
with tab_casino:
    d = st.session_state.engine.db.load_data()
    st.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
    
    # 1. IDLE STATE (CHOOSE WHEEL)
    if st.session_state.casino_stage == "IDLE":
        st.subheader("Choose Your Wheel")
        c1, c2, c3 = st.columns(3)
        
        # BRONZE
        if c1.button("🥉 BRONZE (25 Tix)"):
            if d["ticket_balance"] >= 25:
                st.session_state.casino_stage = "CONFIRM_BRONZE"
                st.rerun()
            else: st.error("Not enough tickets!")

        # SILVER
        if c2.button("🥈 SILVER (50 Tix)"):
            if d["ticket_balance"] >= 50:
                st.session_state.casino_stage = "CONFIRM_SILVER"
                st.rerun()
            else: st.error("Not enough tickets!")

        # GOLD
        if c3.button("👑 GOLD (100 Tix)"):
            if d["ticket_balance"] >= 100:
                st.session_state.casino_stage = "CONFIRM_GOLD"
                st.rerun()
            else: st.error("Not enough tickets!")

    # 2. CONFIRMATION STATES (Are you sure?)
    elif st.session_state.casino_stage == "CONFIRM_BRONZE":
        st.warning("You have chosen the **BRONZE TIER**. Are you sure?")
        c1, c2 = st.columns(2)
        if c1.button("SPIN IT! (-25)"):
            st.session_state.engine.data["ticket_balance"] -= 25
            st.session_state.engine.db.save_data(st.session_state.engine.data)
            name, desc = st.session_state.engine.get_bronze_prize()
            st.session_state.current_prize = {"name": name, "desc": desc}
            st.session_state.casino_stage = "RESULT_SIMPLE"
            st.rerun()
        if c2.button("No (Cancel)"):
            st.session_state.casino_stage = "IDLE"
            st.info(random.choice(st.session_state.engine.fail_prizes))
            st.rerun()

    elif st.session_state.casino_stage == "CONFIRM_SILVER":
        st.warning("Respectable. **SILVER TIER**. Are you sure?")
        c1, c2 = st.columns(2)
        if c1.button("SPIN IT! (-50)"):
            st.session_state.engine.data["ticket_balance"] -= 50
            st.session_state.engine.db.save_data(st.session_state.engine.data)
            name, desc = st.session_state.engine.get_silver_prize()
            st.session_state.current_prize = {"name": name, "desc": desc}
            st.session_state.casino_stage = "RESULT_SIMPLE"
            st.rerun()
        if c2.button("No (Cancel)"):
            st.session_state.casino_stage = "IDLE"
            st.info(random.choice(st.session_state.engine.fail_prizes))
            st.rerun()

    elif st.session_state.casino_stage == "CONFIRM_GOLD":
        st.warning("Oh my god, Daddy... **GOLD TIER**. I hope you're ready. Are you sure?")
        c1, c2 = st.columns(2)
        if c1.button("SPIN IT! (-100)"):
            st.session_state.engine.data["ticket_balance"] -= 100
            st.session_state.engine.db.save_data(st.session_state.engine.data)
            pname = st.session_state.engine.get_gold_prize()
            st.session_state.current_prize = {"name": pname}
            st.session_state.casino_stage = "RESULT_GOLD_INTERACTIVE"
            st.rerun()
        if c2.button("No (Cancel)"):
            st.session_state.casino_stage = "IDLE"
            st.info(random.choice(st.session_state.engine.fail_prizes))
            st.rerun()

    # 3. RESULT STATES (SIMPLE PRIZES)
    elif st.session_state.casino_stage == "RESULT_SIMPLE":
        st.success(f"🏆 YOU WON: {st.session_state.current_prize['name']}")
        st.markdown(f"**Paige:** {st.session_state.current_prize['desc']}")
        if st.button("Claim & Reset"):
            st.session_state.casino_stage = "IDLE"
            st.rerun()

    # 4. RESULT STATES (GOLD INTERACTIVE - COMPLEX)
    elif st.session_state.casino_stage == "RESULT_GOLD_INTERACTIVE":
        prize = st.session_state.current_prize['name']
        st.success(f"👑 JACKPOT: {prize}")
        
        # --- SPECIFIC LOGIC FOR EACH GOLD PRIZE ---
        if prize == "Upside Down BJ":
            st.write("Me upside down taking your dick down my throat, while i gag... Only question is: Today or Save it?")
            c1, c2 = st.columns(2)
            if c1.button("Today/Now"):
                st.info("**Paige:** ok, ill be waitng mouth open for your dick when you walk to the door. Dont forget to lock it behind you. See you soon.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()
            if c2.button("Save/Later"):
                st.info("**Paige:** ok, you just let me know when your ready for it.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()

        elif prize == "Blindfold BJ":
            st.write("Intense blindfold BJ. Who gets the blindfold?")
            c1, c2 = st.columns(2)
            if c1.button("Me (User)"):
                st.info("**Paige:** Ok get ready be blindfolded when you come home. And have me suck you dick till you cum spilling out of my mouth.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()
            if c2.button("You (Paige)"):
                st.info("**Paige:** Ok ill be on my knees blindfolded when you walk in. All you have to do is stick your dick in my mouth and fuck it. Ok? Dont hold back.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()

        elif prize == "Anal Fuck":
            st.write("**Paige:** Fuck my ass until you fill it up, twice.")
            if st.button("Claim"):
                st.info("**Paige:** Let me know if i should put that plug in now, so its ready for you to slide in when you get home.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()

        elif prize == "All 3 Holes":
            st.write("Dick in my mouth, fingers in my ass, vibrator in my pussy. For 20 minutes. Tonight or Later?")
            c1, c2 = st.columns(2)
            if c1.button("Tonight"):
                st.info("**Paige:** Ok. Ill have a plug in when you get home, you can decide from there how youll spend the next 20 minutes.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()
            if c2.button("Later"):
                st.info("**Paige:** Ok, you just let me know when you want to see me sucking on your dick while you finger my asss, and my pussy is vibrating. Ill be ready.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()

        elif prize == "Road Head":
            st.write("**Paige:** Lucky you, youve won road head. For 3 songs lll tease, and lick and suck your dick while you dirve.")
            if st.button("Claim"):
                st.info("**Paige:** Dont forget to push my head down further if we get stuck at a light. All the way down so no one sees me.")
                if st.button("Done"): 
                    st.session_state.casino_stage = "IDLE"
                    st.rerun()

        elif prize == "Slave Day":
            st.markdown("""
            **THE ULTIMATE PRIZE: SLAVE FOR A DAY**
            Anything you want I'll do, for 8 hours. 
            * Fuck me in the shower.
            * Suck your dick while you race on your phone.
            * Waiting on my knees every time you walk into the bedroom.
            * Think of me as your sex doll, no complaints.
            """)
            if st.button("Claim"):
                st.session_state.casino_stage = "IDLE"
                st.rerun()