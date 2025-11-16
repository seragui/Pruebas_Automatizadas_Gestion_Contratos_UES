_candidate_full_name = None

def set_candidate_full_name(name: str):
    global _candidate_full_name
    _candidate_full_name = name

def get_candidate_full_name(default=None):
    return _candidate_full_name or default