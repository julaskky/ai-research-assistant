import { useEffect, useState } from "react";
import axios from "axios";
import {
  BookOpen,
  FileText,
  Search,
  Sparkles,
  StickyNote,
  Upload,
  X,
} from "lucide-react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [papers, setPapers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [selectedPaper, setSelectedPaper] = useState(null);
  const [paperText, setPaperText] = useState("");
  const [loadingPaper, setLoadingPaper] = useState(false);

  const [summary, setSummary] = useState("");
  const [loadingSummary, setLoadingSummary] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loadingAnswer, setLoadingAnswer] = useState(false);

  const fetchPapers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/papers`);
      setPapers(response.data);
    } catch (error) {
      console.error("Failed to load papers:", error);
      setError("Unable to load papers. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are allowed.");
      event.target.value = "";
      return;
    }

    setUploading(true);
    setMessage("");
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      await axios.post(
        `${API_BASE_URL}/papers/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setMessage(`"${file.name}" uploaded successfully.`);
      await fetchPapers();
    } catch (error) {
      console.error("Upload failed:", error);

      const detail =
        error.response?.data?.detail ||
        "Paper upload failed. Please try again.";

      setError(detail);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const openPaper = async (paper) => {
    setSelectedPaper(paper);
    setPaperText("");
    setSummary("");
    setAnswer("");
    setSources([]);
    setQuestion("");
    setLoadingPaper(true);
    setMessage("");
    setError("");

    try {
      const response = await axios.get(
        `${API_BASE_URL}/papers/${paper.id}/text`
      );

      setPaperText(response.data.extracted_text || "");
    } catch (error) {
      console.error("Failed to load paper text:", error);
      setError("Unable to load the paper text.");
    } finally {
      setLoadingPaper(false);
    }
  };

  const closePaper = () => {
    setSelectedPaper(null);
    setPaperText("");
    setSummary("");
    setAnswer("");
    setSources([]);
    setQuestion("");
  };

  const handleSummarize = async (paper) => {
    setSelectedPaper(paper);
    setSummary("");
    setAnswer("");
    setSources([]);
    setLoadingSummary(true);
    setMessage("");
    setError("");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/papers/${paper.id}/summarize`
      );

      setSummary(response.data.summary || "No summary was generated.");
    } catch (error) {
      console.error("Summarization failed:", error);

      const detail =
        error.response?.data?.detail ||
        "Unable to summarize this paper.";

      setError(detail);
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleAskAI = async () => {
    if (!selectedPaper) {
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoadingAnswer(true);
    setAnswer("");
    setSources([]);
    setError("");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/papers/${selectedPaper.id}/ask`,
        {
          question: question.trim(),
        }
      );

      setAnswer(response.data.answer || "No answer was generated.");
      setSources(response.data.sources || []);
    } catch (error) {
      console.error("Question answering failed:", error);

      const detail =
        error.response?.data?.detail ||
        "Unable to answer the question.";

      setError(detail);
    } finally {
      setLoadingAnswer(false);
    }
  };

  const filteredPapers = papers.filter((paper) => {
    const query = search.toLowerCase();

    return (
      paper.title?.toLowerCase().includes(query) ||
      paper.filename?.toLowerCase().includes(query) ||
      paper.authors?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={22} />
          </div>

          <div>
            <h1>Research AI</h1>
            <span>Academic Assistant</span>
          </div>
        </div>

        <nav>
          <a className="nav-item active">
            <BookOpen size={18} />
            Dashboard
          </a>

          <a className="nav-item">
            <FileText size={18} />
            Papers
          </a>

          <a className="nav-item">
            <StickyNote size={18} />
            Research Notes
          </a>
        </nav>

        <label className="upload-button">
          <Upload size={18} />
          {uploading ? "Uploading..." : "Upload Paper"}

          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">RESEARCH WORKSPACE</p>
            <h2>Good to see you.</h2>
            <p className="subtitle">
              Organize, explore, and understand your academic research.
            </p>
          </div>

          <div className="search-box">
            <Search size={18} />

            <input
              type="text"
              placeholder="Search papers..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
        </header>

        {message && (
          <div className="success-message">
            {message}
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <FileText size={20} />
            </div>

            <div>
              <span>Total Papers</span>
              <strong>{papers.length}</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <StickyNote size={20} />
            </div>

            <div>
              <span>Research Notes</span>
              <strong>—</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Sparkles size={20} />
            </div>

            <div>
              <span>AI Assistant</span>
              <strong>Ready</strong>
            </div>
          </div>
        </section>

        <section className="section-header">
          <div>
            <h3>My Research Papers</h3>
            <p>Recently uploaded academic papers</p>
          </div>

          <label className="secondary-button">
            <Upload size={17} />
            {uploading ? "Uploading..." : "Upload Paper"}

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleUpload}
              disabled={uploading}
              hidden
            />
          </label>
        </section>

        {loading ? (
          <div className="empty-state">
            <p>Loading papers...</p>
          </div>
        ) : filteredPapers.length === 0 ? (
          <div className="empty-state">
            <FileText size={36} />
            <h3>No papers found</h3>
            <p>Upload an academic paper to get started.</p>
          </div>
        ) : (
          <div className="paper-grid">
            {filteredPapers.map((paper) => (
              <article className="paper-card" key={paper.id}>
                <div className="paper-icon">
                  <FileText size={22} />
                </div>

                <div className="paper-content">
                  <h3>{paper.title || paper.filename}</h3>

                  <p className="paper-meta">
                    {paper.authors || "Author information unavailable"}
                  </p>

                  <div className="paper-details">
                    {paper.publication_year && (
                      <span>{paper.publication_year}</span>
                    )}

                    {paper.journal && (
                      <span>{paper.journal}</span>
                    )}
                  </div>

                  <div className="paper-actions">
                    <button onClick={() => openPaper(paper)}>
                      View Paper
                    </button>

                    <button onClick={() => handleSummarize(paper)}>
                      Summarize
                    </button>

                    <button onClick={() => {
                      setSelectedPaper(paper);
                      setSummary("");
                      setAnswer("");
                      setSources([]);
                      setQuestion("");
                      setError("");
                    }}>
                      Ask AI
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>

      {selectedPaper && (
        <div className="modal-overlay" onClick={closePaper}>
          <div
            className="modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <p className="eyebrow">RESEARCH ASSISTANT</p>
                <h2>
                  {selectedPaper.title || selectedPaper.filename}
                </h2>
              </div>

              <button
                className="close-button"
                onClick={closePaper}
                aria-label="Close"
              >
                <X size={20} />
              </button>
            </div>

            {loadingPaper && (
              <div className="modal-section">
                <p>Loading paper...</p>
              </div>
            )}

            {!loadingPaper && paperText && (
              <div className="modal-section">
                <h3>Paper Text</h3>
                <div className="paper-text">
                  {paperText}
                </div>
              </div>
            )}

            {loadingSummary && (
              <div className="modal-section">
                <h3>AI Summary</h3>
                <p>Generating summary...</p>
              </div>
            )}

            {summary && (
              <div className="modal-section">
                <h3>
                  <Sparkles size={18} />
                  AI Summary
                </h3>

                <p className="summary-text">
                  {summary}
                </p>
              </div>
            )}

            <div className="modal-section">
              <h3>
                <Sparkles size={18} />
                Ask AI About This Paper
              </h3>

              <div className="question-box">
                <textarea
                  placeholder="Ask a question about this paper..."
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  rows={4}
                />

                <button
                  className="primary-button"
                  onClick={handleAskAI}
                  disabled={loadingAnswer}
                >
                  {loadingAnswer ? "Thinking..." : "Ask AI"}
                </button>
              </div>

              {answer && (
                <div className="answer-box">
                  <h4>Answer</h4>
                  <p>{answer}</p>
                </div>
              )}

              {sources.length > 0 && (
                <div className="sources-box">
                  <h4>Retrieved Sources</h4>

                  {sources.map((source, index) => (
                    <div className="source-item" key={index}>
                      {source}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
