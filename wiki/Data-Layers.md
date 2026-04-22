# 數據分層架構

> 更新日期：2026-04-21

---

## Layer 0 — Source Layer（原始層）

**職責**：存放未經修改的原始輸入。

- 來自 USCCB 的 `.cfm` HTML 文件（禮儀日曆 HTML 頁面）
- 未來擴展：其他語系的 source（iBreviary / Messainlatino / Katholisch.de 等）
- Immutable — 不做任何解讀、修改、刪減

**儲存位置**：
```
data/usccb-calendar/raw/
  2026-04-01-040126.cfm
  2026-04-02-040226-Supper.cfm
  2026-04-02-040226-chrism.cfm
  2027-05-07-050727cfm.cfm     ← 注意：cfm 是 slug 本身的一部分
  ...
```

每個文件代表 **一個 feast 在一天的 URL endpoint**。

**特點**：
- 來自外部網站（USCCB），非我們生成
- Factual source — 事實真相的最原始來源
- 可能包含 HTML 噪聲、無法解析的結構、多餘內容
- 不同 source 的 HTML 結構完全不同，沒有統一格式

**用途**：
- 凍存起來，作為未來重新處事的依據
- 如果任何 downstream 處理有爭議，以 source layer 為準

**已知數據**：
- **1,741 個 .cfm 文件**（凍存完成）
  - 2023: 366 個 ✅
  - 2024: 366 個 ✅
  - 2025: 365 個 ✅
  - 2026: 296 個 ✅
  - 2027: 380 個 ✅
- 15 個空殼（USCCB redirect 入口頁，已識別並跳過）

---

## Layer 1 — Processed Layer（處理層）

**職責**：LLM 從 Source Layer 讀取原始 HTML，分析出結構化屬性，輸出 day object。

每個 day object 包含：
- 日期、 feast 名稱、禮儀顏色
- Lectionary Number
- 讀經 slot、類型、citation_id（標準化章節 ID）
- alternatives（替代讀經選項）

**儲存位置**：
```
data/lectionary/
  readings.json      ← 合併的 Layer 1（1,763 個日期）
data/usccb-calendar/index/
  202604.json        ← 每月 calendar index（含 lectionary_number）
  202605.json
  ...
```

**輸出格式**：見下方「Layer 1 JSON Schema」章節。

---

## Layer 2 — Applied Layer（應用層）

**職責**：根據不同語言的聖經譯本，將 citation_id 轉換為該語言的聖經章節顯示。

例如 `citation_id: luke:24`：
- 英文（USCCB/NAB）：Luke 24:13-35
- 繁體中文（FHL/思高）：若望福音 24:13-35
- 簡體中文（和合本）：路加福音 24:13-35

**版權原則**：
- Layer 1 只存 `citation_id`（公共遺產，無版權）
- Layer 2 的實際聖經章節名稱（書名、章、節）屬於各譯本，有版權
- 不同譯本、不同語言，各自是一個 Applied Layer JSON
- Applied Layer 由翻譯版權方提供，不在我們的 repo 裡

```
Layer 0: .cfm HTML          ← immutable, 凍存
Layer 1: {citation_id}      ← 無版權爭議（只有章節引用數字）
Layer 2: {book_chapter:verse} ← 有版權，由譯本方處理
```

---

## 兩層關係

```
Layer 0: Source         Layer 1: Processed        Layer 2: Applied
────────────────────    ────────────────────    ────────────────────
.cfm HTML ────────→  [LLM 分析]  ────→  day_object ──→ [譯本] ──→ display JSON
(raw, immutable)         (結構化, 可查詢)         (citation_id)     (各語言)
```

---

## Layer 1 JSON Schema

readings.json 的格式（multi-source，1,763 個日期）：

```json
{
  "2026-04-19": [
    {
      "lectionary_number": 46,
      "feast": "Third Sunday of Easter",
      "mass": "default",
      "readings": {
        "first_reading": [
          {"citation": "Acts 2:14b, 22-28", "sources": ["USCCB", "CatholicGallery"]}
        ],
        "responsorial_psalm": [
          {"citation": "Psalm 16:1-2a and 5, 7-8, 9-10, 11", "sources": ["USCCB"]}
        ],
        "second_reading": [
          {"citation": "1 Peter 1:17-21", "sources": ["USCCB"]}
        ],
        "alleluia": [
          {"citation": "Luke 24:32", "sources": ["USCCB"]}
        ],
        "gospel": [
          {"citation": "Luke 24:13-35", "sources": ["USCCB", "CatholicGallery", "CatholicOnline"]}
        ]
      }
    }
  ]
}
```

**欄位說明**：

|| 欄位 | 說明 |
||------|------|
| `date` (key) | 禮儀日期（YYYY-MM-DD） |
| `lectionary_number` | 彌撒讀經編號 |
| `feast` | 英文 feast 名稱 |
| `mass` | `"default"` 或特定 mass（如 `"Chrism"`, `"Supper"`） |
| `readings.{slot}[].citation` | 標準化章節引用（如 `Acts 2:14b, 22-28`） |
| `readings.{slot}[].sources` | 哪些 source 有這個 citation |

**Reading Types（`slot`）**：

| slot | 說明 |
|------|------|
| `first_reading` | 讀經一 |
| `second_reading` | 讀經二 |
| `responsorial_psalm` | 答唱詠 |
| `alleluia` | 阿肋路亞歡呼（可能缺少，因為 USCCB 平日可能無 citation） |
| `verse_before_gospel` | 福音前歡呼（部分大節日） |
| `sequence` | 繼抒詠（Easter, Pentecost 等） |
| `gospel` | 福音 |

**版權原則**：
- `citation` 只存書卷章節（公共遺產，無版權）
- 實際聖經經文由譯本方在 Layer 2 提供

---

## Multi-Source 擴展

已確認的 Cross-Reference Sources：

|| Source | URL 格式 | 狀態 |
||--------|----------|------|
| **USCCB** | `bible.usccb.org/bible/readings/MMDDYY.cfm` | ✅ 主要 source |
| **CatholicGallery** | `catholicgallery.org/mass-reading/DDMMYY/` | ✅ 有 2023-2027 歷史數據 |
| **CatholicOnline** | `catholic.org/bible/daily_reading/?select_date=YYYY-MM-DD` | ✅ 有 2023-2027 歷史數據 |
| **Prayla** | `prayla.app/en/bible/readings/YYYY-MM-DD` | 🔄 待驗證 |

所有 readings.json 的 citation 都以 USCCB 為主 source，CatholicGallery / CatholicOnline 為 cross-reference。

Layer 0 / Layer 1 可以容納多個 source：

```
Layer 0
├── usccb/           (英語, .cfm HTML) ✅ 已凍存 1,741 個檔案
├── fhl/             (繁體中文, 自有格式) — Phase 3
├── ibrev/           (意大利語, 自有格式) — Phase 3
├── kath/            (德語, 自有格式)     — Phase 3
└── ...

Layer 1
├── readings.json    ✅ 1,763 個日期（USCCB 為主 source）
├── fhl/             — Phase 3
└── ...

Layer 2
├── en/nab/2026-04-19.json  — USCCB/NAB 譯本
├── zh/ofm/2026-04-19.json  — FHL 思高譯本
└── ...
```

所有 source 共享同一個 Layer 1 schema，差異只在 source ID。
