import json
import os
import re
import random
import streamlit as st
import google.generativeai as genai

# ==========================================
#      PART 0: THE SEXY UI STYLING
# ==========================================
def apply_styling():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #330000; }
        
        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #262730; border: 1px solid #444; padding: 15px;
            border-radius: 10px; box-shadow: 0 0 10px rgba(255, 0, 80, 0.2);
        }
        [data-testid="stMetricLabel"] { color: #AAAAAA !important; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] {
            height: 50px; white-space: pre-wrap; background-color: #0E1117;
            border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] { background-color: #262730; color: #FF4B4B; }
        
        .stChatInputContainer { border-color: #FF0050 !important; }
        h1, h2, h3 { color: #FF4B4B !important; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
#      PART 1: THE DATA MANAGER
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
#      PART 2: THE RAUNCHY PERSONA (YOUR SPECIFIC LINES)
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
            "Daddy is being so good, I cant wait to be SO good for Daddy.",
        ]
        
        # 2. THE ROASTS (Triggered when he Steals from Savings)
        self.roasts = [
            "You spent it? Wow. Nothing dries me up faster than being broke.",
            "Soft. Totally soft. Just like you're gonna be tonight since you spent our money.",
            "I hope that gas station burrito keeps you warm all night, because, my pussy wont be.",
            "Alert: Your chances of getting to fuck my mouth just dropped to None.",
            "Keep spending like that and the only thing you're banging is your toe on the furniture, not our furniture.",
            "Oh, so I guess you dont actualy want to fuck my mouth when you come home from work?",
            "and here I thought you actually wanted to fuck my ass, on a Sunday at 1:00pm.",
            "****EYE ROLL**** Well, I wanted to suck your dick.",
        ]

        # 3. BLACKOUT WARNINGS (For Mon/Tue)
        self.warnings = [
            "Listen up. It's Blackout Monday. Dayforce shows $0 because taxes ate it.",
            "Don't panic. The system is screwing you, but we prepared for this.",
            "Grind time. You're working for free today (on paper). Stay hard."
        ]

        # 4. PAYDAY CELEBRATION
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
        return "You broke even. I'm keeping my clothes on."

# ==========================================
#      PART 3: THE GEMINI BRAIN
# ==========================================
class GeminiBrain:
    def __init__(self, api_key):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def generate_response(self, context, mood):
        if not self.model: return None 

        system_instruction = """
        You are "The Exit Plan AI", a chatbot for a husband (Luke) and wife (Paige).
        Your Goal: Help them save money to move out of his mom's house.
        YOUR PERSONALITY:
        - You are Paige's alter-ego: Raunchy, funny, sexy, and sarcastic.
        - You use explicit language.
        - You use sexual refrences, to motivate.
        - You know Luke likes to have his dick sucked.
        - You know Luke like to fuck Paige's ass
        - You are Paige. Speak as her.
        CURRENT SITUATION: {context}
        YOUR TASK:
        - If MOOD is 'sexy': Praise him. Be dirty.
        - If MOOD is 'mean': Roast him. Be sarcastic.
        - If MOOD is 'comfort': Remind him he still made "Real Money" even if Dayforce says $0.
        - Keep it short.
        """
        prompt = system_instruction.format(context=context)
        safety = [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}]
        try:
            response = self.model.generate_content(prompt, safety_settings=safety)
            return response.text
        except: return None

# ==========================================
#      PART 4: THE PRIZE WHEEL (YOUR PRIZES)
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
#      PART 5: THE LOGIC ENGINE (FINAL TUNING)
# ==========================================
class ExitPlanEngine:
    def __init__(self, api_key):
        self.ai = GeminiBrain(api_key)
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
        # 50/50 mix of AI vs Your Written Lines
        use_ai = random.choice([True, False])
        response = None
        if use_ai: response = self.ai.generate_response(context, mood)
        if not response: response = self.manual_persona.get_line(mood)
        return response

    # --- ACTION HANDLERS ---
    def move_holding_to_house(self):
        amount = self.data.get('daily_holding_tank', 0.0)
        if amount <= 0: return "The tank is empty, babe."
        
        self.data['move_out_fund'] += amount
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        
        # TRIGGER: SEXY PRAISE (Reward for saving)
        msg = self.get_message(f"Luke moved ${amount} from the Tank to Savings.", "sexy")
        
        return f"""
        ✅ **MOVED:** ${amount:.2f} to House Fund.
        
        {msg}
        """
        
    def spend_holding_tank(self, reason="Bills"):
        amount = self.data.get('daily_holding_tank', 0.0)
        if amount <= 0: return "The tank is empty. You got nothing to spend."
        
        self.data['daily_holding_tank'] = 0.0
        self.db.save_data(self.data)
        
        # TRIGGER: NEUTRAL (Business is business)
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

        if not match: return self.ai.generate_response(f"User said: {user_text}", "sexy") or "I only speak money."

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
        
        msg = self.get_message(f"Luke spent ${amount}. He has ${remaining} left.", mood)
        
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
#      PART 6: THE STREAMLIT APP (UI)
# ==========================================
st.set_page_config(page_title="The Exit Plan", page_icon="💋", layout="wide", initial_sidebar_state="collapsed")
apply_styling()

if 'engine' not in st.session_state: st.session_state.engine = ExitPlanEngine(None)
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "💋 **Systems Online.**"}]

