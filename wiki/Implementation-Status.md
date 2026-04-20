# 實作狀態 — Catholic Assistant

> 更新日期：2026-04-19

---

## Phase 1 MVP ✅ (2026-04-18)

USCCB + FHL 思高譯本，單日測試記錄。

---

## Phase 2 — Layer 0 + Layer 1 ✅ 基本完成

### 2.0 ✅ Layer 0 Source Data

**目標**：凍存所有 USCCB `.cfm` HTML 文件。

**結果**：
- 462 個 `.cfm` 文件（2026-04 → 2027-05，共 14 個月）
- 447 個有效、15 個空殼（redirect 頁，已識別並跳過）
- 存放位置：`data/usccb-calendar/raw/`

**已知空殼檔**：`040226.cfm`、`122526.cfm`、`051426.cfm`、`051726.cfm`、`pentecost-sunday.cfm`、`062426.cfm`、`062926.cfm`、`112626.cfm` 等（共 15 個）。

**URL 異常**：`2027-05-07-050727cfm.cfm` — USCCB URL slug 本身包含 `cfm`（不是檔案副檔名）

### 2.1 ✅ Layer 1 Processed Data

**目標**：每個 `.cfm` → 一個 JSON，包含 citation_id。

**已完成**：
- [x] 分析 462 個檔案的 reading 結構
- [x] 建立 Layer 1 JSON Schema
- [x] 第一個 JSON 範例：`data/daily/2026-04-19.json`
- [x] Wiki 全面更新：Data-Layers / Roadmap / Implementation-Status / README

**JSON Schema 要點**：
- `citation_id`：標準化為 `book:chapter`（如 `acts:2`, `psalm:16`）
- `lectionary_number`：從 calendar index 帶入（不在 .cfm HTML 裡，需 cross-reference）
- `alternatives[]`：Or 區塊歸入前一 reading 的 alternatives
- `condition`：直接用 HTML label verbatim
- Sequence 的 required/optional 直接從 label 機械判斷

**Reading 結構全景**（分析 462 個檔案後）：

| 結構類型 | 例子 | 組合 |
|----------|------|------|
| 簡單平日 | 4月13日 | Reading 1 → Psalm → Alleluia → Gospel |
| 平日含第二讀經 | 4月12日 | Reading 1 → Psalm → Reading 2 → Alleluia → Gospel |
| 大節日（Verse Before）| 復活節八日 | Reading I → Psalm → Reading II → **Verse Before Gospel** → Gospel |
| Easter Sunday | 4月5日 | Reading 1 → Psalm → Reading 2 + Sequence → Alleluia → Gospel + 替代 |
| Easter Vigil | 4月4日 | Reading I-VII + Psalms + Epistle + Gospel |
| Pentecost Extended | 5月24日 | 4篇舊約 + Psalms + Epistle + Gospel |
| Assumption Vigil/Day | 8月15日 | Reading 1 → Psalm → Reading 2 → Alleluia → Gospel |

**Label 不一致問題（已知，解析器需處理）**：
- `Reading I` / `Reading 1` → 統一為 `first_reading`
- `Responsorial Psalm` / `Responsorial` → 統一為 `responsorial_psalm`
- `Verse Before the Gospel` / `Verse before the Gospel`
- `Sequence - Victimæ paschali laudes` / `Sequence -- optional` / `Sequence (Optional)` / `Sequence — Veni, Sancte Spiritus`
- `Or` / `or` / `OR` / `Or:` / `Or at afternoon or evening mass`

### 2.2 ⏳ Layer 2 Applied Layer

未來工作。

---

## GitHub 發佈狀態（2026-04-19）

**已 push**：
- `wiki/Data-Layers.md`（Layer 0/1/2 架構）
- `wiki/Implementation-Status.md`
- `wiki/Roadmap.md`
- `wiki/index.md`
- `scripts/scrape_usccb_calendar.py`（Phase 2 核心工具）
- `data/daily/2026-04-19.json`（Layer 1 模板）
- `README.md`（全面更新）

**已移除（從 GitHub 刪除）**：
- `email-drafts/`（私人來往，已徹底刪除）

---

## 下一步

- [ ] 批量生成 Layer 1 JSON（447 個有效檔案）
- [ ] 建立 citation_id → 各譯本章節顯示 mapping 表（Layer 2 準備）
- [ ] 與 GitHub remote repo 同步進度
