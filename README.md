# 📝 Meeting Summarizer

A modern, full-stack Python application that automatically transcribes audio and video meeting recordings, generates structured AI summaries, extracts key decisions and action items with deadlines, and stores meeting records in a PostgreSQL database.

Built with **Streamlit**, **OpenAI (Whisper & GPT-4o-mini)**, **MoviePy**, and **PostgreSQL**.

---

## ✨ Features

- 🎙️ **Audio & Video Support**: Upload audio files (`.mp3`, `.wav`, `.m4a`) or video recordings (`.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`).
- 🎬 **Automated Audio Extraction**: Automatically extracts audio tracks from video files prior to transcription using MoviePy and FFmpeg.
- ⚡ **AI Transcription**: High-accuracy speech-to-text using OpenAI's hosted Whisper API (`whisper-1`).
- 🧠 **Structured AI Summarization**: Uses OpenAI's `gpt-4o-mini` with JSON mode to extract:
  - **Overview**: Concise 3–5 sentence executive summary.
  - **Key Decisions**: Clear bulleted list of decisions agreed upon during the meeting.
  - **Action Items**: Structured task items complete with assigned owner and deadline.
- 📑 **Smart Text Chunking**: Automatically breaks long transcripts into manageable chunks for processing and intelligently merges results without duplicates.
- 🗄️ **PostgreSQL Persistence**: Saves transcriptions, summaries, decisions, and action items with timestamps into a PostgreSQL database with search capability (`ILIKE`).
- 💻 **Streamlit UI**: Intuitive web dashboard with processing feedback, expandable full transcripts, and formatted action item lists.

---

## 🏗️ Project Architecture

```
Meeting-Summarizer/
├── src/
│   └── meeting_summarizer/
│       ├── __init__.py        # Package initialization
│       ├── app.py             # Streamlit web user interface & workflow controller
│       ├── config.py          # Environment configuration loader & validator
│       ├── database.py        # PostgreSQL schema initialization & query helpers
│       ├── summarizer.py      # OpenAI GPT-4o-mini structured JSON summarizer & chunk merger
│       ├── transcriber.py     # Whisper API wrapper & audio size validator
│       └── utils.py           # Video-to-audio converter, text chunker & cleanup helpers
├── main.py                    # Top-level entrypoint script
├── pyproject.toml             # Project metadata & hatchling build configuration
├── requirements.txt           # Exported dependency lockfile
├── render-build.sh            # Custom build script for deployment (installs FFmpeg)
├── packages.txt               # System package dependencies for deployment
└── README.md                  # Project documentation
```

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed and configured:

1. **Python 3.13+**
2. **FFmpeg**: Required by `moviepy` for audio extraction from video files.
   - **Ubuntu/Debian**: `sudo apt-get update && sudo apt-get install -y ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Install via `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/).
3. **OpenAI API Key**: An active API key with access to `whisper-1` and `gpt-4o-mini`.
4. **PostgreSQL Database**: A running PostgreSQL instance (local or hosted on Supabase, Neon, Render, etc.).

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory of the project based on the required environment variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/meeting_db
```

### Configuration Parameters (`src/meeting_summarizer/config.py`)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | OpenAI API authentication key | *Required* |
| `DATABASE_URL` | PostgreSQL connection string | *Required* |
| `WHISPER_MODEL` | Whisper transcription model | `whisper-1` |
| `SUMMARY_MODEL` | LLM model for summarization | `gpt-4o-mini` |
| `MAX_AUDIO_FILE_SIZE_MB` | Maximum allowed audio size for Whisper API | `25` MB |
| `CHUNK_MAX_CHARS` | Character threshold for splitting long transcripts | `8000` chars |

---

## 🚀 Quick Start

### Option 1: Using `uv` (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shreeragkh/Meeting-Summarizer.git
   cd Meeting-Summarizer
   ```

2. **Create a virtual environment & sync dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run main.py
   ```

---

### Option 2: Using standard `pip`

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shreeragkh/Meeting-Summarizer.git
   cd Meeting-Summarizer
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   streamlit run main.py
   ```

Once started, open your browser and navigate to `http://localhost:8501`.

---

## 🗄️ Database Schema

The application automatically creates the `meetings` table in PostgreSQL on application launch if it does not exist:

```sql
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    transcript TEXT,
    summary TEXT,
    decisions JSONB,
    action_items JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🌐 Deployment Guide (e.g. Render)

To deploy on platforms like [Render](https://render.com/):

1. **System Packages**: `packages.txt` lists `ffmpeg`, ensuring the OS-level binary is installed in the container environment.
2. **Build Command**: Set the build command to use `render-build.sh`:
   ```bash
   chmod +x render-build.sh && ./render-build.sh
   ```
3. **Start Command**:
   ```bash
   streamlit run main.py --server.port $PORT --server.address 0.0.0.0
   ```
4. **Environment Variables**: Add `OPENAI_API_KEY` and `DATABASE_URL` in the hosting dashboard settings.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///home/shreerag/Desktop/shreeragkh/Meeting-Summarizer/LICENSE) file for details.
