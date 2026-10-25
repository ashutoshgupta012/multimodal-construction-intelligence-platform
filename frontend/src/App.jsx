
import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API = "https://constructionai-backend.onrender.com";

const modules = [
  ["Dashboard", "🏠"],
  ["Image Analysis", "🔍"],
  ["Safety Monitor", "🦺"],
  ["Crack Analysis", "🧱"],
  ["Cost Estimator", "💰"],
  ["AI Assistant", "🤖"],
];

function App() {
  const [tab, setTab] = useState("Dashboard");
  const [backend, setBackend] = useState(false);
  const [model, setModel] = useState(false);
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  async function checkBackend() {
    try {
      const { data } = await axios.get(`${API}/api/health`);
      setBackend(data?.status === "healthy");
      setModel(data?.ai_model_loaded === true);
      setStatus("Backend status checked.");
    } catch {
      setBackend(false);
      setModel(false);
      setStatus("Backend offline. Start your FastAPI server.");
    }
  }

  useEffect(() => {
    checkBackend();
  }, []);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  function changeTab(name) {
    setTab(name);
    setStatus("");
  }

  function selectImage(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setStatus("Select a JPG, PNG, or WEBP image.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setStatus("Image must be smaller than 10 MB.");
      event.target.value = "";
      return;
    }

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResults(null);
    setStatus("Image selected.");
  }

  function removeImage() {
    setImage(null);
    setPreview("");
    setResults(null);
    setStatus("");

    const input = document.getElementById("image-analysis-input");
    if (input) input.value = "";
  }

  async function analyzeImage() {
    if (!image) {
      setStatus("Please select an image first.");
      return;
    }

    if (!backend || !model) {
      setStatus("Backend or AI model is unavailable.");
      return;
    }

    setLoading(true);
    setResults(null);
    setStatus("Analyzing image...");

    try {
      const form = new FormData();
      form.append("file", image);

      const { data } = await axios.post(
        `${API}/api/detect-objects`,
        form
      );

      setResults(data);
      setStatus(data?.message || "Analysis completed.");
    } catch (error) {
      setStatus(
        error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          "Image analysis failed."
      );
    } finally {
      setLoading(false);
    }
  }

  function renderContent() {
    switch (tab) {
      case "Dashboard":
        return (
          <>
            <section className="dashboard-welcome">
              <div className="dashboard-welcome-content">
                <p className="eyebrow">CONSTRUCTION WORKSPACE</p>
                <h2>Welcome to ConstructionAI</h2>
                <p>
                  Monitor your project tools, analyze construction images,
                  and estimate building costs from one place.
                </p>
                <button
                  className="primary-button"
                  onClick={() => changeTab("Image Analysis")}
                >
                  Start Image Analysis →
                </button>
              </div>
              <div className="dashboard-illustration">🏗️</div>
            </section>

            <section className="dashboard-stats">
              <article className="dashboard-stat">
                <div className="stat-icon blue">◉</div>
                <div>
                  <p>Backend Status</p>
                  <h3>{backend ? "Online" : "Offline"}</h3>
                  <span>
                    {backend ? "Connection active" : "Not connected"}
                  </span>
                </div>
              </article>

              <article className="dashboard-stat">
                <div className="stat-icon green">✦</div>
                <div>
                  <p>AI Model</p>
                  <h3>{model ? "Ready" : "Unavailable"}</h3>
                  <span>
                    {model ? "Ready to analyze" : "Check model status"}
                  </span>
                </div>
              </article>

              <article className="dashboard-stat">
                <div className="stat-icon purple">▧</div>
                <div>
                  <p>Images Selected</p>
                  <h3>{image ? "1" : "0"}</h3>
                  <span>
                    {image ? "Image uploaded" : "No image selected"}
                  </span>
                </div>
              </article>

              <article className="dashboard-stat">
                <div className="stat-icon orange">⌕</div>
                <div>
                  <p>Objects Detected</p>
                  <h3>
                    {results?.count ?? results?.detections?.length ?? 0}
                  </h3>
                  <span>Latest analysis result</span>
                </div>
              </article>
            </section>

            <section className="dashboard-modules">
              <div className="section-heading">
                <div>
                  <h2>Project Modules</h2>
                  <p>Choose a tool to get started.</p>
                </div>
              </div>

              <div className="dashboard-module-grid">
                {modules.slice(1).map(([name, icon]) => {
                  const descriptions = {
                    "Image Analysis":
                      "Detect objects in construction images.",
                    "Safety Monitor":
                      "Analyze site images with your connected detection model.",
                    "Crack Analysis":
                      "Review wall and concrete crack analysis.",
                    "Cost Estimator":
                      "Calculate an estimated construction budget.",
                    "AI Assistant":
                      "Get answers to common construction questions.",
                  };

                  return (
                    <article className="dashboard-module-card" key={name}>
                      <div className="module-card-top">
                        <span className="module-card-icon">{icon}</span>
                        <span className="module-arrow">↗</span>
                      </div>
                      <h3>{name}</h3>
                      <p>{descriptions[name]}</p>
                      <button
                        className="module-link"
                        onClick={() => changeTab(name)}
                      >
                        Open module <span>→</span>
                      </button>
                    </article>
                  );
                })}
              </div>
            </section>
          </>
        );

      case "Image Analysis":
        return (
          <>
            <section className="welcome">
              <div>
                <p className="eyebrow">AI VISION</p>
                <h2>Construction Image Analysis</h2>
                <p>Upload an image for object detection.</p>
              </div>
              <span className="welcome-icon">🔍</span>
            </section>

            <section className="content-grid">
              <article className="panel upload-panel">
                <h2>Upload Image</h2>
                <p>JPG, PNG, WEBP · Maximum 10 MB</p>

                <input
                  id="image-analysis-input"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={selectImage}
                  disabled={loading}
                />

                {preview && (
                  <div className="preview">
                    <img src={preview} alt="Selected construction site" />
                    <p>{image?.name}</p>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={removeImage}
                      disabled={loading}
                    >
                      Remove Image
                    </button>
                  </div>
                )}

                <button
                  className="primary-button"
                  disabled={!image || loading || !backend || !model}
                  onClick={analyzeImage}
                >
                  {loading ? "Analyzing..." : "Run AI Detection"}
                </button>

                <p className="status-message" role="status">
                  {!backend
                    ? "Start the FastAPI backend."
                    : !model
                    ? "AI model is unavailable."
                    : status}
                </p>
              </article>

              <article className="panel">
                <h2>Analysis Results</h2>

                {!results ? (
                  <p>No results yet. Upload an image to begin.</p>
                ) : (
                  <>
                    <h3>
                      Objects detected:{" "}
                      {results.count ?? results.detections?.length ?? 0}
                    </h3>
                    <p>{results.message}</p>

                    {(results.detections || []).map((item, index) => (
                      <article className="module" key={index}>
                        <div>
                          <h3>{item.object || "Detected object"}</h3>
                          <p>
                            Confidence:{" "}
                            {item.confidence != null
                              ? `${item.confidence}%`
                              : "N/A"}
                          </p>
                          {Array.isArray(item.box) && (
                            <p>Box: {item.box.join(", ")}</p>
                          )}
                        </div>
                      </article>
                    ))}
                  </>
                )}
              </article>
            </section>
          </>
        );

      case "Safety Monitor":
        return (
          <SafetyMonitor
            backend={backend}
            model={model}
            api={API}
          />
        );

      case "Crack Analysis":
        return (
          <section className="panel">
            <h2>🧱 Crack Analysis</h2>
            <p>
              A dedicated crack detection model is required to reliably
              analyze wall and concrete cracks.
            </p>
            <button
              className="primary-button"
              onClick={() => changeTab("Image Analysis")}
            >
              Open Image Analysis
            </button>
          </section>
        );

      case "Cost Estimator":
        return <CostEstimator />;

      case "AI Assistant":
        return <AssistantFAQ />;

      default:
        return null;
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2 className="brand">🏗️ ConstructionAI</h2>
        <p className="nav-label">WORKSPACE</p>

        <nav>
          {modules.map(([name, icon]) => (
            <button
              key={name}
              className={`nav-item ${tab === name ? "active" : ""}`}
              onClick={() => changeTab(name)}
            >
              <span>{icon}</span>
              <span>{name}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          AI-powered construction intelligence
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">CONSTRUCTION INTELLIGENCE PLATFORM</p>
            <h1>{tab}</h1>
          </div>

          <button className="status-button" onClick={checkBackend}>
            {backend ? "🟢 Backend Online" : "🔴 Backend Offline"}
          </button>
        </header>

        {renderContent()}

        {status && tab !== "Image Analysis" && (
          <p className="status-message" role="status">
            {status}
          </p>
        )}

        <footer>
          ConstructionAI · AI-powered construction intelligence
        </footer>
      </main>
    </div>
  );
}

function SafetyMonitor({ backend, model, api }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  function handleImageChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Please select a JPG, PNG, or WEBP image.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("Image size must be smaller than 10 MB.");
      event.target.value = "";
      return;
    }

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResults(null);
    setError("");
  }

  function removeImage() {
    setImage(null);
    setPreview("");
    setResults(null);
    setError("");

    const input = document.getElementById("safety-image-input");
    if (input) input.value = "";
  }

  async function analyzeSafety() {
    if (!image) {
      setError("Please upload a construction-site image.");
      return;
    }

    if (!backend) {
      setError("Backend is offline. Start your FastAPI server.");
      return;
    }

    if (!model) {
      setError("The detection model is not ready. Check the backend.");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("file", image);

      const { data } = await axios.post(
        `${api}/api/detect-objects`,
        formData
      );

      setResults(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          "Unable to analyze the image."
      );
    } finally {
      setLoading(false);
    }
  }

  const detections = Array.isArray(results?.detections)
    ? results.detections
    : [];

  const objectCount = results?.count ?? detections.length;

  return (
    <section className="panel safety-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">CONSTRUCTION SITE</p>
          <h2>🦺 Safety Monitor</h2>
          <p>
            Upload a site image and view objects detected by your connected
            model.
          </p>
        </div>
      </div>

      <div className="safety-notice">
        <strong>Important:</strong> This feature uses your existing object
        detection model. It cannot reliably confirm helmet or safety vest
        compliance unless the model is specifically trained and validated
        for PPE detection.
      </div>

      <div className="safety-upload">
        <label htmlFor="safety-image-input">
          <strong>Select construction-site image</strong>
        </label>

        <input
          id="safety-image-input"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleImageChange}
          disabled={loading}
        />

        <p className="safety-help">
          JPG, PNG, or WEBP · Maximum 10 MB
        </p>

        {preview && (
          <div className="safety-preview">
            <img src={preview} alt="Uploaded construction site" />
            <p>{image?.name}</p>

            <button
              type="button"
              className="secondary-button"
              onClick={removeImage}
              disabled={loading}
            >
              Remove Image
            </button>
          </div>
        )}

        <button
          type="button"
          className="primary-button"
          onClick={analyzeSafety}
          disabled={!image || loading || !backend || !model}
        >
          {loading ? "Analyzing Image..." : "Analyze Site Image"}
        </button>

        <p className="safety-connection">
          Backend: <strong>{backend ? "Online" : "Offline"}</strong>
          {" · "}
          Model: <strong>{model ? "Ready" : "Unavailable"}</strong>
        </p>
      </div>

      {error && (
        <div className="safety-error" role="alert">
          {error}
        </div>
      )}

      {results && (
        <div className="safety-results" aria-live="polite">
          <h3>Analysis Results</h3>

          <div className="safety-result-count">
            <span>Detected objects</span>
            <strong>{objectCount}</strong>
          </div>

          {results.message && <p>{results.message}</p>}

          {detections.length > 0 ? (
            <div className="safety-detection-list">
              {detections.map((item, index) => (
                <article className="module" key={index}>
                  <div>
                    <h3>{item.object || "Detected object"}</h3>
                    <p>
                      Confidence:{" "}
                      {item.confidence != null
                        ? `${item.confidence}%`
                        : "Not provided"}
                    </p>
                    {Array.isArray(item.box) && (
                      <p>Bounding box: {item.box.join(", ")}</p>
                    )}
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <p>No objects were returned by the model.</p>
          )}

          <div className="safety-notice">
            These are general object-detection results, not a verified
            safety inspection. No detection does not prove that a worker
            is missing protective equipment.
          </div>
        </div>
      )}
    </section>
  );
}

function CostEstimator() {
  const [area, setArea] = useState("1000");
  const [rate, setRate] = useState("1800");
  const [type, setType] = useState("Residential");
  const [quality, setQuality] = useState("Standard");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function calculate(event) {
    event.preventDefault();

    const a = Number(area);
    const r = Number(rate);

    if (
      !area.trim() ||
      !rate.trim() ||
      !Number.isFinite(a) ||
      !Number.isFinite(r) ||
      a <= 0 ||
      r <= 0
    ) {
      setError("Enter a valid area and rate greater than zero.");
      setResult(null);
      return;
    }

    setError("");

    const multiplier = { Basic: 0.85, Standard: 1, Premium: 1.3 };
    const total = a * r * multiplier[quality];

    setResult({
      area: a,
      rate: r,
      type,
      quality,
      total,
      materials: total * 0.55,
      labour: total * 0.25,
      finishing: total * 0.2,
    });
  }

  const money = (value) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(value);

  return (
    <section className="panel">
      <h2>💰 Construction Cost Estimator</h2>
      <p>Enter the area and estimated local cost per square foot.</p>

      <form className="assistant-form" onSubmit={calculate}>
        <div className="form-grid">
          <label>
            Built-up area (sq. ft.)
            <input
              type="number"
              min="1"
              step="any"
              required
              value={area}
              onChange={(e) => setArea(e.target.value)}
            />
          </label>

          <label>
            Cost per square foot (₹)
            <input
              type="number"
              min="1"
              step="any"
              required
              value={rate}
              onChange={(e) => setRate(e.target.value)}
            />
          </label>

          <label>
            Building type
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <option>Residential</option>
              <option>Commercial</option>
            </select>
          </label>

          <label>
            Construction quality
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
            >
              <option>Basic</option>
              <option>Standard</option>
              <option>Premium</option>
            </select>
          </label>
        </div>

        <button className="primary-button" type="submit">
          Generate Estimate
        </button>
      </form>

      {error && (
        <p className="status-message" role="alert">
          {error}
        </p>
      )}

      {result && (
        <div className="estimate-result" aria-live="polite">
          <h2>Estimated Total: {money(result.total)}</h2>
          <p>Area: {result.area.toLocaleString("en-IN")} sq. ft.</p>
          <p>Rate: {money(result.rate)} per sq. ft.</p>
          <p>
            Building: {result.type} · Quality: {result.quality}
          </p>
          <hr />
          <h3>Estimated Breakdown</h3>
          <p>Materials (55%): {money(result.materials)}</p>
          <p>Labour (25%): {money(result.labour)}</p>
          <p>Finishing (20%): {money(result.finishing)}</p>
          <small>
            Illustrative estimate only, not a contractor quotation or live
            market price.
          </small>
        </div>
      )}
    </section>
  );
}

function AssistantFAQ() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const faqs = [
    {
      words: ["concrete", "cement"],
      text:
        "Concrete commonly uses cement, water, sand, and coarse aggregate. The mix depends on engineering specifications.",
    },
    {
      words: ["helmet", "safety", "ppe"],
      text:
        "Use appropriate PPE and follow site safety procedures and applicable safety requirements.",
    },
    {
      words: ["crack", "wall"],
      text:
        "Cracks can have different causes. Significant or growing cracks should be inspected by a qualified structural engineer.",
    },
    {
      words: ["cost", "budget", "price"],
      text:
        "Construction costs depend on location, area, design, labour, materials, and finishes. Try the Cost Estimator module.",
    },
    {
      words: ["brick", "bricks"],
      text:
        "Brick quantities depend on wall dimensions, brick size, mortar joints, and openings such as doors and windows.",
    },
  ];

  function answerQuestion(event) {
    event.preventDefault();
    const q = question.trim().toLowerCase();

    if (!q) {
      setAnswer("Please enter a question.");
      return;
    }

    const match = faqs.find((item) =>
      item.words.some((word) => q.includes(word))
    );

    setAnswer(
      match
        ? match.text
        : "This demo supports questions about concrete, safety, cracks, cost, and bricks. It is not connected to a live AI model."
    );
  }

  return (
    <section className="panel">
      <h2>🤖 Construction AI Assistant</h2>
      <p>Ask a construction question.</p>

      <form className="assistant-form" onSubmit={answerQuestion}>
        <label htmlFor="question">Your question</label>
        <textarea
          id="question"
          rows="4"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Example: What causes cracks in walls?"
        />
        <button className="primary-button" type="submit">
          Get Answer
        </button>
      </form>

      {answer && (
        <div className="estimate-result" role="status">
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}
    </section>
  );
}

export default App;
