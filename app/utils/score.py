def normalize_score(distance: float):

    similarity = 1 - distance

    # Better scaling for HR readability
    score = similarity * 150

    return max(
        0,
        min(
            int(score),
            100
        )
    )