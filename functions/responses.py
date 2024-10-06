from difflib import get_close_matches
import json


# Returns the best matched question based on knowledge
def get_best_match(user_question: str, questions: dict) -> str | None:
  """
  Finds and returns the best matching question from a list of known questions based on the user's input.

  Parameters
  ----------
  user_question: str
    The user's question as input.
  questions: dict
    A dictionary containing known questions as keys.

  Returns
  -------
  str:
    The best-matched question if a close match is found.
  None:
    If no match is found that meets the cutoff criteria.
  """
  questions: list[str] = [q for q in questions]
  matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6) # Only 1 match possible

  # Return best match
  if matches:
    return matches[0]
  

# Read user input (i.e., Discord msg)
def get_response(message: str, knowledge: dict) -> str:
  """
  Processes the user's message, finds the closest matching question in the knowledge base, and returns the corresponding response.

  Parameters
  ----------
  message: str
    The user's input message to be matched with a known question.
  knowledge: dict
    A dictionary containing known questions as keys and their corresponding answers as values.

  Returns
  -------
  str:
    The response corresponding to the best-matched question.
  None:
    If no match is found, the function returns None and ignores the message.
  """
  best_match: str | None = get_best_match(message.lower(), knowledge)

  if answer := knowledge.get(best_match): 
    return answer
  # Ignore message if its not part of knowledge
  else:
    return
  

def load_knowledge(file: str) -> dict:
  """
  Loads a JSON file and returns its contents as a dictionary.

  Parameters
  ----------
  file: str
    The file path of the JSON file to be loaded.

  Returns
  -------
  dict:
    A dictionary representing the contents of the loaded JSON file.
  """
  with open(file, "r") as f:
    return json.load(f)
  

if __name__ == "__main__":
  test_knowledge: dict = load_knowledge("knowledge.json")
  test_response: str = get_response("who is you?", knowledge=test_knowledge)
  print(test_response)