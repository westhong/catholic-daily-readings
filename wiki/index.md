# Catholic Assistant Wiki

> 天主教靈修助理 — 想法、試驗、與記錄

## 異象 🌟
>「為神做一些事，讓神的話語更能遠傳。」
> 目標遠大，起點簡單。從每日中文讀經開始，最終建立完整的中文天主教靈修陪伴系統。

## 系統定位
> 不局限於任何一種形式。所有找到的 source，全部評估，全部納進來。
> 核心橋樑：Lectionary Number — 這是跨語言、跨禮儀傳統的統一編號。

## 系統分層架構
```
Source Layer          ← 每個 source 獨立介面（USCCB / iBreviary / FHL / ...）
         ↓
Lectionary Number    ← 核心主鍵，所有 source 靠它對齊
         ↓
Bible Translation DB  ← 各語言譯本（FHL 思高 / 和合本 / ...）
         ↓
Standard Output      ← 統一每日讀經記錄格式
         ↓
Delivery Layer       ← 可插拔（Telegram / Web / API / ...）
```

## MVP 定位
- Phase 1 MVP 與現有 cron 是**兩條獨立的工作線**
- 現有 cron 維持不變
- MVP 專注建立標準格式，用 USCCB + FHL 做出示範

## 最終目標（Public）
- 接觸教會和 source 擁有者，確認 license
- 建立一個讓所有人能使用的系統
- 結果在神手中

## 系統功能藍圖（全部）
- [ ] 聖言讀經系統（Psalm / First Reading / Gospel）
- [ ] 完整祈禱時辰（Divinum Officium — Lauds / Daytime / Vespers / Compline）
- [ ] 靈修導讀 / 默想問題
- [ ] 引導祈禱文
- [ ] 聖人日曆
- [ ] 禮儀年導覽（將臨期 / 聖誕期 / 四旬期 / 復活期）
- [ ] 多語言來源 → 繁/簡體中文輸出
- [ ] License 追蹤

## 導覽
- [[Roadmap]] — **下一步行動指南**（持續更新）
- [[Sources]] — 我們已找到的所有來源
- [[Research-Daily-Catholic-Sources]] — 來源研究報告
- [[Ideas]] — 所有待實現的想法
- [[Phase 1]] — 第一階段建設計劃（已完成）

## MVP 實作狀態 ✅
2026-04-19：USCCB + FHL 思高譯本 MVP 已完成，可產出完整每日讀經記錄（JSON）。
