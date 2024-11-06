import fitz  # PyMuPDF
import streamlit as st
from llama_cpp import Llama  # Assuming you've converted mistral into a llama-compatible model

# Load the mistral model
llm_model_path = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
llm = Llama(model_path=llm_model_path)


# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        extracted_text += f"\n--- Page {page_num + 1} ---\n"
        extracted_text += page.get_text("text")
    return extracted_text


# Initialize or update the conversation history in session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Streamlit App
st.title("PDF Text Extraction and Grading Assistant")
st.subheader("Upload your PDF files for analysis and marking.")

# File upload section
uploaded_pdf = st.file_uploader("Upload your PDF file", type="pdf")
answer_key_pdf = st.file_uploader("Upload Answer Key PDF", type="pdf")

if uploaded_pdf and answer_key_pdf:
    # Save uploaded PDFs
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_pdf.getbuffer())
    with open("answer_key.pdf", "wb") as f:
        f.write(answer_key_pdf.getbuffer())

    # Extract text from the PDFs
    extracted_text = extract_text_from_pdf("uploaded_file.pdf")
    answer_key_text = extract_text_from_pdf("answer_key.pdf")

    # Enhanced prompt focusing on differences for marking and feedback
    prompt = (
        f"You are a teacher evaluating a student's work (Text 1) against an answer key (Text 2). "
        f"Provide a mark out of 10 for the student's submission and give the reason for those marks, and include the following in your response:\n"
        f"1. Marks out of 10.\n"
        f"2. A detailed explanation of the marks given, specifically highlighting the differences between Text 1 and Text 2 that influenced the score.\n"
        f"3. Suggestions for improvement for any areas where marks were deducted.\n"
        f"4. If the student receives 9/10, explain why they did not receive full marks.\n"
        f"5. If the student receives 10/10, give a compliment and highlight what they did well.\n\n"
        f"Text 1 (Student's Work): {extracted_text}\n\n"
        f"Text 2 (Answer Key): {answer_key_text}\n\n"
        f"Your response must start with the format: 'Marks: X/10' (where X is the number)."
    )

    # Loop until a valid response with marks is received
    assistant_response = ""
    while "Marks:" not in assistant_response:
        response = llm(prompt)
        assistant_response = response['choices'][0]['text']

    # Update conversation history with the valid response
    st.session_state.conversation.append(f"Assistant: {assistant_response}")

    # Display the final response
    st.write(assistant_response)

    # Further questions section
    follow_up = st.text_input("You:", "")

    if follow_up:
        follow_up_prompt = f"The user asked: {follow_up}\nContext: {assistant_response}\nAnswer:"
        follow_up_response = llm(follow_up_prompt)

        # Add the user input and the assistant's response to the conversation history
        st.session_state.conversation.append(f"You: {follow_up}")
        st.session_state.conversation.append(f"Assistant: {follow_up_response['choices'][0]['text']}")

        # Display updated conversation history
        for message in st.session_state.conversation:
            st.write(message)
