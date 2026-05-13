import time
import html
import urllib.request
import xml.etree.ElementTree as ET

import telebot


# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = "8798017715:AAH7e0OFZTE5MDsJy_-Hzb_QllqjghNrehE"
TG_CHANNEL = "-1003849323531"
YT_CHANNEL_ID = "UCZbfbuegnnviJ5UhXrNSU-w"

CHECK_INTERVAL = 60  # секунд

# =========================

ATOM_NS = "{http://www.w3.org/2005/Atom}"
YT_NS = "{http://www.youtube.com/xml/schemas/2015}"

bot = telebot.TeleBot(BOT_TOKEN)

# Храним уже отправленные видео
sent_videos = set()

# Первый запуск
initialized = False


def fetch_feed():
    url = (
        "https://www.youtube.com/feeds/videos.xml"
        f"?channel_id={YT_CHANNEL_ID}"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read()

    return ET.fromstring(data)


def send_video(title, video_id):
    link = f"https://youtu.be/{video_id}"

    text = (
        f"🎬 <b>Новое видео на канале!</b>\n\n"
        f"<b>{html.escape(title)}</b>\n\n"
        f"▶️ {link}"
    )

    bot.send_message(
        TG_CHANNEL,
        text,
        parse_mode="HTML",
        disable_web_page_preview=False
    )


def check_new_videos():
    global initialized
    global sent_videos
    

    root = fetch_feed()

    entries = root.findall(f"{ATOM_NS}entry")

    if not entries:
        return
    
    for entry in entries:
        video_id = entry.findtext(f"{YT_NS}videoId", default="")
        title = entry.findtext(f"{ATOM_NS}title", default="")
        print(video_id, title)

    # reversed() чтобы старые шли раньше новых
    for entry in reversed(entries):

        video_id = entry.findtext(
            f"{YT_NS}videoId",
            default=""
        )
        

        title = entry.findtext(
            f"{ATOM_NS}title",
            default="Без названия"
        )

        if not video_id:
            continue

        # Уже отправляли
        if video_id in sent_videos:
            continue

        # Первый запуск:
        # просто сохраняем видео без отправки
        if not initialized:
            sent_videos.add(video_id)
            continue

        # Отправка
        send_video(title, video_id)

        print(f"Отправлено новое видео: {title}")

        sent_videos.add(video_id)

    # После первого полного прохода
    initialized = True


def main():
    print("Бот запущен")

    while True:
        try:
            check_new_videos()

        except Exception as e:
            print("Ошибка:", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
    
