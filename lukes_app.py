import json
import os
import re
import random
import time
import requests
import streamlit as st

# ==========================================
#       PART 0: THE SEXY UI STYLING
# ==========================================
def apply_styling():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #330000; }
        
        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #262730; border: 1px solid #444; padding: 10px;
            border-radius: 10px; box-shadow: 0 0 10px rgba(255, 0, 80, 0.2);
            margin-bottom: 10px;
        }
        [data-testid="stMetricLabel"] { color: #AAAAAA !important; font-size: 0.8rem !important; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.2rem !important; }
        
        .stChatInputContainer { border-color: #FF0050 !important; }
        h1, h2, h3 { color: #FF4B4B !important; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
#       PART 1: THE DATA MANAGER
# ==========================================
class DataManager:
    def __init__(self):
        self.filename = "exit_plan_data.json"
        
    def load_data(self):
        defaults = {
            "move_out_fund": 0.0,
            "ticket_balance": 0,
            "monday_bridge_fund": 0.0,
            "allowance_balance": 0.0,
            "daily_holding_tank": 0.0,
            "bills": {"Rent (Mom)": 200.00, "Insurance": 100.00, "Loans": 80.00}
        }
        if not os.path.exists(self.filename): return defaults
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for key, value in defaults.items():
                    if key not in data: data[key] = value
                return data
        except: return defaults

    def save_data(self, data):
        with open(self.filename, 'w') as f: json.dump(data, f)

# ==========================================
#       PART 2: THE RAUNCHY PERSONA (MANUAL BACKUP)
# ==========================================
class RaunchyPersona:
    def __init__(self):
        # 1. THE TURN ON (Triggered when he Moves Tank -> House)
        self.sexy_praise = [
            "Good boy, Do you want a sloppy blow job in the kitchen? I want to give it to you.",
            "Good boy. You kept the money safe.",
            "That's hot. One more step closer to a giant bottle of Lube, and you and me.",
            "You saved $25? I think I just lost my panties. Oops.",
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
        
        # 2. THE ROASTS (Triggered when he Spends)
        self.roasts = [
            "You spent it? Wow. Nothing dries me up faster than being broke.",
            "Soft. Totally soft. Just like you're gonna be tonight since you spent our money.",
            "I hope that gas station burrito keeps you warm all night, because, my pussy wont be.",
            "Alert: Your chances of getting to fuck my mouth just dropped to None.",
            "Keep spending like that and the only thing you're banging is your toe on the furniture, not our furniture.",
            "Oh, so I guess you dont actualy want to fuck my mouth when you come home from work?",
            "and here I thought you actually wanted to fuck my ass, on a Sunday at 1:00pm.",
            "****EYE ROLL**** Well, I wanted to suck your dick."
        ]
        
        # 3. CASUAL FLIRTING (Backup if AI is slow/down)
        self.casual_flirt = [
            "I'm bored... and horny. Dangerous combination. Get home.",
            "Stop texting and make money so I can sit on your face later.",
            "I'm not wearing any panties right now. Just thought you should know.",
            "I was just thinking about your hands on me. Focus on work, but hurry home.",
            "My knees are waiting for you, Daddy.",
            "Are you being a good boy? Or do I need to punish you tonight?",
            "Less talking, more stacking cash. I want to scream your name in our own bedroom.",
            "I might be touching myself thinking about you. Guess you'll find out later.",
            "Send me a picture. I need something to look at while I wait for you."
        ]

        # 4. BLACKOUT WARNINGS
        self.warnings = [
            "Listen up. It's Blackout Monday. Dayforce shows $0 because taxes ate it.",
            "Don't panic. The system is screwing you, but we prepared for this.",
            "Grind time. You're working for free today (on paper). Stay hard."
        ]

        # 5. PAYDAY CELEBRATION
        self.payday_celebration = [
            "💰 **PAYDAY:** Bills paid. Bridge funded. You're handling business like a man. CUM claim your spin.",
            "💰 **PAYDAY:** We survived another 2 weeks. I'm so proud of you. Spin now? or save it?",
            "💰 **PAYDAY:** Money in the bank, roof over our head (for now). Let's get out of here."
        ]

    def get_line(self, mood):
        if mood == "sexy": return random.choice(self.sexy_praise)
        if mood == "mean": return random.choice(self.roasts)
        if mood == "comfort": return random.choice(self.warnings)
        if mood == "payday": return random.choice(self.payday_celebration)
        if mood == "flirt": return random.choice(self.casual_flirt)
        return "You broke even. I'm keeping my clothes on."

# ==========================================
#       PART 3: THE UNCENSORED HORDE BRAIN
# ==========================================
class HordeBrain:
    def __init__(self, char_name="Paige", user_name="Luke", relationship="Wife/Husband"):
        self.api_key = "0000000000" 
        self.api_url = "https://stablehorde.net/api/v2/generate/text/async"
        self.status_url = "https://stablehorde.net/api/v2/generate/text/status"
        self.fallback = RaunchyPersona()
        
        self.char_name = char_name
        self.user_name = user_name
        self.relationship = relationship

    def generate_response(self, context, mood):
        # 1. The Prompt (Explicit allowed here)
        prompt = f"""
        Character: {self.char_name}. User: {self.user_name}.
        Relationship: {self.relationship}.
        Personality: Raunchy, slutty, sarcastic, loving, explicit.
        Scenario: {context}
        {self.char_name}:
        """
        
        payload = {
            "prompt": prompt,
            "params": {
                "n": 1,
                "max_context_length": 1024,
                "max_length": 60, # Keep replies short
                "rep_pen": 1.1,
                "temperature": 0.8,
                "top_p": 0.9
            },
            "models": ["KoboldCPP"], # Asks for generic models
            "nsfw": True,  # <--- THE MAGIC SWITCH
            "censor_nsfw": False
        }
        
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}

        try:
            # Step A: Send Request
            post_req = requests.post(self.api_url, json=payload, headers=headers)
            if post_req.status_code != 202:
                return self.fallback.get_line("flirt") # Fallback if horde is down
            
            job_id = post_req.json()["id"]
            
            # Step B: Wait for Volunteer (Simple Polling for 20s)
            for _ in range(20): 
                time.sleep(1)
                check = requests.get(f"{self.status_url}/{job_id}", headers=headers)
                status = check.json()
                
                if status["done"]:
                    return status["generations"][0]["text"].strip()
            
            # If timed out, use manual flirt
            return self.fallback.get_line("flirt") 
            
        except:
            return self.fallback.get_line("flirt")

# ==========================================
#       PART 4: THE PRIZE WHEEL
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
#       PART 5: THE LOGIC ENGINE
# ==========================================
class ExitPlanEngine:
    def __init__(self):
        # We start with defaults, but user can change them in sidebar
        self.ai = HordeBrain() 
        self.manual_persona = RaunchyPersona() 
        self.db = DataManager()
        self.wheel = PrizeWheel()
        self.data = self.db.load_data()
        
        # MATH CONFIGURATION
        self.daily_house_goal = 20.00
        self.gas_fixed = 10.00 
        self.bridge_cost = 50.00 
        self.biweekly_allowance = 120.00
        self.hourly_rate = 19.60
        self.shift_hours = 8.0
        self.tax_rate = 0.20 

    def get_message(self, context, mood):
        # PRIORITY 1: If Sexy or Mean, USE MANUAL LINES ONLY
        if mood == "sexy" or mood == "mean":
            return self.manual_persona.get_line(mood)

        # PRIORITY 2: For casual chat/flirt, try the Uncensored AI
        return self.ai.generate_response(context, mood)

    # --- ACTION HANDLERS ---
    def move_holding_to_house(self):
        amount = self.data.get('daily_holding_tank', 0.0)
        if amount <= 0: return "The tank is empty, babe."
        
        self.data['move_out_fund'] += amount
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        
        # TRIGGER: SEXY PRAISE
        msg = self.get_message(f"{self.ai.user_name} moved ${amount} from the Tank to Savings.", "sexy")
        
        return f"""
        ✅ **MOVED:** ${amount:.2f} to House Fund.
        
        {msg}
        """
        
    def spend_holding_tank(self, reason="Bills"):
        amount = self.data.get('daily_holding_tank', 0.0)
        if amount <= 0: return "The tank is empty. You got nothing to spend."
        
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        
        # TRIGGER: NEUTRAL
        return f"💸 **TANK EMPTIED:** Used ${amount:.2f} for {reason}. (Bills paid. No damage done)."

    def chat(self, user_text):
        user_text = user_text.lower()
        match = re.search(r"[-+]?\d*\.\d+|\d+", user_text)
        
        # TANK COMMANDS
        if "tank" in user_text and any(w in user_text for w in ["pay", "spent", "spend", "bill", "use"]):
            return self.spend_holding_tank(reason="Bills")
        if "tank" in user_text and any(w in user_text for w in ["save", "move", "house", "fund"]):
            return self.move_holding_to_house()

        # ADMIN COMMANDS
        if "set wallet" in user_text and match:
            self.data["allowance_balance"] = float(match.group()); self.db.save_data(self.data)
            return f"🔧 **ADMIN:** Wallet set to ${float(match.group()):.2f}"
        if "set tickets" in user_text and match:
            self.data["ticket_balance"] = int(float(match.group())); self.db.save_data(self.data)
            return f"🔧 **ADMIN:** Tickets set to {int(float(match.group()))}"
        if "set holding" in user_text and match:
            self.data["daily_holding_tank"] = float(match.group()); self.db.save_data(self.data)
            return f"🔧 **ADMIN:** Holding Tank set to ${float(match.group()):.2f}"
        if "set bridge" in user_text and match:
            self.data["monday_bridge_fund"] = float(match.group()); self.db.save_data(self.data)
            return f"🔧 **ADMIN:** Bridge set to ${float(match.group()):.2f}"

        # WHEEL
        if any(w in user_text for w in ["spin", "bet", "gamble", "wheel"]):
            if not match: return "🎰 How many tickets? (e.g. 'Spin 25')"
            amount = int(float(match.group()))
            if self.data["ticket_balance"] < amount: return "🚫 Not enough tickets."
            self.data["ticket_balance"] -= amount
            self.db.save_data(self.data)
            return f"{self.wheel.spin(amount)}\n🎟️ Left: {self.data['ticket_balance']}"

        if not match: 
            # CASUAL CHAT (Uses Horde/Uncensored)
            return self.ai.generate_response(user_text, "flirt")

        amount = float(match.group())

        if any(w in user_text for w in ["check", "deposit", "paid", "paycheck"]):
            return self.process_payday(amount)
        elif any(w in user_text for w in ["dayforce", "avail", "balance", "earned"]):
            return self.process_shift(amount)
        elif any(w in user_text for w in ["spent", "spend", "bought", "paid", "cost"]):
            return self.track_spending(amount)
        else: return "🤔 Earned or Spent?"

    def track_spending(self, amount):
        if "allowance_balance" not in self.data: self.data["allowance_balance"] = 0.0
        self.data["allowance_balance"] -= amount
        remaining = self.data["allowance_balance"]
        penalty_msg = ""
        
        # CHECK FOR THE "DIP" (Stealing from Savings)
        if remaining < 0:
            overdraft = abs(remaining)
            if self.data["move_out_fund"] > 0:
                self.data["move_out_fund"] -= overdraft
                self.data["allowance_balance"] = 0.0
                remaining = 0.0
                penalty_msg = f"\n📉 **PENALTY:** You went broke, so I took ${overdraft:.2f} from the House Fund."
        
        self.db.save_data(self.data)
        
        # TRIGGER: MEAN / ROAST (If Penalty or Broke)
        mood = "mean" if (remaining < 20 or penalty_msg) else "neutral"
        
        msg = self.get_message(f"{self.ai.user_name} spent ${amount}. He has ${remaining} left.", mood)
        
        return f"""
        💸 **RECEIPT: -${amount}**
        
        {msg}
        {penalty_msg}
        
        (Wallet: ${remaining:.2f})
        """

    def process_payday(self, check_amount):
        remaining = check_amount
        details = [f"💵 Check: ${check_amount}"]
        
        # 1. TICKET BONUSES
        tickets_earned = 0
        tier_msg = ""
        if check_amount >= 601: tickets_earned = 50; tier_msg = "👑 **GOLD TIER BONUS:** +50 Tickets!"
        elif check_amount >= 551: tickets_earned = 25; tier_msg = "✨ **SILVER TIER BONUS:** +25 Tickets!"
        elif check_amount >= 400: tickets_earned = 10; tier_msg = "🥉 **BRONZE TIER BONUS:** +10 Tickets."
        else: tickets_earned = 0; tier_msg = "🚫 **NO BONUS:** Check too low for tickets."
        self.data['ticket_balance'] += tickets_earned
        
        # 2. BILLS
        for bill, cost in self.data['bills'].items():
            remaining -= cost
            details.append(f"Paid {bill}: -${cost}")
            
        # 3. BRIDGE
        needed = self.bridge_cost - self.data['monday_bridge_fund']
        if needed > 0 and remaining > 0:
            fill = min(remaining, needed)
            self.data['monday_bridge_fund'] += fill
            remaining -= fill
            details.append(f"Bridge Fund: +${fill}")
            
        # 4. ALLOWANCE
        allowance = 0
        if remaining > 0:
            allowance = min(remaining, self.biweekly_allowance)
            remaining -= allowance
            self.data["allowance_balance"] = allowance 
            
        # 5. HOUSE FUND
        if remaining > 0:
            self.data['move_out_fund'] += remaining
            details.append(f"House Fund: +${remaining}")
            
        self.db.save_data(self.data)
        msg = self.get_message("Payday! Bills paid. Allowance set.", "payday")
        return f"{msg}\n{tier_msg}\n" + "\n".join(details) + f"\n\n😎 **ALLOWANCE:** ${allowance:.2f}"

    def process_shift(self, dayforce_available):
        # 1. REAL MONEY CALC
        real_gross = self.hourly_rate * self.shift_hours
        real_net = real_gross * (1 - self.tax_rate) 
        
        # 2. BLACKOUT
        if dayforce_available == 0:
            if self.data['monday_bridge_fund'] > 10:
                self.data['monday_bridge_fund'] -= 25 
                self.db.save_data(self.data)
                msg = self.get_message("Dayforce is $0 due to Blackout. Bridge Fund covered expenses.", "comfort")
                return f"{msg}\n\n(Bridge Fund used: -$25.00)"
            return "⚠️ **BLACKOUT:** No money available."

        # 3. HOLDING TANK LOGIC
        amount_to_hold = min(dayforce_available, self.gas_fixed + self.daily_house_goal)
        
        if "daily_holding_tank" not in self.data: self.data["daily_holding_tank"] = 0.0
        self.data["daily_holding_tank"] += amount_to_hold
        
        # The rest is his Safe Spend
        safe_spend = max(0, dayforce_available - amount_to_hold)
        
        self.db.save_data(self.data)
        
        # Just an update, no emotion needed until he moves the tank
        msg = "Funds locked in tank. " 
        if safe_spend > 0: msg += f"You have ${safe_spend} safe to spend."
        
        return f"""
        {msg}
        
        📊 **SHIFT REPORT**
        Dayforce: ${dayforce_available}
        - To Holding Tank: ${amount_to_hold:.2f}
        (Gas + Daily House Goal)
        
        ✅ **SAFE TO BLOW:** ${safe_spend:.2f}
        
        👉 **ACTION:** Text "Use tank for bill" OR "Move tank to house"
        """

# ==========================================
#       PART 6: THE STREAMLIT APP (UI)
# ==========================================
st.set_page_config(page_title="The Exit Plan", page_icon="💋", layout="wide", initial_sidebar_state="collapsed")
apply_styling()

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine()
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "💋 **Systems Online.**"}]

# --- SIDEBAR (PERSONA SETTINGS) ---
with st.sidebar:
    st.title("💋 Persona Settings")
    
    char_name = st.text_input("Her Name", value="Paige")
    user_name = st.text_input("Your Name", value="Luke")
    relation = st.text_input("Relationship", value="Wife/Husband")
    
    if st.button("Update Persona"):
        st.session_state.engine.ai.char_name = char_name
        st.session_state.engine.ai.user_name = user_name
        st.session_state.engine.ai.relationship = relation
        st.success(f"Updated! She is now {char_name}.")
    
    st.divider()
    st.caption("Using AI Horde (Uncensored)")

# --- SPLIT LAYOUT (DASHBOARD LEFT, CHAT RIGHT) ---
col_dashboard, col_chat = st.columns([1, 1.5])

# --- LEFT COLUMN: DASHBOARD ---
with col_dashboard:
    data = st.session_state.engine.db.load_data()
    
    # 1. THE BIG PICTURE
    st.subheader("🏆 The Big Picture")
    m1, m2 = st.columns(2)
    m1.metric("🏠 HOUSE FUND", f"${data['move_out_fund']:.2f}")
    m2.metric("😎 WALLET (Safe)", f"${data.get('allowance_balance', 0):.2f}")
    
    st.progress(min(data['move_out_fund'] / 4200.0, 1.0))
    st.caption("Goal: $4,200")
    
    st.divider()

    # 2. THE HOLDING TANK
    st.subheader("🚰 Daily Tank")
    st.info("Gas ($10) + House ($20)")
    
    st.metric("In Holding", f"${data.get('daily_holding_tank', 0):.2f}")
    
    # Action Buttons
    c1, c2 = st.columns(2)
    if c1.button("✅ Move to House"):
        msg = st.session_state.engine.move_holding_to_house()
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.rerun()
    if c2.button("💸 Spend (Bills)"):
        msg = st.session_state.engine.spend_holding_tank()
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.rerun()

    st.divider()

    # 3. TICKETS & BILLS
    st.metric("🎟️ TICKETS", f"{data['ticket_balance']}")
    st.caption("Earned from Paychecks over $400")

# --- RIGHT COLUMN: CHAT ---
with col_chat:
    st.subheader("💬 Chat")
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])

    # Chat Input (Fixed to bottom)
    if prompt := st.chat_input("Command me (e.g. 'Dayforce 62', 'Spent 15')..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Show a "Thinking" spinner because AI Horde can be slow
        with st.spinner(f"{st.session_state.engine.ai.char_name} is typing..."):
            response = st.session_state.engine.chat(prompt)
        
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()