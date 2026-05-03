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
    """Run OAuth setup flow."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CLIENT_SECRET_PATH.exists():
        print("=" * 60)
        print("  YouTube 上傳設定 - OAuth 授權")
        print("=" * 60)
        print()
        print("請先到 Google Cloud Console 建立 OAuth 2.0 憑證：")
        print()
        print("  1. 開啟 https://console.cloud.google.com/apis/credentials")
        print("  2. 選擇專案或建立新專案")
        print("  3. 啟用「YouTube Data API v3」")
        print("  4. 建立 OAuth 2.0 用戶端 ID (應用程式類型: 桌面應用程式)")
        print("  5. 下載 JSON 檔案")
        print(f"  6. 存放到: {CLIENT_SECRET_PATH}")
        print()
        print("下載後重新執行: python upload_youtube.py --setup")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    creds = flow.run_local_server(port=8080, open_browser=False)

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
    parser.add_argument("--title", default="每日遊戲處方簽 - 聽聲辨位", help="影片標題")
    parser.add_argument("--description", default="今天的寶寶遊戲時間！來玩「聽聲辨位」🎯\n\n#寶寶遊戲 #幼兒教育 #親子互動 #嬰兒發展", help="影片說明")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="unlisted", help="隱私設定")
    parser.add_argument("--day", type=int, help="第幾天 (自動加入標題)")
    args = parser.parse_args()

    if args.setup:
        run_setup()
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
