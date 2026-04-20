import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

PSN_ID = "Banerlc"   # Your actual PSN ID

def scrape_psnprofiles():
    url = f"https://psnprofiles.com/{PSN_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract basic stats
        level = "N/A"
        total_trophies = "0"
        platinum = "0"
        games_played = "0"

        # Look for level
        level_tag = soup.find("span", class_="trophy-level")
        if level_tag:
            level = level_tag.get_text(strip=True).replace("Level ", "")

        # Trophy counts (Platinum, Total, etc.)
        trophy_counts = soup.find_all("span", class_="trophy-count")
        if trophy_counts:
            for count in trophy_counts:
                text = count.get_text(strip=True)
                if "Platinum" in text or "platinums" in text.lower():
                    platinum = text.split()[0].replace(",", "")
                elif any(x in text for x in ["Trophy", "trophies"]):
                    total_trophies = text.split()[0].replace(",", "")

        # Games played / completion
        games_tag = soup.find(string=lambda t: t and "Games" in t)
        if games_tag and games_tag.parent:
            games_played = games_tag.parent.get_text(strip=True).split()[0]

        return {
            "level": level,
            "total_trophies": total_trophies,
            "platinum": platinum,
            "games_played": games_played
        }

    except Exception as e:
        print(f"Scrape failed: {e}")
        return None

def main():
    data = scrape_psnprofiles()
    
    if not data:
        data = {"level": "N/A", "total_trophies": "0", "platinum": "0", "games_played": "0"}

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!--START_SECTION:psn-->"
    end = "<!--END_SECTION:psn-->"

    new_section = f"""
<div align="center">
  <h3>PSN Profile – {PSN_ID} • PlayStation Plus User since 2026!</h3>
  
  <p><strong>Level {data['level']}</strong> • {data['total_trophies']} Trophies • {data['platinum']} Platinum </p>
  <p><strong>Games Played:</strong> {data['games_played']}</p>

  <a href="https://psnprofiles.com/{PSN_ID}" target="_blank">
    <img src="https://img.shields.io/badge/View%20Full%20Profile%20on%20PSNProfiles-003087?style=for-the-badge&logo=playstation&logoColor=white" alt="PSNProfiles" />
  </a>

  <br><br>
  <p><em>Last updated: {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}</em></p>
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

    print("✅ PSNProfiles data updated successfully!")

if __name__ == "__main__":
    main()
