# 實作狀態 — Catholic Assistant

> 更新日期：2026-04-19

---

## Phase 1 MVP ✅ (2026-04-18)
USCCB + FHL 思高譯本，單日測試記錄。

---

## Phase 2 MVP 2.1 — 三年禮儀年結構數據 ✅ (2026-04-19)

### 專案結構
```
catholic-assistant/
├── main.py
├── src/
│   ├── schema.py
│   ├── sources/usccb.py
│   ├── sources/fhl.py
│   ├── core/reader.py
│   └── liturgy/calendar.py   # 算法禮儀日曆引擎
├── scripts/
│   ├── scrape_usccb_readings.py  # 抓 USCCB .cfm URL
│   └── fill_missing.py           # 補抓特殊日子
├── data/
│   ├── 2026-04-18.json           # Phase 1 測試
│   └── lectionary/
│       ├── calendar_raw.json      # USCCB Drupal Views AJAX 禮儀日曆
│       └── readings.json         # ✅ 1060天讀經數據 (2024-12 至 2027-10)
├── wiki/
└── sources_inventory.json
```

### 已完成
- [x] 發現 USCCB `.cfm` URL 格式可直接 fetch（繞過 JavaScript）
- [x] 抓取全部 3 個禮儀年的讀經結構數據
- [x] 處理聖誕節 4 個時段彌撒 (Vigil/Night/Dawn/Day)
- [x] 處理聖週特殊日子 (Chrism Mass / Evening Mass / Good Friday / Easter Vigil)
- [x] 處理多選項日子（五旬節、耶穌升天、聖母升天等）
- [x] 更新 wiki

### 數據覆蓋率
- 總天數：1060（覆蓋 2024-12-01 → 2027-10-31）
- 完整讀經（lectionary number + 章節引用）：**99.2%**
- 已知缺口：7 個 2026 年日子（USCCB 不提供 readings sub-page）

### 缺口記錄（USCCB 數據限制）
以下日期的 lectionary number 和 feast name 已知，但章節引用無法從 USCCB 取得：
- 2026-05-14: L58 — 耶穌升天節 (The Ascension of the Lord)
- 2026-05-17: L58 — 耶穌升天節主日 (Seventh Sunday of Easter - Ascension)
- 2026-05-24: L62 — 五旬節 (Pentecost Sunday)
- 2026-06-24: L586 — 聖若翰洗者誕辰 (Solemnity of St. John the Baptist)
- 2026-06-29: L590 — 聖伯多祿聖保祿宗徒節 (Solemnity of Sts. Peter and Paul)
- 2026-08-15: L621 — 聖母升天節 (The Assumption of the Blessed Virgin Mary)
- 2026-11-26: L506 — 常年期第34周星期四 (Thursday of the 34th Week)

原因：USCCB 的 `.cfm` 頁面本體無讀經內容，sub-page 返回 HTTP 404。

---

## 下一步
- [ ] 逐日驗證 readings.json 數據
- [ ] 接洽 USCCB / FHL 確認版權
- [ ] 建立 JSON → 中文靈修禱文格式輸出
- [ ] 加入聖人日曆（Menology）
- [ ] 加入靈修導讀問題
- [ ] 確認 source license
