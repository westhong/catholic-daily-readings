# 參與貢獻

感謝你願意幫忙。這個專案很簡單，你可以在很多地方出一分力。

---

## 我可以怎麼幫？

### 🐛 回報問題
- 發現讀經數據有錯？章節不對？請開 [Issue](https://github.com/westhong/catholic-daily-readings/issues)
- 截圖 + 日期，讓我們可以重現問題

### 🌐 加入新語言
- 知道其他免費的天主教每日讀經來源？告訴我們
- 能幫忙翻譯介面或文檔？

### 💻 開發
- Fork → 改 code → Pull Request
- 請先看 [wiki](wiki/) 了解專案架構和當前進度

### 📖 加入靈修內容
- 讀經反省問題
- 祈禱文
- 聖人日曆

### 🙏 推廣
- 分享給你認識的教友、神父
- 在天主教論壇或社群提到這個專案

---

## 專案架構

```
src/
├── sources/
│   ├── usccb.py      # 讀經元數據（英文）
│   └── fhl.py        # 思高譯本聖經（中文）
├── core/
│   └── reader.py     # 組裝數據
└── cron/             # 定時抓取腳本
```

每個 source 獨立在 `sources/` 目錄下，擴展時不影響其他模組。

---

## 當前數據格式

詳見 [wiki/Schema-DailyReadingRecord.md](wiki/Schema-DailyReadingRecord.md)

---

## 聯絡

有任何問題，歡迎聯絡：westhong@gmail.com

---

## 授權

這個專案是 MIT 授權。你的貢獻也會以 MIT 授權。
