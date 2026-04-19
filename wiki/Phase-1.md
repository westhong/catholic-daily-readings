# Phase 1 — MVP：最小可行產品

> 目標：建立一個最小、最核心的系統，證明這個架構是可行的。
> 架構要清晰，以後能擴展到多語言、多 source。
> 現有 cron 維持不變，這是另一條獨立的工作線。

## MVP 範圍

MVP 只做一件事：

**建立一個「每日讀經記錄」的標準資料格式，並用一個 source（USCCB + FHL）做出示範。**

MVP 完成後，系統能輸出：
- 日期 + 星期
- 禮儀節日名稱
- Lectionary Number
- Psalm / First Reading / Gospel 章節
- 三篇經文的繁體中文（思高譯本）+ 簡體中文

## 架構設計原則

```
Source (e.g. USCCB)          ←  資料來源，獨立的介面
    ↓
Lectionary Number 對照表    ←  跨語言對應的核心
    ↓
譯本資料庫                   ←  各語言聖經譯本（目前有 FHL 思高）
    ↓
標準化輸出格式               ←  統一的每日讀經記錄結構
    ↓
Delivery Layer               ←  可插拔，Telegram / Web / API
```

這個架構的關鍵：
- **每層是獨立的**，加新語言 / 新 source 不用改其他層
- **Lectionary Number 是唯一主鍵**，所有 source 靠它對齊
- **Delivery Layer 是最後一層**，替換不影響核心

## Phase 1 工作清單

### 1. 標準化資料格式 ✅
- [x] 設計「每日讀經記錄」的 JSON schema
- [x] 欄位：date, weekday, feast_name, lectionary_number, readings[]
- [x] readings[] 包含：type(psalm/first_reading/gospel), chapter, verse_range, bible_text_tc, bible_text_sc

### 2. 建立核心資料庫 ✅
- [x] 實作 USCCB scraper（只取 metadata，不取經文）
- [x] 實作 FHL 思高譯本 fetcher
- [x] 實作簡/繁體中文轉換（已有 FHL，確認能用）
- [x] 建立 Lectionary Number → 經文章節 的對照表

### 3. 產出 MVP ✅
- [x] 能輸出完整格式的每日讀經記錄
- [x] 能在 terminal 顯示測試結果
- [x] 能生成 JSON 格式輸出

## 進度追蹤
| 任務 | 狀態 |
|------|------|
| 標準化資料格式 | ✅ 完成 |
| 建立核心資料庫 | ✅ 完成 |
| 產出 MVP | ✅ 完成 |

## 現有資源（不動）
- 現有 cron：維持現狀，不改
- 現有 FHL script：維持現狀，不改

## 這個 MVP 的意義
完成後，證明架構可行，未來加任何新 source（iBreviary / DivineOffice / 其他語言）都在同一套架子裡做。

---

*Phase 1 已完成（2026-04-19）。下一步見 [[Roadmap]]。*
