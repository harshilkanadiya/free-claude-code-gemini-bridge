# free-claude-code-gemini-bridge 🚀

A high-performance, local proxy bridge designed to run the Anthropic **Claude Code CLI** entirely for free using Google's **Gemini 3.1 Flash-Lite** (1M token context window).

This project is an industrial-grade evolution of the [original proof-of-concept](https://github.com/Alishahryar1/free-claude-code). While the initial inspiration laid the groundwork, this version re-architects the proxy layer to solve the stability, tool-calling, and reliability issues that plagued the original approach.

---

## ✨ Why This Upgrade?
The original prototype was a great starting point, but it struggled with the complexities of the Claude CLI's internal behavior. We’ve rebuilt this from the ground up to offer:

*   **Robust Dual-Model Routing:** The Claude CLI dynamically switches between "Big Brain" models (Opus/Sonnet) for reasoning and "Worker Bee" models (Haiku) for file reading. Our implementation leverages `LiteLLM` to map these requests dynamically, preventing the crashes common in simpler scripts.
*   **The Tool-Calling "Goldilocks" Fix:** Modern proxies often drop parameters during translation, causing the CLI to fail when executing `bash` or file operations. We have identified and pinned the exact LiteLLM version (`1.81.14`) that guarantees 100% compatibility, ensuring Gemini executes local tools with total accuracy.
*   **Traffic Resilience:** Free preview models are prone to capacity limits (503 errors). Our proxy architecture utilizes LiteLLM's automatic retry logic to absorb these bounces, keeping your terminal session alive and active.
*   **Production-Grade Security:** We’ve eliminated the need to hard-code API keys. All credentials are handled via secure `config.yaml` templates, enforced by `.gitignore` protections, with legacy code archived to keep your repository clean.

## ⚖️ Why Not Just Use OpenRouter?
While services like OpenRouter are convenient, they often act as a third-party aggregator that can limit your throughput or gate the most powerful models behind paid plans. By connecting directly to the Google AI Studio Free Tier via this bridge, you unlock:

| Feature | OpenRouter (Free Tier) | Our Bridge (Direct Google API) |
| :--- | :--- | :--- |
| **Daily Requests** | Limited/Throttled | **1,500 Requests/Day** |
| **Context Window** | Restricted on free models | **1,000,000+ Tokens** |
| **Dependency** | Third-party aggregator | Direct Source Access |
| **Model Quality** | Varies / Often older | Gemini 3.1 Flash-Lite (Latest) |

By bypassing aggregators, you get direct, high-capacity access to the model, ensuring your Claude Code CLI sessions aren't interrupted by arbitrary third-party rate limits.

---

## 🚀 Setup Instructions

### 1. Environment Preparation
Clone the repository and initialize your virtual environment:

```bash
# Clone and enter the directory
git clone https://github.com/harshilkanadiya/free-claude-code-gemini-bridge
cd free-claude-code-gemini-bridge

# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Dependencies
**Important:** You must use the specific version provided to avoid translation bugs between Claude and Gemini tool calls. Do not upgrade these packages.

```bash
pip install -r requirements.txt
```

### 3. Configuration
Copy the template and insert your free **Google AI Studio API Key**:

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your own API key
```

---

## 💻 Usage

This bridge requires two active terminal sessions to function:

### Terminal 1: The Proxy Engine
Launch the bridge to start intercepting and translating requests:

```bash
litellm --config config.yaml --port 8000
```

### Terminal 2: The Claude CLI
Export the necessary environment variables to point the CLI to your local bridge, then launch the agent:

```bash
# Point to your local proxy
export ANTHROPIC_BASE_URL="http://127.0.0.1:8000"
export ANTHROPIC_API_KEY="sk-any-key"

# Disable beta features that may interfere with the bridge
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1

# Run the CLI
claude
```

---

## 📂 Project Structure
*   `config.yaml`: Your central configuration for routing Anthropic models to Gemini.
*   `requirements.txt`: Pinned environment dependencies required for tool-calling stability.
*   `legacy/`: Archived scripts from the initial prototype phase (retained for reference).
*   `venv/`: Your local environment (ignored by Git).

---

## 📝 Acknowledgements
Special thanks to [Alishahryar1](https://github.com/Alishahryar1/free-claude-code) for the initial concept. This project was built by iterating on their work to solve the architectural bottlenecks required for a stable, long-running terminal agent.
