import json
import os
import random
import time
import streamlit as st

# ==========================================
#       PART 1: SETUP & STYLING
# ==========================================
st.set_page_config(page_title="Casino Chat", page_icon="🎰", layout="wide")

st.markdown("""
    <style>
    /* 1. LIGHT THEME BACKGROUND */
    .stApp { 
        background-color: #F2F4F8; 
        color: #000000;
    }
    
    /* 2. CHAT CONTAINER */
    .chat-container {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #E0E0E0;
    }

    /* 3. CHAT BUBBLES */
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
    
    /* NARRATOR TEXT */
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
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold; 
        min-height: 45px;
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #000000;
    }
    .stButton button:hover {
        background-color: #F0F0F0;
        border-color: #FF4B4B;
        color: #FF4B4B;
    }

    /* METRICS */
    div[data-testid="stMetric"] { 
        background-color: #FFFFFF; 
        color: #000000; 
        border: 1px solid #CCCCCC; 
        padding: 10px; 
        border-radius: 10px; 
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label { color: #555555; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #000000; }
    
    </style>
    """, unsafe_allow_html=True)

# ==========================================
#       PART 2: DATA & STATE
# ==========================================
if "ticket_balance" not in st.session_state: st.session_state.ticket_balance = 500
if "casino_history" not in st.session_state: st.session_state.casino_history = []
if "turn_state" not in st.session_state: st.session_state.turn_state = "IDLE"
if "current_prize" not in st.session_state: st.session_state.current_prize = None

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
    
    # 1. Medium Spin
    for _ in range(5):
        placeholder.markdown(f"### 🎰 {random.choice(possible_prizes)}")
        time.sleep(0.3)
        
    # 2. Slow Down
    for _ in range(5):
        placeholder.markdown(f"### 🎰 ... {random.choice(possible_prizes)} ...")
        time.sleep(0.6)

    # 3. Final Suspense
    for _ in range(3):
        placeholder.markdown(f"### 🎰 ...... {random.choice(possible_prizes)} ......")
        time.sleep(1.0)

    # Select Winner
    winner = random.choice(possible_prizes)
    placeholder.markdown(f"### 🎉 WINNER: {winner} 🎉")
    time.sleep(3.0) 
    placeholder.empty()
    return winner

# ==========================================
#       PART 4: MAIN INTERFACE
# ==========================================
st.title("🎰 The Casino")

col1, col2 = st.columns([3,1])
col1.metric("Tickets", st.session_state.ticket_balance)
if col2.button("Reset System"):
    st.session_state.ticket_balance = 500
    st.session_state.casino_history = []
    st.session_state.turn_state = "IDLE"
    st.rerun()

st.divider()

# --- THE CHAT CONTAINER ---
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.casino_history:
        st.caption("Chat started...")

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
                    if item["kind"] == "video":
                        st.video(item["path"])
                    else:
                        st.image(item["path"], width=350)
                else:
                    st.error(f"⚠️ Missing File: {item['path']}")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
#       PART 5: LOGIC CONTROLLER
# ==========================================

# --- 1. IDLE (Choose Wheel) ---
if st.session_state.turn_state == "IDLE":
    c1, c2, c3 = st.columns(3)
    if c1.button("🥈 SILVER (50)"):
        # Check tickets (Assuming 50 for consistency, logic says 501-600 tier but cost is 50)
        if st.session_state.ticket_balance >= 50:
            st.session_state.turn_state = "PRE_SPIN_SILVER"
            st.rerun()
        else:
            st.error("Not enough tickets!")
            
    if c3.button("👑 GOLD (100)"):
        if st.session_state.ticket_balance >= 100:
            add_narrator("I give a devilish grin as I grab onto the handle of the oversized golden wheel.")
            st.session_state.turn_state = "SPIN_GOLD"
            st.rerun()

# --- 2. PRE-SPIN SILVER (Intro Sequence) ---
if st.session_state.turn_state == "PRE_SPIN_SILVER":
    add_chat("assistant", "Silver Tier access. No Bronze pity party tonight, congrats. But don’t get cocky, you still too broke to make me call you Daddy and drop to my knees without being asked.")
    
    simulate_typing(3)
    add_chat("assistant", "So here’s the deal, good boy. You’ve earned one spin on the Silver Wheel. One chance to get something that actually involves my mouth, my hands… or maybe even my pussy if the stars align.")
    
    simulate_typing(3)
    add_chat("assistant", "But first…")
    add_narrator("I tap the screen once, twice—Silver Wheel loading, shimmering silver and gold.")
    add_chat("assistant", "Spin it, baby. Show me what your silver spin check bought you tonight.")
    
    st.session_state.turn_state = "READY_TO_SPIN_SILVER"
    st.rerun()

