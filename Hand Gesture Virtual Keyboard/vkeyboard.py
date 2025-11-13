import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# ------------------- Setup -------------------
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8, maxHands=1)

# ------------------- Keyboard Layout -------------------
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", "<"],
    ["SPACE"]
]

finalText = ""
delayCounter = 0
touchCounter = 0
currentTouchButton = None
TOUCH_THRESHOLD = 15

# ------------------- Button Class -------------------
class Button:
    def __init__(self, pos, text, size=[65, 65]):
        self.pos = pos
        self.text = text
        self.size = size

# ------------------- Create Buttons -------------------
buttonList = []
# Position keyboard to fit in 1280x720
startX = 280  # Center horizontally
startY = 350  # Position in lower half
buttonWidth = 65
buttonHeight = 65
gapX = 75  # Horizontal gap
gapY = 75  # Vertical gap

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "SPACE":
            # Spacebar centered and wide
            buttonList.append(Button([startX + 50, gapY * i + startY], key, size=[550, 65]))
        else:
            buttonList.append(Button([gapX * j + startX, gapY * i + startY], key, [buttonWidth, buttonHeight]))

# ------------------- Drawing Functions -------------------
def draw_all(img, buttonList):
    overlay = img.copy()
    
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (80, 80, 80), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), (150, 150, 150), 2)
        
        if button.text == "SPACE":
            cv2.putText(img, "SPACE", (x + 205, y + 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (50, 50, 50), 4)
            cv2.putText(img, "SPACE", (x + 203, y + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2)
        else:
            cv2.putText(img, button.text, (x + 15, y + 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (50, 50, 50), 4)
            cv2.putText(img, button.text, (x + 13, y + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    return img

def draw_touching(img, button, progress, threshold):
    x, y = button.pos
    w, h = button.size
    
    percentage = int((progress / threshold) * 100)
    
    if percentage < 40:
        color = (255, 150, 0)
    elif percentage < 80:
        color = (255, 255, 0)
    else:
        color = (0, 255, 0)
    
    cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)
    
    bar_width = int((w - 10) * (progress / threshold))
    cv2.rectangle(img, (x + 5, y + h - 12), (x + 5 + bar_width, y + h - 4), 
                  (0, 255, 0), cv2.FILLED)
    
    if button.text == "SPACE":
        cv2.putText(img, button.text, (x + 205, y + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (30, 30, 30), 4)
        cv2.putText(img, button.text, (x + 203, y + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2)
    else:
        cv2.putText(img, button.text, (x + 15, y + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (30, 30, 30), 4)
        cv2.putText(img, button.text, (x + 13, y + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    
    cv2.putText(img, f"{percentage}%", (x + w - 30, y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

def draw_typed(img, button):
    x, y = button.pos
    w, h = button.size
    
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 150), cv2.FILLED)
    
    if button.text == "SPACE":
        cv2.putText(img, button.text, (x + 205, y + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (30, 30, 30), 4)
        cv2.putText(img, button.text, (x + 203, y + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2)
    else:
        cv2.putText(img, button.text, (x + 15, y + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (30, 30, 30), 4)
        cv2.putText(img, button.text, (x + 13, y + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

# ------------------- Main Loop -------------------
justTyped = False

while True:
    success, img = cap.read()
    if not success:
        continue
    
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    img = draw_all(img, buttonList)
    
    touchedButton = None
    bothFingersOnButton = False
    
    if hands and delayCounter == 0:
        hand = hands[0]
        lmList = hand["lmList"]
        
        if lmList:
            index_x, index_y = lmList[8][:2]
            middle_x, middle_y = lmList[12][:2]
            
            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                
                index_on_button = (x < index_x < x + w and y < index_y < y + h)
                middle_on_button = (x < middle_x < x + w and y < middle_y < y + h)
                
                if index_on_button and middle_on_button:
                    touchedButton = button
                    bothFingersOnButton = True
                    
                    if currentTouchButton == button:
                        touchCounter += 1
                        draw_touching(img, button, touchCounter, TOUCH_THRESHOLD)
                        
                        if touchCounter >= TOUCH_THRESHOLD:
                            if button.text == "<":
                                finalText = finalText[:-1]
                            elif button.text == "SPACE":
                                finalText += " "
                            else:
                                finalText += button.text
                            
                            draw_typed(img, button)
                            justTyped = True
                            delayCounter = 1
                            touchCounter = 0
                            currentTouchButton = None
                    else:
                        touchCounter = 1
                        currentTouchButton = button
                        draw_touching(img, button, touchCounter, TOUCH_THRESHOLD)
                    
                    break
    
    if not bothFingersOnButton:
        if touchCounter > 0:
            touchCounter = 0
            currentTouchButton = None
    
    if delayCounter != 0:
        delayCounter += 1
        if delayCounter > 10:
            delayCounter = 0
            justTyped = False
    
    # Display typed text at TOP
    overlay = img.copy()
    cv2.rectangle(overlay, (50, 30), (1230, 120), (40, 40, 40), cv2.FILLED)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    cv2.rectangle(img, (50, 30), (1230, 120), (150, 150, 150), 2)
    
    cv2.putText(img, finalText, (62, 87),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 5)
    cv2.putText(img, finalText, (60, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 2)
    
    # Instructions
    cv2.putText(img, "Place BOTH fingertips on a key and hold", (50, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2)
    
    if touchCounter > 0:
        cv2.putText(img, "HOLDING... Keep both fingers on key!", (50, 190),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    cv2.imshow("Virtual Keyboard", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

