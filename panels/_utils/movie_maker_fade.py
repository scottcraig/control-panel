import os
import argparse
from . import utils


def movie_maker_fade(resolution='1920:1080', images_directory='images', seconds_per_image=8, fade_duration=1, color_space='yuv420p', output_file='/tmp/slideshow_fade.mp4'):
    """Example command with 5 images, per 
    https://superuser.com/questions/1464871/ffmpeg-crossfade-slideshow-image-size-not-decreased

        ffmpeg \
        -loop 1 -t 5 -i 1.jpg \
        -loop 1 -t 5 -i 2.png \
        -loop 1 -t 5 -i 3.png \
        -loop 1 -t 5 -i 4.png \
        -loop 1 -t 5 -i 5.png \
        -filter_complex \
        "[0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,format=yuva444p[bg]; \
        [1]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,format=yuva444p,fade=d=1:t=in:alpha=1,setpts=PTS-STARTPTS+4/TB[f0]; \
        [2]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,format=yuva444p,fade=d=1:t=in:alpha=1,setpts=PTS-STARTPTS+8/TB[f1]; \
        [3]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,format=yuva444p,fade=d=1:t=in:alpha=1,setpts=PTS-STARTPTS+12/TB[f2]; \
        [4]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,format=yuva444p,fade=d=1:t=in:alpha=1,setpts=PTS-STARTPTS+16/TB[f3]; \
        [bg][f0]overlay[bg1];[bg1][f1]overlay[bg2];[bg2][f2]overlay[bg3]; \
        [bg3][f3]overlay,format=yuv420p[v]" -map "[v]" -movflags +faststart out.mp4

    Keyword Arguments:
        resolution {str} -- [description] (default: {'1920:1080'})
        images_directory {str} -- [description] (default: {'images'})
        seconds_per_image {int} -- [description] (default: {7})
        fade_duration {int} -- [description] (default: {1})
        color_space {str} -- [description] (default: {'yuv420p'})
        output_file {str} -- [description] (default: {'/tmp/slideshow.mp4'})
    """

    image_files = sorted(os.listdir(images_directory))  # want them alphabetical so title image comes first!

    if image_files:
        print("\nFound images: {}\n".format(image_files))
    else:
        print("\nNo images found in '{}'!  Quitting this...\n".format(images_directory))
        return False

    num_images = len(image_files)
    image_inputs = ''
    base_filter = f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:-1:-1,setsar=1,format=yuva444p"
    
    for i in range(num_images):
        # '-loop 1 -t 5 -i images/input0.png' 
        image_inputs += f'-loop 1 -t {(seconds_per_image + fade_duration) * (num_images - i) + fade_duration } -i {os.path.join(images_directory, image_files[i])} '

    if num_images == 1:
        cmd = f'{utils.FFMPEG} {image_inputs} -pix_fmt {color_space} -vf {base_filter} {output_file}'
    else:
        # Create transition filter
        filter_complex = '-filter_complex "'
        seconds = 0
        for i in range(num_images):
            # first image only fades out
            if i == 0:
                image_filter = f"[{i}]{base_filter}[bg];"
            else:
                image_filter = f"[{i}]{base_filter},fade=d={fade_duration}:t=in:alpha=1,setpts=PTS-STARTPTS+{seconds}/TB[f{i - 1}];"
            
            filter_complex += image_filter
            seconds += seconds_per_image -1

        # overlays
        for i in range(num_images - 1):
            # [bg][f0]overlay[bg1];[bg1][f1]overlay[bg2];[bg2][f2]overlay[bg3];[bg3][f3]overlay

            filter_complex += f"[bg{'' if i==0 else i}][f{i}]overlay"

            if i != num_images - 2:  # last one is different, if not last one then add this
                filter_complex += f"[bg{i + 1}];"

        filter_complex += f",format={color_space}[v]"  # ...overlay,format=yuv420p[v]
        filter_complex += '"'  # close quote for the filter complex

        map_flag = '-map "[v]"'
        mov_flags = '-movflags +faststart'

        cmd = f'{utils.FFMPEG} {image_inputs} {filter_complex} {map_flag} {mov_flags} {output_file}'
    print(cmd)

    os.system(cmd)


if __name__ == "__main__":
    # execute only if run as a script

    parser = argparse.ArgumentParser(description='Generate a video file from a directory of images.')
    parser.add_argument('--images', type=str, help='directory to find the images ["images"]')
    parser.add_argument('--resolution', type=str, help='output video resolution ["1920:1080"]')
    parser.add_argument('--seconds', type=int, help='seconds per image [3]')
    parser.add_argument('--fade', type=int, help='fade duration between images [1]')
    parser.add_argument('--output', type=str, help='output file ["/tmp/slideshow.mp4"]')

    args = parser.parse_args()

    # If parameters are provided pass them to the function, otherwise defaults will be used.
    kwargs = {}
    if args.images:
        kwargs['images_directory'] = args.images
    if args.resolution:
        kwargs['resolution'] = args.resolution
    if args.seconds:
        kwargs['seconds_per_image'] = args.seconds
    if args.fade:
        kwargs['fade_duration'] = args.fade
    if args.output:
        kwargs['output_file'] = args.output

    movie_maker_fade(**kwargs)
