# HealthGuard - Public Health Awareness Agent System

HealthGuard is a trusted public health assistant. It simplifies medical terminology, identifies and debunks health myths, provides vaccination schedules, and suggests healthy habits.

HealthGuard is designed with **privacy-first security layers**, including input validation and automated PII masking, and features a clean, responsive single-page web application.

<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/4d8bed05-1e57-4699-80a2-c2d29988307a" />


---

## 📋 The Problem & The Solution

### The Problem
*   **Health Misinformation**: Misconceptions (e.g., "antibiotics cure viral infections") spread quickly, leading to unsafe self-treatment.
*   **Complex Terminology**: Medical details are often written in jargon, making them hard for the general public to understand.
*   **Privacy & Data Leaks**: Medical queries often contain sensitive Personal Identifiable Information (PII) like email addresses, phone numbers, or social security numbers, which should never be exposed in model logs or persistent storage.
*   **Prompt/Script Injections**: Remote chat portals are vulnerable to injection attacks (XSS, instruction overrides).

### The Solution
*   **Multi-Agent Coordination**: A central coordinator delegates tasks to specialized sub-agents (Health Information, Myth Verification, Preventive Care).
*   **MCP Grounding**: Sub-agents query a local Model Context Protocol (MCP) server for verified medical records, avoiding hallucinations.
*   **PII Masking & Input Validation**: Security hooks sanitize inputs for dangerous scripts and strip PII in transit before queries hit the LLMs.
*   **Non-Persistent Storage**: Conversation states are stored in-memory and can be manually cleared with a click.

---

## 🕸️ System Architecture

*Detailed technical documentation is available in [architecture.md](architecture.md).*

HealthGuard is structured around a coordinator-delegator pattern:

```mermaid
graph TD
    User([User/Web Dashboard]) -->|GET /api/chat| WebServer[FastAPI Web Server]
    WebServer -->|Runner.run_async| CoordinatorAgent[Health Coordinator Agent]
    
    CoordinatorAgent -->|before_agent_callback| InputValidation[Input Validation & Sanitization]
    CoordinatorAgent -.->|PIIMaskingPlugin| PIIFilter[PII Regex Masking]
    
    CoordinatorAgent -->|Transfer| HealthInfoAgent[Health Information Agent]
    CoordinatorAgent -->|Transfer| MythVerificationAgent[Myth Verification Agent]
    CoordinatorAgent -->|Transfer| PreventiveCareAgent[Preventive Care Agent]
    
    HealthInfoAgent -->|Tool Call| MCPServer[Local MCP Server]
    MythVerificationAgent -->|Tool Call| MCPServer
    PreventiveCareAgent -->|Tool Call| MCPServer
    
    MCPServer -->|retrieve_disease_info| DiseaseDB[(Disease Database)]
    MCPServer -->|verify_health_myth| MythDB[(Myth Database)]
    MCPServer -->|get_vaccination_schedule| VaccineDB[(Vaccine Schedule)]
    MCPServer -->|get_preventive_guidelines| GuidelinesDB[(Guidelines)]
```

<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/03f0142e-6367-4653-95ab-f810aee8ccf2" />



### Agents Role Definitions
1.  **Health Coordinator Agent**: Receives user inputs, runs security checks, routes control to the appropriate sub-agent, and appends clinical disclaimers.
2.  **Health Information Agent**: Explains symptoms, causes, and when to seek medical help. Binds to `retrieve_disease_info`.
3.  **Myth Verification Agent**: Compares claims against clinical databases and details scientific consensus. Binds to `verify_health_myth`.
4.  **Preventive Care Agent**: Provides child and adult vaccination schedules and healthy living guidelines. Binds to `get_vaccination_schedule` and `get_preventive_guidelines`.

---

## 🛡️ Security & Privacy Compliance

*   **Prompt & Script Sanitization**: The `before_agent_callback` runs validation checks rejecting basic script tags (`<script>`), source loaders (`onload`, `onerror`), and prompt bypass keywords.
*   **Automated PII Redaction**: The `PIIMaskingPlugin` intercepts LLM payloads and event streams. Any email addresses, phone numbers, or SSNs are instantly replaced with `[EMAIL_MASKED]`, `[PHONE_MASKED]`, and `[SSN_MASKED]`.
*   **Ephemeral Data Retention**: Configured with `InMemorySessionService` to ensure that conversation histories are kept only in RAM.
*   **Reset Button**: Clears the current session and wipes in-memory data.

---

