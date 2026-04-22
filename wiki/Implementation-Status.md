# 實作狀態 — Catholic Assistant

> 更新日期：2026-04-21

---

## Phase 1 MVP ✅ (2026-04-18)

USCCB + FHL 思高譯本，單日測試記錄。

---

## Phase 2 ✅ Layer 0 基本完成，Layer 1 大量完成

### 2.0 ✅ Layer 0 Source Data

**目標**：凍存所有 USCCB `.cfm` HTML 文件。

**結果**：
- **1,741 個 `.cfm` 文件**（凍存完成）
  - 2023: 366 個（2023-01-01 ~ 2023-12-31）
  - 2024: 366 個（2024-01-01 ~ 2024-12-31）
  - 2025: 365 個（2025-01-01 ~ 2025-12-31）
  - 2026: 296 個（2026-01-01 ~ 2026-12-31）
  - 2027: 380 個（2027-01-01 ~ 2027-12-31，含多個 mass 的特殊日子）
- 存放位置：`data/usccb-calendar/raw/`

**Fetch 記錄（2026-04-21）**：
- 2023-2025 全部 1,096 個凍存檔首次完整 fetch ✅
- 2026 過去日期（2026-01-01 ~ 2026-04-21）重新 fetch（補回 Easter 預覽頁佔用的 Alleluias）✅
- 個別 404：2023-01-31、2023-05-25（USCCB URL 已修復為 Spanish URL）

**已知空殼檔**（redirect 頁）：`040226.cfm`、`122526.cfm`、`051426.cfm` 等，已識別並跳過。

### 2.1 ✅ Layer 1 Processed Data（大量完成）

**目標**：每個 `.cfm` → readings.json，包含 citation_id。

**已完成**：
- [x] 分析 1,741 個檔案的 reading 結構
- [x] 建立 Layer 1 JSON Schema（multi-source 格式）
- [x] readings.json：1,763 個日期（2023-01-01 ~ 2027-10-31）
- [x] 批量處理 1,741 個有效檔案，提取所有讀經 citation
- [x] 修補 984 個缺失段落（second_reading、verse_before_gospel、sequence 等）
- [x] 修補 Alleluias：2026 Easter 期間 + 2023-2025 新凍存檔

**readings.json 覆蓋率（2026-04-21）**：

| 年份 | 總日期 | 有 Alleluia | 缺 Alleluia | 狀態 |
|------|--------|-------------|-------------|------|
| 2023 | 365 | 282 | 83 | 🔄 待驗證 |
| 2024 | 365 | 283 | 82 | 🔄 待驗證 |
| 2025 | 365 | 285 | 80 | 🔄 待驗證 |
| 2026 past | 111 | 64 | 47 | 🔄 待驗證 |
| 2026 future | 254 | — | 21 future | 🔄 USCCB 未發佈 |
| 2027 | 303 | 98 | 205 | 🔄 待驗證 |

**缺 Alleluia 的原因**：
- Lenten 平日（USCCB 真的沒有 citation）
- Holy Week 部分日子（Christ is the light 等禮儀文字）
- 2026 future（USCCB 未發佈未來的 Alleluia）
- 部分 Easter Octave 等（parser 已準確識別）

**Multi-Source Cross-Reference（進行中）**：
- [x] CatholicGallery.org — 已確認有 2023-2027 歷史數據，URL 格式固定
- [x] CatholicOnline.org — 已確認有 2023-2027 歷史數據
- [ ] Prayla.app — 待驗證
- [ ] BibleCor.com — 待研究
- [ ] 尚未整合進 readings.json（需 browser 工具提取）

### 2.2 ⏳ Layer 2 Applied Layer

未來工作。

---

## 驗證方法

原則：**一天一天做，parser 驗證 + cross-reference + commit。**

### Parser 驗證（已完成抽樣檢查）
- 隨機抽樣 50 個日期，parser 输出版本與 JSON 記錄完全一致 ✅
- Alleluia 段落與 .cfm 凍存檔交叉比對：0 mismatches ✅

### Cross-Source 驗證（進行中）
- USCCB .cfm 是主要 source（完整）
- CatholicGallery / CatholicOnline 是 secondary sources（用於交叉確認）
- 所有 citation 只存章節引用（公共遺產，無版權）

---

## GitHub 發佈狀態（2026-04-21）

**已 push**：
- `wiki/Implementation-Status.md`（本文件）
- `wiki/Roadmap.md`
- `wiki/Data-Layers.md`
- `data/usccb-calendar/raw/`（1,741 個 .cfm 凍存檔）
- `data/lectionary/readings.json`（1,763 個日期的 Layer 1 JSON）
- `data/usccb-calendar/index/`（年度 calendar index）

**commit history**：
- `0cedb4b` Add 2023-2025 .cfm files, update readings.json Alleluias, re-fetch 2026 past dates
- `0071bb6` Complete 2023: add May 25 (Spanish URL, lect 300), Jan 31 (lect 317), Apr 17 (lect 267)
- `547031d` Add December 2026 readings: Dec 1-31, multi-source format...

---

## 下一步

- [ ] 逐一驗證缺 Alleluia 的日期（~245 個），確認是否真的沒有 citation
- [ ] 整合 CatholicGallery cross-reference 到 readings.json
- [ ] 整合 CatholicOnline cross-reference 到 readings.json
- [ ] 驗證 2027 年剩餘 205 個缺 Alleluia 的日子
- [ ] 批量處理 2027 年的額外 .cfm 文件（Ascension Thursday/Extended Pentecost 等）
- [ ] Layer 2：建立 citation_id → 各譯本章節顯示 mapping

---

*仍在積極開發中。查看 commit history：https://github.com/westhong/catholic-daily-readings/commits/main*
