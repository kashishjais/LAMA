from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class MyUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(255))
    imgtype = db.Column(db.String(4))
    
    created_on = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return self.img

# Function that initializes the db and creates the tables
def db_init(app):
    db.init_app(app)

    # Creates the logs tables if the db doesnt already exist
    with app.app_context():
        db.create_all()
      


