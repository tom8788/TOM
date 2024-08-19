def ping(ip_address):

    import constants
    import subprocess
    import time

    transmitted = 0
    received = 0

    for i in range(4):
        try:
            transmitted += 1
            # Run the ping command
            output = subprocess.run(["ping", "-c", "1", ip_address], capture_output=True, text=True)

            # Check if the ping was successful
            if output.returncode == 0:
                received += 1
                time_line = [line for line in output.stdout.splitlines() if "time=" in line]
                if time_line:
                    time_value = time_line[0].split("time=")[1].split()[0]
                    print(constants.Cwhite+f"ping {i+1} - time = {time_value}ms")
                #print(f"Ping to {ip_address} was successful:")
                #print(output.stdout)
            else:
                print(constants.Cred+f"Failed to ping {ip_address}."+constants.Cgreen)
                print(output.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(1)

    success_rate = (received / transmitted) * 100
    print(constants.Cwhite+f"\n{transmitted} packets transmitted, {received} received, {success_rate}% success"+constants.Cgreen)
