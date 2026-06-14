from __future__ import annotations

import os
from pathlib import Path
from flask import Flask, render_template, send_from_directory, abort

BASE_DIR = Path(__file__).resolve().parent
PDF_FILES = {
    "report": "十大機器學習演算法完整研讀報告_修訂版_v10.pdf",
    "dialogue": "對話紀錄_十大機器學習演算法.pdf",
}

ALGORITHMS = [
    {
        "slug": "linear-regression",
        "name": "線性迴歸",
        "tag": "Linear Regression",
        "image": "diagrams/linear-regression.svg",
        "summary": "用一條線或超平面描述特徵與連續目標值的關係，適合建立可解釋的基準模型。",
        "uses": "房價、銷售額、成本、趨勢預測",
        "principle": "以最小化預測值與真實值之間的平方誤差為目標，找出一組權重與截距，讓模型能用線性關係描述資料趨勢。",
        "case": "房仲可以用坪數、屋齡、地段分數預測房價，並透過係數理解每個因素對價格的影響方向。",
        "python": "from sklearn.linear_model import LinearRegression\n\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)",
        "check": "為什麼線性迴歸常用均方誤差作為訓練目標？",
    },
    {
        "slug": "logistic-regression",
        "name": "邏輯迴歸",
        "tag": "Logistic Regression",
        "image": "diagrams/logistic-regression.svg",
        "summary": "把輸入轉成類別機率，常用於二元或多類別分類，是分類任務的清楚起點。",
        "uses": "是否流失、是否核准、疾病風險、垃圾郵件",
        "principle": "先計算線性分數，再透過 sigmoid 或 softmax 轉成機率；訓練時調整參數，讓正確類別的機率提高。",
        "case": "訂閱制產品可用登入頻率、使用時長、客服紀錄預測使用者是否可能流失，提早安排挽留方案。",
        "python": "from sklearn.linear_model import LogisticRegression\n\nmodel = LogisticRegression(max_iter=1000)\nmodel.fit(X_train, y_train)\nproba = model.predict_proba(X_test)",
        "check": "邏輯迴歸輸出的機率門檻如果從 0.5 改成 0.7，可能會如何影響召回率？",
    },
    {
        "slug": "decision-tree",
        "name": "決策樹",
        "tag": "Decision Tree",
        "image": "diagrams/decision-tree.svg",
        "summary": "透過一連串條件分裂資料，形成容易閱讀的判斷規則。",
        "uses": "規則萃取、風險分群、客服分流",
        "principle": "每次選擇最能降低混亂程度的特徵切分資料，例如降低 Gini impurity 或 entropy，直到達到停止條件。",
        "case": "客服系統可用問題類型、會員等級、等待時間建立分流規則，把案件送到合適團隊。",
        "python": "from sklearn.tree import DecisionTreeClassifier\n\nmodel = DecisionTreeClassifier(max_depth=4)\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)",
        "check": "限制決策樹的最大深度，主要是在降低哪一種風險？",
    },
    {
        "slug": "random-forest",
        "name": "隨機森林",
        "tag": "Random Forest",
        "image": "diagrams/random-forest.svg",
        "summary": "整合多棵決策樹降低過度擬合，通常在表格資料上有穩定表現。",
        "uses": "信用評分、重要特徵分析、分類與回歸",
        "principle": "用 bootstrap 抽樣建立多棵樹，且每次分裂只看部分特徵；最後透過投票或平均整合結果，降低單棵樹的不穩定。",
        "case": "銀行可用收入、負債比、信用歷史、交易行為預測違約風險，並查看特徵重要性。",
        "python": "from sklearn.ensemble import RandomForestClassifier\n\nmodel = RandomForestClassifier(n_estimators=200, random_state=42)\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)",
        "check": "隨機森林為什麼通常比單一決策樹更不容易過度擬合？",
    },
    {
        "slug": "svm",
        "name": "支援向量機",
        "tag": "SVM",
        "image": "diagrams/svm.svg",
        "summary": "尋找能最大化分類邊界的決策面，也能透過 kernel 處理非線性資料。",
        "uses": "文字分類、影像辨識、小中型高維資料",
        "principle": "尋找一條分隔線或超平面，使不同類別到邊界的距離最大；距離邊界最近的點稱為支援向量。",
        "case": "在文字分類中，可將文件轉成 TF-IDF 特徵，再用 SVM 區分主題或情緒。",
        "python": "from sklearn.svm import SVC\n\nmodel = SVC(kernel=\"rbf\", C=1.0, gamma=\"scale\")\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)",
        "check": "SVM 的 kernel 技巧解決了哪一類資料不容易線性分開的問題？",
    },
    {
        "slug": "knn",
        "name": "K 近鄰",
        "tag": "KNN",
        "image": "diagrams/knn.svg",
        "summary": "用最接近的 K 個樣本投票或平均，概念直覺但對距離尺度很敏感。",
        "uses": "推薦、相似案例查找、快速原型分類",
        "principle": "不先建立複雜參數模型，而是在預測時找出距離新資料最近的 K 個訓練樣本，依多數決或平均給出答案。",
        "case": "電商可根據使用者瀏覽與購買向量，找出相似使用者，推薦他們也喜歡的商品。",
        "python": "from sklearn.neighbors import KNeighborsClassifier\n\nmodel = KNeighborsClassifier(n_neighbors=5)\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)",
        "check": "為什麼使用 KNN 前通常需要先做特徵標準化？",
    },
    {
        "slug": "k-means",
        "name": "K 平均分群",
        "tag": "K-Means",
        "image": "diagrams/k-means.svg",
        "summary": "把資料依距離分成 K 群，適合探索沒有標籤的資料結構。",
        "uses": "客群分群、影像壓縮、行為模式探索",
        "principle": "先指定 K 個群中心，再反覆把樣本分配到最近中心並更新中心位置，直到群中心穩定。",
        "case": "行銷團隊可用消費頻率、客單價、最近購買時間將客戶分群，設計不同促銷策略。",
        "python": "from sklearn.cluster import KMeans\n\nmodel = KMeans(n_clusters=3, n_init=\"auto\", random_state=42)\nlabels = model.fit_predict(X)",
        "check": "如果 K 值選得太大，分群結果可能會出現什麼問題？",
    },
    {
        "slug": "pca",
        "name": "主成分分析",
        "tag": "PCA",
        "image": "diagrams/pca.svg",
        "summary": "把高維資料投影到最能保留變異的方向，常用於降維與視覺化。",
        "uses": "資料壓縮、特徵工程、雜訊降低",
        "principle": "找出資料變異最大的正交方向，將原始特徵轉換到較少的主成分上，以保留主要資訊並降低維度。",
        "case": "資料科學家可把數十個客戶行為指標降到兩個主成分，在圖上觀察群集與離群點。",
        "python": "from sklearn.decomposition import PCA\n\npca = PCA(n_components=2)\nX_2d = pca.fit_transform(X_scaled)\nprint(pca.explained_variance_ratio_)",
        "check": "PCA 的 explained variance ratio 可以幫助我們判斷什麼？",
    },
    {
        "slug": "naive-bayes",
        "name": "樸素貝氏",
        "tag": "Naive Bayes",
        "image": "diagrams/naive-bayes.svg",
        "summary": "以貝氏定理與條件獨立假設進行分類，速度快且常是文字任務強基準。",
        "uses": "垃圾郵件、情緒分析、文件分類",
        "principle": "根據各類別的先驗機率與特徵出現機率計算後驗機率，選擇最可能的類別；樸素假設是特徵彼此條件獨立。",
        "case": "電子郵件系統可用關鍵字出現機率判斷信件是否為垃圾郵件，快速處理大量文本。",
        "python": "from sklearn.naive_bayes import MultinomialNB\n\nmodel = MultinomialNB()\nmodel.fit(X_train_counts, y_train)\npred = model.predict(X_test_counts)",
        "check": "樸素貝氏的「樸素」指的是哪一個核心假設？",
    },
    {
        "slug": "gradient-boosting",
        "name": "梯度提升",
        "tag": "Gradient Boosting",
        "image": "diagrams/gradient-boosting.svg",
        "summary": "逐步訓練弱模型修正前一輪錯誤，在結構化資料競賽與商業預測中很常見。",
        "uses": "排名、風險預測、需求預測、精準行銷",
        "principle": "模型一輪一輪加入新的弱學習器，每一輪都專注修正目前模型的殘差或損失梯度，逐步提升整體表現。",
        "case": "零售業可結合價格、節日、庫存、地區與歷史銷量，預測未來需求並安排補貨。",
        "python": "from sklearn.ensemble import GradientBoostingClassifier\n\nmodel = GradientBoostingClassifier(random_state=42)\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)",
        "check": "梯度提升的 learning_rate 太大時，模型可能會出現什麼現象？",
    },
]

