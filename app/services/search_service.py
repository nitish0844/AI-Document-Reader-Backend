from sqlalchemy import text
from sqlalchemy.orm import Session


def search_resumes(
    db: Session,
    user_id: int,
    query_embedding,
    minimum_years_experience: float = 0,
    limit: int = 10,
    skills_pattern: str = "%"
):

    sql = text("""
        SELECT
    candidate_name,
    current_role,
    years_experience,
    skills,
    embedding <=> CAST(:embedding AS vector) AS distance
    FROM resumes
    WHERE user_id = :user_id
    AND years_experience >= :minimum_years_experience
    AND LOWER(skills) LIKE LOWER(:skills_pattern)
    ORDER BY embedding <=> CAST(:embedding AS vector)
    LIMIT :limit
    """)

    results = db.execute(
        sql,
        {
            "embedding": str(query_embedding),
            "user_id": user_id,
            "minimum_years_experience": minimum_years_experience,
            "skills_pattern": skills_pattern,
            "limit": limit,
        }
    )

    return results.fetchall()