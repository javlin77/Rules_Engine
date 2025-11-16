import React, { useState, useEffect } from "react";

export default function CreateRuleModal({ onClose, onCreate }) {
  useEffect(() => {
    console.log("CreateRuleModal mounted");
  }, []);

  const [formData, setFormData] = useState({
    name: "10% off for premium users",
    priority: 100,
    description: "",
    conditions: JSON.stringify(
      {
        type: "AND",
        clauses: [
          { field: "context.user.tier", op: "==", value: "premium" },
          { field: "event.cart.total", op: ">=", value: 1000 }
        ]
      },
      null,
      2
    ),
    actions: JSON.stringify([
      { type: "apply_discount", payload: { percent: 10 } },
      { type: "log", payload: { tag: "promo_applied" } }
    ], null, 2),
    tags: "discount, promo",
    stop_on_match: false,
  });

  const handleSubmit = () => {
    console.log("handleSubmit clicked");
    try {
      const conditions = JSON.parse(formData.conditions);
      const actionsRaw = JSON.parse(formData.actions);

      // normalize actions to objects with type + payload
      const actions = Array.isArray(actionsRaw)
        ? actionsRaw.map((a) => ({ type: a.type || "unknown", payload: a.payload || {} }))
        : [];

      const ruleData = {
        name: formData.name,
        priority: parseInt(formData.priority || 100, 10),
        conditions,
        actions,
        tags: formData.tags.split(",").map((t) => t.trim()).filter(Boolean),
        stop_on_match: formData.stop_on_match || false,
        description: formData.description || null,
      };

      console.log("creating rule:", ruleData);
      onCreate(ruleData);
    } catch (e) {
      console.error("invalid json", e);
      alert("Invalid JSON in conditions or actions. Check console for details.");
    }
  };

  return (
    <div 
      style={{ 
        position: "fixed", 
        inset: 0, 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center", 
        background: "rgba(0,0,0,0.6)",
        zIndex: 1000,
        padding: "20px"
      }}
      onClick={onClose}
    >
      <div 
        style={{ 
          width: "100%", 
          maxWidth: 760, 
          maxHeight: "90vh",
          background: "#0f172a", 
          color: "#fff", 
          borderRadius: 12, 
          padding: 20,
          overflowY: "auto",
          overflowX: "hidden"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ marginBottom: 12 }}>
          <h2 style={{ margin: 0 }}>Create New Rule</h2>
        </div>

        <div style={{ display: "grid", gap: 12 }}>
          <div>
            <label>Rule Name</label>
            <input value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} style={{ width: "100%", padding: 8, borderRadius: 8 }} />
          </div>

          <div>
            <label>Priority</label>
            <input type="number" value={formData.priority} onChange={(e) => setFormData({ ...formData, priority: e.target.value })} style={{ width: "100%", padding: 8, borderRadius: 8 }} />
          </div>

          <div>
            <label>Conditions (JSON)</label>
            <textarea rows={6} value={formData.conditions} onChange={(e) => setFormData({ ...formData, conditions: e.target.value })} style={{ width: "100%", padding: 8, borderRadius: 8, fontFamily: "monospace" }} />
          </div>

          <div>
            <label>Actions (JSON array)</label>
            <textarea rows={4} value={formData.actions} onChange={(e) => setFormData({ ...formData, actions: e.target.value })} style={{ width: "100%", padding: 8, borderRadius: 8, fontFamily: "monospace" }} />
          </div>

          <div>
            <label>Description (optional)</label>
            <textarea 
              rows={2} 
              value={formData.description} 
              onChange={(e) => setFormData({ ...formData, description: e.target.value })} 
              style={{ width: "100%", padding: 8, borderRadius: 8 }} 
              placeholder="Rule description..."
            />
          </div>

          <div>
            <label>Tags (comma separated)</label>
            <input value={formData.tags} onChange={(e) => setFormData({ ...formData, tags: e.target.value })} style={{ width: "100%", padding: 8, borderRadius: 8 }} />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input 
              type="checkbox" 
              checked={formData.stop_on_match} 
              onChange={(e) => setFormData({ ...formData, stop_on_match: e.target.checked })} 
              id="stop_on_match"
            />
            <label htmlFor="stop_on_match" style={{ fontSize: 14 }}>Stop evaluation on match</label>
          </div>

          <div style={{ fontSize: 12, color: "#c7b6ff", padding: 8, background: "rgba(255,255,255,0.05)", borderRadius: 8 }}>
            <strong>Supported operators:</strong> ==, !=, &gt;, &gt;=, &lt;, &lt;=, in, not_in, contains, regex, starts_with, ends_with
            <br />
            <strong>Example:</strong> {`{ "field": "event.amount", "op": ">=", "value": 1000 }`}
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={handleSubmit} style={{ flex: 1, padding: 10, background: "#7c3aed", color: "#fff", borderRadius: 8 }}>
              Create Rule
            </button>
            <button onClick={onClose} style={{ flex: 1, padding: 10, background: "#111827", color: "#fff", borderRadius: 8 }}>
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
