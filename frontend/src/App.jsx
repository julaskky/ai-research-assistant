import { useEffect, useState } from "react";
import axios from "axios";
import {
  BookOpen,
  FileText,
  Search,
  Sparkles,
  StickyNote,
  Upload,
} from "lucide-react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [papers, setPapers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchPapers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/papers`);
      setPapers(response.data);
    } catch (error) {
      console.error("Failed to load papers:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const filteredPapers = papers.filter((paper) => {
    const query = search.toLowerCase();

    return (
      paper.title?.toLowerCase().includes(query) ||
      paper.filename?.toLowerCase().includes(query)
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

        <button className="upload-button">
          <Upload size={18} />
          Upload Paper
        </button>
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

          <button className="secondary-button">
            <Upload size={17} />
            Upload Paper
          </button>
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
                    <button>View Paper</button>
                    <button>Summarize</button>
                    <button>Ask AI</button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;