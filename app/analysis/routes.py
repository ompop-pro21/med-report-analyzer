import os
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from werkzeug.utils import secure_filename
from .forms import UploadFileForm
from .utils import analyze_medical_image, reanalyze_medical_data

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/reanalyze', methods=['POST'])
def reanalyze():
    try:
        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400
        
        updated_results = reanalyze_medical_data(data)
        return render_template('analysis/result.html', results=updated_results)
    except Exception as e:
        return {"error": str(e)}, 500

@analysis_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        
        # Ensure upload directory exists
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        f.save(file_path)
        
        # Determine mime type
        mime_type = f.mimetype
        if not mime_type:
             if filename.lower().endswith('.pdf'):
                 mime_type = 'application/pdf'
             else:
                 mime_type = 'image/jpeg' # Default fallback

        # Analyze
        try:
            results = analyze_medical_image(file_path, mime_type)
            if results:
                if not results.get('is_medical_report', True):
                    flash(results.get('error', 'The uploaded document does not appear to be a medical report.'), 'error')
                    return render_template('analysis/upload.html', form=form)
                
                return render_template('analysis/result.html', results=results)
            else:
                flash('Could not analyze the document. Please try a clearer image.', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            
    return render_template('analysis/upload.html', form=form)