from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import sqlite3, os, random, re
import pandas as pd
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,'data','mahaskill.db')
app=Flask(__name__); app.secret_key='mahaskill-demo-secret-change-me'

ROLES={'student':'Student','college':'College','industry':'Industry','government':'Government','ngo':'Social NGO'}

UPLOAD_FOLDER=os.path.join(BASE,'static','uploads') if 'BASE' in globals() else os.path.join(os.path.dirname(os.path.abspath(__file__)),'static','uploads')
os.makedirs(UPLOAD_FOLDER,exist_ok=True)
COLLEGE_LIST=sorted([
'Dhole Patil College of Engineering','College of Engineering Pune (COEP Technological University)','Pune Institute of Computer Technology','Pune Vidyarthi Griha College of Engineering and Technology','MIT World Peace University','MIT Academy of Engineering','Vishwakarma Institute of Technology','Vishwakarma Institute of Information Technology','Pimpri Chinchwad College of Engineering','Pimpri Chinchwad University','AISSMS Institute of Information Technology','AISSMS College of Engineering','Sinhgad College of Engineering','Sinhgad Institute of Technology and Science','JSPM Rajarshi Shahu College of Engineering','JSPM Narhe Technical Campus','JSPM Jayawantrao Sawant College of Engineering','DY Patil College of Engineering','Dr. D. Y. Patil Institute of Engineering and Management','Bharati Vidyapeeth College of Engineering','Bharati Vidyapeeth Deemed University College of Engineering','Modern Education Society College of Engineering','Trinity College of Engineering and Technology','Rajarshi Shahu College of Engineering','Genba Sopanrao Moze College of Engineering','International Institute of Information Technology Pune','Army Institute of Technology','Symbiosis Institute of Technology','FLAME University','Indira College of Engineering and Management','Zeal College of Engineering and Research','NBN Sinhgad School of Engineering','Marathwada Mitra Mandal College of Engineering','KJ College of Engineering and Management Research','Alard College of Engineering and Management','G H Raisoni College of Engineering and Management','RMD Sinhgad Technical Institutes Campus','SKN Sinhgad Institute of Technology and Science','Anantrao Pawar College of Engineering and Research','Modern College of Arts Science and Commerce'
])
DOMAINS=['Java Full Stack','Data Engineering','Software Development','Web Development','Python Development','Data Analytics','Android Development','Database & SQL','Networking & Cloud','Cybersecurity','AI & ML Foundations','DevOps','UI/UX Design','Cloud Computing','Mobile App Development','Backend Development','Frontend Development','QA & Testing','Business Analytics','IoT Development','C/C++ Development','System Administration','Digital Marketing Technology','E-Commerce Technology','Technical Support']
CAREER_GOALS=['Java Developer','Full Stack Developer','Data Engineer','Data Analyst','Software Developer','Web Developer','Python Developer','Android Developer','Database Developer','Network Engineer','Cybersecurity Analyst','DevOps Engineer','UI/UX Designer','Cloud Engineer','Mobile App Developer','Backend Developer','Frontend Developer','QA Engineer','Business Analyst','IoT Developer','C/C++ Developer','System Administrator','Digital Technology Specialist','E-Commerce Developer','Technical Support Engineer']
CAREER_COURSES={
'Java Developer':['Java Full Stack Development','SQL & Database Essentials','Java Spring Boot & REST APIs','Git & GitHub Essentials','SDLC & Software Testing'],
'Full Stack Developer':['Web Development Starter','JavaScript Essentials','Java Full Stack Development','Java Spring Boot & REST APIs','SQL & Database Essentials'],
'Data Engineer':['Python for Data Analytics','SQL & Database Essentials','Data Engineering Foundations','Data Analytics with SQL','Cloud Computing Fundamentals'],
'Data Analyst':['Python for Data Analytics','SQL & Database Essentials','Data Analytics with SQL','Data Visualization with Python','Career Ready: Resume & Interview'],
'Software Developer':['Software Development with Python','Java Full Stack Development','Git & GitHub Essentials','SDLC & Software Testing','Problem Solving & Aptitude'],
'Web Developer':['Web Development Starter','JavaScript Essentials','React & Frontend Development','Backend APIs with Python Flask','Git & GitHub Essentials'],
'Python Developer':['Software Development with Python','Python for Data Analytics','Backend APIs with Python Flask','Git & GitHub Essentials','SDLC & Software Testing'],
'Android Developer':['Android Development with Java','Java Full Stack Development','DBMS & Data Modeling','Git & GitHub Essentials','SDLC & Software Testing'],
'Database Developer':['SQL & Database Essentials','DBMS & Data Modeling','Data Analytics with SQL','Data Engineering Foundations','Git & GitHub Essentials'],
'Network Engineer':['Networking Fundamentals','Cloud Computing Fundamentals','Cybersecurity Fundamentals','Python for Data Analytics','Problem Solving & Aptitude'],
'Cybersecurity Analyst':['Cybersecurity Fundamentals','Networking Fundamentals','Python for Data Analytics','Cloud Computing Fundamentals','SDLC & Software Testing'],
'DevOps Engineer':['Git & GitHub Essentials','DevOps & CI/CD Basics','Cloud Computing Fundamentals','Networking Fundamentals','SDLC & Software Testing'],
'UI/UX Designer':['UI/UX for Developers','Web Development Starter','React & Frontend Development','Career Ready: Resume & Interview'],
'Cloud Engineer':['Cloud Computing Fundamentals','Networking Fundamentals','DevOps & CI/CD Basics','Cybersecurity Fundamentals','Git & GitHub Essentials'],
'Mobile App Developer':['Android Development with Java','Java Full Stack Development','DBMS & Data Modeling','Git & GitHub Essentials','SDLC & Software Testing'],
'Backend Developer':['Backend APIs with Python Flask','Java Spring Boot & REST APIs','SQL & Database Essentials','Git & GitHub Essentials','SDLC & Software Testing'],
'Frontend Developer':['Web Development Starter','JavaScript Essentials','React & Frontend Development','UI/UX for Developers','Git & GitHub Essentials'],
'QA Engineer':['SDLC & Software Testing','Web Development Starter','JavaScript Essentials','Git & GitHub Essentials','Problem Solving & Aptitude'],
'Business Analyst':['Data Analytics with SQL','Data Visualization with Python','SQL & Database Essentials','Career Ready: Resume & Interview','Problem Solving & Aptitude'],
'IoT Developer':['IoT & Arduino Basics','C & C++ Programming Basics','Networking Fundamentals','Python for Data Analytics','DBMS & Data Modeling'],
'C/C++ Developer':['C & C++ Programming Basics','Problem Solving & Aptitude','SDLC & Software Testing','Git & GitHub Essentials','DBMS & Data Modeling'],
'System Administrator':['Networking Fundamentals','Cloud Computing Fundamentals','Cybersecurity Fundamentals','Python for Data Analytics','SDLC & Software Testing'],
'Digital Technology Specialist':['Web Development Starter','Data Analytics with SQL','JavaScript Essentials','Career Ready: Resume & Interview'],
'E-Commerce Developer':['Web Development Starter','JavaScript Essentials','Backend APIs with Python Flask','SQL & Database Essentials','Career Ready: Resume & Interview'],
'Technical Support Engineer':['Networking Fundamentals','SQL & Database Essentials','Problem Solving & Aptitude','Career Ready: Resume & Interview']
}
ASSESSMENT_SUBJECT_MAP={
'Java Developer':'Java','Full Stack Developer':'JavaScript','Data Engineer':'SQL','Data Analyst':'Data Analytics','Software Developer':'Python','Web Developer':'HTML/CSS','Python Developer':'Python','Android Developer':'Android','Database Developer':'DBMS','Network Engineer':'Networking','Cybersecurity Analyst':'Networking','DevOps Engineer':'SDLC','UI/UX Designer':'HTML/CSS','Cloud Engineer':'Networking','Mobile App Developer':'Android','Backend Developer':'Python','Frontend Developer':'JavaScript','QA Engineer':'SDLC','Business Analyst':'Data Analytics','IoT Developer':'C','C/C++ Developer':'C++','System Administrator':'Networking','Digital Technology Specialist':'JavaScript','E-Commerce Developer':'JavaScript','Technical Support Engineer':'Networking'}
ASSESSMENT_TRACKS=[(g,ASSESSMENT_SUBJECT_MAP.get(g,'Python')) for g in CAREER_GOALS]
SKILLS=['Java','Python','SQL','Networking','Android','C','C++','DBMS','Data Analytics','SDLC','HTML/CSS','JavaScript']
CAREER_MAP={
 'Java Developer':['Java','SQL','DBMS','SDLC'],
 'Full Stack Developer':['Java','SQL','HTML/CSS','JavaScript','DBMS'],
 'Data Analyst':['Python','SQL','Data Analytics','DBMS'],
 'Software Developer':['Java','Python','SQL','DBMS','SDLC'],
 'Android Developer':['Java','Android','SQL','DBMS'],
 'Network Engineer':['Networking','Python','SQL'],
 'Other':['Python','SQL','DBMS']}

CAREER_ROADMAPS={
 'Java Developer':[('Core Java','Java Full Stack Development','Learn Java syntax, OOP, collections and exception handling.'),('SQL & DBMS','SQL & Database Essentials','Build strong SQL, joins, keys and database concepts.'),('Web Basics','Web Development Starter','Learn HTML, CSS and responsive web basics.'),('JavaScript','JavaScript Essentials','Learn DOM, events and frontend interaction.'),('Full Stack','Java Full Stack Development','Practice backend, JDBC and full-stack application flow.'),('SDLC & Testing','SDLC & Software Testing','Understand development lifecycle, Agile and testing.')],
 'Full Stack Developer':[('Java','Java Full Stack Development','Build Java programming and backend fundamentals.'),('SQL & DBMS','SQL & Database Essentials','Learn relational databases, queries and joins.'),('Web','Web Development Starter','Create responsive web pages with HTML and CSS.'),('JavaScript','JavaScript Essentials','Add dynamic behaviour with JavaScript.'),('Full Stack Practice','Java Full Stack Development','Connect frontend, backend and database.'),('Testing','SDLC & Software Testing','Learn SDLC, testing and project delivery.')],
 'Data Engineer':[('Python','Python for Data Analytics','Strengthen Python and data structures.'),('SQL','SQL & Database Essentials','Master queries, joins and aggregation.'),('DBMS','DBMS & Data Modeling','Learn data modelling, normalization and transactions.'),('Data Analytics','Data Analytics with SQL','Analyse datasets and create useful insights.'),('Data Foundations','Data Engineering Foundations','Understand pipelines, ETL and data workflows.'),('SDLC','SDLC & Software Testing','Apply engineering and testing practices.')],
 'Data Analyst':[('Python','Python for Data Analytics','Use Python for data preparation and analysis.'),('SQL','SQL & Database Essentials','Query and filter business data.'),('Data Analytics','Data Analytics with SQL','Perform practical analysis and insights.'),('DBMS','DBMS & Data Modeling','Understand how structured data is stored.'),('Problem Solving','Problem Solving & Aptitude','Improve analytical thinking.'),('Career Ready','Career Ready: Resume & Interview','Prepare for analyst interviews and jobs.')],
 'Software Developer':[('Programming','Software Development with Python','Build programming and problem-solving fundamentals.'),('Java','Java Full Stack Development','Learn enterprise programming concepts.'),('SQL','SQL & Database Essentials','Work with application databases.'),('Web','Web Development Starter','Build web interfaces.'),('SDLC','SDLC & Software Testing','Understand software lifecycle and testing.'),('Aptitude','Problem Solving & Aptitude','Strengthen placement problem solving.')],
 'Android Developer':[('Java','Android Development with Java','Learn Java for Android development.'),('Android','Android Development with Java','Build screens, activities and layouts.'),('Database','DBMS & Data Modeling','Understand application data and storage.'),('SQL','SQL & Database Essentials','Strengthen database querying.'),('Testing','SDLC & Software Testing','Test and improve applications.'),('Career','Career Ready: Resume & Interview','Prepare for Android development opportunities.')],
 'Network Engineer':[('Networking','Networking Fundamentals','Learn OSI, TCP/IP and network devices.'),('IP & Security','Networking Fundamentals','Practice addressing and troubleshooting.'),('Python','Python for Data Analytics','Use scripting fundamentals for automation.'),('SQL','SQL & Database Essentials','Understand data used by applications.'),('Problem Solving','Problem Solving & Aptitude','Improve technical reasoning.'),('Career','Career Ready: Resume & Interview','Prepare for network roles.')]}


def db():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; return con

