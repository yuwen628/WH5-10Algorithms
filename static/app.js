const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

const openModal = (id) => {
  const modal = document.getElementById(id);
  if (!modal || modal.open) return;

  if (typeof modal.showModal === "function") {
    modal.showModal();
  } else {
    modal.setAttribute("open", "");
  }
};

document.querySelectorAll(".algorithm-card").forEach((card) => {
  const button = card.querySelector("[data-open-modal]");
  const modalId = button?.dataset.openModal;

  card.addEventListener("click", () => openModal(modalId));
  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openModal(modalId);
    }
  });

  button?.addEventListener("click", (event) => {
    event.stopPropagation();
    openModal(modalId);
  });
});

document.querySelectorAll(".algorithm-modal").forEach((modal) => {
  modal.querySelector("[data-close-modal]")?.addEventListener("click", () => {
    modal.close();
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.close();
    }
  });
});

document.querySelectorAll(".modal-content").forEach((content) => {
  const tabs = [...content.querySelectorAll(".modal-tab")];
  const panels = [...content.querySelectorAll(".tab-panel")];

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((item) => {
        item.classList.toggle("is-active", item === tab);
        item.setAttribute("aria-selected", item === tab ? "true" : "false");
      });

      panels.forEach((panel) => {
        const active = panel.id === tab.dataset.tabTarget;
        panel.classList.toggle("is-active", active);
        panel.toggleAttribute("hidden", !active);
      });
    });
  });
});

const formatNumber = (value, step) => {
  const decimals = String(step).includes(".") ? String(step).split(".")[1].length : 0;
  return Number(value).toFixed(decimals).replace(/\.0+$/, "");
};

const collectValues = (lab, demo) => {
  const values = {};

  demo.variables.forEach((variable) => {
    const input = lab.querySelector(`[data-key="${variable.key}"]`);
    const raw = input ? input.value : variable.default;
    const formatted = formatNumber(raw, variable.step);
    values[variable.key] = Number(formatted);

    const label = lab.querySelector(`[data-param-value="${variable.key}"]`);
    if (label) {
      label.textContent = `${formatted}${variable.unit}`;
    }
  });

  return values;
};

const primaryKey = (demo) => demo.variables[0].key;

const normalize = (value, variable) => {
  const span = Number(variable.max) - Number(variable.min);
  return span === 0 ? 0 : (Number(value) - Number(variable.min)) / span;
};

const calculateMetrics = (values, demo) => {
  const primaryVariable = demo.variables[0];
  const primary = normalize(values[primaryVariable.key], primaryVariable);
  const samples = normalize(values.sample_count, demo.variables[1]);
  const noise = normalize(values.noise_level, demo.variables[2]);
  const sweetSpot = demo.slug === "gradient-boosting" ? 0.34 : 0.62;
  const distance = Math.min(1, Math.abs(primary - sweetSpot) / Math.max(sweetSpot, 1 - sweetSpot));

  const performance = Math.round(clamp(60 + (1 - distance) * 24 + samples * 10 - noise * 16, 38, 96));
  const complexity = Math.round(clamp(20 + primary * 58 + samples * 12, 15, 98));
  const stability = Math.round(clamp(92 - distance * 18 + samples * 8 - noise * 28, 35, 96));

  return {
    performance,
    complexity,
    stability,
    metric: (performance / 100).toFixed(2),
  };
};

const codeTemplates = {
  "linear-regression": (v, m) => `from sklearn.linear_model import LinearRegression

X, y = make_regression_dataset(
    n_samples=${v.sample_count},
    n_features=${v.feature_count},
    noise=${v.noise_level}
)
model = LinearRegression()
model.fit(X, y)
print("validation_score", ${m.metric})`,
  "logistic-regression": (v, m) => `from sklearn.linear_model import LogisticRegression

X, y = make_classification_dataset(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = LogisticRegression(C=${v.C}, max_iter=1000)
model.fit(X, y)
print("validation_score", ${m.metric})`,
  "decision-tree": (v, m) => `from sklearn.tree import DecisionTreeClassifier

X, y = make_classification_dataset(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = DecisionTreeClassifier(max_depth=${v.max_depth}, random_state=42)
model.fit(X, y)
print("validation_score", ${m.metric})`,
  "random-forest": (v, m) => `from sklearn.ensemble import RandomForestClassifier

X, y = make_classification_dataset(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = RandomForestClassifier(n_estimators=${v.n_estimators}, random_state=42)
model.fit(X, y)
print("validation_score", ${m.metric})`,
  "svm": (v, m) => `from sklearn.svm import SVC

X, y = make_classification_dataset(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = SVC(kernel="rbf", C=${v.C}, gamma="scale")
model.fit(X, y)
print("validation_score", ${m.metric})`,
  "knn": (v, m) => `from sklearn.neighbors import KNeighborsClassifier

X, y = make_classification_dataset(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = KNeighborsClassifier(n_neighbors=${v.n_neighbors})
model.fit(X, y)
print("validation_score", ${m.metric})`,
  "k-means": (v, m) => `from sklearn.cluster import KMeans

X = make_customer_vectors(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = KMeans(n_clusters=${v.n_clusters}, n_init="auto", random_state=42)
labels = model.fit_predict(X)
print("cluster_score", ${m.metric})`,
  pca: (v, m) => `from sklearn.decomposition import PCA

X = make_feature_matrix(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
pca = PCA(n_components=${v.n_components})
X_reduced = pca.fit_transform(X)
print("explained_variance", ${m.metric})`,
  "naive-bayes": (v, m) => `from sklearn.naive_bayes import MultinomialNB

X, y = make_text_count_matrix(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = MultinomialNB(alpha=${v.alpha})
model.fit(X, y)
print("validation_score", ${m.metric})`,
  "gradient-boosting": (v, m) => `from sklearn.ensemble import GradientBoostingClassifier

X, y = make_classification_dataset(
    n_samples=${v.sample_count},
    noise=${v.noise_level}
)
model = GradientBoostingClassifier(learning_rate=${v.learning_rate}, random_state=42)
model.fit(X, y)
print("validation_score", ${m.metric})`,
};

