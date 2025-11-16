import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Plus, Play, Trash2, CheckCircle, XCircle, History, Eye, Zap } from "lucide-react";
import CreateRuleModal from "./components/CreateRuleModal";
import SimulateModal from "./components/SimulateModal";

const API_URL = "http://localhost:8000";

export default function App() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [rules, setRules] = useState([]);
  const [selectedRule, setSelectedRule] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("rules"); // "rules" or "audit"
  const [auditLogs, setAuditLogs] = useState([]);
  const [evaluationResult, setEvaluationResult] = useState(null);

  // Derive modal states from URL
  const showCreateModal = searchParams.get("modal") === "create";
  const simulateRuleId = searchParams.get("ruleId");
  const showSimulateModal = searchParams.get("modal") === "simulate" && simulateRuleId;

  useEffect(() => {
    fetchRules();
    if (activeTab === "audit") {
      fetchAuditLogs();
    }
  }, [activeTab]);

  // Update selectedRule when simulate modal opens via URL
  useEffect(() => {
    if (showSimulateModal && simulateRuleId) {
      const rule = rules.find(r => r.id === simulateRuleId);
      if (rule) {
        setSelectedRule(rule);
      }
    } else if (!showSimulateModal) {
      // Clear selected rule when modal closes
      setSelectedRule(null);
    }
  }, [showSimulateModal, simulateRuleId, rules]);

  const fetchRules = async () => {
    try {
      const res = await fetch(`${API_URL}/rules`);
      const data = await res.json();
      setRules(data);
    } catch (e) {
      console.error("Fetch rules failed", e);
    }
  };

  const createRule = async (ruleData) => {
    try {
      const res = await fetch(`${API_URL}/rules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ruleData),
      });

      if (!res.ok) {
        const body = await res.text();
        console.error("Create failed:", res.status, body);
        alert("Create rule failed. Check console for details.");
        return;
      }

      // refresh
      await fetchRules();
      // Close modal by removing URL param
      navigate("/");
    } catch (e) {
      console.error("Create rule error", e);
      alert("Create rule error. Check console.");
    }
  };

  const toggleRuleStatus = async (id, current) => {
    try {
      const res = await fetch(`${API_URL}/rules/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active: !current }),
      });
      if (res.ok) fetchRules();
    } catch (e) {
      console.error(e);
    }
  };

  const deleteRule = async (id) => {
    if (!confirm("Delete rule?")) return;
    try {
      const res = await fetch(`${API_URL}/rules/${id}`, { method: "DELETE" });
      if (res.ok) fetchRules();
    } catch (e) {
      console.error(e);
    }
  };

  const simulateRule = async (ruleId, event, context) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/rules/${ruleId}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event, context }),
      });
      const data = await res.json();
      setSimulationResult(data);
    } catch (e) {
      console.error(e);
      alert("Simulation failed. Check console.");
    } finally {
      setLoading(false);
    }
  };

  const evaluateEvent = async (event, context, asyncMode = false) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event, context, async_mode: asyncMode }),
      });
      const data = await res.json();
      setEvaluationResult(data);
      if (activeTab === "audit") {
        fetchAuditLogs();
      }
    } catch (e) {
      console.error(e);
      alert("Evaluation failed. Check console.");
    } finally {
      setLoading(false);
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/audit?limit=50`);
      const data = await res.json();
      setAuditLogs(data);
    } catch (e) {
      console.error("Fetch audit logs failed", e);
    }
  };

  return (
    <div className="min-h-screen p-8" style={{ background: "linear-gradient(#0f172a,#312e81)" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto", color: "#fff" }}>
        <header className="flex items-center justify-between mb-6">
          <div>
            <h1 style={{ fontSize: 28, margin: 0 }}>Rules Engine</h1>
            <p style={{ color: "#c7b6ff" }}>Manage and test rules</p>
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            <button
              onClick={() => navigate("?modal=create")}
              className="px-4 py-2 rounded-md"
              style={{ background: "#7c3aed", color: "#fff", display: "flex", gap: 8, alignItems: "center" }}
            >
              <Plus size={18} /> Create Rule
            </button>
            <button
              onClick={() => {
                const event = { type: "purchase", amount: 1200, user_id: "u_1" };
                const context = { user: { tier: "premium", signup_date: "2024-02-01" } };
                evaluateEvent(event, context);
              }}
              className="px-4 py-2 rounded-md"
              style={{ background: "#059669", color: "#fff", display: "flex", gap: 8, alignItems: "center" }}
            >
              <Zap size={18} /> Quick Test
            </button>
          </div>
        </header>

        <div style={{ display: "flex", gap: 8, marginBottom: 16, borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
          <button
            onClick={() => setActiveTab("rules")}
            style={{
              padding: "8px 16px",
              background: activeTab === "rules" ? "#7c3aed" : "transparent",
              color: "#fff",
              border: "none",
              cursor: "pointer",
              borderRadius: "8px 8px 0 0"
            }}
          >
            Rules
          </button>
          <button
            onClick={() => setActiveTab("audit")}
            style={{
              padding: "8px 16px",
              background: activeTab === "audit" ? "#7c3aed" : "transparent",
              color: "#fff",
              border: "none",
              cursor: "pointer",
              borderRadius: "8px 8px 0 0"
            }}
          >
            <History size={16} style={{ display: "inline", marginRight: 4 }} />
            Audit Logs
          </button>
        </div>

        {activeTab === "rules" && (
          <>
            <div className="mb-6 grid grid-cols-3 gap-4">
              <div style={{ padding: 16, background: "rgba(255,255,255,0.03)", borderRadius: 12 }}>
                <div style={{ color: "#c7b6ff", fontSize: 12 }}>Total Rules</div>
                <div style={{ fontSize: 22 }}>{rules.length}</div>
              </div>
              <div style={{ padding: 16, background: "rgba(255,255,255,0.03)", borderRadius: 12 }}>
                <div style={{ color: "#c7b6ff", fontSize: 12 }}>Active Rules</div>
                <div style={{ fontSize: 22 }}>{rules.filter((r) => r.active).length}</div>
              </div>
              <div style={{ padding: 16, background: "rgba(255,255,255,0.03)", borderRadius: 12 }}>
                <div style={{ color: "#c7b6ff", fontSize: 12 }}>Inactive Rules</div>
                <div style={{ fontSize: 22 }}>{rules.filter((r) => !r.active).length}</div>
              </div>
            </div>

            {evaluationResult && (
              <div style={{ marginBottom: 16, padding: 16, background: "rgba(59, 130, 246, 0.1)", borderRadius: 12, border: "1px solid rgba(59, 130, 246, 0.3)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <strong>Last Evaluation Result</strong>
                  <button onClick={() => setEvaluationResult(null)} style={{ background: "transparent", border: "none", color: "#fff", cursor: "pointer" }}>×</button>
                </div>
                <div style={{ fontSize: 12, color: "#c7b6ff", marginBottom: 8 }}>
                  Matched Rules: {evaluationResult.matched_rules?.length || 0} | 
                  Actions: {evaluationResult.actions?.length || 0} | 
                  Time: {evaluationResult.evaluation_time_ms}ms
                </div>
                {evaluationResult.matched_rules?.length > 0 && (
                  <div style={{ fontSize: 12 }}>
                    <strong>Matched:</strong> {evaluationResult.matched_rules.join(", ")}
                  </div>
                )}
              </div>
            )}

            <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 12, overflow: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ textAlign: "left", color: "#c7b6ff", fontSize: 12 }}>
                    <th style={{ padding: "12px 16px" }}>Name</th>
                    <th style={{ padding: "12px 16px" }}>Priority</th>
                    <th style={{ padding: "12px 16px" }}>Version</th>
                    <th style={{ padding: "12px 16px" }}>Status</th>
                    <th style={{ padding: "12px 16px" }}>Tags</th>
                    <th style={{ padding: "12px 16px" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((rule) => (
                    <tr key={rule.id} style={{ borderTop: "1px solid rgba(255,255,255,0.03)" }}>
                      <td style={{ padding: "12px 16px" }}>
                        <div style={{ fontWeight: 600 }}>{rule.name}</div>
                        <div style={{ color: "#c7b6ff", fontSize: 12 }}>{rule.id}</div>
                      </td>
                      <td style={{ padding: "12px 16px" }}>{rule.priority}</td>
                      <td style={{ padding: "12px 16px" }}>v{rule.version || 1}</td>
                      <td style={{ padding: "12px 16px" }}>
                        <button 
                          onClick={() => toggleRuleStatus(rule.id, rule.active)} 
                          style={{ 
                            padding: "6px 10px", 
                            borderRadius: 8,
                            background: rule.active ? "#059669" : "#6b7280",
                            color: "#fff",
                            border: "none",
                            cursor: "pointer"
                          }}
                        >
                          {rule.active ? "Active" : "Inactive"}
                        </button>
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        {rule.tags?.slice(0, 3).map((t, i) => (
                          <span key={i} style={{ marginRight: 6, background: "#6d28d9", padding: "4px 8px", borderRadius: 6, fontSize: 12 }}>
                            {t}
                          </span>
                        ))}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <button
                          onClick={() => {
                            setSelectedRule(rule);
                            navigate(`?modal=simulate&ruleId=${rule.id}`);
                          }}
                          style={{ marginRight: 8, background: "transparent", border: "none", color: "#fff", cursor: "pointer" }}
                          title="Simulate"
                        >
                          <Play size={16} />
                        </button>
                        <button 
                          onClick={() => deleteRule(rule.id)}
                          style={{ background: "transparent", border: "none", color: "#ef4444", cursor: "pointer" }}
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {activeTab === "audit" && (
          <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 12, overflow: "auto" }}>
            <div style={{ padding: 16, borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
              <h3 style={{ margin: 0 }}>Audit Logs</h3>
              <p style={{ color: "#c7b6ff", fontSize: 12, margin: "4px 0 0 0" }}>Recent rule evaluations and decisions</p>
            </div>
            <div style={{ maxHeight: "600px", overflowY: "auto" }}>
              {auditLogs.length === 0 ? (
                <div style={{ padding: 40, textAlign: "center", color: "#c7b6ff" }}>No audit logs yet</div>
              ) : (
                auditLogs.map((log) => (
                  <div key={log.id} style={{ padding: 16, borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                      <div>
                        <strong>{log.event_type || "Unknown Event"}</strong>
                        <div style={{ fontSize: 12, color: "#c7b6ff" }}>ID: {log.event_id}</div>
                      </div>
                      <div style={{ fontSize: 12, color: "#c7b6ff" }}>
                        {new Date(log.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div style={{ fontSize: 12, marginBottom: 4 }}>
                      <strong>Matched Rules:</strong> {log.matched_rules?.length || 0}
                      {log.matched_rules?.length > 0 && ` (${log.matched_rules.join(", ")})`}
                    </div>
                    <div style={{ fontSize: 12, marginBottom: 4 }}>
                      <strong>Actions:</strong> {log.actions_taken?.length || 0}
                    </div>
                    {log.evaluation_time_ms && (
                      <div style={{ fontSize: 12, color: "#c7b6ff" }}>
                        Evaluation time: {log.evaluation_time_ms}ms
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {showCreateModal && (
          <CreateRuleModal 
            onClose={() => navigate("/")} 
            onCreate={createRule} 
          />
        )}
        {showSimulateModal && (selectedRule || simulateRuleId) && (
          <SimulateModal
            rule={selectedRule || rules.find(r => r.id === simulateRuleId)}
            onClose={() => {
              navigate("/");
              setSimulationResult(null);
              setSelectedRule(null);
            }}
            onSimulate={simulateRule}
            result={simulationResult}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
}
