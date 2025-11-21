import os
from datetime import date, timedelta
from openai import OpenAI
from data_manager import load_entries, save_entries



def summarize_last_week():
    """Use AI to create a reflective summary of the last 7 days."""
    entries = load_entries()
    today = date.today()
    week_ago = today - timedelta(days=7)

    recent_entries = {
        d: v for d, v in entries.items()
        if week_ago.isoformat() <= d <= today.isoformat()
    }

    if not recent_entries:
        return "No recent entries found to summarize."

    text_block = ""
    for day, data in sorted(recent_entries.items()):
        text = data.get("text", "").strip()
        mood = data.get("mood", 0)
        text_block += f"\n### {day}\nMood: {mood}\n{text}\n"

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = (
        "You are a mindful journaling assistant. "
        "Read the user's journal entries from the past week and write a short, thoughtful summary "
        "of the emotional and mental patterns you notice. Highlight the positive points BUT also the negative things, dont be fearful of mentioning the bad things!!!!! Because we learn best from mistakes. "
        "Mention trends in mood and tone.\n\n"
        "Remember that the mood slider things values signify these moods:         if value < -60: Very Unpleasant elif value < -20: Slightly Unpleasant elif value < 20: Neutral elif value < 60: Pleasant  above thatVery Pleasant " 
        f"Here are the entries:\n{text_block}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a reflective journaling coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        summary_text = response.choices[0].message.content.strip()

        moods = [v.get("mood", 0) for v in recent_entries.values()]
        avg_mood = sum(moods) / len(moods) if moods else 0

        summary_id = f"summary-{today.isoformat()}"
        entries[summary_id] = {"text": summary_text, "mood": avg_mood}
        save_entries(entries)

        return summary_id, summary_text

    except Exception as e:
        return f"Error while summarizing: {e}"
