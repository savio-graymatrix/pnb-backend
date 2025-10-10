from pnb.db.data_models.call_center.Session import Session
from pnb.langgraph.call_center.agents.call_analysis_agent import CallAnalysisAgent
from pnb.core.utils import humanize_duration, humanize_date

async def analyze_session(session: Session):
    transcript = session.transcript
    customer_info = session.customer_info

    parsed_transcript = '\n'.join([f'{message.speaker}: {message.text}' for message in transcript])

    call_analysis_agent = CallAnalysisAgent()

    analysis_input = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Please analyze this banking customer service conversation comprehensively:

CONVERSATION:
{parsed_transcript}

CONTEXT:
- Customer: {customer_info.name}
- Phone: {customer_info.phone_number}
- Date: {session.call_time}
- Duration: {session.call_duration}

Provide a comprehensive analysis including summary, compliance report, quality scorecard and customer satisfaction score in the JSON format specified in your instructions."""
                    }
                ]
            }

    config = {"configurable": {"thread_id": session.session_id}}

    call_summary_response = await call_analysis_agent.call_analysis(analysis_input, config)

    compliance = f'''## Call Analysis\n
**Duration:** {humanize_duration(int(session.call_duration)) if session.call_duration else 'N/A'}\n
**Date:** {humanize_date(session.call_time)}\n
**Handled By:** Call Center Agent (Assisted by AI Agent)\n
**Customer Concern:** {call_summary_response.get('structured_response').compliance_report.customer_concern}'''
    compliance += '\n\n'.join([f'#### {i['name']}\n* {'\n* '.join(i['list_of_keys'])}' if isinstance(i, dict) else '' for i in call_summary_response.get('structured_response').compliance_report.model_dump().values()])

    score_card = '''## Scorecard\n\n'''
    score_card += '\n\n'.join(
        [f'#### {i['name']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`{i['score']}`\n* {'\n* '.join(i['list_of_keys'])}'
            for i in call_summary_response.get('structured_response').scorecard.model_dump().values()])

    call_summary = call_summary_response.get('structured_response').summary.replace('•', '-')
    call_summary_gist = call_summary_response.get('structured_response').call_summary_gist

    session.call_summary = call_summary + '\n\n' + '**Gist:** ' + call_summary_gist

    session.compliance = compliance
    session.score_card = score_card
    session.call_status = call_summary_response.get('structured_response').call_status
    session.call_score = call_summary_response.get('structured_response').overall_score
    session.customer_satisfaction_score = call_summary_response.get('structured_response').customer_satisfaction_score
    session.call_improvement_suggestions = call_summary_response.get('structured_response').call_improvement_suggestions.replace('•', '-')
    await session.save()
