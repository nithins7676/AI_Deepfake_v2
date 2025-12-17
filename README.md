# 🕵️‍♂️ AI Deepfake Detector (v2)

A robust, full-stack application for detecting deepfakes in images and videos. It utilizes a **Vision Transformer (ViT-B/16)** model combined with **Sightengine** ensemble detection and **SerpAPI** reverse search to provide high-accuracy forensic analysis.

## ✨ Key Features

-   **Image Detection**:
    -   **Hybrid Ensemble**: Combines local ViT model predictions with Sightengine API (GenAI detection).
    -   **Classification**: Distinguishes between **Real**, **Deepfake**, and **AI-Generated**.
    -   **Explainability**: Generates **Grad-CAM** heatmaps to highlight manipulated regions.
-   **Video Analysis**:
    -   Smart frame extraction and analysis using Sightengine's advanced video GenAI models.
    -   Frame-by-frame deepfake probability breakdown.
-   **Reverse Image Search**:
    -   Integrated **SerpAPI (Google)** and **RapidAPI** to find original sources of images.
    -   Helps verify context and authenticity.
-   **Modern UI**:
    -   Built with **Next.js 16**, **Tailwind CSS**, and **Shadcn UI**.
    -   Futuristic, responsive design with dark mode.

## 🏗️ Architecture

-   **Backend**: Python (Flask)
    -   Handles model inference (PyTorch).
    -   Manages API integrations (Sightengine, SerpAPI).
    -   Serves Grad-CAM heatmaps.
-   **Frontend**: TypeScript (Next.js 16)
    -   Provides the user interface.
    -   Handles file uploads and displays results.
    -   Visualizes confidence scores and heatmaps.

## 🚀 Getting Started

### Prerequisites
-   **Python 3.10+**
-   **Node.js 18+** & **npm/pnpm**
-   **GPU (Optional)**: Recommended for faster local inference (CUDA).

### 1. Backend Setup (Flask)

1.  **Navigate to the root directory**:
    ```bash
    cd "Deepfake/New folder"
    ```
2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Download Model Weights**:
    -   Place your trained `vit3class.pth` file in the root directory.
4.  **Environment Variables**:
    -   Create a `.env` file in the root directory:
        ```env
        # Sightengine (Deepfake/GenAI Detection)
        SIGHTENGINE_API_USER=your_user
        SIGHTENGINE_API_SECRET=your_secret

        # SerpAPI (Reverse Search - Optional)
        SERPAPI_API_KEY=your_serpapi_key
        
        # Supabase (Auth - Optional)
        SUPABASE_URL=your_supabase_url
        SUPABASE_ANON_KEY=your_supabase_key
        ```
5.  **Run the Backend**:
    ```bash
    python app.py
    ```
    *Server runs on `http://localhost:5000`*

### 2. Frontend Setup (Next.js)

1.  **Navigate to the frontend directory**:
    ```bash
    cd FRONTEND
    ```
2.  **Install Dependencies**:
    ```bash
    npm install
    # or
    pnpm install
    ```
3.  **Run the Development Server**:
    ```bash
    npm run dev
    ```
    *Client runs on `http://localhost:3000`*

## 📖 Usage

1.  Open `http://localhost:3000` in your browser.
2.  **Login**: Use the designated login page (if auth is enabled).
3.  **Dashboard**:
    -   **Upload Image**: Select an image to virtually analyze its authenticity. View the prediction and the heatmap.
    -   **Upload Video**: detailed frame-by-frame analysis for video files.
    -   **Reverse Search**: Check if the image exists elsewhere on the web.

## 🛠️ Configuration

| File | Purpose |
| :--- | :--- |
| `app.py` | Main Flask backend entry point. |
| `video_processor.py` | Handles video frame extraction and aggregation. |
| `gradcam_vit.py` | Generates Grad-CAM heatmaps for ViT. |
| `FRONTEND/` | Next.js source code. |
| `requirements.txt` | Python dependencies. |

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/NewFeature`).
3.  Commit your changes (`git commit -m 'Add NewFeature'`).
4.  Push to the branch (`git push origin feature/NewFeature`).
5.  Open a Pull Request.

---
*Created by Nithin S*
