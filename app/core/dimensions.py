# app/core/dimensions.py
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel
from typing import List


class AssessmentType(str, Enum):
    WELLBEING = "wellbeing"
    SKILLS = "skills"
    VALUES = "values"


class DimensionComparisonResponse(BaseModel):
    dimension_names: List[str]
    user_scores: List[float]
    job_scores: List[float]
    company_scores: List[float]  # Optional, if you want company comparison too


class AssessmentDimensions:
    """
    Complete definition of all assessment dimensions with their theoretical background
    and corresponding questions
    """

    WELLBEING_DIMENSIONS = {
        "AUTONOMY": {
            "title": "Autonomy",
            "description": "Degree of independence and self-direction in work",
            "theory": "Based on Self-Determination Theory (Deci & Ryan). Measures need for independence and control over work decisions.",
            "questions": [
                "How much freedom do you need in deciding how to do your work?",
                "How important is it for you to set your own schedule?",
                "How much independence do you prefer in your role?",
            ],
        },
        "MASTERY": {
            "title": "Growth & Mastery",
            "description": "Opportunity for skill development and advancement",
            "theory": "Combines SDT's Competence with Growth Mindset Theory (Dweck). Reflects desire for skill development.",
            "questions": [
                "How important is continuous learning in your work?",
                "How much do you value opportunities to master new skills?",
                "How important is regular feedback for your growth?",
            ],
        },
        "RELATEDNESS": {
            "title": "Social Connection",
            "description": "Quality of workplace relationships and team dynamics",
            "theory": "From SDT's Relatedness and Social Support Theory. Measures importance of workplace relationships.",
            "questions": [
                "How important is team collaboration to you?",
                "How much do you value building connections with colleagues?",
                "How important is a sense of belonging at work?",
            ],
        },
        "WORK_LIFE": {
            "title": "Work-Life Balance",
            "description": "Balance between work and personal life",
            "theory": "Based on Work-Life Border Theory (Clark). Assesses preferred boundaries between work and personal life.",
            "questions": [
                "How important is maintaining clear work-life boundaries?",
                "How much do you value flexible working arrangements?",
                "How important is having time for personal life and recovery?",
            ],
        },
        "PURPOSE": {
            "title": "Purpose & Meaning",
            "description": "Sense of meaning and impact in work",
            "theory": "Based on Purpose-Driven Work Theory. Measures need for meaningful work aligned with personal values.",
            "questions": [
                "How important is it that your work feels meaningful?",
                "How much do you value making a positive impact through your work?",
                "How important is alignment with company mission?",
            ],
        },
        "PSYCHOLOGICAL_SAFETY": {
            "title": "Psychological Safety",
            "description": "Feeling safe to take risks and be authentic",
            "theory": "Based on Edmondson's Psychological Safety Framework. Measures need for supportive, trust-based environment.",
            "questions": [
                "How important is feeling safe to express opinions at work?",
                "How much do you value a supportive management style?",
                "How important is having an inclusive work environment?",
            ],
        },
    }

    SKILLS_DIMENSIONS = {
        "TECHNICAL": {
            "title": "Technical Expertise",
            "description": "Core technical skills and domain knowledge",
            "theory": "Based on Professional Expertise Development Theory. Measures technical competency and specialization.",
            "questions": [
                "How would you rate your technical expertise in your field?",
                "How comfortable are you with learning new technical tools?",
                "How experienced are you with industry-specific software/tools?",
            ],
        },
        "PROBLEM_SOLVING": {
            "title": "Problem Solving",
            "description": "Analytical and creative problem-solving abilities",
            "theory": "Based on Complex Problem Solving Theory. Assesses analytical and creative thinking capabilities.",
            "questions": [
                "How skilled are you at breaking down complex problems?",
                "How good are you at finding innovative solutions?",
                "How well do you handle ambiguous situations?",
            ],
        },
        "COMMUNICATION": {
            "title": "Communication",
            "description": "Verbal, written, and interpersonal communication",
            "theory": "Based on Communication Competence Theory. Measures effectiveness in various communication modes.",
            "questions": [
                "How effective are you at presenting ideas clearly?",
                "How skilled are you in written communication?",
                "How good are you at handling difficult conversations?",
            ],
        },
        "ADAPTABILITY": {
            "title": "Adaptability",
            "description": "Ability to adapt to change and learn quickly",
            "theory": "Based on Adaptive Performance Theory. Measures flexibility and learning agility.",
            "questions": [
                "How quickly do you adapt to new situations?",
                "How well do you handle unexpected changes?",
                "How fast do you learn new skills and processes?",
            ],
        },
        "COLLABORATION": {
            "title": "Collaboration",
            "description": "Ability to work effectively with others",
            "theory": "Based on Team Effectiveness Models. Assesses teamwork and cross-functional capabilities.",
            "questions": [
                "How effective are you at working in teams?",
                "How well do you collaborate across departments?",
                "How good are you at building consensus?",
            ],
        },
        "LEADERSHIP": {
            "title": "Leadership",
            "description": "Ability to guide and influence others",
            "theory": "Based on Transformational Leadership Theory. Measures leadership and influence capabilities.",
            "questions": [
                "How effective are you at leading projects or teams?",
                "How good are you at motivating others?",
                "How well do you handle team conflicts?",
            ],
        },
    }

    VALUES_DIMENSIONS = {
        "INNOVATION": {
            "title": "Innovation",
            "description": "Emphasis on innovation and creative thinking",
            "theory": "Based on Innovation Culture Theory. Measures alignment with innovative work environments.",
            "questions": [
                "How important is working in an innovative environment?",
                "How much do you value creative problem-solving?",
                "How important is experimenting with new ideas?",
            ],
        },
        "SUSTAINABILITY": {
            "title": "Sustainability",
            "description": "Commitment to environmental and social responsibility",
            "theory": "Based on Corporate Sustainability Theory. Measures alignment with sustainable practices.",
            "questions": [
                "How important is environmental responsibility?",
                "How much do you value sustainable business practices?",
                "How important is social impact in business?",
            ],
        },
        "DIVERSITY": {
            "title": "Diversity & Inclusion",
            "description": "Commitment to diversity and inclusive practices",
            "theory": "Based on Diversity Management Theory. Measures value placed on inclusive environments.",
            "questions": [
                "How important is workplace diversity to you?",
                "How much do you value inclusive practices?",
                "How important is equal opportunity?",
            ],
        },
        "ETHICS": {
            "title": "Ethics & Integrity",
            "description": "Commitment to ethical practices and transparency",
            "theory": "Based on Business Ethics Framework. Measures alignment with ethical business practices.",
            "questions": [
                "How important is ethical business conduct?",
                "How much do you value transparency?",
                "How important is integrity in decision-making?",
            ],
        },
        "GROWTH": {
            "title": "Growth Mindset",
            "description": "Focus on continuous improvement and learning",
            "theory": "Based on Growth Mindset Theory. Measures alignment with learning-oriented cultures.",
            "questions": [
                "How important is continuous organizational learning?",
                "How much do you value professional development?",
                "How important is embracing challenges?",
            ],
        },
        "IMPACT": {
            "title": "Social Impact",
            "description": "Commitment to positive societal impact",
            "theory": "Based on Social Impact Theory. Measures alignment with socially responsible business.",
            "questions": [
                "How important is making a positive societal impact?",
                "How much do you value community engagement?",
                "How important is contributing to social good?",
            ],
        },
    }

    @classmethod
    def get_dimensions(cls, assessment_type: AssessmentType) -> Dict:
        """Get dimensions for specific assessment type"""
        if assessment_type == AssessmentType.WELLBEING:
            return cls.WELLBEING_DIMENSIONS
        elif assessment_type == AssessmentType.SKILLS:
            return cls.SKILLS_DIMENSIONS
        elif assessment_type == AssessmentType.VALUES:
            return cls.VALUES_DIMENSIONS
        raise ValueError(f"Unknown assessment type: {assessment_type}")

    @classmethod
    def get_questions(cls, assessment_type: AssessmentType) -> List[Dict]:
        """Get all questions for an assessment type with dimension context"""
        dimensions = cls.get_dimensions(assessment_type)
        questions = []

        for dim_key, dimension in dimensions.items():
            for q in dimension["questions"]:
                questions.append(
                    {
                        "dimension": dim_key,
                        "dimension_title": dimension["title"],
                        "question": q,
                        "theory": dimension["theory"],
                    }
                )

        return questions


# Example scoring function
def calculate_dimension_score(answers: List[int]) -> float:
    """Calculate dimension score from question answers (0-10 scale)"""
    if not answers:
        return 0.0
    return sum(answers) / len(answers)


# Example profile generation
def generate_profile(answers: Dict[str, List[int]], dimensions: Dict) -> Dict:
    """Generate profile from answers, calculating scores for each dimension"""
    profile = {}

    for dim_key, dimension in dimensions.items():
        if dim_key in answers:
            profile[dim_key] = {
                "score": calculate_dimension_score(answers[dim_key]),
                "title": dimension["title"],
                "description": dimension["description"],
            }

    return profile
