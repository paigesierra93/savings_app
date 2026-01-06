import json
import os
import re
import random
import time
import requests
import google.generativeai as genai
import streamlit as st

# ==========================================
#       PART 0: STYLING
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

# BRAIN 1: GEMINI (Financial Advisor)
# BRAIN 1: GEMINI (Financial Advisor)
class GeminiBrain:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            
            # --- THE FIX IS HERE ---
            # We switched from 'gemini-2.0-flash' (Paid/Restricted) 
            # to 'gemini-2.0-flash-exp' (Free/Experimental)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def ask(self, context):
        if not self.model: return "⚠️ Please enter a Google API Key in the sidebar."
        
        prompt = f"""
        Act as a financial advisor (who is also the user's wife).
        User Question: "{context}"
        Task: Give strict financial advice. If it's a waste of money, say so.
        Keep it short.
        """
        
        # Safety Settings (Unblocked)
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        try:
            genai.configure(api_key=self.api_key)
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            return response.text
            
        except Exception as e:
            # If the 'exp' model also fails, we have a backup plan in the error message
            return f"❌ SYSTEM ERROR: {str(e)}\n\n(Try changing line 12 to 'gemini-1.5-flash')"
# BRAIN 2: HORDE (For Casino/Prizes - Explicit/Uncensored)
class HordeBrain:
    def __init__(self):
        self.api_key = "0000000000"
        self.api_url = "https://stablehorde.net/api/v2/generate/text/async"
        self.status_url = "https://stablehorde.net/api/v2/generate/text/status"

    def react_to_win(self, prize, char_name):
        prompt = f"""
        Character: {char_name}. Personality: Nympho, explicit, high libido.
        Scenario: Husband just won a prize: "{prize}".
        Task: Describe excitedly how you will give him this prize. Be graphic.
        {char_name}:"""
        
        payload = {
            "prompt": prompt,
            "params": {"n": 1, "max_length": 80, "temperature": 0.8},
            "models": ["KoboldCPP"], "nsfw": True, "censor_nsfw": False
        }
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        try:
            req = requests.post(self.api_url, json=payload, headers=headers)
            if req.status_code != 202: return "I'm ready when you are. (Horde Offline)"
            job_id = req.json()["id"]
            for _ in range(25):
                time.sleep(1)
                stat = requests.get(f"{self.status_url}/{job_id}", headers=headers).json()
                if stat["done"]: return stat["generations"][0]["text"].strip()
            return "Come claim your prize. (Horde Timeout)"
        except: return "Come claim your prize."

# ==========================================
#       PART 3: THE ENGINE
# ==========================================
class ExitPlanEngine:
    def __init__(self, gemini_key=None):
        self.gemini = GeminiBrain(gemini_key)
        self.horde = HordeBrain()
        self.db = DataManager()
        self.data = self.db.load_data()
        
        # Manual Lines for Money (Reliable)
        self.manual_sexy = [
            "Good boy. You kept the money safe.",
            "That's hot. One step closer to our own bedroom.",
            "My baby is saving to move us out.",
            "Daddy's making moves!"
        ]
        self.manual_mean = [
            "You spent it? Soft.",
            "Nothing dries me up faster than being broke.",
            "Keep spending and you'll never get laid.",
            "Hope that burrito keeps you warm, cause I won't."
        ]

    # --- FINANCE LOGIC (TAB 1) ---
    def process_finance(self, text):
        text = text.lower()
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        
        # 1. Commands
        if "tank" in text:
            if any(w in text for w in ["save", "move"]): return self.move_tank()
            if any(w in text for w in ["pay", "spend"]): return self.spend_tank()
        
        # 2. Math
        if match:
            amt = float(match.group())
            if "dayforce" in text: return self.shift(amt)
            if "spent" in text: return self.spending(amt)
            if "check" in text: return self.payday(amt)

        # 3. Advice (Gemini)
        return self.gemini.ask(text)

    def move_tank(self):
        amt = self.data['daily_holding_tank']
        if amt <= 0: return "Tank empty."
        self.data['move_out_fund'] += amt
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        return f"✅ **MOVED:** ${amt:.2f} to House.\n\n{random.choice(self.manual_sexy)}"

    def spend_tank(self):
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        return "💸 **TANK EMPTIED** for bills."

    def spending(self, amt):
        self.data["allowance_balance"] -= amt
        msg = f"💸 **RECEIPT -${amt}**"
        if self.data["allowance_balance"] < 0:
             self.data["move_out_fund"] -= abs(self.data["allowance_balance"])
             self.data["allowance_balance"] = 0
             msg += f"\n📉 PENALTY. Took from House Fund.\n{random.choice(self.manual_mean)}"
        else:
             msg += f"\n{random.choice(self.manual_mean)}"
        self.db.save_data(self.data)
        return msg

    def shift(self, amt):
        hold = min(amt, 30.00) # Fixed $30 rule
        self.data["daily_holding_tank"] += hold
        self.db.save_data(self.data)
        return f"📊 **SHIFT:** ${amt}\nLocked: ${hold} | Safe: ${max(0, amt-hold):.2f}"

    def payday(self, amt):
        self.data["ticket_balance"] += 50 if amt > 600 else 10
        rem = amt - sum(self.data['bills'].values())
        if rem > 0: self.data['move_out_fund'] += rem
        self.db.save_data(self.data)
        return "💰 **PAYDAY:** Bills paid. Tickets added."

    # --- CASINO LOGIC (TAB 2) ---
    def spin_wheel(self, bet, char_name):
        if self.data["ticket_balance"] < bet: return "🚫 Not enough tickets."
        self.data["ticket_balance"] -= bet
        self.db.save_data(self.data)
        
        prizes = [
            "A firm handshake", "Flash of tits", "Quick Handjob", 
            "Blowjob", "Anal", "Face Sitting", "Massage", "Nude Photo"
        ]
        # Basic weighting: Better prizes are rarer
        weights = [30, 20, 15, 10, 5, 5, 10, 5] 
        prize = random.choices(prizes, weights=weights, k=1)[0]
        
        return prize

