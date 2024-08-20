import netifaces
import constants

def ip():

    format_string = "{:<12} {:<15} {:<15} {:<15}"

    #print(f"{interface} - {ip_address} - {netmask} - {gateway_ip}")
    print(constants.Cwhite + format_string.format("Interface","IP Address","Netmask","Gateway") + constants.Cgreen)
    print(constants.Cwhite + format_string.format("------------","---------------","---------------","---------------") + constants.Cgreen)
    
    interfaces = netifaces.interfaces()

    for interface in interfaces:
        # Skip interfaces without addresses
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET not in addresses:
            continue

        # Get IP Address and Subnet Mask
        ip_info = addresses[netifaces.AF_INET][0]
        ip_address = ip_info.get('addr', 'N/A')
        netmask = ip_info.get('netmask', 'N/A')

        # Get Gateway
        gateways = netifaces.gateways()
        gateway = gateways.get('default', {}).get(netifaces.AF_INET)
        gateway_ip = gateway[0] if gateway else 'N/A'

        print(constants.Cwhite + format_string.format(interface,ip_address,netmask,gateway_ip) + constants.Cgreen)
