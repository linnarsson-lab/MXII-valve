#Python 3 package to control an MXII valve from Rheodyne (part of IDEX).
#Date: 14 October 2016
#Author: Lars E. Borm
#E-mail: lars.borm@ki.se or larsborm@gmail.com
#Python version: 3.5.1
#Based on: MX Series II(TM) Driver Development Package, File-1418039677
#Downloaded from: 
#https://www.idex-hs.com/support/literature-downloads/operation-manuals
#*NOTE* not all possible functions implemented from manual.


import serial
from serial.tools import list_ports
import time
import re

#   FIND SERIAL PORT
def find_address(identifier = None):
    """
    Find the address of a serial device. It can either find the address using
    an identifier given by the user or by manually unplugging and plugging in 
    the device.
    Input:
    `identifier`(str): Any attribute of the connection. Usually USB to Serial
        converters use an FTDI chip. These chips store a number of attributes
        like: name, serial number or manufacturer. This can be used to 
        identify a serial connection as long as it is unique. See the pyserial
        list_ports.grep() function for more details.
    Returns:
    The function prints the address and serial number of the FTDI chip.
    `port`(obj): Returns a pyserial port object. port.device stores the 
        address.
    
    """
    found = False
    if identifier != None:
        port = [i for i in list(list_ports.grep(identifier))]
        
        if len(port) == 1:
            print('Device address: {}'.format(port[0].device))
            found = True
        elif len(port) == 0:
            print('''No devices found using identifier: {}
            \nContinue with manually finding USB address...\n'''.format(identifier))
        else:
            for p in connections:
                print('{:15}| {:15} |{:15} |{:15} |{:15}'.format('Device', 'Name', 'Serial number', 'Manufacturer', 'Description') )
                print('{:15}| {:15} |{:15} |{:15} |{:15}\n'.format(str(p.device), str(p.name), str(p.serial_number), str(p.manufacturer), str(p.description)))
            raise Exception("""The input returned multiple devices, see above.""")

    if found == False:
        print('Performing manual USB address search.')
        while True:
            input('    Unplug the USB. Press Enter if unplugged...')
            before = list_ports.comports()
            input('    Plug in the USB. Press Enter if USB has been plugged in...')
            after = list_ports.comports()
            port = [i for i in after if i not in before]
            if port != []:
                break
            print('    No port found. Try again.\n')
        print('Device address: {}'.format(port[0].device))
        try:
            print('Device serial_number: {}'.format(port[0].serial_number))
        except Exception:
            print('Could not find serial number of device.')
    
    return port[0]


