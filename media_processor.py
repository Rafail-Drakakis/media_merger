import os
import glob
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
import speech_recognition as sr

# Constants for file types
VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi']
AUDIO_EXTENSIONS = ['.mp3', '.wav']

def collect_filenames(extension):
    """
    Collect and confirm filenames with a specific extension in the current directory.
    """
    files = glob.glob(os.path.join(os.getcwd(), f'*{extension}'))
    if not files:
        print(f"No files with extension {extension} found.")
        exit(0)

    print("Collected files:")
    for file in files:
        print(file)

    confirm = input("Do you want to proceed with these files (yes/no)? ")
    if confirm.lower() != "yes":
        print("Operation canceled.")
        exit(0)

    with open('filenames.txt', 'w') as file:
        file.write('\n'.join(files))
    return files

def is_supported_file(file, extensions):
    """
    Check if the file has a supported extension.
    """
    return file.lower().endswith(tuple(extensions))

def merge_media(files, output_filename, media_type='video'):
    """
    Merge video or audio files into a single file.
    """
    clips = []
    for file in files:
        if not is_supported_file(file, VIDEO_EXTENSIONS if media_type == 'video' else AUDIO_EXTENSIONS):
            print(f"Skipping unsupported file: {file}")
            continue

        try:
            clip = VideoFileClip(file) if media_type == 'video' else AudioFileClip(file)
            clips.append(clip)
        except Exception as e:
            print(f"Error processing file: {file} - {e}")

    if not clips:
        print("No supported files to merge.")
        return

    try:
        final_clip = concatenate(clips, media_type)
        final_clip.write_videofile(output_filename) if media_type == 'video' else final_clip.write_audiofile(output_filename)
        print(f"Merged files saved as {output_filename}")
    except Exception as e:
        print(f"Error writing {media_type} file: {e}")

def concatenate(clips, media_type):
    """
    Concatenate a list of clips based on media type.
    """
    if media_type == 'video':
        return concatenate_videoclips(clips, method='compose')
    elif media_type == 'audio':
        return concatenate_audioclips(clips)


def convert_video_to_text(input_filenames, read_from_file=False):
    """
    Convert video files to text using speech recognition.
    """
    recognizer = sr.Recognizer()
    for filename in input_filenames:
        if not is_supported_file(filename, VIDEO_EXTENSIONS + AUDIO_EXTENSIONS):
            print(f"Skipping unsupported file: {filename}")
            continue

        try:
            audio = extract_audio(filename)
            text = transcribe_audio(recognizer, audio)
            write_transcription(filename, text)
            if read_from_file:
                remove_original_file(filename)
        except Exception as e:
            print(f"Error processing file: {filename} - {e}")

    if not read_from_file:
        confirm_removal(input_filenames)

def extract_audio(filename):
    """
    Extract audio from a given file.
    """
    if is_supported_file(filename, VIDEO_EXTENSIONS):
        video = VideoFileClip(filename)
        audio = video.audio
    else:
        audio = AudioFileClip(filename)

    audio.write_audiofile("temp.wav", codec='pcm_s16le')
    return "temp.wav"

def transcribe_audio(recognizer, audio_filename):
    """
    Transcribe audio to text using Google's speech recognition.
    """
    with sr.AudioFile(audio_filename) as audio_file:
        audio = recognizer.record(audio_file)
    return recognizer.recognize_google(audio)

def write_transcription(filename, text):
    """
    Write the transcription to a file.
    """
    output_file_path = os.path.splitext(filename)[0] + ".txt"
    with open(output_file_path, "w") as output_file:
        output_file.write(text)
    os.remove("temp.wav")

def remove_original_file(filename):
    """
    Prompt user to remove the original file.
    """
    remove = input(f"Do you want to remove the original file '{filename}' (yes/no)? ")
    if remove.lower() == "yes":
        os.remove(filename)

def confirm_removal(filenames):
    """
    Prompt user to confirm removal of original files.
    """
    remove = input("Do you want to remove the original file(s) (yes/no)? ")
    if remove.lower() == "yes":
        for file in filenames:
            os.remove(file)

def convert_menu():
    """
    Display a menu for the user to choose how to convert video/audio files to text.
    """
    print("Convert Menu")
    choice = int(input("Enter \n1 to convert all the files in the current directory\n2 to enter filenames manually: "))

    if choice == 1:
        extension = input("Enter the extension you want: ")
        filenames = collect_filenames(extension)
    elif choice == 2:
        filenames = input("Enter the filenames (separated by commas): ").split(",")
    else:
        print("Invalid choice.")
        return

    convert_video_to_text(filenames, read_from_file=True)
    merge_transcribed_files(filenames, extension)

def merge_transcribed_files(input_filenames):
    """
    Merge transcribed text files into a single file.
    """
    merged_file = "merged.txt"
    text_files = [file for file in input_filenames if file.endswith('.txt')]

    with open(merged_file, "w") as merged_file_obj:
        for file_name in text_files:
            if file_name != merged_file:
                with open(file_name, "r") as file:
                    merged_file_obj.write("// " + file_name + "\n")
                    merged_file_obj.write(file.read())
                    merged_file_obj.write("\n\n")

    remove_txt_files = input("Do you want to remove the text files after merging (yes/no)? ")
    if remove_txt_files.lower() == "yes":
        for file in text_files:
            if file != merged_file:
                os.remove(file)

def merge_menu():
    """
    Display a menu for the user to choose how to merge media files.
    """
    print("Merge Menu")
    choice = int(input("Choose an option:\n1. Enter filenames directly\n2. Include all files in this directory with a specified extension: "))

    if choice == 1:
        files = input("Enter the file names to merge (separated by commas): ").split(",")
    elif choice == 2:
        extension = input("Enter the file extension (e.g., mp4, mp3, wav): ")
        files = collect_filenames(extension)
        if 'filenames.txt' in files:
            files.remove('filenames.txt')
    else:
        print("Invalid choice.")
        return

    if not files:
        print("No files to merge.")
        return

    video_or_audio = int(input("Enter \n1 to create a video or \n2 to create an audio file: "))
    output_filename = input("Enter the output file name: ")

    if video_or_audio == 1:
        merge_media(files, output_filename, media_type='video')
    elif video_or_audio == 2:
        merge_media(files, output_filename, media_type='audio')
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    choice = int(input("Enter \n1 Convert Menu \n2. Merge Menu: "))

    if choice == 1:
        convert_menu()
    elif choice == 2:
        merge_menu()
    else:
        print("Invalid choice.")