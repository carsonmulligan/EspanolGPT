import openai
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
import re
import json


# List of YouTube video URLs
videos = [
    {"country": "El Salvador", "title": "Breve historia política de El Salvador", "url": "https://www.youtube.com/watch?v=-e17U_wI0QQ&t=611s"},
    {"country": "Mexico", "title": "Breve historia política de México", "url": "https://www.youtube.com/watch?v=FAr61EzegWo&t=214s"},
    # {"country": "Mexico", "title": "Los Aztecas: Capítulo I, El Origen (Documental Completo)", "url": "https://www.youtube.com/watch?v=HnbnJJD8Vu0"},
    # {"country": "Mexico", "title": "Porfirio Díaz: Líder Supremo de México", "url": "https://www.youtube.com/watch?v=7uO6VzN79eI&t=1548s"},
    # {"country": "Mexico", "title": "Programa Especial | Benito Juárez: La otra historia", "url": "https://www.youtube.com/watch?v=j5agGy_vQ_A"},
    # {"country": "Mexico", "title": "Emiliano Zapata: Caudillo de la Revolución Mexicana", "url": "https://www.youtube.com/watch?v=b2e8BVzmc9w"},
    # {"country": "Mexico", "title": "Pancho Villa: El centauro del norte. Capítulo 1", "url": "https://www.youtube.com/watch?v=KF4N1C0a0co"},
    # {"country": "Venezuela", "title": "Breve historia política de Venezuela", "url": "https://www.youtube.com/watch?v=EE0bm3d4mn4"},
    # {"country": "Honduras", "title": "Breve historia política de Honduras", "url": "https://www.youtube.com/watch?v=8bbYkTgz6nU"},
    # {"country": "Honduras", "title": "¿UN CONFLICTO DESATADO POR FÚTBOL? La Guerra que Empezó con un Partido ⚽️🔥", "url": "https://www.youtube.com/watch?v=5krESyH4BKg"},
    # {"country": "Guatemala", "title": "Breve historia política de Guatemala", "url": "https://www.youtube.com/watch?v=tXLhWHWGaao&t=61s"},
    # {"country": "Guatemala", "title": "Civilización perdida: Viaje a las Misteriosas Ciudades Mayas Perdidas | DOCUMENTAL Historia", "url": "https://www.youtube.com/watch?v=MUpzYayZ1ng"}
]

# Function to get YouTube video ID from URL
def get_video_id(url):
    video_id = re.findall(r'v=([^&]+)', url)
    return video_id[0] if video_id else None

# Function to get YouTube video transcript
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['es']).fetch()
        return ' '.join([t['text'] for t in transcript])
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Function to generate flashcards using OpenAI
def generate_flashcards(transcript):
    client = openai.OpenAI()
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates flashcards."},
            {"role": "user", "content": f"Crea tarjetas de estudio a partir de esta transcripción. Cada tarjeta debe tener un tema y una descripción del evento histórico. La transcripción es: {transcript}"}
        ],
        stream=True,
    )
    
    flashcards_content = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            flashcards_content += chunk.choices[0].delta.content
    return flashcards_content

flashcards_data = []

# Loop through videos, fetch transcripts, generate flashcards, and store them
for video in videos:
    video_id = get_video_id(video["url"])
    if video_id:
        transcript = get_transcript(video_id)
        if transcript:
            flashcards = generate_flashcards(transcript)
            flashcards_data.append({
                "country": video["country"],
                "title": video["title"],
                "url": video["url"],
                "flashcards": flashcards
            })

# Streamlit app to display videos and flashcards
st.title('Language and History Flashcards by Country')

for video in flashcards_data:
    with st.expander(f"{video['country']} - {video['title']}"):
        st.video(video["url"])
        if st.button(f"Show Flashcards for {video['title']}"):
            st.text_area('Flashcards', video["flashcards"], height=300)
