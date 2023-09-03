from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,URLField,SelectField,BooleanField
from wtforms.validators import DataRequired,URL
from flask_ckeditor import CKEditorField

coffee_choices = ['☕','☕☕','☕☕☕','☕☕☕☕','☕☕☕☕☕']
wifi_rating = ['✘','💪💪','💪💪💪','💪💪💪💪','💪💪💪💪💪']
power_rating = ['🔌','🔌🔌','🔌🔌🔌','🔌🔌🔌🔌','🔌🔌🔌🔌🔌']
##WTForm
# class CafeForm(FlaskForm):
#    cafe = StringField('Cafe name',validators=[DataRequired()])
#    location = URLField('Cafe Location on Google Maps(URL)', validators=[DataRequired()])
#    open = StringField('Open Time e.g. 8AM', validators=[DataRequired()])
#    closed = StringField('Closing Time e.g. 5PM', validators=[DataRequired()])
#    coffee = SelectField('Coffee Rating', choices=coffee_choices, validators=[DataRequired()])
#    wifi = SelectField('Wifi Rating', choices=wifi_rating, validators=[DataRequired()])
#    power = SelectField('Power Socket Availability', choices=power_rating, validators=[DataRequired()])
#
#    submit = SubmitField('Submit')

class CafeForm(FlaskForm):
    name = StringField('Cafe Name',validators=[DataRequired()])
    map_url = URLField('Cafe Location on Google Maps(URL)', validators=[DataRequired()])
    img_url = URLField('Cafe Image on Google Maps(URL)',validators=[DataRequired()])
    location = StringField('Cafe Address',validators=[DataRequired()])
    seats = SelectField('Is there a good amount of seating?',choices=['Yes','No'],validators=[DataRequired()])
    has_toilet = SelectField('Does this place have a bathroom?',choices=['True','False'],validators=[DataRequired()])
    has_wifi = SelectField('Does this place have free wifi?',choices=['True','False'],validators=[DataRequired()])
    has_sockets = SelectField('Does this place have electric sockets to use ?',choices=['True','False'],validators=[DataRequired()])
    can_take_calls = SelectField('Can you take calls in this coffee shop?',choices=['True','False'],validators=[DataRequired()])
    coffee_price = StringField('What is the price of black coffee at this coffee shop.',validators=[DataRequired()])
    submit = SubmitField('Submit Review', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),URL()])
    password = PasswordField('Password',validators=[DataRequired()])
    name = StringField('First and Last Name',validators=[DataRequired()])
    submit = SubmitField('Sign Me Up!', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), URL()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')



class CommentForm(FlaskForm):
    body = CKEditorField()
    submit = SubmitField('Comment')