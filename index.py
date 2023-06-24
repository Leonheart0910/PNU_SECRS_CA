import re
from collections import defaultdict

import openai
import streamlit as st

import rubric

import itertools



def analyze_emotional_competencies(conversation):
    # Initialize the OpenAI API client
    openai.api_key = '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'
    print(conversation)

    # Call the OpenAI API for language analysis
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[
            {"role": "system",
             "content": f"You are a psychologist."
                        f"\nbelow is example"
                        f"문장 | 자기인식 | 자기관리 | 사회적 인식 | 관계 기술 | 책임있는 의사결정\n"
                        f"--- | --- | --- | --- | --- | ---\n"
                        f"'...' | %d | %d | %d | %d | %d\n"
                        f"'...' | %d | %d | %d | %d | %d\n"
                        f"'...' | %d | %d | %d | %d | %d\n"
                        f"'...' | %d | %d | %d | %d | %d\n"
                        f"'...' | %d | %d | %d | %d | %d\n"
             },
            {"role": "user",
             "content": str(conversation) +
                        f"Below is rubric \n${rubric.rubric}\n"
                        f"참석자들의 대화내용을 잘 분석해서"
                        f"\n각각의 문장들을 Rubric의 5가지 지표로 나타내고 판단의 근거를 자세하게 설명한 뒤 markdown 표로 표현해줘."
                        f"단, 참석자별로 대화내용을 구분해서 참석자 수 만큼 표를 나누어 만들어줘."
                        f"이 표를 바탕으로 세부적으로 아주 구체적이게 0, 1, 2점의 점수를 매기는 판단의 근거를 자세하게 설명해줘"
                        f"마지막으로 참석자 각각 자기인식, 자기관리, 사회적 인식, 관계기술, 책임있는 의사결정에 대한 각각의 총점이 얼마인지 제일 마지막에 markdown 형태의 표로 출력해줘."
             }
        ],
        temperature=0.6,
        n=1,
        stop=None,
    )

    return response


# Streamlit app
def main():
    st.title("Emotional Competency Analysis")

    # File upload
    uploaded_file = st.file_uploader("Upload conversation file", type=['txt'])

    if uploaded_file is not None:
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
        value = '자기인식', '자기관리', '사회적인식', '관계인식','책임있는의사결정'
        variable = list(value * num)
        list_box = []
        for i in range(len(scores)):
            list_box.append(list(str(i + 1) * 5))
        group = list(itertools.chain(*list_box))

        df = pd.DataFrame(dict(flattened_list,variable,group
                      ))
        fig = px.line_polar(df, r='value', theta='variable', line_close=True,
                          color='group', color_discrete_sequence=px.colors.sequential.Magma)
        fig.update_traces(fill='toself')

    st.plotly_chart(fig)
    st.dataframe(df[['group', 'variable', 'value']])



if __name__ == '__main__':
    main()
