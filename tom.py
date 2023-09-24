variables={}
help_info = [
    ("run", "Run a specific program."),
    ("list", "List a specific program."),
    ("help", "List commands with their explanation"),
    ("exit", "Exit TOM.")

    # Add more commands and explanations here
]

def interpret_line(line):
    global variables
    parts = line.split(" ", 1)
    line_number = parts[0]

#COMMENT function, omit line when preceded by //
    if line_number.startswith("//"):
        return
    else:
        line_number = int(parts[0])
    command = parts[1]

#VARIABLE setting
    if "=" in command:
        variable_name, value = command.split("=", 1)
        variable_name = variable_name.strip()
        value = value.strip()

        if value.startswith('"') and value.endswith('"'):
            # If value is a literal string
            print ("var set: "+value)
            variables[variable_name] = value[1:-1]
        if value.startswith('"') and value.endswith('"'):
            print ("Syntax error on line "+str(line_number))
        else:
            variables[variable_name] = value

#PRINT function
    elif command.startswith("print"):
        content = command[len("print") + 1:].strip()  # Extract content after "print"
        output = ""
        while content:
            if content.startswith('"'):
                end_quote = content[1:].index('"') + 1
                output += content[1:end_quote]  # Extract literal string
                content = content[end_quote + 1:].strip()
            elif "+" in content:
                variable_name, content = content.split("+", 1)
                variable_name = variable_name.strip()
                if variable_name in variables:
                    output += str(variables[variable_name])
                else:
                    output += "null"
            else:
                variable_name = content.strip()
                if variable_name in variables:
                    output += str(variables[variable_name])
                else:
                    output += "null"
                content = ""

        print(output)

#LIST command
def list_program(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    for line in lines:
        print(line.rstrip())

#RUN command
def run_program(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    for line in lines:
        #omit empty lines
        if line.strip():
            interpret_line(line.strip())

def display_help(helpcommand=None):
    if helpcommand:
        # Display the explanation for the specific command
        for cmd, explanation in help_info:
            if cmd == helpcommand:
                print(f"{cmd}: {explanation}")
                return
        print("Command not found in help.")
    else:
        # Display the list of available commands
        print("\n\rAvailable commands:")
        print("===================\n\r")
        for cmd, explanation in help_info:
            print(f"{cmd}: {explanation}")

def main():
    print("\n\rWelcome to TOM 1.0!\n\r")
    while True:
        command = input("COMMAND> ")
        parts = command.split(" ")

        if parts[0] == "run":
            filename = parts[1]
            run_program(filename)
        elif parts[0] == "list":
            filename = parts[1]
            list_program(filename)
        elif parts[0] == "help":
            if command.lower() == "help":
                display_help()
            if command.startswith("help "):
                helpcommand = parts[1]
                display_help(helpcommand)
        elif parts[0] == "exit":
            print("Exiting TOM")
            break
        else:
            print("Invalid command. Run 'help' for available commands")

if __name__ == "__main__":
    main()
