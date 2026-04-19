# Catholic Daily Readings

**免費、开源的天主教每日彌撒讀經。**

從中文譯本開始，為全球華人天主教徒服務，未來計劃支援更多語言和靈修形式。

[🌐 English](#english) · [📖 繁體中文](#繁體中文)

---

## ✝️ 我們的使命

中文世界裡，沒有免費的、開放的天主教每日讀經系統。  
我們相信天主的聖言應該被自由地傳遞。  
這個項目，是對神的服侍。

> *「所以你們要去使萬民成為門徒。」* — 瑪竇福音 28:19

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

## 📖 每日讀經格式

每次獲取包含：
- **Feast Day** — 本日瞻禮名稱
- **讀經一** (First Reading) + 中文翻譯
- **答唱詠** (Responsorial Psalm) + 中文翻譯
- **福音** (Gospel) + 中文翻譯

所有中文譯文來自[思高譯本](https://bible.fhl.net)，經文版權歸香港聖經公會所有。

---

## 📁 專案結構

```
catholic-daily-readings/
├── main.py              # 入口腳本
├── src/
│   ├── sources/
│   │   ├── usccb.py     # USCCB 讀經元數據抓取
│   │   └── fhl.py       # 思高譯本 API
│   ├── core/
│   │   └── reader.py    # 數據組裝
│   └── cron/            # 定時任務腳本
├── data/                # 每日 JSON 輸出
└── wiki/                # 研究與規劃文檔
```

---

## 🌱 未來願景

- [ ] 繁體中文每日靈修禱文（聖母玫瑰經、聖體聖事等）
- [ ] 英文、法文、西班牙文等多語言支援
- [ ] 每日推送（Email / Telegram）
- [ ] 印刷版 PDF 生成
- [ ] 語音版本（Text-to-Speech）

---

## 🤝 貢獻

歡迎貢獻！請參閱 [wiki](wiki/) 了解專案規劃和當前進度。

---

## 📜 授權

MIT — 自由使用，為主服務。

---

## English

**Catholic Daily Readings** is a free, open-source project providing daily Catholic Mass readings, starting with Chinese translations to serve Chinese-speaking Catholics worldwide.

### Quick Start

```bash
git clone https://github.com/westhong/catholic-daily-readings.git
cd catholic-daily-readings
pip install requests beautifulsoup4
python main.py
```

Output: `data/YYYY-MM-DD.json`

### Motivation

There is no free, open-source Catholic daily readings system in Chinese. This project exists to change that — for the glory of God.