const pointCloud = (count, noise, groups = 2) => {
  const points = [];
  const total = Math.round(count / 12);
  const centers = [
    [150, 90],
    [370, 175],
    [250, 180],
    [410, 80],
  ];

  for (let index = 0; index < total; index += 1) {
    const group = index % groups;
    const [cx, cy] = centers[group];
    const drift = noise * 1.6;
    const x = clamp(cx + Math.sin(index * 2.19) * (28 + drift) + Math.cos(index) * 11, 42, 478);
    const y = clamp(cy + Math.cos(index * 1.71) * (24 + drift) + Math.sin(index * 1.3) * 10, 38, 222);
    points.push({ x, y, group });
  }

  return points;
};

const circle = (x, y, r, fill) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}"/>`;
const line = (x1, y1, x2, y2, color, width = 5, extra = "") =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}" stroke-linecap="round" ${extra}/>`;

const renderDiagram = (demo, values, metrics) => {
  const key = primaryKey(demo);
  const primary = values[key];
  const noise = values.noise_level;
  const samples = values.sample_count;
  const colors = ["#0f766e", "#b45309", "#6d5bd0", "#dc2626"];
  const points = pointCloud(samples, noise, demo.slug === "k-means" ? Math.max(2, primary) : 2);
  const pointSvg = points
    .map((point) => circle(point.x, point.y, 5, colors[point.group % colors.length]))
    .join("");

  if (demo.slug === "linear-regression") {
    const slope = 0.36 + primary * 0.055;
    const y1 = 212 - noise * 0.5;
    const y2 = y1 - 320 * slope;
    return `${line(42, 226, 486, 226, "#17324d", 3)}${line(54, 226, 54, 34, "#17324d", 3)}${pointSvg}${line(74, y1, 454, y2, "#0f766e", 7)}<text x="64" y="34" fill="#17324d" font-size="18" font-weight="800">fit</text>`;
  }

  if (demo.slug === "logistic-regression") {
    const curve = 80 + primary * 7;
    return `${line(42, 226, 486, 226, "#17324d", 3)}${line(54, 226, 54, 34, "#17324d", 3)}${pointSvg}<path d="M70 210 C 160 210, 190 ${curve + 70}, 262 ${curve} S 370 54, 458 54" fill="none" stroke="#0f766e" stroke-width="7" stroke-linecap="round"/><line x1="58" y1="132" x2="470" y2="132" stroke="#b45309" stroke-width="3" stroke-dasharray="8 9"/>`;
  }

  if (demo.slug === "decision-tree") {
    const levels = Math.min(5, primary);
    let svg = `<circle cx="260" cy="42" r="24" fill="#0f766e"/>`;
    for (let level = 1; level <= levels; level += 1) {
      const nodes = Math.min(2 ** level, 12);
      for (let node = 0; node < nodes; node += 1) {
        const x = 60 + node * (400 / Math.max(1, nodes - 1));
        const y = 42 + level * 36;
        svg += line(260, 42 + (level - 1) * 24, x, y, "#17324d", 2);
        svg += circle(x, y, 10, colors[node % colors.length]);
      }
    }
    return svg;
  }

  if (demo.slug === "random-forest") {
    const treeCount = Math.round(primary / 30);
    let svg = "";
    for (let index = 0; index < treeCount; index += 1) {
      const x = 54 + index * 38;
      svg += line(x, 126, x, 74, "#17324d", 3);
      svg += line(x, 100, x - 18, 132, "#17324d", 3);
      svg += line(x, 100, x + 18, 132, "#17324d", 3);
      svg += circle(x, 68, 10, colors[index % colors.length]);
    }
    return `${svg}<rect x="190" y="186" width="140" height="42" rx="21" fill="#17324d"/><text x="260" y="213" fill="#fff" text-anchor="middle" font-size="18" font-weight="800">vote ${metrics.stability}%</text>`;
  }

  if (demo.slug === "svm") {
    const margin = clamp(88 - primary * 4.5 + noise * 0.6, 28, 116);
    return `${pointSvg}${line(130, 226, 390, 42, "#17324d", 7)}${line(130 - margin, 226, 390 - margin, 42, "#f5c36b", 3, 'stroke-dasharray="8 8"')}${line(130 + margin, 226, 390 + margin, 42, "#f5c36b", 3, 'stroke-dasharray="8 8"')}<text x="66" y="42" fill="#17324d" font-size="18" font-weight="800">margin</text>`;
  }

  if (demo.slug === "knn") {
    const radius = 40 + primary * 6;
    return `${pointSvg}${circle(260, 130, 10, "#17324d")}<circle cx="260" cy="130" r="${radius}" fill="none" stroke="#0f766e" stroke-width="5" stroke-dasharray="10 8"/><text x="260" y="236" fill="#17324d" text-anchor="middle" font-size="18" font-weight="800">K=${primary}</text>`;
  }

  if (demo.slug === "k-means") {
    const centers = [[150, 90], [370, 175], [250, 180], [410, 80], [116, 180], [320, 84], [220, 70], [430, 215]];
    const centerSvg = centers.slice(0, primary).map(([x, y], index) => `<path d="M${x} ${y - 13}l4 9 10 1-7 7 2 10-9-5-9 5 2-10-7-7 10-1z" fill="${colors[index % colors.length]}"/>`).join("");
    return `${pointSvg}${centerSvg}`;
  }

  if (demo.slug === "pca") {
    const angle = 24 + primary * 4;
    return `${pointSvg}<g transform="rotate(-${angle} 260 130)">${line(70, 130, 454, 130, "#0f766e", 7)}${line(170, 82, 350, 178, "#b45309", 4, 'stroke-dasharray="8 8"')}</g><text x="62" y="42" fill="#17324d" font-size="18" font-weight="800">components=${primary}</text>`;
  }

  if (demo.slug === "naive-bayes") {
    const alpha = primary;
    const bars = [metrics.performance, metrics.stability, 100 - noise * 1.5].map((height, index) =>
      `<rect x="${104 + index * 100}" y="${220 - height * 1.5}" width="54" height="${height * 1.5}" rx="8" fill="${colors[index]}"/>`
    ).join("");
    return `${bars}<text x="260" y="42" fill="#17324d" text-anchor="middle" font-size="18" font-weight="800">alpha=${alpha}</text><path d="M96 226H430" stroke="#17324d" stroke-width="4" stroke-linecap="round"/>`;
  }

  const steps = Math.round(4 + primary * 20);
  let svg = "";
  for (let index = 0; index < Math.min(8, steps); index += 1) {
    const x = 64 + index * 52;
    const height = 42 + index * 15 - noise * 0.4;
    svg += `<rect x="${x}" y="${190 - height}" width="34" height="${height}" rx="8" fill="${colors[index % colors.length]}"/>`;
    if (index < 7) svg += `<text x="${x + 42}" y="150" fill="#b45309" font-size="24" font-weight="800">+</text>`;
  }
  return `${svg}<path d="M58 222C150 206 220 182 292 146C352 116 404 88 458 44" fill="none" stroke="#17324d" stroke-width="6" stroke-linecap="round"/>`;
};

