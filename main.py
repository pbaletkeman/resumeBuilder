## original found here https://github.com/ShawhinT/AI-Builders-Bootcamp-2/tree/main/lightning-lesson
import os

import requests
import datetime
import argparse


from markdown_pdf import MarkdownPdf, Section

class ResumeBuilder:
    name = "Pete Letkeman"
    address = "803-1100 King St W\nToronto, ON\nCanada\nM6K 0C6\n519.331.1405"
    email = "pete@letkeman"

    model = "gemma-3-4b-it-qat"

    endpoint = "http://localhost:1234/api/v0/chat/completions"
    temperature = 0.09

    encoding = "utf-8"

    path = "output"

    if not os.path.exists(path):
        os.makedirs(path)

    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

    def get_job_description(self) -> list[str]:
        job_descriptions = []

        for x in os.listdir("job-descriptions"):
            if x.endswith(".txt"):
                # Prints only text file present in My Folder
                with open("job-descriptions" + os.sep + x, "r", encoding=self.encoding) as content:
                    jd = ".".join(content.readlines())
                    company = x.split("-")[0]
                    title = x.split("-")[1].replace(".txt","")
                    job_descriptions.append({"jd":jd, "company": company, "title":title})

        return job_descriptions

    def get_resume(self) -> str:
        # Open and read the Markdown file
        with open("resume/resume.md", "r", encoding=self.encoding) as file:
            return file.read()

    def create_prompt_template(self,resume_string: str, jd_string: str, is_cover: bool):
        today = (datetime.datetime.now()
        .strftime("%A, %B %d, %Y")
        .replace("01,","1,")
        .replace("02,","2,")
        .replace("03,","3,")
        .replace("04,","4,")
        .replace("04,","4,")
        .replace("05,","5,")
        .replace("06,","6,")
        .replace("07,","7,")
        .replace("08,","8,")
        .replace("09,","9,"))

        retval = ""
        if not is_cover:
            with open("prompts/resume-prompt.md", "r", encoding=self.encoding) as file:
                retval = file.read()
        else:
            with open("prompts/cover-prompt.md", "r", encoding=self.encoding) as file:
                retval = file.read()

        retval = retval.replace("{jd_string}", jd_string)
        retval = retval.replace("{resume_string}", resume_string)
        retval = retval.replace("{today}", today)
        retval = retval.replace("{address}", self.address)
        retval = retval.replace("{name}", self.name)
        retval = retval.replace("{email}", self.email)
        return retval


    def process_prompt(self, is_cover: bool):
        # this fails for long job descriptions if a cover letter is also prompted
        jobs = self.get_job_description()
        if len(jobs) > 0:
            return_listing = []
            for jds in jobs:
                prompt = self.create_prompt_template(self.get_resume(), jds["jd"], is_cover)
                messages = [{"role": "system", "content": "Expert resume writer"}, {"role": "user", "content": prompt}]
                data = {"model": self.model, "messages": messages, "temperature": self.temperature}

                # Make API call
                response = requests.post(self.endpoint, json=data)

                try:
                    response_body = response.json()
                    if 'choices' in response_body:
                        body = response_body['choices'][0]['message']['content']
                        if not is_cover:
                            print("processing resume: [" + jds["company"] + " - " + jds["title"] +"]" )
                            # get resume and suggestions from response
                            resume = body.split("Additional Suggestions")[0].strip()
                            suggestions = body.split("Additional Suggestions")[1].strip()
                            if "```" in resume:
                                start = resume.find("```")
                                if start > 0:
                                    resume = resume[start:]
                                resume = resume.replace("```markdown","")
                            while resume.endswith("#"):
                                resume = resume[0:-1]
                            while resume.endswith("*"):
                                resume = resume[0:-1]
                            resume = resume.replace("`","")
                            resume = resume.replace("---","").strip()
                            return_listing.append({"resume":resume, "suggestions":suggestions, "company": jds["company"], "title":jds["title"]})
                        else:
                            # get cover letter from response
                            print("processing cover letter: [" + jds["company"] + " - " + jds["title"] + "]")
                            return_listing.append({"cover":body, "company": jds["company"], "title":jds["title"]})
                except Exception as ex:
                    print(str(ex))

            return return_listing
        else:
            return None

    def make_cover_letters(self):
        cover_letters = self.process_prompt(is_cover=True)
        for cl in cover_letters:
            x = cl["cover"].split("---")
            try:
                if not os.path.exists(self.path + os.sep + cl["company"] ):
                    os.makedirs(self.path + os.sep + cl["company"])
                with open(self.path + os.sep + cl["company"] + os.sep + "cover-" + cl["title"] + "-" + self.current_date_time + ".txt", "w+t",
                          encoding=self.encoding) as file:
                    print("writing - " + file.name)
                    file.write(x[0])
            except Exception as ex:
                print(str(ex))

    def export_resume(self):
        resumes = self.process_prompt(is_cover=False)
        for res in resumes:
            try:
                if not os.path.exists(self.path + os.sep + res["company"]):
                    os.makedirs(self.path + os.sep + res["company"])
                with open(self.path + os.sep + res["company"] + os.sep + "resume-" + res["title"] + "-" + self.current_date_time + ".md", "w+t",
                          encoding=self.encoding) as file:
                    print("writing - " + file.name)
                    file.write(res["resume"])
                    self.save_pdf(file.name,res["resume"])
                with open(self.path + os.sep + res["company"] + os.sep + "suggestion-" + res["title"] + "-" + self.current_date_time + ".md", "w+t",
                          encoding=self.encoding) as file:
                    print("writing - " + file.name)
                    file.write(res["suggestions"])
            except Exception as ex:
                print(str(ex))

    @staticmethod
    def save_pdf(file_name: str, file_contents:str):

        pdf = MarkdownPdf(toc_level=2, optimize=True)

        css = "p {border: 2px solid white; } li {border: 2px solid white; margin: 2px}"
        pdf.add_section(Section(file_contents), user_css=css)

        print("writing - " + file_name.replace(".md",".pdf"))
        pdf.save(file_name.replace(".md",".pdf"))

    def md_to_pdf(self, md_file:str):
        with open(md_file, "r", encoding=self.encoding) as file:
            retval = file.read()
        self.save_pdf(md_file,retval)

if __name__ == '__main__':
    # python main.py --filepath="output\Systems & Software\resume-Senior Software Engineer-2025-05-03-10-52.md"
    parser = argparse.ArgumentParser(description="resume optimizer")
    parser.add_argument("-o", "--filepath", help="source md file")
    args = parser.parse_args()
    if args.filepath is not None:
        r = ResumeBuilder()
        r.md_to_pdf(args.filepath)
        print("check out `output` directory")
    else:
        r = ResumeBuilder()
        r.export_resume()
        r.make_cover_letters()
        print("check out `output` directory")

