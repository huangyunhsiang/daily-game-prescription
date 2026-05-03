#!/usr/bin/env python3
"""
YouTube upload script for 每日遊戲處方簽 (Daily Game Prescription).

Usage:
  python upload_youtube.py <mp4_path> [--title "TITLE"] [--description "DESC"]
  
First run (OAuth setup):
  python upload_youtube.py --setup
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_PATH = Path.home() / ".hermes" / "youtube_token.json"
CLIENT_SECRET_PATH = Path.home() / ".hermes" / "youtube_client_secret.json"


def get_authenticated_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("❌ 未授權。請先執行: python upload_youtube.py --setup")
            sys.exit(1)

        TOKEN_PATH.write_text(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def run_setup():
    """Run OAuth setup flow (supports mobile/headless via run_console)."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CLIENT_SECRET_PATH.exists():
        print("=" * 60)
        print("  YouTube 上傳設定 - OAuth 授權")
        print("=" * 60)
        print()
        print("請先用手機完成以下步驟：")
        print()
        print("  1. 在手機瀏覽器打開：")
        print("     https://console.cloud.google.com/apis/credentials")
        print()
        print("  2. 建立新專案（或選現有專案）")
        print("  3. 啟用「YouTube Data API v3」")
        print("  4. 建立「OAuth 2.0 用戶端 ID」")
        print("     → 應用程式類型選「桌面應用程式」")
        print("     → 名稱隨便填，例如「Herme Agent」")
        print()
        print("  5. 建立完成後，點「下載 JSON」")
        print()
        print(f"  6. 把下載的 JSON 檔案上傳到 Google Drive：")
        print("     → KASPER_Shared/ 資料夾")
        print("     → 重新命名為 youtube_client_secret.json")
        print()
        print("❗ 上傳完成後通知我，我來繼續下一步。")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)

    print()
    print("=" * 60)
    print("  📱 請用手機完成以下步驟：")
    print("=" * 60)
    print()

    # Use run_console for device-code-style flow
    creds = flow.run_console()

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json())
    print(f"✅ 授權成功！Token 已儲存至 {TOKEN_PATH}")


def upload_video(
    video_path,
    title="寶寶遊戲處方簽",
    description="今天的寶寶遊戲時間來了！\n#寶寶遊戲 #幼兒教育 #親子互動",
    tags=None,
    privacy_status="public",
    category_id="24",  # 24 = Entertainment
):
    if tags is None:
        tags = ["寶寶遊戲", "幼兒教育", "親子互動", "嬰兒遊戲", "每日遊戲處方簽"]

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    print(f"📤 正在上傳: {title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=video_path,
    )

    response = request.execute()
    video_id = response["id"]
    print(f"✅ 上傳成功！")
    print(f"   🔗 https://youtu.be/{video_id}")
    print(f"   📺 https://www.youtube.com/watch?v={video_id}")
    return video_id


def main():
    parser = argparse.ArgumentParser(description="YouTube 上傳工具 - 每日遊戲處方簽")
    parser.add_argument("video", nargs="?", help="MP4 影片路徑")
    parser.add_argument("--setup", action="store_true", help="執行 OAuth 授權設定")
    parser.add_argument("--download-secret", action="store_true", help="從 Google Drive 下載 client secret")
    parser.add_argument("--title", default="每日遊戲處方簽 - 聽聲辨位", help="影片標題")
    parser.add_argument("--description", default="今天的寶寶遊戲時間！來玩「聽聲辨位」🎯\n\n#寶寶遊戲 #幼兒教育 #親子互動 #嬰兒發展", help="影片說明")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="unlisted", help="隱私設定")
    parser.add_argument("--day", type=int, help="第幾天 (自動加入標題)")
    args = parser.parse_args()

    if args.setup:
        run_setup()
        return

    if args.download_secret:
        print("📥 正在從 Google Drive 下載 youtube_client_secret.json...")
        import subprocess as sp
        result = sp.run(
            ["rclone", "copy", "mydrive:KASPER_Shared/youtube_client_secret.json",
             str(CLIENT_SECRET_PATH.parent)],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and CLIENT_SECRET_PATH.exists():
            print(f"✅ 成功下載至 {CLIENT_SECRET_PATH}")
            print("📱 現在執行: python3 upload_youtube.py --setup")
        else:
            print("❌ 下載失敗。請確認已上傳至 KASPER_Shared/youtube_client_secret.json")
            print(f"   錯誤: {result.stderr[:200]}")
        return

    if not args.video:
        parser.print_help()
        print("\n請指定要上傳的影片路徑，或先執行 --setup 設定授權。")
        return

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"❌ 找不到影片: {video_path}")
        return

    title = args.title
    if args.day:
        title = f"每日遊戲處方簽 Day {args.day} - 聽聲辨位"

    upload_video(
        video_path=str(video_path),
        title=title,
        description=args.description,
        privacy_status=args.privacy,
    )


if __name__ == "__main__":
    main()
