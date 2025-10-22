import cv2
import os
import time
import numpy as np
import sys
import tempfile
import re

def check_dependencies():
    """
    Check if required dependencies are installed
    """
    try:
        import yt_dlp
        return True
    except ImportError:
        print("⚠️  yt-dlp is not installed!")
        print("📦 Install it with: pip install yt-dlp")
        return False

def is_youtube_url(url):
    """
    Check if the given string is a YouTube URL
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    
    return bool(re.match(youtube_regex, url))

def download_youtube_video(url, output_dir=None):
    """
    Download or get stream URL from YouTube video
    Downloads to system temp directory by default
    """
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp not found. Please install: pip install yt-dlp")
        return None
    
    # Use system temp directory or user-specified directory
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    # Create a temporary filename
    temp_filename = f"ascii_video_{int(time.time())}.mp4"
    output_path = os.path.join(output_dir, temp_filename)
    
    ydl_opts = {
        'format': 'best[height<=720]',  # Limit to 720p for performance
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
    }
    
    print(f"\n📥 Downloading YouTube video...")
    print(f"💾 Download location: {output_path}")
    print(f"🔗 URL: {url}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown')
            print(f"✅ Downloaded: {video_title}")
            return output_path
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None

def rgb_to_ansi(r, g, b):
    """
    Convert RGB values to ANSI 256-color code
    """
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232
    
    ansi = 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)
    return ansi

def enhance_contrast(frame, clip_limit=4.0, tile_size=8):
    """
    Enhance frame contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    """
    # Convert to LAB color space for better contrast enhancement
    if len(frame.shape) > 2:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
    else:
        l = frame
        a = None
        b = None
    
    # Apply CLAHE to L channel with higher clip limit for more contrast
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    l_enhanced = clahe.apply(l)
    
    # Merge back
    if a is not None and b is not None:
        enhanced_lab = cv2.merge([l_enhanced, a, b])
        enhanced_frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    else:
        enhanced_frame = l_enhanced
    
    return enhanced_frame

def adjust_brightness_contrast(frame, brightness=10, contrast=30):
    """
    Adjust brightness and contrast of frame
    """
    # Convert to float for better precision
    frame_float = frame.astype(np.float32)
    
    # Apply contrast
    frame_float = frame_float * (contrast / 127 + 1) - contrast
    
    # Apply brightness
    frame_float = frame_float + brightness
    
    # Clip values to valid range
    frame_float = np.clip(frame_float, 0, 255)
    
    return frame_float.astype(np.uint8)

def convert_frame_to_colored_ascii(frame, width=80, enhance=True):
    """
    Convert a frame to colored ASCII art using RGB values with enhanced contrast
    """
    # Enhanced ASCII character set with better contrast range
    ascii_chars = "  .:-=+*#%@"
    
    height = int(frame.shape[0] * width / frame.shape[1] / 2) 
    if height == 0:
        height = 1
    
    # Enhance contrast before processing
    if enhance:
        frame = enhance_contrast(frame, clip_limit=2.5, tile_size=8)
        frame = adjust_brightness_contrast(frame, brightness=15, contrast=35)
    
    resized_frame = cv2.resize(frame, (width, height))
    
    # Convert BGR to RGB
    if len(resized_frame.shape) > 2:
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    else:
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_GRAY2RGB)
        gray_frame = resized_frame
    
    # Additional contrast stretch on grayscale
    gray_frame = cv2.normalize(gray_frame, None, 0, 255, cv2.NORM_MINMAX)
    
    normalized = gray_frame / 255.0
    ascii_frame = ""
    
    for y, row in enumerate(normalized):
        for x, pixel in enumerate(row):
            # Get character based on brightness with better distribution
            index = int(pixel * (len(ascii_chars) - 1))
            char = ascii_chars[index]
            
            # Get color from RGB frame
            r, g, b = rgb_frame[y, x]
            
            # Boost color saturation
            hsv = cv2.cvtColor(np.uint8([[rgb_frame[y, x]]]), cv2.COLOR_RGB2HSV)[0][0]
            hsv[1] = min(255, int(hsv[1] * 1.3))  # Increase saturation by 30%
            boosted_rgb = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2RGB)[0][0]
            r, g, b = boosted_rgb
            
            color_code = rgb_to_ansi(r, g, b)
            
            # Add colored character with ANSI escape codes
            ascii_frame += f"\033[38;5;{color_code}m{char}\033[0m"
        ascii_frame += "\n"
    
    return ascii_frame

def play_video_in_terminal(video_path, width=80, fps=30, colored=True, enhance=True):
    """
    Play a video in the terminal using ASCII characters with optional color
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        return
    
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / video_fps if video_fps > 0 else 1.0 / fps
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"\n🎬 Starting playback...")
    print(f"Video FPS: {video_fps:.2f}")
    print(f"Total frames: {total_frames}")
    print(f"Color mode: {'ON' if colored else 'OFF'}")
    print(f"Contrast enhancement: {'ON' if enhance else 'OFF'}")
    print(f"\nPress Ctrl+C to stop\n")
    time.sleep(2)
    
    try:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if colored:
                ascii_art = convert_frame_to_colored_ascii(frame, width, enhance)
            else:
                ascii_art = convert_frame_to_ascii(frame, width, enhance)
            
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Display frame
            print(ascii_art)
            
            # Show progress
            frame_count += 1
            progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
            print(f"\n📊 Frame: {frame_count}/{total_frames} ({progress:.1f}%)")
            
            time.sleep(frame_delay)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Video playback stopped.")
    
    finally:
        cap.release()
        print("\n✅ Playback complete!")

