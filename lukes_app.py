import json
import os
import random
import time
import streamlit as st

# ==========================================
#       PART 1: SETUP & STYLING
# ==========================================
st.set_page_config(page_title="Exit Plan", page_icon="🎰", layout="wide")

st.markdown("""
    <style>
    /* LIGHT THEME */
    .stApp { background-color: #F2F4F8; color: #000000; }
    
    /* CHAT CONTAINER */
    .chat-container {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #E0E0E0;
    }

    /* BUBBLES */
    div[data-testid="stChatMessage"] {
        background-color: #F9FAFC; 
        border: 1px solid #D1D5DB;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stChatMessage"] p, .stMarkdown p {
        color: #000000 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 16px;
        line-height: 1.5;
    }
    
    /* NARRATOR */
    .narrator {
        color: #555555;
        font-style: italic;
        font-size: 15px;
        margin: 10px 0;
        padding-left: 10px;
        border-left: 3px solid #FF4B4B;
    }

    /* BUTTONS */
    .stButton button { 
        width: 100%; border-radius: 8px; font-weight: bold; min-height: 45px;
        background-color: #FFFFFF; color: #000000; border: 1px solid #000000;
    }
    .stButton button:hover {
        background-color: #F0F0F0; border-color: #FF4B4B; color: #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
#       PART 2: STATE MANAGEMENT
# ==========================================
if "ticket_balance" not in st.session_state: st.session_state.ticket_balance = 0
if "casino_history" not in st.session_state: st.session_state.casino_history = []
if "turn_state" not in st.session_state: st.session_state.turn_state = "WALLET_CHECK"
if "current_prize" not in st.session_state: st.session_state.current_prize = None
if "check_amount" not in st.session_state: st.session_state.check_amount = 0.0

# ==========================================
#       PART 3: HELPER FUNCTIONS
# ==========================================
def add_chat(role, content):
    st.session_state.casino_history.append({"type": "chat", "role": role, "content": content})

def add_narrator(content):
    st.session_state.casino_history.append({"type": "narrator", "content": content})

def add_media(filepath, media_type="image"):
    st.session_state.casino_history.append({"type": "media", "path": filepath, "kind": media_type})

def simulate_typing(seconds=1.5):
    placeholder = st.empty()
    placeholder.caption("💬 *Paige is typing...*")
    time.sleep(seconds)
    placeholder.empty()

def simulate_loading(seconds=1.5):
    placeholder = st.empty()
    with placeholder.container():
        with st.spinner("Loading content..."):
            time.sleep(seconds)
    placeholder.empty()

def spin_the_wheel_animation(tier_name, possible_prizes):
    placeholder = st.empty()
    for _ in range(8):
        placeholder.markdown(f"### 🎰 ... {random.choice(possible_prizes)} ...")
        time.sleep(0.1)
    for _ in range(5):
        placeholder.markdown(f"### 🎰 ... {random.choice(possible_prizes)} ...")
        time.sleep(0.3)
    winner = random.choice(possible_prizes)
    placeholder.markdown(f"### 🎉 WINNER: {winner} 🎉")
    time.sleep(2.0)
    placeholder.empty()
    return winner

# ==========================================
#       PART 4: MAIN INTERFACE
# ==========================================
st.title("🎰 The Office & Casino")

# Top Bar
col1, col2 = st.columns([3,1])
col1.metric("Tickets", st.session_state.ticket_balance)
if col2.button("Reset System"):
    st.session_state.ticket_balance = 0
    st.session_state.casino_history = []
    st.session_state.turn_state = "WALLET_CHECK"
    st.rerun()

st.divider()

# --- CHAT HISTORY ---
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if not st.session_state.casino_history:
        st.caption("System Online...")

    for item in st.session_state.casino_history:
        if item["type"] == "chat":
            avatar = "paige.png" if item["role"] == "assistant" else "😎"
            if item["role"] == "assistant" and not os.path.exists("paige.png"): avatar = "💋"
            with st.chat_message(item["role"], avatar=avatar):
                st.write(item["content"])
        
        elif item["type"] == "narrator":
            st.markdown(f"<div class='narrator'>{item['content']}</div>", unsafe_allow_html=True)
        
        elif item["type"] == "media":
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if os.path.exists(item["path"]):
                    if item["kind"] == "video": st.video(item["path"])
                    else: st.image(item["path"], width=350)
                else:
                    st.error(f"⚠️ Missing File: {item['path']}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
#       PART 5: LOGIC CONTROLLER
# ==========================================

# --- 1. WALLET CHECK (The Input) ---
if st.session_state.turn_state == "WALLET_CHECK":
    add_chat("assistant", "Systems Online. Wallet check. Is there something you want to tell me? Remember, the faster we fill that savings tank, the faster you can fill all of my little holes up in our own bedroom…")
    
    amount = st.number_input("Enter Check Amount ($):", min_value=0.0, step=10.0)
    
    if st.button("Submit Check"):
        st.session_state.check_amount = amount
        st.session_state.casino_history = [] # Clear intro
        
        # LOGIC BRANCHES
        if amount < 450:
            st.session_state.turn_state = "CHECK_FAIL"
        elif 450 <= amount < 500:
            st.session_state.turn_state = "CHECK_BRONZE"
            # Add Bronze Tickets
            st.session_state.ticket_balance += 25
        else:
            st.session_state.turn_state = "CHECK_SILVER_GOLD"
            # Add Silver Tickets
            st.session_state.ticket_balance += 50
            
        st.rerun()

# --- 2. CHECK RESPONSES ---

if st.session_state.turn_state == "CHECK_FAIL":
    simulate_typing(3)
    add_chat("assistant", "Under 450? You must have been sick or something? It's an effort. But here efforts don't really count for much.. and…. almost doesn’t unlock the good girl switch, does it, baby?")
    
    simulate_typing(3)
    add_chat("assistant", "So here’s the deal: no ‘Daddy’ tonight. No ‘Good Boy.’ No pretty mouth wrapped around that cock. No riding you until we both forget how to breathe.")
    
    simulate_loading(2)
    # Placeholder name, ensures safe lowercase
    add_media("laying_down.jpeg") 
    
    add_narrator("I trail one fingernail lightly down the center of my own chest, stopping just above the waistband.")
    
    simulate_typing(3)
    add_chat("assistant", "Closed for business. You can look. You can beg. You can jerk off in the shower like a sad little teenager if you want. But you don’t get to touch. Not tonight.")
    add_chat("assistant", "Better luck next check handsome.")
    
    if st.button("Reset"): st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

elif st.session_state.turn_state == "CHECK_BRONZE":
    amt = st.session_state.check_amount
    add_narrator("A slow, dangerous smile curls my lips. Not quite a smirk… but definitely not the eager grin you get when you break five hundred.")
    
    if 450 <= amt <= 459:
        add_chat("assistant", "Four… fifty. Not bad, baby. Not great. Solid middle-class effort.")
    elif 460 <= amt <= 469:
        add_chat("assistant", "Well I guess it's better than the alternative.. nothing. But not enough to buy you anything you really want.")
    else:
        add_chat("assistant", "Solid effort, I guess we didn't save this week. Well you can have a bronze spin if you want.")
        
    add_chat("assistant", "Do you want to save your tickets or spin the bronze wheel now?")
    st.session_state.turn_state = "DECIDE_BRONZE"
    st.rerun()

elif st.session_state.turn_state == "CHECK_SILVER_GOLD":
    msgs = ["Good boy. You kept the money safe.", "That's hot. One more step closer to a giant bottle of Lube.", "Daddy's making moves! Keep stacking cash and I'll keep arching my back.", "My baby is saving, saving up to fuck my mouth in his own home."]
    add_chat("assistant", random.choice(msgs))
    add_chat("assistant", "Silver Tier access. No Bronze pity party tonight, congrats. But don’t get cocky.")
    
    simulate_typing(3)
    add_chat("assistant", "You’ve earned one spin on the Silver Wheel. One chance to get something that actually involves my mouth, my hands… or maybe even my pussy if the stars align.")
    
    add_narrator("I tap the screen once, twice—Silver Wheel loading, shimmering silver and gold.")
    add_chat("assistant", "Spin it, baby. Show me what your silver spin check bought you tonight.")
    
    st.session_state.turn_state = "DECIDE_SILVER"
    st.rerun()

# --- 3. SPIN DECISIONS ---

if st.session_state.turn_state == "DECIDE_BRONZE":
    c1, c2 = st.columns(2)
    if c1.button("Spin Bronze"):
        add_narrator("I watch you toss the bronze token into the app with that hopeful little look—like a kid who thinks he might still get dessert after eating all his vegetables.")
        st.session_state.turn_state = "SPIN_BRONZE"
        st.rerun()
    if c2.button("Save"):
        st.info("Tickets Saved.")
        st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

if st.session_state.turn_state == "DECIDE_SILVER":
    c1, c2 = st.columns(2)
    if c1.button("Spin Silver"):
        add_narrator("I tap the screen with a flourish, the Silver Wheel spinning to life in a swirl of metallic shimmer.")
        st.session_state.turn_state = "SPIN_SILVER"
        st.rerun()
    if c2.button("Save"):
        st.info("Tickets Saved.")
        st.session_state.turn_state = "WALLET_CHECK"; st.rerun()

# --- 4. WHEEL LOGIC ---

if st.session_state.turn_state == "SPIN_BRONZE":
    prizes = ["Bend Over", "Flash Me", "Dick Rub", "Jackoff Pass"]
    winner = spin_the_wheel_animation("Bronze", prizes)
    st.session_state.current_prize = winner
    add_chat("assistant", f"🥉 WINNER: {winner}")
    st.session_state.turn_state = f"PRIZE_{winner.replace(' ', '_').upper()}"
    st.rerun()

if st.session_state.turn_state == "SPIN_SILVER":
    prizes = ["Massage", "Shower Show", "Toy Pic", "Lick Pussy", "Nude Pic", "Tongue Tease", "No Panties", "Road Head", "Plug Tease"]
    winner = spin_the_wheel_animation("Silver", prizes)
    st.session_state.current_prize = winner
    add_chat("assistant", f"🥈 WINNER: {winner}")
    st.session_state.turn_state = f"PRIZE_{winner.replace(' ', '_').upper()}"
    st.rerun()


# ==========================================
#       PART 6: SILVER PRIZES
# ==========================================

# --- MASSAGE ---
if st.session_state.turn_state == "PRIZE_MASSAGE":
    add_chat("assistant", "Looks like you’ve won a massage…")
    if st.button("Shirtless?"):
        st.empty()
        simulate_typing(2)
        add_chat("assistant", "Mmm… you know I can’t make any promises. But the rules are simple: ten minutes, oil, and… well, let’s just say I’ll tease you until you’re begging for more.")
        st.session_state.turn_state = "PRIZE_MASSAGE_2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_MASSAGE_2":
    if st.button("Tell me more?"):
        st.empty()
        simulate_typing(3)
        add_chat("assistant", "I know how you like it, start with your shoulders... firm circles on your lower back. My hands will work out every knot while my body brushes against yours. Maybe a few 'accidental' grazes over sensitive areas... you'll be aching for me.")
        st.session_state.turn_state = "PRIZE_MASSAGE_3"
        st.rerun()

if st.session_state.turn_state == "PRIZE_MASSAGE_3":
    if st.button("Show me"):
        st.empty()
        simulate_loading(3)
        add_media("massage.jpeg")
        add_chat("assistant", "I'll work out every knot.")
        add_narrator("I shift in my seat, pressing my thighs together.")
        st.session_state.turn_state = "PRIZE_MASSAGE_FINAL"
        st.rerun()

if st.session_state.turn_state == "PRIZE_MASSAGE_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("Use Today"): st.info("Timer starts now."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- SHOWER SHOW ---
if st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("My eyes flick up, corner of my mouth lifting in a slow, wicked smile.")
    simulate_typing(2)
    add_chat("assistant", "Ohhh… look at that. Rules are simple: You sit on the edge of the bathtub. You watch. You dry me off when I’m done.")
    
    simulate_loading(3)
    add_media("shower.jpeg")
    
    simulate_typing(3)
    add_chat("assistant", "Hot water steaming up the glass... I’ll face you so you can see everything, but you can’t touch. Not yet.")
    
    time.sleep(3)
    simulate_loading(3)
    add_media("shower_video1.mp4", "video")
    
    simulate_typing(2)
    add_chat("assistant", "Maybe I'll let you dry me off with your tongue.")
    st.session_state.turn_state = "PRIZE_SHOWER_FINAL"
    st.rerun()

if st.session_state.turn_state == "PRIZE_SHOWER_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("Use tonight"): st.info("Go to the bathroom."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- TOY PIC ---
if st.session_state.turn_state == "PRIZE_TOY_PIC":
    add_chat("assistant", "Looks like you’ve leveled up. Rules are simple: You pick the toy. You pick the spot. I take the photo.")
    simulate_loading(3)
    add_media("toy_pic.jpeg")
    simulate_typing(3)
    add_chat("assistant", "Maybe the end of your screwdriver, deep in my pussy, or the vibrating bullet tucked in my tight ass. Tell me exactly which hole to fill.")
    st.session_state.turn_state = "PRIZE_TOY_2"
    st.rerun()

if st.session_state.turn_state == "PRIZE_TOY_2":
    if st.button("Show me"):
        st.empty()
        simulate_loading(4)
        add_media("toy_ass1.jpeg")
        add_chat("assistant", "I’ll make sure you can see how deep it goes and how dripping wet I am.")
        st.session_state.turn_state = "PRIZE_TOY_FINAL"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TOY_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("Claim now"): st.info("Check inbox."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- LICK PUSSY ---
if st.session_state.turn_state == "PRIZE_LICK_PUSSY":
    add_chat("assistant", "Tonight you get to worship me properly.")
    add_narrator("I’m already getting wet just thinking about it.")
    
    if st.button("How do you like it?"):
        st.empty()
        simulate_typing(3)
        add_chat("assistant", "You know how I like it, slow circles around my clit first, then long, flicks up my slit… tease the entrance, push your tongue inside.")
        st.session_state.turn_state = "PRIZE_LICK_2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_LICK_2":
    if st.button("Show me"):
        st.empty()
        simulate_loading(3)
        # Ensuring lowercase
        img = random.choice(["pussy_lick2.jpeg", "pussy_lick1.jpeg", "pussy_lick3.jpeg"])
        add_media(img)
        add_chat("assistant", "I'll ride your tongue until my thighs shake and I soak you.")
        st.session_state.turn_state = "PRIZE_LICK_FINAL"
        st.rerun()

if st.session_state.turn_state == "PRIZE_LICK_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("Claim today"): st.info("Get on your knees."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- NUDE PIC ---
if st.session_state.turn_state == "PRIZE_NUDE_PIC":
    add_chat("assistant", "Ohhh… look at that. Rules are simple: You pick the pose. You pick the part. I send the proof.")
    simulate_loading(3)
    add_media("nude_pic1.jpeg")
    add_chat("assistant", "Do you want my ass in the air? Maybe a close-up of my tits? I’ll make sure the lighting is perfect.")
    
    c1, c2 = st.columns(2)
    if c1.button("Claim now"): st.info("Sent."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- TONGUE TEASE ---
if st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    add_chat("assistant", "Oh this is a good one. Stroke it slow for me but won't cum until I say.")
    if st.button("Tell me the rules"):
        st.empty()
        simulate_loading(3)
        add_media("tease1.jpeg")
        add_chat("assistant", "I’ll be on my knees. This prize is all about my tongue… teasing you until you’re dripping.")
        st.session_state.turn_state = "PRIZE_TEASE_2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TEASE_2":
    if st.button("And then what?"):
        st.empty()
        add_narrator("My tongue slips out and hovers an inch away. I let a single thick string of spit drip slowly from the tip of my tongue onto your shaft.")
        simulate_typing(3)
        add_chat("assistant", "Keep stroking. Nice and slow.")
        
        simulate_loading(3)
        add_media("tease2.jpeg")
        
        add_chat("assistant", "Come for me—right on my tongue—give it all to me—")
        simulate_loading(3)
        # Ensuring lowercase
        add_media("jerking1.jpeg")
        
        st.session_state.turn_state = "PRIZE_TEASE_FINAL"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TEASE_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("Use Today"): st.info("Unzip."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- NO PANTIES ---
if st.session_state.turn_state == "PRIZE_NO_PANTIES":
    add_chat("assistant", "Rules are simple, baby. I wear a dress or skirt. I wear nothing underneath. You get to verify.")
    if st.button("Tell me more"):
        st.empty()
        add_chat("assistant", "At the grocery store… bending over to get food from the bottom shelf. No one else knows that I’m completely bare.")
        simulate_loading(3)
        add_media("exposed2.jpeg")
        st.session_state.turn_state = "PRIZE_NO_PANTIES_2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_NO_PANTIES_2":
    if st.button("Show me"):
        st.empty()
        simulate_loading(3)
        add_media("exposed1.jpeg")
        add_chat("assistant", "I’m going to be dripping wet by the time we get home.")
        st.session_state.turn_state = "PRIZE_NO_PANTIES_FINAL"
        st.rerun()

if st.session_state.turn_state == "PRIZE_NO_PANTIES_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("Claim now"): st.info("Done."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- PLUG TEASE ---
if st.session_state.turn_state == "PRIZE_PLUG_TEASE":
    add_narrator("I've been planning this whole thing out for days now.")
    add_chat("assistant", "I'll get the oil and find the toy you left me. Ill slide it in, without making a sound.")
    simulate_loading(3)
    # Corrected ext
    add_media("plug3.jfif")
    
    add_chat("assistant", "Ill get dressed and continue on with my day. Every movement reminding me of the secret. You'll come home and remove it.")
    simulate_loading(3)
    # Corrected ext
    add_media("plug2.jfif")
    
    c1, c2 = st.columns(2)
    if c1.button("Use Today"): st.info("Plug in."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

# --- ROAD HEAD ---
if st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    add_chat("assistant", "You've won yourself a little something extra special tonight… 'Road Head'.")
    if st.button("What will you do?"):
        st.empty()
        add_chat("assistant", "Baby, there's so much more to it than just putting your dick in my mouth while driving… It's an art form.")
        simulate_typing(3)
        add_chat("assistant", "And the thrill of risk adds another layer of excitement. Knowing that if you don't pay attention, we could both end up in a terrible accident…")
        st.session_state.turn_state = "PRIZE_ROAD_HEAD_2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_ROAD_HEAD_2":
    if st.button("Want a preview?"):
        st.empty()
        simulate_loading(3)
        add_media("road_head.jpeg")
        add_chat("assistant", "So what do you say, babe? Are you ready for the ride of your life?")
        simulate_loading(3)
        add_media("road_head_video.mp4", "video")
        st.session_state.turn_state = "PRIZE_ROAD_HEAD_FINAL"
        st.rerun()

if st.session_state.turn_state == "PRIZE_ROAD_HEAD_FINAL":
    c1, c2 = st.columns(2)
    if c1.button("I want you to suck my dick tonight"):
        add_narrator("My eyes sparkle with delight..."); st.session_state.turn_state="WALLET_CHECK"; st.rerun()
    if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()


# ==========================================
#       PART 7: BRONZE PRIZES
# ==========================================

if st.session_state.turn_state == "PRIZE_BEND_OVER":
    add_chat("assistant", "This is where you get to bend over for me. Sounds fun huh?")
    if st.button("No."):
        st.empty()
        add_chat("assistant", "Just kidding. For just a few seconds, ill bend over right in front of you whenever you say so.")
        simulate_loading(3)
        # Corrected ext
        add_media("bend_over1.jfif")
        
        c1, c2 = st.columns(2)
        if c1.button("Use today"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()
        if c2.button("Save"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

if st.session_state.turn_state == "PRIZE_JACKOFF_PASS":
    add_chat("assistant", "Ohhh, baby… Jackoff Pass. How generous of fate.")
    add_chat("assistant", "That means you get fifteen luxurious minutes of alone time with your right hand. No restrictions. No interruptions from me.")
    simulate_typing(3)
    add_chat("assistant", "But here’s the fun part: I’m not helping. I’m not watching. Just you, your hand, and the memory of how close you were to earning something real tonight.")
    
    if st.button("What could I have won?"):
        st.empty()
        simulate_loading(3)
        # Corrected ext
        add_media("all1.jfif")
        add_chat("assistant", "Clock’s ticking. Don’t waste it thinking about me too hard… or do.")
        if st.button("Finish"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

if st.session_state.turn_state == "PRIZE_FLASH_ME":
    add_chat("assistant", "Oh darling, you really know how to pick 'em. Don't worry though; I won't make you walk around naked. Instead…")
    if st.button("Tell me more"):
        st.empty()
        add_chat("assistant", "You'll be seated somewhere, in the car maybe, and ill lift my shirt over my breasts allowing them to be exposed for you for a quick second.")
        simulate_loading(3)
        # Corrected ext
        add_media("flash2.jfif")
        add_chat("assistant", "Was it a mirage?")
        if st.button("Done"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()

if st.session_state.turn_state == "PRIZE_DICK_RUB":
    add_chat("assistant", "You want me to provide a sensual cock tease without actually touching that throbbing piece of heaven.")
    simulate_loading(3)
    # Corrected ext
    add_media("rub1.jfif")
    if st.button("Use"): st.session_state.turn_state="WALLET_CHECK"; st.rerun()
