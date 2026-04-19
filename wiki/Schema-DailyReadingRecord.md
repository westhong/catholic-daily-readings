# Schema: DailyReadingRecord（每日讀經記錄）

> 標準化資料格式 — 所有多語言來源共用的統一結構
> 核心主鍵：lectionary_number — 所有 source 靠它對齊
> 版本：1.0 | 更新：2026-04-18

---

## 完整結構

```json
{
  "date": "2026-04-18",
  "weekday": "Saturday",
  "feast_name": "Saturday of the Second Week of Easter",
  "feast_name_zh": "復活期第二周星期六",
  "lectionary_number": 272,
  "liturgical_year": "Easter Season",
  "liturgical_year_zh": "復活期",
  "readings": [
    {
      "type": "psalm",
      "reference": {
        "book_en": "Psalm",
        "book_fhl": "詩",
        "book_full_zh": "聖詠",
        "chapter": 33,
        "verse_range": "1-2, 4-5, 18-19"
      },
      "bible_texts": {
        "zh_trad": "義人，你們應向上主踴躍歡呼...",
        "zh_simpl": "义人，你们应向上主踊跃欢呼..."
      },
      "alleluia_verse": null
    },
    {
      "type": "first_reading",
      "reference": {
        "book_en": "Acts",
        "book_fhl": "宗",
        "book_full_zh": "宗徒大事錄",
        "chapter": 6,
        "verse_range": "1-7"
      },
      "bible_texts": {
        "zh_trad": "在那一天...",
        "zh_simpl": "在那一天..."
      },
      "alleluia_verse": null
    },
    {
      "type": "gospel",
      "reference": {
        "book_en": "John",
        "book_fhl": "若",
        "book_full_zh": "若望福音",
        "chapter": 6,
        "verse_range": "16-21"
      },
      "bible_texts": {
        "zh_trad": "那時，耶穌在革乃撒勒湖邊...",
        "zh_simpl": "那时，耶稣在革乃撒勒湖边..."
      },
      "alleluia_verse": "主，你是的話語是我腳前的燈。"
    }
  ],
  "metadata": {
    "sources": [
      {
        "source_id": "usccb",
        "source_name_en": "USCCB Daily Bible Reading",
        "source_name_zh": "美國主教團每日讀經",
        "source_uri": "https://bible.usccb.org/daily-bible-reading",
        "license": "private-use-only",
        "license_detail": "Copyright © Confraternity of Christian Doctrine. Personal/parish use free; redistribution requires permission.",
        "lectionary_ref": 272,
        "data": {}
      }
    ],
    "translations": [
      {
        "translation_id": "fhl_ofm",
        "translation_name_en": "Studium Biblicum Franciscanum (Sikong)",
        "translation_name_zh": "思高學會譯本",
        "source_uri": "https://bible.fhl.net/",
        "language": "zh_trad",
        "license": "research-use",
        "license_detail": "Free for research use; commercial use requires permission."
      }
    ],
    "generated_at": "2026-04-18T17:30:00-06:00",
    "schema_version": "1.0"
  }
}
```

---

## 欄位說明

### 頂層欄位

| 欄位 | 類型 | 說明 |
|------|------|------|
| `date` | string | ISO 格式日期（YYYY-MM-DD） |
| `weekday` | string | 禮儀日名稱（英文） |
| `feast_name` | string | 節日名稱（英文） |
| `feast_name_zh` | string | 節日名稱（繁體中文） |
| `lectionary_number` | integer | **核心主鍵** — 羅馬禮儀日曆編號 |
| `liturgical_year` | string | 禮儀年季節（英文） |
| `liturgical_year_zh` | string | 禮儀年季節（繁體中文） |
| `readings` | array | 讀經陣列 |

### readings[] 內每筆讀經

| 欄位 | 類型 | 說明 |
|------|------|------|
| `type` | enum | `psalm` / `first_reading` / `gospel` / `second_reading` |
| `reference.book_en` | string | 聖經書名（英文，USCCB 標準） |
| `reference.book_fhl` | string | FHL 書名簡稱（用於 fetch 中文經文） |
| `reference.book_full_zh` | string | 書名全稱（繁體中文） |
| `reference.chapter` | integer | 章節 |
| `reference.verse_range` | string | 節數範圍 |
| `bible_texts.zh_trad` | string | 繁體中文經文（思高譯本） |
| `bible_texts.zh_simpl` | string | 簡體中文經文 |
| `alleluia_verse` | string or null | 福音前歡呼詞（若適用） |

### metadata.sources[]

每個用於填充這筆記錄的 source，獨立記錄其 license 和 URI。

| 欄位 | 類型 | 說明 |
|------|------|------|
| `source_id` | string | 來源 ID（如 `usccb` / `ibreviary` / `divineoffice`） |
| `source_name_en` | string | 來源名稱（英文） |
| `source_name_zh` | string | 來源名稱（繁體中文） |
| `source_uri` | string | 原始 URI |
| `license` | string | License 簡稱 |
| `lectionary_ref` | integer | 該 source 的 Lectionary Number（用於對齊） |

