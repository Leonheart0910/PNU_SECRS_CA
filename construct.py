import rubric

GPT_CONSTRUCT = {
    "SYSTEM_CONTENT": f"You are a psychologist."
                      f"\nbelow is example"
                      f"문장 | 자기인식 | 자기관리 | 사회적 인식 | 관계 기술 | 책임있는 의사결정\n"
                      f"--- | --- | --- | --- | --- | ---\n"
                      f"'...' | %d | %d | %d | %d | %d\n"
                      f"'...' | %d | %d | %d | %d | %d\n"
                      f"'...' | %d | %d | %d | %d | %d\n"
                      f"'...' | %d | %d | %d | %d | %d\n"
                      f"'...' | %d | %d | %d | %d | %d\n",
    "USER_CONTENT": f"Below is rubric \n${rubric.rubric}\n"
                    f"참석자들의 대화내용을 잘 분석해서"
                    f"\n각각의 문장들을 Rubric의 5가지 지표로 나타내고 판단의 근거를 자세하게 설명한 뒤 markdown 표로 표현해줘."
                    f"단, 참석자별로 대화내용을 구분해서 참석자 수 만큼 표를 나누어 만들어줘."
                    f"이 표를 바탕으로 세부적으로 아주 구체적이게 0, 1, 2점의 점수를 매기는 판단의 근거를 자세하게 설명해줘"
                    f"마지막으로 참석자 각각 자기인식, 자기관리, 사회적 인식, 관계기술, 책임있는 의사결정에 대한 각각의 총점이 얼마인지 제일 마지막에 markdown 형태의 표로 출력해줘."
}
