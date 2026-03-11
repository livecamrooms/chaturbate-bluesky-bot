import os
import requests
import time
from atproto import Client, client_utils
from datetime import datetime

# === CONFIG ===
BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE')
BLUESKY_PASS = os.getenv('BLUESKY_PASSWORD')
API_URL = "https://chaturbate.com/affiliates/api/onlinerooms/?format=json&wm=T2CSW"
MAX_POSTS_PER_RUN = 4

def get_niche_label(room):
    age = room.get('age')
    tags_lower = [t.lower() for t in room.get('tags', [])]
    country = (room.get('country') or '').upper()
    
    if age == 18:
        return "18yo"
    for kw in ['latina', 'blonde', 'petite', 'pinay', 'french']:
        if kw in tags_lower:
            return kw.capitalize()
    if country == 'FR':
        return "French"
    if country == 'PH':
        return "Pinay"
    return "Hot"

def main():
    client = Client()
    client.login(BLUESKY_HANDLE, BLUESKY_PASS)

    data = requests.get(API_URL).json()

    filtered = [
        room for room in data
        if (room.get('gender') == 'f' and
            room.get('current_show') == 'public' and
            room.get('is_hd') is True and
            int(room.get('num_users', 0)) >= 30 and
            (room.get('age') == 18 or
             any(kw in [t.lower() for t in room.get('tags', [])]
                 for kw in ['latina', 'blonde', 'petite', 'pinay', 'french']) or
             room.get('country') in ['FR', 'PH']))
    ]

    filtered.sort(key=lambda x: int(x.get('num_users', 0)), reverse=True)

    for room in filtered[:MAX_POSTS_PER_RUN]:
        try:
            img_resp = requests.get(room['image_url_360x270'])
            img_bytes = img_resp.content

            niche = get_niche_label(room)
            subject = room['room_subject'][:70] + '...' if len(room['room_subject']) > 70 else room['room_subject']

            tb = client_utils.TextBuilder()
            tb.text(f"🔥 {niche} LIVE NOW ({room['num_users']} watching)\n\n")
            tb.text(f"{room['username']} • {room.get('age') or '?'} • {room.get('country') or '??'}\n")
            tb.text(f"{subject}\n\n")
            tb.link("👉 Watch FREE", room['chat_room_url_revshare'])
            tb.text("\n\n")

            # Clickable hashtags
            tb.tag("#nsfw", "nsfw")
            tb.text(" ")
            tb.tag(f"#{niche}", niche)
            tb.text(" ")
            tb.tag("#nsfwsky", "nsfwsky")
            tb.text(" ")
            tb.tag("#LiveCams", "LiveCams")
            tb.text(" ")
            tb.tag("#Adult", "Adult")

            tags = room.get('tags', [])[:5]
            for tag in tags:
                clean = tag.strip().replace(' ', '')
                if clean:
                    tb.text(" ")
                    tb.tag(f"#{clean.title()}", clean.title())

            client.send_image(
                text=tb,
                image=img_bytes,
                image_alt=f"Live HD thumbnail of {niche} {room['username']} - {subject[:50]}"
            )

            print(f"✅ Posted: {niche} - {room['username']}")
            time.sleep(15)

        except Exception as e:
            print(f"Error posting {room['username']}: {e}")

    print(f"Run finished at {datetime.now()} - {len(filtered)} matching rooms found")

if __name__ == "__main__":
    main()
