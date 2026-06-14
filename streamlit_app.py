from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from app import ALGORITHMS, BASE_DIR, PDF_FILES


st.set_page_config(
    page_title="十大機器學習演算法學習網站",
    page_icon="ML",
    layout="wide",
    initial_sidebar_state="expanded",
)


STATIC_DIR = BASE_DIR / "static"
HERO_IMAGE = STATIC_DIR / "hero-ai.png"
PAGES = ["總覽", "比較矩陣", "練習測驗", "研讀報告 PDF"]


MODEL_FAMILIES = {
    "linear-regression": "監督式學習 / 回歸",
    "logistic-regression": "監督式學習 / 分類",
    "decision-tree": "監督式學習 / 分類與回歸",
    "random-forest": "集成學習 / Bagging",
    "svm": "監督式學習 / 最大間隔",
    "knn": "監督式學習 / 距離模型",
    "k-means": "非監督式學習 / 分群",
    "pca": "非監督式學習 / 降維",
    "naive-bayes": "監督式學習 / 機率模型",
    "gradient-boosting": "集成學習 / Boosting",
}

MODEL_PROFILE = {
    "linear-regression": {
        "difficulty": "入門",
        "data": "連續數值目標、關係近似線性",
        "strength": "速度快、係數容易解釋、適合基準線",
        "watch": "離群值、非線性關係、共線性",
    },
    "logistic-regression": {
        "difficulty": "入門",
        "data": "二元或多類別標籤、需要機率分數",
        "strength": "輸出可解釋機率、門檻容易調整",
        "watch": "特徵尺度、類別不平衡、線性邊界限制",
    },
    "decision-tree": {
        "difficulty": "入門",
        "data": "表格資料、需要明確規則",
        "strength": "流程像 if-then，易向業務說明",
        "watch": "樹太深容易過度擬合",
    },
    "random-forest": {
        "difficulty": "中階",
        "data": "多欄位表格資料、希望結果穩定",
        "strength": "降低單棵樹變異，可看特徵重要性",
        "watch": "單一預測路徑較難解釋、模型較大",
    },
    "svm": {
        "difficulty": "中階",
        "data": "中小型資料、高維特徵",
        "strength": "最大化分類間隔，kernel 能處理非線性",
        "watch": "大資料訓練成本、參數 C 與 gamma",
    },
    "knn": {
        "difficulty": "入門",
        "data": "相似度有意義、特徵尺度已整理",
        "strength": "概念直覺，能做相似案例查找",
        "watch": "預測時成本高、對尺度與雜訊敏感",
    },
    "k-means": {
        "difficulty": "入門",
        "data": "沒有標籤、想探索群組",
        "strength": "速度快，適合客群與行為分群",
        "watch": "K 值選擇、非球狀或密度差異群",
    },
    "pca": {
        "difficulty": "中階",
        "data": "高維數值特徵、想壓縮或視覺化",
        "strength": "保留主要變異，降低維度與雜訊",
        "watch": "主成分不一定有直觀業務語意",
    },
    "naive-bayes": {
        "difficulty": "入門",
        "data": "文字、計數、稀疏特徵",
        "strength": "訓練極快，常是文字分類強基準",
        "watch": "條件獨立假設過於簡化",
    },
    "gradient-boosting": {
        "difficulty": "進階",
        "data": "結構化資料、追求高預測力",
        "strength": "逐步修正錯誤，能捕捉非線性互動",
        "watch": "調參較多、過擬合與訓練成本",
    },
}


