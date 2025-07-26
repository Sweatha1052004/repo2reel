# Repo2Reel - GitHub Repository to Video Generator

A Flask-based web application that transforms GitHub repositories into AI-generated video overviews with professional visuals, enhanced typography, and structured layouts.

## Features

- **Repository Analysis**: Analyzes GitHub repositories using gitingest for comprehensive content extraction
- **AI Script Generation**: Creates video scripts using multiple LLM providers (Groq, OpenAI, Anthropic, Together, HuggingFace)
- **Professional Video Generation**: 
  - Enhanced DejaVu fonts with multiple weights and sizes
  - Multi-layer text shadows for better contrast
  - Professional table layouts with numbered rows
  - Technology flowcharts with layered architecture
  - IDE-style code editor with syntax highlighting
  - Structured content boxes with backgrounds and borders
- **Audio Narration**: Text-to-speech using Edge TTS
- **Background Processing**: Real-time progress tracking with session management

## System Requirements

- Python 3.11+
- ffmpeg (for video processing)
- System fonts (DejaVu family recommended)

## Installation

1. Install Python dependencies:
```bash
pip install flask flask-sqlalchemy gunicorn pillow requests edge-tts psycopg2-binary werkzeug email-validator
```

2. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg fonts-dejavu

# macOS
brew install ffmpeg
```

3. Set environment variables:
```bash
export SESSION_SECRET="your-secret-key"
export GROQ_API_KEY="your-groq-key"  # Optional but recommended
export OPENAI_API_KEY="your-openai-key"  # Optional
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Open http://localhost:5000 in your browser

3. Enter a GitHub repository URL (e.g., https://github.com/user/repo)

4. Wait for processing to complete and download your video

## Project Structure

```
repo2reel/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── generate_video.py     # Enhanced video generation with professional visuals
├── generate_audio.py     # Audio synthesis using Edge TTS
├── merge_av.py          # Audio-video merging with ffmpeg
├── graph_rag.py         # Repository analysis and content extraction
├── llm_utils.py         # LLM integration for script generation
├── prompt_generator.py   # Optimized prompts for video scripts
├── static/              # Frontend assets
│   ├── script.js        # JavaScript for form validation and UI
│   └── style.css        # Custom styling with dark theme
├── templates/           # HTML templates
│   ├── index.html       # Main form page
│   ├── processing.html  # Progress tracking page
│   └── result.html      # Download page
└── README.md           # This file
```

## Video Enhancement Features

### Typography
- **Professional Fonts**: DejaVu Sans family with Bold, Regular, and Mono variants
- **Enhanced Readability**: Multi-layer text shadows and improved contrast
- **Proper Sizing**: Larger fonts (84px titles, 42px subtitles, 32px content)

### Visual Elements
- **Feature Tables**: Structured layouts with alternating row colors and numbered circles
- **Technology Flowcharts**: Layered architecture showing Frontend/Backend/Database/DevOps
- **Code Editor**: IDE-style display with syntax highlighting and line numbers
- **Content Boxes**: Professional backgrounds with borders and proper spacing

### Scene Types
1. **Title Scene**: Repository name with enhanced badges and technology display
2. **Features Scene**: Professional table layout with numbered features
3. **Technology Scene**: Flowchart with categorized tech stack
4. **Code Scene**: IDE-style editor with syntax highlighting
5. **Content Scene**: Structured text boxes with bullet points
6. **Conclusion Scene**: Thank you message with call-to-action

## Configuration

### LLM Providers
The application supports multiple LLM providers with automatic fallback:
1. Groq (preferred for speed and free tier)
2. OpenAI
3. Anthropic
4. Together AI
5. HuggingFace
6. Local template-based generation (fallback)

### Video Settings
- Resolution: 1920x1080 (Full HD)
- Frame Rate: 25 FPS (optimized for CPU)
- Duration: Based on script length (30 seconds to 5 minutes)
- Audio: High-quality TTS with automatic duration matching

## API Keys

Set these environment variables for enhanced functionality:
- `GROQ_API_KEY`: Fast, free LLM processing
- `OPENAI_API_KEY`: High-quality script generation
- `ANTHROPIC_API_KEY`: Alternative LLM provider
- `TOGETHER_API_KEY`: Open-source models
- `HUGGINGFACE_API_KEY`: Transformer models

## Troubleshooting

### Common Issues
1. **"Could not generate video"**: Ensure ffmpeg is properly installed
2. **Poor audio quality**: Install Edge TTS: `pip install edge-tts`
3. **Font issues**: Install DejaVu fonts on your system
4. **Slow processing**: Add API keys for faster LLM processing

### Performance Tips
- Use SSD storage for temporary files
- Ensure adequate RAM (4GB+ recommended)
- Close other applications during video generation
- Use Groq API key for fastest script generation

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Support

For issues or questions, please check the troubleshooting section or create an issue in the repository.