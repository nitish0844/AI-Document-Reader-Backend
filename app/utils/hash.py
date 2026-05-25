import hashlib

def generate_resume_hash(text: str):

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()