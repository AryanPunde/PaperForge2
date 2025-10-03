import os
import uuid
import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, session
from werkzeug.utils import secure_filename
from PIL import Image
from app import app, db
from models import ScanHistory
from utils import allowed_file, process_image, create_pdf, mock_ocr

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page with scanner options"""
    return render_template('index.html')

@app.route('/capture')
def capture():
    """Camera capture page"""
    return render_template('capture.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload from gallery"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process the image
                processed_filepath = process_image(filepath)
                
                # Store in session for preview
                if 'uploaded_images' not in session:
                    session['uploaded_images'] = []
                session['uploaded_images'].append({
                    'filename': filename,
                    'filepath': processed_filepath
                })
                session.modified = True
                
                flash('Image uploaded successfully!', 'success')
                return redirect(url_for('preview'))
            else:
                flash('Invalid file type. Please upload an image.', 'error')
                
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            flash('Error uploading file. Please try again.', 'error')
    
    return render_template('capture.html')

@app.route('/save_camera_image', methods=['POST'])
def save_camera_image():
    """Save image captured from camera"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image data'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image data'}), 400
        
        # Generate unique filename
        filename = f"camera_{uuid.uuid4()}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the image
        processed_filepath = process_image(filepath)
        
        # Store in session
        if 'uploaded_images' not in session:
            session['uploaded_images'] = []
        session['uploaded_images'].append({
            'filename': filename,
            'filepath': processed_filepath
        })
        session.modified = True
        
        return jsonify({'success': True, 'filename': filename})
        
    except Exception as e:
        logger.error(f"Camera save error: {str(e)}")
        return jsonify({'error': 'Failed to save image'}), 500

@app.route('/preview')
def preview():
    """Preview uploaded images with OCR results"""
    images = session.get('uploaded_images', [])
    if not images:
        flash('No images to preview. Please upload or capture images first.', 'info')
        return redirect(url_for('index'))
    
    # Perform mock OCR on all images
    ocr_results = []
    for img in images:
        try:
            # Read image for OCR
            img_path = img['filepath']
            ocr_text = mock_ocr(img_path)
            ocr_results.append({
                'filename': img['filename'],
                'text': ocr_text,
                'filepath': img_path
            })
        except Exception as e:
            logger.error(f"OCR error for {img['filename']}: {str(e)}")
            ocr_results.append({
                'filename': img['filename'],
                'text': 'Error extracting text from this image.',
                'filepath': img['filepath']
            })
    
    return render_template('preview.html', images=ocr_results)

@app.route('/convert_to_pdf', methods=['POST'])
def convert_to_pdf():
    """Convert uploaded images to PDF"""
    try:
        images = session.get('uploaded_images', [])
        if not images:
            flash('No images to convert. Please upload images first.', 'error')
            return redirect(url_for('index'))
        
        # Create PDF
        pdf_filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
        
        image_paths = [img['filepath'] for img in images]
        success = create_pdf(image_paths, pdf_path)
        
        if success:
            # Save to database
            scan_record = ScanHistory(filename=pdf_filename, pages=len(images))
            db.session.add(scan_record)
            db.session.commit()
            
            # Clear session
            session.pop('uploaded_images', None)
            
            flash(f'PDF created successfully: {pdf_filename}', 'success')
            return send_file(pdf_path, as_attachment=True)
        else:
            flash('Error creating PDF. Please try again.', 'error')
            return redirect(url_for('preview'))
            
    except Exception as e:
        logger.error(f"PDF conversion error: {str(e)}")
        flash('Error creating PDF. Please try again.', 'error')
        return redirect(url_for('preview'))

@app.route('/history')
def history():
    """View scan history"""
    try:
        scans = ScanHistory.query.order_by(ScanHistory.timestamp.desc()).all()
        return render_template('history.html', scans=scans)
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        flash('Error loading history.', 'error')
        return render_template('history.html', scans=[])

@app.route('/download_pdf/<int:scan_id>')
def download_pdf(scan_id):
    """Download PDF from history"""
    try:
        scan = ScanHistory.query.get_or_404(scan_id)
        pdf_path = os.path.join(app.config['PDF_FOLDER'], scan.filename)
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True)
        else:
            flash('PDF file not found.', 'error')
            return redirect(url_for('history'))
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        flash('Error downloading PDF.', 'error')
        return redirect(url_for('history'))

@app.route('/delete_scan/<int:scan_id>', methods=['POST'])
def delete_scan(scan_id):
    """Delete scan from history"""
    try:
        scan = ScanHistory.query.get_or_404(scan_id)
        
        # Delete PDF file
        pdf_path = os.path.join(app.config['PDF_FOLDER'], scan.filename)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        # Delete database record
        db.session.delete(scan)
        db.session.commit()
        
        flash('Scan deleted successfully.', 'success')
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        flash('Error deleting scan.', 'error')
    
    return redirect(url_for('history'))

@app.route('/clear_session')
def clear_session():
    """Clear current session images"""
    session.pop('uploaded_images', None)
    flash('Session cleared.', 'info')
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500
