from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename

from db import db_init, db
from models import Img
import base64

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/paint')
def paint():
    image=Img.query.all()
    return render_template('index2.html')


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['file']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()

    return 'Img Uploaded!', 200
    


@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)

if __name__ == '__main__':
  app.run(debug=True)    