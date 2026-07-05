// State variables
let sessionId = "";
let isThinking = false;
let activeAgent = null;
let currentMessageElement = null;
let currentMessageText = "";

// DOM Elements
const chatHistory = document.getElementById("chat-history");
const chatForm = document.getElementById("chat-form");
const queryInput = document.getElementById("query-input");
const btnSubmit = document.getElementById("btn-submit");
const sessionIdDisplay = document.getElementById("session-id-display");
const reasoningTimeline = document.getElementById("reasoning-timeline");
const reasoningPulse = document.getElementById("reasoning-pulse");

// Helper: Generate clean Session ID
function generateSessionId() {
    return "session_" + Math.random().toString(36).substring(2, 12);
}

// Initialize session
sessionId = generateSessionId();
sessionIdDisplay.textContent = sessionId;

// Function to set predefined queries and auto-submit
function setQuery(text) {
    queryInput.value = text;
    queryInput.focus();
}

// Function to clear session data
async function clearSession() {
    try {
        const response = await fetch(`/api/session/clear?session_id=${sessionId}`);
        const result = await response.json();
        
        // Reset local variables
        sessionId = generateSessionId();
        sessionIdDisplay.textContent = sessionId;
        
        // Clear chat
        chatHistory.innerHTML = `
            <div class="chat-message system">
                <div class="message-content">
                    <p>Session data cleared. New session started: <b>${sessionId}</b></p>
                </div>
            </div>
        `;
        
        // Reset timeline if it exists
        if (reasoningTimeline) {
            reasoningTimeline.innerHTML = '<div class="timeline-empty">Awaiting query...</div>';
        }
        
        // Reset agent nodes
        resetAgentNodes();
        
        showPopupAlert("Session Reset", "In-memory session state cleared successfully.", "🔒");
    } catch (e) {
        console.error("Error clearing session", e);
    }
}

// Reset pipeline nodes
function resetAgentNodes() {
    document.querySelectorAll(".pipeline-node").forEach(node => {
        node.classList.remove("active");
    });
    activeAgent = null;
    currentMessageElement = null;
    currentMessageText = "";
}

// Highlight pipeline node
function highlightAgent(agentName) {
    document.querySelectorAll(".pipeline-node").forEach(node => {
        node.classList.remove("active");
    });
    
    const nodeMap = {
        "health_coordinator_agent": "node-health_coordinator_agent",
        "health_info_agent": "node-health_info_agent",
        "myth_verification_agent": "node-myth_verification_agent",
        "preventive_care_agent": "node-preventive_care_agent",
        "community_health_analytics_agent": "node-community_health_analytics_agent"
    };
    
    const elementId = nodeMap[agentName];
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add("active");
        }
    }
    activeAgent = agentName;
}

// Visual Alerts
function showPopupAlert(title, message, icon = "🔒") {
    const alertBox = document.getElementById("safety-alert");
    const alertMessage = document.getElementById("alert-message");
    const alertTitle = alertBox.querySelector("h3");
    const alertIcon = alertBox.querySelector(".alert-icon");
    
    alertTitle.textContent = title;
    alertMessage.textContent = message;
    alertIcon.textContent = icon;
    
    alertBox.style.display = "block";
    
    // Auto close after 5 seconds
    setTimeout(closeAlert, 5000);
}

// Close alert box
function closeAlert() {
    document.getElementById("safety-alert").style.display = "none";
}

// Add timeline step (safe wrapper in case panel is hidden/removed)
function addTimelineStep(type, title, description, codeData = null) {
    console.log(`[Trace] [${type}] ${title} - ${description}`);
    if (!reasoningTimeline) return;
    
    const emptyMsg = reasoningTimeline.querySelector(".timeline-empty");
    if (emptyMsg) emptyMsg.remove();
    
    const step = document.createElement("div");
    step.className = `timeline-step ${type}`;
    
    let html = `<h4>${title}</h4><p>${description}</p>`;
    if (codeData) {
        html += `<div class="code-box">${codeData}</div>`;
    }
    
    step.innerHTML = html;
    reasoningTimeline.appendChild(step);
    reasoningTimeline.scrollTop = reasoningTimeline.scrollHeight;
}

// Scan text for PII Masking markers
function scanForPIIMasking(text, context) {
    if (!text || typeof text !== "string") return;
    
    let emailFound = text.includes("[EMAIL_MASKED]");
    let phoneFound = text.includes("[PHONE_MASKED]");
    let ssnFound = text.includes("[SSN_MASKED]");
    
    if (emailFound || phoneFound || ssnFound) {
        let items = [];
        if (emailFound) items.push("Email");
        if (phoneFound) items.push("Phone");
        if (ssnFound) items.push("SSN");
        
        addTimelineStep(
            "safety-alert",
            "Security Log: PII Masked",
            `Interceptors redacted sensitive information (${items.join(", ")}) in ${context}.`
        );
        
        showPopupAlert(
            "PII Masked Successfully",
            `Your personal ${items.join("/")} was masked in transit.`,
            "🔒"
        );
    }
}

