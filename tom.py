#!/usr/bin/env python3

#The top line makes this directly executable, by typing ./tom.py

######################################################
#
# Open https://liqid.be/blog/tom-manual/ for a manual
# See bottom for ANSI colors
#
######################################################

##################111

import os
import time                     #for WAIT function
from pynput import keyboard     #for capturing the UP key
import readline                 #without this, keys are NOT CAPTURED ON MAC!!!
import re                       #for splitting IF statements
import curses                   #for editor

import constants
from modules import help,cls,ver,ping,ip,list

variables={}
functions={}

linecount = 0
function_found = 0
skipfunction = 0
infilename=""

command_history=[]
history_index=0

#Buffer class for EDIT
class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]

    @property
    def bottom(self):
        return len(self) - 1

    def insert(self, cursor, string):
        row, col = cursor.row, cursor.col
        current = self.lines.pop(row)
        new = current[:col] + string + current[col:]
        self.lines.insert(row, new)

    def split(self, cursor):
        row, col = cursor.row, cursor.col
        current = self.lines.pop(row)
        self.lines.insert(row, current[:col])
        self.lines.insert(row + 1, current[col:])

    def delete(self, cursor):
        row, col = cursor.row, cursor.col
        if (row, col) < (self.bottom, len(self[row])):
            current = self.lines.pop(row)
            if col < len(self[row]):
                new = current[:col] + current[col + 1:]
                self.lines.insert(row, new)
            else:
                next = self.lines.pop(row)
                new = current + next
                self.lines.insert(row, new)

    def get_raw_text(self):
        return '\n'.join(self.lines)

#Clamp function for EDIT
def clamp(x, lower, upper):
    if x < lower:
        return lower
    if x > upper:
        return upper
    return x

#Cursor class for EDIT
class Cursor:
    def __init__(self, row=0, col=0, col_hint=None):
        self.row = row
        self._col = col
        self._col_hint = col if col_hint is None else col_hint

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, col):
        self._col = col
        self._col_hint = col

    def _clamp_col(self, buffer):
        self._col = min(self._col_hint, len(buffer[self.row]))

    def up(self, buffer):
        if self.row > 0:
            self.row -= 1
            self._clamp_col(buffer)

    def down(self, buffer):
        if self.row < len(buffer) - 1:
            self.row += 1
            self._clamp_col(buffer)

    def left(self, buffer):
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            self.col = len(buffer[self.row])
    def right(self, buffer):
        if self.col < len(buffer[self.row]):
            self.col += 1
        elif self.row < len(buffer) - 1:
            self.row += 1
            self.col = 0

#Window class for EDIT
class Window:
    def __init__(self, n_rows, n_cols, row=0, col=0):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.row = row
        self.col = col

    @property
    def bottom(self):
        return self.row + self.n_rows - 1

    def up(self, cursor):
        if cursor.row == self.row - 1 and self.row > 0:
            self.row -= 1

    def down(self, buffer, cursor):
        if cursor.row == self.bottom + 1 and self.bottom < len(buffer) - 1:
            self.row += 1

    def horizontal_scroll(self, cursor, left_margin=5, right_margin=2):
        n_pages = cursor.col // (self.n_cols - right_margin)
        self.col = max(n_pages * self.n_cols - right_margin - left_margin, 0)

    def translate(self, cursor):
        return cursor.row - self.row, cursor.col - self.col

#Left function for EDIT
def left(window, buffer, cursor):
    cursor.left(buffer)
    window.up(cursor)
    window.horizontal_scroll(cursor)

#Right function for EDIT
def right(window, buffer, cursor):
    cursor.right(buffer)
    window.down(buffer, cursor)
    window.horizontal_scroll(cursor)

#Exit procedure for EDIT
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

def on_key_press(key):
    global history_index

    try:
        #print ("Key "+key.char+" released")
        if key == keyboard.Key.up:
            # Handle UP key press for command history
            if history_index > 0:
                history_index -= 1
                update_command_prompt()
        elif key == keyboard.Key.down:
            # Handle DOWN key press for command history
            if history_index < len(command_history) - 1:
                history_index += 1
                update_command_prompt()
        #print ("key")
    except AttributeError:
        pass

