import os
import glob
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

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

if __name__ == "__main__":
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

    if not files:
        print("No files to merge.")


    video_or_audio = int(input("Enter \n1 to create a video or \n2 to create an audio file: "))
    output_filename = input("Enter the output file name: ")

    if video_or_audio == 1:
        merge_media(files, output_filename, media_type='video')
    elif video_or_audio == 2:
        merge_media(files, output_filename, media_type='audio')
    else:
        print("Invalid choice.")