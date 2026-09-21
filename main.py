"""
AI Virtual Keyboard
--------------------
Recreates the classic "AI Virtual Keyboard" project:
webcam feed + hand tracking (cvzone) + on-screen QWERTY keyboard
that you "type" on by hovering your index finger over a key and
pinching it with your middle finger to click.

Tech stack:
    - Python 3.8+
    - opencv-python
    - cvzone
    - mediapipe   (cvzone's HandTrackingModule depends on this)
    - pynput      (to actually send keystrokes to the OS, optional)

Install:
    pip install opencv-python cvzone mediapipe pynput numpy

Run:
    python main.py
"""

import cv2
import numpy as np
from time import sleep
from cvzone.HandTrackingModule import HandDetector

# pynput lets us actually type into whatever window is focused.
# If you don't need real keystrokes (just the on-screen demo),
# you can remove this import and the controller.keys() calls below.
try:
    from pynput.keyboard import Controller
    keyboard = Controller()
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("pynput not installed — running in visual-only mode (no real keystrokes).")


# ---------------------------------------------------------------------------
# Camera setup
# ---------------------------------------------------------------------------
cap = cv2.VideoCapture(0)
cap.set(3, 1280)   # width
cap.set(4, 720)    # height

detector = HandDetector(detectionCon=0.8, maxHands=1)

# ---------------------------------------------------------------------------
# Keyboard layout
# ---------------------------------------------------------------------------
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
]

finalText = ""


class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text


def createKeyboard(keyList):
    buttonList = []
    for i, row in enumerate(keyList):
        for j, key in enumerate(row):
            x = 100 * j + 50
            y = 100 * i + 50
            buttonList.append(Button([x, y], key))
    return buttonList


buttonList = createKeyboard(keys)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def drawAll(img, buttonList, hoveredButton=None):
    """Draw all keyboard buttons; highlight the one under the fingertip."""
    overlay = img.copy()
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        color = (255, 0, 200) if button is hoveredButton else (200, 0, 200)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.putText(overlay, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLEX if hasattr(cv2, "FONT_HERSHEY_PLEX") else cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 255, 255), 3)

    # slight transparency so the camera feed stays visible through the keys
    out = cv2.addWeighted(overlay, 0.85, img, 0.15, 0)
    return out


def findHoveredButton(lmList, buttonList):
    """Return the Button under the index fingertip (landmark 8), or None."""
    if not lmList:
        return None
    x, y = lmList[8][0], lmList[8][1]
    for button in buttonList:
        bx, by = button.pos
        bw, bh = button.size
        if bx < x < bx + bw and by < y < by + bh:
            return button
    return None


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    global finalText
    clickCooldown = 0  # frames to wait before allowing another click

    while True:
        success, img = cap.read()
        if not success:
            print("Could not read from webcam.")
            break

        img = cv2.flip(img, 1)  # mirror for natural "reach out" feel
        hands, img = detector.findHands(img, flipType=False)

        hoveredButton = None

        if hands:
            hand = hands[0]
            lmList = hand["lmList"]

            hoveredButton = findHoveredButton(lmList, buttonList)

            if hoveredButton and clickCooldown == 0:
                # distance between index tip (8) and middle tip (12) = "pinch"
                length, info, img = detector.findDistance(
                    lmList[8][:2], lmList[12][:2], img
                )

                if length < 35:  # pinch threshold in pixels — tune as needed
                    bx, by = hoveredButton.pos
                    bw, bh = hoveredButton.size
                    cv2.rectangle(img, (bx, by), (bx + bw, by + bh),
                                  (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, hoveredButton.text, (bx + 20, by + 65),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

                    finalText += hoveredButton.text
                    if PYNPUT_AVAILABLE:
                        keyboard.press(hoveredButton.text)
                        keyboard.release(hoveredButton.text)

                    clickCooldown = 15  # ~15 frames before next click registers

        if clickCooldown > 0:
            clickCooldown -= 1

        img = drawAll(img, buttonList, hoveredButton)

        # text bar showing what's been typed
        cv2.rectangle(img, (50, 350 + 0), (700, 450), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, finalText, (60, 430),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

        cv2.imshow("AI Virtual Keyboard", img)

        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):  # ESC or 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()