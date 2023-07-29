from flask import Flask,request,render_template,redirect,url_for,flash
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from random import choice
import string

def generate_short_id(num_of_chars: int):
    """Function to generate short_id of specified number of characters"""
    return ''.join(choice(string.ascii_letters+string.digits) for _ in range(num_of_chars))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ADD PATH'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.now(), nullable=False)
          
with app.app_context() :
   db.create_all()
   

class UrlForm(FlaskForm):
    url = StringField("",validators=[DataRequired(), URL()],render_kw={"placeholder": "Enter URL"})
    submit = SubmitField("Generate Url") 

@app.route('/',methods=['GET', 'POST'])
def home():
    form=UrlForm(meta={'csrf':False})
    if form.validate_on_submit():
        print("DONE")
        url = form.url.data
        random_id = generate_short_id(5)
        url_exists = Url.query.filter_by(original_url=url).first()
        if not url_exists :
            new_url = Url(
                original_url=url,
                short_id=random_id,
                created_at=datetime.now()
            )
            db.session.add(new_url)
            db.session.commit()
            short_url = request.host_url + random_id
        else :
            short_url = request.host_url + url_exists.short_id
        return render_template("index.html",form=form,short_url=short_url )
        
    return render_template("index.html",form=form)

@app.route('/<short_id>')
def redirect_url(short_id):
    link = Url.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
