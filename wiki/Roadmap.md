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

## Phase 2 🔄 即將開始：歐洲語系整合

**目標：用歐洲各國來源的 Lectionary Number，配上我們的譯本，輸出多語言每日讀經**

### 2.1 德語整合 🇩🇪🇦🇹🇨🇭

| 來源 | 優先度 | 原因 |
|------|--------|------|
| Katholisch.de（DBK） | 🔴 高 | 官方背書，RSS質量最高，有JSON-LD |
| LITURGIE | 🔴 高 | CDATA格式，質量最好 |
| Kiwi.ch（瑞士） | 🟡 中 | 瑞士主教團相關 |
| katholisch.at（奧） | 🟡 中 | 官方，但RSS只有連結 |
| Bistum Brixen（南蒂） | 🟢 低 | 意大利德語區，覆蓋範圍重疊 |

**交付：**
- `src/sources/katholisch_de.py`
- `src/sources/liturgie_de.py`
- 德語區統一輸出格式

### 2.2 意大利語整合 🇮🇹

| 來源 | 優先度 | 原因 |
|------|--------|------|
| Messainlatino.it | 🔴 高 | 完整static HTML + RSS |
| CEI 官方 | 🟢 低 | 未確認有機器可讀格式 |

**交付：**
- `src/sources/messainlatino_it.py`
- 意大利語輸出

### 2.3 荷蘭語整合 🇳🇱🇧🇪

| 來源 | 優先度 | 原因 |
|------|--------|------|
| Kerknet.be（法蘭德斯） | 🔴 高 | 有專用RSS |
| RKK.nl（荷蘭） | 🟡 中 | 有欄目但無專用feed |

**交付：**
- `src/sources/kerknet_be.py`
- 荷蘭語輸出

---

## Phase 3：更多語言

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
Phase 2  ██░░░░░░░░░░░░░░░░░░ 🔄 德/意/荷整合（下一步）
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
