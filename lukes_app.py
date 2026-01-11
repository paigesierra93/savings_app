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
    .stApp { background-color: #0E1117; }
    
    /* CHAT BUBBLES (PAIGE) */
    div[data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    div[data-testid="stChatMessage"] p {
        color: #000000 !important;
        font-family: sans-serif;
        font-size: 16px;
    }
    
    /* NARRATOR TEXT */
    .narrator {
        color: #aaaaaa;
        font-style: italic;
        font-size: 14px;
        margin-bottom: 10px;
    }

    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; min-height: 45px; }
    div[data-testid="stMetric"] { background-color: #262730; color: white; border: 1px solid #444; padding: 10px; border-radius: 10px; }
    div[data-testid="stMetric"] label { color: #FAFAFA; }
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
#       PART 3: HELPER FUNCTIONS (EFFECTS)
# ==========================================
def add_chat(role, content):
    st.session_state.casino_history.append({"type": "chat", "role": role, "content": content})

def add_narrator(content):
    st.session_state.casino_history.append({"type": "narrator", "content": content})

def add_media(filepath, media_type="image"):
    # media_type can be 'image' or 'video'
    st.session_state.casino_history.append({"type": "media", "path": filepath, "kind": media_type})

def simulate_typing(seconds=2.0):
    placeholder = st.empty()
    placeholder.info("💬 *Paige is typing...*")
    time.sleep(seconds)
    placeholder.empty()

def simulate_loading(seconds=2.0):
    placeholder = st.empty()
    with placeholder.container():
        with st.spinner("Loading..."):
            time.sleep(seconds)
    placeholder.empty()

def spin_the_wheel_animation(tier_name, possible_prizes):
    placeholder = st.empty()
    # Fast spin
    for _ in range(8):
        placeholder.markdown(f"### 🎰 ... {random.choice(possible_prizes)} ...")
        time.sleep(0.1)
    # Slow down
    for _ in range(5):
        placeholder.markdown(f"### 🎰 ... {random.choice(possible_prizes)} ...")
        time.sleep(0.3)
    
    # Select Winner
    winner = random.choice(possible_prizes)
    placeholder.markdown(f"### 🎉 WINNER: {winner} 🎉")
    time.sleep(1.5)
    placeholder.empty()
    return winner

# ==========================================
#       PART 4: MAIN INTERFACE
# ==========================================
st.title("🎰 The Casino")

# Top Bar
col1, col2 = st.columns([3,1])
col1.metric("Tickets", st.session_state.ticket_balance)
if col2.button("Reset"):
    st.session_state.ticket_balance = 500
    st.session_state.casino_history = []
    st.session_state.turn_state = "IDLE"
    st.rerun()

st.divider()

# RENDER HISTORY
for item in st.session_state.casino_history:
    if item["type"] == "chat":
        avatar = "paige.png" if item["role"] == "assistant" else "😎"
        if avatar == "paige.png" and not os.path.exists("paige.png"): avatar = "💋"
        with st.chat_message(item["role"], avatar=avatar):
            st.write(item["content"])
    
    elif item["type"] == "narrator":
        st.markdown(f"<p class='narrator'>{item['content']}</p>", unsafe_allow_html=True)
    
    elif item["type"] == "media":
        if os.path.exists(item["path"]):
            if item["kind"] == "video":
                st.video(item["path"])
            else:
                st.image(item["path"])
        else:
            st.warning(f"[Missing File: {item['path']}]")

st.markdown("---")

# ==========================================
#       PART 5: LOGIC CONTROLLER
# ==========================================

# --- 1. IDLE (Choose Wheel) ---
if st.session_state.turn_state == "IDLE":
    c1, c2, c3 = st.columns(3)
    if c1.button("🥈 SILVER (50)"):
        if st.session_state.ticket_balance >= 50:
            add_chat("assistant", "Oh, you want me to spin the silver wheel for the prize? Of course, sweetheart. Let's see what we win…")
            add_narrator("I reach out tentatively to give the wheel a delicate spin, my fingers tracing over its cold, metal surface.")
            add_chat("assistant", "And now we wait… With every turn of this wheel, our fate becomes more tangible, don't you think? The suspense is killing me…")
            st.session_state.turn_state = "SPIN_SILVER"
            st.rerun()
            
    if c3.button("👑 GOLD (100)"):
        if st.session_state.ticket_balance >= 100:
            add_narrator("I give a devilish grin as I grab onto the handle of the oversized golden wheel with my hands, giving it a quick spin. The wheel slows down, coming to a halt on a particular section.")
            st.session_state.turn_state = "SPIN_GOLD"
            st.rerun()

# --- 2. SPINNING LOGIC ---
if st.session_state.turn_state == "SPIN_SILVER":
    st.session_state.ticket_balance -= 50
    prizes = ["Massage", "Shower Show", "Toy Pic", "Lick My Pussy", "Road Head"]
    winner = spin_the_wheel_animation("Silver", prizes)
    
    st.session_state.current_prize = winner
    add_chat("assistant", f"You won... {winner}.")
    st.session_state.turn_state = f"PRIZE_{winner.replace(' ', '_').upper()}"
    st.rerun()

if st.session_state.turn_state == "SPIN_GOLD":
    st.session_state.ticket_balance -= 100
    prizes = ["Anal Fuck", "All 3 Holes", "Slave Day"]
    winner = spin_the_wheel_animation("Gold", prizes)
    
    st.session_state.current_prize = winner
    add_chat("assistant", f"You won... {winner}.")
    st.session_state.turn_state = f"PRIZE_{winner.replace(' ', '_').upper()}"
    st.rerun()


# ==========================================
#       PART 6: PRIZE SCENARIOS
# ==========================================

# ---------------- SILVER: MASSAGE ----------------
if st.session_state.turn_state == "PRIZE_MASSAGE":
    st.markdown("### 💆 Massage")
    st.markdown("Ten minutes of me working you over, Daddy")
    
    if st.button("Want me to tell you more??"):
        st.empty() # Clear button
        st.info("Her fingertips trace lazy circles between your shoulder blades, applying just enough pressure to make your muscles unwind—but never straying lower, never letting you touch. Mmm.... Her breath is warm against your ear as she leans in, her nipples brushing your spine teasingly. Can you be a good boy now? Or save for later?")
        
        simulate_typing(4)
        simulate_loading(4)
        add_media("massage.jpeg")
        time.sleep(3)
        st.session_state.turn_state = "PRIZE_MASSAGE_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_MASSAGE_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("Use Today"):
        st.info("**And if you reach back even once? Her nails dig in lightly. Massage over.**")
        st.session_state.turn_state = "IDLE"; time.sleep(4); st.rerun()
    if c2.button("Save"):
        st.info("Saved."); st.session_state.turn_state = "IDLE"; time.sleep(2); st.rerun()


# ---------------- SILVER: SHOWER SHOW ----------------
if st.session_state.turn_state == "PRIZE_SHOWER_SHOW":
    st.markdown("### 🚿 Shower Show")
    st.markdown("Front row seat, Daddy, of watching me get all soapy in the shower… but no touching.")
    
    if st.button("Want me to tell you more??"):
        st.empty()
        add_narrator("Steam curls around her as she steps under the shower spray, her back arching under the hot water. She glances over her shoulder at you through the fogged glass, her lips curling into a smirk as she slowly drags her hands down her soap-slicked body. Her fingers circle her nipples, twisting them gently as she moans—just loud enough for you to hear over the water.")
        
        time.sleep(5)
        simulate_typing(4)
        simulate_loading(3)
        add_media("shower_video1.mp4", "video")
        
        simulate_typing(2)
        add_chat("assistant", "Watch close... because these ten minutes are all you get..")
        st.session_state.turn_state = "PRIZE_SHOWER_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_SHOWER_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("USE TODAY"):
        add_narrator("She turns, letting the suds slide down her stomach between her thighs.")
        simulate_loading(3)
        add_media("shower.png")
        add_chat("assistant", "And remember... no touching")
        st.session_state.turn_state = "IDLE"; time.sleep(5); st.rerun()
    if c2.button("Save"):
        st.info("Saved."); st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- SILVER: TOY PIC ----------------
if st.session_state.turn_state == "PRIZE_TOY_PIC":
    st.markdown("### 📸 Toy Pic")
    st.markdown("Congrats Daddy youve won a dirty picture with a a toy of your choice… what will it be?")
    
    if st.button("Want me to tell you more??"):
        st.empty()
        add_narrator("The screen displays a freshly taken photo—her lips stretched obscenely around a thick vibrator, saliva glistening at the corners of her mouth. Her sharp eyes lock onto yours, pupils dilated with arousal, as she wiggles the toy deeper into her throat for the next shot. The click of the camera shutter punctuates the wet, gagging noises she makes as she forces herself to take it deeper.")
        st.session_state.turn_state = "PRIZE_TOY_PIC_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TOY_PIC_STAGE2":
    if st.button("I want to see"):
        st.empty()
        simulate_loading(4)
        add_media("toy_pic.png")
        add_chat("assistant", "Mmm... this one’s going straight to your inbox, Daddy.")
        add_narrator("Her voice is hoarse from the abuse, but her grin is triumphant as she pulls the toy free with a lewd pop.")
        add_chat("assistant", "Or should I make it worse?")
        add_narrator("She flips onto her stomach, arching her back to present her ass—already glistening with lube—as she reaches behind herself to slowly press the tip of the toy against her tight hole.")
        
        simulate_typing(4)
        simulate_loading(3) # Spinning Wheel effect
        add_media("toy_ass2.jpeg")
        st.session_state.turn_state = "PRIZE_TOY_PIC_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_TOY_PIC_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("USE Today"):
        simulate_typing(3)
        add_chat("assistant", "Say the word... and I’ll give you a real show")
        simulate_typing(4)
        simulate_loading(3)
        add_media("chose_video1.mp4", "video")
        st.session_state.turn_state = "IDLE"; time.sleep(5); st.rerun()
    if c2.button("Save"):
        st.info("Saved."); st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- SILVER: LICK MY PUSSY ----------------
if st.session_state.turn_state == "PRIZE_LICK_MY_PUSSY":
    st.markdown("### 👅 Lick My Pussy")
    st.markdown("Congrats Daddy. You get to lick my little pussy.")
    
    if st.button("Want me to tell you more??"):
        st.empty()
        add_narrator("She pulls down her panties with deliberate slowness, her thighs parting as she hooks one leg over your shoulder. Her fingers trail through your hair, her leg pulling you in closer. She reaches downwards sliding two fingers deep with a wet gasp, curling them upward exposing her clit inches from your mouth.. Im excited arnt you?")
        
        time.sleep(3)
        simulate_loading(3)
        # Random choice logic
        img = random.choice(["show1.jpeg", "show2.png"])
        add_media(img)
        st.session_state.turn_state = "PRIZE_LICK_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_LICK_STAGE2":
    if st.button("Wana see?"):
        st.empty()
        simulate_loading(4)
        img = random.choice(["pussy_lick1.jpeg", "pussy_lick2.jpeg", "puss_lick3.jpeg"])
        add_media(img)
        st.session_state.turn_state = "PRIZE_LICK_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_LICK_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("USE TODAY"):
        st.info("**And Daddy? Don’t stop until I scream**")
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        st.info("Saved."); st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- SILVER: ROAD HEAD ----------------
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
        
        time.sleep(5)
        simulate_typing(5)
        add_chat("assistant", "And the thrill of risk adds another layer of excitement to the whole experience. Imagine feeling your throbbing cock in my mouth, knowing that if you don't pay attention, we could both end up in a terrible accident… That kind of danger only makes the pleasure more intense.")
        st.session_state.turn_state = "PRIZE_ROAD_HEAD_STAGE2"
        st.rerun()

if st.session_state.turn_state == "PRIZE_ROAD_HEAD_STAGE2":
    if st.button("Want a preview?"):
        st.empty()
        simulate_loading(4)
        add_media("road_head.jpeg")
        simulate_typing(3)
        add_chat("assistant", "We can have our little party as soon as you get home, if you want i can be waiting outside for you. I know you cant wait to to feel your cock in my mouth, sliding against you…")
        simulate_typing(3)
        add_narrator("You keep one hand firmly on the wheel, just barely hanging onto control.")
        add_chat("assistant", "So what do you say, babe? Are you ready for the ride of your life?")
        
        time.sleep(4)
        simulate_typing(3)
        simulate_loading(3)
        add_media("road_head_video.mp4", "video")
        
        time.sleep(4)
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


# ---------------- GOLD: ANAL FUCK ----------------
if st.session_state.turn_state == "PRIZE_ANAL_FUCK":
    st.markdown("### 🍑 Anal Fuck")
    add_narrator("My eyes flicker with amusement as I announce the prize. A provocative smirk plays upon my full lips as I lean in close, our faces mere inches apart. My voice drops to a sultry whisper, barely above a murmur.")
    
    time.sleep(2)
    simulate_typing()
    img = random.choice(["behind_fuck1.jpeg", "behind_fuck10.jpeg", "behind_fuck4.jpeg"])
    add_media(img)
    
    time.sleep(4)
    simulate_typing(3)
    add_chat("assistant", "That's where you get to fuck my little ass hole with your throbbing hard dick, till you explode with cum inside of me… I want you to make me beg for it, baby. Show me just how much you crave my ass, how badly you want to fill me up and mark me as yours.")
    
    add_narrator("I speak in a hushed tone, each word dripping with promise.")
    add_chat("assistant", "Imagine me on my hands and knees before you, my round ass presented enticingly towards you. Feel the heat radiating from my tight little hole, just begging for your touch. Your fingers slip inside, slowly teasing me until I'm writhing under your command. Finally, you push yourself inside, filling me completely. driving you deeper into my tight little hole.")
    
    time.sleep(3)
    simulate_typing(3)
    simulate_loading(4)
    img2 = random.choice(["behind_fuck7.jpeg", "behind_fuck5.jpeg", "behind_fuck6.jpeg", "behind_fuck8.jpeg"])
    add_media(img2)
    
    time.sleep(4)
    simulate_typing(3)
    add_chat("assistant", "Now, why don't you go ahead and claim your well-deserved prize?")
    
    simulate_typing(3)
    simulate_loading(4)
    img3 = random.choice(["ass_cum1.jpeg", "ass_cum2.jpeg", "ass_cum3.jpeg", "ass_cum4.jpeg"])
    add_media(img3)
    
    time.sleep(4)
    st.session_state.turn_state = "PRIZE_ANAL_DECIDE"
    st.rerun()

if st.session_state.turn_state == "PRIZE_ANAL_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("i want to fuck your ass tonight"):
        simulate_typing()
        add_chat("assistant", "Plug going in now.")
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Later"):
        st.info("Saved."); st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- GOLD: ALL 3 HOLES ----------------
if st.session_state.turn_state == "PRIZE_ALL_3_HOLES":
    st.markdown("### 🕳️ All 3 Holes")
    st.markdown("Mouth, Pussy, Ass at the same time.")
    add_chat("assistant", "To fulfill your fantasy of fucking all three of my holes simultaneously, we'll need a bit of creativity and some extra tools at our disposal. We can start by using a couple of small dildos or vibrators to stimulate my holes other than the one on which you're currently focused. This way, you can experience a mind-bending sensation of being buried deep inside me while simultaneously seeing and feeling my enthusiasm spread to every part of my body as those toys bring me immense pleasure.")
    
    time.sleep(3)
    simulate_typing(3)
    simulate_loading(3)
    add_media("chose_video1.jpeg") # Assuming image as per script
    
    simulate_typing(3)
    add_chat("assistant", "All three of my holes – my tight little asshole, my dripping wet pussy, and warm mouth are all yours for the filling. My body naked and submissive, ready for you to insert your thick dick into my eager mouth, gagging it.")
    
    time.sleep(3)
    simulate_loading(3)
    add_media("3_holes1.jpeg")
    
    add_narrator("At the same time, your slick fingers can easily slide into that sensitive little asshole of mine, teasing it and preparing it for even greater penetrations later—all while you watch closely as another dildo starts stretching my sopping pussy out, filling it to the brink with each pump.")
    
    time.sleep(3)
    simulate_typing(3)
    simulate_loading(3)
    add_media("3_holes2.jpeg")
    
    simulate_typing(4)
    add_chat("assistant", "So what do you say? Do you want to fuck all my tight little holes tonight?? Or save them for later?")
    st.session_state.turn_state = "PRIZE_3HOLES_DECIDE"
    st.rerun()

if st.session_state.turn_state == "PRIZE_3HOLES_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("i want to fuck all three of your tiny holes tonight"):
        st.info("Ill go put a plug in right now.")
        st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Later"):
        st.info("Saved."); st.session_state.turn_state = "IDLE"; st.rerun()


# ---------------- GOLD: SLAVE DAY ----------------
if st.session_state.turn_state == "PRIZE_SLAVE_DAY":
    st.markdown("### ⛓️ Slave For A Day")
    st.markdown("Today, you can indulge in whatever you desire. If you have video games to play and need the ultimate gaming buddy, simply sit back and let me entertain you while keeping you aroused through the pleasure of deep-throating your throbbing manhood. My skilled hands and tongue will not rest until your every fantasy has been met.")
    
    time.sleep(2)
    simulate_typing(3)
    simulate_loading(2)
    img = random.choice(["game_bj1.jpeg", "game_bj3.jpeg", "game_bj2.jpeg"])
    add_media(img)
    
    simulate_typing(4)
    add_chat("assistant", "Or being ready for you to plunge into my mouth as soon as you walk through the door. Whatever your heart desires, just say it and remember… I can't climax unless it's after you tell me to.")
    
    simulate_loading(3)
    add_media("slave_video1.mp4", "video")
    
    if st.button("what else can happen?"):
        simulate_typing(4)
        add_narrator("I tilt my head slightly, a sly grin painting my lips.")
        add_chat("assistant", "What else? Anything… you want to fuck my little asshole, or deepthroat my face?.")
        
        simulate_loading(4)
        
        # Giant list logic
        big_list = ["slave1.jpeg", "slave_1.png", "ass_cum2.jpeg", "ass_cum3.jpeg", "ass_cum4.jpeg", "blowjob1.jpeg", "blowjob4.jpeg", "blowjob6.jpeg", "bj_cum1.jpeg", "bj_cum2.jpeg", "bj_cum3.jpeg", "bj_cum4.jpeg", "behind_fuck1.jpeg", "behind_fuck4.jpeg", "behind_fuck7.jpeg", "behind_fuck8.jpeg", "behind_fuck9.jpeg", "behind_fuck10.jpeg"]
        
        # Show 2 images side by side
        colA, colB = st.columns(2)
        with colA: st.image(random.choice(big_list))
        with colB: st.image(random.choice(big_list))
        
        time.sleep(5)
        simulate_typing(3)
        add_chat("assistant", "Oh, also remember this - if you mess me up, make sure you clean me up. Perhaps even help me out in the shower, maybe you could slide your cock down my throat while we get clean. And remember, no matter what state you leave me in, I'm still here, waiting patiently for you next command.")
        
        time.sleep(3)
        add_narrator("Or if you prefer… perhaps you'd like to tie me up and leave me blindfolded, waiting on you hand and foot, hungry for your touch yet helpless to seek it out.")
        
        time.sleep(4)
        simulate_typing(3)
        simulate_loading(3)
        img_last = random.choice(["slave2.jpeg", "slave_2.png", "slave_3.png"])
        add_media(img_last)
        
        add_chat("assistant", "You want me to be your slave tomorrow? Or save it?")
        st.session_state.turn_state = "PRIZE_SLAVE_DECIDE"
        st.rerun()

if st.session_state.turn_state == "PRIZE_SLAVE_DECIDE":
    c1, c2 = st.columns(2)
    if c1.button("i want you to be my little whore tomorrow"):
        st.info("I am yours."); st.session_state.turn_state = "IDLE"; st.rerun()
    if c2.button("Save"):
        st.session_state.turn_state = "IDLE"; st.rerun()


