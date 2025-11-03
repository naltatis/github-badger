import sys
import os

sys.path.insert(0, "/system/apps/morse")
os.chdir("/system/apps/morse")

from badgeware import screen, PixelFont, shapes, brushes, io, run, Image

# Enable antialiasing for smooth graphics
screen.antialias = Image.X2

# Morse code alphabet mapping (A-Z, 0-9)
MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9'
}

# Timing constants (in milliseconds)
DOT_DASH_THRESHOLD = 300     # Less than this is a dot, >= is a dash
CHAR_GAP_THRESHOLD = 800     # Gap to recognize end of character
WORD_GAP_THRESHOLD = 1500    # Gap to recognize word space

# App state
current_pattern = ""  # Current morse pattern being input (e.g., ".-.")
recognized_text = ""  # Text that has been recognized
button_press_start = None  # When button A was pressed
last_input_time = None  # Last time of any input
waiting_for_gap = False  # Are we waiting to recognize a character?

# Load fonts
title_font = PixelFont.load("/system/assets/fonts/nope.ppf")
pattern_font = PixelFont.load("/system/assets/fonts/absolute.ppf")
text_font = PixelFont.load("/system/assets/fonts/ziplock.ppf")


def update():
    global current_pattern, recognized_text, button_press_start, last_input_time, waiting_for_gap
    
    # Handle button A press (morse input)
    if io.BUTTON_A in io.pressed:
        button_press_start = io.ticks
        waiting_for_gap = False
    
    # Handle button A release (determine dot or dash)
    if io.BUTTON_A in io.released and button_press_start is not None:
        press_duration = io.ticks - button_press_start
        
        if press_duration < DOT_DASH_THRESHOLD:
            current_pattern += "."
        else:
            current_pattern += "-"
        
        last_input_time = io.ticks
        button_press_start = None
        waiting_for_gap = True
    
    # Check for character gap (recognize character)
    if waiting_for_gap and last_input_time is not None:
        gap_duration = io.ticks - last_input_time
        
        if gap_duration >= CHAR_GAP_THRESHOLD and current_pattern:
            # Try to recognize the character
            char = MORSE_CODE.get(current_pattern, '?')
            recognized_text += char
            current_pattern = ""
            waiting_for_gap = False
        
        # Check for word gap (add space)
        if gap_duration >= WORD_GAP_THRESHOLD and recognized_text and not recognized_text.endswith(' '):
            recognized_text += " "
    
    # Handle button B (delete last character)
    if io.BUTTON_B in io.pressed and recognized_text:
        recognized_text = recognized_text[:-1]
    
    # Draw UI
    draw_ui()


def draw_ui():
    """Draw the morse trainer UI"""
    # Clear screen with gradient-like background
    screen.brush = brushes.color(25, 35, 55)
    screen.clear()
    
    # Draw title bar with embossed style
    screen.brush = brushes.color(45, 65, 95)
    screen.draw(shapes.rounded_rectangle(0, 0, 160, 18, 2))
    
    screen.font = title_font
    # Shadow text
    screen.brush = brushes.color(20, 30, 45, 150)
    title = "MORSE TRAINER"
    tw, _ = screen.measure_text(title)
    screen.text(title, 80 - (tw / 2) + 1, 5)
    # Main text
    screen.brush = brushes.color(255, 255, 255)
    screen.text(title, 80 - (tw / 2), 4)
    
    # Draw current pattern area with inset effect
    screen.brush = brushes.color(35, 50, 70)
    screen.draw(shapes.rounded_rectangle(4, 22, 152, 30, 4))
    # Inner shadow for depth
    screen.brush = brushes.color(20, 30, 45, 100)
    screen.draw(shapes.rounded_rectangle(5, 23, 150, 2, 2))
    
    screen.font = pattern_font
    screen.brush = brushes.color(120, 180, 120)
    pattern_label = "Input:"
    screen.text(pattern_label, 8, 26)
    
    # Draw the morse pattern (dots and dashes) with visual feedback
    if current_pattern:
        display_pattern = current_pattern
        screen.brush = brushes.color(150, 255, 150)
    elif button_press_start is not None:
        # Show visual feedback while button is held
        # Blink to show active input
        if int(io.ticks / 150) % 2:
            display_pattern = current_pattern + "_"
            screen.brush = brushes.color(255, 255, 100)
        else:
            display_pattern = current_pattern
            screen.brush = brushes.color(150, 255, 150)
    else:
        display_pattern = "..."
        screen.brush = brushes.color(80, 100, 100)
    
    pw, _ = screen.measure_text(display_pattern)
    screen.text(display_pattern, 80 - (pw / 2), 38)
    
    # Draw recognized text area with inset effect
    screen.brush = brushes.color(35, 50, 70)
    screen.draw(shapes.rounded_rectangle(4, 56, 152, 42, 4))
    # Inner shadow for depth
    screen.brush = brushes.color(20, 30, 45, 100)
    screen.draw(shapes.rounded_rectangle(5, 57, 150, 2, 2))
    
    screen.font = text_font
    
    # Display recognized text
    if recognized_text:
        # Show last characters that fit
        display_text = recognized_text[-24:]  # Show last 24 characters
        screen.brush = brushes.color(255, 220, 100)
        tw, _ = screen.measure_text(display_text)
        screen.text(display_text, 80 - (tw / 2), 72)
    else:
        # Hint text with pulse effect
        alpha = int((io.ticks / 10) % 256)
        if alpha > 127:
            alpha = 255 - alpha
        alpha = 100 + int(alpha * 0.6)
        screen.brush = brushes.color(140, 140, 140, alpha)
        hint = "Press A to begin"
        hw, _ = screen.measure_text(hint)
        screen.text(hint, 80 - (hw / 2), 72)
    
    # Draw bottom instructions bar
    screen.brush = brushes.color(45, 65, 95)
    screen.draw(shapes.rounded_rectangle(0, 102, 160, 18, 2))
    
    screen.font = title_font
    screen.brush = brushes.color(200, 220, 240)
    instructions = "A: Tap  B: Delete"
    iw, _ = screen.measure_text(instructions)
    screen.text(instructions, 80 - (iw / 2), 106)


if __name__ == "__main__":
    run(update)
