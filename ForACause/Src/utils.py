import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/images'  # Define  upload folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def save_image(image_file):
    if image_file and '.' in image_file.filename and \
       image_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        return filename
    return None