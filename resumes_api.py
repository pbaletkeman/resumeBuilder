import json
import os
import threading
from typing import Any
import shutil


from flask import request, send_from_directory, send_file
from flask_restx import Resource, fields, Namespace

from werkzeug.datastructures import FileStorage
from werkzeug.utils import  secure_filename

from resume_builder import ResumeBuilder

ALLOWED_EXTENSIONS = ["txt", "md"]

resumes_api = Namespace("Resumes", description="APIs used to create optimized resumes and optimized cover letter using a LLM, uploaded job description and uploaded resume.", )

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

def make_llm_request(resume_builder: ResumeBuilder, create_cover: bool = True, create_resume: bool = True):
    print("Thread started")

    if create_cover:
            resume_builder.make_cover_letters()
    if create_resume:
            resume_builder.export_resume()

    print("Thread finished")


def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(args, form_field: str, upload_path: str) -> str:
    if form_field in args:
        resume_file = args[form_field]  # This is FileStorage instance
        if resume_file:
            resume_filename = secure_filename(resume_file.filename)
            if allowed_file(resume_filename):
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                resume_file.save(upload_path + os.sep + resume_filename)
                return upload_path + os.sep + resume_filename
            print("bad file extension")
            return ""
        print("empty file")
        return ""
    print("incorrect form element")
    return ""

@resumes_api.route("/process-data/", doc={"description":"Main endpoint which creates a resume and/or cover letter from the supplied data."})
class ProcessData(Resource):
    process_parser = resumes_api.parser()

    process_parser.add_argument("resume", location="files", type=FileStorage, required=False)
    process_parser.add_argument("jobDescription", location="files", type=FileStorage, required=False)
    process_parser.add_argument("body", location="form", default={"name": "pete letkeman",
                                                                  "address": "803-1100 King St. W.\nToronto Ontario\nCanada\nM6K 0C6\n519.331.1405\npete@letkeman",
                                                                  "email": "pete@letkeman.ca",
                                                                  "model": "gemma-3-4b-it-qat", "temperature": 0.09,
                                                                  "sourceJobDescription": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                                                                  "sourceResume": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.",
                                                                  "createCover": True, "createResume": True,
                                                                  "sourceJobTitle": "Software Developer",
                                                                  "sourceJobCompany": "Amazon"})

    encoding = "utf-8"
    upload_path = "uploads"

    @resumes_api.expect(process_parser)
    def post(self):

        args = self.process_parser.parse_args()
        form_data = request.form.to_dict()
        json_body = json.loads(form_data["body"])

        job_descriptions = []
        resume = ""
        job_description_file = handle_file_upload(args,"jobDescription", ProcessData.upload_path)
        if len(job_description_file) > 0:
            with open(job_description_file, "r", encoding=self.encoding) as content:
                jd = ".".join(content.readlines())
                company = job_description_file.split("-")[0]
                title = job_description_file.split("-")[1].replace(".txt", "")
                job_descriptions.append({"jd": jd, "company": company, "title": title})
        else:
            job_descriptions.append({"jd": json_body["sourceJobDescription"], "title": json_body["sourceJobTitle"], "company": json_body["sourceJobCompany"]})

        resume_file = handle_file_upload(args,"resume", ProcessData.upload_path)
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

        create_cover = json_body["createCover"] if "createCover" in json_body else False
        create_resume = json_body["createResume"] if "createResume" in json_body else False

        thread = threading.Thread(target=make_llm_request, args=(resume_builder, create_cover, create_resume))
        # Start the thread
        thread.start()

        return {"status":"processing"}, 201



@resumes_api.route("/get-results", doc={"description":"Get Results Directory File Listing"})
class FileListing(Resource):
    # list file logic
    @staticmethod
    def get(**kwargs: object) -> list[Any]:
        files = []
        main_path = ResumeBuilder.path + os.sep + ProcessData.upload_path
        for x in os.listdir(main_path):
            if os.path.isdir(main_path + os.sep + x):
                for i in os.listdir(main_path + os.sep + x):
                    files.append(x + "#" + i)
        return files

@resumes_api.route("/clear-files/", doc={"description":"Clear Work & Uploaded Files"})
class FileListing(Resource):
    # download file logic
    @staticmethod
    def delete() -> bool:
        try:
            shutil.rmtree(ResumeBuilder.path)
            shutil.rmtree(ProcessData.upload_path)
            return True
        except Exception as ex:
            print(ex)
            return False

@resumes_api.route("/get_results/<path:file_name>", doc={"description":"Download The Generated File"})
class FileListing(Resource):
    # download file logic
    @staticmethod
    def get(file_name: str):
        return send_from_directory(ResumeBuilder.path + os.sep + ProcessData.upload_path,
                                   file_name, as_attachment=True)

@resumes_api.route("/file_converter/", doc={"description": "Convert Markdown To PDF "})
class MarkdownToPDF(Resource):
    md_2_pdf_parser = resumes_api.parser()

    md_2_pdf_parser.add_argument("sourceFile", location="files", type=FileStorage, required=False)
    md_2_pdf_parser.add_argument("body", location="form", default={"source": "file contents file contents", "fileName":"somefile.txt"})

    @resumes_api.expect(md_2_pdf_parser)
    def post(self) :
        args = self.md_2_pdf_parser.parse_args()
        form_data = request.form.to_dict()
        json_body = json.loads(form_data["body"])

        source_file = handle_file_upload(args,"sourceFile", ProcessData.upload_path)
        contents = ""
        if len(source_file) > 0:
            with open(source_file, "r+t", encoding=ProcessData.encoding) as f:
                contents = "".join(f.read())
        else:
            if "source" in json_body:
                contents = json_body["source"]
            if "fileName" in json_body:
                source_file = json_body["fileName"]
        ResumeBuilder.save_pdf(source_file, contents)
        return send_file(source_file.replace(".txt",".pdf").replace(".md",".pdf"), as_attachment=True)
