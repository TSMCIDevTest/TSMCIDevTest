import os
from datetime import datetime
import requests
from psnawp_api import PSNAWP

PSN_ID = "banerlc"          # ← Your PSN Online ID
TWITCH_USERNAME = "crazybrad77" # ← Your Twitch username

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
        print("❌ NPSSO environment variable not found!")
        return

    psnawp = PSNAWP(npsso_cookie=NPSSO)
    user = psnawp.user(online_id=PSN_ID)

    profile = user.profile()
    trophy_summary = user.trophy_summary()
    presence = user.get_presence()

    # FIXED: trophy_titles() returns TrophyTitle objects, not dicts
    recent_platinums = []
    try:
        for title in user.trophy_titles(limit=50):
            # Access attributes directly (TrophyTitle object)
            earned_trophies = title.earned_trophies if hasattr(title, 'earned_trophies') else {}
            platinum_count = earned_trophies.get('platinum', 0) if isinstance(earned_trophies, dict) else 0

            if platinum_count > 0:
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
        print(f"Warning: Could not fetch recent platinums: {e}")
        recent_platinums = []

    now_playing = presence.get("primaryInfo", {}).get("onlineStatus", "Offline")
    current_game = presence.get("primaryInfo", {}).get("gameTitle", "Not playing")

    ps_plus_status = "✅ Active" if getattr(profile, 'is_ps_plus', False) or profile.get('isPsPlus', False) else "❌ Inactive"

    twitch_status = get_twitch_status()

    # Update README
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!--START_SECTION:psn-->"
    end_marker = "<!--END_SECTION:psn-->"

    new_section = f"""
<div align="center">
  <h3>🎮 PSN + Twitch Live Dashboard • Updated {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}</h3>

  <p><strong>Level {getattr(trophy_summary, 'trophy_level', trophy_summary.get('trophyLevel', 'N/A'))}</strong> 
     • {getattr(trophy_summary, 'total_trophies', trophy_summary.get('totalTrophies', 0))} Trophies 
     • {getattr(trophy_summary, 'platinum_count', trophy_summary.get('platinumCount', 0))} Platinum 🏆</p>

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

    if start_marker in content and end_marker in content:
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]
        content = before + start_marker + new_section + end_marker + after
    else:
        content += f"\n{start_marker}{new_section}{end_marker}\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ PSN + Twitch section updated successfully!")

if __name__ == "__main__":
    main()
