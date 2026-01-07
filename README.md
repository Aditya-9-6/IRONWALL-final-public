# 🛡️ IronWall Community Edition (v2.0)

> **"The Firewall That Refuses to Die."**

IronWall is a next-generation security platform combining a zero-dependency Web Application Firewall (WAF) with a high-fidelity "IronEye" biometric authentication system. It is designed to demonstrate advanced security concepts like **Quantum Key Exchange**, **Active Liveness Detection**, and **Active Deception**.

---

## 👁️ IronEye Biometrics (New in v2.0)
The new **IronEye** module brings military-grade authentication to your browser:
*   **Active Liveness Detection**: Uses `face-api.js` (TensorFlow.js) to challenge users (e.g., "Blink", "Smile") before allowing login, preventing photo spoofs.
*   **Evidence Vault**: Captures and stores a snapshot of the user's proven identity into a secure backend vault (`./storage_vault/`) for audit trails.
*   **Zero-Trust Auth**: Full JWT implementation (`auth.py`) integrated directly into the proxy engine.

---

## 🚀 Core Features

### 🛡️ IronWall Proxy (WAF)
*   **🧠 Cortex AI**: A custom Machine Learning classifier (Naive Bayes) to detect payload anomalies without regex.
*   **👻 IronGhost**: Behavioral biometrics that differentiate humans from bots based on mouse/keystroke dynamics.
*   **🧬 IronMorph**: Polymorphic engine that randomly rewrites HTML element IDs/Names on every request to break bot scripts.
*   **💣 The Minefield**: Injects invisible "Honeypot" fields. Any interaction bans the IP instantly.
*   **⚛️ Quantum Handshake**: Implements **Kyber-1024** simulation for post-quantum key exchange.

---

## 🛠️ Installation & Usage

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/Aditya-9-6/IRONWALL-public.git
    cd ironwall-private
    pip install -r requirements.txt
    ```

2.  **Run the System**:
    ```bash
    # Start the backend proxy engine
    python main.py
    ```

3.  **Access the Portal**:
    *   Open `http://localhost:8000` in your browser.
    *   You will see the **IronWall Portal**.
    *   Click **Login** to test the **IronEye** camera system.

---

## 🔒 Deployment

### ☁️ Deploy to Internet (Render.com)
1.  **Push to GitHub (Public)**:
    *   Create a Public repo named `IRONWALL-final-public`.
    *   Run `deploy_final.bat` locally.
    *   This pushes code to `https://github.com/Aditya-9-6/IRONWALL-final-public.git`.

2.  **Connect on Render**:
    *   Log in to [dashboard.render.com](https://dashboard.render.com).
    *   Click **New +** -> **Web Service**.
    *   Connect your `IRONWALL-final-public` repo.
    *   Click **Create Web Service**.

3.  **Secure It (Post-Deploy)**:
    *   Once deployed, go to GitHub Settings and make the repo **Private**.

### 📦 Repo Setup Script
Run `deploy_public.bat` to automate the git init and push process.

---

## ⚠️ Disclaimer
This is a **Security Research Demonstration**. While it implements real cryptographic and ML concepts, it is intended for educational use.
