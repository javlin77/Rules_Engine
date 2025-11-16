import React, { useState, useEffect } from "react";

export default function SimulateModal({ rule, onClose, onSimulate, result, loading }) {
  // Generate example data based on rule conditions
  const getExampleData = () => {
    const conditions = rule?.conditions || {};
    
    // Default examples
    let eventExample = {};
    let contextExample = { user: {} };
    
    // Recursively process conditions to extract field requirements
    const processClause = (clause) => {
      if (!clause) return;
      
      // Handle nested AND/OR conditions
      if (clause.type && clause.clauses) {
        clause.clauses.forEach(processClause);
        return;
      }
      
      // Handle function calls
      if (clause.fn) {
        if (clause.fn === "days_since" && clause.args && clause.args[0]) {
          const fieldPath = clause.args[0];
          if (fieldPath.includes("event.timestamp")) {
            eventExample.timestamp = new Date().toISOString();
          } else if (fieldPath.includes("context.user.signup_date")) {
            const date = new Date();
            date.setDate(date.getDate() - 5);
            contextExample.user.signup_date = date.toISOString().split('T')[0];
          }
        }
        return;
      }
      
      // Handle field comparisons
      const field = clause.field || "";
      const op = clause.op || "";
      const value = clause.value;
      
      if (!field) return;
      
      // Process event fields
      if (field.startsWith("event.")) {
        const fieldName = field.replace("event.", "");
        
        if (fieldName === "type") {
          eventExample.type = value || "purchase";
        } else if (fieldName === "amount") {
          // For > operator, make it higher; for <, make it lower
          if (op === ">") {
            eventExample.amount = value ? value + 1000 : 11000;
          } else if (op === ">=") {
            eventExample.amount = value ? value + 100 : 1100;
          } else if (op === "<") {
            eventExample.amount = value ? value - 100 : 900;
          } else {
            eventExample.amount = value || 1000;
          }
        } else if (fieldName === "stock_level") {
          if (op === "<=") {
            eventExample.stock_level = value ? value - 1 : 9;
          } else {
            eventExample.stock_level = value || 10;
          }
        } else if (fieldName === "product_category") {
          eventExample.product_category = value || "alcohol";
        } else if (fieldName === "day_of_week") {
          eventExample.day_of_week = value && Array.isArray(value) ? value[0] : "Saturday";
        } else if (fieldName.includes("cart.total")) {
          if (!eventExample.cart) eventExample.cart = {};
          if (op === ">=") {
            eventExample.cart.total = value ? value + 100 : 600;
          } else {
            eventExample.cart.total = value || 500;
          }
        } else if (fieldName === "timestamp") {
          eventExample.timestamp = new Date().toISOString();
        }
      }
      
      // Process context fields
      if (field.startsWith("context.")) {
        const fieldPath = field.replace("context.", "").split(".");
        let current = contextExample;
        
        for (let i = 0; i < fieldPath.length - 1; i++) {
          if (!current[fieldPath[i]]) {
            current[fieldPath[i]] = {};
          }
          current = current[fieldPath[i]];
        }
        
        const lastField = fieldPath[fieldPath.length - 1];
        
        if (lastField === "tier") {
          current.tier = value || "premium";
        } else if (lastField === "account_status") {
          if (op === "!=") {
            current.account_status = value === "frozen" ? "active" : "active";
          } else {
            current.account_status = value || "active";
          }
        } else if (lastField === "signup_date") {
          const date = new Date();
          date.setDate(date.getDate() - 5);
          current.signup_date = date.toISOString().split('T')[0];
        } else if (lastField === "transaction_countries") {
          // For contains operator, ensure the value is in the array
          if (op === "contains") {
            current.transaction_countries = value ? [value, "UK", "CA"] : ["US", "UK"];
          } else {
            current.transaction_countries = Array.isArray(value) ? value : [value || "US"];
          }
        } else if (lastField === "suspicious_activity") {
          current.suspicious_activity = value !== undefined ? value : true;
        } else if (lastField === "age") {
          if (op === "<") {
            current.age = value ? value - 1 : 20;
          } else {
            current.age = value || 25;
          }
        }
      }
    };
    
    // Process all clauses
    if (conditions.clauses) {
      conditions.clauses.forEach(processClause);
    } else if (conditions.field) {
      processClause(conditions);
    }
    
    // Set defaults if nothing was set
    if (Object.keys(eventExample).length === 0) {
      eventExample = { type: "purchase", amount: 1000 };
    }
    if (Object.keys(contextExample.user).length === 0) {
      contextExample.user = { tier: "premium" };
    }
    
    return {
      event: eventExample,
      context: contextExample
    };
  };

  const exampleData = getExampleData();
  const [eventData, setEventData] = useState(JSON.stringify(exampleData.event, null, 2));
  const [contextData, setContextData] = useState(JSON.stringify(exampleData.context, null, 2));
  
  // Reset to examples when rule changes
  useEffect(() => {
    if (rule) {
      const newExamples = getExampleData();
      setEventData(JSON.stringify(newExamples.event, null, 2));
      setContextData(JSON.stringify(newExamples.context, null, 2));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rule?.id]);

  const run = () => {
    try {
      const event = JSON.parse(eventData);
      const context = JSON.parse(contextData);
      onSimulate(rule.id, event, context);
    } catch {
      alert("Invalid JSON");
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
        <h2 style={{ marginTop: 0 }}>Simulate Rule: {rule.name}</h2>
        
        {rule.description && (
          <div style={{ marginBottom: 12, padding: 8, background: "rgba(255,255,255,0.05)", borderRadius: 8, fontSize: 14, color: "#c7b6ff" }}>
            {rule.description}
          </div>
        )}

        <div style={{ marginBottom: 8 }}>
          <label style={{ display: "block", marginBottom: 4 }}>
            Event (JSON) - The event data being evaluated
          </label>
          <textarea 
            rows={6} 
            value={eventData} 
            onChange={(e) => setEventData(e.target.value)} 
            style={{ width: "100%", padding: 8, borderRadius: 8, fontFamily: "monospace", background: "#1e293b", color: "#fff", border: "1px solid rgba(255,255,255,0.1)" }} 
            placeholder='Example: {"type": "purchase", "amount": 1000}'
          />
          <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>
            💡 Tip: Use fields like <code>event.type</code>, <code>event.amount</code>, <code>event.cart.total</code>
          </div>
        </div>

        <div style={{ marginBottom: 8 }}>
          <label style={{ display: "block", marginBottom: 4 }}>
            Context (JSON) - Additional context data (user info, etc.)
          </label>
          <textarea 
            rows={4} 
            value={contextData} 
            onChange={(e) => setContextData(e.target.value)} 
            style={{ width: "100%", padding: 8, borderRadius: 8, fontFamily: "monospace", background: "#1e293b", color: "#fff", border: "1px solid rgba(255,255,255,0.1)" }} 
            placeholder='Example: {"user": {"tier": "premium", "account_status": "active"}}'
          />
          <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>
            💡 Tip: Use fields like <code>context.user.tier</code>, <code>context.user.account_status</code>, <code>context.user.signup_date</code>
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <button 
            onClick={run} 
            disabled={loading} 
            style={{ flex: 1, padding: 10, background: "#7c3aed", color: "#fff", borderRadius: 8, border: "none", cursor: loading ? "not-allowed" : "pointer" }}
          >
            {loading ? "Running..." : "Run Simulation"}
          </button>
          <button 
            onClick={() => {
              const examples = getExampleData();
              setEventData(JSON.stringify(examples.event, null, 2));
              setContextData(JSON.stringify(examples.context, null, 2));
            }}
            style={{ padding: "10px 16px", background: "#475569", color: "#fff", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 12 }}
            title="Reset to example values"
          >
            Reset Examples
          </button>
        </div>

        {result && (
          <div style={{ marginTop: 12, padding: 12, background: result.matched ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)", borderRadius: 8 }}>
            <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>
              {result.matched ? "✅ Matched" : "❌ Not Matched"}
            </div>
            {result.matched && (
              <>
                <div style={{ marginBottom: 8 }}>
                  <strong>Actions that would execute:</strong>
                </div>
                <pre style={{ background: "#111827", padding: 10, borderRadius: 8, overflow: "auto", fontSize: 12 }}>
                  {JSON.stringify(result.would_execute, null, 2)}
                </pre>
              </>
            )}
            {result.explanation && (
              <div style={{ marginTop: 12 }}>
                <strong>Explanation:</strong>
                <pre style={{ background: "#111827", padding: 10, borderRadius: 8, overflow: "auto", fontSize: 11, marginTop: 4 }}>
                  {JSON.stringify(result.explanation, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: 12 }}>
          <button onClick={onClose} style={{ padding: 8, background: "#111827", color: "#fff", borderRadius: 8 }}>Close</button>
        </div>
      </div>
    </div>
  );
}
