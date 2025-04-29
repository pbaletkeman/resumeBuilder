## original found here https://github.com/ShawhinT/AI-Builders-Bootcamp-2/tree/main/lightning-lesson

import requests
from markdown import Markdown

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Open and read the Markdown file
with open("resumes/resume.md", "r", encoding="utf-8") as file:
    resume_string = file.read()

jd_string = """

Job Title: Senior Software Engineer – Capital Markets & Portfolio Management

We’re seeking a Senior Software Engineer to design and build robust, scalable systems that support portfolio and risk analytics, order and trade lifecycle processing, and investment strategies. You will work closely with portfolio managers, quantitative analysts, and product teams to develop technology solutions that create tangible business value in the capital markets space.

Key Responsibilities Design and implement end-to-end technology solutions in an Agile environment, collaborating with business and technical partners.
Leverage AWS cloud services to build scalable, cloud-native applications aligned with long-term architecture goals.
Manage structured and unstructured data, ensuring accessibility, accuracy, and usability across various business functions.
Identify and resolve data issues, exceptions, and inconsistencies while improving data quality and reliability.
Build and maintain CI/CD pipelines, automated tests, and infrastructure-as-code for efficient deployment.
Ensure system performance, reliability, and scalability across mission-critical applications.
Drive engineering excellence through coding best practices, technical mentorship, and peer collaboration.
 
Required Qualifications1
10+ years of experience with Python for backend development and data processing
10+ years of experience with Java in enterprise systems
5+ years working with relational databases (e.g., PostgreSQL, MySQL)
5+ years of hands-on experience with MongoDB
5+ years developing and deploying systems on AWS
Demonstrated experience in Capital Markets, Portfolio Management, or Risk Analytics
Strong analytical and problem-solving skills
Excellent verbal and written communication skills


Preferred SkillsFamiliarity with data pipelines, data lakes, and event-driven architectures
Experience with containerization (e.g., Docker, Kubernetes)
Working knowledge of DevOps practices and tools such as Terraform, GitHub Actions, or Jenkins
Exposure to quantitative models, financial data, or multi-asset strategies
Comfortable working in fast-paced, regulated environments with high-performance expectations


What We’re Looking ForIndependent self-starter who thrives in an entrepreneurial environment
Strong interpersonal skills and ability to communicate with diverse stakeholders, including front-office professionals, PMs, and quants
Highly organized with exceptional attention to detail and the ability to manage multiple priorities
Professional, adaptable, and collaborative team player
Results-oriented mindset with the ability to deliver under tight deadlines
"""


prompt_template = lambda resume_string, jd_string : f"""
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
   - Include an **"Additional Suggestions"** section at the end with actionable improvement recommendations.  

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
"""

# Make API call
prompt = prompt_template(resume_string, jd_string)

response = requests.post("http://localhost:1234/api/v0/chat/completions", json={
    "messages": [
        {"role": "system", "content": "Expert resume writer"},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7
})

print(response.content)
print("-" * 10)
print(response.raw)
print("-" * 10)
print(response.json())
print("****" * 10)

# Extract the tailored resume and additional suggestions from the response
try:
    tailored_resume = response.json()['choices'][0]['message']['content'].split("Additional Suggestions")[0].strip()
    additional_suggestions = response.json()['choices'][0]['message']['content'].split("Additional Suggestions")[1].strip()

    print("tailored_resume")
    print(tailored_resume)
    print("-" * 10)
    print("additional_suggestions")
    print(additional_suggestions)
    print("-" * 10)

except Exception as ex:
    print(str(ex))
