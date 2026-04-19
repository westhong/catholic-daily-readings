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

## Phase 2.1 ✅ USCCB 三年讀經結構數據 (2026-04-19)

> 用 `.cfm` URL 繞過 JavaScript，直接 fetch USCCB HTML，1049 天數據，99.2% 覆蓋率。

- [x] 發現 `.cfm` URL 格式（`MMDDYY.cfm`）
- [x] 處理聖誕節多時段 (Vigil/Night/Dawn/Day)
- [x] 處理聖週特殊日子
- [x] 處理多 lectionary option 日子
- [x] 抓取 2024-12 至 2027-10（共 1060 天）
- [x] 更新 wiki
- [ ] 逐日驗證 readings.json 數據 ← 當前任務
- [ ] 建立 GitHub release

### 2.2 🔄 下一個：接洽 USCCB + FHL

> 先做英語系，因為我們已確認這三個都有機器可讀格式。歐洲 sources 需要瀏覽器工具，之後再做。

**目標：同一個 JSON，同時包含 Mass 讀經 + Breviary 祈禱時辰**

```json
{
  "date": "2026-04-18",
  "mass": {
    "feast_name": "復活期第二周星期六",
    "lectionary_number": 272,
    "readings": [
      { "type": "first_reading", "name": "讀經一", "reference": "宗徒大事錄 6:1-7", "bible_texts": {...} },
      { "type": "responsorial_psalm", "name": "答唱詠", "reference": "聖詠 33:1-2, 4-5, 18-19", "bible_texts": {...} },
      { "type": "gospel", "name": "福音", "reference": "若望福音 6:16-21", "bible_texts": {...} }
    ]
  },
  "breviary": {
    "invitatory":      { "name": "邀請禱",  "hour": "Invitatory", "antiphon": "...", "psalm": "聖詠 24" },
    "office_of_readings": { "name": "誦讀課", "hour": "Office of Readings", "antiphon": "...", "reading": "..." },
    "morning_prayer":   { "name": "晨禱",   "hour": "Morning Prayer", "psalms": [...], "antiphon": "..." },
    "midday":          { "name": "午時禱",  "hour": "Midday Prayer", ... },
    "midafternoon":    { "name": "午後禱",  "hour": "Midafternoon Prayer", ... },
    "evening_prayer":  { "name": "晚禱",    "hour": "Evening Prayer", ... },
    "night_prayer":    { "name": "夜禱",    "hour": "Night Prayer", ... }
  }
}
```

### 2.1 英語系：三個來源 🔄 下一步

| 來源 | 系統 | 已有 confirmed types？ | RSS/HTML |
|------|------|----------------------|----------|
| **USCCB** | Mass | ✅ Reading 1, Psalm, Reading 2, Alleluia, Gospel | HTML |
| **CatholicOnline** | Mass | ✅ Reading 1, Psalm, Gospel, Reading 2（主日） | ✅ RSS |
| **DivineOffice.org** | Breviary | ✅ Invitatory / Office / Morning / Midmorning / Midday / Midafternoon / Evening / Night | ✅ RSS |

**交付：**
- [ ] 更新 schema.py：加入 mass + breviary 雙系統結構
- [ ] 新增 `src/sources/catholic_online.py`（RSS parser）
- [ ] 新增 `src/sources/divine_office.py`（RSS parser）
- [ ] 統一 English sources 整合進同一個 record

### 2.2 德語整合 🇩🇪🇦🇹🇨🇭（之後）

> 需要瀏覽器工具抓 JS 渲染的頁面

### 2.3 意大利語整合 🇮🇹（之後）

> 同上

| 語系 | 優先度 | 狀態 |
|------|--------|------|
| 🇵🇹🇧🇷 葡萄牙語 | 🟡 中 | 未研究 |
| 🇪🇸 西班牙語 | 🟡 中 | 已知 Aciprensa, Catholic.net |
| 🇵🇱 波蘭語 | 🔴 高 | 完全JS渲染，需另闢蹊徑 |
| 🇫🇷 法語 | 🟡 中 | 未研究 |
| 🇰🇷 韓語 | 🟡 中 | 未研究 |
| 🇻🇳 越南語 | 🟡 中 | 未研究 |
| 🇯🇵 日語 | 🟢 低 | 未研究 |

---

## Phase 4：功能深化

- [ ] 聖人日曆（配合每日讀經）
- [ ] 禮儀年導覽（將臨期/聖誕期/四旬期/復活期）
- [ ] 靈修導讀問題
- [ ] 引導祈禱文
- [ ] Divinum Officium（祈禱時辰）

---

## Phase 5：傳播

- [ ] 建立 contributors 社群
- [ ] 接觸各國主教團確認 license
- [ ] 中文以外的多語言推送（Telegram / Email）
- [ ] 印刷版 PDF 生成

---

## 進度總覽

```
Phase 1  ████████████████████ ✅ MVP 完成
Phase 2  ██░░░░░░░░░░░░░░░░░░ 🔄 2.1 ✅ → 逐日驗證中
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
