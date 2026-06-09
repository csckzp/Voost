import subprocess
from pathlib import Path

def process_audio_with_subharmonics(input_file, output_file):
    # [0:a] is the input
    # asplit[main][sub] splits the signal
    # [sub] gets lowpassed and distorted to create artificial body
    # [main][sub] amix blends them back together
    filter_complex = (
        "asplit[main][sub];"
        "[sub]lowpass=f=120,aecho=0.8:0.9:1000:0.3,volume=0.5[sub_processed];"
        "[main][sub_processed]amix=inputs=2:duration=first:dropout_transition=0,"
        "lowshelf=f=200:g=4,highshelf=f=5000:g=3,"
        "compand=.3|.3:6:-60/-60|-10/-10:6:0:-90:0.2,"
        "loudnorm"
    )
    
    cmd = [
        "ffmpeg", "-y", "-i", str(input_file),
        "-filter_complex", filter_complex,
        "-c:a", "pcm_s16le",
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Processed: {input_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

# Example setup for parallel execution
from concurrent.futures import ProcessPoolExecutor

input_dir = Path("./raw_recordings")
output_dir = Path("./processed_recordings")
output_dir.mkdir(exist_ok=True)

files = list(input_dir.glob("*.wav"))

with ProcessPoolExecutor() as executor:
    for file in files:
        executor.submit(process_audio_with_subharmonics, file, output_dir / file.name)