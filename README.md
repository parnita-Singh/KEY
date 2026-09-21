# KEY 🎹✋

**KEY** is an AI-powered virtual keyboard that lets you type by hovering and pinching your fingers in the air — no physical keyboard required. It uses real-time hand tracking through your webcam to detect finger positions and register keystrokes.

Originally built in 9th grade, rebuilt here from scratch.

## Demo

A webcam feed shows an on-screen QWERTY keyboard overlay. Hover your index finger over a key, pinch your index and middle fingers together to "press" it, and the typed text appears in a text bar on screen.

## Tech Stack

- **Python 3.9–3.11**
- **OpenCV** (`opencv-python`) — webcam capture and rendering
- **cvzone** — hand tracking wrapper
- **MediaPipe** — underlying hand landmark detection
- **pynput** — sends real keystrokes to the OS (optional)
- **NumPy**

## How It Works

1. `cvzone.HandTrackingModule` detects your hand and returns 21 landmark points per frame.
2. An on-screen keyboard is drawn using OpenCV rectangles and text over the live video feed.
3. The index fingertip position is checked against each key's bounding box to detect hover.
4. When the index and middle fingertips pinch together (distance below a threshold), the hovered key is "clicked" — it flashes green and the character is added to the typed text.
5. Optionally, `pynput` sends the actual keypress to whatever application is focused, so KEY can be used like a real input device.

## Installation

```bash
git clone https://github.com/<your-username>/KEY.git
cd KEY
pip install -r requirements.txt
```

> **Note:** MediaPipe does not yet fully support Python 3.12+. Use Python 3.9–3.11.

## Usage

```bash
python main.py
```

- Move your hand in front of the webcam.
- Hover your index finger over a key.
- Pinch index + middle finger together to type that character.
- Press `q` or `ESC` to quit.

## Project Structure

```
KEY/
├── main.py            # Main application: hand tracking + virtual keyboard logic
├── requirements.txt   # Python dependencies
└── README.md
```

## Future Improvements

- [ ] Add a number row and special keys (space, backspace, enter)
- [ ] Support two-handed typing
- [ ] Add sound feedback on keypress
- [ ] Adjustable pinch-sensitivity slider
- [ ] Save typed text to a file

## License

MIT