def parse_check(infilename):
    global functions
    global parse_error
    errorflag = 0
    in_if_block = False
    linenum = 0

    try:
        with open(infilename, "r") as file:
            lines = file.readlines()
            file.seek(0) #reset line pointer back to beginning of file

            for line in lines:
                linenum += 1
                command = line.strip()

                if not in_if_block:
                    if command.startswith("function"):
                        in_function = True
                        parts = line.split(" ")
                        function_name = parts[1].strip()
                        functions[function_name] = linenum
                    elif command.startswith("if"):
                        in_if_block = True
                    elif command.startswith("end"):
                        if in_function:
                            in_function = False
                        else:
                            print ("\033[1;31;40mError: End found without function definition on line "+str(linecount)+"\033[1;37;40m")
                            errorflag = 1
                    elif command.startswith("endif"):
                        print ("\033[1;31;40mError: Endif found without if definition on line "+str(linecount)+"\033[1;37;40m")
                        errorflag = 1
                else:
                    if command.startswith("function"):
                        print ("\033[1;31;40mError: Function definition in if block on line "+str(linecount)+"\033[1;37;40m")
                        errorflag = 1
                    elif command.startswith("if"):
                        print ("\033[1;31;40mError: If-command found without previous endif on line "+str(linecount)+"\033[1;37;40m")
                        errorflag = 1
                    elif command.startswith("endif"):
                        in_if_block = False
                    elif command.startswith("end"):
                        print ("\033[1;31;40mError: End found in if-block on line "+str(linecount)+"\033[1;37;40m")
                        errorflag = 1

            return errorflag

    except FileNotFoundError:
        print("\033[1;31;40mError: The file '{infilename}' does not exist.\033[1;37;40m")

def lookfor_function(line):
    global linecount
    global function_found
    global functionend_error
    global functions

    command = line.strip()

    if command.startswith("function"):
        function_found = 1
        parts = line.split(" ")
        function_name = parts[1]
        functions[function_name] = linecount

def lookfor_functionend(line):
    global linecount
    global function_found
    global functionend_error

    command = line.strip()

    if command.startswith("function"):
        functionend_error = 1
    elif line.startswith("end"):
        function_found = 0

#skipto_end skips functions during run_program
def skipto_end(line):
    global skipfunction

    command = line.strip()

    if command=="end":
        skipfunction = 0

#Interpret lines
def interpret_line(line):
    global variables
    global linecount
    global skipfunction
    global functions
    functfound = 0

#COMMENT function, omit line when preceded by //
    if line.startswith("//"):
        return
    else:
        command = line.strip()

#VARIABLE setting
    if not command.startswith("if") and "=" in command:
        variable_name, value = command.split("=", 1)
        variable_name = variable_name.strip()
        value = value.strip()

        if value.startswith('"') and value.endswith('"'):
            # If value is a literal string
            variables[variable_name] = value[1:-1]
        elif value.startswith('"') and not value.endswith('"'):
            print ("\033[1;31;40mSyntax error on line "+str(linecount)+"\033[1;37;40m")
        else:
            variables[variable_name] = value

#PRINT function
    elif command.startswith("print"):
        content = command[len("print") + 1:].strip()  # Extract content after "print"
        output = ""

        #AANPASSEN!!! Anders wordt ELK punt als een concat gezien
        elements = content.split('.')

        for element in elements:
            element = element.strip()

            if element.startswith('"'):
                # Literal string enclosed in double quotes
                end_quote = element[1:].index('"') + 1
                output += element[1:end_quote]  # Extract literal string
            else:
                # Variable
                variable_name = element
                if variable_name in variables:
                    output += str(variables[variable_name])
                else:
                    result.append("null")

        print(constants.Cwhite+output)

#CLS function
    elif command.startswith("cls"):
        os.system('clear')

#WAIT function
    elif command.startswith("wait"):
        arg = command[len("arg") + 1:].strip()  # Extract
        if arg=="":
            input(constants.Cwhite+"Press Enter to continue...")
        elif arg.isnumeric():
            time.sleep(int(arg))
        else:
            print(Cred+"Syntax error: wrong argument for wait function on line "+str(linecount))

#INPUT function
    elif command.startswith("input"):
        #Placeholder
        variable_name = command[len("input") + 1:].strip()
        variable_name = variable_name.strip()
        value = input(">")
        variables[variable_name] = value

#FUNCTION function
    elif command.startswith("function"):
        skipfunction = 1

#IF function
    elif command.startswith("if"):
        print (Cwhite+"IF found - placeholder")

#ENDIF function - TEMP!!!!
    elif command.startswith("endif"):
        print (constants.Cwhite+"ENDIF found - placeholder")

    else:
        for funct_search in functions:
            if command == funct_search:
                functfound = 1
                run_procedure(functions[funct_search])
        if functfound == 0:
            print(Cred+"Syntax error: command not recognized on line "+str(linecount))

#EDIT command
def edit_program(infilename):
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    with open(infilename) as f:
        buffer = Buffer(f.read().splitlines())

    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor()

    while True:
        stdscr.erase()
        for row, line in enumerate(buffer[window.row:window.row + window.n_rows]):
            if row == cursor.row - window.row and window.col > 0:
                line = "«" + line[window.col + 1:]
            if len(line) > window.n_cols:
                line = line[:window.n_cols - 1] + "»"
            stdscr.addstr(row, 0, line)
        stdscr.move(*window.translate(cursor))

        k = stdscr.getkey()
