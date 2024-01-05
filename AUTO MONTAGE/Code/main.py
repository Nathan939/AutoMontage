import os
from shutil import copyfile
from google.cloud import speech_v1p1beta1 as speech
from moviepy.editor import VideoFileClip, TextClip, AudioFileClip, concatenate_videoclips

# Constantes
VIDEO_INPUT_PATH = "D:\AUTO MONTAGE\test.MOV"
OUTPUT_FOLDER = "D:\AUTO MONTAGE\Output"
VIDEO_COPY_PATH = os.path.join(OUTPUT_FOLDER, "video_copy.mp4")
MUSIC_FOLDER = "D:\AUTO MONTAGE\Musique"

# Définir le chemin vers le fichier JSON de la clé d'API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\AUTO MONTAGE\api-key.json"

def transcribe_audio(audio_file_path):
    client = speech.SpeechClient()

    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        print(f"Error in transcription: {e}")
        raise  # Re-raise the exception to propagate it

    text = ""
    for result in response.results:
        text += result.alternatives[0].transcript + " "

    return text

def add_subtitles(video_clip, subtitles_text):
    subtitle_clip = TextClip(subtitles_text, fontsize=24, color="white")
    subtitle_clip = subtitle_clip.set_pos(("center", "bottom")).set_duration(video_clip.duration)
    video_with_subtitles = concatenate_videoclips([video_clip, subtitle_clip])
    return video_with_subtitles

def choose_music_based_on_speech_rate(speech_rate, music_folder):
    music_files = [f for f in os.listdir(music_folder) if os.path.isfile(os.path.join(music_folder, f))]

    if not music_files:
        raise Exception(f"No music files found in {music_folder}")

    # Trier les fichiers de musique en fonction de la proximité du débit de parole
    music_files.sort(key=lambda x: abs(int(x.split("_")[1]) - speech_rate))
    
    # Récupérer le fichier de musique le plus proche du débit de parole souhaité
    chosen_music = music_files[0]

    # TODO: Traitement du fichier de musique choisi, par exemple, récupérer le chemin complet
    chosen_music_path = os.path.join(music_folder, chosen_music)
    return chosen_music_path

def find_most_relevant_file(folder, target_rate):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    
    if not files:
        raise Exception(f"No files found in {folder}")

    # Exemple : choisir le fichier le plus proche de la cible (à adapter selon les critères)
    files.sort(key=lambda x: abs(int(x.split("_")[1]) - target_rate))

    return files[0]

def main():
    # Vérifier les dépendances nécessaires
    try:
        import speech_v1p1beta1 as speech  # Vérifier si la bibliothèque Google Speech est installée
        import moviepy  # Vérifier si la bibliothèque MoviePy est installée
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install the required libraries using 'pip install -r requirements.txt'")
        return

    # Copier la vidéo d'origine dans le dossier de sortie
    copyfile(VIDEO_INPUT_PATH, VIDEO_COPY_PATH)

    # 1. Convertir la copie de la vidéo au format XML
    audio_file_path = os.path.join(OUTPUT_FOLDER, "video_audio.wav")
    subtitles_text = transcribe_audio(audio_file_path)

    # 2. Superposer des sous-titres à la copie de la vidéo d'entrée
    video_clip_copy = VideoFileClip(VIDEO_COPY_PATH)
    video_with_subtitles = add_subtitles(video_clip_copy, subtitles_text)

    # 3. Choisir la musique en fonction du débit de parole
    speech_rate = 150  # Exemple de débit de parole en mots par minute
    music_file = choose_music_based_on_speech_rate(speech_rate, MUSIC_FOLDER)

    # Charger la musique 
    music = AudioFileClip(os.path.join(MUSIC_FOLDER, music_file))

    # Superposer la musique à la vidéo avec sous-titres
    video_with_music = video_with_subtitles.set_audio(music)

    # 4. Sauvegarder la nouvelle vidéo au format MP4
    output_file_path = os.path.join(OUTPUT_FOLDER, "output_video.mp4")
    video_with_music.write_videofile(output_file_path, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    main()
