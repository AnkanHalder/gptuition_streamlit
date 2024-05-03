import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import plotly.express as px
import os

st.title("Generate A Quiz")
st.write("Crafting engaging quizzes can be time-consuming. Here's where large language models (LLMs) like Gemini come in. Gemini can streamline the process by generating quizzes on a chosen topic. Simply provide the subject, and Gemini will create a set of questions, often in JSON format. This format allows for easy integration with online quiz platforms or custom-built applications.")
st.markdown("---")

prompt = '''Please format the response as a Stringified JSON array of objects, where each object has the following properties:
- `QuestionNumber`: An integer indicating the question's numerical order (starting from 1). Use the format `question_number=n` in the prompt to specify this explicitly.
- `Question`: The actual question text, limited to 50 characters.
- `A`, `B`, `C`, and `D`: Four answer options, each also limited to 50 characters.
- `CorrectAnswer`: The single correct answer (A, B, C, or D).
- `Explanation`: A clear and concise explanation of the correct answer, adhering to a 200-character limit.
Do not use Markdown styles. No added text or replies. Should be parsable by JSON.parse() . No styling. no ```* .
**Example:**
[{"QuestionNumber": 1,"Question": "Capital of France?","A": "London","B": "Berlin","C": "Paris","D": "Rome","CorrectAnswer": "C","Explanation": "Paris is the capital of France."
  }, // ... more questions ]

'''

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
topic = st.chat_input("Please Enter A Topic Name eg. The French Revolution ")



if topic is not None and topic != "" and topic:
    print(topic)
    st.markdown(f"### **Take A quiz on** {topic}")

    prompt += f"\nPlease generate a questionnaire on the topic: **{topic}**\n**Number of questions:** 10 and response should be in unstyled JSON format"
    generated_text = llm.invoke(prompt).content.strip()
    if generated_text:
        try:
            with st.form(key="form-1"): 
                quizArray = json.loads(generated_text)
                answers = {}
                for i,quiz in enumerate(quizArray):
                    with st.container(border=True):
                        st.write(f"**{quiz["QuestionNumber"]}) {quiz["Question"]}**")
                        answer=st.radio("Options", [f"A) {quiz["A"]}",f"B) {quiz["B"]}",f"C) {quiz["C"]}",f"D) {quiz["D"]}"] ,key=f"{i}-QuizQuestionOptions")
                        answers[i] = answer
                submitted = st.form_submit_button("Submit")
                if submitted:
                    st.write("# Your Results")
                    count = 0
                    for i, quiz in enumerate(quizArray):
                        if (quiz['CorrectAnswer']==answers[i]):
                            count += 1
                        st.write(f"**{quiz["QuestionNumber"]}) {quiz["Question"]}**")
                        st.write(f"Chosen Answer: {answers[i]}")
                        st.write(f"Correct Answer: {quiz['CorrectAnswer']}")
                        st.write(f"Explanation: {quiz['Explanation']}")
                        st.write(f"Verdict: {str(quiz['CorrectAnswer']==answers[i])}")
                    correctAnswers = count
                    wrongAnswers = len(quizArray) - count
                    
                    fig = px.pie(
                        values=[correctAnswers, wrongAnswers],
                        names=["Correct", "Wrong"],
                        title="Correct vs. Wrong Answers",
                        color_discrete_sequence=[ "rgb(0, 102, 204)","rgb(102, 178, 255)"],
                        )
                    st.plotly_chart(fig)

        except Exception as e:
            st.markdown("An Error Occured!! Please try Again....")
            print(e)
else:
    st.write(" No Topic Has Yet Been Chosen ")
