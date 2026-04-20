# Roadmap — 天主教每日讀經系統

> 最後更新：2026-04-19
> 方向：Agile。持續交付，不斷更新。

---

## 背景共識

我們的系統只需要各國來源的：
- ✅ 日期
- ✅ Lectionary Number（Year A/B/C + 讀經編號）
- ✅ 讀經章節（路加福音 10:25-37）
- ✅ 禮儀節日名稱

聖經經文由**我們自己的譯本**輸出（中文用 FHL思高），各國語言由對應譯本輸出。

Lectionary Number 是公共遺產，無版權問題。

---

## 數據分層架構（Phase 2 核心）

```
Layer 0 — Source Layer     原始 HTML 文件（.cfm），凍存不動
Layer 1 — Processed Layer  citation_id JSON（無版權爭議）
Layer 2 — Applied Layer   各譯本完整章節顯示（譯本方處理）
```

詳見：[[Data-Layers]]

---

## Phase 1 ✅ 已完成

**MVP：USCCB（英文） + FHL 思高譯本（繁體中文）**

- [x] 標準 JSON 輸出格式
- [x] USCCB scraper（Lectionary + 章節）
- [x] FHL 思高譯本 API（繁體中文經文）
- [x] 每日 cron 三次抓取（Psalm / First Reading / Gospel）
- [x] GitHub public repo + v1.0.0 release
- [x] CONTRIBUTING.md
- [x] Sources.md 研究清單

---

## Phase 2 🔄 即將完成：Layer 0 + Layer 1

### 2.0 ✅ Layer 0 Source Data（2026-04-19）

462 個 USCCB `.cfm` 文件，已凍存。

- 2026-04 → 2027-04（共 13 個月）
- 2027-05（練習月）
- 447 個有效、15 個空殼（redirect 頁）
- URL 404 問題已修復

### 2.1 🔄 Layer 1 Processed Data（進行中）

每個 `.cfm` → 一個 JSON（Layer 1），包含 citation_id。

- [x] 分析 462 個檔案的 reading 結構
- [x] 確認 reading label 不一致問題（Reading I / Reading 1 / Reading 2 等）
- [x] 確認 alternatives（Or 區塊）結構
- [x] 確認 lectionary_number 需從 calendar index 帶入
- [x] 建立 Layer 1 JSON Schema
- [ ] 生成第一個完整 JSON（2026-04-19 示範）
- [ ] 批量處理 447 個有效檔案
- [ ] 更新 wiki：Processed Layer JSON Schema

### 2.2 🔄 下一個：Layer 2 Applied Layer

同一個 Layer 1 JSON，針對不同譯本產生不同顯示：

- [ ] en-us（USCCB/NAB）：`Luke 24:13-35`
- [ ] zh-tw（FHL/思高）：`若望福音 24:13-35`
- [ ] zh-cn（和合本）：`路加福音 24:13-35`

---

## Phase 3 ⏳ 多語言整合

### 英語系 ✅ 已確認來源

| 來源 | 系統 | RSS/HTML |
|------|------|----------|
| **USCCB** | Mass | HTML ✅ |
| **CatholicOnline** | Mass | RSS ✅ |
| **DivineOffice.org** | Breviary | RSS ✅ |

### 其他語系（需要瀏覽器工具）

| 語系 | 優先度 | 狀態 |
|------|--------|------|
| 🇩🇪 德語（Katholisch.de） | 🔴 高 | JS 渲染，需瀏覽器工具 |
| 🇮🇹 意大利語（Messainlatino） | 🔴 高 | JS 渲染，需瀏覽器工具 |
| 🇵🇹🇧🇷 葡萄牙語 | 🟡 中 | 未研究 |
| 🇪🇸 西班牙語 | 🟡 中 | 已知 Aciprensa, Catholic.net |
| 🇵🇱 波蘭語 | 🔴 高 | 完全JS渲染，需另闢蹊徑 |
| 🇫🇷 法語 | 🟡 中 | 未研究 |
| 🇰🇷 韓語 | 🟡 中 | 未研究 |
| 🇻🇳 越南語 | 🟡 中 | 未研究 |
| 🇯🇵 日語 | 🟢 低 | 未研究 |

---

## Phase 4 ⏳ 功能深化

- [ ] 聖人日曆（配合每日讀經）
- [ ] 禮儀年導覽（將臨期/聖誕期/四旬期/復活期）
- [ ] 靈修導讀問題
- [ ] 引導祈禱文
- [ ] Divinum Officium（祈禱時辰）

---

## Phase 5 ⏳ 傳播

- [ ] 建立 contributors 社群
- [ ] 接觸各國主教團確認 license
- [ ] 中文以外的多語言推送（Telegram / Email）
- [ ] 印刷版 PDF 生成

---

## 進度總覽

```
Phase 1  ████████████████████ ✅ MVP 完成
Phase 2  ██░░░░░░░░░░░░░░░░░░ 🔄 2.0 ✅ → 2.1 Layer 1 生成中
Phase 3  ░░░░░░░░░░░░░░░░░░░ ⏳ 更多語言
Phase 4  ░░░░░░░░░░░░░░░░░░░ ⏳ 功能深化
Phase 5  ░░░░░░░░░░░░░░░░░░░ ⏳ 傳播
```

---

## GitHub Topics（待設定）⚠️

需要在 GitHub 瀏覽器設定，才能讓別人搜到：
```
catholic, bible, liturgy, python, open-source, daily-readings, chinese
```

詳見：[設定說明](https://github.com/westhong/catholic-daily-readings/settings)

---

*這個 Roadmap 會持續更新。有任何建議：westhong@gmail.com*
