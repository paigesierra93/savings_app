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
#       PART 2: THE BRAINS & PERSONA
# ==========================================

# 1. MANUAL LIST (The "Safety Net")
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
        self.casual_flirt = [
            "I'm bored... and horny. Dangerous combination. Get home.",
            "Stop texting and make money so I can sit on your face later.",
            "I'm not wearing any panties right now. Just thought you should know.",
            "My knees are waiting for you, Daddy.",
            "Less talking, more stacking cash. I want to scream your name in our own bedroom.",
            "Send me a picture. I need something to look at while I wait for you."
        ]
        self.warnings = ["Listen up. It's Blackout Monday.", "Grind time. You're working for free today (on paper)."]
        self.payday_celebration = ["💰 **PAYDAY:** Bills paid. CUM claim your spin.", "💰 **PAYDAY:** We survived. Spin now?"]

    def get_line(self, mood):
        if mood == "sexy": return random.choice(self.sexy_praise)
        if mood == "mean": return random.choice(self.roasts)
        if mood == "comfort": return random.choice(self.warnings)
        if mood == "payday": return random.choice(self.payday_celebration)
        return random.choice(self.casual_flirt)

# 2. GOOGLE GEMINI (The Split Brain Fix)
class GeminiBrain:
    def __init__(self, api_key):
        self.active = False
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.active = True

    def try_response(self, context, char_name, user_name, rel):
        if not self.active: return None 
        
        # 1. DETECT THE VIBE
        # If you use these words, she becomes a "Financial Advisor" (Safe Mode)
        money_triggers = ["save", "cost", "bill", "box", "plan", "worth", "buy", "spend", "afford", "price"]
        is_financial = any(trigger in context.lower() for trigger in money_triggers)

        if is_financial:
            # MODE A: The Accountant (Safe)
            # We explicitly tell her NOT to be sexual here so Google permits the answer.
            tone = "Strict, Sarcastic, Financially Conservative. NO sex jokes."
            task = f"Analyze if '{context}' is a good financial decision for people trying to save money. Be ruthless."
        else:
            # MODE B: The Wife (Explicit)
            # This is where we allow the dirty stuff.
            tone = "Raunchy, Explicit, Nympho, Dirty, Submissive."
            task = "Reply in 1-2 sentences. Be flirtatious and dirty."

        prompt = f"""
        Role: {char_name} (Wife). User: {user_name} (Husband). Rel: {rel}.
        Tone: {tone}
        Context: {context}
        Task: {task}
        """
        
        try:
            # 2. SAFETY SETTINGS
            # We still keep them loose for Mode B
            safety = [
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
            
            response = self.model.generate_content(prompt, safety_settings=safety)
            
            # 3. SUCCESS CHECK
            if response.text: 
                return response.text
            return None # If blocked, returns None -> Falls back to Horde/Manual
            
        except:
            return None # Error -> Falls back to Horde/Manual

# 3. AI HORDE (Uncensored - Second Choice)
class HordeBrain:
    def __init__(self):
        self.api_key = "0000000000"
        self.api_url = "https://stablehorde.net/api/v2/generate/text/async"
        self.status_url = "https://stablehorde.net/api/v2/generate/text/status"

    def try_response(self, context, char_name, user_name, rel):
        prompt = f"Character: {char_name}. User: {user_name}. Rel: {rel}. Personality: Nympho, sarcastic. Input: {context}\n{char_name}:"
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
            for _ in range(20): # Wait 20s max
                time.sleep(1)
                stat = requests.get(f"{self.status_url}/{job_id}", headers=headers).json()
                if stat["done"]: return stat["generations"][0]["text"].strip()
            return None # Timed out
        except: return None

# ==========================================
#       PART 3: THE PRIZE WHEEL (RESTORED)
# ==========================================
class PrizeWheel:
    def __init__(self):
        self.common = [
            "🏆 PRIZE: A firm handshake.", "🏆 PRIZE: Coupon for a 30-second hug.",
            "🏆 PRIZE: I pick the music (K$SHA).", "🏆 PRIZE: Bathroom Jack-off pass.",
            "🏆 PRIZE: I lick your elbow.", "🏆 PRIZE: Tell me a dirty joke."
        ]
        self.rare = [
            "✨ PRIZE: 10 Min Massage.", "✨ PRIZE: Shower Show (Look don't touch).",
            "✨ PRIZE: Slow bend over.", "✨ PRIZE: Argument Free Card.", "✨ PRIZE: NSFW Photo, tell me what position, and youll get a picture (next day)."
        ]
        self.legendary = [
            "👑 JACKPOT: Wet, sloppy, Face fucking, Blow job.", 
            "👑 JACKPOT: Let me blindfold you and suck your cock.",
            "👑 JACKPOT: Fuck my ass until you fill it up, twice.",
            "👑 JACKPOT: Fuck all my holes, with whatever you want, for 20 minutes.",
            "👑 JACKPOT: Ill suck your dick while you drive. 3 songs",
            "👑 JACKPOT: Sex Slave Day. I'll be waiting for you on my knees, all day long as you do chores."
        ]

    def spin(self, tickets_bid):
        pool = []
        tier = ""
        if tickets_bid < 10: return "🚫 Minimum bet is 10."
        elif tickets_bid < 25:
            tier = "🥉 BRONZE"; pool.extend(self.common*80 + self.rare*19 + self.legendary*1)
        elif tickets_bid < 50:
            tier = "🥈 SILVER"; pool.extend(self.rare*90 + self.legendary*10)
        else:
            tier = "🥇 GOLD"; pool.extend(self.legendary*100)
        return f"🎰 **SPINNING {tier}...**\n\n{random.choice(pool)}"

# ==========================================
#       PART 4: THE ENGINE (CONTROLLER)
# ==========================================
class ExitPlanEngine:
    def __init__(self, gemini_key=None):
        self.manual = RaunchyPersona()
        self.gemini = GeminiBrain(gemini_key)
        self.horde = HordeBrain()
        self.db = DataManager()
        self.wheel = PrizeWheel() # <--- Restored Wheel Logic
        self.data = self.db.load_data()
        
        # Identity Defaults
        self.char_name = "Paige"
        self.user_name = "Luke"
        self.relation = "Wife/Husband"

        # Math Defaults
        self.daily_house_goal = 20.00
        self.gas_fixed = 10.00 
        self.bridge_cost = 50.00
        self.hourly_rate = 19.60

    def get_message(self, context, mood="flirt"):
        # PRIORITY 1: MANUAL LINES for Money Transactions (Consistency)
        if mood == "sexy" or mood == "mean":
            return self.manual.get_line(mood)

        # PRIORITY 2: GOOGLE GEMINI (Fastest)
        resp = self.gemini.try_response(context, self.char_name, self.user_name, self.relation)
        if resp: return resp

        # PRIORITY 3: AI HORDE (Uncensored Backup)
        return "USE_HORDE" 

    def get_horde_response(self, context):
        resp = self.horde.try_response(context, self.char_name, self.user_name, self.relation)
        if resp: return resp
        return self.manual.get_line("flirt")

    # --- LOGIC & CHAT ---
    def process_chat(self, user_text):
        user_text = user_text.lower()
        match = re.search(r"[-+]?\d*\.\d+|\d+", user_text)

        # 1. COMMANDS (Money Stuff)
        if "tank" in user_text:
            if any(w in user_text for w in ["save", "move", "house"]): return self.move_tank()
            if any(w in user_text for w in ["pay", "spend", "bill"]): return self.spend_tank()
        
        # 2. WHEEL / GAMBLING (Restored Logic)
        if any(w in user_text for w in ["spin", "bet", "gamble", "wheel"]):
            if not match: return "🎰 How many tickets? (e.g. 'Spin 25')"
            amount = int(float(match.group()))
            if self.data["ticket_balance"] < amount: return "🚫 Not enough tickets."
            self.data["ticket_balance"] -= amount
            self.db.save_data(self.data)
            return f"{self.wheel.spin(amount)}\n🎟️ Left: {self.data['ticket_balance']}"

        # 3. ADMIN
        if "set wallet" in user_text and match:
            self.data["allowance_balance"] = float(match.group()); self.db.save_data(self.data)
            return f"🔧 Wallet: ${float(match.group()):.2f}"
            
        # 4. CASUAL CHAT (The Fallback Logic)
        if not match:
            return self.get_message(user_text, "flirt")

        # 5. MATH LOGIC
        amount = float(match.group())
        if any(w in user_text for w in ["check", "payday"]): return self.payday(amount)
        if "dayforce" in user_text: return self.shift(amount)
        if "spent" in user_text: return self.spending(amount)
        return "🤔 Earned or Spent?"

    # --- MATH HELPERS ---
    def move_tank(self):
        amt = self.data['daily_holding_tank']
        if amt <= 0: return "Tank empty."
        self.data['move_out_fund'] += amt
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        msg = self.get_message("He saved the money.", "sexy")
        return f"✅ **MOVED:** ${amt:.2f} to House.\n\n{msg}"

    def spend_tank(self):
        amt = self.data['daily_holding_tank']
        if amt <= 0: return "Tank empty."
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        return f"💸 **TANK EMPTIED:** ${amt:.2f} used for bills."

    def spending(self, amt):
        self.data["allowance_balance"] -= amt
        if self.data["allowance_balance"] < 0:
            pen = abs(self.data["allowance_balance"])
            self.data["move_out_fund"] -= pen
            self.data["allowance_balance"] = 0
            self.db.save_data(self.data)
            msg = self.get_message("He overspent.", "mean")
            return f"💸 **RECEIPT -${amt}**\n\n{msg}\n📉 Penalty: -${pen} from House Fund."
        self.db.save_data(self.data)
        return f"💸 **RECEIPT -${amt}**\nRemaining: ${self.data['allowance_balance']:.2f}"

    def shift(self, amt):
        hold = min(amt, self.gas_fixed + self.daily_house_goal)
        self.data["daily_holding_tank"] += hold
        safe = max(0, amt - hold)
        self.db.save_data(self.data)
        return f"📊 **SHIFT:** ${amt}\nLocked: ${hold} | Safe: ${safe:.2f}"

    def payday(self, amt):
        self.data["ticket_balance"] += 50 if amt > 600 else 10
        rem = amt - sum(self.data['bills'].values())
        if rem > 0: self.data['move_out_fund'] += rem
        self.db.save_data(self.data)
        msg = self.get_message("Payday!", "payday")
        return f"{msg}\n💰 Check processed. Bills paid. (+Tickets Earned)"

# ==========================================
#       PART 5: APP UI
# ==========================================
st.set_page_config(page_title="Exit Plan", page_icon="💋", layout="wide", initial_sidebar_state="collapsed")
apply_styling()

# Session State Init
if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine()
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "💋 **Systems Online.**"}]

