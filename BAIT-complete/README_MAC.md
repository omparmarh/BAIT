# BAIT macOS Setup & Usage Guide

Welcome to the macOS version of BAIT! This version has been specifically optimized for Apple Silicon (M1/M2/M3) and Intel Macs.

## 🚀 One-Click Setup

1.  **Open Terminal**.
2.  Navigate to the project folder:
    ```bash
    cd "/Users/macbookair/Downloads/BAIT-complete (1) - Copy/BAIT-complete"
    ```
3.  Run the installation script:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    *This will install Homebrew, PortAudio, Python 3.11, Node.js, and all project dependencies.*

## 🎬 How to Run

Simply double-click the **`start_bait.command`** file in the project root.

Alternatively, run it from Terminal:
```bash
./start_bait.command
```

## 🛠 macOS Permissions (CRITICAL)

macOS has strict security. You must grant permissions for:
1.  **Microphone**: For voice commands (STT).
2.  **Screen Recording**: For taking screenshots.
3.  **Accessibility**: For controlling other apps.

When you first use these features, macOS will show a popup. Click **"Open System Settings"** and ensure **Terminal** (or your IDE) is toggled **ON**.

## 🎤 Key Features on Mac

- **Hyper-Human TTS**: Uses native `afplay` for lightning-fast speech.
- **System Control**: Say "Open Safari" or "Open Chrome" to launch apps.
- **Screenshot**: Say "Take a screenshot" to save a capture to your Desktop.
- **Video Chat**: Full WebRTC support for camera and mic.

## 📦 Desktop App (Electron)

To run as a dedicated desktop window:
```bash
npm run electron
```

To build a .dmg or .app bundle:
```bash
npm run dist
```

---
*Created for BAIT Conversion Project 2026*
