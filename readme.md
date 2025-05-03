## AI Resume And Cover Letter Optimizer

### Inspiration/original: 
https://github.com/ShawhinT/AI-Builders-Bootcamp-2/tree/main/lightning-lesson

This project generates cover letters and resumes that optimized for the supplied job descriptions.

Custom dynamic prompts are created and sent to an OpenAI compatiable service (completions endpoint).

LM Studio from https://lmstudio.ai/ is a great free resource, which is used in this project as well.

## Setup
### How to:
1. Install https://lmstudio.ai/ - LM Studio 0.3.15 (Build 11) or newer
2. Within LM Studio download `gemma-3-4b-it-qat` or any other LLM GUFF model file
   - Different LLM file will produce different results
3. Install https://python.org/ - Python 3.12 or newer  
4. Update these values in main.py: 
```
    name = "Pete Letkeman"
    address = "803-1100 King St W\nToronto, ON\nCanada\nM6K 0C6\n519.331.1405"
    email = "pete@letkeman"

    model = "gemma-3-4b-it-qat" // name of the model file that you downloaded

    endpoint = "http://localhost:1234/api/v0/chat/completions" // default LM Studio endpoint
    temperature = 0.09 // valid values range from 0.0 to 2.0, the higher the number more the change of a hallucination 
```
5. OpenAI can be used instead of LM Studio, you'll have to change 
```
# Make API call
response = requests.post(self.endpoint, json=data)
```
6. Install python requirements `pip install -r requirements.txt`

## Run:
- Place source `resume.md` in the `resume` directory
- Place all job descriptions in `job-descriptions` directory
  - Files should be named `company-position title.txt`
- Run by `python main.py`:
  - Once complete view contents of `output` directory
## Optional
   - The resumes may be incorrect, you can edit the resume markdown files and then regenerate the PDFs
   - To generate a new PDF from the markdown file run:
  
    python main.py --filepath=[path to markdown file]
