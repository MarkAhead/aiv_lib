import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from sympy import im
import os

posts_base_dir = "/Users/yadubhushan/Documents/workplace/prod/python_scripts/"
video_dir = "resources/social/insta/bollywood/659b1751-b275-4550-90ba-7163af9ea911"
video_dir_path = os.path.join(posts_base_dir, video_dir)
unique_file_name = str(uuid.uuid4())
output_file = os.path.join(posts_base_dir, unique_file_name + ".mp4")

def resize_and_crop(clip, width=1080, height=1920):
    # Calculate the aspect ratio of the clip
    clip_aspect_ratio = clip.size[0] / clip.size[1]
    target_aspect_ratio = width / height

    # Resize the clip while maintaining its aspect ratio
    if clip_aspect_ratio > target_aspect_ratio:
        # Clip is wider than target, resize based on width
        clip_resized = clip.resize(width=width)
    else:
        # Clip is taller than target, resize based on height
        clip_resized = clip.resize(height=height)

    # Crop or pad to achieve the desired dimensions
    clip_cropped = clip_resized.crop(
        x_center=clip_resized.size[0] / 2, y_center=clip_resized.size[1] / 2,
        width=width, height=height
    )
    return clip_cropped

def subtitle_position(t):
    # This will position the subtitle at the center horizontally and at the bottom vertically.
    # Adjust as needed.
    return ('center', 'bottom')

def create_video(videos):
    clips = []
    for video in videos:
        clip = VideoFileClip(video["path"]).subclip(video["start"], video["end"])
        clip = resize_and_crop(clip)  # Resize and crop the clip

        # Create a subtitle text clip with shadow
        txt_clip = (TextClip(video["subtitle"], fontsize=108, color='white')
           .set_pos(subtitle_position)
           .set_duration(clip.duration)
           .crossfadein(0.5)
           .crossfadeout(0.5))

        # Add a shadow for the subtitle for better visibility
        shadow = (TextClip(video["subtitle"], fontsize=108, color='black')
            .set_pos(('center', 'bottom'))
            .set_duration(clip.duration)
            .crossfadein(0.5)
            .crossfadeout(0.5))
        # Overlay the text clip on the video clip
        video_with_subtitle = CompositeVideoClip([clip, shadow, txt_clip])
        clips.append(video_with_subtitle)
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_file, fps=24)


if __name__ == "__main__":
    # for all mp4 files in the directory
    videos = []
    for file in os.listdir(video_dir_path):
        if file.endswith(".mp4"):
            video_data = {}
            video_data["path"] = os.path.join(video_dir_path, file)
            video_data["start"] = 0
            video_data["end"] = 5
            video_data["subtitle"] = "Subtitle for video " + file.split(".")[0]
            videos.append(video_data)

    create_video(videos)
