from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UploadForm(FlaskForm):
    file = FileField('File', validators=[InputRequired()])

    def validate_file(self, field):
        # Get the file extension
        if field.data:
            filename = secure_filename(field.data.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            if file_ext not in ['jpg', 'png']:
                raise ValidationError('Only .jpg and .png files are allowed.')