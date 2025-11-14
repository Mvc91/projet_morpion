def add_activity(session_historique, activity):
    from datetime import datetime
    r = datetime.now()
    session_historique[r] = activity