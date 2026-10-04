import asyncio
import nest_asyncio2  # ✅ Naya fix: event loop patching
from fbchat_muqit import Client, ThreadType

# Event loop nested usage ko enable karein (Render ke liye zaroori)
nest_asyncio2.apply()

# --- CONFIGURATION ---
ADMIN_IDS = ["100000000000000"]  # Yahan apna Facebook UID daalein
BOT_NICKNAME = "Group Manager Bot"

# State storage (Render restart pe reset ho jayega)
GROUP_LOCK = {}
NICKNAME_LOCK = {}
PHOTO_LOCK = {}


class GroupManagerBot(Client):

    async def onMessage(self, mid, author_id, message_object, thread_id, thread_type, **kwargs):
        if author_id == self.uid:
            return

        text = (message_object.text or "").strip()
        if not text.startswith("/"):
            return

        if thread_type != ThreadType.GROUP:
            return

        is_admin = str(author_id) in ADMIN_IDS
        tid_str = str(thread_id)

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
            await message_object.reply(help_text)

        # --- /tid ---
        elif text == "/tid":
            await message_object.reply(f"Group ID: {thread_id}")

        # --- /uid ---
        elif text.startswith("/uid"):
            if message_object.mentions:
                mentioned_id = message_object.mentions[0].user_id
                await message_object.reply(f"User ID: {mentioned_id}")
            else:
                await message_object.reply(f"Aapki ID: {author_id}")

        # --- /botnick ---
        elif text.startswith("/botnick") and is_admin:
            global BOT_NICKNAME
            new_nick = text.replace("/botnick", "").strip()
            if new_nick:
                BOT_NICKNAME = new_nick
                await message_object.reply(f"✅ Bot nickname set: {new_nick}")
            else:
                await message_object.reply("Usage: /botnick <name>")

        # --- /photolock ---
        elif text.startswith("/photolock") and is_admin:
            action = text.replace("/photolock", "").strip().lower()
            if action == "on":
                PHOTO_LOCK[tid_str] = True
                await message_object.reply("🔒 Group Photo Lock: ON")
            elif action == "off":
                PHOTO_LOCK[tid_str] = False
                await message_object.reply("🔓 Group Photo Lock: OFF")
            else:
                await message_object.reply("Usage: /photolock on | /photolock off")

        # --- /grouplock ---
        elif text.startswith("/grouplock") and is_admin:
            action = text.replace("/grouplock", "").strip().lower()
            if action == "on":
                GROUP_LOCK[tid_str] = True
                await message_object.reply("🔒 Group Name Lock: ON")
            elif action == "off":
                GROUP_LOCK[tid_str] = False
                await message_object.reply("🔓 Group Name Lock: OFF")
            else:
                await message_object.reply("Usage: /grouplock on | /grouplock off")

        # --- /nicklock ---
        elif text.startswith("/nicklock") and is_admin:
            action = text.replace("/nicklock", "").strip().lower()
            if action == "on":
                NICKNAME_LOCK[tid_str] = True
                await message_object.reply("🔒 Nickname Lock: ON")
            elif action == "off":
                NICKNAME_LOCK[tid_str] = False
                await message_object.reply("🔓 Nickname Lock: OFF")
            else:
                await message_object.reply("Usage: /nicklock on | /nicklock off")

        # --- /status ---
        elif text == "/status":
            status_msg = (
                f"📊 **Group Lock Status**\n"
                f"🔒 Photo Lock: {'ON' if PHOTO_LOCK.get(tid_str) else 'OFF'}\n"
                f"🔒 Group Name Lock: {'ON' if GROUP_LOCK.get(tid_str) else 'OFF'}\n"
                f"🔒 Nickname Lock: {'ON' if NICKNAME_LOCK.get(tid_str) else 'OFF'}\n"
                f"🤖 Bot Nickname: {BOT_NICKNAME}"
            )
            await message_object.reply(status_msg)

    async def onPeopleAdded(self, added_ids, author_id, thread_id, **kwargs):
        if self.uid not in added_ids:
            for user_id in added_ids:
                welcome_msg = f"⭐ Welcome {{name}} to the group! Enjoy your stay! ⭐"
                await self.sendMessage(
                    welcome_msg,
                    thread_id,
                    ThreadType.GROUP,
                    mentions=[user_id]
                )


async def main():
    cookies_path = "./cookies.json"
    print("🚀 Bot start ho raha hai...")

    bot = await Client.startSession(cookies_path)

    if await bot.isLoggedIn():
        print(f"✅ Logged in as UID: {bot.uid}")
        print("👂 Bot listening for commands...")
        await bot.listen()
    else:
        print("❌ Login failed! Cookies check karein.")


if __name__ == "__main__":
    asyncio.run(main())
