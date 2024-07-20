from nltk import sent_tokenize, word_tokenize
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def in_there(smaller_chunks, large_string):
    found = False
    for chunk in smaller_chunks:
        if chunk in large_string:
            found = True
            print(chunk)
            break

    if found:
        return True
    else:
        return False


def is_question(prompt):
    words = word_tokenize(prompt.lower())
    questions_words = ["what", "when", "where", "why", "how", "who", "whom", "is", "are", "do", "does", "can"]
    question_patterns = ["are you", "can you", "what is", "how are"]
    for pattern in question_patterns:
        if pattern in prompt.lower():
            return True
    if words[0] in questions_words:
        return True

    return False


def question_answering(question):
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")

        inputs = tokenizer(question, return_tensors="pt")
        outputs = model.generate(**inputs)
        result = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        # with open("intelligence/intelligence.txt", 'r') as file:
        #     # Step 2: Read the entire content of the file
        #     file_content = file.read()
        # input_text = f"question={question} context={file_content}"
        #
        # # Get the answer
        # result = pipe(input_text, max_length=128, num_return_sequences=1)
        # # Print the result
        return result[0]
    except Exception as e:
        print(f"Error loading model or generating text: {e}")


def format_transcription(transcription):
    # Tokenize to get sentences
    try:
        sentences = sent_tokenize(transcription)

        # Process each sentence
        formatted_sentences = []
        for sentence in sentences:

            isQuestion = is_question(sentence)

            # Add punctuation and capitalize
            if isQuestion:
                formatted_sentence = sentence.strip() + " ?"
            else:
                formatted_sentence = sentence.strip() + " ."

            # Capitalize first letter
            formatted_sentence = formatted_sentence.capitalize()

            # Append to formatted sentences list
            formatted_sentences.append(formatted_sentence)

        # Join sentences back into a single string
        formatted_transcription = " ".join(formatted_sentences)
        return formatted_transcription
    except Exception as e:
        print(f"Error formatting transcription: {e}")
