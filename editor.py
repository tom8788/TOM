import curses
import os

def display_text(win, text, cursor_y, cursor_x):
    win.clear()
    win.addstr(0, 0, text)
    win.move(cursor_y, cursor_x)
    win.refresh()

def edit_file(filename):
    try:
        with open(filename, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        text = ""

    cursor_y, cursor_x = 0, 0

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    while True:
        display_text(stdscr, text, cursor_y, cursor_x)
        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            cursor_y = min(cursor_y + 1, curses.LINES - 1)
        elif key == curses.KEY_UP:
            cursor_y = max(cursor_y - 1, 0)
        elif key == curses.KEY_RIGHT:
            cursor_x = min(cursor_x + 1, curses.COLS - 1)
        elif key == curses.KEY_LEFT:
            cursor_x = max(cursor_x - 1, 0)
        elif key == 27:  # Escape key
            choice = input_yes_no_cancel(stdscr, "Do you want to save? (yes/no/cancel): ")
            if choice == "yes":
                with open(filename, 'w') as file:
                    file.write(text)
                break
            elif choice == "no":
                break
        #elif key == curses.ascii.DEL or key == curses.KEY_BACKSPACE:
        elif key == curses.KEY_BACKSPACE:
            text = text[:cursor_y * curses.COLS + cursor_x - 1] + text[(cursor_y * curses.COLS + cursor_x):]
            cursor_x -= 1
        elif 32 <= key <= 126 or key == 10:  # Handle printable ASCII characters and Enter key
            text = text[:cursor_y * curses.COLS + cursor_x] + chr(key) + text[cursor_y * curses.COLS + cursor_x:]
            cursor_x += 1

    curses.endwin()

def input_yes_no_cancel(win, prompt):
    win.clear()
    win.addstr(0, 0, prompt)
    win.refresh()

    while True:
        key = win.getch()
        if key == ord('y') or key == ord('Y'):
            return "yes"
        elif key == ord('n') or key == ord('N'):
            return "no"
        elif key == ord('c') or key == ord('C'):
            return "cancel"

if __name__ == "__main__":
    filename = input("Enter filename: ")
    edit_file(filename)
