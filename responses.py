from difflib import get_close_matches
import json

# Returns the best matched question based on knowledge
def get_best_match(user_question: str, questions: dict) -> str | None:
  questions: list[str] = [q for q in questions]
  matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6) # Only 1 match possible

  # Return best match
  if matches:
    return matches[0]
  
# Read user input (i.e., Discord msg)
def get_response(message: str, knowledge: dict) -> str:
  '''
  WIP: Command prefix ****
  if message[0] != "!":
    return
  '''
  best_match: str | None = get_best_match(message, knowledge)

  if answer := knowledge.get(best_match): 
    return answer
  # Ignore message if its not part of knowledge
  else:
    return
  
def load_knowledge(file: str) -> dict:
  with open(file, "r") as f:
    return json.load(f)
  


if __name__ == "__main__":
  test_knowledge: dict = load_knowledge("knowledge.json")
  test_response: str = get_response("who is you?", knowledge=test_knowledge)
  print(test_response)