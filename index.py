import itertools
import re
from collections import defaultdict

import openai
import pandas as pd
import plotly.express as px  # 5.15.0
import streamlit as st

import construct

openai.api_key = 'YOUR_API_KEY'
gpt_model = 'gpt-4'
gpt_temperature = 0.1
gpt_top_p = 1


def analyze_emotional_competencies(messages):
    global gpt_model
    global gpt_temperature
    global gpt_top_p

    # Initialize the OpenAI API client
    # print(conversation)

    # Call the OpenAI API for language analysis
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
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

    # Extract conversation for each participant
    for match in re.finditer(r'(참석자 \d+)\s*(.*?)\s*(?=(참석자 \d+)|$)', upload_lines, re.DOTALL):
        participant, dialog = match.group(1), match.group(2)

        # Replace newline characters with spaces within sentences
        dialog = dialog.replace('\n', ' ').strip()

        # Exclude URLs or non-sentence strings
        if 'clovanote.naver.com' in dialog:
            dialog = dialog.split('clovanote.naver.com')[0].strip()

        # Add the dialog to the participant's list
        dialogs[participant].append(dialog)

    return dialogs


# Function to display conversation for each participant
def display_dialogs(dialogs):
    for participant, dialog in dialogs.items():
        st.write(f'{participant}의 대화: {dialog}')


# Function to extract scores from the analyzed conversation
def extract_scores(markdown_text):
    total_score_section = markdown_text.split('### 총점')[-1]
    response = re.findall(r'\|\s참석자 \d\s\|\s(\d)\s\|\s(\d)\s\|\s(\d)\s\|\s(\d)\s\|\s(\d)\s\|', total_score_section)
    response = [[int(score) for score in participant_score] for participant_score in response]
    flattened_list = list(itertools.chain(*response))
    num = len(response)
    value = '자기인식', '자기관리', '사회적인식', '관계인식', '책임있는의사결정'
    variable = list(value * num)
    list_box = []
    for i in range(len(response)):
        list_box.append(list(str(i + 1) * 5))
    group = list(itertools.chain(*list_box))

    df = pd.DataFrame({'value': flattened_list, 'variable': variable, 'group': group})
    fig = px.line_polar(df, r='value', theta='variable', line_close=True,
                        color='group', color_discrete_sequence=px.colors.sequential.Magma)
    fig.update_traces(fill='toself')

    return df, fig


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

    messages = [
        {
            "role": "system",
            "content": construct.GPT_CONSTRUCT['SYSTEM_CONTENT']
        },
        {
            "role": "user",
            "content": str(dialogs) + construct.GPT_CONSTRUCT['USER_CONTENT']
        }
    ]

    # Analyze the conversation and get the scores
    response = analyze_emotional_competencies(messages)
    st.markdown(response.choices[0].message.content)

    markdown_text = response.choices[0].message.content

    df, fig = extract_scores(markdown_text)

    st.plotly_chart(fig)
    st.dataframe(df[['group', 'variable', 'value']])

    if response.choices[0].finish_reason == "stop":
        st.markdown("### 대화가 끝났습니다.")
        st.info("결과가 완전하지 않다면 재시도해주세요.")
        if st.button("재시도", key="retry", use_container_width=True):
            analyze_emotional_competencies(messages)
    else:
        st.error("### 대화가 끝나지 않았습니다.")
        if st.button("Continue", key="continue", use_container_width=True):
            main()


if __name__ == '__main__':
    main()
