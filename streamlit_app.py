from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import ALGORITHMS, BASE_DIR, PDF_FILES


st.set_page_config(
    page_title="十大機器學習演算法研讀報告",
    layout="wide",
    initial_sidebar_state="expanded",
)


STYLE = """
<style>
  .main .block-container {
    max-width: 1220px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
  }
  .hero {
    position: relative;
    min-height: 360px;
    overflow: hidden;
    border-radius: 8px;
    background: #162b3f;
    margin-bottom: 1.5rem;
  }
  .hero img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(10, 23, 36, .86), rgba(10, 23, 36, .42) 58%, rgba(10, 23, 36, .16));
  }
  .hero-content {
    position: relative;
    z-index: 1;
    width: min(760px, 100%);
    padding: 78px 54px;
    color: #fff;
  }
  .hero-content p {
    margin: 0 0 10px;
    color: #f5c36b;
    font-weight: 800;
    text-transform: uppercase;
  }
  .hero-content h1 {
    margin: 0 0 14px;
    font-size: clamp(2.2rem, 7vw, 4.8rem);
    line-height: 1.04;
  }
  .hero-content span {
    display: block;
    max-width: 640px;
    color: #edf4f7;
    font-size: 1.08rem;
  }
  .metric-card, .step-card, .qa-card, .info-card {
    border: 1px solid #d7dee8;
    border-radius: 8px;
    background: #fff;
    padding: 16px;
    height: 100%;
  }
  .step-card strong, .qa-card strong {
    color: #17324d;
  }
  .step-number {
    display: inline-grid;
    place-items: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #0f766e;
    color: #fff;
    font-weight: 850;
    margin-bottom: 10px;
  }
  .tip {
    border-left: 5px solid #b45309;
    border-radius: 8px;
    background: #fff7ed;
    color: #17324d;
    padding: 16px;
    font-weight: 700;
  }
  code, pre {
    white-space: pre-wrap !important;
  }
  .demo-svg-wrap {
    width: 100%;
    min-height: 390px;
    border: 1px solid #d7dee8;
    border-radius: 8px;
    background: #f8fbfb;
    padding: 12px;
  }
  .demo-svg-wrap svg {
    width: 100%;
    height: 360px;
    display: block;
  }
</style>
"""


def file_size_mb(path: Path) -> float:
    return round(path.stat().st_size / 1024 / 1024, 1)


def pct_bar(label: str, value: int) -> None:
    st.markdown(f"**{label}**")
    st.progress(max(0, min(100, value)), text=f"{value}")


def normalize(value: float, minimum: float, maximum: float) -> float:
    if maximum == minimum:
        return 0.0
    return (value - minimum) / (maximum - minimum)


def calculate_metrics(values: dict[str, float], demo: dict) -> dict[str, int | str]:
    primary = demo["variables"][0]
    primary_norm = normalize(values[primary["key"]], primary["min"], primary["max"])
    sample_norm = normalize(values["sample_count"], demo["variables"][1]["min"], demo["variables"][1]["max"])
    noise_norm = normalize(values["noise_level"], demo["variables"][2]["min"], demo["variables"][2]["max"])
    sweet_spot = 0.34 if demo["slug"] == "gradient-boosting" else 0.62
    distance = min(1.0, abs(primary_norm - sweet_spot) / max(sweet_spot, 1 - sweet_spot))

    performance = round(max(38, min(96, 60 + (1 - distance) * 24 + sample_norm * 10 - noise_norm * 16)))
    complexity = round(max(15, min(98, 20 + primary_norm * 58 + sample_norm * 12)))
    stability = round(max(35, min(96, 92 - distance * 18 + sample_norm * 8 - noise_norm * 28)))
    return {
        "performance": performance,
        "complexity": complexity,
        "stability": stability,
        "metric": f"{performance / 100:.2f}",
    }


def make_points(sample_count: int, noise_level: int, groups: int = 2) -> list[tuple[float, float, int]]:
    centers = [(150, 90), (370, 175), (250, 180), (410, 80)]
    points = []
    for index in range(round(sample_count / 12)):
        group = index % groups
        cx, cy = centers[group % len(centers)]
        drift = noise_level * 1.6
        x = max(42, min(478, cx + __import__("math").sin(index * 2.19) * (28 + drift) + __import__("math").cos(index) * 11))
        y = max(38, min(222, cy + __import__("math").cos(index * 1.71) * (24 + drift) + __import__("math").sin(index * 1.3) * 10))
        points.append((x, y, group))
    return points


