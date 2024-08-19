def display_help(helpcommand=None):

    import constants

    help_info = [
        ("run", "Run a specific program."),
        ("edit", "Edit a specific program."),
        ("list", "List the contents of a specific program. If no infilename is given, all *.tom files of the current directory are listed."),
        ("help", "List commands with their explanation"),
        ("cls", "Clear the screen."),
        ("ver", "Print the current version."),
        ("ip", "Print the network interfaces and their IP address."),
        ("ping", "Ping a network address."),
        ("exit", "Exit TOM.")
    ]

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