if st.session_state.turn_state == "READY_TO_SPIN_SILVER":
    c1, c2 = st.columns(2)
    if c1.button("Spin?"):
        st.session_state.turn_state = "SPIN_SILVER"
        st.rerun()
    if c2.button("Save"):
        add_chat("assistant", "Suit yourself. Saving tickets.")
        st.session_state.turn_state = "IDLE"; st.rerun()

# --- 3. SPINNING LOGIC ---
if st.session_state.turn_state == "SPIN_SILVER":
    st.session_state.ticket_balance -= 50
    add_narrator("I tap the screen with a flourish, the Silver Wheel spinning to life in a swirl of metallic shimmer and teasing icons. The clicks slow… slower… until it lands with a satisfying chime.")
    
    prizes = ["Massage", "Shower Show", "Toy Pic", "Lick My Pussy", "Nude Pic", "Tongue Tease", "No Panties", "Road Head"]
    winner = spin_the_wheel_animation("Silver", prizes)
    
    st.session_state.current_prize = winner
    add_chat("assistant", f"🥈 WINNER: {winner}")
    st.session_state.turn_state = f"PRIZE_{winner.replace(' ', '_').upper()}"
    st.rerun()

if st.session_state.turn_state == "SPIN_GOLD":
    st.session_state.ticket_balance -= 100
    prizes = ["Anal Fuck", "All 3 Holes", "Slave Day"]
    winner = spin_the_wheel_animation("Gold", prizes)
    st.session_state.current_prize = winner
    add_chat("assistant", f"👑 WINNER: {winner}")
    st.session_state.turn_state = f"PRIZE_{winner.replace(' ', '_').upper()}"
    st.rerun()


# ==========================================
#       PART 6: SILVER PRIZE SCENARIOS
# ==========================================

# ---------------- 1. MASSAGE ----------------
if st.session_state.turn_state == "PRIZE_MASSAGE":
    add_chat("assistant", "Looks like you’ve won a massage…")
    
    if st.button("Shirtless?"):
        st.empty()
        simulate_typing(2)
        add_chat("assistant", "Mmm… you know I can’t make any promises. But the rules are simple: ten minutes, oil, and… well, let’s just say I’ll tease you until you’re begging for more.")
        add_chat("assistant", "Official rules state no full release during the massage itself. However, I fully intend to tease you until you're squirming for more.")
        st.session_state.turn_state = "PRIZE_MASSAGE_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_MASSAGE_STAGE2":
    if st.button("Tell me more?"):
        st.empty()
        simulate_typing(3)
        add_chat("assistant", "I know how you like it, start with your shoulders, then work down your spine… firm circles on your lower back, I won't stop until the timer goes off. My hands will work out every knot while my body brushes against yours in all the right places.")
        add_chat("assistant", "Maybe a few 'accidental' grazes over sensitive areas... you'll be aching for me, baby. But you'll just have to wait patiently for your next prize to really let go. I want you desperate for me. And trust me—")
        st.session_state.turn_state = "PRIZE_MASSAGE_STAGE3"
        st.rerun()

