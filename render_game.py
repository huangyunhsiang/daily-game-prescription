#!/usr/bin/env python3
"""
Render a game prescription video and save with proper filename.

Usage:
  python render_game.py [game_id]     # Render specific game (default: random)
  python render_game.py --all          # Render all 30 games
  python render_game.py --list         # Show today's pick
"""

import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parent
GAMES_FILE = PROJECT_DIR / "games.json"
COMPOSITIONS_DIR = PROJECT_DIR / "compositions"
RENDERS_DIR = PROJECT_DIR / "renders"
INDEX_HTML = PROJECT_DIR / "index.html"
INDEX_BACKUP = PROJECT_DIR / "index-backup.html"


def load_games():
    with open(GAMES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_today_game():
    """Use game ID based on day of year so it's deterministic per day."""
    day_of_year = datetime.now().timetuple().tm_yday
    games = load_games()
    game_index = (day_of_year - 1) % len(games)
    return games[game_index]


def render_game(game, output_name=None):
    """Copy game composition to index.html and render."""
    comp_path = COMPOSITIONS_DIR / f"game-{game['id']:02d}.html"
    if not comp_path.exists():
        print(f"❌ 找不到模板: {comp_path}")
        return None

    # Copy to index.html
    shutil.copy2(comp_path, INDEX_HTML)
    print(f"📄 已載入: {game['name']}")

    # Run render
    result = subprocess.run(
        ["npm", "run", "render"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PATH": f"{Path.home()}/.n/bin:{os.environ.get('PATH', '')}"},
    )

    if result.returncode != 0:
        print(f"❌ 渲染失敗: {result.stderr}")
        return None

    # Find the rendered file
    rendered_files = list(RENDERS_DIR.glob("*.mp4"))
    if not rendered_files:
        print("❌ 找不到渲染後的 MP4")
        return None

    # Rename the latest rendered file
    latest = max(rendered_files, key=lambda f: f.stat().st_mtime)
    if output_name:
        new_path = RENDERS_DIR / output_name
        shutil.move(str(latest), str(new_path))
        print(f"🎬 輸出: {new_path}")
        return new_path

    return latest


def render_all():
    """Render all 30 games."""
    games = load_games()
    print(f"🎬 開始批次渲染 {len(games)} 個遊戲...")
    for i, game in enumerate(games):
        print(f"\n[{i+1}/{len(games)}] {game['name']}...")
        output_name = f"game-{game['id']:02d}-{game['name']}.mp4"
        result = render_game(game, output_name=output_name)
        if result:
            size_mb = result.stat().st_size / (1024 * 1024)
            print(f"   ✅ {size_mb:.1f} MB")

    # Restore backup
    if INDEX_BACKUP.exists():
        shutil.copy2(INDEX_BACKUP, INDEX_HTML)

    print(f"\n✅ 全部渲染完成！")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="遊戲處方簽 - 渲染器")
    parser.add_argument("game_id", nargs="?", type=int, help="遊戲 ID (預設: 今日隨機)")
    parser.add_argument("--all", action="store_true", help="渲染全部 30 個遊戲")
    parser.add_argument("--list", action="store_true", help="顯示今日遊戲")
    args = parser.parse_args()

    if args.list:
        game = get_today_game()
        print(f"📅 今日遊戲 (Day {datetime.now().timetuple().tm_yday}):")
        print(f"   {game['icon']} {game['name']} ({game['age_min']}-{game['age_max']}個月)")
        print(f"   道具: {game['materials']}")
        print(f"   玩法: {game['description']}")
        return

    if args.all:
        render_all()
        return

    if args.game_id:
        games = load_games()
        game = next((g for g in games if g["id"] == args.game_id), None)
        if not game:
            print(f"❌ 找不到遊戲 ID: {args.game_id}")
            sys.exit(1)
    else:
        game = get_today_game()
        print(f"📅 今日遊戲: {game['icon']} {game['name']}")

    render_game(game)


if __name__ == "__main__":
    main()
