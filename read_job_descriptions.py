import os

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

for x in job_descriptions:
    print(x)