CASE_STUDIES = {
    "linear-regression": {
        "case_detail": "以房價估算為例，團隊先收集坪數、屋齡、距離捷運、樓層與行政區等特徵，訓練後不只得到預測價格，也能用係數說明哪些因素推高或拉低估值。適合用在需要透明解釋的報價流程。",
        "case_metrics": [("估價誤差下降", 18), ("人工報價時間縮短", 72), ("主要解釋特徵", 5)],
    },
    "logistic-regression": {
        "case_detail": "在會員流失預測中，模型把使用頻率、最近登入、訂單間隔與客服紀錄轉成流失機率。營運人員可設定門檻，例如高於 0.7 就觸發優惠或人工關懷。",
        "case_metrics": [("高風險會員召回", 31), ("行銷名單縮減", 54), ("可行動門檻", 70)],
    },
    "decision-tree": {
        "case_detail": "客服分流可以把問題類型、客戶等級、等待時間與關鍵字轉成清楚規則。每個節點都是可解釋條件，管理者能檢查流程是否符合服務政策。",
        "case_metrics": [("首次分派正確率", 84), ("平均等待下降", 36), ("可讀規則數", 12)],
    },
    "random-forest": {
        "case_detail": "信用風險模型會從多棵樹整合決策，降低單一規則對異常資料的敏感度。模型也能產生特徵重要性，協助風控團隊理解主要風險來源。",
        "case_metrics": [("違約辨識提升", 22), ("模型穩定度", 88), ("重要特徵覆蓋", 9)],
    },
    "svm": {
        "case_detail": "文字分類常把文件轉成 TF-IDF 向量，再用 SVM 找出最大間隔邊界。當特徵很多、資料量中等時，它能建立穩定的主題或情緒分類器。",
        "case_metrics": [("分類精準度", 91), ("人工標記節省", 46), ("支援向量占比", 18)],
    },
    "knn": {
        "case_detail": "推薦系統可把使用者行為轉成向量，找出最相似的鄰居。若一位使用者和某些會員的瀏覽與購買模式接近，就能推薦鄰居喜歡但他尚未看過的商品。",
        "case_metrics": [("推薦點擊提升", 27), ("冷啟動可用性", 64), ("相似案例數", 5)],
    },
    "k-means": {
        "case_detail": "行銷團隊可用最近購買時間、購買頻率、客單價與品類偏好分群，形成高價值客、沉睡客、價格敏感客等群組，再安排不同溝通策略。",
        "case_metrics": [("分群輪廓分數", 62), ("活動轉換提升", 24), ("建議客群數", 4)],
    },
    "pca": {
        "case_detail": "當資料有數十個行為欄位時，PCA 可把資訊壓縮成少數主成分。分析者能用 2D 圖觀察群集、離群點，也能降低後續模型的訓練成本。",
        "case_metrics": [("保留變異量", 87), ("特徵維度下降", 80), ("視覺化維度", 2)],
    },
    "naive-bayes": {
        "case_detail": "垃圾郵件偵測會統計詞彙在垃圾信與正常信中的出現機率。即使假設簡化，它在大量文字場景仍很快，常作為文本分類的第一版基準模型。",
        "case_metrics": [("處理速度提升", 93), ("垃圾信攔截", 89), ("低成本基準", 76)],
    },
    "gradient-boosting": {
        "case_detail": "零售需求預測會逐輪修正前一版模型的誤差，整合節日、折扣、庫存、地區與歷史銷量。它適合表格資料，常用於銷售、風險與排序任務。",
        "case_metrics": [("需求誤差下降", 29), ("缺貨率下降", 17), ("預測穩定度", 86)],
    },
}

