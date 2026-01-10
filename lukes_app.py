import json
import os
import re
import random
import time
import base64
import requests
import google.generativeai as genai
import streamlit as st
from datetime import datetime
from PIL import Image

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
            "move_out_fund": 0.0, 
            "ticket_balance": 0, 
            "allowance_balance": 0.0,
            "daily_holding_tank": 0.0,
            "bills": {"Rent (Mom)": 200.00, "Insurance": 100.00, "Loans": 80.00},
            "history": [] 
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
        if len(data["history"]) > 50:
            data["history"] = data["history"][-50:]
        with open(self.filename, 'w') as f: json.dump(data, f)

    def log_event(self, data, event_type, desc, value=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {"time": timestamp, "type": event_type, "desc": desc, "val": value}
        if "history" not in data: data["history"] = []
        data["history"].append(entry)
        self.save_data(data)

# ==========================================
#       PART 2: CARD READER
# ==========================================
class CharacterImporter:
    def parse_card(self, uploaded_file):
        try:
            if uploaded_file.name.endswith(".json"):
                return self._extract_fields(json.load(uploaded_file))
            if uploaded_file.name.endswith(".png"):
                img = Image.open(uploaded_file)
                img.load() 
                chara_content = img.info.get('chara')
                if chara_content:
                    decoded = base64.b64decode(chara_content).decode('utf-8')
                    return self._extract_fields(json.loads(decoded))
        except Exception as e:
            st.error(f"Error reading card: {e}")
            return None
        return None

    def _extract_fields(self, data):
        if 'data' in data: d = data['data']
        else: d = data
        
        full_personality = f"""
        {d.get("personality", "")}
        [DESCRIPTION]
        {d.get("description", "")}
        [SYSTEM RULES & PRIZE DEFINITIONS]
        {d.get("system_prompt", "")}
        {d.get("creator_notes", "")}
        """

        return {
            "name": d.get("name", "Unknown"),
            "personality": full_personality,
            "scenario": d.get("scenario", ""),
            "greeting": d.get("first_mes", "Systems Online."),
            "examples": d.get("mes_example", "")
        }

# ==========================================
#       PART 3: THE BRAINS
# ==========================================
class GeminiBrain:
    def __init__(self, api_key):
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def ask(self, context, persona, chat_history):
        if not self.model: return "⚠️ Connect Google Key."
        try:
            # We convert the chat history list into a string so the AI remembers context
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-5:]])
            
            prompt = f"""
            Roleplay as: {persona['name']}
            Personality & Rules: {persona['personality']}
            Examples: {persona['examples']}
            
            RECENT CHAT HISTORY:
            {history_text}
            
            Current User Input: {context}
            Task: Reply strictly in character. Keep it short (text message style).
            """
            return self.model.generate_content(prompt).text
        except: return "My brain hurts (Google blocked this)."

