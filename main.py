## original found here https://github.com/ShawhinT/AI-Builders-Bootcamp-2/tree/main/lightning-lesson
import argparse

from resume_builder import ResumeBuilder

if __name__ == '__main__':
    # python main.py --filepath="output\Systems & Software\resume-Senior Software Engineer-2025-05-03-10-52.md"
    parser = argparse.ArgumentParser(description="resume optimizer")
    parser.add_argument("-o", "--filepath", help="source md file")
    args = parser.parse_args()
    if args.filepath is not None:
        r = ResumeBuilder(get_by_file=True)
        r.md_to_pdf(args.filepath)
        print("check out `output` directory")
    else:
        r = ResumeBuilder(get_by_file=True)
        r.export_resume()
        r.make_cover_letters()
        print("check out `output` directory")

