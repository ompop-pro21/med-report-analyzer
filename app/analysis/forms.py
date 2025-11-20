from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField

class UploadFileForm(FlaskForm):
    file = FileField('Medical Report', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDFs only!')
    ])
    submit = SubmitField('Analyze Report')