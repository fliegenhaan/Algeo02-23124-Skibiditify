# app/routes/audio_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename  # Tambahkan ini
from app.services.audio_service import AudioService
from app.utils.audio.file_handler import save_dataset_file, allowed_file
from app.config import AUDIO_DATASET_DIR, AUDIO_TEMP_DIR
import os

bp = Blueprint('audio', __name__)
audio_service = AudioService()

@bp.route('/upload', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Save file temporarily
        temp_path = os.path.join(AUDIO_TEMP_DIR, secure_filename(file.filename))
        file.save(temp_path)
        
        # Process audio and get matches
        matches = audio_service.find_matches(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        print("Sending response:", {  # Debug print
            'matches': matches,
            'executionTime': audio_service.last_execution_time
        })
        
        return jsonify({
            'matches': matches,
            'executionTime': audio_service.last_execution_time
        })
    except Exception as e:
        print("Error processing query:", str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/dataset', methods=['POST'])
def upload_dataset():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    uploaded_files = []
    
    for file in files:
        if file.filename == '' or not allowed_file(file.filename):
            continue
            
        filepath = save_dataset_file(file)
        if filepath:
            uploaded_files.append(os.path.basename(filepath))
    
    return jsonify({
        'message': f'Successfully uploaded {len(uploaded_files)} files',
        'files': uploaded_files
    })

@bp.route('/dataset', methods=['GET'])
def get_dataset():
    try:
        files = [f for f in os.listdir(AUDIO_DATASET_DIR) if allowed_file(f)]
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500