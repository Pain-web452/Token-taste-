import asyncio
import json
import os
from fbchat_muqit import Client, ThreadType, Message

# --- CONFIGURATION ---
ADMIN_IDS = ["100000000000000"]  # Yahan apna Facebook UID daalein
BOT_NICKNAME = "Group Manager Bot"

# State storage (Render pe temporary rahega, restart pe reset ho jayega)
GROUP_LOCK = {}       # {thread_id: True/False} - Group name/photo lock
NICKNAME_LOCK = {}    # {thread_id: True/False} - Nickname lock
PHOTO_LOCK = {}       # {thread_id: True/False} - Photo lock

class GroupManagerBot(Client):

    async def onMessage(self, mid, author_id, message_object, thread_id, thread_type, **kwargs):
        # Bot apne messages pe reply na kare
        if author_id == self.uid:
            return

        text = (message_object.text or "").strip()
        if not text.startswith("/"):
            return

        # Sirf group chat mein commands
        if thread_type != ThreadType.GROUP:
            return

        is_admin = str(author_id) in ADMIN_IDS
        tid_str = str(thread_id)

        # ============================
        # 1. /tid - Group ID
        # ============================
        if text == "/tid":
            await message_object.reply(f"Group ID: {thread_id}")

        # ============================
        # 2. /uid <mention> - User ID
        # ============================
        elif text.startswith("/uid"):
            if message_object.mentions:
                mentioned_id = message_object.mentions[0].user_id
                await message_object.reply(f"User ID: {mentioned_id}")
            else:
                await message_object.reply(f"Aapki ID: {author_id}")

        # ============================
        # 3. /botnick <name> - Bot ka nickname (Admin)
        # ============================
        elif text.startswith("/botnick") and is_admin:
            global BOT_NICKNAME
            new_nick = text.replace("/botnick", "").strip()
            if new_nick:
                BOT_NICKNAME = new_nick
                await message_object.reply(f"✅ Bot nickname set: {new_nick}")
            else:
                await message_object.reply("Usage: /botnick <name>")

        # ============================
        # 4. /photolock on/off - Photo Lock (Admin)
        # ============================
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

        # ============================
        # 5. /grouplock on/off - Group Name Lock (Admin)
        # ============================
        elif text.startswith("/grouplock") and is_admin:
            action = text.replace("/grouplock", "").strip().lower()
            if action == "on":
                GROUP_LOCK[tid_str] = True
                await message_object.reply("🔒 Group Name Lock: ON (Group ka naam change nahi ho sakta)")
            elif action == "off":
                GROUP_LOCK[tid_str] = False
                await message_object.reply("🔓 Group Name Lock: OFF")
            else:
                await message_object.reply("Usage: /grouplock on | /grouplock off")

        # ============================
        # 6. /nicklock on/off - Nickname Lock (Admin)
        # ============================
        elif text.startswith("/nicklock") and is_admin:
            action = text.replace("/nicklock", "").strip().lower()
            if action == "on":
                NICKNAME_LOCK[tid_str] = True
                await message_object.reply("🔒 Nickname Lock: ON (Koi apna nickname change nahi kar sakta)")
            elif action == "off":
                NICKNAME_LOCK[tid_str] = False
                await message_object.reply("🔓 Nickname Lock: OFF")
            else:
                await message_object.reply("Usage: /nicklock on | /nicklock off")

        # ============================
        # 7. /status - Sabhi locks ka status
        # ============================
        elif text == "/status":
            status_msg = (
                f"📊 **Group Lock Status**\n"
                f"🔒 Photo Lock: {'ON' if PHOTO_LOCK.get(tid_str) else 'OFF'}\n"
                f"🔒 Group Name Lock: {'ON' if GROUP_LOCK.get(tid_str) else 'OFF'}\n"
                f"🔒 Nickname Lock: {'ON' if NICKNAME_LOCK.get(tid_str) else 'OFF'}\n"
                f"🤖 Bot Nickname: {BOT_NICKNAME}"
            )
            await message_object.reply(status_msg)

        # ============================
        # 8. /help - Commands list
        # ============================
        elif text == "/help":
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

    # ============================
    # AUTO PROTECTION LOGIC
    # ============================
    async def onTitleChange(self, author_id, new_title, thread_id, **kwargs):
        """Agar koi group ka naam change kare jab Group Lock ON ho."""
        if GROUP_LOCK.get(str(thread_id)):
            # Group ka naam wapas purana kar do
            # Note: fbchat-muqit mein purana naam fetch karna limited hai
            await self.sendMessage(
                "⚠️ Group Name Lock ON hai! Naam change nahi kar sakte.",
                thread_id,
                ThreadType.GROUP
            )

    async def onNicknameChange(self, author_id, new_nickname, thread_id, **kwargs):
        """Agar koi apna nickname change kare jab Nickname Lock ON ho."""
        if NICKNAME_LOCK.get(str(thread_id)):
            await self.sendMessage(
                "⚠️ Nickname Lock ON hai! Nickname change nahi kar sakte.",
                thread_id,
                ThreadType.GROUP
            )

    # ============================
    # WELCOME MESSAGE
    # ============================
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
    bot = await GroupManagerBot.startSession(cookies_path)

    if await bot.isLoggedIn():
        print(f"✅ Logged in as UID: {bot.uid}")
        print("👂 Bot listening for commands...")
        await bot.listen()
    else:
        print("❌ Login failed! Cookies check karein.")

if __name__ == "__main__":
    asyncio.run(main())
