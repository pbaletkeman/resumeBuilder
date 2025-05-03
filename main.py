## original found here https://github.com/ShawhinT/AI-Builders-Bootcamp-2/tree/main/lightning-lesson
import os

import requests
import datetime

from markdown import Markdown

class ResumeBuilder:
    model = "gemma-3-4b-it-qat"

    endpoint = "http://localhost:1234/api/v0/chat/completions"
    # model = "codestral @ iq2_m"
    temperature = 0.7
    encoding = "utf-8"

    name = "Pete Letkeman"
    address = "803-1100 King St W\nToronto, ON\nCanada\nM6K 0C6\n519.331.1405"
    email = "pete@letkeman"

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
                print("processing - [" + jds["company"] + " - " + jds["title"] +"]" )
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
                            # get resume and suggestions from response
                            resume = body.split("Additional Suggestions")[0].strip()
                            suggestions = body.split("Additional Suggestions")[1].strip()
                            resume = resume.replace("*  ","- ").replace("*   ","- ").replace("-  ","- ")
                            return_listing.append({"resume":resume, "suggestions":suggestions, "company": jds["company"], "title":jds["title"]})
                        else:
                            # get cover letter from response
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
                with open(self.path + os.sep + cl["company"] + "-" + cl["title"] + "-" + self.current_date_time + ".txt", "w+t",
                          encoding=self.encoding) as file:
                    print("writing - " + file.name)
                    file.write(x[0])
            except Exception as ex:
                print(str(ex))

    def export_resume(self,new_resume):
        """
        Convert a markdown resume to PDF format and save it.

        Args:
            new_resume (str): The resume content in markdown format

        Returns:
            str: A message indicating success or failure of the PDF export
        """

        return new_resume
        #
        # try:
        #     # save as PDF
        #     output_pdf_file = "resumes/resume_new.pdf"
        #
        #     # Convert Markdown to HTML
        #     html_content = markdown(new_resume)
        #
        #     # Convert HTML to PDF and save
        #     HTML(string=html_content).write_pdf(output_pdf_file, stylesheets=['resumes/style.css'])
        #
        #     return f"Successfully exported resume to {output_pdf_file} 🎉"
        # except Exception as e:
        #     return f"Failed to export resume: {str(e)} 💔"

r = ResumeBuilder()
r.make_cover_letters()