PRINCIPLE_GUIDES = {
    "linear-regression": {
        "steps": [("輸入特徵", "把坪數、屋齡、距離等欄位整理成 X。"), ("建立直線", "用權重與截距形成 y = wX + b。"), ("降低誤差", "反覆調整參數，使預測與真實值的平方誤差變小。")],
        "chart": [("線性關係", 82), ("可解釋性", 90), ("非線性彈性", 38)],
        "tip": "先看散佈圖是否接近直線趨勢；若殘差呈現明顯曲線，可能需要加入多項式特徵或改用非線性模型。",
    },
    "logistic-regression": {
        "steps": [("線性分數", "先把特徵加權成一個分數。"), ("機率轉換", "用 sigmoid 或 softmax 把分數壓到 0 到 1。"), ("門檻分類", "依任務成本設定機率門檻，例如 0.5 或 0.7。")],
        "chart": [("機率解釋", 88), ("分類基準", 84), ("複雜邊界", 42)],
        "tip": "邏輯迴歸不是直接畫出曲線回歸，而是用線性邊界分類；門檻調整會改變 precision 與 recall 的取捨。",
    },
    "decision-tree": {
        "steps": [("選切分欄位", "找出最能降低混亂程度的問題。"), ("分裂節點", "把資料依條件分成較純的子集合。"), ("形成規則", "從根節點到葉節點就是一條可讀的決策規則。")],
        "chart": [("可解釋性", 95), ("非線性能力", 76), ("穩定性", 48)],
        "tip": "樹太深會記住訓練資料細節；常用 max_depth、min_samples_leaf 讓規則保留泛化能力。",
    },
    "random-forest": {
        "steps": [("抽樣資料", "每棵樹看到不同的 bootstrap 樣本。"), ("隨機特徵", "每次切分只考慮部分欄位。"), ("整合投票", "分類取多數決，回歸取平均。")],
        "chart": [("穩定性", 90), ("特徵重要性", 82), ("單模型可讀性", 45)],
        "tip": "隨機森林靠多樣化的樹降低變異；樹越多通常越穩，但推論成本也會增加。",
    },
    "svm": {
        "steps": [("找分隔面", "尋找能區分類別的線或超平面。"), ("最大間隔", "讓邊界到最近樣本的距離最大。"), ("Kernel 映射", "必要時把資料映到高維空間處理非線性。")],
        "chart": [("高維表現", 86), ("間隔控制", 88), ("大資料速度", 44)],
        "tip": "C 控制錯分容忍度，gamma 控制 RBF kernel 的局部程度；兩者都會影響邊界是否太硬。",
    },
    "knn": {
        "steps": [("計算距離", "比較新樣本與訓練樣本的距離。"), ("找 K 個鄰居", "選出最近的 K 筆資料。"), ("投票或平均", "分類用多數決，回歸用平均。")],
        "chart": [("直覺性", 94), ("訓練速度", 92), ("預測成本", 38)],
        "tip": "KNN 對尺度非常敏感；使用前通常要標準化，否則數值大的欄位會支配距離。",
    },
    "k-means": {
        "steps": [("設定 K", "先決定要分成幾群。"), ("指派中心", "每筆資料分到最近的群中心。"), ("更新中心", "重新計算各群平均位置，直到收斂。")],
        "chart": [("探索分群", 88), ("速度", 82), ("非球狀群", 36)],
        "tip": "K-Means 假設群形狀大致接近圓球；若群形狀彎曲或密度差異大，效果會變差。",
    },
    "pca": {
        "steps": [("標準化", "先讓不同尺度的特徵可比較。"), ("找主軸", "尋找資料變異最大的正交方向。"), ("投影降維", "把資料轉到較少主成分上。")],
        "chart": [("降維壓縮", 90), ("視覺化", 84), ("語意直觀", 42)],
        "tip": "PCA 的主成分是原始特徵的線性組合；它保留變異量，但不一定保留最容易解釋的業務語意。",
    },
    "naive-bayes": {
        "steps": [("計算先驗", "估計每個類別原本出現的比例。"), ("估計特徵機率", "計算詞彙或特徵在各類別中的機率。"), ("比較後驗", "選擇後驗機率最高的類別。")],
        "chart": [("文字分類", 88), ("訓練速度", 96), ("特徵依賴處理", 35)],
        "tip": "條件獨立假設常不完全成立，但在文字計數特徵中仍常有很好的速度與基準表現。",
    },
    "gradient-boosting": {
        "steps": [("建立弱模型", "先用簡單模型得到初步預測。"), ("學習殘差", "下一棵樹專注修正前面犯的錯。"), ("逐步加總", "用 learning_rate 控制每一步修正幅度。")],
        "chart": [("表格資料表現", 92), ("調參彈性", 86), ("訓練成本", 54)],
        "tip": "learning_rate 越小通常越穩，但需要更多樹；若太大，模型可能快速過擬合或震盪。",
    },
}

