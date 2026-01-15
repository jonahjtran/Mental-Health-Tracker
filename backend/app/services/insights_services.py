from backend.app import db
from backend.app.db.models import JournalInsights

def analyze_journal_entry(journal_id: int, user_id: int, force=False):
    existing_insights = get_existing_insights(journal_id, user_id)

    journal_entry = get_journal_entry(journal_id, user_id)
    if not journal_entry:
        raise ValueError(f"Journal entry does not exist for user {user_id}")
    
    if existing_insights and not force:
        return existing_insights
     
    mood_rating = journal_entry.mood_rating
    entry = journal_entry.entry
    date = journal_entry.date
    
    next step: feed info to llm

    response = llm.generate_insights(mood_rating, entry, date, prompt -> stored in env variable)

    insights = parse_insights(response)

    save insights to db

    return insights
