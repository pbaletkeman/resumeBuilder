from flask import Flask
from flask_restx import Api

from resumes_api import  resumes_api

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 0.5 * 1024 * 1024  # 0.5 megabytes
api = Api(
    title='My Title',
    version='1.0',
    description='A description',
    # All API metadatas
)

api.add_namespace(resumes_api)


if __name__ == "__main__":
    api.init_app(app)
    app.run(debug=True)
