# 實作狀態 — Catholic Assistant

> 更新日期：2026-04-19

---

## MVP 實作完成 ✅

### 專案結構
```
catholic-assistant/
├── main.py                      # Entry point
├── src/
│   ├── schema.py               # DailyReadingRecord schema + book mappings
│   ├── sources/
│   │   ├── usccb.py           # USCCB metadata scraper ✅
│   │   └── fhl.py             # FHL 思高譯本 fetcher ✅
│   └── core/
│       └── reader.py           # Assembles record from sources ✅
└── data/
    └── 2026-04-18.json        # First test record ✅
```

### 已實現功能
- [x] USCCB 每日讀經章節抓取（scrape）
- [x] FHL 思高譯本聖經經文取得（繁體中文）
- [x] 繁→簡體中文轉換
- [x] Lectionary Number 對齊
- [x] 禮儀年識別（將臨期/聖誕期/四旬期/復活期/常年 期）
- [x] 節日名稱中文化
- [x] 完整 DailyReadingRecord JSON 輸出
- [x] 測試記錄產出（2026-04-18）

### 測試結果（2026-04-18 復活期第二周星期六）
- Lectionary: 272
- Reading 1: 宗徒大事錄 6:1-7 — ✅ 思高譯本（宗徒大事錄）
- Psalm: 聖詠 33:1-2, 4-5, 18-19 — ✅ 思高譯本
- Alleluia: USCCB 無明確經文章節，略過
- Gospel: 若望福音 6:16-21 — ✅ 思高譯本

### 技術修正記錄
1. **FHL API 參數名**：`CN` ❌ → `chineses` ✅
2. **FHL 書名簡稱**（已驗證）：
   - Acts → `徒`（不是 `宗`）
   - John → `約`（不是 `若`）
   - Psalms → `詩`（不是 `詠`）
3. **USCCB HTML parsing**：Alleluia section 的 anchor tag 是 malformed（`">`），需偵測並跳過
4. **FHL 章節範圍**：需逐節 fetch（`1-2, 4-5` 分開請求）

---

## 下一步
- [ ] 建立格式化靈修禱文輸出（Telegram 格式）
- [ ] 設定每日 cron job
- [ ] 加入聖人日曆（Menology）
- [ ] 加入靈修導讀問題
- [ ] 加入引導祈禱文
- [ ] 建立第二譯本支援（和合本）
- [ ] 確認各 source license

---

## GitHub 準備
- [x] 初始化 git repo
- [ ] 建立 public repo
- [ ] 撰寫 README
- [ ] 選擇 license（建議：MIT 或 Apache 2.0）

