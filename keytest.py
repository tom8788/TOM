from pynput import keyboard
from queue import Queue

kbd_q = Queue(maxsize=1)

def on_activate_s():
    kbd_q.put("Hotkey s")


listener = keyboard.GlobalHotKeys({
    's': on_activate_s,
})
listener.start()
listener.wait()

while True:
    key = kbd_q.get()
    if key:
        print(key)
        print ("TOP")
