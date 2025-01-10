import streamlit as st
from audiorecorder import audiorecorder
import openai, os
from datetime import datetime
from gtts import gTTS
import base64

def STT(audio, apikey):
    filename = 'input.mp3'
    audio.export(filename, format='mp3')
    audio_file = open(filename, 'rb')
    api = openai.OpenAI(api_key=apikey)
    response = api.audio.transcriptions.create(model='whisper-1', file=audio_file)
    audio_file.close()
    os.remove(filename)
    return response.text

def ask_gpt(prompt, model, apikey):
    api = openai.OpenAI(api_key=apikey)
    response = api.chat.completions.create(
        model = model,
        message = prompt
    )
    gptResponse = response.choices[0].message.content
    return gptResponse

def TTS(response):
    filename = 'output.mp3'
    tts = gTTS(text=filename, lang='ko')
    tts.save(filename)
    with open(filename, 'rb') as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'''
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            '''
        st.markdown(md, unsafe_allow_html=True,)
    os.remove(filename)

def main():
    st.set_page_config(
        page_title='음성 비서 프로그램',
        layout='wide'
    )

    if 'chat' not in st.session_state:
        st.session_state['chat'] = []

    if 'OPENAI_API' not in st.session_state:
        st.session_state['OPENAI_API'] = ''

    if 'message' not in st.session_state:
        st.session_state['message'] = [
            {'role':'system', 'content':'You are thoughtful assistant. Respond to all input in 25 words and answer in korean'}
        ]

    if 'check_audio' not in st.session_state:
        st.session_state['check_audio'] = False

    st.header('음성 비서 프로그램')

    st.markdown('---')

    with st.expander('음성 비서 프로그램에 관하여', expanded=True):
        st.write(
            '''
            - UI : Streamlit 활용
            - STT(Speech-To-Text) : Open AI의 Whisper AI 활요
            - 답변 : Open AI의 GPT 모델
            - TTS(Text-To-Speech) : Google Translate TTS
            '''
        )
        st.markdown('')

    with st.sidebar:
        st.session_state["OPENAI_API"] = st.text_input(label='OpenAI API Key', placeholder='Enter your API Key', value='', type='password')
        st.markdown('---')

        model = st.radio(label='GPT 모델', options=['gpt-4', 'gpt-3.5-turbo'])
        st.markdown('---')

        if st.button(label='초기화'):
            st.session_state['chat'] = []
            st.session_state['message'] =[
                {'role':'system', 'content':'You are thoughtful assistant. Respond to all input in 25 words and answer in korean'}
            ]
            st.session_state['check_reset'] = True
            
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('질문')
        audio = audiorecorder('클릭하여 녹음하기', '녹음중....')
        if (audio.duration_seconds>0) and (st.session_state['check_reset']==False):
            st.audio(audio.export().read())
            question=STT(audio, st.session_state['OPENAI_API'])
            now=datetime.now().strftime('%H:%M')
            st.session_state['chat'] = st.session_state['chat'] + [('user', now, question)]
            st.session_state['message'] = st.session_state['message'] + [{'role':'user', 'content':question}]

    with col2:
        st.subheader('답변')
        if (audio.duration_seconds>0) and (st.session_state['check_reset']==False):
            response = ask_gpt(st.session_state['message'], model, st.session_state['OPENAI_API'])
            st.session_state['mesage'] = st.session_state['message'] + [{'role':'system', 'content':response}]
            now=datetime.now().strftime('%H:%M')
            st.session_state['chat'] = st.session_state['chat'] + [('bot', now, response)]
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")

if __name__ == '__main__':
    main()