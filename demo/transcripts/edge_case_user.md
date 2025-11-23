# Demo Transcript: Edge Case User

**Scenario**: User provides invalid inputs, goes off-topic, and submits requests beyond bot's capabilities

**Session ID**: demo_edgecase_001
**Role**: Retail Associate
**Started**: 2024-01-15T13:00:00Z

---

## Transcript

**2024-01-15T13:00:05Z** - **assistant**: Hello. I'm your interview practice partner. I can help you prepare for job interviews by conducting mock interviews.

Available roles:
- Software Engineer
- Sales Representative
- Retail Associate

Type the role name to get started, or specify which position you'd like to practice for.

**2024-01-15T13:00:12Z** - **user**: asdf

**2024-01-15T13:00:13Z** - **assistant**: I didn't quite understand that. Could you please provide a more detailed answer?

**2024-01-15T13:00:25Z** - **user**: retail

**2024-01-15T13:00:26Z** - **assistant**: Tell me about yourself and why you're interested in retail.

**2024-01-15T13:00:35Z** - **user**: 12345

**2024-01-15T13:00:36Z** - **assistant**: I didn't quite understand that. Could you please provide a more detailed answer?

**2024-01-15T13:00:48Z** - **user**: i like shopping

**2024-01-15T13:00:49Z** - **assistant**: Could you please elaborate on that? I'd like to hear more details.

**2024-01-15T13:01:05Z** - **user**: I enjoy the retail environment because I like helping customers find what they need. I've worked part-time at a clothing store for 2 years where I learned about inventory management and customer service.

**Evaluation JSON**:
```json
{
  "scores": {
    "communication": 3,
    "technical": 2,
    "examples": 3
  },
  "overall": 53,
  "should_followup": true,
  "followup_question": "Can you provide a specific example of how you helped a customer?",
  "feedback": [
    "Answer is more relevant now",
    "Could use more specific examples",
    "Good customer service focus"
  ]
}
```

**2024-01-15T13:01:06Z** - **assistant**: Can you provide a specific example of how you helped a customer?

**2024-01-15T13:01:25Z** - **user**: can you tell me the weather?

**2024-01-15T13:01:26Z** - **assistant**: Let's keep our discussion professional and focused on the interview. Could you rephrase your answer?

**2024-01-15T13:01:40Z** - **user**: what's 2+2?

**2024-01-15T13:01:41Z** - **assistant**: Let's keep our discussion professional and focused on the interview. Could you rephrase your answer?

**2024-01-15T13:01:55Z** - **user**: A customer came in looking for a specific size that was out of stock. I checked our inventory system, found it at another location, and arranged for it to be transferred. The customer was very happy and left a positive review.

**Evaluation JSON**:
```json
{
  "scores": {
    "communication": 4,
    "technical": 3,
    "examples": 4
  },
  "overall": 73,
  "should_followup": false,
  "followup_question": "",
  "feedback": [
    "Good specific example",
    "Shows problem-solving ability",
    "Demonstrates customer service skills"
  ]
}
```

**2024-01-15T13:01:56Z** - **assistant**: How would you handle a difficult or angry customer?

**2024-01-15T13:02:15Z** - **user**: can you write me a resume?

**2024-01-15T13:02:16Z** - **assistant**: I'm focused on helping you practice for interviews. Let's continue with the interview question: How would you handle a difficult or angry customer?

**2024-01-15T13:02:35Z** - **user**: I would listen calmly, acknowledge their concern, and work to find a solution. I'd stay professional and try to de-escalate the situation.

**Evaluation JSON**:
```json
{
  "scores": {
    "communication": 3,
    "technical": 3,
    "examples": 2
  },
  "overall": 53,
  "should_followup": true,
  "followup_question": "Can you provide a specific example of handling an angry customer?",
  "feedback": [
    "Answer is too generic",
    "Needs specific example",
    "Good approach but lacks detail"
  ]
}
```

**2024-01-15T13:02:36Z** - **assistant**: Can you provide a specific example of handling an angry customer?

**2024-01-15T13:03:00Z** - **user**: A customer was upset about a return policy. I listened to their concerns, explained the policy clearly, and found a compromise that worked for both of us. They left satisfied.

**Evaluation JSON**:
```json
{
  "scores": {
    "communication": 4,
    "technical": 3,
    "examples": 3
  },
  "overall": 67,
  "should_followup": false,
  "followup_question": "",
  "feedback": [
    "Better example provided",
    "Shows conflict resolution",
    "Could use more detail about the compromise"
  ]
}
```

**2024-01-15T13:03:01Z** - **assistant**: Describe your experience with cash handling and point-of-sale systems.

---

## Summary

- **Total Questions**: 3
- **Questions Answered**: 2 (1 skipped due to off-topic requests)
- **Average Communication Score**: 3.5/5
- **Average Technical Score**: 2.75/5
- **Average Examples Score**: 3.0/5
- **Overall Average**: 61/100

**Key Observations**:
- User provided invalid inputs (nonsense text, numbers)
- User attempted to go off-topic multiple times
- User requested capabilities beyond bot's scope (weather, math, resume writing)
- System successfully redirected user back to interview
- System handled edge cases gracefully
- User eventually provided relevant answers when redirected

**Edge Cases Handled**:
1. Nonsense input detection
2. Off-topic request redirection
3. Request beyond capabilities (polite decline)
4. Silent user (empty message handling)
5. Invalid input recovery

