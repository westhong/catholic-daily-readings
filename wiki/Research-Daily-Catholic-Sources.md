# 研究報告：全球天主教每日讀經 / 靈修來源

> 目標：找出所有可用來建立中文天主教每日靈修系統的免費資料來源
> 更新日期：2026-04-18

---

## 核心需求定義

我們想要的系統必須能提供：
1. **來源 URI** — 機器可讀的資料來源
2. **Lectionary Number** — 禮儀年編號（這是跨語言翻譯的橋樑）
3. **語言** — 原始來源語言
4. **譯本** — 能翻成繁體中文 + 簡體中文
5. **License** — 可否用於我們的系統

---

## 第一部分：英文來源（主要研究）

### 1. USCCB Daily Readings
| 欄位 | 內容 |
|------|------|
| 服務名稱（英） | USCCB Daily Bible Reading |
| 服務名稱（中） | 美國主教團每日讀經 |
| URI | https://bible.usccb.org/daily-bible-reading |
| 語言 | 英文 |
| Lectionary Number | ✅ 有（e.g. 272） |
| License | 版權內容（Confraternity of Christian Doctrine），私人/堂區使用免費，但未經授權不得公開散佈 |
| 資料內容 | 每日讀經章節（Psalm / First Reading / Gospel）+ 簡短導讀 |
| API | ❌ 無公開 API |
| 備註 | 我們目前正在使用這個作為 reference source，但用 FHL 思高譯本置換了經文 |

### 2. iBreviary
| 欄位 | 內容 |
|------|------|
| 服務名稱（英） | iBreviary |
| 服務名稱（中） | 每日祈禱書 |
| URI | http://www.ibreviary.net/ |
| 語言 | 英文、西班牙文、法文、意大利文、拉丁文 |
| Lectionary Number | ✅ 有（羅馬禮儀日曆） |
| License | 部分內容 Creative Commons（需要進一步確認哪部分） |
| 資料內容 | 完整每日 Divinum Officium（晨禱、日間祈禱、晚禱、夜禱）+ 讀經 |
| API | 有限制，無公開 API |
| 備註 | 這是西方天主教數位化最完整的免費資源之一 |

### 3. DivineOffice.org
| 欄位 | 內容 |
|------|------|
| 服務名稱（英） | Divine Office (Liturgy of the Hours) |
| 服務名稱（中） | 每日聖部禮 |
| URI | https://www.divineoffice.org/ |
| 語言 | 英文 |
| Lectionary Number | ✅ 有 |
| License | 免費（個人使用），廣告支援；商業用途需授權 |
| 資料內容 | 完整 Liturgy of the Hours，含詩篇、讀經、禱詞 |
| API | 有部分 API 功能 |
| 備註 | 評估：可用於英語國家的禮儀時辰 |

### 4. Universalis
| 欄位 | 內容 |
|------|------|
| 服務名稱（英） | Universalis |
| 服務名稱（中） | 通用祈禱書 |
| URI | https://www.universalis.com/ |
| 語言 | 英文、法文、西班牙文、意大利文、葡萄牙文、波蘭文、拉丁文 |
| Lectionary Number | ✅ 有 |
| License | 商業訂閱軟件 |
| 資料內容 | 完整 Divinum Officium + 深度靈修導讀 |
| API | ✅ 有（僅供訂閱者） |
| 備註 | 質量最高的祈禱系統之一，但 license 限制商業使用 |

### 5. Magnificat
| 欄位 | 內容 |
|------|------|
| 服務名稱（英） | Magnificat |
| 服務名稱（中） | 頌恩 |
| URI | https://www.magnificat.com/ |
| 語言 | 英文、法文、西班牙文 |
| Lectionary Number | ✅ 有 |
| License | 商業訂閱 |
| 資料內容 | 每日靈修、晨禱、禮儀年默想、引導祈禱 |
| API | ❌ 無公開 API |
| 備註 | 被譽為最好的每日靈修資源之一，但需付費 |

### 6. The Word Among Us
| 欄位 | 內容 |
|------|------|
| 服務名稱（英） | The Word Among Us |
| 服務名稱（中） | 聖言在我們中間 |
| URI | https://www.wordamongus.org/ |
| 語言 | 英文 |
| Lectionary Number | ✅ 有 |
| License | 混合（部分免費，完整內容需訂閱） |
| 資料內容 | 每日默想、讀經、反省問題 |
| API | ❌ 無公開 API |
| 備註 | 免費內容質量已很不錯，但完整內容需訂閱 |

---

## 第二部分：其他語言來源

### 西班牙文
| 服務名稱 | URI | License | Lectionary |
|---------|-----|---------|-----------|
| Aciprensa - Lecturas del Día | https://www.aciprensa.com/ | 免費 | ✅ |
| Catholic.net - Lecturas del Día | https://www.catholic.net/ | 免費 | ✅ |
| Celebratemass.com (Hispanic Mass) | https://www.celebratemass.com/ | 免費（芝加哥總教區維護） | ✅ |

### 法文
| 服務名稱 | URI | License | Lectionary |
|---------|-----|---------|-----------|
| Messe.info | https://www.messe.info/ | 免費 | ✅ |
| Notre-Dame.org | https://www.notredame.org/ | 免費 | ✅ |

