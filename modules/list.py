def list(infile=None):

    import os
    import constants

    if infile:
        if not infile.endswith(".tom"):
            infile = infile+".tom"
            with open(infile, "r") as file:
                lines = file.readlines()
            print (constants.Cwhite)
            for line in lines:
                print(line.rstrip())
            print (constants.Cgreen)
    else:
        # List all files with the .tom extension in the current directory
        tom_files = [file for file in os.listdir() if file.endswith(".tom")]

        if tom_files:
            print (constants.Cwhite)
            for tom_file in tom_files:
                print(tom_file)
            print (constants.Cgreen)
        else:
            print(constants.Cred+"No .tom files found in the current directory."+constants.Cgreen)