def init_db():
    os.makedirs(os.path.dirname(DB),exist_ok=True)
    con=db(); c=con.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,role TEXT NOT NULL,full_name TEXT,username TEXT UNIQUE,email TEXT UNIQUE,mobile TEXT,password TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS students(user_id INTEGER PRIMARY KEY,education TEXT,college_name TEXT,domain TEXT,current_skills TEXT,career_goal TEXT,location TEXT);
    CREATE TABLE IF NOT EXISTS colleges(user_id INTEGER PRIMARY KEY,college_name TEXT,college_id TEXT,coordinator TEXT,email TEXT,mobile TEXT,department TEXT,address TEXT,city TEXT,industry_info TEXT);
    CREATE TABLE IF NOT EXISTS industries(user_id INTEGER PRIMARY KEY,organization_name TEXT,company_id TEXT,contact_person TEXT,email TEXT,mobile TEXT,domain TEXT,address TEXT,city TEXT,website TEXT);
    CREATE TABLE IF NOT EXISTS governments(user_id INTEGER PRIMARY KEY,department_name TEXT,officer_name TEXT,email TEXT,mobile TEXT,department_type TEXT,state_district TEXT,address TEXT);
    CREATE TABLE IF NOT EXISTS ngos(user_id INTEGER PRIMARY KEY,ngo_name TEXT,registration_id TEXT,coordinator TEXT,email TEXT,mobile TEXT,focus_area TEXT,address TEXT,city TEXT,website TEXT);
    CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT,question TEXT,a TEXT,b TEXT,c TEXT,d TEXT,answer TEXT,difficulty TEXT);
    CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,subject TEXT,score INTEGER,total INTEGER,percentage REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,subject TEXT,description TEXT,duration TEXT,mode TEXT,paid TEXT,price REAL,trainer TEXT,image TEXT,provider TEXT,lessons TEXT DEFAULT '6');
    CREATE TABLE IF NOT EXISTS enrollments(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,course_id INTEGER,progress INTEGER DEFAULT 0,completed INTEGER DEFAULT 0,final_score INTEGER,certificate_code TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id,course_id));
    CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,industry_id INTEGER,title TEXT,description TEXT,skills TEXT,location TEXT,job_type TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT,job_id INTEGER,student_id INTEGER,status TEXT DEFAULT 'Applied',created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(job_id,student_id));
    CREATE TABLE IF NOT EXISTS college_enrollments(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER,student_id INTEGER,course_id INTEGER,mode TEXT,attendance INTEGER DEFAULT 0,test_score INTEGER DEFAULT 0,progress INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS trainers(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER,name TEXT,subject TEXT,email TEXT);
    CREATE TABLE IF NOT EXISTS syllabus(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER,title TEXT,subject TEXT,details TEXT);
    CREATE TABLE IF NOT EXISTS funding(id INTEGER PRIMARY KEY AUTOINCREMENT,ngo_id INTEGER,title TEXT,amount REAL,source TEXT,status TEXT);
    CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,name TEXT,rating INTEGER,comment TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS lessons(id INTEGER PRIMARY KEY AUTOINCREMENT,course_id INTEGER,title TEXT,lecture_no INTEGER,lesson_type TEXT DEFAULT 'Recorded Lecture',video_url TEXT,duration TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS lesson_progress(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,lesson_id INTEGER,completed INTEGER DEFAULT 0,watched_seconds INTEGER DEFAULT 0,completed_at TEXT,UNIQUE(user_id,lesson_id));
    CREATE TABLE IF NOT EXISTS teacher_reports(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER,trainer_id INTEGER,report_date TEXT,course_name TEXT,batch_name TEXT,topic TEXT,attendance INTEGER DEFAULT 0,total_students INTEGER DEFAULT 0,activities TEXT,issues TEXT,next_plan TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS ngo_supports(id INTEGER PRIMARY KEY AUTOINCREMENT,ngo_id INTEGER,title TEXT,support_type TEXT,target TEXT,seats INTEGER DEFAULT 0,location TEXT,status TEXT DEFAULT 'Open',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS ngo_support_applications(id INTEGER PRIMARY KEY AUTOINCREMENT,support_id INTEGER,student_id INTEGER,status TEXT DEFAULT 'Applied',created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(support_id,student_id));
    CREATE TABLE IF NOT EXISTS offline_attendance(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER,student_id INTEGER,course_id INTEGER,attendance_date TEXT,lecture_no INTEGER,topic TEXT,present INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(student_id,course_id,attendance_date,lecture_no));
    CREATE TABLE IF NOT EXISTS offline_schedule(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER,course_id INTEGER,batch_name TEXT,schedule_date TEXT,start_time TEXT,end_time TEXT,teacher_name TEXT,topic TEXT,room TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS course_syllabus(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER,course_id INTEGER,lecture_no INTEGER,topic TEXT,description TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(college_id,course_id,lecture_no));
        ''')
    # Backward-compatible columns for existing databases.
    for table, column, definition in [
        ('industries','verification_status',"TEXT DEFAULT 'Pending'"),
        ('industries','verified',"INTEGER DEFAULT 0"),
        ('industries','license_path',"TEXT DEFAULT ''"),
        ('jobs','approval_status',"TEXT DEFAULT 'Pending'"),
        ('jobs','approved',"INTEGER DEFAULT 0"),
        ('courses','lessons',"TEXT DEFAULT '3'"),
        ('students','resume_path',"TEXT DEFAULT ''"),
        ('jobs','image',"TEXT DEFAULT ''"),
        ('jobs','duration',"TEXT DEFAULT ''"),
        ('jobs','compensation',"TEXT DEFAULT ''"),
        ('jobs','company_name',"TEXT DEFAULT ''"),
        ('jobs','posted_by_role',"TEXT DEFAULT 'industry'"),
        ('jobs','provider_name',"TEXT DEFAULT ''"),
        ('courses','provider_role',"TEXT DEFAULT 'platform'"),
        ('courses','provider_user_id',"INTEGER DEFAULT 0"),
        ('college_enrollments','total_lectures',"INTEGER DEFAULT 18"),
        ('college_enrollments','batch_name',"TEXT DEFAULT 'Batch A'"),
        ('college_enrollments','teacher_name',"TEXT DEFAULT ''")
    ]:
        cols=[r['name'] for r in c.execute(f'PRAGMA table_info({table})').fetchall()]
        if column not in cols:
            c.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
    if c.execute('SELECT COUNT(*) FROM questions').fetchone()[0]==0: seed_questions(c)
    ensure_fifteen_courses(c)
    ensure_extra_questions(c)
    ensure_lessons(c)
    ensure_demo_jobs(c)
    if c.execute('SELECT COUNT(*) FROM feedback').fetchone()[0]==0:
        for n,r,t in [('Ananya','Student','The assessment and course flow is simple and useful.'),('Rahul','College','The dashboard gives a clear view of student progress.'),('Meera','Industry','Skill-based profiles make shortlisting easier.')]:
            c.execute('INSERT INTO feedback(name,rating,comment) VALUES(?,?,?)',(n,5,t))
    con.commit(); con.close()

def seed_questions(cur):
    bank={
    'Java':['Which OOP concept allows a class to acquire properties of another class?','Inheritance','Encapsulation','Abstraction','Compilation','A','Easy','Which keyword is used to create an object in Java?','new','class','this','static','A','Easy','Which collection does not allow duplicate elements?','Set','List','ArrayList','Vector','A','Easy','Which keyword prevents method overriding?','final','super','extends','private','A','Medium','What does JVM stand for?','Java Virtual Machine','Java Variable Method','Joint Virtual Machine','Java Verified Mode','A','Easy','Which method is the entry point of a Java application?','main()','start()','run()','init()','A','Easy','Which feature means one interface, many implementations?','Polymorphism','Inheritance','Compilation','Packaging','A','Medium','Which is a checked exception?','IOException','ArithmeticException','NullPointerException','ArrayIndexOutOfBoundsException','A','Medium','Which keyword refers to the current object?','this','super','self','current','A','Easy','Which access modifier gives widest access?','public','private','protected','default','A','Easy'],
    'Python':['Which symbol starts a Python comment?','#','//','/*','--','A','Easy','Which type is mutable?','list','tuple','string','int','A','Easy','Which keyword defines a function?','def','fun','function','define','A','Easy','What does len() return?','Number of items','Memory size','Data type','Index','A','Easy','Which structure stores key-value pairs?','dict','list','tuple','set','A','Easy','Which statement handles exceptions?','try/except','if/else','for/in','switch','A','Medium','What is indentation used for in Python?','Defining code blocks','Comments','Variables','Imports','A','Easy','Which operator is exponentiation?','**','^','//','%%','A','Easy','Which library is widely used for tabular data?','pandas','pygame','flask','tkinter','A','Easy','Which value represents no value?','None','Null','Empty','Void','A','Easy'],
    'SQL':['Which command retrieves data?','SELECT','GET','FETCHALL','OPEN','A','Easy','Which clause filters rows?','WHERE','ORDER BY','GROUP BY','JOIN','A','Easy','Which command adds a row?','INSERT','ADD','PUT','CREATE','A','Easy','Which clause sorts results?','ORDER BY','SORT','GROUP','ARRANGE','A','Easy','Which key uniquely identifies a row?','Primary key','Foreign key','Candidate text','Index only','A','Easy','Which function counts rows?','COUNT()','SUM()','TOTAL()','ROWS()','A','Easy','Which command changes table structure?','ALTER','CHANGE','MODIFYROW','UPDATE','A','Medium','Which join returns matching rows from both tables?','INNER JOIN','LEFT JOIN','RIGHT JOIN','FULL JOIN','A','Medium','Which command changes existing data?','UPDATE','ALTER','MODIFY','EDIT','A','Easy','Which constraint prevents NULL values?','NOT NULL','NO NULL','REQUIRED','EMPTY FALSE','A','Easy'],
    'Networking':['Which device forwards packets between networks?','Router','Hub','Repeater','Keyboard','A','Easy','What does IP stand for?','Internet Protocol','Internal Process','Internet Port','Input Protocol','A','Easy','Which protocol is used for web pages securely?','HTTPS','FTP','SMTP','TELNET','A','Easy','Which layer handles routing in OSI?','Network','Transport','Session','Physical','A','Medium','What is a MAC address?','Hardware network address','Website address','Port number','Password','A','Easy','Which protocol resolves domain names?','DNS','DHCP','ARP','SSH','A','Easy','Which device broadcasts frames to all ports?','Hub','Router','Switch','Gateway','A','Easy','What does LAN mean?','Local Area Network','Large Access Network','Long Area Node','Local Admin Network','A','Easy','Which protocol assigns IP addresses automatically?','DHCP','DNS','HTTP','ARP','A','Easy','Which protocol is used for remote secure login?','SSH','FTP','SMTP','POP3','A','Medium'],
    'Android':['Which language is commonly used for Android apps?','Java','SQL','HTML only','Bash','A','Easy','Which IDE is official for Android development?','Android Studio','Eclipse only','NetBeans','Notepad','A','Easy','Which file declares Android app components?','AndroidManifest.xml','Main.java','styles.css','config.txt','A','Easy','Which component represents one screen?','Activity','Service','Receiver','Provider','A','Easy','Which layout is flexible for positioning?','ConstraintLayout','PlainLayout','ScreenLayout','BoxOnly','A','Medium','Which file stores string resources?','strings.xml','colors.xml','main.xml','assets.xml','A','Easy','Which component can run background work?','Service','Activity','Intent','View','A','Easy','What is an Intent used for?','Communication between components','Database backup','CSS styling','Compiler setup','A','Medium','Which database is built into Android?','SQLite','Oracle','MongoDB','MySQL server','A','Easy','What is APK?','Android application package','Android process key','Application private key','App protocol kernel','A','Easy'],
    'C':['Which symbol ends a C statement?',';','.',':',',','A','Easy','Which function starts a C program?','main()','start()','run()','begin()','A','Easy','Which format specifier prints an integer?','%d','%f','%c','%s','A','Easy','Which operator gives address?','&','*','%','#','A','Medium','Which loop executes while condition is true?','while','repeat','loop','during','A','Easy','Which header is used for printf?','stdio.h','stdlib.h','string.h','math.h','A','Easy','Which data type stores a character?','char','string','text','byte','A','Easy','Which keyword declares a constant?','const','fixed','constant','final','A','Easy','Which operator is logical AND?','&&','||','!','&','A','Easy'],
    'C++':['Which feature supports classes?','OOP','Markup','Querying','Routing','A','Easy','Which symbol is used for scope resolution?','::','->','=>','..','A','Easy','Which keyword creates an object dynamically?','new','create','malloc only','object','A','Easy','Which concept hides data?','Encapsulation','Compilation','Iteration','Linking','A','Easy','Which function is called when object is created?','Constructor','Destructor','main','friend','A','Medium','Which operator overload is possible?','+','?','::','sizeof only','A','Easy','Which STL container stores ordered dynamic elements?','vector','router','stackview','database','A','Easy','Which keyword supports inheritance?','class syntax with :','extends','inherits','base','A','Medium','Which pointer stores an address?','pointer','reference only','array','object','A','Easy','Which stream is used for output?','cout','cin','cerrin','print','A','Easy'],
    'DBMS':['What is a database?','Organized collection of data','Only a file','Program only','Network cable','A','Easy','What does DBMS stand for?','Database Management System','Data Backup Memory Service','Database Machine Setup','Digital Base Management Software','A','Easy','Which normal form removes repeating groups?','1NF','2NF','3NF','BCNF','A','Medium','Which key references another table?','Foreign key','Primary key','Super key','Unique text','A','Easy','Which command is DDL?','CREATE','SELECT','INSERT','UPDATE','A','Easy','What is a transaction?','Logical unit of work','A table','A key','A report','A','Medium','ACID includes Atomicity and?','Consistency, Isolation, Durability','Control, Index, Data','Connection, Input, Domain','None','A','Medium','Which is a relational database?','MySQL','HTML','CSS','Linux','A','Easy','Which constraint ensures uniqueness?','UNIQUE','ONLY','DISTINCT KEY','ONE','A','Easy','What is indexing used for?','Faster data retrieval','Deleting tables','Encrypting passwords only','Creating users','A','Medium'],
    'Data Analytics':['Which Python library is used for dataframes?','pandas','flask','pygame','requests','A','Easy','What does mean represent?','Average','Middle value','Most frequent','Range','A','Easy','Which chart is good for trends over time?','Line chart','Pie chart only','Radar','Icon','A','Easy','What does CSV stand for?','Comma-Separated Values','Common System Values','Column Sorted View','Computer Stored Variable','A','Easy','Which is a measure of central tendency?','Median','Variance','Range','Standard deviation','A','Medium','What is data cleaning?','Fixing quality issues in data','Deleting all data','Encrypting data','Printing data','A','Easy','Which tool can create interactive charts in web apps?','Chart.js','SQLite','Flask only','Jinja','A','Easy','What is an outlier?','Unusually distant observation','Average row','Duplicate column','Header','A','Medium','Which operation combines tables?','Merge/Join','Compile','Render','Encrypt','A','Medium'],
    'SDLC':['What does SDLC stand for?','Software Development Life Cycle','System Data Link Control','Software Design Logic Code','Secure Development Local Cycle','A','Easy','Which phase gathers requirements?','Requirement analysis','Deployment','Testing','Maintenance','A','Easy','Which phase checks defects?','Testing','Design','Planning','Deployment','A','Easy','What comes after design in many models?','Implementation','Requirement gathering','Retirement','Support only','A','Easy','Which model is iterative?','Agile','Waterfall only','Big Bang only','V model only','A','Medium','What is maintenance?','Changes after release','Initial coding','Only testing','Only design','A','Easy','Who commonly writes code?','Developer','End user only','Auditor only','Client only','A','Easy','What is deployment?','Releasing software','Writing requirements','Drawing UML','Testing locally','A','Easy','What is a requirement?','A needed system capability','A bug only','A database row','A UI color','A','Easy'],
    'HTML/CSS':['Which tag creates a hyperlink?','a','link','href','url','A','Easy','Which tag creates a paragraph?','p','para','text','pg','A','Easy','Which CSS property changes text color?','color','font','text-style','paint','A','Easy','Which selector targets an id?','#id','.id','*id','@id','A','Easy','Which tag inserts an image?','img','image','pic','src','A','Easy','What does CSS stand for?','Cascading Style Sheets','Computer Style Syntax','Creative Sheet System','Color Style Source','A','Easy','Which HTML element is semantic?','header','div','span','box','A','Easy','Which CSS property controls spacing inside an element?','padding','margin-out','space','inside','A','Medium','Which Bootstrap class makes a button?','btn','button','btn-style','control','A','Easy','Which tag is the main heading?','h1','head','title1','heading','A','Easy'],
    'JavaScript':['Which keyword declares a block-scoped variable?','let','varonly','define','dim','A','Easy','Which symbol starts a single-line comment?','//','<!--','##','**','A','Easy','Which method prints to console?','console.log()','print()','echo()','write()','A','Easy','Which type stores true/false?','Boolean','Binary','Bit','LogicOnly','A','Easy','Which operator checks strict equality?','===','==','!=','=>','A','Medium','Which function converts JSON text to object?','JSON.parse()','JSON.convert()','parse.JSON()','toObject()','A','Medium','Which event occurs on button click?','click','press','taponly','button','A','Easy','Which keyword defines a function?','function','def','fun','method','A','Easy','Which array method adds at end?','push()','add()','appendOnly()','insert()','A','Easy','What is DOM?','Document Object Model','Data Object Mode','Document Order Method','Digital Object Map','A','Medium']}
    for subject,arr in bank.items():
        for i in range(0,len(arr),7):
            if i+6>=len(arr): break
            q,a,b,c_opt,d,ans,diff=arr[i:i+7]
            cur.execute('INSERT INTO questions(subject,question,a,b,c,d,answer,difficulty) VALUES(?,?,?,?,?,?,?,?)',(subject,q,a,b,c_opt,d,ans,diff))

def seed_courses(c):
    items=[
    ('Java Fundamentals & OOP','Java','Core Java, OOP and problem solving practice.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=900','MahaSkill'),
    ('SQL & Database Essentials','SQL','Queries, joins, keys, normalization and database practice.','3 Weeks','Online + Offline','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=900','MahaSkill'),
    ('Python for Data Analytics','Python','Python, pandas and practical data analysis basics.','5 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=900','MahaSkill'),
    ('Networking Fundamentals','Networking','IP, OSI, protocols and network troubleshooting.','3 Weeks','Offline','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=900','MahaSkill'),
    ('Android Development with Java','Android','Build Android applications using Java and SQLite.','6 Weeks','Online','Paid',999,'MahaSkill Trainer Team','https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?w=900','MahaSkill'),
    ('Web Development Starter','HTML/CSS','Responsive HTML, CSS and Bootstrap projects.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=900','MahaSkill')]
    c.executemany('INSERT INTO courses(title,subject,description,duration,mode,paid,price,trainer,image,provider) VALUES(?,?,?,?,?,?,?,?,?,?)',items)


COURSE_SEEDS=[
('Java Full Stack Development','Java','Java, OOP, JDBC, Spring Boot, HTML, CSS and SQL with a practical full-stack path.','6 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=900','MahaSkill'),
('SQL & Database Essentials','SQL','Queries, joins, keys, normalization, transactions and database practice.','4 Weeks','Online + Offline','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=900','MahaSkill'),
('Python for Data Analytics','Python','Python fundamentals, pandas, data cleaning and practical analytics.','5 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=900','MahaSkill'),
('Data Engineering Foundations','SQL','ETL concepts, SQL, data pipelines and engineering fundamentals.','6 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900','MahaSkill'),
('Software Development with Python','Python','Programming, functions, OOP, testing and small software projects.','5 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=900','MahaSkill'),
('Web Development Starter','HTML/CSS','HTML, CSS, Bootstrap and responsive web development.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=900','MahaSkill'),
('JavaScript Essentials','JavaScript','JavaScript fundamentals, DOM, events and browser interactions.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=900','MahaSkill'),
('Android Development with Java','Android','Android Studio, Java, activities, layouts and SQLite basics.','6 Weeks','Online','Paid',999,'MahaSkill Trainer Team','https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?w=900','MahaSkill'),
('Networking Fundamentals','Networking','IP addressing, OSI model, protocols and troubleshooting.','3 Weeks','Offline','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=900','MahaSkill'),
('DBMS & Data Modeling','DBMS','ER models, normalization, transactions, indexing and database design.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=900','MahaSkill'),
('C & C++ Programming Basics','C','Programming logic, functions, arrays, pointers and OOP basics.','5 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1518770660439-4636190af475?w=900','MahaSkill'),
('Data Analytics with SQL','Data Analytics','SQL analysis, data preparation, KPIs and dashboard-ready datasets.','5 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900','MahaSkill'),
('SDLC & Software Testing','SDLC','Software development lifecycle, Agile, testing and quality practices.','3 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1553877522-43269d4ea984?w=900','MahaSkill'),
('Career Ready: Resume & Interview','Career Skills','Resume building, communication, interview preparation and workplace readiness.','2 Weeks','Online','Free',0,'MahaSkill Career Team','https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=900','MahaSkill'),
('Problem Solving & Aptitude','Aptitude','Logical reasoning, quantitative aptitude and coding problem-solving practice.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=900','MahaSkill'),
('React & Frontend Development','HTML/CSS','Modern component-based frontend development, responsive UI and React fundamentals.','5 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=900','MahaSkill'),
('Backend APIs with Python Flask','Python','Build REST APIs, forms, authentication and database-backed web applications.','5 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=900','MahaSkill'),
('Java Spring Boot & REST APIs','Java','Create Java backend services, REST APIs and database-connected applications.','6 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=900','MahaSkill'),
('Git & GitHub Essentials','SDLC','Version control, branches, commits, pull requests and team collaboration.','2 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=900','MahaSkill'),
('Cloud Computing Fundamentals','Networking','Cloud concepts, virtual machines, storage, networking and deployment basics.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900','MahaSkill'),
('DevOps & CI/CD Basics','SDLC','CI/CD, automation, deployment pipelines and engineering collaboration.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=900','MahaSkill'),
('Cybersecurity Fundamentals','Networking','Security basics, threats, authentication, safe networking and incident awareness.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=900','MahaSkill'),
('UI/UX for Developers','HTML/CSS','User research, wireframes, usability, responsive layouts and design systems.','3 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1558655146-d09347e92766?w=900','MahaSkill'),
('IoT & Arduino Basics','C','Sensors, Arduino programming, connectivity and beginner IoT projects.','4 Weeks','Offline + Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1553406830-ef2513450d76?w=900','MahaSkill'),
('Data Visualization with Python','Data Analytics','Create charts, dashboards and clear data stories using Python.','4 Weeks','Online','Free',0,'MahaSkill Academy','https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900','MahaSkill'),
('Offline Java Programming Lab','Java','Instructor-led Core Java and OOP practical lab with daily attendance.','6 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=900','MahaSkill'),
('Offline Web Development Bootcamp','HTML/CSS','Classroom HTML, CSS, Bootstrap and responsive web projects.','6 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=900','MahaSkill'),
('Offline Python Development Lab','Python','Classroom Python programming, OOP and practical coding.','6 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=900','MahaSkill'),
('Offline Data Analytics Lab','Data Analytics','Hands-on classroom data cleaning, SQL and dashboard practice.','6 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900','MahaSkill'),
('Offline SQL & DBMS Lab','SQL','Classroom SQL queries, DBMS, normalization and database labs.','5 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=900','MahaSkill'),
('Offline Android Development Lab','Android','Instructor-led Android Studio, Java, layouts and SQLite practice.','7 Weeks','Offline','Paid',999,'MahaSkill Training Centre','https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?w=900','MahaSkill'),
('Offline Networking Lab','Networking','Classroom networking, IP addressing, OSI and troubleshooting labs.','5 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=900','MahaSkill'),
('Offline C & C++ Programming Lab','C','Classroom programming, pointers, arrays and C++ OOP practicals.','6 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1518770660439-4636190af475?w=900','MahaSkill'),
('Offline QA & Software Testing Lab','SDLC','Classroom SDLC, manual testing, test cases and quality practices.','5 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1553877522-43269d4ea984?w=900','MahaSkill'),
('Offline Cloud & DevOps Lab','Networking','Instructor-led cloud, Linux, CI/CD and deployment fundamentals.','6 Weeks','Offline','Free',0,'MahaSkill Training Centre','https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900','MahaSkill')
]
DEMO_VIDEO='https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4'
COURSE_VIDEO_MAP={
'React & Frontend Development':'/static/videos/react_frontend.mp4','Backend APIs with Python Flask':'/static/videos/flask_backend.mp4','Java Spring Boot & REST APIs':'/static/videos/spring_boot.mp4','Git & GitHub Essentials':'/static/videos/git_github.mp4','Cloud Computing Fundamentals':'/static/videos/cloud.mp4','DevOps & CI/CD Basics':'/static/videos/devops.mp4','Cybersecurity Fundamentals':'/static/videos/cybersecurity.mp4','UI/UX for Developers':'/static/videos/uiux.mp4','IoT & Arduino Basics':'/static/videos/iot_arduino.mp4','Data Visualization with Python':'/static/videos/data_visualization.mp4'}

EXTRA_QUESTIONS={
'Java':[('Which keyword is used for inheritance?','extends','implements','inherits','super','A','Easy'),('Which package contains ArrayList?','java.util','java.io','java.net','java.lang.reflect','A','Easy'),('Which concept hides implementation details?','Abstraction','Iteration','Compilation','Casting','A','Easy'),('Which keyword is used to handle exceptions?','try','catchonly','throwonly','error','A','Easy'),('Which type stores whole numbers?','int','double','boolean','char[]','A','Easy')],
'Python':[('Which keyword creates a class?','class','object','struct','typeonly','A','Easy'),('Which method adds an item to a list?','append()','push()','insertEnd()','addItem()','A','Easy'),('Which operator checks equality?','==','=','===','<>','A','Easy'),('Which function reads user input?','input()','read()','scan()','get()','A','Easy'),('Which keyword imports a module?','import','include','using','require','A','Easy')],
'SQL':[('Which clause groups rows?','GROUP BY','GROUP','COLLECT','ROW BY','A','Easy'),('Which command removes rows?','DELETE','DROP ROW','REMOVE','CLEAR','A','Easy'),('Which keyword removes duplicate results?','DISTINCT','UNIQUE ROWS','ONLY','SINGLE','A','Easy'),('Which aggregate returns the largest value?','MAX()','HIGH()','TOP()','LARGE()','A','Easy'),('Which join keeps all left rows?','LEFT JOIN','INNER JOIN','MATCH JOIN','LEFT ONLY','A','Easy')],
'Networking':[('Which protocol transfers web pages?','HTTP','SMTP','SSH','SNMP','A','Easy'),('Which device connects devices in a LAN?','Switch','Router only','Modem only','Firewall only','A','Easy'),('Which address identifies a network interface?','MAC address','URL','DNS name','SSID only','A','Easy'),('Which protocol translates IP to MAC?','ARP','DNS','DHCP','FTP','A','Easy'),('Which topology uses a central device?','Star','Bus','Ring','Mesh only','A','Easy')],
'Android':[('Which component displays a screen?','Activity','Service','Receiver','Provider','A','Easy'),('Which layout arranges views vertically or horizontally?','LinearLayout','DatabaseLayout','ScreenLayout','CodeLayout','A','Easy'),('Which database is commonly embedded in Android?','SQLite','Oracle only','Mongo only','Excel','A','Easy'),('Which file stores UI resources?','res','src-only','db','bin','A','Easy'),('Which tool builds Android projects?','Gradle','JDBC','Maven only','Flask','A','Easy')],
'C':[('Which symbol dereferences a pointer?','*','&','%','@','A','Easy'),('Which header provides string functions?','string.h','stdio.h','math.h','time.h','A','Easy'),('Which operator is logical OR?','||','&&','!','|','A','Easy'),('Which loop runs at least once?','do-while','while','for only','if','A','Easy'),('Which memory function allocates dynamic memory?','malloc()','alloconly()','newC()','create()','A','Easy')],
'C++':[('Which keyword defines a class?','class','structonly','object','define','A','Easy'),('Which stream is used for input?','cin','cout','scanfout','inputstream','A','Easy'),('Which concept allows same function name with different parameters?','Function overloading','Inheritance','Linking','Casting','A','Easy'),('Which symbol accesses members through a pointer?','->','.','::','=>','A','Easy'),('Which keyword prevents a class from being inherited?','final','sealed','private','stop','A','Easy')],
'DBMS':[('Which normal form removes partial dependency?','2NF','1NF','3NF','4NF','A','Medium'),('Which command removes a table?','DROP','DELETE','REMOVE TABLE','CLEAR','A','Easy'),('Which property means all-or-nothing?','Atomicity','Consistency','Isolation','Durability','A','Easy'),('Which object stores a query result definition?','View','Trigger','Index','Cursor','A','Easy'),('Which key can have duplicate values?','Foreign key','Primary key','Candidate key','Super key only','A','Easy')],
'Data Analytics':[('Which metric is the middle value?','Median','Mean','Mode','Range','A','Easy'),('Which chart compares categories?','Bar chart','Line only','Scatter only','Area only','A','Easy'),('What does KPI stand for?','Key Performance Indicator','Key Process Input','Knowledge Performance Index','Known Project Indicator','A','Easy'),('Which step removes duplicate records?','Data cleaning','Modeling','Deployment','Rendering','A','Easy'),('Which analysis describes what happened?','Descriptive analysis','Predictive only','Prescriptive only','Diagnostic only','A','Easy')],
'SDLC':[('Which approach delivers small increments?','Agile','Waterfall','Big Bang','Code-and-fix','A','Easy'),('Which artifact describes requirements?','SRS','CSS','JAR','APK','A','Easy'),('Which testing checks individual units?','Unit testing','System testing','Acceptance testing','Load testing','A','Easy'),('Which phase releases software?','Deployment','Requirement','Design','Analysis','A','Easy'),('Which practice integrates code frequently?','Continuous integration','Manual integration','Late integration','Offline coding','A','Medium')],
'HTML/CSS':[('Which CSS property changes background color?','background-color','bg','back-color','color-bg','A','Easy'),('Which HTML attribute provides alternative image text?','alt','src','titleonly','href','A','Easy'),('Which CSS unit is relative to root font size?','rem','px','cm','pt','A','Easy'),('Which HTML tag creates a list item?','li','ul','list','item','A','Easy'),('Which Bootstrap class creates a responsive container?','container','box','wrap','responsive-box','A','Easy')],
'JavaScript':[('Which method selects an element by id?','getElementById()','selectId()','queryId()','findId()','A','Easy'),('Which keyword creates a constant?','const','constant','final','fixed','A','Easy'),('Which method removes the last array item?','pop()','removeLast()','delete()','shift()','A','Easy'),('Which value means not a number?','NaN','NullNumber','None','Void','A','Easy'),('Which operator is logical AND?','&&','||','!','&','A','Easy')]
}

def add_course_with_lessons(con, title, subject, description, duration, mode, paid, price, trainer, image, provider, provider_role, provider_user_id=0):
    cur=con.execute(
        'INSERT INTO courses(title,subject,description,duration,mode,paid,price,trainer,image,provider,lessons,provider_role,provider_user_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (title,subject,description,duration,mode,paid,price,trainer,image,provider,'3',provider_role,provider_user_id)
    )
    cid=cur.lastrowid
    topics={
        'Java':['Introduction & Setup','OOP and Core Java','Backend / JDBC Practice'],
        'Python':['Python Fundamentals','Data Structures & Functions','Practical Python Project'],
        'SQL':['SQL Basics','Joins & Aggregation','Database Practice'],
        'DBMS':['ER Model & Keys','Normalization','Transactions & Indexing'],
        'HTML/CSS':['HTML Structure','CSS & Bootstrap','Responsive Project'],
        'JavaScript':['JavaScript Basics','DOM & Events','Interactive Web Project'],
        'Networking':['Networking Basics','IP Addressing & Protocols','Troubleshooting Practice'],
        'Data Analytics':['Data Preparation','SQL Analysis','Dashboard Insights'],
        'SDLC':['SDLC Basics','Agile & Testing','Project Delivery'],
        'C':['Programming Basics','Pointers & Arrays','Practical Coding'],
        'C++':['OOP & Classes','STL & Pointers','C++ Practice'],
        'Android':['Android Studio','Layouts & Java','SQLite App Practice'],
    }
    arr=topics.get(subject,['Introduction','Core Concepts','Practical Project'])
    for i,t in enumerate(arr,1):
        con.execute('INSERT INTO lessons(course_id,title,lecture_no,lesson_type,video_url,duration) VALUES(?,?,?,?,?,?)',(cid,t,i,'Recorded Lecture',COURSE_VIDEO_MAP.get(title,DEMO_VIDEO),'05:00'))
    return cid

def ensure_demo_jobs(c):
    roles=[
      ('Java Developer','Java,SQL,DBMS','Pune','Full-time','0-2 years','₹4.0-6.0 LPA','https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=900','Full-time'),
      ('Junior Java Developer','Java,SQL,OOP','Pune','Full-time','0-1 year','₹3.0-4.5 LPA','https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=900','Full-time'),
      ('Java Full-Stack Developer','Java,SQL,HTML/CSS,JavaScript','Pune','Full-time','1-2 years','₹5.0-8.0 LPA','https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=900','Full-time'),
      ('Backend Developer','Java,SQL,REST API','Pune','Full-time','1-2 years','₹4.5-7.0 LPA','https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=900','Full-time'),
      ('Software Developer','Java,Python,SQL,Git','Pune','Full-time','0-2 years','₹4.0-7.0 LPA','https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=900','Full-time'),
      ('Web Developer','HTML/CSS,JavaScript,Bootstrap','Pune','Full-time','0-2 years','₹3.0-5.5 LPA','https://images.unsplash.com/photo-1547658719-da2b51169166?w=900','Full-time'),
      ('Frontend Developer','HTML/CSS,JavaScript,Bootstrap','Pune','Full-time','0-1 year','₹3.5-6.0 LPA','https://images.unsplash.com/photo-1558655146-d09347e92766?w=900','Full-time'),
      ('JavaScript Developer','JavaScript,HTML/CSS,DOM','Pune','Full-time','0-2 years','₹3.5-6.0 LPA','https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=900','Full-time'),
      ('SQL Developer','SQL,DBMS,MySQL','Pune','Full-time','0-2 years','₹3.5-6.0 LPA','https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=900','Full-time'),
      ('Database Developer','SQL,DBMS,Data Modeling','Pune','Full-time','1-2 years','₹4.0-7.0 LPA','https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=900','Full-time'),
      ('Data Analysis','Python,SQL,Data Analytics','Pune','Full-time','0-2 years','₹4.0-7.0 LPA','https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900','Full-time'),
      ('Data Engineering Intern','Python,SQL,ETL','Pune','Internship','3-6 months','₹12,000-20,000/month','https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=900','Internship'),
      ('Junior Data Engineer','Python,SQL,ETL,DBMS','Pune','Full-time','0-2 years','₹4.5-8.0 LPA','https://images.unsplash.com/photo-1551434678-e076c223a692?w=900','Full-time'),
      ('ETL Developer','SQL,ETL,Python,DBMS','Pune','Full-time','1-3 years','₹5.0-9.0 LPA','https://images.unsplash.com/photo-1556761175-b413da4baf72?w=900','Full-time'),
      ('Network Support Engineer','Networking,TCP/IP,Linux','Pune','Full-time','0-2 years','₹3.5-6.0 LPA','https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=900','Full-time'),
      ('Network Technician','Networking,IP,Hardware','Pune','Full-time','0-1 year','₹2.8-4.5 LPA','https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900','Full-time'),
      ('IT Support Engineer','Networking,Windows,Hardware','Pune','Full-time','0-2 years','₹3.0-5.0 LPA','https://images.unsplash.com/photo-1551434678-e076c223a692?w=900','Full-time'),
      ('Technical Support Associate','Networking,Communication,SQL','Pune','Full-time','0-1 year','₹2.8-4.5 LPA','https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=900','Full-time'),
      ('Software Developer Intern','Python,Java,SQL','Pune','Internship','3-6 months','₹10,000-18,000/month','https://images.unsplash.com/photo-1516321165247-4aa89a48be28?w=900','Internship'),
      ('Full-Stack Developer Intern','Java,HTML/CSS,JavaScript,SQL','Pune','Internship','3-6 months','₹12,000-20,000/month','https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=900','Internship'),
      ('Java Developer Intern','Java,SQL,OOP','Pune','Internship','3-6 months','₹10,000-18,000/month','https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=900','Internship'),
      ('Web Developer Intern','HTML/CSS,JavaScript,Bootstrap','Pune','Internship','3-6 months','₹8,000-15,000/month','https://images.unsplash.com/photo-1547658719-da2b51169166?w=900','Internship'),
      ('Data Analyst Intern','Python,SQL,Data Analytics','Pune','Internship','3-6 months','₹10,000-18,000/month','https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900','Internship'),
      ('Database Intern','SQL,DBMS,MySQL','Pune','Internship','3-6 months','₹8,000-15,000/month','https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=900','Internship'),
      ('Network Engineer Intern','Networking,TCP/IP,Linux','Pune','Internship','3-6 months','₹8,000-16,000/month','https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900','Internship')]
    existing={r['title'] for r in c.execute('SELECT title FROM jobs').fetchall()}
    for title,skills,loc,jtype,duration,comp,img,_ in roles:
        if title not in existing:
            c.execute('INSERT INTO jobs(industry_id,title,description,skills,location,job_type,approval_status,approved,image,duration,compensation,company_name) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(0,title,'Demo opportunity for MahaSkill student practice and placement exploration.',skills,loc,jtype,'Approved',1,img,duration,comp,'MahaSkill Demo Partner'))

def ensure_extra_questions(c):

    minimum_questions={
      'HTML/CSS':[
        ('Which tag creates a hyperlink?','<a>','<link>','<href>','<url>','A','Easy'),('Which CSS property changes text color?','color','font-color','text-color','foreground','A','Easy'),('Which HTML tag is used for the largest heading?','<h1>','<h6>','<head>','<title>','A','Easy'),('Which CSS property controls space inside an element?','padding','margin','gap','border','A','Easy'),('Which Bootstrap class creates a primary button?','btn btn-primary','button-primary','primary-btn','btn-blue','A','Easy'),('Which HTML attribute provides alternative text for an image?','alt','src','href','title','A','Easy'),('Which CSS layout system is commonly used for one-dimensional layouts?','Flexbox','Floatbox','Gridline','Position','A','Easy'),('Which tag defines a table row?','<tr>','<td>','<th>','<row>','A','Easy'),('Which CSS property rounds corners?','border-radius','corner-radius','radius','round','A','Easy'),('Which meta tag helps responsive design?','viewport','responsive','screen','device','A','Medium')],
      'JavaScript':[
        ('Which keyword declares a block-scoped variable?','let','var','define','constvar','A','Easy'),('Which method converts JSON text to an object?','JSON.parse()','JSON.object()','JSON.read()','JSON.convert()','A','Easy'),('Which symbol is used for strict equality?','===','==','=','!=','A','Easy'),('Which method selects an element by id?','getElementById()','queryId()','getById()','selectId()','A','Easy'),('Which event occurs when a button is clicked?','click','press','tap','submit-only','A','Easy'),('Which keyword defines a constant?','const','constant','final','fixed','A','Easy'),('Which value represents absence of a value?','null','empty','void','zero','A','Easy'),('Which array method adds an item at the end?','push()','append()','add()','insertEnd()','A','Easy'),('Which operator means logical AND?','&&','||','!','&','A','Easy'),('Which statement is used for conditional execution?','if','when','check','condition','A','Easy')],
      'C++':[
        ('Which feature allows the same function name with different parameters?','Function overloading','Inheritance','Encapsulation','Compilation','A','Easy'),('Which symbol starts a single-line comment in C++?','//','/*','#','--','A','Easy'),('Which keyword creates a class?','class','structonly','object','type','A','Easy'),('Which concept hides implementation details?','Encapsulation','Compilation','Linking','Iteration','A','Medium'),('Which operator accesses a member through an object?','.','-> only','::','=>','A','Easy'),('Which keyword is used for inheritance?','public/protected/private with class inheritance syntax','inherit','extends','base','A','Medium'),('Which is a standard C++ input stream?','cin','input','scan','readln','A','Easy'),('Which is a standard C++ output stream?','cout','print','output','write','A','Easy'),('Which container stores dynamic sequence elements?','vector','arrayfixed','tupleonly','stackonly','A','Easy'),('Which file extension is common for C++ source code?','.cpp','.java','.py','.html','A','Easy')],
      'C':[
        ('Which function prints formatted output in C?','printf()','print()','cout','display()','A','Easy'),('Which symbol ends a C statement?',';','.',':',',','A','Easy'),('Which header is used for printf?','stdio.h','stdlib.h','string.h','math.h','A','Easy'),('Which operator gets the address of a variable?','&','*','@','#','A','Easy'),('Which data type stores a single character?','char','character','string','text','A','Easy'),('Which loop checks the condition before execution?','while','do-while only','repeat','loop','A','Easy'),('Which keyword returns a value from a function?','return','send','yield','back','A','Easy'),('Which collection-like structure stores same-type elements?','array','class','file','pointer','A','Easy'),('Which operator is used to dereference a pointer?','*','&','->','%','A','Easy'),('Which header provides malloc?','stdlib.h','stdio.h','string.h','ctype.h','A','Medium')],
      'Networking':[
        ('Which protocol translates domain names to IP addresses?','DNS','HTTP','FTP','SMTP','A','Easy'),('Which device forwards packets between networks?','Router','Switch','Hub','Repeater','A','Easy'),('Which protocol is connection-oriented?','TCP','UDP','IP','ICMP','A','Easy'),('Which layer handles routing in OSI?','Network','Transport','Session','Physical','A','Easy'),('Which address identifies a network interface at data-link layer?','MAC address','URL','Port','Domain','A','Easy'),('Which command commonly tests reachability?','ping','copy','mkdir','tasklist','A','Easy'),('Which protocol securely transfers web pages?','HTTPS','HTTP','FTP','TELNET','A','Easy'),('What does LAN stand for?','Local Area Network','Large Access Node','Linked Application Network','Local Admin Network','A','Easy'),('Which device connects devices within a LAN?','Switch','Router only','Modem only','Firewall only','A','Easy'),('Which port is commonly used by HTTPS?','443','80','21','25','A','Easy')],
      'Android':[
        ('Which IDE is commonly used for Android development?','Android Studio','Eclipse Web','Visual Studio only','NetBeans only','A','Easy'),('Which file describes app components and permissions?','AndroidManifest.xml','Main.java','config.html','app.json','A','Easy'),('Which component represents a screen?','Activity','Service','Receiver','Provider','A','Easy'),('Which layout arranges children vertically or horizontally?','LinearLayout','TextLayout','ScreenLayout','FlowOnly','A','Easy'),('Which database is commonly embedded in Android apps?','SQLite','MongoDB only','Oracle only','Redis only','A','Easy'),('Which method is called when an Activity is first created?','onCreate()','onStartApp()','create()','initActivity()','A','Easy'),('Which file contains Android UI resources?','res','src-only','bin','server','A','Easy'),('Which class is used to show a short message?','Toast','AlertText','MessageBoxOnly','Notify','A','Easy'),('Which language is supported for Android development?','Java','Java only','Both Java and Kotlin','C only','C','Medium'),('Which component can run background work?','Service','Activity','Layout','IntentOnly','A','Easy')],
      'DBMS':[
        ('What does DBMS stand for?','Database Management System','Data Backup Management Service','Database Machine System','Data Model Service','A','Easy'),('Which key uniquely identifies a row?','Primary key','Foreign key','Candidate value','Index only','A','Easy'),('Which command retrieves data?','SELECT','GET','FETCHROW','READ','A','Easy'),('Which command adds a row?','INSERT','ADDROW','PUT','APPENDDB','A','Easy'),('Which command changes existing data?','UPDATE','CHANGE','MODIFYROW','ALTERDATA','A','Easy'),('Which command removes rows?','DELETE','REMOVE','DROPROW','CLEAR','A','Easy'),('Which normal form removes repeating groups?','1NF','2NF','3NF','BCNF','A','Medium'),('Which constraint enforces unique values?','UNIQUE','DISTINCTONLY','ONLY','SINGLE','A','Easy'),('Which SQL object stores a query result logically?','View','Loop','Cursor only','Trigger only','A','Medium'),('Which property ensures a transaction is all-or-nothing?','Atomicity','Consistency','Isolation','Durability','A','Medium')],
      'Data Analytics':[
        ('Which Python library is widely used for tabular data?','Pandas','Flask','Requests','Tkinter','A','Easy'),('What is data cleaning?','Fixing missing, duplicate or invalid data','Encrypting data','Deleting every row','Printing reports','A','Easy'),('Which chart is useful for trends over time?','Line chart','Pie chart only','Radar only','Table only','A','Easy'),('What does KPI mean?','Key Performance Indicator','Known Process Index','Key Program Input','Kernel Performance Item','A','Easy'),('Which SQL clause filters rows?','WHERE','ORDER','GROUP','HAVINGONLY','A','Easy'),('Which measure represents the middle value?','Median','Mean','Mode','Range','A','Easy'),('Which measure is most affected by extreme values?','Mean','Median','Mode','Count','A','Medium'),('What is an outlier?','An unusually distant observation','A duplicate column','A table key','A missing header','A','Easy'),('Which tool can create interactive charts in a web app?','Chart.js','SQLite','Jinja only','Flask route','A','Easy'),('What is ETL?','Extract, Transform, Load','Evaluate, Test, Learn','Encode, Transfer, Link','Enter, Track, List','A','Easy')],
      'Career Skills':[('What should a resume highlight first?','Relevant skills and experience','Every hobby','Only marks','A long story','A','Easy'),('What is an elevator pitch?','A short professional introduction','A salary slip','A technical report','A job contract','A','Easy'),('Which is useful before an interview?','Research the role and company','Ignore the job description','Skip preparation','Avoid questions','A','Easy'),('Which communication habit is helpful?','Listen actively','Interrupt often','Avoid eye contact','Use unclear language','A','Easy'),('What is a professional email subject?','Clear and specific','Empty','Very long','Random emojis','A','Easy'),('What should you do after an interview?','Send a professional follow-up','Delete the application','Ignore messages','Change your resume every hour','A','Easy'),('Which is a transferable skill?','Problem solving','Only a software version','A database row','A file extension','A','Easy'),('What does teamwork involve?','Coordinating with others','Working without communication','Avoiding responsibility','Ignoring feedback','A','Easy'),('What should a project description include?','Problem, solution and technologies','Only the title','Only a screenshot','Only a logo','A','Easy'),('What is STAR commonly used for?','Answering behavioural interview questions','Database indexing','Network routing','Writing HTML','A','Medium')],
      'Aptitude':[('What is 20% of 100?','20','10','25','50','A','Easy'),('If 2x=10, x is?','5','2','10','20','A','Easy'),('Which number is prime?','13','15','21','27','A','Easy'),('Average of 10 and 20 is?','15','10','20','30','A','Easy'),('A train travels 60 km in 1 hour. Speed is?','60 km/h','30 km/h','120 km/h','1 km/h','A','Easy'),('If a:b=2:3 and a=10, b is?','15','12','20','5','A','Easy'),('Which comes next: 2,4,6,8,?','10','9','12','16','A','Easy'),('A 10% discount on ₹100 gives price?','₹90','₹80','₹95','₹110','A','Easy'),('If today is Monday, after 3 days is?','Thursday','Wednesday','Friday','Sunday','A','Easy'),('Which reasoning method identifies a pattern from examples?','Induction','Compilation','Normalization','Encapsulation','A','Medium')],
      'SDLC':[
        ('What does SDLC stand for?','Software Development Life Cycle','System Data Logic Cycle','Software Design Learning Course','System Development Link Chain','A','Easy'),('Which phase gathers requirements?','Requirement Analysis','Deployment','Maintenance','Testing only','A','Easy'),('Which model is iterative?','Agile','Waterfall only','V-Only','Big Bang only','A','Easy'),('What is testing used for?','Finding defects and verifying behaviour','Writing requirements','Buying hardware','Designing logos','A','Easy'),('What is a sprint in Scrum?','A short development cycle','A database table','A final exam','A deployment server','A','Easy'),('Which document describes expected software behaviour?','Requirements specification','Invoice','Resume','Network map','A','Easy'),('What is maintenance?','Updating and improving released software','Deleting source code','Only testing','Only design','A','Easy'),('What is version control used for?','Tracking code changes','Compressing images','Hosting databases only','Creating passwords','A','Easy'),('What is debugging?','Finding and fixing program errors','Designing UI','Writing a resume','Deploying hardware','A','Easy'),('Which is a common testing type?','Unit testing','User typing','Server painting','Data drawing','A','Easy')]
    }
    for subject, items in minimum_questions.items():
        existing_count=c.execute('SELECT COUNT(*) FROM questions WHERE subject=?',(subject,)).fetchone()[0]
        for q in items[existing_count:]:
            c.execute('INSERT INTO questions(subject,question,a,b,c,d,answer,difficulty) VALUES(?,?,?,?,?,?,?,?)',(subject,)+q)
    for subject, items in EXTRA_QUESTIONS.items():
        existing=c.execute('SELECT question FROM questions WHERE subject=?',(subject,)).fetchall(); seen={r['question'] for r in existing}
        for q in items:
            if q[0] not in seen:
                c.execute('INSERT INTO questions(subject,question,a,b,c,d,answer,difficulty) VALUES(?,?,?,?,?,?,?,?)',(subject,)+q)

def ensure_fifteen_courses(c):
    existing={r['title'] for r in c.execute('SELECT title FROM courses').fetchall()}
    for item in COURSE_SEEDS:
        if item[0] not in existing:
            c.execute('INSERT INTO courses(title,subject,description,duration,mode,paid,price,trainer,image,provider,lessons) VALUES(?,?,?,?,?,?,?,?,?,?,?)',item+('3',))

def ensure_lessons(c):
    # Add three working video lessons per course if missing. The URL is a public demo MP4; replace video_url with licensed course videos for production use.
    courses=c.execute('SELECT id,title,subject FROM courses ORDER BY id').fetchall()
    topics={
      'Java':['Introduction & Setup','OOP and Classes','JDBC / Full Stack Practice'],
      'SQL':['SQL Basics','Joins and Aggregation','Database Practice'],
      'Python':['Python Fundamentals','Data Structures','Pandas & Analysis'],
      'HTML/CSS':['HTML Structure','CSS & Bootstrap','Responsive Project'],
      'JavaScript':['JavaScript Basics','DOM & Events','Interactive Web Project'],
      'Android':['Android Studio & Activities','Layouts & Java','SQLite App Practice'],
      'Networking':['OSI & TCP/IP','IP Addressing','Network Troubleshooting'],
      'DBMS':['ER Model & Keys','Normalization','Transactions & Indexing'],
      'C':['C Programming Basics','Pointers & Arrays','C++ / OOP Concepts'],
      'Data Analytics':['Data Preparation','SQL Analysis','Dashboard Insights'],
      'Career Skills':[('What should a resume highlight first?','Relevant skills and experience','Every hobby','Only marks','A long story','A','Easy'),('What is an elevator pitch?','A short professional introduction','A salary slip','A technical report','A job contract','A','Easy'),('Which is useful before an interview?','Research the role and company','Ignore the job description','Skip preparation','Avoid questions','A','Easy'),('Which communication habit is helpful?','Listen actively','Interrupt often','Avoid eye contact','Use unclear language','A','Easy'),('What is a professional email subject?','Clear and specific','Empty','Very long','Random emojis','A','Easy'),('What should you do after an interview?','Send a professional follow-up','Delete the application','Ignore messages','Change your resume every hour','A','Easy'),('Which is a transferable skill?','Problem solving','Only a software version','A database row','A file extension','A','Easy'),('What does teamwork involve?','Coordinating with others','Working without communication','Avoiding responsibility','Ignoring feedback','A','Easy'),('What should a project description include?','Problem, solution and technologies','Only the title','Only a screenshot','Only a logo','A','Easy'),('What is STAR commonly used for?','Answering behavioural interview questions','Database indexing','Network routing','Writing HTML','A','Medium')],
      'Aptitude':[('What is 20% of 100?','20','10','25','50','A','Easy'),('If 2x=10, x is?','5','2','10','20','A','Easy'),('Which number is prime?','13','15','21','27','A','Easy'),('Average of 10 and 20 is?','15','10','20','30','A','Easy'),('A train travels 60 km in 1 hour. Speed is?','60 km/h','30 km/h','120 km/h','1 km/h','A','Easy'),('If a:b=2:3 and a=10, b is?','15','12','20','5','A','Easy'),('Which comes next: 2,4,6,8,?','10','9','12','16','A','Easy'),('A 10% discount on ₹100 gives price?','₹90','₹80','₹95','₹110','A','Easy'),('If today is Monday, after 3 days is?','Thursday','Wednesday','Friday','Sunday','A','Easy'),('Which reasoning method identifies a pattern from examples?','Induction','Compilation','Normalization','Encapsulation','A','Medium')],
      'SDLC':['SDLC Models','Agile & Scrum','Testing & Quality'],
      'Career Skills':['Resume Essentials','Interview Skills','Workplace Readiness'],
      'Aptitude':['Quantitative Basics','Logical Reasoning','Problem Solving']}
    for course in courses:
        n=c.execute('SELECT COUNT(*) FROM lessons WHERE course_id=?',(course['id'],)).fetchone()[0]
        if n<3:
            arr=topics.get(course['subject'],['Introduction','Core Concepts','Practice'])
            for i,t in enumerate(arr,1):
                c.execute('INSERT INTO lessons(course_id,title,lecture_no,lesson_type,video_url,duration) VALUES(?,?,?,?,?,?)',(course['id'],t,i,'Recorded Lecture',COURSE_VIDEO_MAP.get(course['title'],DEMO_VIDEO),'05:00'))

def course_progress(con, uid, cid):
    total=con.execute('SELECT COUNT(*) FROM lessons WHERE course_id=?',(cid,)).fetchone()[0]
    done=con.execute('SELECT COUNT(*) FROM lesson_progress lp JOIN lessons l ON l.id=lp.lesson_id WHERE lp.user_id=? AND l.course_id=? AND lp.completed=1',(uid,cid)).fetchone()[0]
    return round(done*100/total) if total else 0

def sync_enrollment_progress(con, uid, cid):
    p=course_progress(con,uid,cid)
    e=con.execute('SELECT * FROM enrollments WHERE user_id=? AND course_id=?',(uid,cid)).fetchone()
    if e:
        con.execute('UPDATE enrollments SET progress=?,completed=? WHERE id=?',(p,1 if p>=100 else 0,e['id']))
    return p

def student_recommended_opportunities(con, uid, limit=25):
    st=con.execute('SELECT * FROM students WHERE user_id=?',(uid,)).fetchone()
    if not st: return []
    skills=(st['current_skills'] or '').lower(); domain=(st['domain'] or '').lower(); goal=(st['career_goal'] or '').lower()
    jobs=con.execute("SELECT j.*,i.organization_name FROM jobs j LEFT JOIN industries i ON i.user_id=j.industry_id WHERE (j.approved=1 OR j.industry_id=0) ORDER BY j.id DESC").fetchall()
    out=[]
    for j in jobs:
        req=[x.strip().lower() for x in (j['skills'] or '').split(',') if x.strip()]
        text=' '.join(req)
        hits=sum(1 for x in req if x in skills or x in domain or x in goal)
        if domain and any(k in text for k in domain.split()): hits+=1
        if goal and any(k in text for k in goal.split()): hits+=1
        score=round(100*hits/max(len(req),1))
        out.append((score,j))
    return [j for _,j in sorted(out,key=lambda x:x[0],reverse=True)[:limit]]

def login_required(f):
    @wraps(f)
    def w(*a,**kw):
        if 'user_id' not in session: flash('Please login to continue.','warning'); return redirect(url_for('login'))
        return f(*a,**kw)
    return w

def role_required(role):
    def deco(f):
        @wraps(f)
        @login_required
        def w(*a,**kw):
            if session.get('role')!=role: abort(403)
            return f(*a,**kw)
        return w
    return deco

def student_name():
    if session.get('full_name'): return session['full_name']
    con=db(); u=con.execute('SELECT full_name,username FROM users WHERE id=?',(session.get('user_id'),)).fetchone(); con.close(); return (u['full_name'] or u['username'] or 'Student') if u else 'Student'

def skill_scores(uid):
    con=db(); rows=con.execute('SELECT subject, MAX(percentage) p FROM assessments WHERE user_id=? GROUP BY subject',(uid,)).fetchall(); con.close()
    return {r['subject']:r['p'] for r in rows}

def course_recs(uid):
    con=db(); courses=con.execute('SELECT * FROM courses ORDER BY id').fetchall(); st=con.execute('SELECT * FROM students WHERE user_id=?',(uid,)).fetchone(); scores=skill_scores(uid); con.close()
    if not st: return courses[:6]
    preferred=CAREER_COURSES.get(st['career_goal'],[])
    domain=(st['domain'] or '').lower(); goal=(st['career_goal'] or '').lower(); weak=set(sorted(scores,key=scores.get)[:5]) if scores else set()
    scored=[]
    for c in courses:
        text=(c['title']+' '+c['subject']+' '+c['description']).lower(); score=0
        if c['title'] in preferred: score+=10
        if any(k.strip().lower() in text for k in domain.split() if k.strip()): score+=4
        if any(k.strip().lower() in text for k in goal.split() if k.strip()): score+=4
        if c['subject'] in weak: score+=3
        scored.append((score,c))
    return [c for _,c in sorted(scored,key=lambda x:x[0],reverse=True)[:8]]

@app.context_processor
def inject(): return {'roles':ROLES,'current_role':session.get('role'),'logged':bool(session.get('user_id'))}

@app.route('/')
def index():
    con=db(); stats={'students':con.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0], 'colleges':con.execute("SELECT COUNT(*) FROM users WHERE role='college'").fetchone()[0], 'industries':con.execute("SELECT COUNT(*) FROM users WHERE role='industry'").fetchone()[0], 'courses':con.execute('SELECT COUNT(*) FROM courses').fetchone()[0]}; fb=con.execute('SELECT * FROM feedback ORDER BY id DESC LIMIT 6').fetchall(); con.close(); return render_template('index.html',stats=stats,feedback=fb)

@app.route('/register')
def register(): return render_template('register.html')

def save_user(role,full_name,username,email,mobile,password):
    con=db()
    try:
        username=(username or '').strip(); email=(email or '').strip(); mobile=(mobile or '').strip()
        if not re.fullmatch(r'\d{10}',mobile): return ('mobile_invalid',None)
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email): return ('email_invalid',None)
        if len(password or '')<6: return ('password_short',None)
        if con.execute('SELECT 1 FROM users WHERE lower(username)=lower(?)',(username,)).fetchone(): return ('username_exists',None)
        if con.execute('SELECT 1 FROM users WHERE lower(email)=lower(?)',(email,)).fetchone(): return ('email_exists',None)
        if con.execute('SELECT 1 FROM users WHERE mobile=?',(mobile,)).fetchone(): return ('mobile_exists',None)
        cur=con.execute('INSERT INTO users(role,full_name,username,email,mobile,password) VALUES(?,?,?,?,?,?)',(role,full_name,username,email,mobile,generate_password_hash(password))); uid=cur.lastrowid; con.commit(); return ('ok',uid)
    except sqlite3.IntegrityError:
        con.rollback(); return ('duplicate',None)
    finally: con.close()

def registration_error(status):
    return {'username_exists':'Username already exists. Please choose another username.','email_exists':'Email already registered. Please use another email.','mobile_exists':'Mobile number already registered. Please use another number.','email_invalid':'Please enter a valid email address containing @.','mobile_invalid':'Mobile number must contain exactly 10 digits.','password_short':'Password must be at least 6 characters.','duplicate':'This account information is already registered.'}.get(status,'Please check the entered details.')

def registration_field_error(status):
    msg=registration_error(status)
    field={'username_exists':'username','email_exists':'email','mobile_exists':'mobile','email_invalid':'email','mobile_invalid':'mobile','password_short':'password'}.get(status)
    return ({field:msg} if field else {})

def registration_context(options=None, **extra):
    ctx={'form_values':request.form.to_dict() if request.method=='POST' else {}, 'field_errors':extra.pop('field_errors',{})}
    if options is not None: ctx['options']=options
    ctx.update(extra)
    return ctx

@app.route('/student-register',methods=['GET','POST'])
def student_register():
    if request.method=='POST':
        f=request.form; status,uid=save_user('student',f.get('full_name'),f.get('username'),f.get('email'),f.get('mobile'),f.get('password'))
        if not uid:
            messages={'username_exists':'Username already exists. Please choose another username.','email_exists':'Email already registered. Please use another email.','mobile_exists':'Mobile number already registered. Please use another number.','email_invalid':'Please enter a valid email address containing @.','mobile_invalid':'Mobile number must contain exactly 10 digits.','password_short':'Password must be at least 6 characters.','duplicate':'This account information is already registered.'}
            flash(messages.get(status,'Please check the entered details.'),'danger'); return render_template('student_register.html',college_list=COLLEGE_LIST,domains=DOMAINS,career_goals=CAREER_GOALS,**registration_context(field_errors=registration_field_error(status)))
        con=db(); con.execute('INSERT INTO students(user_id,education,college_name,domain,current_skills,career_goal,location,resume_path) VALUES(?,?,?,?,?,?,?,?)',(uid,f.get('education'),f.get('college_name'),f.get('domain'),f.get('current_skills'),f.get('career_goal'),f.get('location'),'')); con.commit(); con.close(); flash('Registration successful. Please login.','success'); return redirect(url_for('login'))
    return render_template('student_register.html',college_list=COLLEGE_LIST,domains=DOMAINS,career_goals=CAREER_GOALS)

COLLEGE_REGISTER_OPTIONS={'college_name':COLLEGE_LIST,'department':['Computer Engineering','Information Technology','Electronics & Telecommunication','Mechanical Engineering','Civil Engineering','Artificial Intelligence & Data Science','Electronics Engineering','Management'], 'city':['Pune','Pimpri-Chinchwad','Mumbai','Nashik','Nagpur','Solapur','Kolhapur','Satara','Ahmednagar','Other']}

@app.route('/college-register',methods=['GET','POST'])
def college_register():
    if request.method=='POST':
        f=request.form; status,uid=save_user('college',f.get('coordinator'),f.get('username'),f.get('email'),f.get('mobile'),f.get('password'))
        if not uid: flash(registration_error(status),'danger'); return render_template('college_register.html', **registration_context(options=COLLEGE_REGISTER_OPTIONS, field_errors=registration_field_error(status)))
        con=db(); con.execute('INSERT INTO colleges VALUES(?,?,?,?,?,?,?,?,?,?)',(uid,f.get('college_name'),f.get('college_id'),f.get('coordinator'),f.get('email'),f.get('mobile'),f.get('department'),f.get('address'),f.get('city'),f.get('industry_info'))); con.commit(); con.close(); flash('College registered. Please login.','success'); return redirect(url_for('login'))
    return render_template('college_register.html', options=COLLEGE_REGISTER_OPTIONS)

@app.route('/industry-register',methods=['GET','POST'])
def industry_register():
    if request.method=='POST':
        f=request.form; status,uid=save_user('industry',f.get('organization_name'),f.get('username'),f.get('email'),f.get('mobile'),f.get('password'))
        if not uid: flash(registration_error(status),'danger'); return render_template('industry_register.html', **registration_context(field_errors=registration_field_error(status)))
        con=db(); con.execute('INSERT INTO industries(user_id,organization_name,company_id,contact_person,email,mobile,domain,address,city,website) VALUES(?,?,?,?,?,?,?,?,?,?)',(uid,f.get('organization_name'),f.get('company_id'),f.get('contact_person'),f.get('email'),f.get('mobile'),f.get('domain'),f.get('address'),f.get('city'),f.get('website'))); con.commit(); con.close(); flash('Industry registered. Please login.','success'); return redirect(url_for('login'))
    return render_template('industry_register.html')

@app.route('/government-register',methods=['GET','POST'])
def government_register():
    if request.method=='POST':
        f=request.form; status,uid=save_user('government',f.get('officer_name'),f.get('username'),f.get('email'),f.get('mobile'),f.get('password'))
        if not uid: flash(registration_error(status),'danger'); return render_template('government_register.html', **registration_context(field_errors=registration_field_error(status)))
        con=db(); con.execute('INSERT INTO governments VALUES(?,?,?,?,?,?,?,?)',(uid,f.get('department_name'),f.get('officer_name'),f.get('email'),f.get('mobile'),f.get('department_type'),f.get('state_district'),f.get('address'))); con.commit(); con.close(); flash('Government account registered. Please login.','success'); return redirect(url_for('login'))
    return render_template('government_register.html')

@app.route('/ngo-register',methods=['GET','POST'])
def ngo_register():
    if request.method=='POST':
        f=request.form; status,uid=save_user('ngo',f.get('coordinator'),f.get('username'),f.get('email'),f.get('mobile'),f.get('password'))
        if not uid: flash(registration_error(status),'danger'); return render_template('ngo_register.html', **registration_context(field_errors=registration_field_error(status)))
        con=db(); con.execute('INSERT INTO ngos VALUES(?,?,?,?,?,?,?,?,?,?)',(uid,f.get('ngo_name'),f.get('registration_id'),f.get('coordinator'),f.get('email'),f.get('mobile'),f.get('focus_area'),f.get('address'),f.get('city'),f.get('website'))); con.commit(); con.close(); flash('NGO registered. Please login.','success'); return redirect(url_for('login'))
    return render_template('ngo_register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        f=request.form; identity=(f.get('username') or '').strip(); password=f.get('password') or ''
        con=db(); u=con.execute('SELECT * FROM users WHERE lower(username)=lower(?) OR lower(email)=lower(?)',(identity,identity)).fetchone()
        if not u:
            con.close(); flash('Account not found. Please check your username/email or register first.','danger'); return render_template('login.html',login_value=identity)
        if not check_password_hash(u['password'],password):
            con.close(); flash('Incorrect password. Please try again.','danger'); return render_template('login.html',login_value=identity)
        career=''
        if u['role']=='student':
            row=con.execute('SELECT career_goal FROM students WHERE user_id=?',(u['id'],)).fetchone(); career=row['career_goal'] if row else ''
        con.close(); session.clear(); session.update(user_id=u['id'],role=u['role'],full_name=u['full_name'] or u['username'],username=u['username'],career_goal=career)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))
@app.route('/dashboard')
@login_required
def dashboard(): return redirect(url_for(f"{session['role']}_dashboard"))

@app.route('/student-dashboard')
@role_required('student')
def student_dashboard():
    con=db(); user_row=con.execute('SELECT full_name,username FROM users WHERE id=?',(session['user_id'],)).fetchone(); a=con.execute('SELECT * FROM assessments WHERE user_id=? ORDER BY id DESC LIMIT 8',(session['user_id'],)).fetchall(); e=con.execute('SELECT e.*,c.title,c.image,c.subject FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=? ORDER BY e.id DESC',(session['user_id'],)).fetchall();
    for row in e: sync_enrollment_progress(con,session['user_id'],row['course_id'])
    con.commit(); e=con.execute('SELECT e.*,c.title,c.image,c.subject FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=? ORDER BY e.id DESC',(session['user_id'],)).fetchall(); jobs=student_recommended_opportunities(con,session['user_id'],limit=25); st=con.execute('SELECT * FROM students WHERE user_id=?',(session['user_id'],)).fetchone(); certs=con.execute('SELECT COUNT(*) n FROM enrollments WHERE user_id=? AND certificate_code IS NOT NULL',(session['user_id'],)).fetchone()['n']; cert_rows=con.execute('SELECT e.course_id,e.certificate_code,c.title FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=? AND e.certificate_code IS NOT NULL',(session['user_id'],)).fetchall(); offline=con.execute("SELECT ce.*,c.title FROM college_enrollments ce JOIN courses c ON c.id=ce.course_id WHERE ce.student_id=? AND lower(c.mode) LIKE '%offline%' ORDER BY ce.id DESC",(session['user_id'],)).fetchall(); today=__import__('datetime').date.today().isoformat(); tomorrow=con.execute("SELECT os.*,c.title FROM offline_schedule os JOIN courses c ON c.id=os.course_id WHERE os.schedule_date>=? AND (os.course_id IN (SELECT course_id FROM college_enrollments WHERE student_id=?) OR os.college_id=(SELECT col.user_id FROM colleges col JOIN students st ON lower(trim(st.college_name))=lower(trim(col.college_name)) WHERE st.user_id=? LIMIT 1)) ORDER BY os.schedule_date,os.start_time LIMIT 5",(today,session['user_id'],session['user_id'])).fetchall(); scholarships=con.execute("SELECT * FROM ngo_supports WHERE lower(status)='open' AND lower(support_type)='scholarship' ORDER BY id DESC LIMIT 6").fetchall(); con.close(); roadmap=build_roadmap((st['career_goal'] if st else '') or 'Software Developer'); return render_template('student_dashboard.html',assessments=a,enrollments=e,jobs=jobs,student=st,user_display_name=(user_row['full_name'] or user_row['username'] or 'Student'),scores=skill_scores(session['user_id']),certificates=certs,roadmap=roadmap,cert_rows=cert_rows,offline=offline,tomorrow=tomorrow,scholarships=scholarships)

@app.route('/college-dashboard')
@role_required('college')
def college_dashboard():
    con=db(); col=con.execute('SELECT * FROM colleges WHERE user_id=?',(session['user_id'],)).fetchone(); students=con.execute('SELECT u.*,s.* FROM users u JOIN students s ON s.user_id=u.id WHERE lower(trim(s.college_name))=lower(trim(?)) ORDER BY u.id DESC',(col['college_name'],)).fetchall(); trainers=con.execute('SELECT * FROM trainers WHERE college_id=?',(session['user_id'],)).fetchall(); ce=con.execute('SELECT COUNT(*) n FROM college_enrollments WHERE college_id=?',(session['user_id'],)).fetchone()['n'];
    student_ids=[s['user_id'] for s in students]; ids=student_ids or [-1]; ph=','.join('?'*len(ids)); completed=con.execute(f'SELECT COUNT(*) n FROM enrollments WHERE user_id IN ({ph}) AND completed=1',ids).fetchone()['n']; certs=con.execute(f'SELECT COUNT(*) n FROM enrollments WHERE user_id IN ({ph}) AND certificate_code IS NOT NULL',ids).fetchone()['n']; avg=con.execute(f'SELECT AVG(percentage) a FROM assessments WHERE user_id IN ({ph})',ids).fetchone()['a'] or 0;
    skill_rows=con.execute('SELECT subject,AVG(percentage) avg FROM assessments GROUP BY subject ORDER BY avg DESC').fetchall(); skill_data=[{'subject':r['subject'],'avg':round(r['avg'],1)} for r in skill_rows]; employment={'trained':len(student_ids),'completed':completed,'certificates':certs,'avg_score':round(avg,1)};
    con.close(); return render_template('college_dashboard.html',college=col,students=students,trainers=trainers,enroll_count=ce,skill_data=skill_data,employment=employment)

def build_roadmap(goal):
    names=CAREER_COURSES.get(goal) or CAREER_COURSES.get('Software Developer',[])
    labels=['Foundation','Core Skill','Practical Skill','Project Skill','Industry Skill']
    return [(labels[i] if i < len(labels) else 'Career Ready', course, f'Complete {course} to build the skills required for {goal}.') for i,course in enumerate(names[:6])]

@app.route('/career-roadmap')
@role_required('student')
def career_roadmap():
    con=db(); st=con.execute('SELECT * FROM students WHERE user_id=?',(session['user_id'],)).fetchone(); goal=(st['career_goal'] if st else '') or 'Software Developer'; roadmap=build_roadmap(goal); rows=[]
    for i,(step,course,desc) in enumerate(roadmap,1):
        c=con.execute('SELECT * FROM courses WHERE title=? LIMIT 1',(course,)).fetchone(); progress=course_progress(con,session['user_id'],c['id']) if c else 0; rows.append({'step':i,'subject':step,'course':course,'description':desc,'course_id':c['id'] if c else None,'progress':progress})
    con.close(); return render_template('career_roadmap.html',goal=goal,roadmap=rows)

@app.route('/college/reports')
@role_required('college')
def college_reports():
    con=db(); col=con.execute('SELECT * FROM colleges WHERE user_id=?',(session['user_id'],)).fetchone(); reports=con.execute('SELECT tr.*,t.name trainer_name FROM teacher_reports tr LEFT JOIN trainers t ON t.id=tr.trainer_id WHERE tr.college_id=? ORDER BY tr.id DESC LIMIT 50',(session['user_id'],)).fetchall(); students=con.execute('SELECT u.id,u.full_name,s.domain,s.career_goal,s.current_skills FROM users u JOIN students s ON s.user_id=u.id WHERE lower(trim(s.college_name))=lower(trim(?))',(col['college_name'],)).fetchall();
    progress_rows=con.execute('SELECT u.full_name,c.title,e.progress,e.completed FROM college_enrollments ce JOIN users u ON u.id=ce.student_id JOIN courses c ON c.id=ce.course_id LEFT JOIN enrollments e ON e.user_id=ce.student_id AND e.course_id=ce.course_id WHERE ce.college_id=? ORDER BY e.progress DESC',(session['user_id'],)).fetchall(); gaps=con.execute('SELECT subject,ROUND(AVG(percentage),1) avg FROM assessments a JOIN students s ON s.user_id=a.user_id WHERE lower(trim(s.college_name))=lower(trim(?)) GROUP BY subject ORDER BY avg ASC',(col['college_name'],)).fetchall(); feedbacks=con.execute('SELECT f.*,u.full_name FROM feedback f JOIN users u ON u.id=f.user_id LEFT JOIN students s ON s.user_id=u.id WHERE lower(trim(s.college_name))=lower(trim(?)) ORDER BY f.id DESC LIMIT 10',(col['college_name'],)).fetchall(); con.close(); return render_template('college_reports.html',college=col,reports=reports,students=students,progress_rows=progress_rows,gaps=gaps,feedbacks=feedbacks)

@app.route('/college/daily-report',methods=['GET','POST'])
@role_required('college')
def daily_teacher_report():
    con=db(); trainers=con.execute('SELECT * FROM trainers WHERE college_id=? ORDER BY name',(session['user_id'],)).fetchall(); col=con.execute('SELECT * FROM colleges WHERE user_id=?',(session['user_id'],)).fetchone()
    if request.method=='POST':
        f=request.form; teacher=(f.get('teacher_name') or '').strip(); trainer_id=None
        if teacher:
            tr=con.execute('SELECT id FROM trainers WHERE college_id=? AND lower(name)=lower(?)',(session['user_id'],teacher)).fetchone()
            if tr: trainer_id=tr['id']
            else:
                cur=con.execute('INSERT INTO trainers(college_id,name,subject,email) VALUES(?,?,?,?)',(session['user_id'],teacher,f.get('course_name') or 'General','')); trainer_id=cur.lastrowid
        con.execute('INSERT INTO teacher_reports(college_id,trainer_id,report_date,course_name,batch_name,topic,attendance,total_students,activities,issues,next_plan) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(session['user_id'],trainer_id,f.get('report_date'),f.get('course_name'),f.get('batch_name'),f.get('topic'),int(f.get('attendance') or 0),int(f.get('total_students') or 0),f.get('activities'),f.get('issues'),f.get('next_plan'))); con.commit(); con.close(); flash('Daily teacher report submitted successfully.','success'); return redirect(url_for('college_reports'))
    con.close(); return render_template('daily_report.html',trainers=trainers,college=col)

@app.route('/reports')
@role_required('government')
def government_reports():
    con=db(); counts={r:con.execute('SELECT COUNT(*) n FROM users WHERE role=?',(r,)).fetchone()['n'] for r in ROLES}; avg=con.execute('SELECT subject,ROUND(AVG(percentage),1) avg FROM assessments GROUP BY subject ORDER BY avg DESC').fetchall(); courses=con.execute('SELECT c.title,COUNT(e.id) enrollments,ROUND(AVG(e.progress),1) progress FROM courses c LEFT JOIN enrollments e ON e.course_id=c.id GROUP BY c.id ORDER BY enrollments DESC').fetchall(); industry=con.execute('SELECT COUNT(*) total,SUM(CASE WHEN COALESCE(verified,0)=1 THEN 1 ELSE 0 END) verified FROM industries').fetchone(); opp=con.execute('SELECT COUNT(*) total,SUM(CASE WHEN COALESCE(approved,0)=1 OR industry_id=0 THEN 1 ELSE 0 END) approved FROM jobs').fetchone(); apps=con.execute('SELECT COUNT(*) n FROM applications').fetchone()['n']; hired=con.execute("SELECT COUNT(*) n FROM applications WHERE status='Hired'").fetchone()['n']; reports=con.execute('SELECT COUNT(*) n FROM teacher_reports').fetchone()['n']; con.close(); return render_template('government_reports.html',counts=counts,avg=avg,courses=courses,industry=industry,opp=opp,applications=apps,hired=hired,teacher_reports=reports)

@app.route('/industry-dashboard')
@role_required('industry')
def industry_dashboard():
    con=db(); ind=con.execute('SELECT * FROM industries WHERE user_id=?',(session['user_id'],)).fetchone()
    jobs=con.execute('SELECT * FROM jobs WHERE industry_id=? ORDER BY id DESC',(session['user_id'],)).fetchall()
    candidates=con.execute("SELECT u.id,u.full_name,u.email,s.domain,s.career_goal,MAX(a.percentage) score FROM users u JOIN students s ON s.user_id=u.id LEFT JOIN assessments a ON a.user_id=u.id GROUP BY u.id ORDER BY score DESC LIMIT 10").fetchall()
    apps=con.execute('SELECT COUNT(*) n FROM applications a JOIN jobs j ON j.id=a.job_id WHERE j.industry_id=?',(session['user_id'],)).fetchone()['n']
    hired=con.execute("SELECT COUNT(*) n FROM applications a JOIN jobs j ON j.id=a.job_id WHERE j.industry_id=? AND a.status='Hired'",(session['user_id'],)).fetchone()['n']
    verified=bool(ind['verified']) if ind and 'verified' in ind.keys() else False
    license_uploaded=bool(ind['license_path']) if ind and 'license_path' in ind.keys() else False
    con.close(); return render_template('industry_dashboard.html',industry=ind,jobs=jobs,candidates=candidates,applications_count=apps,hired_count=hired,verified=verified,license_uploaded=license_uploaded)

@app.route('/industry/upload-license',methods=['POST'])
@role_required('industry')
def industry_upload_license():
    f=request.files.get('company_license')
    if not f or not f.filename:
        flash('Please upload your company licence first.','warning'); return redirect(url_for('industry_dashboard'))
    if not f.filename.lower().endswith(('.pdf','.png','.jpg','.jpeg')):
        flash('Company licence must be PDF, PNG, JPG or JPEG.','danger'); return redirect(url_for('industry_dashboard'))
    if request.content_length and request.content_length > 6*1024*1024:
        flash('Company licence must be smaller than 6 MB.','danger'); return redirect(url_for('industry_dashboard'))
    filename=f"company_license_{session['user_id']}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_FOLDER,filename))
    con=db(); con.execute("UPDATE industries SET license_path=?,verified=0,verification_status='Pending' WHERE user_id=?",(f'/static/uploads/{filename}',session['user_id'])); con.commit(); con.close()
    flash('Company licence uploaded. Government can now verify your industry.','success'); return redirect(url_for('industry_dashboard'))

@app.route('/government-dashboard')
@role_required('government')
def government_dashboard():
    con=db(); counts={r:con.execute('SELECT COUNT(*) n FROM users WHERE role=?',(r,)).fetchone()['n'] for r in ROLES}; courses=con.execute('SELECT * FROM courses ORDER BY id DESC LIMIT 8').fetchall(); gap_rows=con.execute('SELECT subject,percentage FROM assessments').fetchall();
    if gap_rows:
        df=pd.DataFrame([dict(x) for x in gap_rows]); gaps=[{'subject':k,'avg':round(float(v),1)} for k,v in df.groupby('subject')['percentage'].mean().sort_values().items()]
    else: gaps=[]
    total_students=counts['student']; completed=con.execute("SELECT COUNT(*) n FROM enrollments WHERE completed=1").fetchone()['n']; certs=con.execute("SELECT COUNT(*) n FROM enrollments WHERE certificate_code IS NOT NULL").fetchone()['n']; jobs=con.execute("SELECT COUNT(*) n FROM jobs WHERE approved=1 OR industry_id=0").fetchone()['n']; internships=con.execute("SELECT COUNT(*) n FROM jobs WHERE (approved=1 OR industry_id=0) AND lower(job_type)='internship'").fetchone()['n']; employed=con.execute("SELECT COUNT(*) n FROM applications WHERE status='Hired'").fetchone()['n'];
    outcome=[{'label':'Trained','value':completed},{'label':'Certified','value':certs},{'label':'Jobs/Internships','value':jobs},{'label':'Hired','value':employed}]; verified_industries=con.execute("SELECT COUNT(*) n FROM industries WHERE COALESCE(verified,0)=1").fetchone()['n']; pending_industry_count=con.execute("SELECT COUNT(*) n FROM industries WHERE COALESCE(verified,0)=0").fetchone()['n']; pending_industries=con.execute("SELECT * FROM industries WHERE COALESCE(verified,0)=0 ORDER BY user_id DESC LIMIT 8").fetchall(); pending_jobs=con.execute("SELECT j.*,i.organization_name FROM jobs j LEFT JOIN industries i ON i.user_id=j.industry_id WHERE COALESCE(j.approved,0)=0 AND j.industry_id<>0 ORDER BY j.id DESC LIMIT 8").fetchall();
    con.close(); return render_template('government_dashboard.html',counts=counts,courses=courses,gaps=gaps,total_students=total_students,completed=completed,certs=certs,jobs=jobs,internships=internships,employed=employed,outcome=outcome,pending_industries=pending_industries,pending_jobs=pending_jobs,verified_industries=verified_industries,pending_industry_count=pending_industry_count)

@app.route('/ngo-dashboard')
@role_required('ngo')
def ngo_dashboard():
    con=db(); ngo=con.execute('SELECT * FROM ngos WHERE user_id=?',(session['user_id'],)).fetchone()
    funds=con.execute('SELECT * FROM funding WHERE ngo_id=?',(session['user_id'],)).fetchall()
    courses=con.execute('SELECT * FROM courses WHERE provider=? ORDER BY id DESC',(ngo['ngo_name'],)).fetchall()
    supports=con.execute('SELECT * FROM ngo_supports WHERE ngo_id=? ORDER BY id DESC',(session['user_id'],)).fetchall()
    apps=con.execute("SELECT nsa.*,ns.title,ns.support_type,u.full_name,u.email,s.domain,s.career_goal,s.resume_path FROM ngo_support_applications nsa JOIN ngo_supports ns ON ns.id=nsa.support_id JOIN users u ON u.id=nsa.student_id LEFT JOIN students s ON s.user_id=u.id WHERE ns.ngo_id=? ORDER BY nsa.id DESC",(session['user_id'],)).fetchall()
    scholarship_count=con.execute("SELECT COUNT(*) n FROM ngo_supports WHERE ngo_id=? AND lower(support_type)='scholarship'",(session['user_id'],)).fetchone()['n']
    con.close(); return render_template('ngo_dashboard.html',ngo=ngo,funds=funds,courses=courses,supports=supports,applications=apps,scholarship_count=scholarship_count)

@app.route('/profile')
@login_required
def profile():
    con=db(); u=con.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone(); table={'student':'students','college':'colleges','industry':'industries','government':'governments','ngo':'ngos'}[session['role']]; extra=con.execute(f'SELECT * FROM {table} WHERE user_id=?',(session['user_id'],)).fetchone()
    attendance_summary=[]; profile_schedule=[]; support_apps=[]
    if session['role']=='student':
        attendance_summary=con.execute("""SELECT ce.course_id,c.title,ce.batch_name,ce.attendance,ce.total_lectures,ce.progress,COUNT(oa.id) AS marked_lectures,
            SUM(CASE WHEN oa.present=1 THEN 1 ELSE 0 END) AS present_count
            FROM college_enrollments ce JOIN courses c ON c.id=ce.course_id
            LEFT JOIN offline_attendance oa ON oa.student_id=ce.student_id AND oa.course_id=ce.course_id
            WHERE ce.student_id=? AND lower(c.mode) LIKE '%offline%'
            GROUP BY ce.id ORDER BY ce.id DESC""",(session['user_id'],)).fetchall()
        profile_schedule=con.execute("""SELECT os.*,c.title FROM offline_schedule os JOIN courses c ON c.id=os.course_id
            WHERE os.schedule_date>=? AND EXISTS(
              SELECT 1 FROM college_enrollments ce WHERE ce.student_id=? AND ce.college_id=os.college_id
              AND (ce.course_id=os.course_id OR ce.batch_name=os.batch_name)
            ) ORDER BY os.schedule_date,os.start_time LIMIT 10""",(__import__('datetime').date.today().isoformat(),session['user_id'])).fetchall()
        support_apps=con.execute("SELECT nsa.*,ns.title,ns.support_type FROM ngo_support_applications nsa JOIN ngo_supports ns ON ns.id=nsa.support_id WHERE nsa.student_id=? ORDER BY nsa.id DESC",(session['user_id'],)).fetchall()
    con.close(); return render_template('profile.html',u=u,extra=extra,attendance_summary=attendance_summary,profile_schedule=profile_schedule,support_apps=support_apps)

@app.route('/assessment')
@role_required('student')
def assessment():
    return render_template('assessment.html',tracks=ASSESSMENT_TRACKS)

@app.route('/quiz/<path:subject>')
@role_required('student')
def quiz(subject):
    con=db(); qs=con.execute('SELECT * FROM questions WHERE subject=? ORDER BY RANDOM() LIMIT 10',(subject,)).fetchall(); con.close();
    if len(qs)<10: flash('Question bank needs at least 10 questions for this subject.','warning'); return redirect(url_for('assessment'))
    return render_template('quiz.html',subject=subject,questions=qs)

@app.route('/quiz/<path:subject>/submit',methods=['POST'])
@role_required('student')
def quiz_submit(subject):
    con=db(); qs=con.execute('SELECT * FROM questions WHERE id IN (%s)'%','.join('?'*10),[request.form.get('qid'+str(i)) for i in range(10)]).fetchall() if request.form.get('qid0') else []
    byid={str(q['id']):q for q in qs}; score=0
    for i in range(10):
        q=byid.get(request.form.get('qid'+str(i))); ans=request.form.get('ans'+str(i));
        if q and ans==q['answer']: score+=1
    pct=score*10; con.execute('INSERT INTO assessments(user_id,subject,score,total,percentage) VALUES(?,?,?,?,?)',(session['user_id'],subject,score,10,pct)); con.commit(); con.close(); return render_template('quiz_result.html',subject=subject,score=score,pct=pct,level='Strong' if pct>=75 else ('Moderate' if pct>=50 else 'Needs Improvement'))

@app.route('/courses')
@role_required('student')
def courses():
    con=db(); rows=con.execute('SELECT * FROM courses ORDER BY id DESC').fetchall(); con.close(); return render_template('courses.html',courses=rows,recommended=course_recs(session['user_id']))

@app.route('/course/<int:cid>')
@role_required('student')
def course_detail(cid):
    con=db(); c=con.execute('SELECT * FROM courses WHERE id=?',(cid,)).fetchone(); e=con.execute('SELECT * FROM enrollments WHERE user_id=? AND course_id=?',(session['user_id'],cid)).fetchone(); lessons=con.execute('SELECT * FROM lessons WHERE course_id=? ORDER BY lecture_no',(cid,)).fetchall(); done={r['lesson_id'] for r in con.execute('SELECT lesson_id FROM lesson_progress WHERE user_id=? AND completed=1',(session['user_id'],)).fetchall()}; p=course_progress(con,session['user_id'],cid); con.close(); return render_template('course_detail.html',course=c,enrollment=e,lessons=lessons,done=done,course_progress=p)

@app.route('/course/<int:cid>/enroll',methods=['POST'])
@role_required('student')
def enroll(cid):
    con=db();
    try: con.execute('INSERT INTO enrollments(user_id,course_id) VALUES(?,?)',(session['user_id'],cid)); con.commit(); flash('Course enrolled successfully. Start your first lecture!','success')
    except sqlite3.IntegrityError: flash('You are already enrolled.','info')
    con.close(); return redirect(url_for('course_detail',cid=cid))

@app.route('/course/<int:cid>/learn',methods=['POST'])
@role_required('student')
def learn(cid):
    con=db(); e=con.execute('SELECT * FROM enrollments WHERE user_id=? AND course_id=?',(session['user_id'],cid)).fetchone();
    if not e: con.close(); return redirect(url_for('course_detail',cid=cid))
    lesson=con.execute('SELECT * FROM lessons WHERE course_id=? ORDER BY lecture_no',(cid,)).fetchone();
    if lesson:
        con.execute('INSERT OR REPLACE INTO lesson_progress(user_id,lesson_id,completed,watched_seconds,completed_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP)',(session['user_id'],lesson['id'],1,0))
    sync_enrollment_progress(con,session['user_id'],cid); con.commit(); con.close(); flash('Lesson completed. Progress updated.','success'); return redirect(url_for('course_detail',cid=cid))

@app.route('/lesson/<int:lid>/complete',methods=['POST'])
@role_required('student')
def lesson_complete(lid):
    con=db(); lesson=con.execute('SELECT * FROM lessons WHERE id=?',(lid,)).fetchone();
    if not lesson: abort(404)
    e=con.execute('SELECT * FROM enrollments WHERE user_id=? AND course_id=?',(session['user_id'],lesson['course_id'])).fetchone();
    if not e: con.close(); return {'ok':False,'message':'Enroll first'},403
    con.execute('INSERT OR REPLACE INTO lesson_progress(user_id,lesson_id,completed,watched_seconds,completed_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP)',(session['user_id'],lid,1,0)); p=sync_enrollment_progress(con,session['user_id'],lesson['course_id']); con.commit(); con.close(); return {'ok':True,'progress':p,'completed':p>=100}

@app.route('/course/<int:cid>/final-test')
@role_required('student')
def final_test(cid):
    con=db(); c=con.execute('SELECT * FROM courses WHERE id=?',(cid,)).fetchone(); e=con.execute('SELECT * FROM enrollments WHERE user_id=? AND course_id=?',(session['user_id'],cid)).fetchone(); p=course_progress(con,session['user_id'],cid); qs=con.execute('SELECT * FROM questions WHERE subject=? ORDER BY RANDOM() LIMIT 10',(c['subject'],)).fetchall(); con.close();
    if not e or p<100: flash('Complete all course lectures before taking the final assessment.','warning'); return redirect(url_for('course_detail',cid=cid))
    if len(qs)<10: flash('Final assessment is not available for this subject yet.','warning'); return redirect(url_for('course_detail',cid=cid))
    return render_template('final_test.html',course=c,questions=qs)

@app.route('/course/<int:cid>/final-test',methods=['POST'])
@role_required('student')
def final_submit(cid):
    con=db(); c=con.execute('SELECT * FROM courses WHERE id=?',(cid,)).fetchone(); ids=[request.form.get('qid'+str(i)) for i in range(10)]; qs=con.execute('SELECT * FROM questions WHERE id IN (%s)'%','.join('?'*10),ids).fetchall(); byid={str(q['id']):q for q in qs}; score=sum(1 for i in range(10) if byid.get(request.form.get('qid'+str(i))) and request.form.get('ans'+str(i))==byid.get(request.form.get('qid'+str(i)))['answer']); e=con.execute('SELECT * FROM enrollments WHERE user_id=? AND course_id=?',(session['user_id'],cid)).fetchone(); p=course_progress(con,session['user_id'],cid); passed=(score>=9 and p>=100); code=f'MS-{session["user_id"]}-{cid}-{score*10}-{random.randint(100,999)}'; con.execute('UPDATE enrollments SET final_score=?,completed=?,progress=?,certificate_code=? WHERE id=?',(score,1 if p>=100 else e['completed'],p,code if passed else None,e['id'])); con.commit(); con.close(); return render_template('final_result.html',course=c,score=score,pct=score*10,passed=passed,code=code)

@app.route('/certificate/<int:cid>')
@role_required('student')
def certificate(cid):
    con=db(); e=con.execute('SELECT e.*,c.title,c.subject FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=? AND e.course_id=?',(session['user_id'],cid)).fetchone(); con.close();
    if not e or not e['certificate_code']: abort(404)
    return render_template('certificate.html',name=student_name(),e=e)

@app.route('/my-certificates')
@role_required('student')
def my_certificates():
    con=db(); rows=con.execute('SELECT e.course_id,e.certificate_code,e.final_score,c.title,c.subject FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=? AND e.certificate_code IS NOT NULL ORDER BY e.id DESC',(session['user_id'],)).fetchall(); con.close(); return render_template('certificates.html',certificates=rows)

@app.route('/jobs')
@role_required('student')
def jobs():
    con=db(); rows=student_recommended_opportunities(con,session['user_id']); applied={r['job_id'] for r in con.execute('SELECT job_id FROM applications WHERE student_id=?',(session['user_id'],)).fetchall()}; st=con.execute('SELECT resume_path FROM students WHERE user_id=?',(session['user_id'],)).fetchone(); has_resume=bool(st and st['resume_path']); rows=[dict(r,applied=(r['id'] in applied),has_resume=has_resume) for r in rows]; scores=skill_scores(session['user_id']); con.close(); return render_template('jobs.html',jobs=rows,scores=scores)

@app.route('/jobs/<int:jid>/apply',methods=['POST'])
@role_required('student')
def apply(jid):
    con=db(); job=con.execute('SELECT j.*,i.organization_name FROM jobs j LEFT JOIN industries i ON i.user_id=j.industry_id WHERE j.id=? AND (j.approved=1 OR j.industry_id=0)',(jid,)).fetchone()
    u=con.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone(); st=con.execute('SELECT * FROM students WHERE user_id=?',(session['user_id'],)).fetchone(); assessments=con.execute('SELECT subject,MAX(percentage) percentage FROM assessments WHERE user_id=? GROUP BY subject',(session['user_id'],)).fetchall()
    if not job:
        con.close(); return render_template('application_profile.html',job=None,student=st,user=u,assessments=assessments,already=False,message='This opportunity is not available for applications yet.')
    if not (st and st['resume_path']):
        con.close(); return render_template('application_profile.html',job=job,student=st,user=u,assessments=assessments,already=False,message='Please upload your resume before applying to this job or internship.',resume_required=True)
    already=bool(con.execute('SELECT 1 FROM applications WHERE job_id=? AND student_id=?',(jid,session['user_id'])).fetchone())
    if not already:
        con.execute('INSERT INTO applications(job_id,student_id) VALUES(?,?)',(jid,session['user_id'])); con.commit()
    con.close()
    return render_template('application_profile.html',job=job,student=st,user=u,assessments=assessments,already=already,message=('You have already applied to this opportunity.' if already else 'Application submitted successfully. Connect with us — we will inform you soon.'),resume_required=False)

@app.route('/my-applications')
@role_required('student')
def my_applications():
    con=db(); rows=con.execute('SELECT a.*,j.title,j.location,j.job_type,j.compensation,j.company_name FROM applications a JOIN jobs j ON j.id=a.job_id WHERE a.student_id=? ORDER BY a.id DESC',(session['user_id'],)).fetchall(); con.close(); return render_template('applications.html',applications=rows)

@app.route('/post-job',methods=['GET','POST'])
@role_required('industry')
def post_job():
    con=db(); ind=con.execute('SELECT * FROM industries WHERE user_id=?',(session['user_id'],)).fetchone();
    if not ind or not ind['verified']:
        con.close(); flash('Industry verification is required before posting a job or internship.','warning'); return redirect(url_for('industry_dashboard'))
    if request.method=='POST':
        f=request.form; con.execute('INSERT INTO jobs(industry_id,title,description,skills,location,job_type,approval_status,approved,image,duration,compensation,company_name,posted_by_role,provider_name) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(session['user_id'],f['title'],f['description'],f['skills'],f['location'],f['job_type'],'Pending',0,f.get('image',''),f.get('duration',''),f.get('compensation',''),ind['organization_name'],'industry',ind['organization_name'])); con.commit(); con.close(); flash('Opportunity submitted for verification.','success'); return redirect(url_for('industry_dashboard'))
    con.close(); return render_template('post_job.html')

@app.route('/industry/candidates')
@role_required('industry')
def industry_candidates():
    con=db()
    ind=con.execute('SELECT * FROM industries WHERE user_id=?',(session['user_id'],)).fetchone()
    rows=con.execute("SELECT u.id,u.full_name,u.email,s.domain,s.career_goal,s.current_skills,s.location,MAX(a.percentage) AS score FROM users u JOIN students s ON s.user_id=u.id LEFT JOIN assessments a ON a.user_id=u.id GROUP BY u.id ORDER BY COALESCE(score,0) DESC,u.full_name LIMIT 30").fetchall()
    domain=(ind['domain'] or '').lower() if ind else ''
    jobs=con.execute('SELECT skills,title FROM jobs WHERE industry_id=?',(session['user_id'],)).fetchall()
    skill_text=' '.join((r['skills'] or '') for r in jobs).lower()
    candidates=[]
    for r in rows:
        text=' '.join([r['domain'] or '',r['career_goal'] or '',r['current_skills'] or '']).lower()
        match=0
        if domain and domain in text: match+=35
        if skill_text:
            wanted=[x.strip() for x in skill_text.replace(';',',').split(',') if x.strip()]
            hits=sum(1 for x in wanted if x in text)
            match += min(45,hits*9)
        match += min(20,float(r['score'] or 0)*0.20)
        candidates.append(dict(r,match_score=min(100,round(match))))
    candidates.sort(key=lambda x:(x['match_score'],float(x['score'] or 0)),reverse=True)
    con.close()
    return render_template('industry_candidates.html',industry=ind,candidates=candidates)

@app.route('/industry/candidate/<int:uid>')
@role_required('industry')
def industry_candidate(uid):
    con=db()
    user=con.execute("SELECT * FROM users WHERE id=? AND role='student'",(uid,)).fetchone()
    student=con.execute('SELECT * FROM students WHERE user_id=?',(uid,)).fetchone() if user else None
    assessments=con.execute('SELECT subject,MAX(percentage) percentage FROM assessments WHERE user_id=? GROUP BY subject ORDER BY percentage DESC',(uid,)).fetchall() if user else []
    courses=con.execute('SELECT c.title,e.progress,e.completed FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=? ORDER BY e.id DESC',(uid,)).fetchall() if user else []
    if not user or not student:
        con.close(); abort(404)
    con.close()
    return render_template('industry_candidate.html',user=user,student=student,assessments=assessments,courses=courses)

@app.route('/industry/hiring',methods=['GET','POST'])
@role_required('industry')
def industry_hiring():
    con=db()
    if request.method=='POST':
        aid=int(request.form.get('application_id'))
        status=request.form.get('status','Applied')
        con.execute('UPDATE applications SET status=? WHERE id=? AND job_id IN (SELECT id FROM jobs WHERE industry_id=?)',(status,aid,session['user_id']))
        con.commit(); flash('Hiring pipeline updated.','success')
    rows=con.execute('SELECT a.*,j.title,j.job_type,u.full_name,u.email,s.domain,s.career_goal,s.current_skills,s.resume_path FROM applications a JOIN jobs j ON j.id=a.job_id JOIN users u ON u.id=a.student_id JOIN students s ON s.user_id=u.id WHERE j.industry_id=? ORDER BY a.id DESC',(session['user_id'],)).fetchall()
    counts={status:con.execute('SELECT COUNT(*) n FROM applications a JOIN jobs j ON j.id=a.job_id WHERE j.industry_id=? AND a.status=?',(session['user_id'],status)).fetchone()['n'] for status in ['Applied','Shortlisted','Interview Scheduled','Hired','Rejected']}
    con.close()
    return render_template('industry_hiring.html',applications=rows,counts=counts)

@app.route('/industry/applications',methods=['GET','POST'])
@role_required('industry')
def industry_applications():
    con=db()
    if request.method=='POST':
        aid=int(request.form.get('application_id')); status=request.form.get('status','Applied')
        con.execute('UPDATE applications SET status=? WHERE id=? AND job_id IN (SELECT id FROM jobs WHERE industry_id=?)',(status,aid,session['user_id'])); con.commit(); flash('Application status updated.','success')
    rows=con.execute('SELECT a.*,j.title,u.full_name,u.email,s.domain,s.career_goal,s.current_skills,s.resume_path FROM applications a JOIN jobs j ON j.id=a.job_id JOIN users u ON u.id=a.student_id JOIN students s ON s.user_id=u.id WHERE j.industry_id=? ORDER BY a.id DESC',(session['user_id'],)).fetchall(); con.close(); return render_template('industry_applications.html',applications=rows)

@app.route('/government/verify-industry/<int:uid>',methods=['POST'])
@role_required('government')
def verify_industry(uid):
    con=db(); ind=con.execute('SELECT * FROM industries WHERE user_id=?',(uid,)).fetchone()
    if not ind:
        con.close(); flash('Industry record not found.','danger'); return redirect(url_for('government_dashboard'))
    if not ind['license_path']:
        con.close(); flash('Verification cannot be completed until the company licence is uploaded.','warning'); return redirect(url_for('government_dashboard'))
    con.execute("UPDATE industries SET verified=1,verification_status='Verified' WHERE user_id=?",(uid,)); con.commit(); con.close()
    flash('Industry verified successfully. It can now submit jobs, internships and courses.','success'); return redirect(url_for('government_dashboard'))

@app.route('/government/approve-job/<int:jid>',methods=['POST'])
@role_required('government')
def approve_job(jid):
    con=db(); con.execute("UPDATE jobs SET approved=1,approval_status='Approved' WHERE id=?",(jid,)); con.commit(); con.close(); flash('Opportunity approved and published.','success'); return redirect(url_for('government_dashboard'))

@app.route('/government/courses',methods=['GET','POST'])
@role_required('government')
def gov_courses():
    if request.method=='POST':
        f=request.form; con=db()
        add_course_with_lessons(con,f['title'],f['subject'],f['description'],f['duration'],f['mode'],'Free',0,f['trainer'],f.get('image',''),session.get('full_name') or 'Government Skill Initiative','government',session['user_id'])
        con.commit(); con.close(); flash('Government course published and added to the Courses catalog.','success'); return redirect(url_for('gov_courses'))
    con=db(); rows=con.execute("SELECT * FROM courses WHERE provider_role='government' AND provider_user_id=? ORDER BY id DESC",(session['user_id'],)).fetchall(); con.close(); return render_template('gov_courses.html',courses=rows,provider_label=session.get('full_name') or 'Government Skill Initiative')

@app.route('/industry/courses',methods=['GET','POST'])
@role_required('industry')
def industry_courses():
    con=db(); ind=con.execute('SELECT * FROM industries WHERE user_id=?',(session['user_id'],)).fetchone()
    if not ind or not ind['verified']:
        con.close(); flash('Industry verification is required before publishing a course.','warning'); return redirect(url_for('industry_dashboard'))
    if request.method=='POST':
        f=request.form
        add_course_with_lessons(con,f['title'],f['subject'],f['description'],f['duration'],f['mode'],f.get('paid','Free'),float(f.get('price') or 0),f['trainer'],f.get('image',''),ind['organization_name'],'industry',session['user_id'])
        con.commit(); con.close(); flash('Industry course published and added to the Courses catalog.','success'); return redirect(url_for('industry_courses'))
    rows=con.execute("SELECT * FROM courses WHERE provider_role='industry' AND provider_user_id=? ORDER BY id DESC",(session['user_id'],)).fetchall(); con.close(); return render_template('partner_courses.html',role_label='Industry',heading='Publish Industry Course',provider=ind['organization_name'],courses=rows,route_name='industry_courses')

@app.route('/ngo/courses',methods=['GET','POST'])
@role_required('ngo')
def ngo_courses():
    con=db(); ngo=con.execute('SELECT * FROM ngos WHERE user_id=?',(session['user_id'],)).fetchone()
    if request.method=='POST':
        f=request.form
        add_course_with_lessons(con,f['title'],f['subject'],f['description'],f['duration'],f['mode'],'Free',0,f['trainer'],f.get('image',''),ngo['ngo_name'],'ngo',session['user_id'])
        con.commit(); con.close(); flash('NGO course published and added to the Courses catalog.','success'); return redirect(url_for('ngo_courses'))
    rows=con.execute("SELECT * FROM courses WHERE provider_role='ngo' AND provider_user_id=? ORDER BY id DESC",(session['user_id'],)).fetchall(); con.close(); return render_template('partner_courses.html',role_label='Social NGO',heading='Publish NGO Course',provider=ngo['ngo_name'],courses=rows,route_name='ngo_courses')

@app.route('/publish-opportunity',methods=['GET','POST'])
@role_required('government')
def publish_opportunity():
    # Government opportunities are published directly as verified portal opportunities.
    if request.method=='POST':
        f=request.form; con=db(); name=session.get('full_name') or 'Government Opportunity'
        con.execute("INSERT INTO jobs(industry_id,title,description,skills,location,job_type,approval_status,approved,image,duration,compensation,company_name,posted_by_role,provider_name) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(0,f['title'],f['description'],f['skills'],f['location'],f['job_type'],'Approved',1,f.get('image',''),f.get('duration',''),f.get('compensation',''),name,'government',name)); con.commit(); con.close(); flash('Government job/internship published in Jobs & Internships.','success'); return redirect(url_for('government_dashboard'))
    return render_template('partner_opportunity.html',role_label='Government',heading='Publish Government Job / Internship',provider=session.get('full_name') or 'Government')

@app.route('/ngo/publish-opportunity',methods=['GET','POST'])
@role_required('ngo')
def ngo_publish_opportunity():
    con=db(); ngo=con.execute('SELECT * FROM ngos WHERE user_id=?',(session['user_id'],)).fetchone()
    if request.method=='POST':
        f=request.form; name=ngo['ngo_name']
        con.execute("INSERT INTO jobs(industry_id,title,description,skills,location,job_type,approval_status,approved,image,duration,compensation,company_name,posted_by_role,provider_name) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(0,f['title'],f['description'],f['skills'],f['location'],f['job_type'],'Approved',1,f.get('image',''),f.get('duration',''),f.get('compensation',''),name,'ngo',name)); con.commit(); con.close(); flash('NGO job/internship published in Jobs & Internships.','success'); return redirect(url_for('ngo_dashboard'))
    con.close(); return render_template('partner_opportunity.html',role_label='Social NGO',heading='Publish NGO Job / Internship',provider=ngo['ngo_name'])

@app.route('/college/manage',methods=['GET','POST'])
@role_required('college')
def college_manage():
    con=db(); col=con.execute('SELECT * FROM colleges WHERE user_id=?',(session['user_id'],)).fetchone()
    if request.method=='POST':
        f=request.form; con.execute('INSERT INTO trainers(college_id,name,subject,email) VALUES(?,?,?,?)',(session['user_id'],f['name'],f['subject'],f['email'])); con.commit(); flash('Trainer added.','success')
    students=con.execute('SELECT u.id,u.full_name,u.email,s.domain,s.career_goal FROM users u JOIN students s ON s.user_id=u.id WHERE s.college_name=?',(col['college_name'],)).fetchall(); trainers=con.execute('SELECT * FROM trainers WHERE college_id=?',(session['user_id'],)).fetchall(); con.close(); return render_template('college_manage.html',students=students,trainers=trainers)

@app.route('/ngo/support/<int:support_id>/apply',methods=['POST'])
@role_required('student')
def apply_ngo_support(support_id):
    con=db(); row=con.execute("SELECT * FROM ngo_supports WHERE id=? AND lower(status)='open'",(support_id,)).fetchone()
    if not row:
        con.close(); flash('This NGO support program is not currently open.','warning'); return redirect(url_for('jobs'))
    try:
        con.execute('INSERT INTO ngo_support_applications(support_id,student_id,status) VALUES(?,?,?)',(support_id,session['user_id'],'Applied')); con.commit(); flash('Support application submitted successfully.','success')
    except sqlite3.IntegrityError:
        flash('You have already applied for this support program.','warning')
    con.close(); return redirect(url_for('profile'))

@app.route('/ngo/supports',methods=['GET','POST'])
@role_required('ngo')
def ngo_supports():
    con=db()
    if request.method=='POST':
        if request.form.get('action')=='status':
            con.execute('UPDATE ngo_support_applications SET status=? WHERE id=? AND support_id IN (SELECT id FROM ngo_supports WHERE ngo_id=?)',(request.form.get('status','Applied'),int(request.form.get('application_id')),session['user_id'])); con.commit(); flash('Support application status updated.','success')
        else:
            f=request.form; con.execute('INSERT INTO ngo_supports(ngo_id,title,support_type,target,seats,location,status) VALUES(?,?,?,?,?,?,?)',(session['user_id'],f.get('title'),f.get('support_type'),f.get('target'),int(f.get('seats') or 0),f.get('location'),f.get('status') or 'Open')); con.commit(); flash('Support program published.','success')
    rows=con.execute('SELECT * FROM ngo_supports WHERE ngo_id=? ORDER BY id DESC',(session['user_id'],)).fetchall()
    apps=con.execute("SELECT nsa.*,ns.title,u.full_name,u.email,s.domain,s.career_goal FROM ngo_support_applications nsa JOIN ngo_supports ns ON ns.id=nsa.support_id JOIN users u ON u.id=nsa.student_id LEFT JOIN students s ON s.user_id=u.id WHERE ns.ngo_id=? ORDER BY nsa.id DESC",(session['user_id'],)).fetchall()
    con.close(); return render_template('ngo_supports.html',supports=rows,applications=apps)

@app.route('/ngo/manage',methods=['GET','POST'])
@role_required('ngo')
def ngo_manage():
    if request.method=='POST':
        f=request.form; con=db(); con.execute('INSERT INTO funding(ngo_id,title,amount,source,status) VALUES(?,?,?,?,?)',(session['user_id'],f['title'],f['amount'],f['source'],f['status'])); con.commit(); flash('Funding record added.','success')
    con=db(); funds=con.execute('SELECT * FROM funding WHERE ngo_id=?',(session['user_id'],)).fetchall(); con.close(); return render_template('ngo_manage.html',funds=funds)

@app.route('/feedback',methods=['POST'])
@login_required
def feedback():
    f=request.form; con=db(); con.execute('INSERT INTO feedback(user_id,name,rating,comment) VALUES(?,?,?,?)',(session['user_id'],student_name(),int(f['rating']),f['comment'])); con.commit(); con.close(); flash('Thank you for your feedback!','success'); return redirect(request.referrer or url_for('index'))


@app.route('/profile/resume',methods=['POST'])
@role_required('student')
def upload_resume():
    f=request.files.get('resume')
    if not f or not f.filename: flash('Please choose a resume file.','warning'); return redirect(url_for('profile'))
    if not f.filename.lower().endswith(('.pdf','.doc','.docx')): flash('Resume must be PDF, DOC or DOCX.','danger'); return redirect(url_for('profile'))
    name=f"student_{session['user_id']}_{secure_filename(f.filename)}"; path=os.path.join(UPLOAD_FOLDER,name); f.save(path)
    con=db(); con.execute('UPDATE students SET resume_path=? WHERE user_id=?',(f'/static/uploads/{name}',session['user_id'])); con.commit(); con.close(); flash('Resume uploaded successfully.','success'); return redirect(url_for('profile'))

@app.route('/college/enrollments',methods=['GET','POST'])
@role_required('college')
def college_enrollments():
    con=db(); col=con.execute('SELECT * FROM colleges WHERE user_id=?',(session['user_id'],)).fetchone()
    students=con.execute('SELECT u.id,u.full_name,s.domain,s.career_goal FROM users u JOIN students s ON s.user_id=u.id WHERE lower(trim(s.college_name))=lower(trim(?))',(col['college_name'],)).fetchall()
    courses=con.execute("SELECT id,title,mode FROM courses WHERE lower(mode) LIKE '%offline%' ORDER BY title").fetchall()
    if request.method=='POST':
        action=request.form.get('action')
        try:
            cid=int(request.form.get('course_id'))
            sid=int(request.form.get('student_id')) if request.form.get('student_id') else None
            if action=='link':
                if not sid:
                    raise ValueError('Student is required for enrollment.')
                mode='Offline'; total=max(1,int(request.form.get('total_lectures') or 18)); batch=request.form.get('batch_name') or 'Batch A'; teacher=request.form.get('teacher_name') or ''
                con.execute('INSERT OR IGNORE INTO college_enrollments(college_id,student_id,course_id,mode,total_lectures,batch_name,teacher_name) VALUES(?,?,?,?,?,?,?)',(session['user_id'],sid,cid,mode,total,batch,teacher))
                con.execute('UPDATE college_enrollments SET total_lectures=?,batch_name=?,teacher_name=? WHERE college_id=? AND student_id=? AND course_id=?',(total,batch,teacher,session['user_id'],sid,cid))
                flash('Student linked to offline course.','success')
            elif action=='attendance':
                if not sid:
                    raise ValueError('Student is required for attendance.')
                date=request.form.get('attendance_date') or __import__('datetime').date.today().isoformat(); lecture=max(1,int(request.form.get('lecture_no') or 1)); present=1 if request.form.get('present')=='1' else 0; topic=request.form.get('topic') or 'Classroom Lecture'
                con.execute('INSERT OR REPLACE INTO offline_attendance(college_id,student_id,course_id,attendance_date,lecture_no,topic,present) VALUES(?,?,?,?,?,?,?)',(session['user_id'],sid,cid,date,lecture,topic,present))
                total=con.execute('SELECT total_lectures FROM college_enrollments WHERE college_id=? AND student_id=? AND course_id=?',(session['user_id'],sid,cid)).fetchone()
                att=con.execute('SELECT COUNT(*) n FROM offline_attendance WHERE college_id=? AND student_id=? AND course_id=? AND present=1',(session['user_id'],sid,cid)).fetchone()['n']
                totaln=(total['total_lectures'] if total and total['total_lectures'] else 18); prog=round(att*100/totaln)
                con.execute('UPDATE college_enrollments SET attendance=?,progress=? WHERE college_id=? AND student_id=? AND course_id=?',(att,prog,session['user_id'],sid,cid)); flash(f'Attendance saved: {att}/{totaln} lectures.','success')
            elif action=='schedule':
                schedule_date=request.form.get('schedule_date')
                topic=(request.form.get('topic') or '').strip()
                if not schedule_date or not request.form.get('start_time') or not topic:
                    raise ValueError('Please enter date, start time and topic for the timetable.')
                con.execute('INSERT INTO offline_schedule(college_id,course_id,batch_name,schedule_date,start_time,end_time,teacher_name,topic,room) VALUES(?,?,?,?,?,?,?,?,?)',(session['user_id'],cid,request.form.get('batch_name') or 'Batch A',schedule_date,request.form.get('start_time'),request.form.get('end_time'),request.form.get('teacher_name'),topic,request.form.get('room'))); flash('Timetable published successfully. Students can now see it in Offline Classes and Profile.','success')
            elif action=='syllabus':
                topic=(request.form.get('topic') or '').strip()
                if not topic:
                    raise ValueError('Please enter a syllabus topic.')
                lecture=max(1,int(request.form.get('lecture_no') or 1))
                con.execute('INSERT OR REPLACE INTO course_syllabus(college_id,course_id,lecture_no,topic,description) VALUES(?,?,?,?,?)',(session['user_id'],cid,lecture,topic,request.form.get('description'))); flash('Syllabus published successfully. Students can now see the pending syllabus and progress.','success')
            con.commit()
        except (ValueError,sqlite3.Error) as e:
            con.rollback(); flash('Please check the entered attendance/schedule details.','danger')
    rows=con.execute("SELECT ce.*,u.full_name,c.title FROM college_enrollments ce JOIN users u ON u.id=ce.student_id JOIN courses c ON c.id=ce.course_id WHERE ce.college_id=? ORDER BY ce.id DESC",(session['user_id'],)).fetchall()
    schedules=con.execute("SELECT os.*,c.title FROM offline_schedule os JOIN courses c ON c.id=os.course_id WHERE os.college_id=? ORDER BY os.schedule_date,os.start_time",(session['user_id'],)).fetchall()
    syllabus=con.execute("SELECT cs.*,c.title FROM course_syllabus cs JOIN courses c ON c.id=cs.course_id WHERE cs.college_id=? ORDER BY cs.course_id,cs.lecture_no",(session['user_id'],)).fetchall()
    con.close(); return render_template('college_enrollments.html',students=students,courses=courses,rows=rows,schedules=schedules,syllabus=syllabus)

@app.route('/student/support-programs')
@role_required('student')
def student_support_programs():
    con=db(); supports=con.execute("SELECT * FROM ngo_supports WHERE lower(status)='open' ORDER BY id DESC").fetchall(); con.close(); return render_template('support_programs.html',supports=supports)

@app.route('/student/offline-learning')
@role_required('student')
def student_offline_learning():
    con=db(); uid=session['user_id']
    rows=con.execute("SELECT ce.*,c.title,c.subject,c.duration FROM college_enrollments ce JOIN courses c ON c.id=ce.course_id WHERE ce.student_id=? AND lower(c.mode) LIKE '%offline%' ORDER BY ce.id DESC",(uid,)).fetchall()
    today=__import__('datetime').date.today().isoformat()
    schedules=con.execute("SELECT os.*,c.title FROM offline_schedule os JOIN courses c ON c.id=os.course_id WHERE os.schedule_date>=? AND EXISTS (SELECT 1 FROM college_enrollments ce WHERE ce.student_id=? AND ce.college_id=os.college_id AND (ce.course_id=os.course_id OR ce.batch_name=os.batch_name)) ORDER BY os.schedule_date,os.start_time LIMIT 30",(today,uid)).fetchall()
    syllabus=con.execute("SELECT cs.*,c.title FROM course_syllabus cs JOIN courses c ON c.id=cs.course_id WHERE cs.course_id IN (SELECT course_id FROM college_enrollments WHERE student_id=?) ORDER BY cs.course_id,cs.lecture_no",(uid,)).fetchall()
    attendance=con.execute("SELECT oa.*,c.title FROM offline_attendance oa JOIN courses c ON c.id=oa.course_id WHERE oa.student_id=? ORDER BY oa.attendance_date DESC,oa.lecture_no DESC LIMIT 100",(uid,)).fetchall()
    completed_lectures={r['course_id']:set() for r in rows}
    for a in attendance:
        if a['present']:
            completed_lectures.setdefault(a['course_id'],set()).add(a['lecture_no'])
    syllabus_progress=[]
    for r in rows:
        items=[x for x in syllabus if x['course_id']==r['course_id']]
        completed=sum(1 for x in items if x['lecture_no'] in completed_lectures.get(r['course_id'],set()))
        total=len(items)
        percent=round(completed*100/total) if total else (r['progress'] or 0)
        syllabus_progress.append({'course_id':r['course_id'],'title':r['title'],'completed':completed,'total':total,'pending':max(0,total-completed),'percent':percent})
    con.close()
    return render_template('student_offline.html',rows=rows,schedules=schedules,syllabus=syllabus,attendance=attendance,syllabus_progress=syllabus_progress)

@app.route('/college/feedback')
@role_required('college')
def college_feedback():
    con=db(); col=con.execute('SELECT college_name FROM colleges WHERE user_id=?',(session['user_id'],)).fetchone(); rows=con.execute('SELECT f.*,u.full_name,s.college_name FROM feedback f JOIN users u ON u.id=f.user_id LEFT JOIN students s ON s.user_id=u.id WHERE lower(trim(s.college_name))=lower(trim(?)) ORDER BY f.id DESC',(col['college_name'],)).fetchall(); con.close(); return render_template('college_feedback.html',rows=rows)

@app.route('/progress')
@role_required('student')
def progress():
    con=db(); rows=con.execute('SELECT e.*,c.title,c.subject FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=?',(session['user_id'],)).fetchall(); con.close(); return render_template('progress.html',rows=rows)

if __name__=='__main__':
    init_db(); app.run(debug=True)
