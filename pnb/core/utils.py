from datetime import datetime, timezone, timedelta
import re
import json
from uuid import uuid4
import openai

from fastapi.exceptions import HTTPException
from fastapi import File, UploadFile



def humanize_date(dt: datetime) -> str:
    return dt.strftime("%b %d, %Y at %I:%M %p")


def humanize_duration(seconds: int) -> str:
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)

    parts = []
    if hrs:
        parts.append(f"{hrs} hour{'s' if hrs > 1 else ''}")
    if mins:
        parts.append(f"{mins} minute{'s' if mins > 1 else ''}")
    if secs or not parts:
        parts.append(f"{secs} second{'s' if secs > 1 else ''}")

    return " ".join(parts)

def identify_speakers_with_ai(utterances):
    """
    Use AI to intelligently identify which speaker is the agent vs customer.

    Heuristics used:
    1. Agent typically speaks first (greeting)
    2. Agent uses more formal language, company-specific terms
    3. Agent asks more questions
    4. Customer describes problems, asks for help
    5. Agent provides solutions, instructions
    """

    if not utterances or len(utterances) == 0:
        return {}

    # Collect text by speaker
    speaker_texts = {}
    speaker_stats = {}

    for utterance in utterances:
        speaker = utterance.speaker
        text = utterance.text.lower()

        if speaker not in speaker_texts:
            speaker_texts[speaker] = []
            speaker_stats[speaker] = {
                'total_words': 0,
                'question_count': 0,
                'greeting_score': 0,
                'professional_score': 0,
                'helping_score': 0,
                'problem_score': 0,
                'first_speaker': False,
                'utterance_count': 0
            }

        speaker_texts[speaker].append(text)
        speaker_stats[speaker]['utterance_count'] += 1
        speaker_stats[speaker]['total_words'] += len(text.split())

        # Count questions
        if '?' in utterance.text:
            speaker_stats[speaker]['question_count'] += 1

        # Greeting indicators (agent typically greets)
        greeting_words = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening',
                         'thank you for calling', 'thanks for calling', 'welcome']
        for greeting in greeting_words:
            if greeting in text:
                speaker_stats[speaker]['greeting_score'] += 1

        # Professional/agent language
        professional_phrases = ['how can i help', 'how may i assist', 'let me check',
                               'i can help you', 'i\'ll be happy to', 'i understand',
                               'let me look into', 'i apologize', 'i see here',
                               'account', 'verify', 'confirm', 'policy', 'system']
        for phrase in professional_phrases:
            if phrase in text:
                speaker_stats[speaker]['professional_score'] += 1

        # Help/solution providing (agent behavior)
        helping_phrases = ['i can', 'i will', 'let me', 'i\'ll help', 'i\'ll assist',
                          'what i can do', 'here\'s what', 'you can', 'you should',
                          'you need to', 'you\'ll need', 'i recommend']
        for phrase in helping_phrases:
            if phrase in text:
                speaker_stats[speaker]['helping_score'] += 1

        # Problem description (customer behavior)
        problem_phrases = ['i need', 'i want', 'i\'m trying to', 'i can\'t', 'i have a problem',
                          'not working', 'doesn\'t work', 'issue with', 'help me',
                          'my account', 'my order', 'my payment']
        for phrase in problem_phrases:
            if phrase in text:
                speaker_stats[speaker]['problem_score'] += 1

    # Mark first speaker
    if utterances:
        first_speaker = utterances[0].speaker
        speaker_stats[first_speaker]['first_speaker'] = True

    # Use LLM for intelligent classification if available
    try:
        # Prepare sample texts for each speaker (first 3 utterances)
        speaker_samples = {}
        for speaker in speaker_texts:
            speaker_samples[speaker] = ' '.join(speaker_texts[speaker][:3])

        # Create prompt for GPT
        prompt = """Analyze this call center conversation and identify which speaker is the AGENT and which is the CUSTOMER.

Speakers and their sample dialogue:
"""
        for speaker, sample in speaker_samples.items():
            prompt += f"\n{speaker}: \"{sample[:500]}...\"\n"

        prompt += """
Based on the dialogue patterns, language used, and context:
- The AGENT typically: greets first, uses professional language, asks clarifying questions, provides solutions
- The CUSTOMER typically: describes problems, asks for help, expresses concerns

Respond with ONLY a JSON object in this exact format:
{"agent": "SPEAKER_X", "customer": "SPEAKER_Y"}
"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a call center conversation analyzer. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)

        # Validate the response
        if 'agent' in result and 'customer' in result:
            return {
                result['agent']: 'agent',
                result['customer']: 'customer'
            }

    except Exception as e:
        print(f"AI identification failed, falling back to heuristics: {e}")

    # Fallback to heuristic scoring if AI fails
    speakers = list(speaker_stats.keys())
    if len(speakers) < 2:
        # Only one speaker detected
        return {speakers[0]: 'agent'} if speakers else {}

    # Calculate agent score for each speaker
    for speaker in speakers:
        stats = speaker_stats[speaker]
        agent_score = (
            stats['greeting_score'] * 3 +
            stats['professional_score'] * 2 +
            stats['helping_score'] * 2 +
            (stats['question_count'] / max(stats['utterance_count'], 1)) * 2 +
            (1 if stats['first_speaker'] else 0) * 2 -
            stats['problem_score'] * 1.5
        )
        speaker_stats[speaker]['agent_score'] = agent_score

    # Sort by agent score
    sorted_speakers = sorted(speakers, key=lambda s: speaker_stats[s]['agent_score'], reverse=True)

    # Assign roles
    return {
        sorted_speakers[0]: 'agent',
        sorted_speakers[1]: 'customer' if len(sorted_speakers) > 1 else 'unknown'
    }