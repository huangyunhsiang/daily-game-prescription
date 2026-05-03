#!/usr/bin/env python3
"""
Game Prescription Video Generator
Reads from games.json and generates Hyperframes composition HTML.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parent
GAMES_FILE = PROJECT_DIR / "games.json"
RENDERS_DIR = PROJECT_DIR / "renders"
COMPOSITIONS_DIR = PROJECT_DIR / "compositions"


def load_games():
    with open(GAMES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


COMPOSITION_TEMPLATE = '''<!doctype html>
<html lang="zh-Hant-TW">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{
        margin: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: linear-gradient(135deg, #fff0e6 0%, #ffe4f0 30%, #e6f3ff 70%, #f0fff4 100%);
        font-family: "Noto Sans TC", "Microsoft JhengHei", system-ui, sans-serif;
      }}
      .scene {{
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px;
        text-align: center;
      }}
      h1 {{
        font-size: 120px;
        font-weight: 900;
        color: #ff6b8a;
        text-shadow: 0 8px 24px rgba(255,107,138,0.25);
        line-height: 1.2;
      }}
      .subtitle {{
        font-size: 64px;
        font-weight: 700;
        color: #5a7d9c;
        margin-top: 16px;
      }}
      .game-icon {{
        font-size: 120px;
        margin-bottom: 20px;
      }}
      .game-name {{
        font-size: 130px;
        font-weight: 900;
        color: #ff8a5c;
        text-shadow: 0 8px 24px rgba(255,138,92,0.3);
      }}
      .age-badge {{
        display: inline-block;
        font-size: 48px;
        font-weight: 800;
        color: #fff;
        background: linear-gradient(135deg, #5ab7ff, #54d8a8);
        border-radius: 60px;
        padding: 14px 44px;
        margin-top: 20px;
        box-shadow: 0 8px 24px rgba(90,183,255,0.3);
      }}
      .material-text {{
        font-size: 54px;
        font-weight: 700;
        color: #5a6a7a;
        line-height: 1.4;
      }}
      .material-icon {{
        font-size: 70px;
        display: block;
        margin-bottom: 8px;
      }}
      .highlight {{
        color: #ff6b8a;
        font-weight: 900;
      }}
      .step-text {{
        font-size: 48px;
        font-weight: 600;
        color: #4a5a6a;
        line-height: 1.5;
        max-width: 1400px;
      }}
      .safety-box {{
        background: rgba(255,216,77,0.2);
        border: 4px solid #ffd84d;
        border-radius: 48px;
        padding: 28px 56px;
        margin-top: 20px;
      }}
      .safety-text {{
        font-size: 42px;
        font-weight: 700;
        color: #c07a2e;
      }}
      .benefit-text {{
        font-size: 44px;
        font-weight: 700;
        color: #54a88a;
      }}
      .label-tag {{
        display: inline-block;
        font-size: 34px;
        font-weight: 800;
        color: #fff;
        background: #ff6b8a;
        border-radius: 20px;
        padding: 6px 24px;
        margin-bottom: 10px;
      }}
      .day-badge {{
        font-size: 40px;
        font-weight: 800;
        color: #7a5a8a;
        margin-top: 10px;
      }}
      .scene-0 {{ z-index: 10; }}
      .scene-1 {{ z-index: 9; }}
      .scene-2 {{ z-index: 8; }}
      .scene-3 {{ z-index: 7; }}
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="game-{game_id}"
      data-start="0"
      data-duration="15"
      data-width="1920"
      data-height="1080"
    >
      <!-- Scene 1: Title Card -->
      <div id="scene1" class="scene scene-0 clip" data-start="0" data-duration="3.5" data-track-index="0">
        <h1 id="titleMain">每日遊戲處方簽</h1>
        <div id="daySub" class="subtitle" style="opacity:0">Day {day}</div>
      </div>

      <!-- Scene 2: Game Name + Age -->
      <div id="scene2" class="scene scene-1 clip" data-start="3.5" data-duration="3.5" data-track-index="0" style="opacity:0">
        <div class="game-icon">{icon}</div>
        <div class="game-name" id="gameName">{game_name}</div>
        <div class="age-badge" id="ageBadge" style="opacity:0">👶 {age_min}-{age_max} 個月</div>
      </div>

      <!-- Scene 3: Materials + How to Play -->
      <div id="scene3" class="scene scene-2 clip" data-start="7" data-duration="4" data-track-index="0" style="opacity:0">
        <div class="label-tag" id="tag3">🎲 準備</div>
        <div class="material-text" id="matText" style="opacity:0">
          <span class="material-icon">{icon}</span>
          {materials}
        </div>
        <div class="step-text" id="stepText" style="opacity:0; margin-top:20px">
          {description}
        </div>
      </div>

      <!-- Scene 4: Safety + Benefit -->
      <div id="scene4" class="scene scene-3 clip" data-start="11" data-duration="4" data-track-index="0" style="opacity:0">
        <div class="label-tag" id="tag4" style="background:#5ab7ff">⚠️ 安全提醒</div>
        <div class="safety-box" id="safetyBox" style="opacity:0">
          <div class="safety-text">🔊 {safety}</div>
        </div>
        <div class="benefit-text" id="benefitText" style="opacity:0; margin-top:16px">
          ✨ {benefit}
        </div>
      </div>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});

      // Scene 1: Title
      tl.from("#titleMain", {{ opacity: 0, y: -60, scale: 0.8, duration: 0.8, ease: "back.out(1.5)" }}, 0);
      tl.to("#daySub", {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }}, 1.2);
      tl.to("#titleMain", {{ scale: 1.03, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 1.8);

      // Scene 2: Game Name entrance
      tl.to("#scene2", {{ opacity: 1, duration: 0.3 }}, 3.5);
      tl.from("#gameName", {{ opacity: 0, scale: 0.3, rotation: -10, duration: 0.8, ease: "elastic.out(1.2, 0.4)" }}, 3.6);
      tl.to("#ageBadge", {{ opacity: 1, y: 0, duration: 0.5, ease: "bounce.out" }}, 4.2);

      // Scene 3: Materials + How to Play
      tl.to("#scene3", {{ opacity: 1, duration: 0.3 }}, 7);
      tl.from("#tag3", {{ opacity: 0, y: -20, duration: 0.4, ease: "power2.out" }}, 7.1);
      tl.to("#matText", {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 7.5);
      tl.to("#stepText", {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 8.2);
      tl.to(".highlight", {{ scale: 1.1, color: "#ff4a6a", duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 9.0);

      // Scene 4: Safety + Benefit
      tl.to("#scene4", {{ opacity: 1, duration: 0.3 }}, 11);
      tl.from("#tag4", {{ opacity: 0, x: -30, duration: 0.4, ease: "power2.out" }}, 11.1);
      tl.to("#safetyBox", {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.2)" }}, 11.5);
      tl.to("#benefitText", {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 12.5);
      tl.to({{}}, {{ duration: 1.5 }}, 13.5);

      window.__timelines["game-{game_id}"] = tl;
    </script>
  </body>
</html>
'''


def generate_video(game, day=None):
    """Generate Hyperframes composition HTML for a game."""
    if day is None:
        day = game["id"]

    html = COMPOSITION_TEMPLATE.format(
        game_id=game["id"],
        game_name=game["name"],
        age_min=game["age_min"],
        age_max=game["age_max"],
        materials=game["materials"],
        description=game["description"],
        safety=game["safety"],
        benefit=game["benefit"],
        icon=game["icon"],
        day=day,
    )

    compositions_dir = PROJECT_DIR / "compositions"
    compositions_dir.mkdir(exist_ok=True)

    output_path = compositions_dir / f"game-{game['id']:02d}.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def generate_all(day_start=1):
    """Generate compositions for all games."""
    games = load_games()
    print(f"📝 產生 {len(games)} 個遊戲影片模板...")
    for i, game in enumerate(games):
        path = generate_video(game, day=day_start + i)
        print(f"   ✅ {game['name']} → {path.name}")
    print(f"\n共產生 {len(games)} 個 HTML 組合")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="每日遊戲處方簽 - 影片產生器")
    parser.add_argument("action", choices=["list", "generate", "render-all", "status"],
                       default="list", nargs="?")
    parser.add_argument("--game-id", type=int, help="指定遊戲 ID")
    parser.add_argument("--day-start", type=int, default=1, help="起始天數")
    args = parser.parse_args()

    if args.action == "list":
        games = load_games()
        print(f"📋 共 {len(games)} 個遊戲：")
        print()
        for g in games:
            age_range = f"{g['age_min']}-{g['age_max']}m"
            print(f"  #{g['id']:02d} {g['icon']} {g['name']:12s} ({age_range:8s}) {g['materials']}")

    elif args.action == "generate":
        if args.game_id:
            games = load_games()
            game = next((g for g in games if g["id"] == args.game_id), None)
            if game:
                path = generate_video(game)
                print(f"✅ 已產生: {path}")
            else:
                print(f"❌ 找不到遊戲 ID: {args.game_id}")
        else:
            generate_all(day_start=args.day_start)

    elif args.action == "render-all":
        print("請在專案目錄執行: npm run render")
        print("（Hyperframes 會自動找到 compositions/ 下的檔案）")

    elif args.action == "status":
        compositions_dir = PROJECT_DIR / "compositions"
        renders_dir = PROJECT_DIR / "renders"
        comps = list(compositions_dir.glob("*.html")) if compositions_dir.exists() else []
        renders = list(renders_dir.glob("*.mp4")) if renders_dir.exists() else []
        print(f"📊 狀態")
        print(f"  遊戲資料庫: {len(load_games())} 個")
        print(f"  已產生 HTML: {len(comps)} 個")
        print(f"  已渲染 MP4: {len(renders)} 個")


if __name__ == "__main__":
    main()
