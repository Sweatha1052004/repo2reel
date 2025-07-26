# Repo2Reel - GitHub Repository to Video Generator

## Overview

Repo2Reel is a Flask-based web application that transforms GitHub repositories into AI-generated video overviews. The application analyzes repository content, generates scripts using LLM services, creates visual content, and produces final videos with optional audio narration.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: HTML templates with Bootstrap 5 dark theme
- **Styling**: Custom CSS with gradient backgrounds and card-based layout
- **JavaScript**: Vanilla JS for form validation, real-time URL validation, and UI enhancements
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

### Backend Architecture
- **Framework**: Flask with ProxyFix middleware for reverse proxy support
- **Session Management**: Flask sessions with configurable secret key
- **File Handling**: Temporary file management with automatic cleanup
- **Error Handling**: Comprehensive logging and graceful error recovery
- **Processing Pipeline**: Modular design with separate processors for each stage

## Key Components

### Core Processing Modules

1. **GraphRAGProcessor** (`graph_rag.py`)
   - Analyzes GitHub repositories using gitingest
   - Downloads and processes repository content
   - Extracts structured information about technologies, features, and codebase

2. **LLMProcessor** (`llm_utils.py`)
   - Handles text generation using multiple LLM providers
   - Supports Groq, OpenAI, Anthropic, Together, and HuggingFace APIs
   - Fallback system with priority ordering (Groq preferred for free/fast generation)

3. **PromptGenerator** (`prompt_generator.py`)
   - Creates optimized prompts for video script generation
   - Structures prompts with timing sections and content requirements
   - Formats repository analysis data for LLM consumption

4. **VideoGenerator** (`generate_video.py`)
   - Creates video content using CPU-optimized processing
   - Generates visual scenes based on script and repository analysis
   - Uses PIL for image generation and ffmpeg for video compilation

5. **AudioGenerator** (`generate_audio.py`)
   - Converts text to speech using platform-specific TTS engines
   - Supports Windows SAPI, macOS say, Linux espeak/festival
   - CPU-optimized audio generation

6. **AudioVideoMerger** (`merge_av.py`)
   - Combines audio and video using ffmpeg
   - Includes fallback mechanisms for failed merges
   - Validates output file integrity

### Web Application Structure

- **Main Application** (`app.py`): Flask app with route handlers and status management
- **Entry Point** (`main.py`): Application startup with debug configuration
- **Static Assets**: CSS styling and JavaScript for frontend functionality
- **Templates**: HTML templates for index, processing status, and results pages

## Data Flow

1. **User Input**: GitHub repository URL submitted through web form
2. **Repository Analysis**: GraphRAGProcessor downloads and analyzes repository content
3. **Script Generation**: LLMProcessor creates video script using repository analysis
4. **Content Creation**: 
   - VideoGenerator creates visual content
   - AudioGenerator creates narration (optional)
5. **Final Assembly**: AudioVideoMerger combines audio and video
6. **Delivery**: User downloads final MP4 file

## External Dependencies

### Required Services
- **LLM Providers**: Groq (preferred), OpenAI, Anthropic, Together, HuggingFace
- **System Dependencies**: ffmpeg for video processing, platform-specific TTS engines

### Optional Integrations
- **GitHub API**: For enhanced repository metadata (not currently implemented)
- **Cloud Storage**: For persistent file storage (currently uses temporary files)

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `OPENAI_API_KEY`: OpenAI API access
- `GROQ_API_KEY`: Groq API access (preferred)
- `ANTHROPIC_API_KEY`: Anthropic API access
- `TOGETHER_API_KEY`: Together API access
- `HUGGINGFACE_API_KEY`: HuggingFace API access

## Deployment Strategy

### Current Configuration
- **Local Development**: Flask development server on port 5000
- **Production Ready**: ProxyFix middleware for reverse proxy deployment
- **File Management**: Automatic cleanup of temporary files older than 1-24 hours
- **Session Handling**: Unique session IDs for concurrent processing

### Scalability Considerations
- CPU-optimized processing for cost-effective deployment
- Modular design allows for easy service separation
- Temporary file cleanup prevents storage bloat
- Multiple LLM provider support for reliability and cost optimization

### Security Features
- Input validation for GitHub URLs
- Secure session management
- Environment-based configuration
- Graceful error handling without information disclosure