import os
import logging
import tempfile
import shutil
from flask import Flask, render_template, request, flash, redirect, url_for, send_file, session, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid
import threading
import time

# Import our custom modules
from generate_audio import generate_audio_from_text
from generate_video import generate_video_from_script
from graph_rag import GraphRAGProcessor
from llm_utils import LLMProcessor
from merge_av import merge_audio_video
from prompt_generator import PromptGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Global storage for processing status
processing_status = {}

def clean_old_files():
    """Clean up old temporary files"""
    try:
        temp_dir = tempfile.gettempdir()
        repo2reel_dir = os.path.join(temp_dir, 'repo2reel')
        if os.path.exists(repo2reel_dir):
            for item in os.listdir(repo2reel_dir):
                item_path = os.path.join(repo2reel_dir, item)
                if os.path.isdir(item_path):
                    # Remove directories older than 1 hour
                    if time.time() - os.path.getctime(item_path) > 3600:
                        shutil.rmtree(item_path)
                        logger.info(f"Cleaned up old directory: {item_path}")
                elif os.path.isfile(item_path):
                    # Remove files older than 24 hours
                    if time.time() - os.path.getctime(item_path) > 86400:
                        os.remove(item_path)
                        logger.info(f"Cleaned up old file: {item_path}")
    except Exception as e:
        logger.error(f"Error cleaning old files: {e}")

@app.route('/')
def index():
    """Main page with GitHub URL input"""
    clean_old_files()
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_repository():
    """Process the GitHub repository and generate video"""
    github_url = request.form.get('github_url', '').strip()
    
    if not github_url:
        flash('Please provide a GitHub repository URL', 'error')
        return redirect(url_for('index'))
    
    # Validate GitHub URL format
    if not (github_url.startswith('https://github.com/') or github_url.startswith('http://github.com/')):
        flash('Please provide a valid GitHub repository URL', 'error')
        return redirect(url_for('index'))
    
    # Basic URL validation
    try:
        parts = github_url.replace('https://github.com/', '').replace('http://github.com/', '').split('/')
        if len(parts) < 2 or not parts[0] or not parts[1]:
            flash('Please provide a valid GitHub repository URL with owner and repository name', 'error')
            return redirect(url_for('index'))
    except Exception:
        flash('Invalid GitHub repository URL format', 'error')
        return redirect(url_for('index'))
    
    # Generate unique session ID for this processing task
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    # Initialize processing status
    processing_status[session_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initializing repository processing...',
        'error': None,
        'result_file': None,
        'github_url': github_url
    }
    
    # Start processing in background thread
    thread = threading.Thread(target=process_repository_background, args=(github_url, session_id))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('processing', session_id=session_id))

def process_repository_background(github_url: str, session_id: str):
    """Background processing of the repository"""
    try:
        logger.info(f"Starting background processing for session {session_id}: {github_url}")
        
        # Update status - Repository Analysis
        processing_status[session_id].update({
            'status': 'analyzing',
            'progress': 10,
            'message': 'Downloading and analyzing repository content...'
        })
        
        # Initialize processors
        graph_rag = GraphRAGProcessor()
        llm_processor = LLMProcessor()
        prompt_gen = PromptGenerator()
        
        # Analyze repository using GraphRAG
        logger.info("Starting repository analysis")
        repo_analysis = graph_rag.analyze_repository(github_url)
        logger.info("Repository analysis completed")
        
        # Update status - Script Generation
        processing_status[session_id].update({
            'progress': 30,
            'message': 'Generating video script from repository analysis...'
        })
        
        # Generate video script using LLM
        logger.info("Generating video script")
        script_prompt = prompt_gen.generate_video_script_prompt(repo_analysis)
        video_script = llm_processor.generate_text(script_prompt, max_length=800)
        logger.info("Video script generated")
        
        # Update status - Audio Generation
        processing_status[session_id].update({
            'progress': 50,
            'message': 'Creating audio narration from script...'
        })
        
        # Generate audio from script
        logger.info("Generating audio")
        audio_file = generate_audio_from_text(video_script, session_id)
        logger.info(f"Audio generated: {audio_file}")
        
        # Update status - Video Generation
        processing_status[session_id].update({
            'progress': 70,
            'message': 'Generating video content and visuals...'
        })
        
        # Generate video
        logger.info("Generating video")
        video_file = generate_video_from_script(video_script, repo_analysis, session_id)
        logger.info(f"Video generated: {video_file}")
        
        # Update status - Merging
        processing_status[session_id].update({
            'progress': 90,
            'message': 'Merging audio and video components...'
        })
        
        # Merge audio and video
        logger.info("Merging audio and video")
        final_video = merge_audio_video(video_file, audio_file, session_id)
        logger.info(f"Final video created: {final_video}")
        
        # Complete
        processing_status[session_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Video generation completed successfully!',
            'result_file': final_video
        })
        
        logger.info(f"Processing completed successfully for session {session_id}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing repository for session {session_id}: {error_msg}")
        processing_status[session_id].update({
            'status': 'error',
            'error': error_msg,
            'message': f'Error: {error_msg}'
        })

@app.route('/processing/<session_id>')
def processing(session_id):
    """Show processing status page"""
    if session_id not in processing_status:
        flash('Invalid or expired session ID', 'error')
        return redirect(url_for('index'))
    
    status = processing_status[session_id]
    
    if status['status'] == 'completed':
        return redirect(url_for('result', session_id=session_id))
    
    return render_template('processing.html', status=status, session_id=session_id)

@app.route('/status/<session_id>')
def get_status(session_id):
    """API endpoint to get processing status"""
    if session_id not in processing_status:
        return jsonify({'error': 'Invalid session ID'}), 404
    
    status = processing_status[session_id]
    return jsonify(status)

@app.route('/result/<session_id>')
def result(session_id):
    """Show result page with download link"""
    if session_id not in processing_status:
        flash('Invalid or expired session ID', 'error')
        return redirect(url_for('index'))
    
    status = processing_status[session_id]
    
    if status['status'] != 'completed':
        return redirect(url_for('processing', session_id=session_id))
    
    return render_template('result.html', status=status, session_id=session_id)

@app.route('/download/<session_id>')
def download_video(session_id):
    """Download the generated video"""
    if session_id not in processing_status:
        flash('Invalid or expired session ID', 'error')
        return redirect(url_for('index'))
    
    status = processing_status[session_id]
    
    if status['status'] != 'completed' or not status['result_file']:
        flash('Video not ready for download', 'error')
        return redirect(url_for('index'))
    
    try:
        if not os.path.exists(status['result_file']):
            flash('Video file not found', 'error')
            return redirect(url_for('index'))
        
        return send_file(
            status['result_file'],
            as_attachment=True,
            download_name=f'repo2reel_{session_id[:8]}.mp4',
            mimetype='video/mp4'
        )
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        flash('Error downloading video', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
