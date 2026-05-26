from app.services.requirement_parser import (
    parse_requirement
)

def calculate_ai_score(
    candidate_skills: list[str],
    candidate_experience: int,
    requirement_text: str
):

    parsed_requirement = (
        parse_requirement(
            requirement_text
        )
    )

    required_skills = parsed_requirement.get(
        "skills",
        []
    )

    minimum_experience = (
        parsed_requirement.get(
            "minimum_years_experience",
            0
        )
    )

    matched_skills = 0

    for skill in required_skills:

        if skill.lower() in [
            s.lower()
            for s in candidate_skills
        ]:

            matched_skills += 1

    skill_score = 0

    if required_skills:

        skill_score = int(
            (
                matched_skills /
                len(required_skills)
            ) * 70
        )

    experience_score = 0

    if (
        candidate_experience >=
        minimum_experience
    ):

        experience_score = 30

    total_score = (
        skill_score +
        experience_score
    )

    return min(total_score, 100)