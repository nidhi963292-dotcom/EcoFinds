from flask import Flask
from extensions import db, bcrypt, jwt
from routes import bp
import config
import urllib.parse  # For URL-encoding

app = Flask(__name__)

# URL-encode the password in case it has special characters
password = urllib.parse.quote_plus(config.MYSQL_PASSWORD)

# Correct SQLAlchemy URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config.MYSQL_USER}:{password}@{config.MYSQL_HOST}/{config.MYSQL_DB}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

# Register blueprint under /api prefix
app.register_blueprint(bp, url_prefix='/api')

# Root route (just for quick check in browser)
@app.route('/')
def home():
    return "✅ Backend is running! Use /api/register (POST), /api/login (POST), or /api/products"

# Create tables if not exists
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
