import os
from parsers.jd_parser import parse_jd
from parsers.resume_parser import parse_resume
from loguru import logger

def main():
    logger.info("Testing Parsers...")
    
    jd_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_jd.txt')
    with open(jd_path, 'r', encoding='utf-8') as f:
        jd_text = f.read()
        
    resume_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_resume.txt')
    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    print("\n--- Extracted JD Skills ---")
    skills = parse_jd(jd_text)
    for s in skills:
        print(s)
        
    print("\n--- Extracted Candidate Profile ---")
    profile = parse_resume(resume_text)
    print(profile.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
