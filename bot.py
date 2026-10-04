import asyncio
from fbchat_muqit import Client, Message, ThreadType

# --- CONFIGURATION ---
ADMIN_IDS = ["100000000000000"]  # Yahan apna Facebook UID daalein
BOT_NICKNAME = "Group Manager Bot"

# State storage (Render restart pe reset ho jayega)
GROUP_LOCK = {}
NICKNAME_LOCK = {}
PHOTO_LOCK = {}

# ✅ FIX: Client ko seedha initialize karein, startSession() nahi
client = Client(cookies_file_path="cookies.json")

# ✅ FIX: @client.event decorator use karein, subclassing nahi
@client.event
async def on_message(message: Message):
    # Bot apne messages pe reply na kare
    if message.sender_id == client.uid:
        return

    text = (message.text or "").strip()
    if not text.startswith("/"):
        return

    # Sirf group chat mein commands
    if message.thread_type != ThreadType.GROUP:
        return

    is_admin = str(message.sender_id) in ADMIN_IDS
    tid_str = str(message.thread_id)

    # --- /help ---
    if text == "/help":
        help_text = (
            "📜 **Available Commands:**\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔹 /tid - Group ID\n"
            "🔹 /uid <mention> - User ID\n"
            "🔹 /botnick <name> - Bot Nickname (Admin)\n"
            "🔹 /photolock on/off - Photo Lock (Admin)\n"
            "🔹 /grouplock on/off - Group Name Lock (Admin)\n"
            "🔹 /nicklock on/off - Nickname Lock (Admin)\n"
            "🔹 /status - Current Lock Status\n"
            "🔹 /help - Yeh menu"
        )
        await client.send_message(help_text, message.thread_id)

    # --- /tid ---
    elif text == "/tid":
        await client.send_message(f"Group ID: {message.thread_id}", message.thread_id)

    # --- /uid ---
    elif text.startswith("/uid"):
        if message.mentions:
            mentioned_id = message.mentions[0].user_id
            await client.send_message(f"User ID: {mentioned_id}", message.thread_id)
        else:
            await client.send_message(f"Aapki ID: {message.sender_id}", message.thread_id)

    # --- /botnick ---
    elif text.startswith("/botnick") and is_admin:
        global BOT_NICKNAME
        new_nick = text.replace("/botnick", "").strip()
        if new_nick:
            BOT_NICKNAME = new_nick
            await client.send_message(f"✅ Bot nickname set: {new_nick}", message.thread_id)
        else:
            await client.send_message("Usage: /botnick <name>", message.thread_id)

    # --- /photolock ---
    elif text.startswith("/photolock") and is_admin:
        action = text.replace("/photolock", "").strip().lower()
        if action == "on":
            PHOTO_LOCK[tid_str] = True
            await client.send_message("🔒 Group Photo Lock: ON", message.thread_id)
        elif action == "off":
            PHOTO_LOCK[tid_str] = False
            await client.send_message("🔓 Group Photo Lock: OFF", message.thread_id)
        else:
            await client.send_message("Usage: /photolock on | /photolock off", message.thread_id)

    # --- /grouplock ---
    elif text.startswith("/grouplock") and is_admin:
        action = text.replace("/grouplock", "").strip().lower()
        if action == "on":
            GROUP_LOCK[tid_str] = True
            await client.send_message("🔒 Group Name Lock: ON", message.thread_id)
        elif action == "off":
            GROUP_LOCK[tid_str] = False
            await client.send_message("🔓 Group Name Lock: OFF", message.thread_id)
        else:
            await client.send_message("Usage: /grouplock on | /grouplock off", message.thread_id)

    # --- /nicklock ---
    elif text.startswith("/nicklock") and is_admin:
        action = text.replace("/nicklock", "").strip().lower()
        if action == "on":
            NICKNAME_LOCK[tid_str] = True
            await client.send_message("🔒 Nickname Lock: ON", message.thread_id)
        elif action == "off":
            NICKNAME_LOCK[tid_str] = False
            await client.send_message("🔓 Nickname Lock: OFF", message.thread_id)
        else:
            await client.send_message("Usage: /nicklock on | /nicklock off", message.thread_id)

    # --- /status ---
    elif text == "/status":
        status_msg = (
            f"📊 **Group Lock Status**\n"
            f"🔒 Photo Lock: {'ON' if PHOTO_LOCK.get(tid_str) else 'OFF'}\n"
            f"🔒 Group Name Lock: {'ON' if GROUP_LOCK.get(tid_str) else 'OFF'}\n"
            f"🔒 Nickname Lock: {'ON' if NICKNAME_LOCK.get(tid_str) else 'OFF'}\n"
            f"🤖 Bot Nickname: {BOT_NICKNAME}"
        )
        await client.send_message(status_msg, message.thread_id)


@client.event
async def on_people_added(added_ids, author_id, thread_id, **kwargs):
    if client.uid not in added_ids:
        for user_id in added_ids:
            welcome_msg = "⭐ Welcome {name} to the group! Enjoy your stay! ⭐"
            await client.send_message(
                welcome_msg,
                thread_id,
                mentions=[user_id]
            )


if __name__ == "__main__":
    print("🚀 Bot start ho raha hai...")
    # ✅ FIX: client.run() khud event loop manage karta hai, asyncio.run() ki zaroorat nahi
    client.run()
