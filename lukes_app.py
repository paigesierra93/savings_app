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
        [data-testid="stMetricLabel"] { color: #AAAAAA !important; font-size: 0.8rem !important; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.2rem !important; }
        h1, h2, h3 { color: #FF4B4B !important; }
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: #0E1117; }
        .stTabs [aria-selected="true"] { background-color: #262730; color: #FF4B4B; }
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
            "move_out_fund": 0.0, "ticket_balance": 0, "monday_bridge_fund": 0.0,
            "allowance_balance": 0.0, "daily_holding_tank": 0.0,
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

# A. MANUAL LINES (For Button Clicks)
class RaunchyPersona:
    def __init__(self):
        self.sexy_praise = [
            "Good boy, Do you want a sloppy blow job in the kitchen? I want to give it to you.",
            "Good boy. You kept the money safe.",
            "That's hot. One more step closer to a giant bottle of Lube, and you and me.",
            "My baby is saving, saving up to fuck my mouth in his own home.",
            "Good job, one step closer to to a blow job in the middle of own living room.",
            "Way to go, You'll be fucking my ass in our own house in no time.",
            "I like the way you save money, almost as much as I like it when you fuck my ass.",
            "Seeing you save money like that, makes me want to suck your dick.",
            "Daddy is being so good, I cant wait to be SO good for Daddy."
        ]
        self.roasts = [
            "You spent it? Wow. Nothing dries me up faster than being broke.",
            "Soft. Totally soft. Just like you're gonna be tonight since you spent our money.",
            "I hope that gas station burrito keeps you warm all night, because, my pussy wont be.",
            "Alert: Your chances of getting to fuck my mouth just dropped to None.",
            "Keep spending like that and the only thing you're banging is your toe on the furniture.",
            "****EYE ROLL**** Well, I wanted to suck your dick."
        ]
    def get_line(self, mood):
        if mood == "sexy": return random.choice(self.sexy_praise)
        return random.choice(self.roasts)

# B. GEMINI BRAIN (For Financial Advice - ROBOT MODE)
class GeminiBrain:
    def __init__(self, api_key):
        self.active = False
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.active = True
    
    def ask_financial_advice(self, question):
        if not self.active: return "⚠️ Connect API Key in Sidebar to ask questions."
        
        # We enforce "Robot Mode" here so it never gets blocked
        prompt = f"""
        Role: Ruthless Financial Advisor.
        User Question: {question}
        Task: Is this a waste of money? Be short, sarcastic, and strictly mathematical. No sex jokes.
        """
        try:
            response = self.model.generate_content(prompt)
            if response.text: return response.text
            return "Google blocked this answer. Try rephrasing."
        except: return "I'm having trouble thinking right now."

# C. HORDE BRAIN (For Dirty Chat - UNCENSORED)
class HordeBrain:
    def __init__(self):
        self.api_key = "0000000000"
        self.api_url = "https://stablehorde.net/api/v2/generate/text/async"
        self.status_url = "https://stablehorde.net/api/v2/generate/text/status"

    def try_response(self, context, char_name, user_name, rel):
        prompt = f"Character: {char_name}. User: {user_name}. Rel: {rel}. Personality: Nympho, sarcastic, loving. Input: {context}\n{char_name}:"
        payload = {
            "prompt": prompt,
            "params": {"n": 1, "max_length": 60, "rep_pen": 1.1, "temperature": 0.8},
            "models": ["KoboldCPP"], "nsfw": True, "censor_nsfw": False
        }
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        try:
            req = requests.post(self.api_url, json=payload, headers=headers)
            if req.status_code != 202: return None
            job_id = req.json()["id"]
            for _ in range(25): # Wait 25s
                time.sleep(1)
                stat = requests.get(f"{self.status_url}/{job_id}", headers=headers).json()
                if stat["done"]: return stat["generations"][0]["text"].strip()
            return None 
        except: return None

# ==========================================
#       PART 3: WHEEL & ENGINE
# ==========================================
class PrizeWheel:
    def __init__(self):
        self.pool = [
            "🏆 PRIZE: A firm handshake.", "🏆 PRIZE: 30-second hug.",
            "🏆 PRIZE: Bathroom Jack-off pass.", "🏆 PRIZE: Tell me a dirty joke.",
            "✨ PRIZE: 10 Min Massage.", "✨ PRIZE: Shower Show (Look don't touch).",
            "👑 JACKPOT: Wet, sloppy, Face fucking, Blow job.", 
            "👑 JACKPOT: Let me blindfold you and suck your cock.",
            "👑 JACKPOT: Fuck my ass until you fill it up, twice."
        ]
    def spin(self, tickets_bid):
        return f"🎰 **SPINNING...**\n\n{random.choice(self.pool)}"

class ExitPlanEngine:
    def __init__(self, gemini_key=None):
        self.manual = RaunchyPersona()
        self.horde = HordeBrain()
        self.gemini = GeminiBrain(gemini_key)
        self.db = DataManager()
        self.wheel = PrizeWheel()
        self.data = self.db.load_data()
        self.char_name = "Paige"
        self.user_name = "Luke"
        self.relation = "Wife/Husband"

    # --- TAB 1 ACTIONS (MANUAL + ADVICE) ---
    def move_tank(self):
        amt = self.data['daily_holding_tank']
        if amt <= 0: return "Tank empty."
        self.data['move_out_fund'] += amt
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        line = self.manual.get_line("sexy")
        return f"✅ **MOVED ${amt:.2f} TO HOUSE.**\n\n_{line}_"

    def spend_tank(self):
        amt = self.data['daily_holding_tank']
        if amt <= 0: return "Tank empty."
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        return f"💸 **TANK EMPTIED.** Used ${amt:.2f} for bills."

    def log_spending(self, amt):
        self.data["allowance_balance"] -= amt
        if self.data["allowance_balance"] < 0:
            pen = abs(self.data["allowance_balance"])
            self.data["move_out_fund"] -= pen
            self.data["allowance_balance"] = 0
            self.db.save_data(self.data)
            line = self.manual.get_line("mean")
            return f"📉 **PENALTY!** Overdraft -${pen} from House.\n\n_{line}_"
        self.db.save_data(self.data)
        return f"💸 **SPENT -${amt:.2f}**\nRemaining: ${self.data['allowance_balance']:.2f}"

    def update_dayforce(self, amt):
        hold = min(amt, 30.00) # $10 Gas + $20 House
        self.data["daily_holding_tank"] += hold
        safe = max(0, amt - hold)
        self.db.save_data(self.data)
        return f"📊 **SHIFT REPORT**\nLocked: ${hold:.2f}\nSafe: ${safe:.2f}"
    
    def get_financial_advice(self, question):
        return self.gemini.ask_financial_advice(question)

    # --- TAB 2 ACTIONS (UNCENSORED AI) ---
    def chat_dirty(self, text):
        if "spin" in text.lower():
            match = re.search(r"\d+", text)
            if match:
                bid = int(match.group())
                if self.data["ticket_balance"] < bid: return "🚫 Not enough tickets."
                self.data["ticket_balance"] -= bid
                self.db.save_data(self.data)
                return self.wheel.spin(bid)
        
        resp = self.horde.try_response(text, self.char_name, self.user_name, self.relation)
        if resp: return resp
        return "I'm feeling shy... try asking me again."

# ==========================================
#       PART 6: THE UI (TABS)
# ==========================================
st.set_page_config(page_title="Exit Plan", page_icon="💋", layout="wide")
apply_styling()

# Load Key from Secrets or Sidebar
gemini_key = None
if "GOOGLE_API_KEY" in st.secrets: gemini_key = st.secrets["GOOGLE_API_KEY"]

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine(gemini_key)
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "advice_history" not in st.session_state: st.session_state.advice_history = []

# SIDEBAR
with st.sidebar:
    st.title("Settings")
    if not gemini_key:
        gemini_key = st.text_input("Google API Key", type="password")
        if gemini_key: st.session_state.engine.gemini = GeminiBrain(gemini_key)
    else:
        st.success("🔒 Key Locked & Loaded")
    
    st.divider()
    cn = st.text_input("Her Name", value="Paige")
    un = st.text_input("Your Name", value="Luke")
    rel = st.text_input("Relation", value="Wife/Husband")
    if st.button("Update"):
        st.session_state.engine.char_name = cn
        st.session_state.engine.user_name = un
        st.session_state.engine.relation = rel
        st.success("Updated!")

# TABS
tab_money, tab_dirty = st.tabs(["💰 MONEY MANAGER", "💋 DIRTY CHAT"])

# --- TAB 1: MONEY MANAGER (LOGIC + ADVICE) ---
with tab_money:
    d = st.session_state.engine.db.load_data()
    
    # Dashboard
    c1, c2, c3 = st.columns(3)
    c1.metric("🏠 HOUSE FUND", f"${d['move_out_fund']:.2f}")
    c2.metric("😎 WALLET", f"${d['allowance_balance']:.2f}")
    c3.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
    
    st.divider()
    
    # Input Area
    st.subheader("Daily Actions")
    col_input, col_tank = st.columns([1, 1])
    
    with col_input:
        amt = st.number_input("Amount ($)", min_value=0.0, step=1.0)
        if st.button("📊 Log Dayforce Shift"):
            msg = st.session_state.engine.update_dayforce(amt)
            st.info(msg)
            st.rerun()
        if st.button("💸 Log Spending"):
            msg = st.session_state.engine.log_spending(amt)
            if "PENALTY" in msg: st.error(msg)
            else: st.warning(msg)
            st.rerun()

    with col_tank:
        st.info(f"**Holding Tank:** ${d['daily_holding_tank']:.2f}")
        if st.button("✅ Move Tank to House"):
            msg = st.session_state.engine.move_tank()
            st.success(msg) # Shows your Sexy Manual Line
            st.rerun()
        if st.button("💳 Spend Tank (Bills)"):
            msg = st.session_state.engine.spend_tank()
            st.warning(msg)
            st.rerun()
            
    st.divider()
    st.subheader("🧠 Ask the Financial Advisor")
    st.caption("Strict advice only. No chatting.")
    advice_q = st.text_input("Should we buy this?")
    if st.button("Analyze Purchase"):
        with st.spinner("Analyzing..."):
            answer = st.session_state.engine.get_financial_advice(advice_q)
        st.write(f"**Advisor:** {answer}")

# --- TAB 2: DIRTY CHAT (AI ONLY) ---
with tab_dirty:
    st.caption(f"Chatting with {st.session_state.engine.char_name} (Uncensored Mode)")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Talk dirty or spin the wheel..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.spinner("Thinking..."):
            response = st.session_state.engine.chat_dirty(prompt)
        
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})