---

## 設計原則

1. **Lectionary Number 是唯一主鍵** — 所有 source 靠這個數字對齊，不是靠日期
2. **Bible text 與 source metadata 分離** — 聖言是聖言，source 是取得 reference 的工具
3. **一個記錄可有多個 sources** — 未來同一篇讀經從多個 source 取得資料時，可以並存
4. **可擴展語言** — 只要在 `bible_texts` 加新的 language key 即可

---

## Book Name 對照表（USCCB → FHL）✅ 已驗證

> 2026-04-19 更新 — 以下均經實際 API 測試驗證

```python
USCCB_TO_FHL = {
    # ── 新約 ──
    "psalm":         "詩",    # 聖詠（詩篇）
    "psalms":        "詩",    # 聖詠（詩篇）
    "john":          "約",    # 若望福音（FHL用「約」，不是「若」）
    "acts":          "徒",    # 宗徒大事錄（FHL用「徒」，不是「宗」）
    "matthew":       "太",    # 瑪竇福音
    "mark":          "可",    # 馬爾谷福音
    "luke":          "路",    # 路加福音
    "romans":        "羅",    # 羅馬書
    "1corinthians":  "林前",  # 格林多前書
    "2corinthians":  "林後",  # 格林多後書
    "ephesians":     "弗",    # 厄弗所書
    "philippians":   "斐",    # 斐理伯書
    "colossians":    "哥",    # 哥羅森書
    "1thessalonians":"得前",  # 得撒洛尼前書
    "2thessalonians":"得後",  # 得撒洛尼後書
    "1timothy":      "弟前",  # 弟茂德前書
    "2timothy":      "弟後",  # 弟茂德後書
    "titus":         "弟",    # 弟铎书
    "philemon":      "費",    # 費肋孟書
    "hebrews":       "希",    # 希伯來書
    "james":         "雅",    # 雅各伯書
    "1peter":        "伯前",  # 伯多祿前書
    "2peter":        "伯後",  # 伯多祿後書
    "1john":         "若一",  # 若望一書
    "2john":         "若二",  # 若望二書
    "3john":         "若三",  # 若望三書
    "jude":          "猶",    # 猶達書
    "revelation":    "默",    # 若望默示錄
    # ── 舊約 ──
    "genesis":       "創",    # 創世記
    "exodus":       "出",    # 出谷紀
    "leviticus":     "肋",    # 肋未紀
    "numbers":       "民",    # 戶籍紀
    "deuteronomy":   "申",    # 申命紀
    "joshua":        "蘇",    # 若蘇厄書
    "judges":        "民",    # 民長紀
    "ruth":          "盧",    # 路得紀
    "1samuel":       "撒上",  # 撒慕爾紀上
    "2samuel":       "撒下",  # 撒慕爾紀下
    "1kings":        "列上",  # 列王紀上
    "2kings":        "列下",  # 列王紀下
    "1chronicles":   "編上",  # 編年紀上
    "2chronicles":   "編下",  # 編年紀下
    "ezra":          "厄上",  # 厄斯德拉上
    "nehemiah":      "厄下",  # 厄斯德拉下
    "tobit":         "多",    # 多俾亞傳
    "esther":        "艾",    # 艾斯德爾傳
    "job":           "約伯",  # 約伯傳
    "proverbs":      "箴",    # 箴言
    "ecclesiastes":  "訓",    # 訓道篇
    "song of songs": "歌",    # 雅歌
    "isaiah":        "依",    # 依撒意亞
    "jeremiah":      "耶",    # 耶肋米亞
    "lamentations":  "哀",    # 哀歌
    "ezekiel":       "則",    # 厄則克耳
    "daniel":        "達",    # 達尼爾
    "hosea":         "歐",    # 歐瑟亞
    "joel":          "岳",    # 岳厄爾
    "amos":          "亞",    # 亞毛斯
    "obadiah":       "納",    # 約纳
    "jonah":         "納",    # 約纳
    "micah":         "米",    # 米該亞
    "nahum":         "納",    # 納鴻
    "habakkuk":      "哈",    # 哈巴谷
    "zephaniah":     "索",    # 索福尼亞
    "haggai":        "蓋",    # 哈蓋
    "zechariah":     "匝",    # 匝加利亞
    "malachi":       "瑪",    # 瑪拉基亞
}
```

### 常見錯誤修正
| 錯誤寫法 | 正確寫法 | 說明 |
|---------|---------|------|
| `宗` | `徒` | FHL 用 `徒` 表示宗徒大事錄 |
| `若` | `約` | FHL 用 `約` 表示若望福音 |
| `詠` | `詩` | FHL 用 `詩` 表示聖詠/詩篇 |

---

*版本：1.0 | 建立：2026-04-18*
