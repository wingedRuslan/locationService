from flask import Flask, render_template
from models import db, User

# instance of the Flask class
app = Flask(__name__)

# app use the pilot db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pilot'
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
