#!/usr/bin/env python3
"""
每日遊戲處方簽 - 每日自動執行腳本
由 cronjob 每天23:00觸發，自動渲染當日遊戲影片。
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
COMPOSITIONS_DIR = PROJECT_DIR / "compositions"
RENDERS_DIR = PROJECT_DIR / "renders"
INDEX_HTML = PROJECT_DIR / "index.html"
INDEX_BACKUP = PROJECT_DIR / "index-backup.html"
GAMES_FILE = PROJECT_DIR / "games.json"
STATUS_FILE = RENDERS_DIR / "render_status.json"


def get_today_game():
    """From day of year so it's deterministic."""
    with open(GAMES_FILE, "r", encoding="utf-8") as f:
        games = json.load(f)
    day_of_year = datetime.now().timetuple().tm_yday
    game_index = (day_of_year - 1) % len(games)
    return games[game_index], day_of_year


def log(text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {text}")


def main():
    log("🎬 每日遊戲處方簽 - 開始執行")

    game, day_num = get_today_game()
    log(f"📅 Day {day_num} → #{game['id']:02d} {game['icon']} {game['name']}")

    comp_path = COMPOSITIONS_DIR / f"game-{game['id']:02d}.html"
    if not comp_path.exists():
        log(f"❌ 找不到模板: {comp_path}")
        sys.exit(1)

    # Copy to index.html
    shutil.copy2(comp_path, INDEX_HTML)
    log(f"📄 已載入模板")

    # Render
    result = subprocess.run(
        ["npx", "--yes", "hyperframes@0.4.42", "render"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
        env={
            **os.environ,
            "PATH": f"{Path.home()}/.n/bin:{os.environ.get('PATH', '')}",
        },
    )

    if result.returncode != 0:
        log(f"❌ 渲染失敗: {result.stderr[-500:]}")
        sys.exit(1)

    # Find and rename
    RENDERS_DIR.mkdir(exist_ok=True)
    mp4_files = sorted(RENDERS_DIR.glob("*.mp4"), key=lambda f: f.stat().st_mtime)
    if not mp4_files:
        log("❌ 找不到渲染 MP4")
        sys.exit(1)

    latest = mp4_files[-1]
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_name = f"game-day{day_num:03d}-{date_str}-{game['name']}.mp4"
    output_path = RENDERS_DIR / output_name

    shutil.move(str(latest), str(output_path))
    size_mb = output_path.stat().st_size / (1024 * 1024)

    log(f"🎬 渲染完成！{output_name} ({size_mb:.1f} MB)")

    # Restore backup
    if INDEX_BACKUP.exists():
        shutil.copy2(INDEX_BACKUP, INDEX_HTML)
        log("📄 已恢復 index.html")

    # Save status for upload script
    status = {
        "date": date_str,
        "day": day_num,
        "game_id": game["id"],
        "game_name": game["name"],
        "video_path": str(output_path),
        "video_size_mb": round(size_mb, 1),
        "timestamp": datetime.now().isoformat(),
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

    log(f"📊 狀態已儲存: {STATUS_FILE}")

    # Upload to YouTube
    upload_script = PROJECT_DIR / "upload_youtube.py"
    if upload_script.exists():
        log(f"📤 正在上傳至 YouTube...")
        upload_result = subprocess.run(
            ["python3", str(upload_script), str(output_path), "--day", str(day_num), "--privacy", "unlisted"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            env={
                **os.environ,
                "PATH": f"{Path.home()}/.n/bin:{os.environ.get('PATH', '')}",
            },
        )
        if upload_result.returncode == 0:
            log(f"✅ YouTube 上傳成功！")
            # Extract YouTube URL
            for line in upload_result.stdout.split("\n"):
                if "youtu.be" in line or "youtube.com" in line:
                    log(f"   {line.strip()}")
        else:
            log(f"⚠️ YouTube 上傳失敗: {upload_result.stderr[:200]}")

    log(f"✅ 完成！")


if __name__ == "__main__":
    main()
