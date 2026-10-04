import asyncio
import threading
import datetime
from fbchat_muqit import Client, Message, ThreadType

bot_state = {"status": "Stopped", "client": None, "thread": None}
logs = []
GROUP_LOCK = {}
NICKNAME_LOCK = {}
PHOTO_LOCK = {}
ADMIN_IDS = []
PREFIX = "/"


def add_log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    logs.append(f"[BOT] [{ts}] {msg}")
    if len(logs) > 200:
        logs.pop(0)


def get_logs():
    return logs


def clear_logs():
    logs.clear()


async def bot_main(appstate, prefix, admin_id):
    global PREFIX, ADMIN_IDS
    PREFIX = prefix
    ADMIN_IDS = [str(admin_id)] if admin_id else []

    add_log("INFO: ✅ Dashboard client connected")
    add_log("Bot status: Started")

    client = Client(appstate=appstate)

    @client.event
    async def on_message(message: Message):
        if message.sender_id == client.uid:
            return
        if not message.text or not message.text.startswith(prefix):
            return
        if message.thread_type != ThreadType.GROUP:
            return

        text = message.text.strip()
        cmd = text[len(prefix):].strip().lower()
        is_admin = str(message.sender_id) in ADMIN_IDS
        tid = str(message.thread_id)

        if cmd == "help":
            await client.send_message(
                "📜 Commands:\n"
                f"{prefix}group on/off - Group name lock\n"
                f"{prefix}nickname on/off - Nickname lock\n"
                f"{prefix}photolock on/off - Photo lock\n"
                f"{prefix}tid - Group ID\n"
                f"{prefix}uid - User ID\n"
                f"{prefix}status - Lock status",
                message.thread_id,
            )

        elif cmd == "tid":
            await client.send_message(f"Group ID: {message.thread_id}", message.thread_id)

        elif cmd.startswith("uid"):
            if message.mentions:
                await client.send_message(
                    f"User ID: {message.mentions[0].user_id}", message.thread_id
                )
            else:
                await client.send_message(f"Aapki ID: {message.sender_id}", message.thread_id)

        elif cmd.startswith("group") and is_admin:
            action = cmd.replace("group", "").strip()
            if action == "on":
                GROUP_LOCK[tid] = True
                await client.send_message("🔒 Group Name Lock: ON", message.thread_id)
            elif action == "off":
                GROUP_LOCK[tid] = False
                await client.send_message("🔓 Group Name Lock: OFF", message.thread_id)

        elif cmd.startswith("nickname") and is_admin:
            action = cmd.replace("nickname", "").strip()
            if action == "on":
                NICKNAME_LOCK[tid] = True
                await client.send_message("🔒 Nickname Lock: ON", message.thread_id)
            elif action == "off":
                NICKNAME_LOCK[tid] = False
                await client.send_message("🔓 Nickname Lock: OFF", message.thread_id)

        elif cmd.startswith("photolock") and is_admin:
            action = cmd.replace("photolock", "").strip()
            if action == "on":
                PHOTO_LOCK[tid] = True
                await client.send_message("🔒 Photo Lock: ON", message.thread_id)
            elif action == "off":
                PHOTO_LOCK[tid] = False
                await client.send_message("🔓 Photo Lock: OFF", message.thread_id)

        elif cmd == "status":
            await client.send_message(
                f"📊 Lock Status\n"
                f"🔒 Group: {'ON' if GROUP_LOCK.get(tid) else 'OFF'}\n"
                f"🔒 Nickname: {'ON' if NICKNAME_LOCK.get(tid) else 'OFF'}\n"
                f"🔒 Photo: {'ON' if PHOTO_LOCK.get(tid) else 'OFF'}",
                message.thread_id,
            )

    bot_state["client"] = client
    bot_state["status"] = "Running"
    add_log("✅ Bot logged in successfully")

    try:
        client.run()
    except Exception as e:
        add_log(f"ERROR: {e}")
        bot_state["status"] = "Stopped"


def run_bot_thread(appstate, prefix, admin_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(bot_main(appstate, prefix, admin_id))
    except Exception as e:
        add_log(f"ERROR in thread: {e}")


def start_bot(appstate, prefix, admin_id):
    if bot_state["status"] == "Running":
        return {"status": "already_running"}

    thread = threading.Thread(
        target=run_bot_thread, args=(appstate, prefix, admin_id), daemon=True
    )
    thread.start()
    bot_state["thread"] = thread
    return {"status": "started"}


def stop_bot():
    bot_state["status"] = "Stopped"
    bot_state["client"] = None
    add_log("Bot stopped by user")
    return {"status": "stopped"}
