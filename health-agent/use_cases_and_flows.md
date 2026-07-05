# HealthInsight AI – Use Cases and Process Flows

This document details the system's functional boundaries (Use Case Diagram) and runtime execution sequence (Process Flow Sequence Diagram).

---

## 👥 Use Case Diagram

The use case diagram illustrates the roles of two key actors (General Users/Residents and Public Health Officers) and their interactions with the platform's core boundaries.

```mermaid
graph TD
    User([User / Resident])
    Officer([Public Health Officer])

    subgraph "HealthInsight AI Platform Boundaries"
        UC1(Ask Health Information & Symptoms)
        UC2(Verify Health Myths & Rumors)
        UC3(Request Vaccine Schedules & Guidelines)
        UC4(View Community Health Trends & KPI Cards)
        UC5(Predict Regional Risk Levels)
        UC6(Receive Safety Alerts / PII Masking Notifications)
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC6

    Officer --> UC1
    Officer --> UC3
    Officer --> UC4
    Officer --> UC5
    Officer --> UC6
```

---

## 🔄 Process Flow Diagram (Sequence Diagram)

The sequence diagram details the step-by-step transaction flow from the moment a client query hits the web server, showing validation, masking, routing, grounding, and response streaming.

```mermaid
sequenceDiagram
    autonumber
    actor U as User / UI Dashboard
    participant WS as FastAPI Web Server (/api/chat)
    participant ADK as ADK Runner
    participant Coord as Health Coordinator Agent
    participant Sec as Security Engine (security.py)
    participant Sub as Specialized Sub-Agent
    participant MCP as Local MCP Server (mcp_server.py)
    participant LLM as Gemini Flash LLM

    U->>WS: Sends query (e.g. "What is Dengue risk in Ward 1? Contact: test@mail.com")
    WS->>ADK: runner.run_async(query, session_id)
    
    %% Validation & Security Hook
    ADK->>Coord: Invoke before_agent_callback
    Coord->>Sec: validate_user_input(query)
    Sec-->>Coord: Input is Safe (No script injection/instruction bypass)
    
    %% Inline PII Redaction
    Coord->>Sec: mask_text(query)
    Sec-->>Coord: Redacted Query ("What is Dengue risk in Ward 1? Contact: [EMAIL_MASKED]")
    
    %% Plugin Hook intercept
    ADK->>Sec: PIIMaskingPlugin: before_model_callback()
    Sec-->>ADK: Continue (Payload sanitized)
    
    %% Coordinator routing evaluation
    ADK->>LLM: Evaluate query routing intent
    LLM-->>ADK: Route control to community_health_analytics_agent
    
    %% Sub-agent control & Tool call
    ADK->>Sub: Transfer execution control
    Sub->>MCP: Call tool predict_health_risk(disease="Dengue", region="Ward 1")
    
    %% MCP Execution
    MCP->>MCP: Load community_health_data.csv & compute MoM % change
    MCP-->>Sub: Tool Output ("Calculated Risk Level: High Risk, Vaccination: 80%...")
    
    %% Response Generation & Transfer back
    Sub->>LLM: Construct detailed answer with statistics
    LLM-->>ADK: Raw Agent response
    ADK->>Coord: Transfer control back to Coordinator
    Coord->>Coord: Append Medical Disclaimer footer
    
    %% Streaming Event Yield
    ADK-->>WS: Yield events (agent_event) & token streams
    WS-->>U: Stream SSE tokens to Client
    Note over U: Client displays response. Triggers modal safety alert if masked PII tokens are found.
```
