import streamlit as st
import openai
import rubric
import re
import example
from collections import defaultdict


def analyze_emotional_competencies(conversation):
    # Initialize the OpenAI API client
    openai.api_key = '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'

    # Analyze the conversation and assign points to each participant
    scores = {}
    # for participant, utterances in conversation.items():
    #     # Concatenate all utterances of the participant into a single string
    #     text = " ".join(utterances)

    # Call the OpenAI API for language analysis
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-16k',
        messages=[
            {"role": "system",
             "content": f"You are a psychologist. ${rubric} that is big five categories of personality traits and "
                        f"three detail trasit levels then you can give a score to the participant based analysis."
                        f"You should give a score to the sentence based on the analysis."
                        f"Here is example ${example}"
                        f"위 답변을 보며 각 문장을 분석하고 그 이유와 점수를 제공한 다음 A와 B의 총점을 제시해주세요. "
                        f"5개의 역량과 15개의 하위 역량을 제공한 후 2-5사람의 대화를 업로드 하면 이를 분석하여 아래와 같은 출력을 보여주세요."
                        f"출력은 첫째, 각 개인별로 5개의 역량과 15개의 하위역량 별 총점수, 둘째, 위에서 제시한 것처럼 각 대화의 문장별로 분석한 근거와 점수 제시해주세요."
                        f"점수는 각각 0~2점 사이 정수입니다."},
            {"role": "user", "content": str(conversation)}
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

    # # Process the API response and assign points based on the rubric
    # answer = str(response.choices[0].message).strip()
    # competency_scores = []
    # for competency, criteria in rubric.items():
    #     competency_score = 0
    #     for score, description in criteria.items():
    #         if description.lower() in answer.lower():
    #             competency_score = int(score)
    #             break
    #     competency_scores.append(competency_score)
    # scores[participant] = sum(competency_scores) / len(competency_scores)

    return response


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

        upload_lines = uploaded_file.read().decode('utf-8')  # .splitlines()

                
        dialogs = defaultdict(list)

        # 각 참석자의 대화 추출
        for match in re.finditer(r'(참석자 \d+)\s*(.*?)\s*(?=(참석자 \d+)|$)', upload_lines, re.DOTALL):
            participant, dialog = match.group(1), match.group(2)
            
            # 문장 내부의 개행 문자를 공백으로 치환
            dialog = dialog.replace('\n', ' ').strip()

            # URL이나 문장이 아닌 문자열 제외
            if 'clovanote.naver.com' in dialog:
                dialog = dialog.split('clovanote.naver.com')[0].strip()
            
            # 대화를 참석자의 리스트에 추가
            dialogs[participant].append(dialog)

        # 결과 출력
        for participant, dialog in dialogs.items():
            st.write(f'{participant}의 대화: {dialog}')

   

        # Analyze the conversation and get the scores
        scores = analyze_emotional_competencies(user_list)
        st.write(scores.choices[0].message)
        #
        # # Display the scores
        # for participant, score in scores.items():
        #     st.write(f"{participant}: {score}")

        # st.write(conversation)


if __name__ == '__main__':
    main()
