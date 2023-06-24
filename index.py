import streamlit as st
import openai
import rubric
import re


def analyze_emotional_competencies(conversation):
    # Initialize the OpenAI API client
    openai.api_key = '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'

    # Analyze the conversation and assign points to each participant
    scores = {}
    for participant, utterances in conversation.items():
        # Concatenate all utterances of the participant into a single string
        text = " ".join(utterances)

        # Call the OpenAI API for language analysis
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system",
                 "content": f"You are a psychologist. ${rubric} that is big five categories of personality traits and "
                            f"three detail trasit levels then you can give a score to the participant based analysis."
                            f"You should give a score to the sentence based on the analysis."},
                {"role": "user", "content": text}
            ],
            # functions=[
            #     {
            #         "name": "psychologist",
            #         "description": f"${rubric} that is big five categories of personality traits and three detail trasit levels then you can give a score to the participant based"
            #                        f"analysis.",
            #     }
            # ],
            # max_tokens=100,
            temperature=0.6,
            n=1,
            stop=None,
        )

        print(response)

        # Process the API response and assign points based on the rubric
        answer = str(response.choices[0].message).strip()
        competency_scores = []
        for competency, criteria in rubric.items():
            competency_score = 0
            for score, description in criteria.items():
                if description.lower() in answer.lower():
                    competency_score = int(score)
                    break
            competency_scores.append(competency_score)
        scores[participant] = sum(competency_scores) / len(competency_scores)

    return scores


# Streamlit app
def main():
    st.title("Emotional Competency Analysis")

    # File upload
    uploaded_file = st.file_uploader("Upload conversation file", type=['txt'])

    if uploaded_file is not None:
        # Read the uploaded file
        # conversation = {}
        # current_speaker = None
        # for line in uploaded_file.readlines()[3:-1]:
        #     line = line.strip().decode('utf-8')
        #     if line:
        #         # print(line)
        #         if line.startswith("참석자"):
        #             current_speaker = line.split()[1]
        #             conversation[current_speaker] = []
        #         else:
        #             conversation[current_speaker].append(line)

        upload_lines = uploaded_file.read().decode('utf-8')#.splitlines()

        # 정규식 패턴을 사용하여 사용자별로 분리
        user_pattern = r"(?<=참석자 )\d+"
        users = re.findall(user_pattern, upload_lines)

        # 사용자별로 텍스트 추출
        user_texts = re.split(user_pattern, upload_lines)[1:]

        # 사용자별로 분리된 텍스트를 리스트에 담기
        user_list = []
        for user, user_text in zip(users, user_texts):
            user_list.append(user_text.strip())

        st.write(user_list)

        # Analyze the conversation and get the scores
        # scores = analyze_emotional_competencies(conversation)
        #
        # # Display the scores
        # for participant, score in scores.items():
        #     st.write(f"{participant}: {score}")

        # st.write(conversation)


if __name__ == '__main__':
    main()
