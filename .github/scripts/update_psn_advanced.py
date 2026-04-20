import os
from datetime import datetime

TWITCH_USERNAME = "crazybrad77"

def main():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!--START_SECTION:psn-->"
    end = "<!--END_SECTION:psn-->"

    new_section = f"""
<div align="center">
  <h3>🎮 PSN + Twitch Status • Last Updated {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}</h3>
  
  <p><strong>PSN ID:</strong> Banerlc</p>
  <p>Add me for GTA Online sessions or co-op!</p>

  <img src="https://img.shields.io/badge/PS%20Plus-Check%20in%20game-003087?style=for-the-badge&logo=playstation&logoColor=white" alt="PS Plus" />

  <a href="https://psnprofiles.com/Banerlc" target="_blank">
    <img src="https://img.shields.io/badge/View%20Full%20Profile%20on%20PSNProfiles-003087?style=for-the-badge&logo=playstation&logoColor=white" alt="PSNProfiles" />
  </a>
  
  <a href="https://twitch.tv/{TWITCH_USERNAME}" target="_blank">
    <img src="https://img.shields.io/badge/Twitch-Follow%20Live-9146FF?style=for-the-badge&logo=twitch&logoColor=white" alt="Twitch" />
  </a>
</div>
"""

    if start in content and end in content:
        before = content.split(start)[0]
        after = content.split(end)[1]
        content = before + start + new_section + end + after

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Minimal PSN section updated")

if __name__ == "__main__":
    main()
