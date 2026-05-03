#!/usr/bin/env python3
"""
Generate HyperFrames compositions for the daily game prescription series.

The same template is used for index.html and every compositions/game-XX.html
file. Each generated file embeds one game as window._gameData near the top of
the page so the renderer has no external data dependency.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
GAMES_FILE = PROJECT_DIR / "games.json"
COMPOSITIONS_DIR = PROJECT_DIR / "compositions"
INDEX_HTML = PROJECT_DIR / "index.html"
INDEX_BACKUP = PROJECT_DIR / "index-backup.html"


TEMPLATE = """<!doctype html>
<html lang="zh-Hant-TW">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window._gameData = __GAME_DATA_JSON__;
    </script>
    <style>
      * {
        box-sizing: border-box;
      }

      html,
      body {
        width: 1080px;
        height: 1920px;
        margin: 0;
        overflow: hidden;
        background: #ffe0e6;
        font-family: "Noto Sans TC", "Microsoft JhengHei", system-ui, sans-serif;
      }

      body {
        color: #333;
      }

      [data-composition-id="main"] {
        position: relative;
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        background:
          radial-gradient(circle at 16% 12%, rgba(255, 216, 77, 0.45), transparent 22%),
          radial-gradient(circle at 88% 22%, rgba(84, 216, 168, 0.38), transparent 24%),
          linear-gradient(155deg, #ffe0e6 0%, #fff2c9 42%, #d2ebff 100%);
      }

      .ambient {
        position: absolute;
        inset: 0;
        pointer-events: none;
        z-index: 0;
      }

      .dot,
      .star {
        position: absolute;
        display: grid;
        place-items: center;
        color: #fff;
        text-shadow: 0 3px 0 rgba(51, 51, 51, 0.28);
        filter: drop-shadow(0 16px 24px rgba(51, 51, 51, 0.12));
      }

      .dot {
        width: 34px;
        height: 34px;
        border-radius: 999px;
        background: #5ab7ff;
      }

      .dot-a { left: 82px; top: 164px; background: #ff6b8a; }
      .dot-b { left: 932px; top: 342px; background: #54d8a8; }
      .dot-c { left: 142px; top: 1572px; background: #ffd84d; }
      .dot-d { left: 876px; top: 1492px; background: #5ab7ff; }

      .star {
        width: 54px;
        height: 54px;
        font-size: 44px;
      }

      .star-a { left: 138px; top: 286px; }
      .star-b { left: 838px; top: 204px; }
      .star-c { left: 786px; top: 1612px; }
      .star-d { left: 230px; top: 1428px; }

      .stage {
        position: absolute;
        inset: 0;
        z-index: 2;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 34px;
        padding: 170px 86px 360px;
        text-align: center;
        opacity: 0;
        transform: scale(0.8);
        transform-origin: center center;
      }

      .stage-top {
        justify-content: flex-start;
        padding-top: 220px;
      }

      .stage-roomy {
        gap: 48px;
      }

      .kicker {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 74px;
        padding: 12px 34px;
        border-radius: 999px;
        background: #333;
        color: #fff;
        font-size: 34px;
        font-weight: 900;
        line-height: 1.2;
        box-shadow: 0 10px 0 rgba(51, 51, 51, 0.12);
      }

      .title {
        margin: 0;
        color: #ff6b8a;
        font-size: 112px;
        font-weight: 900;
        line-height: 1.08;
        letter-spacing: 0;
        text-shadow:
          0 6px 0 #fff,
          0 11px 0 rgba(51, 51, 51, 0.14),
          0 28px 42px rgba(255, 107, 138, 0.26);
      }

      .title-tight {
        font-size: 96px;
      }

      .headline {
        margin: 0;
        color: #333;
        font-size: 82px;
        font-weight: 900;
        line-height: 1.15;
        letter-spacing: 0;
      }

      .outlined {
        color: #fff;
        -webkit-text-stroke: 9px #333;
        paint-order: stroke fill;
        text-shadow: 0 18px 0 rgba(51, 51, 51, 0.12);
      }

      .question-icon {
        width: 230px;
        height: 230px;
        display: grid;
        place-items: center;
        border-radius: 64px;
        background: #ffd84d;
        color: #333;
        font-size: 158px;
        font-weight: 900;
        box-shadow: 0 18px 0 rgba(51, 51, 51, 0.12), 0 26px 46px rgba(255, 216, 77, 0.34);
      }

      .brand-lockup {
        position: relative;
        display: grid;
        gap: 26px;
        justify-items: center;
      }

      .brand-pill {
        display: inline-flex;
        padding: 16px 36px;
        border: 6px solid #333;
        border-radius: 999px;
        background: #fff;
        color: #333;
        font-size: 36px;
        font-weight: 900;
        box-shadow: 0 12px 0 rgba(51, 51, 51, 0.14);
      }

      .game-icon {
        display: grid;
        place-items: center;
        width: 340px;
        height: 340px;
        border: 8px solid #333;
        border-radius: 78px;
        background: #fff;
        font-size: 198px;
        box-shadow: 0 20px 0 rgba(51, 51, 51, 0.14), 0 30px 54px rgba(90, 183, 255, 0.26);
      }

      .game-name {
        max-width: 900px;
        margin: 0;
        color: #ff6b8a;
        font-size: 104px;
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: 0;
        text-shadow:
          0 5px 0 #fff,
          0 10px 0 rgba(51, 51, 51, 0.12);
      }

      .age-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 86px;
        padding: 14px 42px;
        border: 6px solid #333;
        border-radius: 999px;
        background: #5ab7ff;
        color: #fff;
        font-size: 42px;
        font-weight: 900;
        line-height: 1.2;
        box-shadow: 0 12px 0 rgba(51, 51, 51, 0.14);
      }

      .material-grid,
      .review-grid {
        width: 100%;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 22px;
      }

      .material-card,
      .review-card {
        min-height: 250px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 18px;
        padding: 24px 20px;
        border: 6px solid #333;
        border-radius: 28px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 12px 0 rgba(51, 51, 51, 0.12);
      }

      .material-card:nth-child(1),
      .review-card:nth-child(1) {
        background: #fff6c7;
      }

      .material-card:nth-child(2),
      .review-card:nth-child(2) {
        background: #dff3ff;
      }

      .material-card:nth-child(3),
      .review-card:nth-child(3) {
        background: #dcfff2;
      }

      .card-icon {
        font-size: 76px;
        line-height: 1;
      }

      .card-title {
        color: #333;
        font-size: 34px;
        font-weight: 900;
        line-height: 1.18;
      }

      .play-step-wrap {
        position: relative;
        width: 100%;
        min-height: 520px;
        display: grid;
        place-items: center;
      }

      .play-step {
        position: absolute;
        left: 0;
        right: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 330px;
        padding: 42px;
        border: 7px solid #333;
        border-radius: 40px;
        background: rgba(255, 255, 255, 0.88);
        color: #333;
        font-size: 58px;
        font-weight: 900;
        line-height: 1.26;
        box-shadow: 0 16px 0 rgba(51, 51, 51, 0.12);
        opacity: 0;
      }

      .step-count {
        position: absolute;
        left: 34px;
        top: -34px;
        display: grid;
        place-items: center;
        width: 88px;
        height: 88px;
        border: 6px solid #333;
        border-radius: 999px;
        background: #ff6b8a;
        color: #fff;
        font-size: 40px;
        font-weight: 900;
      }

      .alert-panel,
      .benefit-panel {
        position: relative;
        width: 100%;
        min-height: 520px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 34px;
        padding: 54px;
        border: 8px solid #333;
        border-radius: 48px;
        background: rgba(255, 255, 255, 0.84);
        box-shadow: 0 18px 0 rgba(51, 51, 51, 0.13);
      }

      .alert-panel::before {
        content: "";
        position: absolute;
        inset: -24px;
        border-radius: 66px;
        background: radial-gradient(circle, rgba(255, 216, 77, 0.7), transparent 62%);
        z-index: -1;
      }

      .alert-icon,
      .benefit-icon {
        font-size: 136px;
        line-height: 1;
      }

      .alert-text,
      .benefit-text {
        color: #333;
        font-size: 58px;
        font-weight: 900;
        line-height: 1.28;
      }

      .benefit-panel {
        background: #dcfff2;
      }

      .benefit-stars {
        position: absolute;
        inset: 0;
        pointer-events: none;
      }

      .benefit-stars span {
        position: absolute;
        font-size: 58px;
        filter: drop-shadow(0 8px 0 rgba(51, 51, 51, 0.1));
      }

      .benefit-stars span:nth-child(1) { left: 94px; top: 72px; }
      .benefit-stars span:nth-child(2) { right: 100px; top: 120px; }
      .benefit-stars span:nth-child(3) { left: 158px; bottom: 96px; }
      .benefit-stars span:nth-child(4) { right: 152px; bottom: 76px; }

      .cta-wave {
        font-size: 168px;
        line-height: 1;
        transform-origin: 70% 70%;
      }

      .cta-text {
        display: grid;
        gap: 22px;
        justify-items: center;
      }

      .cta-line {
        display: inline-flex;
        padding: 18px 40px;
        border: 7px solid #333;
        border-radius: 999px;
        background: #ff6b8a;
        color: #fff;
        font-size: 58px;
        font-weight: 900;
        line-height: 1.15;
        box-shadow: 0 12px 0 rgba(51, 51, 51, 0.14);
      }

      .cta-line.secondary {
        background: #5ab7ff;
        font-size: 46px;
      }

      .end-card {
        width: 100%;
        display: grid;
        gap: 38px;
        justify-items: center;
      }

      .series-mark {
        width: 300px;
        height: 300px;
        display: grid;
        place-items: center;
        border: 8px solid #333;
        border-radius: 74px;
        background: #fff;
        font-size: 160px;
        box-shadow: 0 18px 0 rgba(51, 51, 51, 0.14);
      }

      .footer-brand {
        color: #333;
        font-size: 48px;
        font-weight: 900;
        line-height: 1.25;
      }

      .caption {
        position: absolute;
        left: 70px;
        right: 70px;
        bottom: 300px;
        z-index: 10;
        min-height: 92px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px 18px;
        color: #fff;
        -webkit-text-stroke: 7px #111;
        paint-order: stroke fill;
        font-size: 36px;
        font-weight: 900;
        line-height: 1.22;
        text-align: center;
        letter-spacing: 0;
        opacity: 0;
      }

      .progress {
        position: absolute;
        left: 80px;
        right: 80px;
        bottom: 170px;
        z-index: 12;
        height: 20px;
        border: 4px solid #333;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.72);
        overflow: hidden;
      }

      .progress-fill {
        width: 100%;
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #ff6b8a, #ffd84d, #54d8a8, #5ab7ff);
        transform: scaleX(0);
        transform-origin: left center;
      }
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="75"
      data-width="1080"
      data-height="1920"
    >
      <div class="ambient" data-layout-ignore>
        <span id="dotA" class="dot dot-a"></span>
        <span id="dotB" class="dot dot-b"></span>
        <span id="dotC" class="dot dot-c"></span>
        <span id="dotD" class="dot dot-d"></span>
        <span id="starA" class="star star-a">✦</span>
        <span id="starB" class="star star-b">✦</span>
        <span id="starC" class="star star-c">✦</span>
        <span id="starD" class="star star-d">✦</span>
      </div>

      <section id="stagePain" class="stage clip" data-start="0" data-duration="3" data-track-index="0">
        <div id="questionIcon" class="question-icon clip" data-start="0" data-duration="3" data-track-index="101">?</div>
        <h1 class="headline outlined clip" data-start="0" data-duration="3" data-track-index="102">今天陪寶寶玩什麼？</h1>
      </section>

      <section id="stageBrand" class="stage stage-roomy clip" data-start="3" data-duration="3" data-track-index="0">
        <div class="brand-lockup">
          <div class="brand-pill clip" data-start="3" data-duration="3" data-track-index="103">親子 1 分鐘</div>
          <h1 id="brandTitle" class="title clip" data-start="3" data-duration="3" data-track-index="104">每日遊戲<br />處方簽</h1>
        </div>
      </section>

      <section id="stageTopic" class="stage clip" data-start="6" data-duration="4" data-track-index="0">
        <div id="gameIcon" class="game-icon clip" data-start="6" data-duration="4" data-track-index="105"></div>
        <h2 id="gameName" class="game-name clip" data-start="6" data-duration="4" data-track-index="106"></h2>
        <div id="ageBadge" class="age-badge clip" data-start="6" data-duration="4" data-track-index="107"></div>
      </section>

      <section id="stageMaterials" class="stage stage-top clip" data-start="10" data-duration="8" data-track-index="0">
        <div class="kicker">你需要準備</div>
        <div id="materialGrid" class="material-grid"></div>
      </section>

      <section id="stagePlay" class="stage stage-top clip" data-start="18" data-duration="10" data-track-index="0">
        <div class="kicker">怎麼玩</div>
        <div id="playStepWrap" class="play-step-wrap"></div>
      </section>

      <section id="stageSafety" class="stage clip" data-start="28" data-duration="10" data-track-index="0">
        <div id="alertPanel" class="alert-panel clip" data-start="28" data-duration="10" data-track-index="108">
          <div class="alert-icon">⚠️</div>
          <div id="safetyText" class="alert-text"></div>
        </div>
      </section>

      <section id="stageBenefit" class="stage clip" data-start="38" data-duration="10" data-track-index="0">
        <div id="benefitPanel" class="benefit-panel clip" data-start="38" data-duration="10" data-track-index="109">
          <div class="benefit-stars">
            <span id="benefitStar1">✦</span>
            <span id="benefitStar2">✦</span>
            <span id="benefitStar3">✦</span>
            <span id="benefitStar4">✦</span>
          </div>
          <div class="benefit-icon">✨</div>
          <div id="benefitText" class="benefit-text"></div>
        </div>
      </section>

      <section id="stageReview" class="stage stage-top clip" data-start="48" data-duration="7" data-track-index="0">
        <div class="kicker">重點回顧</div>
        <div id="reviewGrid" class="review-grid"></div>
      </section>

      <section id="stageCta" class="stage clip" data-start="55" data-duration="10" data-track-index="0">
        <div id="ctaWave" class="cta-wave clip" data-start="55" data-duration="10" data-track-index="110">👋</div>
        <div class="cta-text">
          <div class="cta-line clip" data-start="55" data-duration="10" data-track-index="111">明天見</div>
          <div class="cta-line secondary clip" data-start="55" data-duration="10" data-track-index="112">記得按讚訂閱</div>
        </div>
      </section>

      <section id="stageOutro" class="stage clip" data-start="65" data-duration="10" data-track-index="0">
        <div class="end-card">
          <div class="series-mark clip" data-start="65" data-duration="10" data-track-index="113">🎲</div>
          <h1 class="title title-tight clip" data-start="65" data-duration="10" data-track-index="114">每日遊戲<br />處方簽</h1>
          <div class="footer-brand clip" data-start="65" data-duration="10" data-track-index="115">每天一個小遊戲<br />把陪伴變成習慣</div>
        </div>
      </section>

      <div id="captionPain" class="caption clip" data-start="0" data-duration="3" data-track-index="20">今天陪寶寶玩什麼？</div>
      <div id="captionBrand" class="caption clip" data-start="3" data-duration="3" data-track-index="20">每日遊戲處方簽</div>
      <div id="captionTopic" class="caption clip" data-start="6" data-duration="4" data-track-index="20"></div>
      <div id="captionMaterials" class="caption clip" data-start="10" data-duration="8" data-track-index="20"></div>
      <div id="captionPlay1" class="caption clip" data-start="18" data-duration="3" data-track-index="20"></div>
      <div id="captionPlay2" class="caption clip" data-start="21" data-duration="3" data-track-index="20"></div>
      <div id="captionPlay3" class="caption clip" data-start="24" data-duration="3" data-track-index="20"></div>
      <div id="captionPlay4" class="caption clip" data-start="27" data-duration="1" data-track-index="20"></div>
      <div id="captionSafety" class="caption clip" data-start="28" data-duration="10" data-track-index="20"></div>
      <div id="captionBenefit" class="caption clip" data-start="38" data-duration="10" data-track-index="20"></div>
      <div id="captionReview" class="caption clip" data-start="48" data-duration="7" data-track-index="20">重點回顧：材料、玩法、安全提醒</div>
      <div id="captionCta" class="caption clip" data-start="55" data-duration="10" data-track-index="20">明天見，記得按讚訂閱</div>
      <div id="captionOutro" class="caption clip" data-start="65" data-duration="10" data-track-index="20">每日遊戲處方簽，每天陪寶寶玩一點</div>

      <div class="progress clip" data-start="0" data-duration="75" data-track-index="30">
        <div id="progressFill" class="progress-fill"></div>
      </div>
    </div>

    <script>
      window.__timelines = window.__timelines || {};

      const game = window._gameData;
      const stages = [
        { id: "stagePain", start: 0, duration: 3, caption: "今天陪寶寶玩什麼？" },
        { id: "stageBrand", start: 3, duration: 3, caption: "每日遊戲處方簽" },
        { id: "stageTopic", start: 6, duration: 4, caption: "今天玩：" + game.name + "，適合 " + game.age_min + " 到 " + game.age_max + " 個月" },
        { id: "stageMaterials", start: 10, duration: 8, caption: "你需要準備：" + game.materials },
        { id: "stagePlay", start: 18, duration: 10, caption: game.description },
        { id: "stageSafety", start: 28, duration: 10, caption: "安全提醒：" + game.safety },
        { id: "stageBenefit", start: 38, duration: 10, caption: "發展好處：" + game.benefit },
        { id: "stageReview", start: 48, duration: 7, caption: "重點回顧：材料、玩法、安全提醒" },
        { id: "stageCta", start: 55, duration: 10, caption: "明天見，記得按讚訂閱" },
        { id: "stageOutro", start: 65, duration: 10, caption: "每日遊戲處方簽，每天陪寶寶玩一點" }
      ];

      const materialIconSet = ["🧸", "🧺", "✨"];

      function splitMaterials(value) {
        const cleaned = String(value || "無").replace(/[()（）]/g, " ");
        const parts = cleaned.split(/[、,，或與和]/).map((part) => part.trim()).filter(Boolean);
        return (parts.length ? parts : ["無"]).slice(0, 3);
      }

      function splitSteps(value) {
        const source = String(value || "").replace(/[「」]/g, "");
        const parts = source.split(/[，。；;]/).map((part) => part.trim()).filter(Boolean);
        if (parts.length >= 3) {
          return parts.slice(0, 4);
        }
        if (parts.length === 2) {
          return [parts[0], parts[1], "觀察寶寶反應，跟著寶寶的節奏互動"];
        }
        return [source || "陪寶寶一起玩", "動作放慢，給寶寶時間回應", "用微笑和聲音鼓勵寶寶"];
      }

      function fitText(text, maxLength) {
        const value = String(text || "");
        return value.length > maxLength ? value.slice(0, maxLength - 1) + "…" : value;
      }

      const materials = splitMaterials(game.materials);
      const steps = splitSteps(game.description);
      const reviewItems = [
        { icon: game.icon || "🎲", title: fitText(game.name, 8) },
        { icon: "🧺", title: fitText(game.materials, 8) },
        { icon: "🛡️", title: fitText(game.safety, 8) }
      ];

      document.getElementById("gameIcon").textContent = game.icon || "🎲";
      document.getElementById("gameName").textContent = game.name;
      document.getElementById("ageBadge").textContent = "👶 " + game.age_min + "-" + game.age_max + " 個月";
      document.getElementById("safetyText").textContent = game.safety;
      document.getElementById("benefitText").textContent = game.benefit;
      document.getElementById("captionTopic").textContent = stages[2].caption;
      document.getElementById("captionMaterials").textContent = stages[3].caption;
      document.getElementById("captionSafety").textContent = stages[5].caption;
      document.getElementById("captionBenefit").textContent = stages[6].caption;

      const materialGrid = document.getElementById("materialGrid");
      for (let index = 0; index < 3; index += 1) {
        const card = document.createElement("div");
        card.className = "material-card clip";
        card.setAttribute("data-start", "10");
        card.setAttribute("data-duration", "8");
        card.setAttribute("data-track-index", String(120 + index));
        card.innerHTML = '<div class="card-icon">' + (index === 0 ? (game.icon || materialIconSet[index]) : materialIconSet[index]) + '</div><div class="card-title">' + fitText(materials[index] || "親子陪伴", 8) + '</div>';
        materialGrid.appendChild(card);
      }

      const playStepWrap = document.getElementById("playStepWrap");
      for (let index = 0; index < 4; index += 1) {
        const step = document.createElement("div");
        step.id = "playStep" + (index + 1);
        step.className = "play-step clip";
        step.setAttribute("data-start", String(18 + index * 3));
        step.setAttribute("data-duration", index === 3 ? "1" : "3");
        step.setAttribute("data-track-index", String(40 + index));
        step.innerHTML = '<span class="step-count">' + (index + 1) + '</span><span>' + fitText(steps[index] || "陪寶寶一起互動", 28) + '</span>';
        playStepWrap.appendChild(step);
        const caption = document.getElementById("captionPlay" + (index + 1));
        if (caption) caption.textContent = steps[index] || stages[4].caption;
      }

      const reviewGrid = document.getElementById("reviewGrid");
      for (let index = 0; index < reviewItems.length; index += 1) {
        const item = reviewItems[index];
        const card = document.createElement("div");
        card.className = "review-card clip";
        card.setAttribute("data-start", "48");
        card.setAttribute("data-duration", "7");
        card.setAttribute("data-track-index", String(130 + index));
        card.innerHTML = '<div class="card-icon">' + item.icon + '</div><div class="card-title">' + item.title + '</div>';
        reviewGrid.appendChild(card);
      }

      const tl = gsap.timeline({ paused: true });
      gsap.set(".stage", { opacity: 0, scale: 0.8 });
      gsap.set(".caption", { opacity: 0, y: 18 });
      gsap.set("#stagePain", { opacity: 1, scale: 1 });

      function stageIn(selector, at, easeName) {
        tl.fromTo(selector, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.46, ease: easeName || "back.out(1.45)" }, at);
      }

      function stageOut(selector, at) {
        tl.to(selector, { opacity: 0, scale: 0.8, duration: 0.34, ease: "power2.in" }, at);
      }

      function captionIn(selector, at) {
        tl.fromTo(selector, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.22, ease: "power2.out" }, at + 0.1);
      }

      function captionOut(selector, at) {
        tl.to(selector, { opacity: 0, y: -12, duration: 0.2, ease: "power2.in" }, at - 0.24);
      }

      for (let index = 0; index < stages.length; index += 1) {
        const stage = stages[index];
        const captionId = index === 0 ? "captionPain" : index === 1 ? "captionBrand" : index === 2 ? "captionTopic" : index === 3 ? "captionMaterials" : index === 4 ? "captionPlay1" : index === 5 ? "captionSafety" : index === 6 ? "captionBenefit" : index === 7 ? "captionReview" : index === 8 ? "captionCta" : "captionOutro";
        if (index > 0) stageIn("#" + stage.id, stage.start, index === 1 || index === 2 ? "bounce.out" : "back.out(1.3)");
        captionIn("#" + captionId, stage.start);
        if (index < stages.length - 1) {
          stageOut("#" + stage.id, stage.start + stage.duration - 0.38);
          captionOut("#" + captionId, stage.start + stage.duration);
        }
      }

      tl.from("#questionIcon", { y: -60, rotation: -24, duration: 0.72, ease: "bounce.out" }, 0.18);
      tl.to("#questionIcon", { rotation: 360, duration: 2.2, ease: "sine.inOut" }, 0.5);
      tl.from("#stagePain .headline", { y: 58, opacity: 0, duration: 0.56, ease: "back.out(1.5)" }, 0.52);

      tl.from("#brandTitle", { y: 90, opacity: 0, scale: 0.62, duration: 0.72, ease: "bounce.out" }, 3.14);
      tl.from(".brand-pill", { y: -36, opacity: 0, duration: 0.44, ease: "back.out(1.4)" }, 3.08);
      tl.to(["#starA", "#starB", "#starC", "#starD"], { opacity: 0.32, scale: 0.7, duration: 0.18, yoyo: true, repeat: 5, stagger: 0.12, ease: "sine.inOut" }, 3.18);

      tl.from("#gameIcon", { y: -70, rotation: -8, opacity: 0, scale: 0.58, duration: 0.7, ease: "back.out(1.6)" }, 6.14);
      tl.from("#gameName", { y: 50, opacity: 0, duration: 0.54, ease: "back.out(1.3)" }, 6.72);
      tl.from("#ageBadge", { y: 34, opacity: 0, duration: 0.42, ease: "bounce.out" }, 7.12);

      tl.from(".material-card", { y: 70, opacity: 0, scale: 0.74, duration: 0.52, stagger: 0.18, ease: "back.out(1.45)" }, 10.78);
      for (let index = 0; index < 4; index += 1) {
        const selector = "#playStep" + (index + 1);
        const start = 18 + index * 3;
        tl.fromTo(selector, { opacity: 0, y: 50, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(1.25)" }, start + 0.15);
        tl.to(selector, { opacity: 0, y: -34, scale: 0.92, duration: 0.24, ease: "power2.in" }, start + (index === 3 ? 0.76 : 2.7));
        if (index > 0) {
          captionIn("#captionPlay" + (index + 1), start);
          captionOut("#captionPlay" + (index + 1), start + (index === 3 ? 1 : 3));
        }
      }

      tl.from("#alertPanel", { scale: 0.72, opacity: 0, duration: 0.62, ease: "back.out(1.25)" }, 28.2);
      tl.to("#alertPanel", { boxShadow: "0 18px 0 rgba(51,51,51,0.13), 0 0 68px rgba(255,216,77,0.95)", duration: 0.7, yoyo: true, repeat: 8, ease: "sine.inOut" }, 28.8);

      tl.from("#benefitPanel", { y: 74, opacity: 0, scale: 0.82, duration: 0.62, ease: "back.out(1.3)" }, 38.16);
      tl.to(["#benefitStar1", "#benefitStar2", "#benefitStar3", "#benefitStar4"], { y: -34, opacity: 0.2, rotation: 28, scale: 1.25, duration: 1.1, yoyo: true, repeat: 5, stagger: 0.14, ease: "sine.inOut" }, 38.7);

      tl.from(".review-card", { y: 68, opacity: 0, scale: 0.76, duration: 0.5, stagger: 0.16, ease: "back.out(1.45)" }, 48.72);
      tl.from("#ctaWave", { y: -42, opacity: 0, scale: 0.55, duration: 0.48, ease: "bounce.out" }, 55.24);
      tl.to("#ctaWave", { rotation: 18, duration: 0.32, yoyo: true, repeat: 8, ease: "sine.inOut" }, 56);
      tl.from(".cta-line", { x: -60, opacity: 0, duration: 0.44, stagger: 0.18, ease: "back.out(1.35)" }, 55.62);
      tl.from(".series-mark", { rotation: -12, opacity: 0, scale: 0.6, duration: 0.62, ease: "back.out(1.4)" }, 65.22);
      tl.from("#stageOutro .title", { y: 48, opacity: 0, duration: 0.54, ease: "back.out(1.2)" }, 65.72);
      tl.from(".footer-brand", { y: 36, opacity: 0, duration: 0.48, ease: "power2.out" }, 66.16);
      tl.to("#progressFill", { scaleX: 1, duration: 75, ease: "none" }, 0);
      tl.to(["#dotA", "#dotB", "#dotC", "#dotD"], { y: -22, duration: 2.8, yoyo: true, repeat: 26, stagger: 0.2, ease: "sine.inOut" }, 0);
      tl.to(["#starA", "#starB", "#starC", "#starD"], { rotation: 360, duration: 9, repeat: 8, ease: "none" }, 0);

      window.__timelines["main"] = tl;

      function createDing(context, startTime, panStart, panEnd) {
        const oscillator = context.createOscillator();
        const gain = context.createGain();
        const panner = context.createStereoPanner();
        oscillator.type = "sine";
        oscillator.frequency.setValueAtTime(880, startTime);
        oscillator.frequency.exponentialRampToValueAtTime(1320, startTime + 0.18);
        gain.gain.setValueAtTime(0.0001, startTime);
        gain.gain.exponentialRampToValueAtTime(0.12, startTime + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.42);
        panner.pan.setValueAtTime(panStart, startTime);
        panner.pan.linearRampToValueAtTime(panEnd, startTime + 0.42);
        oscillator.connect(gain);
        gain.connect(panner);
        panner.connect(context.destination);
        oscillator.start(startTime);
        oscillator.stop(startTime + 0.45);
      }

      function startBackgroundMusic() {
        if (window.__dailyGameAudioStarted) return;
        window.__dailyGameAudioStarted = true;
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        // 繞過瀏覽器自動播放阻擋
        if (ctx.state === "suspended") ctx.resume();
        const masterGain = ctx.createGain();
        masterGain.gain.setValueAtTime(0.02, ctx.currentTime);
        masterGain.connect(ctx.destination);

        // 溫柔和弦進行: C - G - Am - F (I-V-vi-IV)
        const chords = [
          [261.63, 329.63, 392.00],
          [392.00, 493.88, 587.33],
          [440.00, 523.25, 659.25],
          [349.23, 440.00, 523.25],
        ];
        const beat = 2;
        const totalBeats = Math.ceil(78 / beat);

        for (let b = 0; b < totalBeats; b++) {
          const chord = chords[b % chords.length];
          const t = ctx.currentTime + b * beat;
          for (let n = 0; n < 3; n++) {
            const osc = ctx.createOscillator();
            const g = ctx.createGain();
            osc.type = "triangle";
            osc.frequency.setValueAtTime(chord[n], t);
            g.gain.setValueAtTime(0.0001, t);
            g.gain.exponentialRampToValueAtTime(0.035, t + 0.06);
            g.gain.exponentialRampToValueAtTime(0.03, t + 1.6);
            g.gain.linearRampToValueAtTime(0.0001, t + 1.9);
            osc.connect(g);
            g.connect(masterGain);
            osc.start(t);
            osc.stop(t + 2.0);
          }
        }

        // 階段切換提示音（左右聲道交錯）
        for (let i = 0; i < stages.length; i++) {
          const t = ctx.currentTime + stages[i].start + 0.12;
          const osc = ctx.createOscillator();
          const g = ctx.createGain();
          const pan = ctx.createStereoPanner();
          osc.type = "sine";
          osc.frequency.setValueAtTime(880, t);
          osc.frequency.exponentialRampToValueAtTime(1320, t + 0.18);
          g.gain.setValueAtTime(0.0001, t);
          g.gain.exponentialRampToValueAtTime(0.10, t + 0.02);
          g.gain.exponentialRampToValueAtTime(0.0001, t + 0.42);
          pan.pan.setValueAtTime(-0.6 + (i % 2) * 1.2, t);
          pan.pan.linearRampToValueAtTime(0.6 - (i % 2) * 1.2, t + 0.42);
          osc.connect(g);
          g.connect(pan);
          pan.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.45);
        }
      }

      function startSpeechSequence() {
        if (window.__dailyGameSpeechStarted || !("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) return;
        window.__dailyGameSpeechStarted = true;
        let index = 0;
        function speakNext() {
          if (index >= stages.length) return;
          tl.tweenTo(stages[index].start + 0.9, { duration: 0.45, ease: "sine.inOut" });
          const utterance = new SpeechSynthesisUtterance(stages[index].caption);
          utterance.lang = "zh-TW";
          utterance.rate = 1;
          utterance.pitch = 1.08;
          utterance.volume = 0.92;
          const current = index;
          utterance.onend = function () {
            index = current + 1;
            if (index < stages.length) {
              tl.tweenTo(stages[index].start, { duration: 0.45, ease: "sine.inOut" });
              speakNext();
            }
          };
          window.speechSynthesis.speak(utterance);
        }
        speakNext();
      }

      function startPlayback() {
        startBackgroundMusic();
        startSpeechSequence();
      }

      // 自動啟動（延遲確保渲染器就緒）
      setTimeout(startPlayback, 500);
      // 互動式觸發（瀏覽器預覽用）
      window.addEventListener("pointerdown", startPlayback, { once: true });
      window.addEventListener("keydown", startPlayback, { once: true });
      window.addEventListener("hf-play", startPlayback);
    </script>
  </body>
</html>
"""


def load_games() -> list[dict]:
    with GAMES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def render_html(game: dict) -> str:
    game_json = json.dumps(game, ensure_ascii=False, indent=8)
    return TEMPLATE.replace("__GAME_DATA_JSON__", game_json)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate(index_game_id: int = 1) -> None:
    games = load_games()
    game_by_id = {int(game["id"]): game for game in games}
    index_game = game_by_id.get(index_game_id, games[0])

    write_file(INDEX_HTML, render_html(index_game))
    write_file(INDEX_BACKUP, render_html(index_game))

    COMPOSITIONS_DIR.mkdir(exist_ok=True)
    for game in games:
        path = COMPOSITIONS_DIR / f"game-{int(game['id']):02d}.html"
        write_file(path, render_html(game))

    print(f"Generated index.html, index-backup.html, and {len(games)} compositions.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Daily Game Prescription HyperFrames compositions.")
    parser.add_argument("--index-game-id", type=int, default=1, help="Game ID to embed in index.html and index-backup.html.")
    args = parser.parse_args()
    generate(index_game_id=args.index_game_id)


if __name__ == "__main__":
    main()