def convert_frame_to_ascii(frame, width=80, enhance=True):
    """
    Convert a frame to ASCII art (grayscale version) with enhanced contrast
    """
    # Enhanced ASCII character set
    ascii_chars = "  .:-=+*#%@"
    
    height = int(frame.shape[0] * width / frame.shape[1] / 2) 
    if height == 0:
        height = 1
    
    # Enhance contrast
    if enhance:
        frame = enhance_contrast(frame, clip_limit=2.5, tile_size=8)
        frame = adjust_brightness_contrast(frame, brightness=15, contrast=35)
        
    resized_frame = cv2.resize(frame, (width, height))
    if len(resized_frame.shape) > 2:
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    else:
        gray_frame = resized_frame
    
    # Normalize for better contrast
    gray_frame = cv2.normalize(gray_frame, None, 0, 255, cv2.NORM_MINMAX)
    
    normalized = gray_frame / 255.0
    ascii_frame = ""
    
    for row in normalized:
        for pixel in row:
            index = int(pixel * (len(ascii_chars) - 1)) 
            ascii_frame += ascii_chars[index]
        ascii_frame += "\n"
    
    return ascii_frame

if __name__ == "__main__":
    print("=" * 60)
    print("🎥  COLORED ASCII VIDEO PLAYER  🎨")
    print("=" * 60)
    
    video_input = input("\n📁 Enter video path or YouTube URL: ").strip()
    
    temp_file = None
    video_path = video_input
    
    # Check if it's a YouTube URL
    if is_youtube_url(video_input):
        if not check_dependencies():
            sys.exit(1)
        
        print(f"\n💡 Videos are downloaded to: {tempfile.gettempdir()}")
        temp_file = download_youtube_video(video_input)
        if temp_file is None:
            print("❌ Failed to download YouTube video")
            sys.exit(1)
        video_path = temp_file
    
    try:
        width_input = int(input("📏 Enter terminal width (default 120): ") or "120")
    except ValueError:
        width_input = 120
    
    try:
        fps = int(input("⏱️  Enter FPS (default: use video FPS): ") or "0")
    except ValueError:
        fps = 0
    
    colored_input = input("🎨 Enable color? (y/n, default y): ").strip().lower()
    colored = colored_input != 'n'
    
    enhance_input = input("✨ Enable contrast enhancement? (y/n, default y): ").strip().lower()
    enhance = enhance_input != 'n'
    
    try:
        play_video_in_terminal(video_path, width_input, fps, colored, enhance)
    finally:
        # Clean up temporary file if it was created
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"🧹 Cleaned up temporary file: {temp_file}")
            except:
                pass