# ==========================================
#       PART 4: THE ENGINE
# ==========================================
class ExitPlanEngine:
    def __init__(self, gemini_key=None):
        self.gemini = GeminiBrain(gemini_key)
        self.db = DataManager()
        self.importer = CharacterImporter()
        self.data = self.db.load_data()
        
        self.persona = {
            "name": "Paige",
            "personality": "Strict Financial Wife. Sarcastic.",
            "scenario": "Reviewing finances.",
            "greeting": "Wallet check. Did you make us money today?",
            "examples": ""
        }
        self.daily_tax = 40.00 
        self.manual_mean = ["Alert: Chances of sex dropped to 0.", "****EYE ROLL****"]
        self.manual_sexy = ["Good boy.", "That's hot.", "Daddy's making moves!"]

    # --- FINANCE LOGIC ---
    def process_finance(self, text):
        text = text.lower()
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        
        if "tank" in text:
            if "move" in text: return self.move_tank()
            if "pay" in text: return self.spend_tank()

        if match:
            amt = float(match.group())
            if any(w in text for w in ["dayforce", "shift", "daily"]): return self.shift_logic(amt)
            if any(w in text for w in ["check", "payday"]): return self.payday_logic(amt)
            if "spent" in text: return self.spending_logic(amt)

        return None # Return None if it's not a math command (let Chat handle it)

    def shift_logic(self, amt):
        hold = min(amt, self.daily_tax)
        safe = max(0, amt - hold)
        self.data["daily_holding_tank"] += hold
        self.data["allowance_balance"] += safe
        self.db.log_event(self.data, "SHIFT", f"Earned ${amt}", f"+${safe:.2f} Wallet")
        return f"📊 **SHIFT:** ${amt}\n🔒 Tank: ${hold:.2f}\n😎 Wallet: ${safe:.2f}"

    def payday_logic(self, amt):
        tickets = 100 if amt >= 501 else 25
        self.data["ticket_balance"] += tickets
        bill_total = sum(self.data['bills'].values())
        rem = amt - bill_total
        if rem > 0: self.data['move_out_fund'] += rem
        
        self.db.log_event(self.data, "PAYDAY", f"Check ${amt}", f"+{tickets} Tix")
        return f"💰 **PAYDAY:** ${amt}\n🎟️ **EARNED:** {tickets} Tix\n(Bills paid, remainder to House)"

    def spending_logic(self, amt):
        self.data["allowance_balance"] -= amt
        self.db.log_event(self.data, "SPEND", "Spending", f"-${amt}")
        return f"💸 **SPENT: ${amt}**\n\n**{self.persona['name']}:** {random.choice(self.manual_mean)}"

    def move_tank(self):
        amt = self.data['daily_holding_tank']
        self.data['move_out_fund'] += amt
        self.data['daily_holding_tank'] = 0.0
        self.db.log_event(self.data, "SAVE", "Tank -> House", f"+${amt}")
        return f"✅ **MOVED TO HOUSE:** ${amt:.2f}"

    def spend_tank(self):
        amt = self.data['daily_holding_tank']
        self.data['daily_holding_tank'] = 0.0
        self.db.log_event(self.data, "BILL", "Tank Used", f"-${amt}")
        return f"💸 **TANK EMPTIED:** ${amt:.2f}"

    # --- CASINO PRIZES ---
    def get_bronze_prize(self):
        prizes = {"Bend Over": "I'll bend over for you.", "Flash": "I'll flash you right now.", "Dick Rub": "Rubbing you while you drive."}
        k = random.choice(list(prizes.keys()))
        return k, prizes[k]

    def get_silver_prize(self):
        prizes = {"Massage": "10 min massage.", "Shower Show": "Watch me shower.", "Toy Pic": "Dirty pic with a toy.", "Lick Pussy": "I straddle your face, you lick."}
        k = random.choice(list(prizes.keys()))
        return k, prizes[k]
        
    def get_gold_prize(self):
        return random.choice(["Upside Down BJ", "Blindfold BJ", "Anal Fuck", "All 3 Holes", "Road Head", "Slave Day"])

# ==========================================
#       PART 5: APP UI
# ==========================================
st.set_page_config(page_title="Exit Plan", page_icon="💋", layout="wide", initial_sidebar_state="collapsed")
apply_styling()

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine()
if "advisor_log" not in st.session_state: st.session_state.advisor_log = [{"role": "assistant", "content": st.session_state.engine.persona['greeting']}]

if "casino_stage" not in st.session_state: st.session_state.casino_stage = "IDLE" 
if "current_prize" not in st.session_state: st.session_state.current_prize = None

# SIDEBAR
with st.sidebar:
    st.title("Settings")
    gemini_key = st.text_input("Google API Key", type="password")
    if gemini_key: st.session_state.engine.gemini = GeminiBrain(gemini_key)
    
    st.divider()
    st.subheader("📂 Import Character")
    uploaded_file = st.file_uploader("Drop PNG/JSON", type=["png", "json"])
    if uploaded_file:
        p = st.session_state.engine.importer.parse_card(uploaded_file)
        if p: 
            st.session_state.engine.persona = p
            if st.button("Activate New Character"):
                st.session_state.advisor_log = [{"role": "assistant", "content": f"**{p['name']}:** {p['greeting']}"}]
                st.rerun()

    st.divider()
    st.subheader("📜 Ledger")
    history = st.session_state.engine.data.get("history", [])
    if history:
        for h in reversed(history[-10:]): 
            st.text(f"{h['time']} | {h['type']}\n{h['desc']} ({h['val']})")
            st.markdown("---")

# TABS
tab_office, tab_casino = st.tabs(["💼 **THE OFFICE**", "🎰 **THE CASINO**"])

