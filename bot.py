import asyncio
from fbchat_muqit import Client, Message, ThreadType

# --- CONFIGURATION ---
ADMIN_IDS = ["61594936980939"]  # ✅ Aapki User ID (cookies se mili)
BOT_NICKNAME = "Group Manager Bot"

GROUP_LOCK = {}
NICKNAME_LOCK = {}
PHOTO_LOCK = {}

# ✅ Client initialize
client = Client(cookies_file_path="cookies.json")


# ============================
# MESSAGE HANDLER
# ============================
@client.event
async def on_message(message: Message):
    if message.sender_id == client.uid:
        return

    text = (message.text or "").strip()
    if not text.startswith("/"):
        return

    if message.thread_type != ThreadType.GROUP:
        return

    is_admin = str(message.sender_id) in ADMIN_IDS
    tid_str = str(message.thread_id)

    # --- /help ---
    if text == "/help":
        help_text = (
            "📜 **Available Commands:**\n"
            "🔹 /tid - Group ID\n"
            "🔹 /uid <mention> - User ID\n"
            "🔹 /botnick <name> - Bot Nickname (Admin)\n"
            "🔹 /photolock on/off - Photo Lock (Admin)\n"
            "🔹 /grouplock on/off - Group Name Lock (Admin)\n"
            "🔹 /nicklock on/off - Nickname Lock (Admin)\n"
            "🔹 /status - Current Lock Status"
        )
        await client.send_message(help_text, message.thread_id)

    elif text == "/tid":
        await client.send_message(f"Group ID: {message.thread_id}", message.thread_id)

    elif text.startswith("/uid"):
        if message.mentions:
            mentioned_id = message.mentions[0].user_id
            await client.send_message(f"User ID: {mentioned_id}", message.thread_id)
        else:
            await client.send_message(f"Aapki ID: {message.sender_id}", message.thread_id)

    elif text.startswith("/botnick") and is_admin:
        global BOT_NICKNAME
        new_nick = text.replace("/botnick", "").strip()
        if new_nick:
            BOT_NICKNAME = new_nick
            await client.send_message(f"✅ Bot nickname set: {new_nick}", message.thread_id)

    elif text.startswith("/photolock") and is_admin:
        action = text.replace("/photolock", "").strip().lower()
        if action == "on":
            PHOTO_LOCK[tid_str] = True
            await client.send_message("🔒 Photo Lock: ON", message.thread_id)
        elif action == "off":
            PHOTO_LOCK[tid_str] = False
            await client.send_message("🔓 Photo Lock: OFF", message.thread_id)

    elif text.startswith("/grouplock") and is_admin:
        action = text.replace("/grouplock", "").strip().lower()
        if action == "on":
            GROUP_LOCK[tid_str] = True
            await client.send_message("🔒 Group Name Lock: ON", message.thread_id)
        elif action == "off":
            GROUP_LOCK[tid_str] = False
            await client.send_message("🔓 Group Name Lock: OFF", message.thread_id)

    elif text.startswith("/nicklock") and is_admin:
        action = text.replace("/nicklock", "").strip().lower()
        if action == "on":
            NICKNAME_LOCK[tid_str] = True
            await client.send_message("🔒 Nickname Lock: ON", message.thread_id)
        elif action == "off":
            NICKNAME_LOCK[tid_str] = False
            await client.send_message("🔓 Nickname Lock: OFF", message.thread_id)

    elif text == "/status":
        status_msg = (
            f"📊 **Group Lock Status**\n"
            f"🔒 Photo Lock: {'ON' if PHOTO_LOCK.get(tid_str) else 'OFF'}\n"
            f"🔒 Group Name Lock: {'ON' if GROUP_LOCK.get(tid_str) else 'OFF'}\n"
            f"🔒 Nickname Lock: {'ON' if NICKNAME_LOCK.get(tid_str) else 'OFF'}"
        )
        await client.send_message(status_msg, message.thread_id)


# ============================
# RUN BOT
# ============================
if __name__ == "__main__":
    print("🚀 Bot start ho raha hai...")
    client.run()