#        k = stdscr.getch()
        if k == "q":
            sys.exit(0)
        elif k == "KEY_LEFT":
            left(window, buffer, cursor)
        elif k == "KEY_DOWN":
            cursor.down(buffer)
            window.down(buffer, cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_UP":
            cursor.up(buffer)
            window.up(cursor)
            window.horizontal_scroll(cursor)
        elif k == "KEY_RIGHT":
            right(window, buffer, cursor)
        elif k == "\n":
            buffer.split(cursor)
            right(window, buffer, cursor)
        elif k in ("KEY_DELETE", "\x04"):
            buffer.delete(cursor)
        elif k in ("KEY_BACKSPACE", "\x7f"):
            if (cursor.row, cursor.col) > (0, 0):
                left(window, buffer, cursor)
                buffer.delete(cursor)
        elif k in ("ESCAPE", "\x1b"):  # Escape key
            choice = input_yes_no_cancel(stdscr, "Do you want to save? (yes/no/cancel): ")
            if choice == "yes":
                #savefile = args.filename
                with open(infilename, 'w') as file:
                    raw_text = buffer.get_raw_text()
                    file.write(raw_text)
                curses.nocbreak()
                stdscr.keypad(False)
                curses.echo()
                curses.endwin()
                break
            elif choice == "no":
                curses.nocbreak()
                stdscr.keypad(False)
                curses.echo()
                curses.endwin()
                break
        else:
            buffer.insert(cursor, k)
            for _ in k:
                right(window, buffer, cursor)

#PROCEDURE command
def run_procedure(functline):
    global infilename
    global skipfunction

    #print ("Running procedure")
    with open(infilename, "r") as procfile:
        for i in range(functline-1):
            next (procfile)
#        print ("Skipped lines")
        for line in procfile:
            command=line.strip()
            if command != "end":
#                print ("Going to interpret "+line.strip())
                interpret_line(line.strip())
            else:
                skipfunction=0
                break

#RUN command
def run_program(infilename):
    global linecount
    global function_found
    global skipfunction

    function_found = 0
    linecount=0

    parse_error = parse_check(infilename)

    if parse_error == 1:
        sys.exit()

    try:
        with open(infilename, "r") as file:
            lines = file.readlines()
            file.seek(0) #reset line pointer back to beginning of file

            for line in lines:
                linecount += 1
                if line.strip():
                    if skipfunction == 0:
#                        print ("Going to interpret, now line "+str(linecount))
                        interpret_line(line.strip())
                    else:
#                        print ("Going to skip, now line "+str(linecount))
                        skipto_end(line.strip())
        skipfunction = 0 #reset skip back to zero
    except FileNotFoundError:
        print(Cred+"Error: The file '{infilename}' does not exist.")

#HELP command
def display_help(helpcommand=None):
    if helpcommand:
        # Display the explanation for the specific command
        for cmd, explanation in help_info:
            if cmd == helpcommand:
                print(f"{cmd}: {explanation}")
                return
        print(constants.Cred+"Command not found in help.")
    else:
        # Display the list of available commands
        print("\nAvailable commands:")
        print("===================\n")
        for cmd, explanation in help_info:
            print(f"{cmd}: {explanation}")

def main():
    global infilename

    global command_history
    global history_index

    os.system('clear')
    print ("\033[0m")   #reset colour
    print ("\033[40m")  #black background
    print (constants.Cgreen)  #green text
    print ("  ***********************")
    print ("  * Welcome to TOM 1.0! *")
    print ("  ***********************")

    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()
    listener.wait()

    while True:
        print ("")
        command = input(constants.Cgreen+"COMMAND> ")

        if command:
            command_history.append(command)
            history_index = len(command_history)
            #print ("CMD index is "+str(history_index))
            parts = command.split(" ")

            if parts[0] == "run":
                infilename = parts[1]
                if not infilename.endswith(".tom"):
                    infilename = infilename+".tom"
                run_program(infilename)
            elif parts[0] == "edit":
                infilename = parts[1]
                if not infilename.endswith(".tom"):
                    infilename = infilename+".tom"
                edit_program(infilename)
            elif parts[0] == "list":
                if command.lower() == "list":
                    list.list()
                if command.startswith("list "):
                    infile = parts[1]
                    list.list(infile)
            elif parts[0] == "help":
                if command.lower() == "help":
                    help.display_help()
                if command.startswith("help "):
                    helpcommand = parts[1]
                    help.display_help(helpcommand)
            elif parts[0] == "cls":
                cls.cls()
            elif parts[0] == "ver":
                ver.ver()
            elif parts[0] == "ip":
                ip.ip()
            elif parts[0] == "ping":
                if len(parts)>1:
                    address = parts[1]
                    ping.ping(address)
                else:
                    print(constants.Cred+"IP address cannot be empty"+constants.Cgreen)
            elif parts[0] == "":
                pass
            elif parts[0] == "exit":
                print(constants.Cwhite+"Exiting TOM")
                print ("")
                break
            else:
                print(constants.Cred+"Invalid command. Run 'help' for available commands."+constants.Cgreen)

if __name__ == "__main__":
    main()


