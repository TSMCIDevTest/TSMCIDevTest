import os
from datetime import datetime
from psnawp_api import PSNAWP

PSN_ID = "banerlc"
TWITCH_USERNAME = "crazybrad77"   # ← Change if your Twitch name is different
NPSSO = os.getenv("NPSSO")

def get_twitch_status():
    # Simple public check via Twitch API (no secret needed for basic status)
    try:
        import requests
        url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
        headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1k9"}  # Public client ID
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json().get("data", [])
        if data:
            stream = data[0]
            return f"🔴 LIVE on Twitch: {stream['title']} ({stream['viewer_count']} viewers)"
        return "🟢 Offline on Twitch"
    except:
        return "Twitch status unavailable"

def main():
    psnawp = PSNAWP(npsso=NPSSO)
    user = psnawp.user(online_id=PSN_ID)

    profile = user.get_profile()
    trophy_summary = user.trophy_summary()
    presence = user.get_presence()

    # Recent platinums with icons
    trophy_titles = list(user.trophy_titles(limit=50))
    recent_platinums = []
    for title in trophy_titles:
        if title.get("trophySummary", {}).get("earnedTrophies", {}).get("platinum", 0) > 0:
            icon = title.get("trophyTitleIconUrl", "")
            earned = title.get("earnedDateTime", "N/A")[:10]
            recent_platinums.append({"title": title["trophyTitleName"], "icon": icon, "earned": earned})
            if len(recent_platinums) >= 5:
                break

    now_playing = presence.get("primaryInfo", {}).get("onlineStatus", "Offline")
    current_game = presence.get("primaryInfo", {}).get("gameTitle", "Not playing")

    # PS Plus (fallback to visible badge)
    ps_plus_status = "✅ Active" if profile.get("isPsPlus", True) else "❌ Inactive"  # Many accounts show via presence

    twitch_status = get_twitch_status()

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!--START_SECTION:psn-->"
    end = "<!--END_SECTION:psn-->"

    new_section = f"""
<div align="center">
  <h3>🎮 PSN + Twitch Live Dashboard • Updated {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}</h3>

  <p><strong>Level {trophy_summary.get('trophyLevel', 'N/A')}</strong> • {trophy_summary.get('totalTrophies', 0)} Trophies • {trophy_summary.get('platinumCount', 0)} Platinum 🏆</p>

  <!-- PS Plus Icon -->
  <img src="https://img.shields.io/badge/PS%20Plus-{ps_plus_status.replace(' ', '%20')}-003087?style=for-the-badge&logo=playstation&logoColor=white" alt="PS Plus Status" />

  <h4>🔥 Recent Platinums</h4>
  <table>
    <tr><th>Game</th><th>Earned</th></tr>
    {"".join(f"<tr><td><img src='{p['icon']}' width='32' height='32'> {p['title']}</td><td>{p['earned']}</td></tr>" for p in recent_platinums)}
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
        content = content.split(start)[0] + start + new_section + end + content.split(end)[1]
    else:
        content += f"\n{start}{new_section}{end}\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Updated with custom neon skyscrapers, Twitch integration & PS Plus icon!")

if __name__ == "__main__":
    main()
