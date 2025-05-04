import json
import os
import threading
import time

from flask import request
from flask_restx import Resource, fields, Namespace

from werkzeug.datastructures import FileStorage
from werkzeug.utils import  secure_filename

from resume_builder import ResumeBuilder

ALLOWED_EXTENSIONS = ["txt", "md"]
ALLOWED_MIME_TYPES = ["text/plain"] #['image/png', 'image/jpeg', 'application/pdf']


resumes_api = Namespace("resumes", description="Resume")


model = resumes_api.model("Model", {
    "name": fields.String,
    "address": fields.String,
    "email": fields.String,
    "model": fields.String,
    "temperature": fields.Float(exclusiveMin=0, exclusiveMax=2),
    "sourceJobDescription": fields.String,
    "sourceJobTitle": fields.String,
    "sourceJobCompany": fields.String,
    "sourceResume": fields.String,
    "createCover": fields.Boolean(example=True),
    "createResume": fields.Boolean(example=True),
    # 'date_updated': fields.DateTime(dt_format='rfc822'),
})



process_parser = resumes_api.parser()

process_parser.add_argument("resume", location="files", type=FileStorage, required=False)
process_parser.add_argument("jobDescription", location="files", type=FileStorage, required=False)
process_parser.add_argument("body", location="form", default={"name": "pete letkeman", "address": "803-1100 King St. W.\nToronto Ontario\nCanada\nM6K 0C6\n519.331.1405\npete@letkeman", "email": "pete@letkeman.ca", "model": "gemma-3-4b-it-qat", "temperature":0.09, "sourceJobDescription": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", "sourceResume":"Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.", "createCover": True, "createResume":True, "sourceJobTitle": "Software Developer", "sourceJobCompany": "Amazon"})

def make_llm_request():
    print("Thread started")
    with open("sample.txt", "w+t", encoding="utf-8") as t:
        for i in range(10):
            t.write(str(i))
            time.sleep(3)  # Simulate some work being done
    print("Thread finished")


def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resumes_api.route("/process-data/")
@resumes_api.expect(process_parser)
class ProcessData(Resource):
    encoding = "utf-8"
    upload_path = "uploads"

    def post(self):

        # # Create a new thread that runs the function do_this()
        # thread = threading.Thread(target=make_llm_request)
        #
        # # Start the thread
        # thread.start()

        args = process_parser.parse_args()
        form_data = request.form.to_dict()
        json_body = json.loads(form_data["body"])

        job_descriptions = []
        resume = ""
        job_description_file = self.handle_file_upload(args,"jobDescription")
        if len(job_description_file) > 0:
            with open(job_description_file, "r", encoding=self.encoding) as content:
                jd = ".".join(content.readlines())
                company = job_description_file.split("-")[0]
                title = job_description_file.split("-")[1].replace(".txt", "")
                job_descriptions.append({"jd": jd, "company": company, "title": title})
        else:
            job_descriptions.append({"jd": json_body["sourceJobDescription"], "title": json_body["sourceJobTitle"], "company": json_body["sourceJobCompany"]})

        resume_file = self.handle_file_upload(args,"resume")
        if len(resume_file) > 0:
            with open(resume_file, "r+t", encoding=self.encoding) as content:
                resume = "".join(content.readlines())

        resume_builder = ResumeBuilder(get_by_file=False)
        resume_builder.name = json_body["name"] if "name" in json_body else ""
        resume_builder.address = json_body["address"] if "address" in  json_body else ""
        resume_builder.email = json_body["email"] if "email" in  json_body else ""
        resume_builder.temperature = json_body ["temperature"]if "temperature" in  json_body else ""
        resume_builder.model = json_body["model"] if "model" in  json_body else ""
        resume_builder.resume = resume
        resume_builder.jobs = job_descriptions

        if "createCover" in json_body:
            if json_body["createCover"]:
                resume_builder.make_cover_letters()
        if "createResume" in json_body:
            if json_body["createResume"]:
                resume_builder.export_resume()

        return {"status":"processing"}, 201

    @staticmethod
    def handle_file_upload(args, form_field: str) -> str:
        if form_field in args:
            resume_file = args[form_field]  # This is FileStorage instance
            resume_filename = secure_filename(resume_file.filename)
            if allowed_file(resume_filename):
                if not os.path.exists(ProcessData.upload_path):
                    os.makedirs(ProcessData.upload_path)
                resume_file.save(ProcessData.upload_path + os.sep + resume_filename)
                return ProcessData.upload_path + os.sep + resume_filename
            return ""
        return ""

# @resumes_api.route("/")
# class Todo(Resource):
#     @resumes_api.marshal_with(model, envelope="resource")
#     def get(self, **kwargs):
#         return model # Some function that queries the db
