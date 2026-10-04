import asyncio
from fbchat_muqit import Client, ThreadType

# --- CONFIGURATION ---
ADMIN_IDS = ["100000000000000"]  # Yahan apna Facebook UID daalein
BOT_NICKNAME = "Group Manager Bot"

GROUP_LOCK = {}
NICKNAME_LOCK = {}
PHOTO_LOCK = {}

async def main():
    # Client object banayein (startSession nahi)
    bot = Client(cookies_file_path="./cookies.json")

    # ✅ Event handlers ko decorator se register karein
    @bot.event
    async def on_message(message):
        # Bot apne messages pe reply na kare
        if message.sender_id == bot.uid:
            return

        text = (message.text or "").strip()
        if not text.startswith("/"):
            return

        # Sirf group chat mein commands
        if message.thread_type != ThreadType.GROUP:
            return

        is_admin = str(message.sender_id) in ADMIN_IDS
        tid_str = str(message.thread_id)

        # /tid
        if text == "/tid":
            await bot.send_message(f"Group ID: {message.thread_id}", message.thread_id)

        # /uid
        elif text.startswith("/uid"):
            if message.mentions:
                mentioned_id = message.mentions[0].user_id
                await bot.send_message(f"User ID: {mentioned_id}", message.thread_id)
            else:
                await bot.send_message(f"Aapki ID: {message.sender_id}", message.thread_id)

        # /help
        elif text == "/help":
            help_text = (
                "📜 **Available Commands:**\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🔹 /tid - Group ID\n"
                "🔹 /uid <mention> - User ID\n"
                "🔹 /help - Yeh menu"
            )
            await bot.send_message(help_text, message.thread_id)

    print("🚀 Bot start ho raha hai...")
    bot.run()

if __name__ == "__main__":
    asyncio.run(main())