def svg_circle(x: float, y: float, r: int, fill: str) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'


def svg_line(x1: float, y1: float, x2: float, y2: float, color: str, width: int = 5, extra: str = "") -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" {extra}/>'


def build_demo_svg(slug: str, values: dict[str, float], demo: dict, metrics: dict[str, int | str]) -> str:
    colors = ["#0f766e", "#b45309", "#6d5bd0", "#dc2626"]
    primary_key = demo["variables"][0]["key"]
    primary = values[primary_key]
    noise = values["noise_level"]
    samples = values["sample_count"]
    groups = max(2, int(primary)) if slug == "k-means" else 2
    points = "".join(svg_circle(x, y, 5, colors[group % len(colors)]) for x, y, group in make_points(int(samples), int(noise), groups))

    if slug == "linear-regression":
        slope = 0.36 + primary * 0.055
        y1 = 212 - noise * 0.5
        y2 = y1 - 320 * slope
        body = f'{svg_line(42, 226, 486, 226, "#17324d", 3)}{svg_line(54, 226, 54, 34, "#17324d", 3)}{points}{svg_line(74, y1, 454, y2, "#0f766e", 7)}'
    elif slug == "logistic-regression":
        curve = 80 + primary * 7
        body = f'{svg_line(42, 226, 486, 226, "#17324d", 3)}{svg_line(54, 226, 54, 34, "#17324d", 3)}{points}<path d="M70 210 C 160 210, 190 {curve + 70:.1f}, 262 {curve:.1f} S 370 54, 458 54" fill="none" stroke="#0f766e" stroke-width="7" stroke-linecap="round"/><line x1="58" y1="132" x2="470" y2="132" stroke="#b45309" stroke-width="3" stroke-dasharray="8 9"/>'
    elif slug == "decision-tree":
        levels = min(5, int(primary))
        body = '<circle cx="260" cy="42" r="24" fill="#0f766e"/>'
        for level in range(1, levels + 1):
            nodes = min(2 ** level, 12)
            for node in range(nodes):
                x = 60 + node * (400 / max(1, nodes - 1))
                y = 42 + level * 36
                body += svg_line(260, 42 + (level - 1) * 24, x, y, "#17324d", 2)
                body += svg_circle(x, y, 10, colors[node % len(colors)])
    elif slug == "random-forest":
        body = ""
        for index in range(max(1, round(primary / 30))):
            x = 54 + index * 38
            body += svg_line(x, 126, x, 74, "#17324d", 3)
            body += svg_line(x, 100, x - 18, 132, "#17324d", 3)
            body += svg_line(x, 100, x + 18, 132, "#17324d", 3)
            body += svg_circle(x, 68, 10, colors[index % len(colors)])
        body += f'<rect x="190" y="186" width="140" height="42" rx="21" fill="#17324d"/><text x="260" y="213" fill="#fff" text-anchor="middle" font-size="18" font-weight="800">vote {metrics["stability"]}%</text>'
    elif slug == "svm":
        margin = max(28, min(116, 88 - primary * 4.5 + noise * 0.6))
        dashed = 'stroke-dasharray="8 8"'
        body = f'{points}{svg_line(130, 226, 390, 42, "#17324d", 7)}{svg_line(130 - margin, 226, 390 - margin, 42, "#f5c36b", 3, dashed)}{svg_line(130 + margin, 226, 390 + margin, 42, "#f5c36b", 3, dashed)}'
    elif slug == "knn":
        radius = 40 + primary * 6
        body = f'{points}{svg_circle(260, 130, 10, "#17324d")}<circle cx="260" cy="130" r="{radius:.1f}" fill="none" stroke="#0f766e" stroke-width="5" stroke-dasharray="10 8"/><text x="260" y="236" fill="#17324d" text-anchor="middle" font-size="18" font-weight="800">K={primary:g}</text>'
    elif slug == "k-means":
        centers = [(150, 90), (370, 175), (250, 180), (410, 80), (116, 180), (320, 84), (220, 70), (430, 215)]
        body = points
        for index, (x, y) in enumerate(centers[: int(primary)]):
            body += f'<path d="M{x} {y - 13}l4 9 10 1-7 7 2 10-9-5-9 5 2-10-7-7 10-1z" fill="{colors[index % len(colors)]}"/>'
    elif slug == "pca":
        angle = 24 + primary * 4
        dashed = 'stroke-dasharray="8 8"'
        body = f'{points}<g transform="rotate(-{angle:.1f} 260 130)">{svg_line(70, 130, 454, 130, "#0f766e", 7)}{svg_line(170, 82, 350, 178, "#b45309", 4, dashed)}</g><text x="62" y="42" fill="#17324d" font-size="18" font-weight="800">components={primary:g}</text>'
    elif slug == "naive-bayes":
        body = ""
        for index, height in enumerate([metrics["performance"], metrics["stability"], 100 - noise * 1.5]):
            body += f'<rect x="{104 + index * 100}" y="{220 - float(height) * 1.5:.1f}" width="54" height="{float(height) * 1.5:.1f}" rx="8" fill="{colors[index]}"/>'
        body += f'<text x="260" y="42" fill="#17324d" text-anchor="middle" font-size="18" font-weight="800">alpha={primary:g}</text><path d="M96 226H430" stroke="#17324d" stroke-width="4" stroke-linecap="round"/>'
    else:
        steps = round(4 + primary * 20)
        body = ""
        for index in range(min(8, steps)):
            x = 64 + index * 52
            height = 42 + index * 15 - noise * 0.4
            body += f'<rect x="{x}" y="{190 - height:.1f}" width="34" height="{height:.1f}" rx="8" fill="{colors[index % len(colors)]}"/>'
            if index < 7:
                body += f'<text x="{x + 42}" y="150" fill="#b45309" font-size="24" font-weight="800">+</text>'
        body += '<path d="M58 222C150 206 220 182 292 146C352 116 404 88 458 44" fill="none" stroke="#17324d" stroke-width="6" stroke-linecap="round"/>'

    return f"""
    <svg viewBox="0 0 520 260" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
      <rect width="520" height="260" rx="18" fill="#f8fbfb"/>
      {body}
    </svg>
    """


