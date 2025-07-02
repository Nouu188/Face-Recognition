from flask import Flask
from routes.face_routes import face_bp

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(face_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
from face_utils import delete_invalid_vectors
delete_invalid_vectors()
