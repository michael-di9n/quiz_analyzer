
# Project setup
1.Settings Up the Virtual Env
`python -m venv venv_quiz`
`.\venv_quiz\Scripts\activate`

2. Install requirement
`pip install -r requirements.txt`


Currently only works with simple questions - multiple choice and no coding questions
## Potential improvement
1. Two scan 
   1. First identify question region, answer region etc., by using identation 
   2. Identify pattern of a question on the screen 
2. Then do a high quality OCR on the question