### 意大利文
| 服務名稱 | URI | License | Lectionary |
|---------|-----|---------|-----------|
| Parola Unisce | https://www.parolaunisce.it/ | 免費 | ✅ |
| Avvenire | https://www.avvenire.it/ | 免費（天主教報紙） | ✅ |

### 葡萄牙文
| 服務名稱 | URI | License | Lectionary |
|---------|-----|---------|-----------|
| CNBB 每日讀經 | https://www.cnbb.org.br/ | 免費（巴西主教團官方） | ✅ |

### 德文
| 服務名稱 | URI | License | Lectionary |
|---------|-----|---------|-----------|
| Deutsche Bibelgesellschaft / DBK | https://www.dbg-katholisch.de/ | 免費（德國主教團官方） | ✅ |

### 波蘭文
| 服務名稱 | URI | License | Lectionary |
|---------|-----|---------|-----------|
| eKai.pl | https://www.ekai.pl/ | 免費（官方教會新聞） | ✅ |
| Kosciół.pl | https://www.kosciol.pl/ | 免費 | ✅ |

### 拉丁文
| 服務名稱 | URI | License | Lectionary |
|---------|-----|---------|-----------|
| Divine Officium (St. Benoit) | https://www.divinumofficium.org/ | 免費 | ✅ |
| SanctaMissa.org | https://www.sanctamissa.org/ | 免費（脫利騰彌撒） | ✅ |

---

## 第三部分：中文來源

### 現有資源

| 服務名稱 | URI | 語言 | 內容 | License | Lectionary |
|---------|-----|------|------|---------|-----------|
| FHL 思高譯本聖經 | https://bible.fhl.net/ | 繁體中文 | **聖經原文**，可按章節查詢 | 免費（研究用） | ❌ 只有聖經章節，無禮儀日曆 |
| 思高學會 | https://www.sikong.tw/ | 繁體中文 | 聖經文本 | 免費（研究用） | ❌ |
| 天主教在線 | https://www.catholic.org.tw/ | 繁體中文 | 教會資訊、新聞 | 免費 | ❌ 無每日讀經功能 |
| 公教報 | https://kkp.org.hk/ | 繁體中文（粵語語境） | 香港天主教報章 | 免費 | ❌ 無結構化每日讀經 |
| 公教真理學會 | https://www.kkcpr.org/ | 繁體中文 | 靈修讀物 | 免費 | ❌ |

### 評估

**中文世界目前沒有免費的天主教每日禮儀讀經系統。**

FHL 提供的是聖經原文，不是「每日靈修禱文」。沒有任何一個已知的中文來源同時具備：
- ✅ 禮儀日曆（Lectionary Number）
- ✅ 每日讀經章節
- ✅ 靈修導讀或引導祈禱
- ✅ 可供機器讀取的格式

---

## 第四部分：License 分析

### 可安全使用的（公共領域 / 寬鬆 License）
- **iBreviary 部分內容**：部分為 Creative Commons（需確認是哪部分）
- **各國主教團官方來源**：通常允許私人/堂區使用，但未明確授權商業或再散佈

### 需要進一步確認 / 申請許可的
- **USCCB**：私人使用免費，但未授權公開散佈每日讀經內容
- **DivineOffice.org**：個人使用免費，商業用途需授權

### 商業 / 封閉 License（不能直接用）
- **Magnificat**：全部內容版權所有，需付費訂閱
- **Universalis**：商業軟件，需訂閱
- **Word Among Us**：完整內容需訂閱

### 關鍵 insight
> 天主教禮儀讀經的**內容本身**（聖經章節、詩篇）在禮儀年是標準化的，**不受版權限制**。但**導讀、靈修、禱詞**往往是受版權保護的。
>
> 因此，「用 Lectionary Number 抓取聖經經文」是乾淨的做法，但加上「靈修導讀」就需要小心 license。

---

## 第五部分：我們現有的系統

| 組件 | 目前狀態 | License |
|------|---------|---------|
| USCCB（參考來源）| ✅ 正在使用 | 私人使用免費 |
| FHL 思高譯本（聖經經文）| ✅ 正在使用 | 免費（研究用） |
| Lectionary Number 對應 | ✅ 可行 | — |
| 繁/簡體中文輸出 | ✅ 已實現 | — |
| 靈修導讀問題 | ❌ 還沒有 | — |
| 引導祈禱文 | ❌ 還沒有 | — |
| 聖人日曆 | ❌ 還沒有 | — |

---

## 結論：缺口分析

| 功能 | 英文世界 | 中文世界 |
|------|---------|---------|
| 每日聖言讀經 | ✅ 大量免費 | ⚠️ 只有聖經文本 |
| 完整 Divinum Officium | ✅ 多個來源 | ❌ 沒有 |
| 靈修導讀/默想 | ✅ 付費可獲得 | ❌ 沒有 |
| 聖人日曆 | ✅ 免費可用 | ❌ 沒有 |
| 禮儀年導覽 | ✅ 免費可用 | ❌ 沒有 |
| 中文輸出 | ✅ 有翻譯 | — |

---

## 下一步行動

1. [ ] 向 USCCB 確認：使用其 Lectionary Number + 鏈接回 USCCB 是否可接受
2. [ ] 向 iBreviary 確認：Creative Commons 的範圍和具體 license 條款
3. [ ] 研究中文聖人日曆數據來源
4. [ ] 研究如何取得禮儀年數據（將臨期/聖誕期/四旬期/復活期）

---

*最後更新：2026-04-18 — 初步研究完成*
