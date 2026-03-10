from models.session_state import SessionState

sessions = {}

def get_session(session_id):

    if session_id not in sessions:
        sessions[session_id] = SessionState()

    return sessions[session_id]