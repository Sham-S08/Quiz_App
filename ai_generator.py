import os, json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use gemini-2.5-flash — fastest, free, best for JSON tasks
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",  # forces clean JSON output
    }
)

SYSTEM_INSTRUCTION = """You are an expert quiz question creator.
Return ONLY a valid JSON object with this exact structure:
{
  "questions": [
    {
      "question": "Question text here?",
      "option1": "First option",
      "option2": "Second option",
      "option3": "Third option",
      "option4": "Fourth option",
      "answer": "option1"
    }
  ]
}
The answer field must be exactly one of: option1, option2, option3, option4.
No markdown. No explanation. Only the JSON object."""


def generate_context(topic):
    """Generate a knowledge summary when admin provides no context."""
    try:
        context_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"temperature": 0.5, "max_output_tokens": 500}
        )
        response = context_model.generate_content(
            f"Write a concise 200-word factual summary about: {topic}. Plain text only, no formatting."
        )
        return response.text.strip()
    except Exception as e:
        return f"General knowledge about {topic}"


def generate_questions(topic, difficulty, num=5, context=None):
    """
    Main function called by app.py
    Returns: (list of question dicts, context string used)
    """
    if not context:
        context = generate_context(topic)

    prompt = f"""Generate {num} {difficulty}-level multiple choice questions about: {topic}

Base the questions on this context:
{context}

Rules:
- Each question must have exactly 4 options
- Only one option must be correct
- The answer field must match the key of the correct option exactly (option1, option2, option3, or option4)
- Questions should be clear and unambiguous
- Focus on conceptual understanding, practical scenarios, and logical reasoning
- Avoid purely historical or trivial fact-based questions unless necessary
- Prefer application-based questions that test skills rather than memorization
- Include real-world or problem-solving situations when possible
- Avoid repeated question patterns and ensure variety
- Keep questions strictly relevant to the topic provided
- For {difficulty} difficulty: {'simple and straightforward conceptual checks' if difficulty == 'easy' else 'moderately challenging with applied logic and understanding' if difficulty == 'medium' else 'advanced, analytical, and requiring deep conceptual knowledge'}

Return the JSON object with {num} questions."""


    try:
        # Use system instruction via GenerativeModel with system_instruction
        structured_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json",
            }
        )
        response = structured_model.generate_content(prompt)
        raw = response.text.strip()

        # Clean up any accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        questions = data.get("questions", [])

        # Validate each question has required fields
        valid_questions = []
        for q in questions:
            if all(k in q for k in ["question", "option1", "option2", "option3", "option4", "answer"]):
                if q["answer"] in ["option1", "option2", "option3", "option4"]:
                    valid_questions.append(q)

        return valid_questions, context

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {raw}")
        return [], context
    except Exception as e:
        print(f"Gemini API error: {e}")
        return [], context