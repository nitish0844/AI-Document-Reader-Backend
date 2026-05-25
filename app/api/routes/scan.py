from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.models.scan import ScanRequest

from app.services.resume_service import (
    generate_embedding
)

from app.services.search_service import (
    search_resumes
)

from app.utils.score import (
    normalize_score
)

from app.services.requirement_parser import (
    parse_requirement
)

router = APIRouter()


@router.post("/scan-resumes")
async def scan_resumes(
    data: ScanRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    parsed_requirement = parse_requirement(
        data.requirement
    )

    user_id = current_user["user_id"]

    query_embedding = generate_embedding(
        data.requirement
    )

    minimum_years_experience = (
        parsed_requirement.get(
            "minimum_years_experience",
            0
        )
    )

    skills = parsed_requirement.get(
        "skills",
        []
    )

    skills_pattern = "%"

    if skills:
        skills_pattern = f"%{skills[0]}%"

    results = search_resumes(
        db,
        user_id,
        query_embedding,
        minimum_years_experience,
        skills_pattern=skills_pattern
    )
    


    ranked_candidates = []

    for row in results:

        score = normalize_score(
            row.distance
        )

        ranked_candidates.append({
            "candidate_name": row.candidate_name,
            "current_role": row.current_role,
            "years_experience": row.years_experience,
            "skills": row.skills,
            "match_score": score
        })

    ranked_candidates.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return {
        "requirement": data.requirement,
        "total_matches": len(ranked_candidates),
        "results": ranked_candidates
    }