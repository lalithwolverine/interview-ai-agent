# Demo Transcript: Confused User

**Scenario**: User is unsure what they want and needs guidance

**Session ID**: demo_confused_001
**Role**: Software Engineer
**Started**: 2024-01-15T10:00:00Z

---

## Transcript

**2024-01-15T10:00:15Z** - **assistant**: Hello. I'm your interview practice partner. I can help you prepare for job interviews by conducting mock interviews.

Available roles:
- Software Engineer
- Sales Representative
- Retail Associate

Type the role name to get started, or specify which position you'd like to practice for.

**2024-01-15T10:00:32Z** - **user**: umm i dont know

**2024-01-15T10:00:33Z** - **assistant**: I'm here to help you practice for job interviews. Which role would you like to practice for?

• Software Engineer
• Sales Representative
• Retail Associate

Type the role name to get started.

**2024-01-15T10:00:45Z** - **user**: maybe software?

**2024-01-15T10:00:46Z** - **assistant**: Tell me about yourself and your experience with software development.

**2024-01-15T10:01:12Z** - **user**: i guess i code sometimes

**2024-01-15T10:01:13Z** - **assistant**: Could you please elaborate on that? I'd like to hear more details.

**2024-01-15T10:01:28Z** - **user**: well i took some classes in college

**2024-01-15T10:01:29Z** - **assistant**: Can you provide a specific example or metric to illustrate that point?

**2024-01-15T10:01:45Z** - **user**: i built a website for a class project

**2024-01-15T10:01:46Z** - **assistant**: Describe a challenging project you worked on and how you solved it.

**2024-01-15T10:02:15Z** - **user**: the website was hard because i didnt know javascript

**2024-01-15T10:02:16Z** - **assistant**: Can you provide more specific details about that?

**Evaluation JSON**:
```json
{
  "scores": {
    "communication": 2,
    "technical": 2,
    "examples": 2
  },
  "overall": 40,
  "should_followup": true,
  "followup_question": "What specific challenges did you face with JavaScript?",
  "feedback": [
    "Answer lacks specific technical details",
    "Could benefit from more structured explanation",
    "Try using STAR method for project descriptions"
  ]
}
```

**2024-01-15T10:02:35Z** - **user**: i learned react and it got easier

**2024-01-15T10:02:36Z** - **assistant**: How do you approach debugging a complex issue?

---

## Summary

- **Total Questions**: 3
- **Questions Answered**: 3
- **Average Communication Score**: 2.0/5
- **Average Technical Score**: 2.0/5
- **Average Examples Score**: 2.0/5
- **Overall Average**: 40/100

**Key Observations**:
- User needed multiple prompts to provide detailed answers
- Answers were brief and lacked specifics initially
- System successfully guided user to provide more information
- Follow-up questions helped extract more details

