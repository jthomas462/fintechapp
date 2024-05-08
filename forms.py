from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class SignUpForm(FlaskForm):
    ticker = StringField('Ticker')
    submit = SubmitField('Submit')



#Source: https://www.youtube.com/watch?v=-O9NMdvWmE8