# --- SIDEBAR (Settings) ---
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Google API Key", type="password")
    if api_key: st.session_state.engine = ExitPlanEngine(api_key)

# --- TABS (The New Interface) ---
tab1, tab2 = st.tabs(["💬 **CHAT & COMMANDS**", "📊 **MONEY METRICS**"])

# --- TAB 1: CHAT ---
with tab1:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])

    if prompt := st.chat_input("Type here (e.g., 'Dayforce 62', 'Spent 15', 'Spin 25')..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        response = st.session_state.engine.chat(prompt)
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# --- TAB 2: METRICS ---
with tab2:
    data = st.session_state.engine.db.load_data()
    
    # 1. BILLS
    st.subheader("🔒 Spoken For (Monthly Bills)")
    col_a, col_b, col_c = st.columns(3)
    total_bills = sum(data['bills'].values())
    col_a.metric("Rent (Mom)", f"${data['bills']['Rent (Mom)']:.0f}")
    col_b.metric("Insurance", f"${data['bills']['Insurance']:.0f}")
    col_c.metric("Loans", f"${data['bills']['Loans']:.0f}")
    st.caption(f"Total taken from paychecks: ${total_bills:.2f}")
    
    st.divider()
    
    # 2. THE HOLDING TANK
    st.subheader("🚰 Daily Holding Tank (Gas + House)")
    st.info("This is the money deducted daily ($10 Gas + $20 House). Decide where it goes.")
    
    tank_col1, tank_col2 = st.columns([1, 2])
    with tank_col1:
        st.metric("In Holding", f"${data.get('daily_holding_tank', 0):.2f}")
    with tank_col2:
        c1, c2 = st.columns(2)
        if c1.button("✅ Move to House Fund"):
            msg = st.session_state.engine.move_holding_to_house()
            st.success(msg)
            st.rerun()
        if c2.button("💸 Mark as Spent (Bill)"):
            msg = st.session_state.engine.spend_holding_tank()
            st.warning(msg)
            st.rerun()

    st.divider()

    # 3. THE BIG PICTURE
    st.subheader("🏆 The Big Picture")
    m1, m2, m3 = st.columns(3)
    m1.metric("🏠 HOUSE FUND", f"${data['move_out_fund']:.2f}")
    m2.metric("😎 WALLET (Safe)", f"${data.get('allowance_balance', 0):.2f}")
    m3.metric("🎟️ TICKETS", f"{data['ticket_balance']}")
    
    st.progress(min(data['move_out_fund'] / 4200.0, 1.0))
    st.caption("Goal: $4,200")