// Format markdown-like text to clean HTML
function formatMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>')
        .replace(/- (.*?)(<br>|$)/g, '• $1$2');
}

// Initialize a new assistant message container for real-time streaming
function startAssistantMessage(author) {
    currentMessageText = "";
    
    let authorClass = "coordinator";
    let displayName = "Health Coordinator";
    
    if (author === "health_info_agent") {
        authorClass = "subagent-info";
        displayName = "Health Info Specialist";
    } else if (author === "myth_verification_agent") {
        authorClass = "subagent-myth";
        displayName = "Myth Analyst";
    } else if (author === "preventive_care_agent") {
        authorClass = "subagent-preventive";
        displayName = "Preventive Care Specialist";
    } else if (author === "community_health_analytics_agent") {
        authorClass = "subagent-analytics";
        displayName = "Health Analyst";
    }
    
    const message = document.createElement("div");
    message.className = `chat-message ${authorClass}`;
    message.innerHTML = `
        <div class="message-content">
            <span class="agent-label">${displayName}</span>
            <p class="message-text"></p>
        </div>
    `;
    
    chatHistory.appendChild(message);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    currentMessageElement = message.querySelector(".message-text");
}

// Update the current assistant message box in real-time
function updateAssistantMessage(text) {
    if (currentMessageElement) {
        currentMessageText += text;
        currentMessageElement.innerHTML = formatMarkdown(currentMessageText);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

// Append complete chat message
function appendChatMessage(author, text) {
    const message = document.createElement("div");
    
    let authorClass = "coordinator";
    let displayName = "Health Coordinator";
    
    if (author === "user") {
        authorClass = "user";
        displayName = "You";
    } else if (author === "health_info_agent") {
        authorClass = "subagent-info";
        displayName = "Health Info Specialist";
    } else if (author === "myth_verification_agent") {
        authorClass = "subagent-myth";
        displayName = "Myth Analyst";
    } else if (author === "preventive_care_agent") {
        authorClass = "subagent-preventive";
        displayName = "Preventive Care Specialist";
    } else if (author === "community_health_analytics_agent") {
        authorClass = "subagent-analytics";
        displayName = "Health Analyst";
    }
    
    message.className = `chat-message ${authorClass}`;
    message.innerHTML = `
        <div class="message-content">
            <span class="agent-label">${displayName}</span>
            <p>${formatMarkdown(text)}</p>
        </div>
    `;
    
    chatHistory.appendChild(message);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Form Submission & Event Streaming
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    
    const query = queryInput.value.trim();
    if (!query || isThinking) return;
    
    // Set UI to thinking state
    isThinking = true;
    btnSubmit.disabled = true;
    btnSubmit.textContent = "...";
    queryInput.disabled = true;
    if (reasoningPulse) reasoningPulse.className = "pulse-indicator thinking";
    
    // Clear nodes and timeline
    resetAgentNodes();
    if (reasoningTimeline) reasoningTimeline.innerHTML = "";
    
    // 1. Add User query to chat
    appendChatMessage("user", query);
    queryInput.value = "";
    
    // 2. Add validation trace
    addTimelineStep(
        "validation",
        "Input Validation",
        "Sanitizing query and scanning for injection/scripting patterns..."
    );
    
    // Build event stream URL
    const url = `/api/chat?query=${encodeURIComponent(query)}&session_id=${sessionId}`;
    const eventSource = new EventSource(url);
    
    let lastAgent = null;
    let accumulatedContent = "";
    
    // Listen for agent events
    eventSource.addEventListener("agent_event", (event) => {
        const data = JSON.parse(event.data);
        const author = data.author;
        const content = data.content;
        const output = data.output;
        const actions = data.actions;
        
        // Detect transitions and highlight nodes
        if (author && author !== "user" && author !== lastAgent) {
            lastAgent = author;
            highlightAgent(author);
            
            addTimelineStep(
                "routing",
                `Agent Transition: ${author}`,
                `Control transferred to agent ${author}.`
            );
            
            // Start a new streaming message container
            startAssistantMessage(author);
        }
        
        // Scan user input for PII if it's returning the user message event
        if (author === "user" && content && content.parts) {
            const userText = content.parts.map(p => p.text).join(" ");
            scanForPIIMasking(userText, "user query");
            
            // Detect if blocked by security callback
            if (userText.includes("SYSTEM EXPLICIT SECURITY ALERT")) {
                addTimelineStep(
                    "safety-alert",
                    "Security Trigger: Input Blocked",
                    "Input validation callback flagged the message as dangerous. Terminating execution."
                );
            }
        }
        
        // Detect Tool Calls
        if (content && content.parts) {
            content.parts.forEach(part => {
                if (part.function_call) {
                    const call = part.function_call;
                    addTimelineStep(
                        "tool-call",
                        `Tool Invocation: ${call.name}`,
                        `Agent is calling tool ${call.name} with parameters:`,
                        JSON.stringify(call.args, null, 2)
                    );
                    
                    scanForPIIMasking(JSON.stringify(call.args), "tool arguments");
                }
            });
        }
        
        // Detect Tool Outputs
        if (output && typeof output === "object") {
            const outputStr = JSON.stringify(output);
            addTimelineStep(
                "tool-response",
                "Tool Output Returned",
                "Tool execution finished successfully. Returned data:",
                outputStr
            );
            
            scanForPIIMasking(outputStr, "tool response data");
        }
        
        // Check for text parts representing responses and stream them (only if NOT user event)
        if (author !== "user" && content && content.parts) {
            content.parts.forEach(part => {
                if (part.text) {
                    accumulatedContent += part.text;
                    updateAssistantMessage(part.text);
                    scanForPIIMasking(part.text, "model response text");
                }
            });
        }
    });
    
    // Handle Stream Completion
    eventSource.onerror = (err) => {
        eventSource.close();
        
        // Clean up UI state
        isThinking = false;
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Send";
        queryInput.disabled = false;
        if (reasoningPulse) reasoningPulse.className = "pulse-indicator";
        
        // If no content was generated
        if (!accumulatedContent) {
            addTimelineStep(
                "safety-alert",
                "Execution Error",
                "Failed to stream response from the agent. Please check your API Key and backend console logs."
            );
            appendChatMessage("health_coordinator_agent", "Sorry, I encountered an issue connecting to the AI model. Please verify your environment configurations.");
        } else {
            // Coordinator wraps up
            highlightAgent("health_coordinator_agent");
            addTimelineStep(
                "final",
                "Response Complete",
                "Agent execution finished successfully."
            );
            loadAnalyticsDashboard();
        }
    };
});

// Global Chart instance reference
let analyticsChart = null;

// Function to fetch metrics and load/render the Chart.js visual trend data
async function loadAnalyticsDashboard() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        
        if (data.error) {
            console.error("Error loading analytics:", data.error);
            return;
        }
        
        // Update KPI values
        document.getElementById("kpi-total-cases").textContent = data.total_cases;
        document.getElementById("kpi-highest-region").textContent = data.highest_risk_region;
        document.getElementById("kpi-avg-vac").textContent = (data.average_vaccination_rate * 100).toFixed(1) + "%";
        
        const riskLevelEl = document.getElementById("kpi-risk-level");
        riskLevelEl.textContent = data.risk_level;
        riskLevelEl.className = "kpi-value"; // reset
        if (data.risk_level.toLowerCase().includes("high")) {
            riskLevelEl.classList.add("risk-high");
        } else if (data.risk_level.toLowerCase().includes("medium")) {
            riskLevelEl.classList.add("risk-medium");
        } else {
            riskLevelEl.classList.add("risk-low");
        }
        
        // Update Recommendations list
        const recsList = document.getElementById("recs-list");
        recsList.innerHTML = "";
        data.recommendations.forEach(rec => {
            const li = document.createElement("li");
            li.textContent = rec;
            recsList.appendChild(li);
        });
        
        // Render Chart.js line chart
        const ctx = document.getElementById('analyticsChart').getContext('2d');
        if (analyticsChart) {
            analyticsChart.destroy();
        }
        
        // Assign distinct color palette matching existing HSL colors
        const colors = {
            "Dengue": "hsl(196, 95%, 50%)",      // Coordinator / Cyan
            "Influenza": "hsl(210, 95%, 55%)",   // Info / Blue
            "Diabetes": "hsl(282, 85%, 65%)",    // Myth / Purple
            "Heat Stroke": "hsl(355, 85%, 60%)"  // Danger / Red
        };
        
        const datasets = data.trend_data.datasets.map(ds => {
            const color = colors[ds.label] || "hsl(36, 100%, 55%)";
            return {
                label: ds.label,
                data: ds.data,
                borderColor: color,
                backgroundColor: color.replace(")", ", 0.15)"),
                borderWidth: 2,
                pointBackgroundColor: color,
                pointRadius: 4,
                tension: 0.3,
                fill: false
            };
        });
        
        analyticsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.trend_data.labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#f5f5f5',
                            font: { family: 'Outfit', size: 10 }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.08)' },
                        ticks: { color: '#b2b2b2', font: { family: 'Inter', size: 9 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.08)' },
                        ticks: { color: '#b2b2b2', font: { family: 'Inter', size: 9 } }
                    }
                }
            }
        });
        
    } catch (e) {
        console.error("Failed to load analytics dashboard data", e);
    }
}

// Initial load
document.addEventListener("DOMContentLoaded", () => {
    loadAnalyticsDashboard();
});
