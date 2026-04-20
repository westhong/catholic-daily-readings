# Catholic Daily Readings

**免費、開源的天主教每日讀經。**

為神做一些事，去填補這個世界應該要有的東西，讓神的話語更能遠傳。溫柔地對待這個世界。

[🌐 English](#english) · [📖 繁體中文](#繁體中文)

---

## ✝️ 我們的使命

中文世界裡，沒有免費的、開放的天主教每日讀經系統。
我們相信天主的聖言應該被自由地傳遞。
這個項目，是對神的服侍。

> *「所以你們要去使萬民成為門徒。」* — 瑪竇福音 28:19

---

## 📐 數據分層架構

```
Layer 0 — Source Layer     原始 HTML 文件，凍存不動
Layer 1 — Processed Layer  citation_id JSON（無版權爭議）
Layer 2 — Applied Layer   各譯本完整章節顯示（譯本方處理）
```

**版權原則**：Layer 1 只儲存 `citation_id`（如 `acts:2`，公共遺產），不儲存有版權的經文本身。
詳見 [wiki/Data-Layers.md](wiki/Data-Layers.md)。

---

## 📁 專案結構

```
catholic-daily-readings/
├── main.py                        # 入口腳本（Phase 1 MVP）
├── src/
│   ├── sources/
│   │   ├── usccb.py              # USCCB 讀經元數據
│   │   └── fhl.py                # 思高譯本 API
│   ├── core/
│   │   └── reader.py              # 數據組裝
│   └── cron/                      # 定時任務腳本
├── data/
│   ├── daily/                     # Layer 1 JSON（Processed Layer）
│   └── usccb-calendar/            # Layer 0 RAW 文件（原始 HTML）
├── scripts/
│   └── scrape_usccb_calendar.py  # USCCB 日曆 Scraper（Phase 2 核心工具）
└── wiki/                          # 研究與規劃文檔
```

---

## 🚀 快速開始

```bash
# 克隆專案
git clone https://github.com/westhong/catholic-daily-readings.git
cd catholic-daily-readings

# 安裝依賴
pip install requests beautifulsoup4

# 取得今日讀經
python main.py
```

---

## 📖 每日讀經格式（Phase 1 MVP）

每次獲取包含：
- **Feast Day** — 本日瞻禮名稱
- **讀經一** (First Reading) + 中文翻譯
- **答唱詠** (Responsorial Psalm) + 中文翻譯
- **福音** (Gospel) + 中文翻譯

所有中文譯文來自[思高譯本](https://bible.fhl.net)，經文版權歸香港聖經公會所有。

---

## 🌱 未來願景

- [ ] 繁體中文每日靈修禱文（聖母玫瑰經、聖體聖事等）
- [ ] Layer 2 Applied Layer — 多語言譯本對接
- [ ] 祈禱時辰（Divine Office / Liturgy of the Hours）
- [ ] 每日推送（Email / Telegram）
- [ ] 印刷版 PDF 生成
- [ ] 語音版本（Text-to-Speech）

---

## 🤝 貢獻

歡迎貢獻！請參閱 [wiki](wiki/) 了解專案規劃和當前進度。

如果你知道任何免費的天主教每日讀經來源（任何語言）、或有任何能令這個系統更豐富的想法，歡迎告訴我們：

📧 **westhong@gmail.com**

---

## 📜 授權與使用聲明

### 聖經經文
- **英文聖經經文**：來自 New American Bible Revised Edition (NABRE)，版權 © Confraternity of Christian Doctrine (CCD)，Washington, DC。僅供私人研究使用。
- **中文聖經經文**：來自律敦思高譯本，版權 © 香港聖經公會 / 信望愛資源中心。僅供私人研究使用。

### 讀經結構數據
讀經選擇與編排（Lectionary Selection）版權 © Confraternity of Christian Doctrine。僅供私人研究使用。

### citation_id（Layer 1 核心欄位）
`citation_id`（如 `acts:2`、`psalm:16`）屬於公共遺產，無版權爭議。本專案僅儲存此類公共資料。

### 軟件
MIT — 自由使用，為主服務。

---

*本專案旨在榮耀天主。所有聖經經文版權歸其各自持有者所有。*

---

## English

**Catholic Daily Readings** is a free, open-source project providing daily Catholic Mass readings, starting with Chinese translations to serve Chinese-speaking Catholics worldwide.

> *"Go, therefore, and make disciples of all nations."* — Matthew 28:19

### Motivation

There is no free, open-source Catholic daily readings system in Chinese. This project exists to change that — for the glory of God.

### Data Architecture

```
Layer 0 — Source Layer     Raw HTML files, immutable
Layer 1 — Processed Layer  citation_id JSON (public domain, no copyright issues)
Layer 2 — Applied Layer    Full scripture display per translation (handled by translators)
```

`citation_id` (e.g., `acts:2`, `psalm:16`) is public domain. See [wiki/Data-Layers.md](wiki/Data-Layers.md).

### Quick Start

```bash
git clone https://github.com/westhong/catholic-daily-readings.git
cd catholic-daily-readings
pip install requests beautifulsoup4
python main.py
```

Output: `data/YYYY-MM-DD.json`
