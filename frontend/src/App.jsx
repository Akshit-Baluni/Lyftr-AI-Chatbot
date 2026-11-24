
import { useState, useEffect, useRef } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function createSessionId() {
  return crypto.randomUUID();
}

function App() {
  const [sessionId, setSessionId] = useState(() => createSessionId());
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const messagesEndRef = useRef(null);

  // =====================================================
  // AUTO SCROLL
  // =====================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // =====================================================
  // LOAD ALL SESSIONS
  // =====================================================

  useEffect(() => {
    fetchSessions();
  }, []);

  async function fetchSessions() {
    try {
      const response = await fetch(`${API_URL}/sessions`);

      if (!response.ok) {
        throw new Error("Unable to load chat history.");
      }

      const data = await response.json();

      setSessions(data.sessions || []);
    } catch (err) {
      console.error("Sessions loading error:", err);
    }
  }

  // =====================================================
  // SEND MESSAGE
  // =====================================================

  async function sendMessage(e) {
    e.preventDefault();

    const message = input.trim();

    if (!message || loading) return;

    setError("");
    setInput("");

    const userMessage = {
      role: "user",
      content: message,
    };

    setMessages((previous) => [...previous, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: message,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message ||
          data.detail ||
          `Request failed with status ${response.status}`
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.reply,
          metadata: data.metadata,
        },
      ]);

      // Refresh sidebar after a conversation update
      await fetchSessions();

    } catch (err) {
      console.error("Chat request error:", err);

      if (err instanceof TypeError) {
        setError(
          "Unable to connect to Lyftr AI. Please check whether the backend server is running."
        );
      } else {
        setError(
          err.message ||
          "Lyftr AI is temporarily unavailable. Please try again later."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  // =====================================================
  // NEW CHAT
  // =====================================================

  function startNewChat() {
    setSessionId(createSessionId());
    setMessages([]);
    setInput("");
    setError("");
  }

  // =====================================================
  // OPEN EXISTING CHAT
  // =====================================================

  async function openSession(selectedSessionId) {
    if (loading || historyLoading) return;

    setHistoryLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/sessions/${selectedSessionId}/messages`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || "Unable to load this conversation."
        );
      }

      setSessionId(selectedSessionId);
      setMessages(data.messages || []);
      setInput("");

    } catch (err) {
      console.error("Conversation loading error:", err);
      setError(err.message || "Unable to load conversation.");
    } finally {
      setHistoryLoading(false);
    }
  }

  // =====================================================
  // DELETE CHAT
  // =====================================================

  async function deleteSession(selectedSessionId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this conversation?"
    );

    if (!confirmed) return;

    try {
      const response = await fetch(
        `${API_URL}/sessions/${selectedSessionId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || "Unable to delete conversation."
        );
      }

      setSessions((previous) =>
        previous.filter(
          (session) => session.session_id !== selectedSessionId
        )
      );

      // If the deleted conversation is currently open,
      // switch to a fresh chat.
      if (sessionId === selectedSessionId) {
        startNewChat();
      }

    } catch (err) {
      console.error("Delete chat error:", err);

      setError(
        err.message || "Unable to delete this conversation."
      );
    }
  }

  // =====================================================
  // FORMAT CHAT TITLE
  // =====================================================

  function formatTitle(title) {
    if (!title) return "New Chat";

    return title.length > 35
      ? title.substring(0, 35) + "..."
      : title;
  }

  // =====================================================
  // FRONTEND
  // =====================================================

  return (
    <div className="app-container">

      {/* SIDEBAR */}

      <aside
        className={`sidebar ${
          sidebarCollapsed ? "sidebar-collapsed" : ""
        }`}
      >

        <div className="sidebar-top">

          <div className="brand">

            <div className="brand-icon">✦</div>

            {!sidebarCollapsed && (
              <div className="brand-text">
                <h2>Lyftr AI</h2>
                <span>Intelligent assistant</span>
              </div>
            )}

          </div>

          <button
            className="sidebar-toggle"
            onClick={() =>
              setSidebarCollapsed((previous) => !previous)
            }
            title={
              sidebarCollapsed
                ? "Expand sidebar"
                : "Collapse sidebar"
            }
          >
            {sidebarCollapsed ? "☰" : "◀"}
          </button>

        </div>

        {/* NEW CHAT */}

        <button
          className="new-chat-btn"
          onClick={startNewChat}
          title="New Chat"
        >
          <span>＋</span>

          {!sidebarCollapsed && "New Chat"}
        </button>

        {!sidebarCollapsed && (

          <div className="history-section">

            <p className="section-label">
              RECENT CHATS
            </p>

            <div className="history-list">

              {sessions.length === 0 ? (

                <div className="empty-history">
                  No conversations yet
                </div>

              ) : (

                sessions.map((session) => (

                  <div
                    key={session.session_id}
                    className={`history-item ${
                      session.session_id === sessionId
                        ? "history-item-active"
                        : ""
                    }`}
                  >

                    <button
                      className="history-title-btn"
                      onClick={() =>
                        openSession(session.session_id)
                      }
                      title={session.title}
                      disabled={historyLoading || loading}
                    >
                      <span className="history-icon">◷</span>

                      <span className="history-title">
                        {formatTitle(session.title)}
                      </span>
                    </button>

                    <button
                      className="delete-chat-btn"
                      onClick={() =>
                        deleteSession(session.session_id)
                      }
                      title="Delete chat"
                    >
                      ×
                    </button>

                  </div>

                ))

              )}

            </div>

          </div>

        )}

        {sidebarCollapsed && (

          <div className="collapsed-history">

            {sessions.map((session) => (

              <button
                key={session.session_id}
                className={`collapsed-history-item ${
                  session.session_id === sessionId
                    ? "collapsed-history-active"
                    : ""
                }`}
                onClick={() =>
                  openSession(session.session_id)
                }
                title={session.title}
              >
                ◷
              </button>

            ))}

          </div>

        )}

        <div className="sidebar-footer">

          <div className="status-dot"></div>

          {!sidebarCollapsed && (
            <span>Backend connection interface</span>
          )}

        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        {/* TOPBAR */}

        <header className="topbar">

          <div className="topbar-left">

            <div>
              <span className="topbar-title">
                AI Assistant
              </span>

              <span className="online-status">
                <span className="status-dot"></span>
                Ready
              </span>
            </div>

          </div>

          <div className="topbar-actions">

            {historyLoading && (
              <span className="history-loading">
                Loading chat...
              </span>
            )}

            <button
              className="history-btn"
              onClick={fetchSessions}
              title="Refresh chat history"
            >
              ↻
            </button>

          </div>

        </header>

        {/* CHAT AREA */}

        <div className="chat-area">

          {messages.length === 0 ? (

            <div className="welcome-screen">

              <div className="welcome-icon">✦</div>

              <h1>How can I help you today?</h1>

              <p>
                Ask me anything. I'm here to help you explore ideas,
                solve problems and learn something new.
              </p>

              <div className="suggestion-grid">

                <button
                  onClick={() =>
                    setInput(
                      "Explain artificial intelligence in simple terms."
                    )
                  }
                >
                  <span>◈</span>
                  <strong>Learn something</strong>
                  <small>Explain AI in simple terms</small>
                </button>

                <button
                  onClick={() =>
                    setInput("Help me brainstorm a project idea.")
                  }
                >
                  <span>✧</span>
                  <strong>Brainstorm ideas</strong>
                  <small>Generate creative project ideas</small>
                </button>

                <button
                  onClick={() =>
                    setInput("Help me write a professional email.")
                  }
                >
                  <span>✎</span>
                  <strong>Write something</strong>
                  <small>Create a professional email</small>
                </button>

                <button
                  onClick={() =>
                    setInput("Help me solve a difficult problem.")
                  }
                >
                  <span>⌘</span>
                  <strong>Solve a problem</strong>
                  <small>Break down a complex problem</small>
                </button>

              </div>

            </div>

          ) : (

            <div className="messages-container">

              {messages.map((message, index) => (

                <div
                  key={index}
                  className={`message-row ${message.role}`}
                >

                  <div className="message-avatar">
                    {message.role === "user" ? "U" : "✦"}
                  </div>

                  <div className="message-content">

                    <div className="message-role">
                      {message.role === "user"
                        ? "You"
                        : "Lyftr AI"}
                    </div>

                    <div className="message-text">
                      {message.content}
                    </div>

                    {message.metadata && (

                      <div className="metadata">

                        <span className="source-tag">
                          {message.metadata.resolution_source}
                        </span>

                        <span>
                          {message.metadata.model}
                        </span>

                        <span>
                          {message.metadata.latency_ms} ms
                        </span>

                        <span>
                          {message.metadata.input_tokens} in /{" "}
                          {message.metadata.output_tokens} out
                        </span>

                        {message.metadata.key_id && (
                          <span>
                            Key: {message.metadata.key_id}
                          </span>
                        )}

                        {message.metadata.fallback_attempts > 0 && (
                          <span>
                            Fallbacks:{" "}
                            {message.metadata.fallback_attempts}
                          </span>
                        )}

                      </div>

                    )}

                  </div>

                </div>

              ))}

              {loading && (

                <div className="message-row assistant">

                  <div className="message-avatar">✦</div>

                  <div className="message-content">

                    <div className="message-role">
                      Lyftr AI
                    </div>

                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                  </div>

                </div>

              )}

              <div ref={messagesEndRef} />

            </div>

          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

        </div>

        {/* INPUT AREA */}

        <div className="input-section">

          <form
            className="chat-input-form"
            onSubmit={sendMessage}
          >

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message Lyftr AI..."
              rows={1}
              onKeyDown={(e) => {
                if (
                  e.key === "Enter" &&
                  !e.shiftKey
                ) {
                  e.preventDefault();
                  sendMessage(e);
                }
              }}
            />

            <button
              className="send-button"
              type="submit"
              disabled={!input.trim() || loading}
            >
              ↑
            </button>

          </form>

          <p className="input-disclaimer">
            Lyftr AI may generate inaccurate information.
            Verify important details.
          </p>

        </div>

      </main>

    </div>
  );
}

export default App;