if st.session_state.turn_state == "PRIZE_MASSAGE_STAGE3":
    if st.button("Show me"):
        st.empty()
        simulate_loading(3)
        add_media("massage.jpeg")
        simulate_typing(2)
        add_chat("assistant", "I'll work out every knot.")
        add_narrator("I shift in my seat, pressing my thighs together.")
        simulate_typing(2)
        add_chat("assistant", "Your prize is waiting, good boy. Don't keep me waiting.")
        st.session_state.turn_state = "PRIZE_MASSAGE_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_MASSAGE_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("Use Today"):
        st.info("Timer starts now."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- 2. SHOWER SHOW ----------------
if st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    add_narrator("My eyes flick up from my screen pupils dilating just a fraction. The corner of my mouth lifts in a slow, wicked smile.")
    simulate_typing(2)
    add_chat("assistant", "Ohhh… look at that. Oh, honey—you know this one's going to be cheeky.")
    simulate_typing(3)
    add_chat("assistant", "Rules are simple, baby: You sit on the edge of the bathtub. You watch. You dry me off when I’m done.")
    
    simulate_typing(3)
    add_chat("assistant", "I’m already getting wet just thinking about you watching me. But here’s the twist—you can’t touch until the water’s off. Not a single finger.")
    
    simulate_loading(3)
    add_media("shower.jpeg")
    
    simulate_typing(3)
    add_chat("assistant", "Hot water steaming up the glass, soap dripping down my curves… I’ll face you so you can see everything, but you can’t touch. Not yet.")
    add_narrator("Your free hand clenches into a fist, knuckles whitening.")
    
    time.sleep(3)
    simulate_loading(3)
    add_media("shower_video1.mp4", "video")
    
    simulate_typing(3)
    add_chat("assistant", "I’m going to tease you until you’re begging to get in here with me.")
    add_narrator("Dripping with mischief.")
    add_chat("assistant", "Maybe I'll let you dry me off with your tongue.")
    
    st.session_state.turn_state = "PRIZE_SHOWER_DECIDE"
    st.rerun()

if st.session_state.turn_state == "PRIZE_SHOWER_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("Use tonight"):
        st.info("Get in the bathroom."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save for later"):
        st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- 3. TOY PIC ----------------
if st.session_state.turn_state == "PRIZE_TOY_PIC":
    add_narrator("My eyes flick up from my screen pupils dilating just a fraction.")
    simulate_typing(2)
    add_chat("assistant", "Ohhh… look at that. Looks like you’ve leveled up from Bronze duty.")
    add_narrator("I’m already getting wet just thinking about putting on a show for you.")
    
    simulate_typing(3)
    add_chat("assistant", "Rules are simple, baby. You pick the toy. You pick the spot. I take the photo.")
    
    simulate_loading(3)
    add_media("toy_pic.jpeg")
    
    simulate_typing(3)
    add_chat("assistant", "I know what you like, maybe the end of your screwdriver, deep in my pussy, or the vibrating bullet tucked in my tight ass. Tell me exactly which hole to fill and where I should be when I snap it. Make it dirty. And trust me—")
    st.session_state.turn_state = "PRIZE_TOY_PIC_STAGE2"
    st.rerun()

if st.session_state.turn_state == "PRIZE_TOY_PIC_STAGE2":
    if st.button("Show me"):
        st.empty()
        simulate_loading(4)
        add_media("toy_ass1.jpeg")
        simulate_typing(3)
        add_chat("assistant", "I’ll make sure you can see how deep it goes and how dripping wet I am.")
        add_narrator("You imagine me reaching into the drawer, my fingers brushing over the silicone.")
        st.session_state.turn_state = "PRIZE_TOY_PIC_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TOY_PIC_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("Claim now"):
        st.info("Check your inbox."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save for later"):
        st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- 4. LICK PUSSY ----------------
if st.session_state.turn_state == "PRIZE_LICK_MY_PUSSY":
    add_narrator("The corner of my mouth lifts in a slow, wicked smile.")
    simulate_typing(2)
    add_chat("assistant", "Tonight you get to worship me properly.")
    add_narrator("I’m already getting wet just thinking about it.")
    simulate_typing(3)
    add_chat("assistant", "Rules are simple, baby. You kneel. You use only your mouth. You lick me exactly how I like it.")
    
    if st.button("How do you like it?"):
        st.empty()
        simulate_typing(3)
        add_chat("assistant", "You know how I like it, slow circles around my clit first, then long, flicks up my slit… tease the entrance, push your tongue inside. You don’t stop until I cum. And trust me—")
        st.session_state.turn_state = "PRIZE_LICK_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_LICK_STAGE2":
    if st.button("Show me"):
        st.empty()
        simulate_loading(4)
        img = random.choice(["Pussy_lick2.jpeg", "pussy_lick1.jpeg", "pussy_lick3.jpeg"])
        add_media(img)
        simulate_typing(3)
        add_chat("assistant", "I'll ride your tongue until my thighs shake and I soak you.")
        add_narrator("You imagine One finger hooking under the waistband. I tug it aside, showing you how glistening I am already.")
        add_chat("assistant", "Or I might just change my mind and make you watch me cum on my fingers instead.")
        st.session_state.turn_state = "PRIZE_LICK_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_LICK_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("Claim today"):
        st.info("Get on your knees."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save for later"):
        st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- 5. NUDE PIC ----------------
if st.session_state.turn_state == "PRIZE_NUDE_PIC":
    add_narrator("My eyes flick up from my screen pupils dilating just a fraction.")
    simulate_typing(2)
    add_chat("assistant", "Ohhh… look at that.")
    add_narrator("I’m already getting wet just thinking about exposing myself for you.")
    simulate_typing(3)
    add_chat("assistant", "Rules are simple, baby. You pick the pose. You pick the part. I send the proof.")
    
    simulate_loading(3)
    add_media("nude_pic1.jpeg")
    
    simulate_typing(3)
    add_chat("assistant", "Do you want my ass in the air? Maybe a close-up of my tits? Tell me exactly what you want to see on your screen right now. And trust me—")
    simulate_typing(3)
    add_chat("assistant", "I’ll make sure the lighting is perfect so you can see every single curve.")
    add_narrator("You imagine me untying my robe, letting it fall open to reveal everything.")
    
    c1, c2 = st.columns(2)
    if c1.button("Claim now"):
        st.info("Sent."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- 6. TONGUE TEASE ----------------
if st.session_state.turn_state == "PRIZE_TONGUE_TEASE":
    simulate_typing(2)
    add_chat("assistant", "Oh this is a good one, it's pretty self explanatory but would you like me to explain the rules?")
    
    if st.button("Tell me the rules"):
        st.empty()
        simulate_typing(3)
        add_chat("assistant", "I’ll be on my knees at the edge of the mattress, facing you as you stand your dick in your hand before me. My lips already wet and parted.")
        simulate_loading(3)
        add_media("tease1.jpeg")
        simulate_typing(2)
        add_chat("assistant", "Stroke it slow for me but won't cum until I say. This prize is all about my tongue… teasing you until you’re dripping.")
        add_narrator("I lean forward just enough that you feel the heat of my breath ghosting over the head. No contact yet. Just warm, wet exhales—slow, deliberate—making your tip twitch with every puff of air.")
        st.session_state.turn_state = "PRIZE_TEASE_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TEASE_STAGE2":
    if st.button("And then what?"):
        st.empty()
        simulate_typing(3)
        add_narrator("My tongue slips out and hovers an inch away. I let a single thick string of spit drip slowly from the tip of my tongue onto your shaft. It lands warm and slick, sliding down meeting your hand.")
        
        simulate_typing(4)
        add_narrator("You take a step closer—still no touching with lips just the tip of my tongue barely grazing the head as you slowly stroke it.")
        add_chat("assistant", "Keep stroking. Nice and slow.")
        
        simulate_typing(3)
        add_narrator("I circle the head now—tongue tracing slow, wet spirals around the ridge, never quite giving you the full pressure you crave.")
        time.sleep(2)
        add_narrator("Over and over. Relentless little teases that make your whole length jump and leak more. My hands stay behind my back—obedient to the game. Only my mouth exists for you right now.")
        
        time.sleep(3)
        add_narrator("I open wider, letting my tongue slide over and over your head. Dripping spit your stroking fast now. The tip in my mouth, eyes looking up to you.")
        
        simulate_typing(2)
        add_chat("assistant", "God, you’re so fucking hard… you’re close, aren’t you?")
        
        simulate_loading(3)
        add_media("tease2.jpeg")
        
        add_narrator("I pull back again—cruelly—letting cool air hit the wet trail I left behind. Then I lean in once more, licking your head slowly. My mouth begging for cum. Lips around just the head—sucking hard, tongue swirling wildly inside while my hand finally joins, stroking fast and slick.")
        
        simulate_typing(3)
        add_chat("assistant", "Come for me—right on my tongue—give it all to me—")
        
        add_narrator("You explode—thick, hot ropes hitting my waiting tongue, spilling over my lips, dripping down my chin as I moan around you, milking every pulse with slow, greedy licks until you’re completely spent.")
        
        simulate_loading(3)
        add_media("Jerking1.jpeg")
        
        add_narrator("I pull back slowly, licking my lips clean, eyes glazed and satisfied. Such a filthy, perfect prize…")
        
        st.session_state.turn_state = "PRIZE_TEASE_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TEASE_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("I want a tongue tease today"):
        st.info("Unzip."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save it"):
        st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- 7. NO PANTIES ALL DAY ----------------
if st.session_state.turn_state == "PRIZE_NO_PANTIES":
    add_narrator("My eyes flick up from my screen pupils dilating just a fraction. The corner of my mouth lifts in a slow, wicked smile.")
    simulate_typing(2)
    add_chat("assistant", "Looks like you’ve leveled up from Bronze duty.")
    add_narrator("I’m already getting wet just thinking about the friction against my bare skin.")
    simulate_typing(3)
    add_chat("assistant", "Rules are simple, baby. I wear a dress or skirt. I wear nothing underneath. You get to verify.")
    
    if st.button("Tell me more"):
        st.empty()
        simulate_typing(3)
        add_chat("assistant", "At the grocery store… bending over to get food from the bottom shelf. No one else knows that I’m completely bare. You can check whenever you want, just slide your hand up my thigh. And trust me—")
        simulate_loading(3)
        add_media("exposed2.jpeg")
        st.session_state.turn_state = "PRIZE_NOPANTIES_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_NOPANTIES_STAGE2":
    if st.button("Show me"):
        st.empty()
        simulate_loading(3)
        add_media("exposed1.jpeg")
        simulate_typing(2)
        add_chat("assistant", "I’m going to be dripping wet by the time we get home from just the thought of you catching me.")
        add_narrator("You imagine me lifting my hips slightly, sliding the fabric down and tossing it aside.")
        st.session_state.turn_state = "PRIZE_NOPANTIES_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_NOPANTIES_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("Claim now"):
        st.info("Done."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save for later"):
        st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- 8. ROAD HEAD ----------------
if st.session_state.turn_state == "PRIZE_ROAD_HEAD":
    st.markdown("### 🚗 Road Head")
    add_narrator("A gleam of excitement sparkles in my eyes…")
    add_chat("assistant", "You've won yourself a little something extra special tonight… 'Road Head'. I can already envision those thick, throbbing inches disappearing down the back of my throat…")
    add_narrator("I pause, taking a moment to let the image settle before continuing.")
    add_chat("assistant", "How about you, sweetheart?")

    if st.button("What will you do to me??"):
        st.empty()
        add_narrator("My heart races as I imagine all the possibilities that await us, a wide grin spreading across my face.")
        add_chat("assistant", "Baby, there's so much more to it than just putting your dick in my mouth while driving… It's an art form, a dance of pleasure where every move counts. The way I tease with my tongue, can send you over the edge…..")
        
        time.sleep(4)
        simulate_typing(4)
        add_chat("assistant", "And the thrill of risk adds another layer of excitement to the whole experience. Imagine feeling your throbbing cock in my mouth, knowing that if you don't pay attention, we could both end up in a terrible accident… That kind of danger only makes the pleasure more intense.")
        st.session_state.turn_state = "PRIZE_ROAD_HEAD_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_ROAD_HEAD_STAGE2":
    if st.button("Want a preview?"):
        st.empty()
        simulate_loading(3)
        add_media("road_head.jpeg")
        simulate_typing(3)
        add_chat("assistant", "We can have our little party as soon as you get home, if you want i can be waiting outside for you. I know you cant wait to to feel your cock in my mouth, sliding against you…")
        simulate_typing(3)
        add_narrator("You keep one hand firmly on the wheel, just barely hanging onto control.")
        add_chat("assistant", "So what do you say, babe? Are you ready for the ride of your life?")
        
        time.sleep(3)
        simulate_typing(3)
        simulate_loading(3)
        add_media("road_head_video.mp4", "video")
        
        time.sleep(3)
        st.session_state.turn_state = "PRIZE_ROAD_HEAD_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_ROAD_HEAD_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("I want you suck my dick tonightt"):
        simulate_typing(4)
        add_narrator("My eyes sparkle with delight at your eager reply…as i put my phone down to get ready.")
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save for Later"):
        simulate_typing(3)
        add_narrator("My bottom lip pouts our a bit. And i think, well i guess he must be saving it for a special occasion. And there is always the next wheel spin. As i close the chat.")
        st.info("SAVED"); st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- GOLD PRIZES (PLACEHOLDERS TO PREVENT CRASH) ----------------
if st.session_state.turn_state.startswith("PRIZE_") and "SLAVE" not in st.session_state.turn_state and "ANAL" not in st.session_state.turn_state and "HOLES" not in st.session_state.turn_state and st.session_state.turn_state not in ["PRIZE_MASSAGE", "PRIZE_SHOWER_SHOW", "PRIZE_TOY_PIC", "PRIZE_LICK_MY_PUSSY", "PRIZE_ROAD_HEAD", "PRIZE_NUDE_PIC", "PRIZE_TONGUE_TEASE", "PRIZE_NO_PANTIES"]:
    # Catch-all for other Gold prizes not fully scripted yet
    st.info("Gold Prize Script Loading...")
    if st.button("Claim"): st.session_state.turn_state = "IDLE"; st.rerun()

# ---------------- GOLD: SLAVE DAY ----------------
if st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    st.markdown("### ⛓️ Slave For A Day")
    # ... (Keeping your existing Slave Day Logic Here) ...
    # Re-inserting the previous Slave Day Code for completeness
    if st.button("Tell me more??"):
        st.empty()
        add_chat("assistant", "If you have video games to play and need the ultimate gaming buddy, simply sit back and let me entertain you while keeping you aroused through the pleasure of deep-throating your throbbing manhood.")
        simulate_loading(2)
        add_media("game_bj1.jpeg") 
        st.session_state.turn_state = "IDLE"; st.rerun()