# SIDEBAR
with st.sidebar:
    st.title("Settings")
    
    # 1. Check for Secrets first
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("🔒 API Key loaded from Secrets")
        gemini_key = st.secrets["GOOGLE_API_KEY"]
    else:
        # If no secret found, ask manually
        gemini_key = st.text_input("Google API Key (Optional)", type="password")
        
    # Initialize Gemini if key exists
    if gemini_key: 
        st.session_state.engine.gemini = GeminiBrain(gemini_key)
    
    st.divider()
    
    # Persona Settings
    cn = st.text_input("Her Name", value="Paige")
    un = st.text_input("Your Name", value="Luke")
    rel = st.text_input("Relation", value="Wife/Husband")
    if st.button("Update Persona"):
        st.session_state.engine.char_name = cn
        st.session_state.engine.user_name = un
        st.session_state.engine.relation = rel
        st.success("Updated!")
# LAYOUT
col1, col2 = st.columns([1, 1.5])

with col1: # Dashboard
    d = st.session_state.engine.db.load_data()
    st.metric("🏠 HOUSE FUND", f"${d['move_out_fund']:.2f}")
    st.metric("😎 WALLET", f"${d['allowance_balance']:.2f}")
    st.info(f"Tank: ${d['daily_holding_tank']:.2f}")
    
    # Restored Ticket Display
    st.metric("🎟️ TICKETS", f"{d['ticket_balance']}")
    
    c1, c2 = st.columns(2)
    if c1.button("Move to House"):
        msg = st.session_state.engine.move_tank()
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.rerun()
    if c2.button("Spend (Bills)"):
        msg = st.session_state.engine.spend_tank()
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.rerun()

with col2: # Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # LOGIC FLOW:
        response = st.session_state.engine.process_chat(prompt)
        
        if response == "USE_HORDE":
            with st.spinner("Paige is thinking explicitly..."):
                response = st.session_state.engine.get_horde_response(prompt)
        
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()