import json
import os
import re
import random
import streamlit as st
import google.generativeai as genai

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
#      PART 2: YOUR CUSTOM LINES (The Classics)
# ==========================================
class RaunchyPersona:
    def __init__(self):
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

        self.payday_celebration = [
            "💰 **PAYDAY:** Bills paid. Bridge funded. You're handling business like a man. Come claim your reward.",
            "💰 **PAYDAY:** We survived another 2 weeks. I'm so proud of you. Now let's put the rest in the house fund.",
            "💰 **PAYDAY:** Money in the bank, roof over our head (for now). Let's get out of here."
        ]

    def get_line(self, mood):
        if mood == "sexy": return random.choice(self.sexy_praise)
        if mood == "mean": return random.choice(self.roasts)
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
        CURRENT SITUATION: {context}
        YOUR TASK:
        - If MOOD is 'sexy': Praise him. Be dirty.
        - If MOOD is 'mean': Roast him. Be sarcastic.
        - If MOOD is 'payday': Celebrate surviving another 2 weeks. Be proud.
        - Keep it short.
        """
        prompt = system_instruction.format(context=context)
        safety = [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}]
        try:
            response = self.model.generate_content(prompt, safety_settings=safety)
            return response.text
        except: return None

# ==========================================
#      PART 4: THE PRIZE WHEEL
# ==========================================
class PrizeWheel:
    def __init__(self):
        self.common = ["🏆 PRIZE: A firm handshake.", "🏆 PRIZE: I pick the movie.", "🏆 PRIZE: Dirty Joke."]
        self.rare = ["✨ PRIZE: 10 Min Massage.", "✨ PRIZE: Shower Show.", "✨ PRIZE: NSFW Photo."]
        self.legendary = ["👑 JACKPOT: The 'Full Service'.", "👑 JACKPOT: You're the boss for 1 hour.", "👑 JACKPOT: Anything you want."]

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
#      PART 5: THE LOGIC ENGINE
# ==========================================
class ExitPlanEngine:
    def __init__(self, api_key):
        self.ai = GeminiBrain(api_key)
        self.manual_persona = RaunchyPersona() 
        self.db = DataManager()
        self.wheel = PrizeWheel()
        self.data = self.db.load_data()
        
        self.daily_goal = 25.00
        self.gas_fixed = 10.00
        self.bridge_cost = 50.00 
        self.biweekly_allowance = 120.00 

    def get_message(self, context, mood):
        # 50/50 Chance to use YOUR LIST vs GEMINI
        use_ai = random.choice([True, False])
        
        response = None
        if use_ai:
            response = self.ai.generate_response(context, mood)
            
        # If AI failed or we chose the manual list:
        if not response:
            response = self.manual_persona.get_line(mood)
            
        return response

    def chat(self, user_text):
        user_text = user_text.lower()
        match = re.search(r"[-+]?\d*\.\d+|\d+", user_text)
        
        if any(w in user_text for w in ["spin", "bet", "gamble", "wheel"]):
            if not match: return "🎰 How many tickets? (e.g. 'Spin 25')"
            amount = int(float(match.group()))
            if self.data["ticket_balance"] < amount: return "🚫 Not enough tickets."
            self.data["ticket_balance"] -= amount
            self.db.save_data(self.data)
            return f"{self.wheel.spin(amount)}\n🎟️ Left: {self.data['ticket_balance']}"

        if not match:
            # Casual chat -> Always use AI
            return self.ai.generate_response(f"User said: {user_text}", "sexy") or "I only speak money, babe."

        amount = float(match.group())

        if any(w in user_text for w in ["check", "deposit", "paid", "paycheck"]):
            return self.process_payday(amount)
        elif any(w in user_text for w in ["dayforce", "avail", "balance", "earned"]):
            return self.process_shift(amount)
        elif any(w in user_text for w in ["spent", "spend", "bought", "paid", "cost"]):
            return self.track_spending(amount)
        else:
            return "🤔 Earned or Spent?"

    def track_spending(self, amount):
        if "allowance_balance" not in self.data: self.data["allowance_balance"] = 0.0
        self.data["allowance_balance"] -= amount
        self.db.save_data(self.data)
        remaining = self.data["allowance_balance"]
        
        mood = "mean" if remaining < 20 else "neutral"
        msg = self.get_message(f"Luke spent ${amount}. He has ${remaining} left.", mood)
        
        return f"💸 **RECEIPT: -${amount}**\n\n{msg}\n\n(Allowance Left: ${remaining:.2f})"

    def process_payday(self, check_amount):
        remaining = check_amount
        details = [f"💵 Check: ${check_amount}"]
        for bill, cost in self.data['bills'].items():
            remaining -= cost
            details.append(f"Paid {bill}: -${cost}")
        needed = self.bridge_cost - self.data['monday_bridge_fund']
        if needed > 0 and remaining > 0:
            fill = min(remaining, needed)
            self.data['monday_bridge_fund'] += fill
            remaining -= fill
            details.append(f"Bridge Fund: +${fill}")
        allowance = 0
        if remaining > 0:
            allowance = min(remaining, self.biweekly_allowance)
            remaining -= allowance
            self.data["allowance_balance"] = allowance 
        if remaining > 0:
            self.data['move_out_fund'] += remaining
            tickets = int(remaining / 5)
            self.data['ticket_balance'] += tickets
            details.append(f"House Fund: +${remaining}")
        self.db.save_data(self.data)
        
        msg = self.get_message("Payday! Bills paid. Allowance set.", "payday")
        return f"{msg}\n\n" + "\n".join(details) + f"\n\n😎 **ALLOWANCE:** ${allowance:.2f}"

    def process_shift(self, dayforce_available):
        if dayforce_available == 0:
            if self.data['monday_bridge_fund'] > 10:
                self.data['monday_bridge_fund'] -= 25
                self.db.save_data(self.data)
                return "🌑 **BLACKOUT:** Dayforce is $0. Bridge Fund covered expenses."
            return "⚠️ **BLACKOUT:** No money available."

        saved = dayforce_available - self.gas_fixed
        mood = "sexy" if saved >= self.daily_goal else ("mean" if saved < 5 else "neutral")
        
        if saved > 0:
            self.data['move_out_fund'] += saved
            self.data['ticket_balance'] += int(saved / 5)
        self.db.save_data(self.data)
        
        msg = self.get_message(f"Luke saved ${saved} from Dayforce today.", mood)
        return f"{msg}\n\n💰 **STASH:** ${self.data['move_out_fund']:.2f}\n🎟️ **TICKETS:** {self.data['ticket_balance']}"

# ==========================================
#      PART 6: THE STREAMLIT APP
# ==========================================
st.set_page_config(page_title="The Exit Plan", page_icon="💋", layout="wide")

# Sidebar for API Key
with st.sidebar:
    st.title("💋 The Exit Plan")
    api_key = st.text_input("Google API Key (Optional)", type="password")
    st.divider()

if 'engine' not in st.session_state:
    st.session_state.engine = ExitPlanEngine(api_key)
# Update engine if key changes
if api_key and not st.session_state.engine.ai.model:
    st.session_state.engine = ExitPlanEngine(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "💋 **Systems Online.**\nTell me: Did you earn money (Dayforce) or spend money today?"}]

# Sidebar Metrics
current_data = st.session_state.engine.db.load_data()
with st.sidebar:
    col1, col2 = st.columns(2)
    with col1: st.metric("🏠 House Fund", f"${current_data['move_out_fund']:.2f}")
    with col2: st.metric("🎟️ Tickets", f"{current_data['ticket_balance']}")
    allowance = current_data.get('allowance_balance', 0)
    st.metric("😎 Safe-to-Spend", f"${allowance:.2f}")
    st.progress(min(current_data['move_out_fund'] / 4200.0, 1.0))

# Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    response = st.session_state.engine.chat(prompt)
    with st.chat_message("assistant"): st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()