CHECK_QUESTIONS = {
    "linear-regression": [
        {"question": "線性迴歸的係數代表什麼？", "answer": "在其他特徵不變時，某個特徵增加一單位，預測值平均改變多少。"},
        {"question": "殘差圖出現曲線形狀時可能代表什麼？", "answer": "資料關係可能不是線性的，可以考慮多項式特徵或非線性模型。"},
        {"question": "為什麼要注意共線性？", "answer": "高度相關的特徵會讓係數不穩定，解釋時容易誤判單一特徵的影響。"},
    ],
    "logistic-regression": [
        {"question": "邏輯迴歸輸出的值通常如何解讀？", "answer": "可解讀為樣本屬於某類別的機率。"},
        {"question": "提高分類門檻通常會造成什麼影響？", "answer": "預測為正類會更保守，precision 可能上升，recall 可能下降。"},
        {"question": "C 值變大代表正則化變強還是變弱？", "answer": "C 越大，正則化越弱，模型更容易貼近訓練資料。"},
    ],
    "decision-tree": [
        {"question": "決策樹每次切分資料的目標是什麼？", "answer": "讓切分後的子節點更純，降低 Gini 或 entropy 等混亂程度。"},
        {"question": "樹太深可能造成什麼問題？", "answer": "容易記住訓練資料細節，造成過度擬合。"},
        {"question": "決策樹為什麼容易解釋？", "answer": "每條根到葉的路徑都是一串明確的 if-then 規則。"},
    ],
    "random-forest": [
        {"question": "隨機森林如何降低單棵樹的不穩定？", "answer": "用不同資料樣本和特徵建立多棵樹，再投票或平均。"},
        {"question": "n_estimators 增加通常會帶來什麼取捨？", "answer": "結果更穩定，但訓練與推論成本也會增加。"},
        {"question": "特徵重要性可以用來做什麼？", "answer": "協助理解哪些欄位對模型判斷最有影響。"},
    ],
    "svm": [
        {"question": "SVM 的 margin 是什麼？", "answer": "分類邊界到最近樣本點之間的距離。"},
        {"question": "Kernel 的用途是什麼？", "answer": "讓模型能處理原始空間中不容易線性分開的資料。"},
        {"question": "C 值太大可能有什麼風險？", "answer": "模型會更努力分類正確訓練資料，可能過度擬合。"},
    ],
    "knn": [
        {"question": "KNN 為什麼需要特徵標準化？", "answer": "距離會受特徵尺度影響，尺度大的欄位可能支配結果。"},
        {"question": "K 值太小可能造成什麼現象？", "answer": "模型容易受雜訊或離群點影響。"},
        {"question": "KNN 的訓練快但預測慢，原因是什麼？", "answer": "它幾乎不建參數模型，預測時才需要計算與訓練樣本的距離。"},
    ],
    "k-means": [
        {"question": "K-Means 的 K 代表什麼？", "answer": "預先指定要分成幾個群。"},
        {"question": "初始中心會影響結果嗎？", "answer": "會，因此常用多次初始化或 k-means++ 降低不穩定。"},
        {"question": "K-Means 不適合哪類群形狀？", "answer": "不規則、彎曲、密度差異很大的群通常較不適合。"},
    ],
    "pca": [
        {"question": "PCA 為什麼常需要標準化？", "answer": "不同尺度會影響變異量計算，尺度大的特徵會主導主成分。"},
        {"question": "explained variance ratio 表示什麼？", "answer": "某些主成分保留了原始資料多少比例的變異。"},
        {"question": "PCA 是監督式還是非監督式方法？", "answer": "非監督式，因為它不使用目標標籤。"},
    ],
    "naive-bayes": [
        {"question": "樸素貝氏的核心假設是什麼？", "answer": "在給定類別後，各特徵彼此條件獨立。"},
        {"question": "alpha 平滑的目的為何？", "answer": "避免某些未出現詞彙讓機率變成 0。"},
        {"question": "它為什麼常用於文字分類？", "answer": "文字可轉成詞頻特徵，模型訓練快且基準效果常不錯。"},
    ],
    "gradient-boosting": [
        {"question": "Gradient Boosting 每一輪主要在學什麼？", "answer": "學習目前模型尚未處理好的錯誤或殘差。"},
        {"question": "learning_rate 太大可能造成什麼問題？", "answer": "每步修正太激烈，可能過擬合或表現震盪。"},
        {"question": "為什麼它在表格資料常表現好？", "answer": "它能逐步捕捉非線性與特徵交互作用，對結構化特徵很有彈性。"},
    ],
}

