"""
core/resume_ai/skills_list.py

Ported from resume-analyzer-nlp (unchanged) — a curated reference vocabulary
used for keyword-based skill extraction from both resume and job description
text. Deliberately plain-list rather than ML-based extraction: fast, fully
offline, and easy to extend by just adding a string.
"""

SKILLS_LIST = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "perl", "sql", "bash", "shell scripting",

    # Web development
    "html", "css", "sass", "react", "angular", "vue", "next.js",
    "node.js", "express", "django", "flask", "fastapi", "spring boot",
    "asp.net", "rest api", "graphql", "api development", "webpack",
    "streamlit", "bootstrap", "tailwind css",

    # Data science / ML / AI
    "machine learning", "deep learning", "artificial intelligence",
    "nlp", "natural language processing", "computer vision",
    "data analysis", "data science", "data visualization",
    "data engineering", "data mining", "statistics", "predictive modeling",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "opencv", "matplotlib", "seaborn", "plotly", "spacy", "nltk",
    "hugging face", "transformers", "llm", "large language models",
    "feature engineering", "model deployment", "mlops", "a/b testing",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
    "database design", "database management", "nosql", "data warehousing",
    "etl", "big data", "hadoop", "spark", "apache spark", "snowflake",

    # Cloud & DevOps
    "aws", "azure", "google cloud", "gcp", "docker", "kubernetes",
    "ci/cd", "jenkins", "terraform", "linux", "unix", "devops",
    "cloud computing", "microservices", "serverless",

    # Tools & platforms
    "git", "github", "gitlab", "jira", "confluence", "slack",
    "excel", "power bi", "tableau", "looker", "google analytics",
    "postman", "figma", "vs code",

    # Project management / business
    "project management", "agile", "scrum", "kanban", "product management",
    "business analysis", "stakeholder management", "risk management",
    "budgeting", "strategic planning", "vendor management",

    # Soft skills
    "communication", "leadership", "teamwork", "collaboration",
    "problem solving", "critical thinking", "time management",
    "adaptability", "creativity", "attention to detail",
    "presentation skills", "negotiation", "conflict resolution",
    "decision making", "mentoring", "customer service",

    # Marketing / design (in case of non-tech resumes)
    "seo", "sem", "content marketing", "social media marketing",
    "email marketing", "brand management", "adobe photoshop",
    "adobe illustrator", "ui/ux design", "graphic design",
    "copywriting", "market research",

    # General/office
    "microsoft office", "google workspace", "typing", "data entry",
    "research", "report writing", "documentation"
]