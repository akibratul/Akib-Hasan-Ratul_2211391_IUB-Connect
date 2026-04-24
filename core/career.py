"""Career recommendation engine — ported from Express career.js"""
import json

DEPARTMENT_CAREERS = {
    'CSE': [
        {'title': 'Software Developer', 'skills': ['JavaScript', 'Python', 'Java', 'C++', 'Git']},
        {'title': 'Web Developer', 'skills': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js']},
        {'title': 'Data Analyst', 'skills': ['Python', 'SQL', 'Excel', 'Tableau', 'Statistics']},
        {'title': 'AI Engineer', 'skills': ['Python', 'TensorFlow', 'Machine Learning', 'Deep Learning', 'Math']},
        {'title': 'Mobile App Developer', 'skills': ['React Native', 'Flutter', 'Kotlin', 'Swift']},
        {'title': 'DevOps Engineer', 'skills': ['Docker', 'Kubernetes', 'CI/CD', 'AWS', 'Linux']},
        {'title': 'Cybersecurity Analyst', 'skills': ['Networking', 'Security', 'Linux', 'Ethical Hacking']},
        {'title': 'Cloud Architect', 'skills': ['AWS', 'Azure', 'GCP', 'Terraform', 'Microservices']},
    ],
    'BBA': [
        {'title': 'Marketing Executive', 'skills': ['Digital Marketing', 'SEO', 'Analytics', 'Communication']},
        {'title': 'Business Analyst', 'skills': ['Data Analysis', 'SQL', 'Excel', 'Problem Solving']},
        {'title': 'HR Manager', 'skills': ['People Management', 'Recruitment', 'Communication', 'Leadership']},
        {'title': 'Financial Analyst', 'skills': ['Accounting', 'Excel', 'Financial Modeling', 'Economics']},
        {'title': 'Project Manager', 'skills': ['Agile', 'Scrum', 'Communication', 'Leadership', 'Planning']},
        {'title': 'Entrepreneur', 'skills': ['Business Strategy', 'Leadership', 'Marketing', 'Finance']},
    ],
    'EEE': [
        {'title': 'Electrical Engineer', 'skills': ['Circuit Design', 'MATLAB', 'Power Systems']},
        {'title': 'Embedded Systems Engineer', 'skills': ['C', 'C++', 'Microcontrollers', 'IoT']},
        {'title': 'Telecommunications Engineer', 'skills': ['Networking', 'Signal Processing', '5G']},
        {'title': 'Robotics Engineer', 'skills': ['Python', 'ROS', 'Control Systems', 'AI']},
    ],
    'ECO': [
        {'title': 'Economist', 'skills': ['Statistics', 'Econometrics', 'Research', 'Data Analysis']},
        {'title': 'Policy Analyst', 'skills': ['Research', 'Writing', 'Critical Thinking', 'Statistics']},
        {'title': 'Financial Consultant', 'skills': ['Finance', 'Excel', 'Risk Analysis', 'Economics']},
    ],
    'ENG': [
        {'title': 'Content Writer', 'skills': ['Writing', 'SEO', 'Research', 'Communication']},
        {'title': 'Editor', 'skills': ['Editing', 'Proofreading', 'Writing', 'Attention to Detail']},
        {'title': 'Communications Specialist', 'skills': ['PR', 'Writing', 'Social Media', 'Branding']},
    ],
}

SKILL_CAREER_MAP = {
    'python': ['Data Scientist', 'AI Engineer', 'Machine Learning Engineer', 'Data Analyst'],
    'javascript': ['Frontend Developer', 'Full-Stack Developer', 'Web Developer'],
    'react': ['Frontend Developer', 'Web Developer', 'Full-Stack Developer'],
    'node': ['Backend Developer', 'Full-Stack Developer', 'Web Developer'],
    'web': ['Frontend Developer', 'Backend Developer', 'Web Developer'],
    'machine_learning': ['AI Engineer', 'Machine Learning Engineer', 'Data Scientist'],
    'ml': ['AI Engineer', 'Machine Learning Engineer', 'Data Scientist'],
    'ai': ['AI Engineer', 'Machine Learning Engineer', 'Data Scientist'],
    'data': ['Data Analyst', 'Data Scientist', 'Business Analyst'],
    'sql': ['Data Analyst', 'Database Administrator', 'Business Analyst'],
    'cloud': ['Cloud Architect', 'DevOps Engineer', 'Cloud Engineer'],
    'aws': ['Cloud Architect', 'DevOps Engineer', 'Cloud Engineer'],
    'docker': ['DevOps Engineer', 'Cloud Engineer', 'Backend Developer'],
    'mobile': ['Mobile App Developer', 'iOS Developer', 'Android Developer'],
    'flutter': ['Mobile App Developer', 'Cross-Platform Developer'],
    'marketing': ['Marketing Executive', 'Digital Marketing Specialist'],
    'finance': ['Financial Analyst', 'Financial Consultant', 'Investment Banker'],
    'design': ['UI/UX Designer', 'Graphic Designer', 'Product Designer'],
    'security': ['Cybersecurity Analyst', 'Security Engineer', 'Penetration Tester'],
    'management': ['Project Manager', 'Product Manager', 'HR Manager'],
    'leadership': ['Project Manager', 'Team Lead', 'Entrepreneur'],
}

CAREER_SKILLS_SUGGESTION = {
    'Data Scientist': ['Python', 'R', 'Machine Learning', 'Statistics', 'SQL', 'TensorFlow'],
    'AI Engineer': ['Python', 'PyTorch', 'TensorFlow', 'Deep Learning', 'NLP', 'Computer Vision'],
    'Frontend Developer': ['React', 'TypeScript', 'CSS', 'Figma', 'Testing', 'Next.js'],
    'Backend Developer': ['Node.js', 'Python', 'Databases', 'REST APIs', 'Docker', 'Redis'],
    'Full-Stack Developer': ['React', 'Node.js', 'Databases', 'Docker', 'TypeScript', 'Git'],
    'Web Developer': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Git'],
    'Mobile App Developer': ['React Native', 'Flutter', 'Kotlin', 'Swift', 'Firebase'],
    'DevOps Engineer': ['Docker', 'Kubernetes', 'CI/CD', 'AWS', 'Terraform', 'Linux'],
    'Cloud Architect': ['AWS', 'Azure', 'GCP', 'Microservices', 'Terraform', 'Security'],
    'Cybersecurity Analyst': ['Networking', 'Ethical Hacking', 'SIEM', 'Linux', 'Python'],
    'Machine Learning Engineer': ['Python', 'TensorFlow', 'MLOps', 'Statistics', 'Docker'],
    'Data Analyst': ['SQL', 'Python', 'Excel', 'Tableau', 'Power BI', 'Statistics'],
    'Marketing Executive': ['Google Ads', 'SEO', 'Social Media', 'Analytics', 'Content Strategy'],
    'Business Analyst': ['SQL', 'Excel', 'Tableau', 'Process Mapping', 'Requirements Analysis'],
    'HR Manager': ['Recruitment', 'HRIS', 'Labor Law', 'Conflict Resolution', 'Training'],
    'Financial Analyst': ['Excel', 'Financial Modeling', 'Bloomberg', 'Python', 'Valuation'],
    'Project Manager': ['Jira', 'Agile', 'Scrum', 'MS Project', 'Risk Management'],
}


def get_recommendations(student_profile):
    department = (student_profile.department or '').upper()
    skills = student_profile.get_skills_list()
    interests = (student_profile.interests or '').lower()
    skills_lower = [s.lower() for s in skills]

    careers = {}

    # Department-based
    dept_careers = DEPARTMENT_CAREERS.get(department, DEPARTMENT_CAREERS.get('CSE', []))
    for c in dept_careers:
        careers[c['title']] = {
            'title': c['title'], 'score': 50,
            'matchReasons': [f"Department: {department}"],
            'requiredSkills': c['skills']
        }

    # Skill-based
    for skill in skills_lower:
        for keyword, career_list in SKILL_CAREER_MAP.items():
            if skill in keyword or keyword in skill:
                for career_title in career_list:
                    if career_title in careers:
                        careers[career_title]['score'] += 20
                        careers[career_title]['matchReasons'].append(f"Skill match: {skill}")
                    else:
                        careers[career_title] = {
                            'title': career_title, 'score': 30,
                            'matchReasons': [f"Skill match: {skill}"],
                            'requiredSkills': []
                        }

    # Interest-based boost
    if interests:
        for key, career in careers.items():
            title_lower = career['title'].lower()
            if interests in title_lower or any(w in interests for w in title_lower.split()):
                career['score'] += 15
                career['matchReasons'].append('Matches interests')

    sorted_careers = sorted(careers.values(), key=lambda x: x['score'], reverse=True)[:8]

    for career in sorted_careers:
        career['suggestedSkills'] = CAREER_SKILLS_SUGGESTION.get(career['title'], career['requiredSkills'])
        career['matchPercentage'] = min(career['score'], 100)
        career['stars'] = round(career['matchPercentage'] / 20)

    return sorted_careers