const updatePythonLab = (lab) => {
  const demo = JSON.parse(lab.dataset.demo);
  const values = collectValues(lab, demo);
  const metrics = calculateMetrics(values, demo);
  const result = lab.querySelector("[data-demo-result]");
  const code = lab.querySelector("[data-code-output]");
  const svg = lab.querySelector("[data-demo-visual] svg");
  const primaryVariable = demo.variables[0];
  const primaryValue = values[primaryVariable.key];

  if (result) {
    result.textContent = `參數組合：${primaryVariable.label} ${primaryValue}${primaryVariable.unit}、訓練資料量 ${values.sample_count} 筆、資料雜訊 ${values.noise_level}%。模擬表現 ${metrics.performance}%，複雜度 ${metrics.complexity}%，穩定度 ${metrics.stability}%。`;
  }

  if (code) {
    const template = codeTemplates[demo.slug];
    code.textContent = template ? template(values, metrics) : demo.template;
  }

  if (svg) {
    svg.innerHTML = `<rect width="520" height="260" rx="18" fill="#f8fbfb"/>${renderDiagram(demo, values, metrics)}`;
  }
};

document.querySelectorAll(".python-lab").forEach((lab) => {
  updatePythonLab(lab);
  lab.querySelectorAll("[data-param-input]").forEach((input) => {
    input.addEventListener("input", () => updatePythonLab(lab));
  });
});
