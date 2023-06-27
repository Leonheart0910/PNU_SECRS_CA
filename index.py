import re
from collections import defaultdict

import openai
import pandas as pd
import streamlit as st
import plotly.express as px  # 5.15.0
import pandas as pd
import numpy as np  # 1.24.3
import rubric

import construct

gpt_model = 'gpt-4'
gpt_temperature = 0.1
gpt_top_p = 1


def analyze_emotional_competencies(conversation):
    global gpt_model
    global gpt_temperature
    global gpt_top_p

    # Initialize the OpenAI API client
    openai.api_key = 'YOUR_API_KEY'
    print(conversation)

    # Call the OpenAI API for language analysis
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=[
            {"role": "system",
             "content": construct.GPT_CONSTRUCT['SYSTEM_CONTENT']
             },
            {"role": "user",
             "content": str(conversation) + construct.GPT_CONSTRUCT['USER_CONTENT']
             }
        ],
        temperature=gpt_temperature,
        n=1,
        top_p=gpt_top_p,
        stop=None,
    )

    return response


# Streamlit app

# Function to process uploaded conversation file
def process_uploaded_file(uploaded_file):
    upload_lines = uploaded_file.read().decode('utf-8')

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
    scores = analyze_emotional_competencies(dialogs)
    st.markdown(scores.choices[0].message.content)
    print(scores.choices[0].message.content)

    markdown_text = scores.choices[0].message.content

    # "### 총점" 아래의 내용만 추출
    total_score_section = markdown_text.split('### 총점')[-1]

    # 참석자의 점수를 추출
    scores = re.findall(r'\|\s참석자 \d\s\|\s(\d)\s\|\s(\d)\s\|\s(\d)\s\|\s(\d)\s\|\s(\d)\s\|', total_score_section)

    # 점수를 int형으로 변환하고 리스트로 출력
    scores = [[int(score) for score in participant_score] for participant_score in scores]
    # 1차원 리스트로 변경
    flattened_list = list(itertools.chain(*scores))
    num = len(scores)
    value = '자기인식', '자기관리', '사회적인식', '관계인식', '책임있는의사결정'
    variable = list(value * num)
    list_box = []
    for i in range(len(scores)):
        list_box.append(list(str(i + 1) * 5))
    group = list(itertools.chain(*list_box))

    df = pd.DataFrame({'value':flattened_list, 'variable':variable, 'group' : group})
    fig = px.line_polar(df, r='value', theta='variable', line_close=True,
                        color='group', color_discrete_sequence=px.colors.sequential.Magma)
    fig.update_traces(fill='toself')



# Streamlit app
def main():
    global gpt_model
    global gpt_temperature
    global gpt_top_p

    st.title("Emotional Competency Analysis")
    gpt_model = st.selectbox("Select the model", ["gpt-4", "gpt-3.5-turbo-16k"])
    gpt_temperature = st.slider("Select the temperature", 0.0, 2.0, 0.1, 0.1,
                                help="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will "
                                     "make the output more random, while lower values like 0.2 will make it more "
                                     "focused and deterministic.\n\n"
                                     "We generally recommend altering this or top_p but not both.\n\n"
                                     "DEFAULT: 1.0\n\n"
                                     "WE HAVE CHANGED THIS VALUE")
    gpt_top_p = st.slider("Select the top_p", 0.0, 1.0, 1.0, 0.1,
                          help="An alternative to sampling with temperature, called nucleus sampling, where the model "
                               "considers the results of the tokens with top_p probability mass.\n"
                               "So 0.1 means only the tokens comprising the top 10% probability mass are "
                               "considered.\n\n"
                               "We generally recommend altering this or temperature but not both.")

    # File upload
    uploaded_file = st.file_uploader("Upload conversation file", type=['txt'])

    if uploaded_file is None:
        return

    dialogs = process_uploaded_file(uploaded_file)

    display_dialogs(dialogs)

    # Analyze the conversation and get the scores
    response = analyze_emotional_competencies(dialogs)
    st.markdown(response.choices[0].message.content)

    markdown_text = response.choices[0].message.content

    df, fig = extract_scores(markdown_text)

    st.plotly_chart(fig)
    st.dataframe(df[['group', 'variable', 'value']])


if __name__ == '__main__':
    main()
