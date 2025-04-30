## original found here https://github.com/ShawhinT/AI-Builders-Bootcamp-2/tree/main/lightning-lesson
import os

import requests
import re
import datetime


from markdown import Markdown

model = "gemma-3-4b-it-qat"
temperature = 0.7

def get_job_description() -> list[str]:
    job_descriptions = []

    for x in os.listdir("job-descriptions"):
        if x.endswith(".txt"):
            # Prints only text file present in My Folder
            print(x)
            with open("job-descriptions" + os.sep + x, "r", encoding="utf-8") as content:
                jd = ".".join(content.readlines())
                company = x.split("-")[0]
                title = x.split("-")[1].replace(".txt","")
                job_descriptions.append({"jd":jd, "company": company, "title":title})

    return job_descriptions

def get_resume() -> str:
    # Open and read the Markdown file
    with open("resume/resume.md", "r", encoding="utf-8") as file:
        return file.read()


def create_prompt_template(resume_string: str, jd_string: str):
    today = (datetime.datetime(2025, 6, 1)
    .strftime("%A, %B %d, %Y")
    .replace("01,", "1,")
    .replace("02,", "2,")
    .replace("03,","3,")
    .replace("04,", "4,")
    .replace("04,", "4,")
    .replace("05,", "5,")
    .replace("06,", "6,")
    .replace("07,", "7,")
    .replace("08,","8,")
    .replace("09,", "9,"))

    return f"""
You are a professional resume optimization expert specializing in tailoring resumes to specific job descriptions. Your goal is to optimize my resume and provide actionable suggestions for improvement to align with the target role.

### Guidelines:
1. **Relevance**:
    - Prioritize experiences, skills, and achievements **most relevant to the job description**.
    - Remove or de-emphasize irrelevant details to ensure a **concise** and **targeted** resume.
    - Limit work experience section to 2-3 most relevant roles
    - Limit bullet points under each role to 2-3 most relevant impacts

2. **Action-Driven Results**:
    - Use **strong action verbs** and **quantifiable results** (e.g., percentages, revenue, efficiency improvements) to highlight impact.

3. **Keyword Optimization**:
    - Integrate **keywords** and phrases from the job description naturally to optimize for ATS (Applicant Tracking Systems).

4. **Additional Suggestions** *(If Gaps Exist)*:
    - If the resume does not fully align with the job description, suggest:
        1. **Additional technical or soft skills** that I could add to make my profile stronger.
        2. **Certifications or courses** I could pursue to bridge the gap.
        3. **Project ideas or experiences** that would better align with the role.

5. **Formatting**:
    - Output the tailored resume in **clean Markdown format**.
    - Include an **"Additional Suggestions"** section next with actionable improvement recommendations.
    - Include a **"Cover Letter"** section at the end with cover letter for the job description.
        - The cover letter should be concise and highlight my key skills and experience, tailored the job description
        - Include Pete Letkeman as the name
        
---

### Input:
- **My resume**:
{resume_string}

- **The job description**:
{jd_string}

---

### Output:
1. **Tailored Resume**:
    - A resume in **Markdown format** that emphasizes relevant experience, skills, and achievements.
    - Incorporates job description **keywords** to optimize for ATS.
    - Uses strong language and is no longer than **one page**.

2. **Additional Suggestions** *(if applicable)*:
    - List **skills** that could strengthen alignment with the role.
    - Recommend **certifications or courses** to pursue.
    - Suggest **specific projects or experiences** to develop.

3. **Cover Letter**
    - A cover letter in **Markdown format** tailored to the {jd_string} and company.
"""

# Make API call
jds = get_job_description()[0]
prompt = create_prompt_template(get_resume(), jds["jd"])
messages = [{"role": "system", "content": "Expert resume writer"}, {"role": "user", "content": prompt}]
data = {"model": model, "messages": messages, "temperature": temperature}

response = requests.post("http://localhost:1234/api/v0/chat/completions", json=data)


# Extract the tailored resume and additional suggestions from the response
try:
    body = response.json()['choices'][0]['message']['content']
    tailored_resume = body.split("Additional Suggestions")[0].strip()
    cover_letter = body.split("Cover Letter")[1].strip()
    additional_suggestions = body.split("Additional Suggestions")[1].strip()
    additional_suggestions = additional_suggestions.replace(cover_letter,"")
    tailored_resume = tailored_resume.replace("*  ","- ").replace("*   ","- ").replace("-  ","- ")
    print("tailored_resume")
    print(tailored_resume)
    print("-" * 20)
    print("cover letter")
    print(cover_letter)
    print("-" * 20)
    print("additional_suggestions")
    print(additional_suggestions)
    # print("-" * 20)
    # print(response.json())

except Exception as ex:
    print(str(ex))
