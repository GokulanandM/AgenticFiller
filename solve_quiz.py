"""Quiz solver using Azure OpenAI agent."""
import asyncio
import json
from config import settings
from agents.azure_agent import AzureFormAgent

def solve_quiz():
    """Solve the quiz questions using Azure OpenAI."""
    
    # Get Azure OpenAI credentials from config
    api_key = settings.azure_api_key
    endpoint = settings.azure_endpoint
    deployment_id = settings.azure_deployment_id
    
    if not api_key or not endpoint:
        print("ERROR: Azure OpenAI credentials not configured in .env file")
        print("Please ensure AZURE_API_KEY and AZURE_ENDPOINT are set")
        return
    
    print("Using Form Automation Agent's Azure OpenAI connection...")
    print(f"   Endpoint: {endpoint}")
    print(f"   Model: {deployment_id}")
    print("\n" + "="*60)
    print("QUIZ SOLVER - Answering Questions")
    print("="*60 + "\n")
    
    # Initialize the agent
    agent = AzureFormAgent(api_key, endpoint, deployment_id)
    
    # Quiz questions
    quiz = [
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["A. Earth", "B. Mars", "C. Jupiter", "D. Venus"]
        },
        {
            "question": "What is the largest ocean on Earth?",
            "options": ["A. Atlantic Ocean", "B. Indian Ocean", "C. Arctic Ocean", "D. Pacific Ocean"]
        },
        {
            "question": "Who wrote the play Romeo and Juliet?",
            "options": ["A. Charles Dickens", "B. William Shakespeare", "C. Jane Austen", "D. Mark Twain"]
        },
        {
            "question": "What is the chemical symbol for Gold?",
            "options": ["A. Ag", "B. Au", "C. Gd", "D. Go"]
        },
        {
            "question": "Which country is known as the Land of the Rising Sun?",
            "options": ["A. China", "B. South Korea", "C. Japan", "D. Thailand"]
        },
        {
            "question": "How many continents are there on Earth?",
            "options": ["A. 5", "B. 6", "C. 7", "D. 8"]
        },
        {
            "question": "What is the hardest natural substance on Earth?",
            "options": ["A. Iron", "B. Gold", "C. Diamond", "D. Quartz"]
        },
        {
            "question": "Who was the first person to walk on the Moon?",
            "options": ["A. Buzz Aldrin", "B. Yuri Gagarin", "C. Neil Armstrong", "D. Michael Collins"]
        },
        {
            "question": "Which gas do plants primarily use for photosynthesis?",
            "options": ["A. Oxygen", "B. Nitrogen", "C. Carbon Dioxide", "D. Hydrogen"]
        },
        {
            "question": "What is the capital city of Australia?",
            "options": ["A. Sydney", "B. Melbourne", "C. Perth", "D. Canberra"]
        }
    ]
    
    answers = []
    
    for i, q in enumerate(quiz, 1):
        print(f"Question {i}: {q['question']}")
        for option in q['options']:
            print(f"   {option}")
        
        # Create prompt for Azure OpenAI
        prompt = f"""Answer this multiple choice question. Provide only the letter (A, B, C, or D) of the correct answer.

Question: {q['question']}
Options:
{chr(10).join(q['options'])}

Answer with only the letter (A, B, C, or D):"""
        
        try:
            response = agent.client.chat.completions.create(
                model=deployment_id,
                messages=[
                    {"role": "system", "content": "You are a quiz expert. Answer multiple choice questions accurately. Respond with only the letter (A, B, C, or D)."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            answer = response.choices[0].message.content.strip().upper()
            # Extract just the letter if it includes extra text
            if len(answer) > 1:
                answer = answer[0] if answer[0] in ['A', 'B', 'C', 'D'] else answer
            
            # Find the full answer text
            option_index = ord(answer) - ord('A')
            if 0 <= option_index < len(q['options']):
                answer_text = q['options'][option_index].split('. ', 1)[1] if '. ' in q['options'][option_index] else q['options'][option_index]
            else:
                answer_text = "Invalid answer"
            
            print(f"   [ANSWER] Agent's Answer: {answer} - {answer_text}")
            answers.append({"question": i, "answer": answer, "text": answer_text})
            print()
            
        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            answers.append({"question": i, "answer": "ERROR", "text": str(e)})
            print()
    
    # Summary
    print("="*60)
    print("QUIZ SUMMARY")
    print("="*60)
    print(f"\nTotal Questions: {len(quiz)}")
    print(f"Answered: {len([a for a in answers if a['answer'] != 'ERROR'])}")
    print(f"Errors: {len([a for a in answers if a['answer'] == 'ERROR'])}")
    print("\nAll Answers:")
    for ans in answers:
        print(f"  Q{ans['question']}: {ans['answer']} - {ans['text']}")
    
    return answers

if __name__ == "__main__":
    solve_quiz()