DEMO_SETTINGS = {
    "linear-regression": {
        "parameter": "feature_count",
        "label": "特徵數量",
        "min": 1,
        "max": 8,
        "step": 1,
        "default": 4,
        "unit": " 個",
        "low": "模型簡單、可能欠擬合",
        "high": "資訊較完整、需留意共線性",
        "template": "from sklearn.linear_model import LinearRegression\n\nfeatures = select_features(k={value})\nmodel = LinearRegression()\nmodel.fit(features, y_train)\npred = model.predict(X_test_selected)\nprint(\"estimated_rmse\", {metric})",
    },
    "logistic-regression": {
        "parameter": "C",
        "label": "正則化強度 C",
        "min": 0.1,
        "max": 10,
        "step": 0.1,
        "default": 1,
        "unit": "",
        "low": "正則化較強、模型保守",
        "high": "正則化較弱、邊界更貼近資料",
        "template": "from sklearn.linear_model import LogisticRegression\n\nmodel = LogisticRegression(C={value}, max_iter=1000)\nmodel.fit(X_train, y_train)\nproba = model.predict_proba(X_test)\nprint(\"validation_score\", {metric})",
    },
    "decision-tree": {
        "parameter": "max_depth",
        "label": "最大深度",
        "min": 1,
        "max": 10,
        "step": 1,
        "default": 4,
        "unit": " 層",
        "low": "規則少、解釋容易",
        "high": "規則細、較可能過度擬合",
        "template": "from sklearn.tree import DecisionTreeClassifier\n\nmodel = DecisionTreeClassifier(max_depth={value}, random_state=42)\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)\nprint(\"validation_score\", {metric})",
    },
    "random-forest": {
        "parameter": "n_estimators",
        "label": "樹的數量",
        "min": 20,
        "max": 300,
        "step": 20,
        "default": 160,
        "unit": " 棵",
        "low": "訓練快、變異較高",
        "high": "預測穩定、成本較高",
        "template": "from sklearn.ensemble import RandomForestClassifier\n\nmodel = RandomForestClassifier(n_estimators={value}, random_state=42)\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)\nprint(\"validation_score\", {metric})",
    },
    "svm": {
        "parameter": "C",
        "label": "間隔懲罰 C",
        "min": 0.1,
        "max": 10,
        "step": 0.1,
        "default": 1,
        "unit": "",
        "low": "間隔較寬、容忍錯分",
        "high": "邊界較硬、重視訓練正確",
        "template": "from sklearn.svm import SVC\n\nmodel = SVC(kernel=\"rbf\", C={value}, gamma=\"scale\")\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)\nprint(\"validation_score\", {metric})",
    },
    "knn": {
        "parameter": "n_neighbors",
        "label": "鄰居數 K",
        "min": 1,
        "max": 15,
        "step": 2,
        "default": 5,
        "unit": " 位",
        "low": "反應靈敏、易受雜訊影響",
        "high": "較平滑、可能忽略局部差異",
        "template": "from sklearn.neighbors import KNeighborsClassifier\n\nmodel = KNeighborsClassifier(n_neighbors={value})\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)\nprint(\"validation_score\", {metric})",
    },
    "k-means": {
        "parameter": "n_clusters",
        "label": "分群數 K",
        "min": 2,
        "max": 8,
        "step": 1,
        "default": 4,
        "unit": " 群",
        "low": "群組概略、容易解釋",
        "high": "分群細緻、可能切太碎",
        "template": "from sklearn.cluster import KMeans\n\nmodel = KMeans(n_clusters={value}, n_init=\"auto\", random_state=42)\nlabels = model.fit_predict(X)\nprint(\"silhouette_like_score\", {metric})",
    },
    "pca": {
        "parameter": "n_components",
        "label": "主成分數",
        "min": 1,
        "max": 8,
        "step": 1,
        "default": 2,
        "unit": " 維",
        "low": "壓縮強、資訊損失較多",
        "high": "資訊保留高、視覺化較難",
        "template": "from sklearn.decomposition import PCA\n\npca = PCA(n_components={value})\nX_reduced = pca.fit_transform(X_scaled)\nprint(\"explained_variance\", {metric})",
    },
    "naive-bayes": {
        "parameter": "alpha",
        "label": "平滑係數 alpha",
        "min": 0.1,
        "max": 2,
        "step": 0.1,
        "default": 1,
        "unit": "",
        "low": "較相信訓練詞頻",
        "high": "降低罕見詞影響",
        "template": "from sklearn.naive_bayes import MultinomialNB\n\nmodel = MultinomialNB(alpha={value})\nmodel.fit(X_train_counts, y_train)\npred = model.predict(X_test_counts)\nprint(\"validation_score\", {metric})",
    },
    "gradient-boosting": {
        "parameter": "learning_rate",
        "label": "學習率",
        "min": 0.01,
        "max": 0.3,
        "step": 0.01,
        "default": 0.1,
        "unit": "",
        "low": "更新穩定、需要更多樹",
        "high": "學習快速、可能震盪",
        "template": "from sklearn.ensemble import GradientBoostingClassifier\n\nmodel = GradientBoostingClassifier(learning_rate={value}, random_state=42)\nmodel.fit(X_train, y_train)\npred = model.predict(X_test)\nprint(\"validation_score\", {metric})",
    },
}