# --- TAB 1: OFFICE ---
with tab_office:
    col1, col2 = st.columns([1, 1.5])
    with col1:
        d = st.session_state.engine.db.load_data()
        st.metric("🏠 HOUSE FUND", f"${d['move_out_fund']:.2f}")
        st.metric("😎 WALLET", f"${d['allowance_balance']:.2f}")
        st.info(f"🔒 TANK: ${d['daily_holding_tank']:.2f}")
        
        c1, c2 = st.columns(2)
        if c1.button("Move Tank -> House"):
            msg = st.session_state.engine.move_tank()
            st.session_state.advisor_log.append({"role": "assistant", "content": msg})
            st.rerun()
        if c2.button("Spend Tank"):
            msg = st.session_state.engine.spend_tank()
            st.session_state.advisor_log.append({"role": "assistant", "content": msg})
            st.rerun()

    with col2:
        # Chat History Display
        for m in st.session_state.advisor_log:
            with st.chat_message(m["role"]): st.markdown(m["content"])
            
        # Chat Input (OFFICE)
        if prompt := st.chat_input("Ex: 'Dayforce 200' or Chat...", key="office_chat"):
            st.session_state.advisor_log.append({"role": "user", "content": prompt})
            
            # 1. Try Finance Command
            resp = st.session_state.engine.process_finance(prompt)
            
            # 2. If not finance, ask Brain
            if not resp:
                resp = st.session_state.engine.gemini.ask(prompt, st.session_state.engine.persona, st.session_state.advisor_log)
            
            st.session_state.advisor_log.append({"role": "assistant", "content": resp})
            st.rerun()

# --- TAB 2: CASINO ---
with tab_casino:
    d = st.session_state.engine.db.load_data()
    st.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
    
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

    # 2. SPIN & WIN LOGIC
    elif "CONFIRM" in st.session_state.casino_stage:
        st.warning(f"Spin {st.session_state.casino_stage.split('_')[1]} Wheel?")
        if st.button("SPIN IT!"):
            cost = 100 if "GOLD" in st.session_state.casino_stage else 50 if "SILVER" in st.session_state.casino_stage else 25
            st.session_state.engine.data["ticket_balance"] -= cost
            
            # Determine Prize
            if cost == 100:
                pname = st.session_state.engine.get_gold_prize()
                st.session_state.current_prize = {"name": pname}
                st.session_state.casino_stage = "RESULT_GOLD"
            elif cost == 50:
                name, desc = st.session_state.engine.get_silver_prize()
                st.session_state.current_prize = {"name": name, "desc": desc}
                st.session_state.casino_stage = "RESULT_SIMPLE"
            else:
                name, desc = st.session_state.engine.get_bronze_prize()
                st.session_state.current_prize = {"name": name, "desc": desc}
                st.session_state.casino_stage = "RESULT_SIMPLE"
            
            # LOG TO LEDGER AND CHAT HISTORY (So AI knows context)
            st.session_state.engine.db.log_event(st.session_state.engine.data, "CASINO", f"Won {st.session_state.current_prize['name']}", f"-{cost} Tix")
            
            win_msg = f"🎰 **CASINO WINNER:** {st.session_state.current_prize['name']}\n(Cost: {cost} tickets)"
            st.session_state.advisor_log.append({"role": "assistant", "content": win_msg})
            st.rerun()
            
        if st.button("Cancel"):
            st.session_state.casino_stage = "IDLE"
            st.rerun()

    # 3. SHOW PRIZE RESULTS
    elif st.session_state.casino_stage == "RESULT_SIMPLE":
        st.success(f"🏆 {st.session_state.current_prize['name']}")
        st.markdown(st.session_state.current_prize['desc'])
        if st.button("Done"): st.session_state.casino_stage = "IDLE"; st.rerun()

    elif st.session_state.casino_stage == "RESULT_GOLD":
        prize = st.session_state.current_prize['name']
        st.success(f"👑 JACKPOT: {prize}")
        
        # Hardcoded Interactive Logic
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

    # --- CASINO CHAT INTERFACE (NEW) ---
    st.divider()
    st.subheader("💬 Chat with Paige about your Prize")
    
    # Show Chat Log
    for m in st.session_state.advisor_log[-3:]: # Show last 3 messages for context
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Chat Input (CASINO)
    if prompt := st.chat_input("Ex: 'Tell me more about Slave Day'", key="casino_chat"):
        st.session_state.advisor_log.append({"role": "user", "content": prompt})
        
        # Send directly to Brain (No finance logic needed here)
        resp = st.session_state.engine.gemini.ask(prompt, st.session_state.engine.persona, st.session_state.advisor_log)
        
        st.session_state.advisor_log.append({"role": "assistant", "content": resp})
        st.rerun()