# ==========================================
#       PART 4: APP UI
# ==========================================
st.set_page_config(page_title="Exit Plan", page_icon="💋", layout="wide", initial_sidebar_state="collapsed")
apply_styling()

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine()
if "advisor_log" not in st.session_state: st.session_state.advisor_log = [{"role": "assistant", "content": "💋 **Financial Advisor Online.**"}]
if "casino_log" not in st.session_state: st.session_state.casino_log = [{"role": "assistant", "content": "🎰 **Casino Open. Place your bets.**"}]

# SIDEBAR
with st.sidebar:
    st.title("Settings")
    gemini_key = st.text_input("Google API Key", type="password")
    if gemini_key: st.session_state.engine.gemini = GeminiBrain(gemini_key)
    st.divider()
    char_name = st.text_input("Her Name", value="Paige")

# TABS
tab_office, tab_casino = st.tabs(["💼 **THE OFFICE**", "🎰 **THE CASINO**"])

# --- TAB 1: THE OFFICE (FINANCE) ---
with tab_office:
    col1, col2 = st.columns([1, 1.5])
    with col1: # Dashboard
        d = st.session_state.engine.db.load_data()
        st.metric("🏠 HOUSE FUND", f"${d['move_out_fund']:.2f}")
        st.metric("😎 WALLET", f"${d['allowance_balance']:.2f}")
        st.info(f"Tank: ${d['daily_holding_tank']:.2f}")
        
        c1, c2 = st.columns(2)
        if c1.button("Move to House"):
            msg = st.session_state.engine.move_tank()
            st.session_state.advisor_log.append({"role": "assistant", "content": msg})
            st.rerun()
        if c2.button("Spend (Bills)"):
            msg = st.session_state.engine.spend_tank()
            st.session_state.advisor_log.append({"role": "assistant", "content": msg})
            st.rerun()

    with col2: # Chat
        for m in st.session_state.advisor_log:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Finance commands..."):
            st.session_state.advisor_log.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            resp = st.session_state.engine.process_finance(prompt)
            st.session_state.advisor_log.append({"role": "assistant", "content": resp})
            st.rerun()

# --- TAB 2: THE CASINO (EXPLICIT) ---
with tab_casino:
    d = st.session_state.engine.db.load_data()
    st.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
    
    # Spin Buttons
    c1, c2, c3 = st.columns(3)
    bet = 0
    if c1.button("SPIN (10 Tix)"): bet = 10
    if c2.button("SPIN (25 Tix)"): bet = 25
    if c3.button("SPIN (50 Tix)"): bet = 50
    
    if bet > 0:
        prize = st.session_state.engine.spin_wheel(bet, char_name)
        if "Not enough" in prize:
            st.error(prize)
        else:
            st.session_state.casino_log.append({"role": "user", "content": f"🎰 **SPIN {bet}!**"})
            
            # 1. Show the Prize
            win_msg = f"🏆 **WINNER:** {prize}"
            st.session_state.casino_log.append({"role": "assistant", "content": win_msg})
            
            # 2. Get Explicit Reaction from Horde
            with st.spinner(f"{char_name} is preparing your prize..."):
                reaction = st.session_state.engine.horde.react_to_win(prize, char_name)
                st.session_state.casino_log.append({"role": "assistant", "content": reaction})
            st.rerun()

    # Chat Display for Casino
    for m in st.session_state.casino_log:
        with st.chat_message(m["role"]): st.markdown(m["content"])
        
    if st.button("Clear Casino Log"):
        st.session_state.casino_log = []
        st.rerun()