for algorithm in ALGORITHMS:
    algorithm.update(CASE_STUDIES[algorithm["slug"]])
    algorithm["principle_guide"] = PRINCIPLE_GUIDES[algorithm["slug"]]
    algorithm["check_questions"] = CHECK_QUESTIONS[algorithm["slug"]]
    demo = DEMO_SETTINGS[algorithm["slug"]]
    demo["slug"] = algorithm["slug"]
    demo["variables"] = [
        {
            "key": demo["parameter"],
            "label": demo["label"],
            "min": demo["min"],
            "max": demo["max"],
            "step": demo["step"],
            "default": demo["default"],
            "unit": demo["unit"],
            "low": demo["low"],
            "high": demo["high"],
        },
        {
            "key": "sample_count",
            "label": "訓練資料量",
            "min": 40,
            "max": 240,
            "step": 20,
            "default": 120,
            "unit": " 筆",
            "low": "資料少、模型較不穩",
            "high": "資料多、趨勢較可靠",
        },
        {
            "key": "noise_level",
            "label": "資料雜訊",
            "min": 0,
            "max": 40,
            "step": 5,
            "default": 15,
            "unit": "%",
            "low": "資料乾淨、模式明顯",
            "high": "資料分散、判斷較難",
        },
    ]
    algorithm["demo"] = demo

app = Flask(__name__)


@app.route("/")
def index():
    pdfs = [
        {"key": key, "filename": filename, "size_mb": round((BASE_DIR / filename).stat().st_size / 1024 / 1024, 1)}
        for key, filename in PDF_FILES.items()
        if (BASE_DIR / filename).exists()
    ]
    return render_template("index.html", algorithms=ALGORITHMS, pdfs=pdfs)


@app.route("/pdf/<key>")
def pdf(key: str):
    filename = PDF_FILES.get(key)
    if not filename or not (BASE_DIR / filename).exists():
        abort(404)
    return send_from_directory(BASE_DIR, filename, mimetype="application/pdf", as_attachment=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
