# 數據分層架構

> 更新日期：2026-04-19

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
- 462 個 .cfm 文件（2026-04 → 2027-05）
- 其中 447 個有效、15 個空殼（USCCB redirect 入口頁）
- 15 個空殼：`040226.cfm`、`122526.cfm`、`051426.cfm`、`051726.cfm` 等

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
data/daily/
  2026-04-19.json      ← 一個 day object
  2026-04-20.json
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

```json
{
  "date": "2026-04-19",
  "source": "usccb",
  "lectionary_number": 46,
  "feast_en": "Third Sunday of Easter",
  "color": "white",
  "local_file": "2026-04-19-041926.cfm",
  "url": "https://bible.usccb.org/bible/readings/041926.cfm",
  "readings": [
    {
      "slot": 1,
      "type": "first_reading",
      "label": "Reading 1",
      "citation_id": "acts:2",
      "usccb_url": "https://bible.usccb.org/bible/acts/2?14",
      "alternatives": []
    },
    {
      "slot": 2,
      "type": "responsorial_psalm",
      "label": "Responsorial Psalm",
      "citation_id": "psalm:16",
      "usccb_url": "https://bible.usccb.org/bible/psalms/16?1",
      "alternatives": []
    },
    {
      "slot": 3,
      "type": "second_reading",
      "label": "Reading 2",
      "citation_id": "1peter:1",
      "usccb_url": "https://bible.usccb.org/bible/1peter/1?17",
      "alternatives": []
    },
    {
      "slot": 4,
      "type": "alleluia_verse",
      "label": "Alleluia",
      "citation_id": "luke:24",
      "usccb_url": "https://bible.usccb.org/bible/luke/24?32",
      "alternatives": []
    },
    {
      "slot": 5,
      "type": "gospel",
      "label": "Gospel",
      "citation_id": "luke:24",
      "usccb_url": "https://bible.usccb.org/bible/luke/24?13",
      "alternatives": []
    }
  ]
}
```

---

## 欄位說明

| 欄位 | 說明 | 例子 |
|------|------|------|
| `date` | 禮儀日期（YYYY-MM-DD） | `2026-04-19` |
| `source` | 來源 ID | `usccb` |
| `lectionary_number` | 彌撒讀經編號（從 calendar index 帶入） | `46` |
| `feast_en` | 英文 feast 名稱 | `Third Sunday of Easter` |
| `color` | 禮儀顏色 | `white` |
| `local_file` | Layer 0 文件名（用於溯源） | `2026-04-19-041926.cfm` |
| `url` | 原始 URL | `https://bible.usccb.org/bible/readings/041926.cfm` |
| `readings[].slot` | 禮儀順序 | `1`, `2`, `3`... |
| `readings[].type` | 讀經類型 | `first_reading`, `gospel` 等 |
| `readings[].label` | 原始 HTML 標籤（verbatim） | `Reading 1`, `Responsorial Psalm` |
| `readings[].citation_id` | 標準化章節 ID | `acts:2`, `psalm:16`, `luke:24` |
| `readings[].usccb_url` | USCCB 聖經章節 URL | `https://bible.usccb.org/bible/acts/2?14` |
| `readings[].alternatives[]` | 替代讀經選項（Or 區塊） | 见下方 |

### Reading Types（`type`）

| type | 說明 |
|------|------|
| `first_reading` | 讀經一 |
| `second_reading` | 讀經二 |
| `old_testament_reading` | 舊約讀經（Easter Vigil 專用） |
| `responsorial_psalm` | 答唱詠 |
| `gospel` | 福音 |
| `alleluia_verse` | 阿肋路亞歡呼 |
| `verse_before_gospel` | 福音前詠唱（部分大節日用） |
| `sequence` | 繼抒詠（Easter, Pentecost 等） |
| `epistle` | 書信（Easter Vigil 專用） |
| `alternative` | 替代讀經（本欄位不用，見 alternatives[]） |

### Alternatives（替代讀經）

`Or` 區塊在 HTML 中出現在其附屬讀經之後，用於記錄禮儀可選讀經。

```json
{
  "slot": 7,
  "type": "gospel",
  "label": "Gospel",
  "citation_id": "john:20",
  "usccb_url": "https://bible.usccb.org/bible/john/20?1",
  "alternatives": [
    {
      "citation_id": "matthew:28",
      "usccb_url": "https://bible.usccb.org/bible/matthew/28?1",
      "condition": "Or"
    },
    {
      "citation_id": "luke:24",
      "usccb_url": "https://bible.usccb.org/bible/luke/24?13",
      "condition": "Or at afternoon or evening mass"
    }
  ]
}
```

`condition` 的值直接來自 HTML label verbatim，**不翻譯、不簡化**。

### Citation ID 格式

`citation_id` = `book:chapter`，book 用 canonical 名字（小寫，數字英文）：

| USCCB URL book | citation_id |
|----------------|------------|
| `acts` | `acts` |
| `psalms` | `psalm` |
| `1peter` | `1peter` |
| `luke` | `luke` |
| `john` | `john` |
| `matthew` | `matthew` |
| `genesis` | `genesis` |
| `exodus` | `exodus` |
| `romans` | `romans` |
| ... | ... |

原則：
- **只用章 + 節起點**（不記 ending verse），避免冗餘
- `citation_id` 是公共遺產，無版權
- Applied Layer 負責把 `citation_id` + 譯本 → 完整顯示（如 `Luke 24:13-35`）

---

## Multi-Source 擴展

未來 Layer 0 / Layer 1 可以容納多個 source：

```
Layer 0
├── usccb/           (英語, .cfm HTML) ✅ 已完成
├── fhl/             (繁體中文, 自有格式) — Phase 3
├── ibrev/           (意大利語, 自有格式) — Phase 3
├── kath/            (德語, 自有格式)     — Phase 3
└── ...

Layer 1
├── usccb/2026-04-19.json   ✅ 已完成
├── fhl/2026-04-19.json     — Phase 3
└── ...

Layer 2
├── en/nab/2026-04-19.json  — USCCB/NAB 譯本
├── zh/ofm/2026-04-19.json  — FHL 思高譯本
└── ...
```

所有 source 共享同一個 Layer 1 schema，差異只在 source ID。