def code_sample(slug: str, values: dict[str, float], metrics: dict[str, int | str], demo: dict) -> str:
    primary_key = demo["variables"][0]["key"]
    primary_value = values[primary_key]
    if slug == "linear-regression":
        return f"""from sklearn.linear_model import LinearRegression

X, y = make_regression_dataset(
    n_samples={values['sample_count']},
    n_features={primary_value},
    noise={values['noise_level']}
)
model = LinearRegression()
model.fit(X, y)
print("validation_score", {metrics['metric']})"""
    if slug == "k-means":
        return f"""from sklearn.cluster import KMeans

X = make_customer_vectors(
    n_samples={values['sample_count']},
    noise={values['noise_level']}
)
model = KMeans(n_clusters={primary_value}, n_init="auto", random_state=42)
labels = model.fit_predict(X)
print("cluster_score", {metrics['metric']})"""
    estimator_map = {
        "logistic-regression": ("from sklearn.linear_model import LogisticRegression", f"LogisticRegression(C={primary_value}, max_iter=1000)"),
        "decision-tree": ("from sklearn.tree import DecisionTreeClassifier", f"DecisionTreeClassifier(max_depth={primary_value}, random_state=42)"),
        "random-forest": ("from sklearn.ensemble import RandomForestClassifier", f"RandomForestClassifier(n_estimators={primary_value}, random_state=42)"),
        "svm": ("from sklearn.svm import SVC", f'SVC(kernel="rbf", C={primary_value}, gamma="scale")'),
        "knn": ("from sklearn.neighbors import KNeighborsClassifier", f"KNeighborsClassifier(n_neighbors={primary_value})"),
        "pca": ("from sklearn.decomposition import PCA", f"PCA(n_components={primary_value})"),
        "naive-bayes": ("from sklearn.naive_bayes import MultinomialNB", f"MultinomialNB(alpha={primary_value})"),
        "gradient-boosting": ("from sklearn.ensemble import GradientBoostingClassifier", f"GradientBoostingClassifier(learning_rate={primary_value}, random_state=42)"),
    }
    import_line, estimator = estimator_map[slug]
    return f"""{import_line}

X, y = make_dataset(
    n_samples={values['sample_count']},
    noise={values['noise_level']}
)
model = {estimator}
model.fit(X, y)
print("validation_score", {metrics['metric']})"""