class MX_valve():
    """
    Class to control MXII valves from Rheodyne (part of IDEX).

    Use the change_port() function to control the valve. It will check if the
    input is correct, if the valve is already in the required position, change
    the valve position and check if the port is in the right position.
    
    **No error handeling**
    
    Written for and tested on: MXX778-605 10-port valve.
    If you use a different valve change the number of ports. Not tested.
    
    """
     
    def __init__(self, address, ports = 10, name = '', verbose = False):
        '''
        Input:
        `Address`: address of valve, '/dev/ttyUSBX' on linux. 'COMX' on windows.
        `Ports` (int): Number of ports, default = 10.
        `Name` (str): Name to identify valve for user (not necessary).
        
        '''
        self.address = address
        self.ports = ports
        self.name = name
        self.ser = serial.Serial(address, timeout = 2, baudrate=19200, 
                   write_timeout=5)
        self.verbose = verbose
        self.verboseprint = print if self.verbose else lambda *a, **k: None
        #19200 is the default baudrate for the MXII valve. see manual if you
        #want to change this: MX Series II(TM) Driver Development Package,
        #File-141803967
        #download from:
        #https://www.idex-hs.com/support/literature-downloads/operation-manuals
    
    def stripped_hex(self, target):
        """
        Function to convert a decimal to a hexadecimal but without the "0x" and 
        capitalized
        Input:
            `target` (int): Decimal to cenvert to stripped hex
        Output: Striped hexadecimal
        
        The normal python hex() functions returns a hex including the "0x" and 
        in lower case. This should work for all lengths of integer decimals
        
        """
        result = hex(target)
        result = result[-(len(result)-2):]
        result = result.upper()
        return result
    
    def wait_ready(self):
        """
        Function that repeatetly asks the valve if it is ready for new input.
        
        """
        msg = self.message_builder('read')
        self.read_message() 
        while True:
            self.write_message(msg)
            response = self.read_message()
            if response != b'**':
                break

    def message_builder (self, objective, port = 1):
        """
        Build and format message for Rheodyne MXII valve
        Imput:
        `objective` (str): 'change' to change port. 'read' to get current port
        `port` (int): port number to change to
        
        *No error handling for invalid input*
        Works only for MXII valves with <16 ports because the port value has to 
        be stored in one character. This can easily be changed by using the zero
        in the message.
        
        """
        message = ''
        if objective == 'change':
            message += 'P0' #"P" = command to read, "0" part of the port 
            # number, the number does not exeed 15, so when using hex values
            # the first digit is not needed
            message += self.stripped_hex(port) #hex value of the port
        elif objective == 'read':
            message += 'S' #"S" = read the current valve position.

        message += '\r' #escape character at the end of every message
        message = message.encode('ascii')
        return message
        

    def read_message(self):
        """
        Read response of the valve.
        Output: response of the pump.
        
        """
        n = self.ser.inWaiting()
        time.sleep(0.05) #Alow valve to process
        response = self.ser.read(n)
        time.sleep(0.05) #Alow valve to process
        return response
    
    def write_message(self, message):
        """
        Write message to the MXII valve. 
        Input:
        `message`: Message to sent to valve
            
        """
        #Flush the pre-existing output
        self.read_message() 
        #Write new message
        self.ser.write(message)
        time.sleep(0.05)
    
    def response_interpret(self, response):
        '''
        Interpret the messages from the MXII valve. Only two responses possible:
            (1) Current port
            (2) Valve ready
        Input: 
        `response` = response from the pump as byte
        Output either:
        (1): current port (int)
        (2): pump status (bool), if ready returns True, if bussy returns False
        
        '''
        port_val = re.compile(b'0.\\r')
        err_val = re.compile
        if re.match(port_val, response):
            #Conversion is confusing
            #The valve sends Hexadecimals back for the values, if you slice this 
            #it becomes the decimal representation of the ASCII character:
            #Pump sends: 'A', this becomes: decimal '65' after slicing
            #Here 65 is transformed back to A with chr() and then converted
            #to the right decimal (in this case '10') with int(x, 16)
            current_port = int(chr(response[1]), 16)
            return int(current_port)
        elif response == b'\r':
            return True
        # Valve bussy
        elif response == b'*' or response == b'**':
            return False
        else:
            print(''' If you see this message, you found an unknown error,
            Please send me (Lars Borm) a message with the following error code
            and your script. I will try to fix it.''')
            raise ValueError('Unknown valve response: "{}", can not interpret',format(response))

    def get_port(self):
        """
        Read the current port position of the valve. 
        Returns:
        Current port

        """
        msg = self.message_builder('read')
        self.write_message(msg)
        response = self.read_message()
        return self.response_interpret(response)
    
    def change_port(self, port):
        """
        Function to change the port of the valve. 
        Input: 
            `port` (int): Port to change to
        Checks if the provided port is valid and checks the current port, it 
        change the port and sleep during the transition time. 
        
        """
        #Check input
        if not isinstance(port, int) or port < 1 or port > self.ports:
            raise ValueError('Invalid port number: {}'.format(port))

        #Check if valve is already in correct position
        current_port = self.get_port()
        if current_port == port:
            self.verboseprint('Valve: "{}" already in position {}'.format(self.name, port))
        
        #Change port
        else:
            while True:
                self.write_message(self.message_builder('change', port))
                self.wait_ready()
                current_port = self.get_port()
                if  current_port == port:
                    self.verboseprint('Valve: "{}" moved to port {}'.format(self.name, current_port))
                    break