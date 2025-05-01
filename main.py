## original found here https://github.com/ShawhinT/AI-Builders-Bootcamp-2/tree/main/lightning-lesson
import os

import requests
import datetime

from markdown import Markdown

class ResumeBuilder:
    # model = "gemma-3-4b-it-qat"

    endpoint = "http://localhost:1234/api/v0/chat/completions"
    model = "codestral @ iq2_m"
    temperature = 0.7
    encoding = "utf-8"

    name = "Pete Letkeman"
    address = "803-1100 King St W\nToronto, ON\nCanada\nM6K 0C6\n519.331.1405\n"
    email = "pete@letkeman"

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

    def create_prompt_template(self,resume_string: str, jd_string: str):
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

        # name = "Pete Letkeman"
        # address = "803-1100 King St W\nToronto, ON\nCanada\nM6K 0C6\n519.331.1405\n"
        # email = "pete@letkeman"

        with open("prompts/prompt.md", "r", encoding=self.encoding) as file:
            retval = file.read()
        retval = retval.replace("{jd_string}", jd_string)
        retval = retval.replace("{resume_string}", resume_string)
        retval = retval.replace("{today}", today)
        retval = retval.replace("{address}", self.address)
        retval = retval.replace("{name}", self.name)
        retval = retval.replace("{email}", self.email)
        return retval


    def process_prompt(self):
        # this fails for long job descriptions if a cover letter is also prompted
        jobs = self.get_job_description()
        if len(jobs) > 0:
            return_listing = []
            for jds in jobs:
                prompt = self.create_prompt_template(self.get_resume(), jds["jd"])
                messages = [{"role": "system", "content": "Expert resume writer"}, {"role": "user", "content": prompt}]
                data = {"model": self.model, "messages": messages, "temperature": self.temperature}

                # Make API call
                response = requests.post(self.endpoint, json=data)

                # Extract the tailored resume and additional suggestions from the response
                try:
                    response_body = response.json()
                    if ('choices' in response_body) and (len(response_body['choices'] > 0)):
                        body = response_body['choices'][0]['message']['content']
                        resume = body.split("Additional Suggestions")[0].strip()
                        cover = body.split("Cover Letter")[1].strip()
                        suggestions = body.split("Additional Suggestions")[1].strip()
                        suggestions = suggestions.replace(cover,"")
                        resume = resume.replace("*  ","- ").replace("*   ","- ").replace("-  ","- ")
                        return_listing.append({"cover":cover, "resume":resume, "suggestions":suggestions})
                except Exception as ex:
                    print(str(ex))

            return return_listing
        else:
            return None

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

items = r.process_prompt()
print(items)
