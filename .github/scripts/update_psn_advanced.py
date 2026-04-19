import os
from datetime import datetime
import requests
from psnawp_api import PSNAWP

PSN_ID = "banerlc"
TWITCH_USERNAME = "crazybrad77"

NPSSO = os.getenv("NPSSO")

def get_twitch_status():
    try:
        url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
        headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1k9"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json().get("data", [])
        if data:
            stream = data[0]
            return f"🔴 LIVE on Twitch: {stream['title']} ({stream['viewer_count']} viewers)"
        return "🟢 Offline on Twitch"
    except:
        return "Twitch status unavailable"

def main():
    if not NPSSO:
        print("❌ NPSSO not found!")
        return

    psnawp = PSNAWP(npsso_cookie=NPSSO)
    user = psnawp.user(online_id=PSN_ID)

    profile = user.profile()
    trophy_summary = user.trophy_summary()
    presence = user.get_presence()

    # Recent Platinums (safer handling of TrophyTitle objects)
    recent_platinums = []
    try:
        for title in user.trophy_titles(limit=30):
            earned = getattr(title, 'earned_trophies', {})
            platinum = earned.get('platinum', 0) if isinstance(earned, dict) else 0

            if platinum > 0:
                icon = getattr(title, 'trophy_title_icon_url', '') or getattr(title, 'icon_url', '')
                earned_date = getattr(title, 'last_updated_datetime', 'N/A')
                if isinstance(earned_date, str):
                    earned_date = earned_date[:10]

                recent_platinums.append({
                    "title": getattr(title, 'trophy_title_name', 'Unknown Game'),
                    "icon": icon,
                    "earned": earned_date
                })
                if len(recent_platinums) >= 5:
                    break
    except Exception as e:
        print(f"Warning: Could not load platinums: {e}")

    # Safe attribute access for trophy summary
    level = getattr(trophy_summary, 'trophy_level', getattr(trophy_summary, 'level', 'N/A'))
    total_trophies = getattr(trophy_summary, 'total_trophies', getattr(trophy_summary, 'totalTrophies', 0))
    platinum_count = getattr(trophy_summary, 'platinum_count', getattr(trophy_summary, 'platinum', 0))

    now_playing = presence.get("primaryInfo", {}).get("onlineStatus", "Offline")
    current_game = presence.get("primaryInfo", {}).get("gameTitle", "Not playing")

    ps_plus_status = "✅ Active" if getattr(profile, 'is_ps_plus', False) or getattr(profile, 'isPsPlus', False) else "❌ Inactive"

    twitch_status = get_twitch_status()

    # Update README
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!--START_SECTION:psn-->"
    end = "<!--END_SECTION:psn-->"

    new_section = f"""
<div align="center">
  <h3>🎮 PSN + Twitch Live Dashboard • Updated {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}</h3>

  <p><strong>Level {level}</strong> • {total_trophies} Trophies • {platinum_count} Platinum 🏆</p>

  <img src="https://img.shields.io/badge/PS%20Plus-{ps_plus_status.replace(' ', '%20')}-003087?style=for-the-badge&logo=playstation&logoColor=white" alt="PS Plus" />

  <h4>🔥 Recent Platinums</h4>
  <table>
    <tr><th>Game</th><th>Earned</th></tr>
    {"".join(f"<tr><td><img src='{p['icon']}' width='32' height='32' style='vertical-align:middle'> {p['title']}</td><td>{p['earned']}</td></tr>" for p in recent_platinums)}
  </table>

  <h4>📡 Live Status</h4>
  <p><strong>PSN:</strong> {now_playing} • <strong>Playing:</strong> {current_game}</p>
  <p><strong>Twitch:</strong> {twitch_status}</p>

  <a href="https://twitch.tv/{TWITCH_USERNAME}" target="_blank">
    <img src="https://img.shields.io/badge/Twitch-Follow%20Me-9146FF?style=for-the-badge&logo=twitch&logoColor=white" alt="Twitch" />
  </a>
</div>
"""

    if start in content and end in content:
        before = content.split(start)[0]
        after = content.split(end)[1]
        content = before + start + new_section + end + after
    else:
        content += f"\n{start}{new_section}{end}\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ PSN Dashboard updated successfully!")

if __name__ == "__main__":
    main()
