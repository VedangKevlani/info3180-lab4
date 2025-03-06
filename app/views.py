import os
from app import app, db, login_manager
from flask import send_from_directory, current_app, render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import UserProfile
from app.forms import LoginForm, UploadForm

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

ALLOWED_EXTENSIONS = {'png', 'jpg'}

# Check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_uploaded_images():
    # Specify the folder where the images are stored
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    
    # List to store the image filenames
    image_files = []

    # Loop through the folder and get the filenames of all images
    for filename in os.listdir(upload_folder):
        # Optionally filter for image files if necessary (e.g. .jpg, .png)
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(filename)

    return image_files

@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    form = UploadForm()
    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File Saved', 'success')
            return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files
        else:
            flash('Invalid file type. Only .jpg and .png files are allowed.', 'danger')
            return redirect(request.url)  # Stay on the same page to allow re-uploading

    return render_template('upload.html', form=form)

from flask import current_app, send_from_directory

@app.route('/uploads/<filename>')
def get_image(filename):
    # Ensure the app context is active, so current_app can be used
    upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    print(f"Looking for file in: {upload_folder}")

    # Check if the file exists in the folder
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        abort(404)  # If file is not found, return a 404 error

    # Return the file using send_from_directory
    return send_from_directory(upload_folder, filename)


@app.route('/image-list')
def image_list():
    image_filenames = get_uploaded_images()
    upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    print(f"Looking for file in: {upload_folder}")
    print(f"Looking for file in: {image_filenames}")
    return "<br>".join(image_filenames)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Get the username and password values from the form.
        username = form.username.data
        password = form.password.data
        
        # Query the database for a user based on the username
        user = UserProfile.query.filter_by(username=username).first()

        print("Password updated successfully")
        print(f"Entered Username: {username}")
        print(f"User Retrieved: {user}")
        print(f"User Password: {user.password}")
        
        if user:
            print(f"Stored Hashed Password in DB: {user.password}")
            print(f"Entered Plain Password: {password}")

            # Check if the entered plain password matches the hashed password stored in the DB
            password_match = check_password_hash(user.password, password)  # No need to hash again
            print(f"Password Match: {password_match}")

            if not password_match:
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('upload'))
            else:
                return redirect(url_for('upload'))
                flash("Login failed! Incorrect password.", "danger")
        else:
            flash("Login failed! Username not found.", "danger")

    return render_template("login.html", form=form)

@app.route('/files')
def files():
    # Get the list of uploaded image files using the helper function
    images = get_uploaded_images()

    # Render the 'files.html' template and pass the list of image files
    return render_template('files.html', images=images)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
