from markdown_pdf import MarkdownPdf, Section

pdf = MarkdownPdf(toc_level=2, optimize=True)

file_contents = ""
with open("resumes/resume.md", "r", encoding="utf-8") as src:
    file_contents += "".join(src.readlines())


css = "p {border: 1px solid white; }"
pdf.add_section(Section(file_contents), user_css=css)

pdf.save("sample.pdf")