def image_data_uri(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    mime = "image/svg+xml" if suffix == "svg" else f"image/{suffix}"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


@st.cache_data(show_spinner=False)
def cached_image_data_uri(path_text: str) -> str:
    return image_data_uri(Path(path_text))


@st.cache_data(show_spinner=False)
def cached_pdf_data_uri(path_text: str) -> str:
    path = Path(path_text)
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:application/pdf;base64,{encoded}"


def css() -> None:
    st.markdown(
        """
<style>
  :root {
    --bg: #f6f7f9;
    --panel: #ffffff;
    --panel-soft: #eef6f4;
    --ink: #18202a;
    --muted: #647181;
    --line: #dbe2ea;
    --accent: #087f8c;
    --accent-deep: #075b63;
    --warm: #b86216;
    --warm-soft: #fff4e6;
  }
  .stApp {
    background: var(--bg);
    color: var(--ink);
  }
  .main .block-container {
    max-width: 1220px;
    padding-top: 1.3rem;
    padding-bottom: 3rem;
  }
  section[data-testid="stSidebar"] {
    width: 250px !important;
    min-width: 250px !important;
    max-width: 250px !important;
    background: #ffffff;
    border-right: 1px solid var(--line);
  }
  section[data-testid="stSidebar"] > div {
    width: 250px !important;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] {
    margin-top: 8px;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    min-height: 46px;
    justify-content: flex-start;
    padding: .62rem .75rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #f8fafc;
    color: var(--ink);
    font-weight: 700;
    box-shadow: 0 1px 0 rgba(24, 32, 42, .03);
    transition: transform .16s ease, border-color .16s ease, background .16s ease, box-shadow .16s ease;
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    transform: translateX(4px);
    border-color: #86c8c5;
    background: #eef9f7;
    color: var(--accent-deep);
    box-shadow: 0 8px 22px rgba(8, 127, 140, .11);
  }
  section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
    border-color: var(--accent);
    background: linear-gradient(135deg, #e9f8f5, #fff7eb);
    color: var(--accent-deep);
    box-shadow: inset 4px 0 0 var(--accent), 0 8px 22px rgba(8, 127, 140, .12);
    font-weight: 800;
  }
  h1, h2, h3 {
    letter-spacing: 0;
  }
  .hero {
    position: relative;
    min-height: 390px;
    border-radius: 8px;
    overflow: hidden;
    background: #111827;
    margin-bottom: 1.2rem;
  }
  .hero img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .hero:after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(8, 17, 28, .92), rgba(8, 17, 28, .62) 50%, rgba(8, 17, 28, .18));
  }
  .hero-content {
    position: relative;
    z-index: 1;
    width: min(740px, 100%);
    padding: 70px 52px 86px;
    color: white;
  }
  .eyebrow {
    margin: 0 0 .65rem;
    color: #f1b35b;
    font-size: .84rem;
    font-weight: 800;
    text-transform: uppercase;
  }
  .hero h1 {
    margin: 0 0 .9rem;
    font-size: clamp(2.25rem, 6vw, 4.7rem);
    line-height: 1.02;
  }
  .hero p.copy {
    color: rgba(255,255,255,.86);
    font-size: 1.06rem;
    line-height: 1.75;
    margin: 0;
    max-width: 670px;
  }
  .metric-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: .8rem;
    margin: .75rem 0 1.25rem;
  }
  .metric {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: .95rem 1rem;
  }
  .metric strong {
    display: block;
    font-size: 1.55rem;
    color: var(--accent-deep);
    line-height: 1.2;
  }
  .metric span {
    color: var(--muted);
    font-size: .88rem;
  }
  .algo-card {
    min-height: 268px;
    background: transparent;
  }
  .main div[data-testid="stButton"] {
    margin-top: 10px;
  }
  .main div[data-testid="stButton"] > button {
    border-radius: 8px;
    border-color: #087f8c;
    background: #087f8c;
    color: #ffffff;
    font-weight: 800;
    transition: transform .16s ease, border-color .16s ease, background .16s ease, box-shadow .16s ease;
  }
  .main div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    border-color: #075b63;
    background: #075b63;
    color: #ffffff;
    box-shadow: 0 8px 18px rgba(8, 127, 140, .12);
  }
  .main div[data-testid="stButton"] > button:focus,
  .main div[data-testid="stButton"] > button:active {
    color: #ffffff;
  }
  .algo-card img {
    width: 100%;
    height: 92px;
    object-fit: contain;
    margin-bottom: .75rem;
    background: #f9fbfc;
    border-radius: 6px;
  }
  .algo-card h3 {
    margin: .1rem 0 .25rem;
    font-size: 1.12rem;
  }
  .tag {
    display: inline-flex;
    align-items: center;
    border: 1px solid #b7deda;
    color: #075b63;
    background: #eef9f7;
    border-radius: 999px;
    padding: .16rem .55rem;
    font-size: .76rem;
    font-weight: 700;
    margin-bottom: .55rem;
  }
  .muted {
    color: var(--muted);
    line-height: 1.65;
  }
  .section-note {
    color: var(--muted);
    margin-top: -.35rem;
    margin-bottom: 1rem;
  }
  .info-panel {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 1rem 1.05rem;
    height: 100%;
  }
  .info-panel h4 {
    margin: 0 0 .45rem;
    font-size: .95rem;
    color: #1f2937;
  }
  .flow-step {
    display: grid;
    grid-template-columns: 34px 1fr;
    gap: .7rem;
    align-items: start;
    padding: .72rem 0;
    border-bottom: 1px solid var(--line);
  }
  .flow-step:last-child {
    border-bottom: 0;
  }
  .step-no {
    width: 34px;
    height: 34px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: var(--accent);
    color: #fff;
    font-weight: 800;
  }
  .bar {
    height: 12px;
    background: #e5ebf1;
    border-radius: 999px;
    overflow: hidden;
    margin: .28rem 0 .72rem;
  }
  .bar span {
    display: block;
    height: 100%;
    background: linear-gradient(90deg, var(--accent), #d68a2f);
    border-radius: 999px;
  }
  .callout {
    background: var(--warm-soft);
    border: 1px solid #f1cfaa;
    border-radius: 8px;
    padding: .9rem 1rem;
    color: #4a2d12;
    line-height: 1.65;
  }
  .pdf-frame {
    border: 1px solid var(--line);
    border-radius: 8px;
    overflow: hidden;
    background: white;
  }
  div[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 8px;
  }
  @media (max-width: 820px) {
    .hero {
      min-height: 430px;
    }
    .hero-content {
      padding: 54px 24px 74px;
    }
    .metric-row {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
  @media (max-width: 560px) {
    .metric-row {
      grid-template-columns: 1fr;
    }
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def selected_algorithm(slug: str) -> dict[str, Any]:
    return next(item for item in ALGORITHMS if item["slug"] == slug)


def init_state() -> None:
    st.session_state.setdefault("active_page", "總覽")
    st.session_state.setdefault("selected_slug", ALGORITHMS[0]["slug"])


def set_page(page: str) -> None:
    st.session_state["active_page"] = page


def open_algorithm(slug: str) -> None:
    st.session_state["selected_slug"] = slug
    st.session_state["active_page"] = "深入學習"


def card_html(algo: dict[str, Any]) -> str:
    image_path = STATIC_DIR / algo["image"]
    image_src = cached_image_data_uri(str(image_path)) if image_path.exists() else ""
    return f"""
<div class="algo-card">
  {'<img src="' + image_src + '" alt="">' if image_src else ''}
  <span class="tag">{html.escape(MODEL_FAMILIES[algo["slug"]])}</span>
  <h3>{html.escape(algo["name"])}</h3>
  <div class="muted"><strong>{html.escape(algo["tag"])}</strong></div>
  <p class="muted">{html.escape(algo["summary"])}</p>
</div>
"""


def metric_grid() -> None:
    st.markdown(
        """
<div class="metric-row">
  <div class="metric"><strong>10</strong><span>核心演算法</span></div>
  <div class="metric"><strong>6</strong><span>學習分類脈絡</span></div>
  <div class="metric"><strong>30</strong><span>檢核題與解答</span></div>
  <div class="metric"><strong>1</strong><span>完整研讀報告 PDF</span></div>
</div>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    image_src = cached_image_data_uri(str(HERO_IMAGE)) if HERO_IMAGE.exists() else ""
    st.markdown(
        f"""
<section class="hero">
  {'<img src="' + image_src + '" alt="Machine learning visual">' if image_src else ''}
  <div class="hero-content">
    <p class="eyebrow">Machine Learning Study Guide</p>
    <h1>十大機器學習演算法</h1>
    <p class="copy">依照研讀報告整理成可瀏覽、可比較、可練習的 Streamlit 學習網站。從模型直覺、適用場景、Python 範例到檢核題，幫你把演算法放進可以使用的知識架構。</p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def overview_page() -> None:
    hero()
    metric_grid()

    st.subheader("學習地圖")
    st.markdown(
        '<p class="section-note">先用模型類型建立大方向，再進到單一演算法看原理、案例與參數。</p>',
        unsafe_allow_html=True,
    )

    groups: dict[str, list[dict[str, Any]]] = {}
    for algo in ALGORITHMS:
        groups.setdefault(MODEL_FAMILIES[algo["slug"]].split(" / ")[0], []).append(algo)

    cols = st.columns(3)
    for index, (family, items) in enumerate(groups.items()):
        with cols[index % 3]:
            names = "、".join(item["name"] for item in items)
            st.markdown(
                f"""
<div class="info-panel">
  <h4>{html.escape(family)}</h4>
  <p class="muted">{html.escape(names)}</p>
</div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("十個演算法速覽")
    for row_start in range(0, len(ALGORITHMS), 4):
        cols = st.columns(4, gap="medium")
        for col, algo in zip(cols, ALGORITHMS[row_start : row_start + 4]):
            with col:
                with st.container(border=True):
                    st.markdown(card_html(algo), unsafe_allow_html=True)
                    st.button(
                        "深入學習",
                        key=f"open-{algo['slug']}",
                        on_click=open_algorithm,
                        args=(algo["slug"],),
                        use_container_width=True,
                    )


def score_from_demo(algo: dict[str, Any], value: float, samples: int, noise: int) -> int:
    demo = algo["demo"]
    min_v = float(demo["min"])
    max_v = float(demo["max"])
    span = max(max_v - min_v, 0.001)
    position = (float(value) - min_v) / span
    sample_bonus = (samples - 40) / 200 * 18
    noise_penalty = noise * 0.55

    if algo["slug"] in {"linear-regression", "pca", "random-forest"}:
        base = 60 + position * 18
    elif algo["slug"] in {"decision-tree", "knn", "k-means", "gradient-boosting"}:
        base = 83 - abs(position - 0.45) * 34
    elif algo["slug"] in {"logistic-regression", "svm", "naive-bayes"}:
        base = 78 - abs(position - 0.35) * 24
    else:
        base = 72

    return max(35, min(96, round(base + sample_bonus - noise_penalty)))


def format_value(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(int(value))


def code_from_demo(algo: dict[str, Any], value: int | float, metric: int) -> str:
    template = algo["demo"]["template"]
    return template.format(value=format_value(value), metric=metric)


def detail_page(slug: str) -> None:
    algo = selected_algorithm(slug)
    profile = MODEL_PROFILE[slug]
    image_path = STATIC_DIR / algo["image"]

    top_left, top_right = st.columns([1.55, 1])
    with top_left:
        st.caption(MODEL_FAMILIES[slug])
        st.title(algo["name"])
        st.markdown(f"**{algo['tag']}**")
        st.write(algo["summary"])
    with top_right:
        if image_path.exists():
            st.image(str(image_path), use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("難度", profile["difficulty"])
    c2.metric("資料型態", "表格 / 文字" if slug in {"naive-bayes", "svm"} else "表格 / 數值")
    c3.metric("學習類型", MODEL_FAMILIES[slug].split(" / ")[0])
    c4.metric("案例指標", f"{len(algo['case_metrics'])} 個")

    tab_intro, tab_case, tab_demo, tab_check = st.tabs(["原理", "案例", "互動參數", "檢核題"])

    with tab_intro:
        st.subheader("核心原理")
        st.write(algo["principle"])
        guide = algo["principle_guide"]
        flow_col, chart_col = st.columns([1.2, 1])
        with flow_col:
            st.markdown("#### 學習流程")
            for i, (title, text) in enumerate(guide["steps"], start=1):
                st.markdown(
                    f"""
<div class="flow-step">
  <div class="step-no">{i}</div>
  <div><strong>{html.escape(title)}</strong><br><span class="muted">{html.escape(text)}</span></div>
</div>
                    """,
                    unsafe_allow_html=True,
                )
        with chart_col:
            st.markdown("#### 能力輪廓")
            for label, value in guide["chart"]:
                st.markdown(
                    f"""
<div>
  <strong>{html.escape(label)}</strong>
  <div class="bar"><span style="width:{int(value)}%"></span></div>
</div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown(f'<div class="callout">{html.escape(guide["tip"])}</div>', unsafe_allow_html=True)

        st.subheader("適用與注意")
        a, b, c = st.columns(3)
        a.markdown(f"**適合資料**\n\n{profile['data']}")
        b.markdown(f"**主要優勢**\n\n{profile['strength']}")
        c.markdown(f"**常見風險**\n\n{profile['watch']}")

    with tab_case:
        st.subheader("應用情境")
        st.write(algo["case_detail"])
        st.markdown("#### 案例成效指標")
        metric_cols = st.columns(3)
        for col, (label, value) in zip(metric_cols, algo["case_metrics"]):
            col.metric(label, value)
        st.markdown("#### 常見用途")
        st.info(algo["uses"])

    with tab_demo:
        st.subheader("參數直覺模擬")
        demo = algo["demo"]
        control_cols = st.columns(3)
        variable = demo["variables"][0]
        with control_cols[0]:
            param_value = st.slider(
                variable["label"],
                min_value=variable["min"],
                max_value=variable["max"],
                value=variable["default"],
                step=variable["step"],
                help=f"{variable['low']}；{variable['high']}",
            )
        with control_cols[1]:
            sample_count = st.slider("訓練資料量", 40, 240, 120, 20)
        with control_cols[2]:
            noise_level = st.slider("資料雜訊", 0, 40, 15, 5)

        metric = score_from_demo(algo, param_value, sample_count, noise_level)
        st.metric("模擬驗證表現", f"{metric} / 100")
        st.progress(metric / 100)

        low_col, high_col = st.columns(2)
        with low_col:
            st.markdown(f"**低設定傾向**\n\n{variable['low']}")
        with high_col:
            st.markdown(f"**高設定傾向**\n\n{variable['high']}")

        st.code(code_from_demo(algo, param_value, metric), language="python")
        st.caption("這裡的分數是教學用的直覺模擬，用來觀察參數、資料量與雜訊的取捨。")

    with tab_check:
        st.subheader("檢核題")
        for index, qa in enumerate(algo["check_questions"], start=1):
            with st.expander(f"{index}. {qa['question']}"):
                st.write(qa["answer"])
        st.markdown(f'<div class="callout">{html.escape(algo["check"])}</div>', unsafe_allow_html=True)


def comparison_page() -> None:
    st.title("演算法比較矩陣")
    st.write("用任務型態、優勢與風險快速判斷應該先試哪一類模型。")

    rows = []
    for algo in ALGORITHMS:
        profile = MODEL_PROFILE[algo["slug"]]
        rows.append(
            {
                "演算法": algo["name"],
                "英文": algo["tag"],
                "類型": MODEL_FAMILIES[algo["slug"]],
                "難度": profile["difficulty"],
                "適合資料": profile["data"],
                "主要優勢": profile["strength"],
                "注意事項": profile["watch"],
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.subheader("選型建議")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
**需要解釋**

線性迴歸、邏輯迴歸、決策樹通常較容易說明模型依據。

**追求穩定表格預測**

隨機森林與梯度提升常是商業資料的實用起點。
            """
        )
    with c2:
        st.markdown(
            """
**沒有標籤**

K-Means 用於分群，PCA 用於降維與視覺化。

**文字或高維稀疏特徵**

樸素貝氏與 SVM 常能建立快速而有效的分類基準。
            """
        )


def practice_page() -> None:
    st.title("練習測驗")
    st.write("從每個演算法抽一題，先想答案，再展開核對。")

    total = 0
    for algo in ALGORITHMS:
        qa = algo["check_questions"][0]
        total += 1
        with st.expander(f"{algo['name']}：{qa['question']}"):
            st.write(qa["answer"])
            st.caption(f"延伸思考：{algo['check']}")

    st.success(f"本頁共 {total} 題。完成後建議回到深入學習頁，調整參數模擬一次。")


def report_page() -> None:
    st.title("研讀報告 PDF")
    st.write("這個網站依據資料夾內的完整研讀報告整理；可在此下載或開啟預覽。")

    for key, filename in PDF_FILES.items():
        path = BASE_DIR / filename
        if not path.exists():
            continue

        size_mb = path.stat().st_size / 1024 / 1024
        title = "完整研讀報告" if key == "report" else "對話紀錄"
        st.subheader(title)
        st.caption(f"{filename} · {size_mb:.1f} MB")
        st.download_button(
            label=f"下載 {title}",
            data=path.read_bytes(),
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )

        if st.checkbox(f"在頁面中預覽 {title}", value=(key == "report"), key=f"preview-{key}"):
            data_uri = cached_pdf_data_uri(str(path))
            components.html(
                f"""
<div class="pdf-frame">
  <iframe src="{data_uri}" width="100%" height="760" style="border:0;"></iframe>
</div>
                """,
                height=780,
                scrolling=False,
            )


def sidebar() -> tuple[str, str]:
    st.sidebar.title("學習網站")
    for page in PAGES:
        is_active = st.session_state["active_page"] == page
        st.sidebar.button(
            page,
            key=f"nav-{page}",
            on_click=set_page,
            args=(page,),
            type="primary" if is_active else "secondary",
            use_container_width=True,
        )

    st.sidebar.divider()
    st.sidebar.markdown("**學習順序**")
    st.sidebar.markdown("1. 總覽點選演算法\n2. 深入學習看原理\n3. 比較矩陣做選型\n4. 練習測驗確認理解")
    return st.session_state["active_page"], st.session_state["selected_slug"]


def main() -> None:
    init_state()
    css()
    page, slug = sidebar()

    if page == "總覽":
        overview_page()
    elif page == "深入學習":
        detail_page(slug)
    elif page == "比較矩陣":
        comparison_page()
    elif page == "練習測驗":
        practice_page()
    else:
        report_page()


if __name__ == "__main__":
    main()