st.markdown(STYLE, unsafe_allow_html=True)

hero_path = BASE_DIR / "static" / "hero-ai.png"
st.image(hero_path, width="stretch")
st.title("十大機器學習演算法研讀報告")
st.caption("Streamlit Cloud 版本：互動式演算法摘要、案例、Python 參數模擬與檢核題。")

with st.sidebar:
    st.header("演算法導覽")
    selected_name = st.radio("選擇演算法", [item["name"] for item in ALGORITHMS], label_visibility="collapsed")
    st.divider()
    st.subheader("原始 PDF")
    for key, filename in PDF_FILES.items():
        path = BASE_DIR / filename
        if path.exists():
            st.download_button(
                label=f"{filename} ({file_size_mb(path)} MB)",
                data=path.read_bytes(),
                file_name=filename,
                mime="application/pdf",
                key=f"pdf-{key}",
            )

selected = next(item for item in ALGORITHMS if item["name"] == selected_name)

top_cols = st.columns([1, 1.2], vertical_alignment="center")
with top_cols[0]:
    st.image(BASE_DIR / "static" / selected["image"], width="stretch")
with top_cols[1]:
    st.subheader(selected["name"])
    st.caption(selected["tag"])
    st.write(selected["summary"])
    st.info(f"常見用途：{selected['uses']}")

principle_tab, case_tab, python_tab, check_tab = st.tabs(["原理", "實務案例", "Python 實作", "檢核題"])

with principle_tab:
    st.write(selected["principle"])
    step_cols = st.columns(3)
    for index, (title, description) in enumerate(selected["principle_guide"]["steps"]):
        with step_cols[index]:
            st.markdown(
                f'<div class="step-card"><span class="step-number">{index + 1:02d}</span><br><strong>{title}</strong><p>{description}</p></div>',
                unsafe_allow_html=True,
            )
    st.write("")
    chart_cols = st.columns(3)
    for index, (label, value) in enumerate(selected["principle_guide"]["chart"]):
        with chart_cols[index]:
            pct_bar(label, value)
    st.markdown(f'<div class="tip">{selected["principle_guide"]["tip"]}</div>', unsafe_allow_html=True)

with case_tab:
    st.write(selected["case"])
    st.write(selected["case_detail"])
    for label, value in selected["case_metrics"]:
        pct_bar(label, value)

with python_tab:
    demo = selected["demo"]
    values = {}
    control_cols = st.columns(3)
    for index, variable in enumerate(demo["variables"]):
        with control_cols[index]:
            values[variable["key"]] = st.slider(
                variable["label"],
                min_value=variable["min"],
                max_value=variable["max"],
                value=variable["default"],
                step=variable["step"],
                format="%g",
                help=f"{variable['low']} / {variable['high']}",
            )
            st.caption(f"{variable['low']} / {variable['high']}")

    metrics = calculate_metrics(values, demo)
    st.html(f'<div class="demo-svg-wrap">{build_demo_svg(selected["slug"], values, demo, metrics)}</div>')
    m1, m2, m3 = st.columns(3)
    m1.metric("模擬表現", f"{metrics['performance']}%")
    m2.metric("複雜度", f"{metrics['complexity']}%")
    m3.metric("穩定度", f"{metrics['stability']}%")
    st.code(code_sample(selected["slug"], values, metrics, demo), language="python")

with check_tab:
    for index, qa in enumerate(selected["check_questions"], start=1):
        st.markdown(
            f'<div class="qa-card"><strong>Q{index}. {qa["question"]}</strong><p>{qa["answer"]}</p></div>',
            unsafe_allow_html=True,
        )
        st.write("")
