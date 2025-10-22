# 🎥 Colored ASCII Video Player

A Python script that converts and plays videos (local or from YouTube) directly in your terminal using **colored ASCII art**.
It enhances video contrast, adjusts brightness, and supports both color and grayscale playback modes.

---

## 💡 Why I Created This

I came across a similar project and thought it was really cool — but it lacked proper color handling, contrast enhancement, and smooth playback. So I decided to improve it, adding features like enhanced contrast, brightness adjustment, and dynamic color rendering.
Plus, I had a lot of free time and wanted to challenge myself with something fun and creative — so why not turn videos into ASCII art?

---

## 🧩 Features

* 🎨 Colored and grayscale ASCII rendering
* ⚡ Adjustable brightness and contrast
* 🎬 Play videos directly from YouTube or local files
* 🧠 Automatic dependency checks
* 🧹 Cleans up temporary files after playback

---

## 🚀 Requirements

Make sure you have **Python 3.8+** installed, then install the required dependencies:

```bash
pip install opencv-python numpy yt-dlp
```

(If you don’t need GUI support, use `opencv-python-headless` instead.)

---

## 📦 Clone the Repository

You can clone this project directly from GitHub:

```bash
git clone https://github.com/H190K/mp4toasciichar-art.git
cd mp4toasciichar-art
```

Then you can run the program as described below.

---

## 🕹️ Usage

1. Run the program:

   ```bash
   python app.py
   ```

2. Enter a **video path** or a **YouTube URL** when prompted.

3. Adjust:

   * Terminal width (default: 120)
   * FPS (default: video’s FPS)
   * Color mode (`y/n`)
   * Contrast enhancement (`y/n`)

4. Watch your video play as ASCII art inside your terminal!

---

## 🧩 Example

```bash
python app.py
📁 Enter video path or YouTube URL: https://youtu.be/dQw4w9WgXcQ
📏 Enter terminal width (default 120): 100
🎨 Enable color? (y/n, default y): y
✨ Enable contrast enhancement? (y/n, default y): y
```

---

## 🧹 Notes

* YouTube videos are downloaded temporarily to your system temp directory.
* Press **Ctrl + C** to stop playback.
* Temporary files are automatically deleted after playback ends.

---

## ⚖️ License

This project is open-source and free to use for educational or personal purposes.

---

## **💖 Support me:**

[![Donate on DeStream](https://img.shields.io/badge/Donate-DeStream-blue?style=for-the-badge)](https://destream.net/live/H190K/donate)  
[![Donate with NOWPayments](https://img.shields.io/badge/Donate-NOWPayments-purple?style=for-the-badge)](https://nowpayments.io/donation?api_key=J0QACAH-BTH4F4F-QDXM4ZS-RCA58BH)  
