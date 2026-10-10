# MahaSkill – Skill to Employment Portal

A Flask + SQLite + Bootstrap prototype for connecting students, colleges, industry, government and NGOs through one skill-to-employment workflow.

## Run on Windows

```powershell
cd .\MahaSkill_Hackathon_Final_FIXED
python -m pip install -r requirements.txt
python app.py
```

Open: `http://127.0.0.1:5000`

## Main working modules

- Student / College / Industry / Government / NGO registration and login
- Username/email + password validation and duplicate credential checks
- 10-digit mobile validation and email `@` validation
- Student college searchable list with 40+ colleges and manual typing for unlisted colleges
- 25 student domains and 25 career goals
- 25-course learning catalog
- Recorded video lectures, lesson completion and progress tracking
- 25 career/domain assessment tracks using 10-question quizzes
- Final course assessment and 90% certificate rule
- Certificate view / print
- Career roadmap based on selected career goal
- Resume upload in student profile
- Skill/domain/career based job and internship recommendations
- 25 demo job/internship opportunities
- Apply Now opens an application profile in a new tab and records the application
- Industry candidate/application pipeline
- Government industry verification and opportunity approval
- College linked students, trainers, digital enrollment and offline attendance
- Teacher daily report with typed teacher name, attendance, today's topic and tomorrow's plan
- College report center with progress, skill gaps, feedback and teacher plans
- Student feedback to college/trainer
- NGO support programs for scholarships, training, devices, counselling and internship support
- Bootstrap cards, charts, animations and responsive UI

## Demo lecture videos

The original 15 demo courses keep the existing public demo MP4 lecture behaviour. The additional course tracks include local short demo lecture MP4 files inside `static/videos/` so the player works without needing extra files.

These are demonstration videos for the prototype; replace them with licensed instructional videos for production deployment.
