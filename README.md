# 十大機器學習演算法學習網站

這是一個以 Streamlit 建置的互動式學習網站，內容依據「十大機器學習演算法完整研讀報告」整理，將常見機器學習演算法轉成可瀏覽、可比較、可練習的網頁教材。

## Demo

[https://wh5-10algorithms-7cwn4izk2dknbjsxfaoxbi.streamlit.app/](https://wh5-10algorithms-7cwn4izk2dknbjsxfaoxbi.streamlit.app/)

## 專案特色

- 總覽頁：以卡片方式快速瀏覽十大機器學習演算法。
- 深入學習：從總覽卡片進入單一演算法頁，查看原理、案例、參數模擬與檢核題。
- 比較矩陣：整理各演算法的類型、難度、適合資料、主要優勢與注意事項。
- 練習測驗：透過題目與答案檢查演算法核心概念。
- 研讀報告 PDF：提供完整報告與對話紀錄的下載與頁面預覽。
- 互動式介面：包含 sidebar 導覽、卡片跳轉、參數 slider、進度條與 PDF viewer。

## 涵蓋演算法

1. 線性迴歸 Linear Regression
2. 邏輯迴歸 Logistic Regression
3. 決策樹 Decision Tree
4. 隨機森林 Random Forest
5. 支援向量機 SVM
6. K 近鄰 KNN
7. K 平均分群 K-Means
8. 主成分分析 PCA
9. 樸素貝氏 Naive Bayes
10. 梯度提升 Gradient Boosting

## 主要檔案

- `streamlit_app.py`：Streamlit 互動式學習網站主程式。
- `app.py`：整理演算法資料、案例、測驗題與 Flask 版本入口。
- `static/`：首頁主視覺、演算法 SVG 圖示與前端資源。
- `templates/`：Flask 版本模板。
- `十大機器學習演算法完整研讀報告_修訂版_v10.pdf`：完整研讀報告。
- `對話紀錄_十大機器學習演算法.pdf`：相關對話紀錄。
- `requirements.txt`：部署與執行所需套件。

## 本機執行

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

啟動後可在瀏覽器開啟 Streamlit 顯示的本機網址。
