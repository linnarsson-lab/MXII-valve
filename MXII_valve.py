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
import time
import re


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
        self.read_message() #flush output
        while True:
            self.write_message(msg)
            response = self.read_message()
            port_val = re.compile(b'0.\\r')
            if re.match(port_val, response):
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
        ser = self.ser
        n = ser.inWaiting()
        time.sleep(0.05) #Alow valve to process
        response = ser.read(n)
        time.sleep(0.05) #Alow valve to process
        return response
    
    def write_message(self, message):
        """
        Write message to the MXII valve. 
        Input:
        `message`: Message to sent to valve
            
        """
        ser = self.ser
        ser.write(message)
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
            return True, int(current_port)
        elif response == b'\r':
            return True
        elif response == b'*' or response == b'**':
            print(response)
            print('I did not test this yet, if you see it confirm it works and change the code')
            return False
            #I (LEBorm) added this part to interpret the 'bussy' response. However I did not test it.
            #Response: "*" i.e. "0x2A" for 
            #"valve is busy". However, the other functions should not allow this to happen.
        else:
            print(''' If you see this message, you found an unknown error,
            Please send me (Lars Borm) a message with the following error code
            and your script. I will try to fix it.''')
            raise ValueError('Unknown valve response: "{}", can not interpret',format(response))
    
    def change_port(self, port):
        """
        Function to change the port of an MXII valve. 
        Input: 
            `port` (int): Port to change to
        Checks if the provided port is valid and checks the current port, it 
        change the port and sleep during the transition time. 
        
        """
        if not isinstance(port, int) or port < 1 or port > self.ports:
            raise ValueError('Invalid port number')

        ser = self.ser
        while True:
            self.read_message() #flush output   
            self.write_message(self.message_builder('read'))
            response1 = self.read_message()
            #This should catch the only known error: the pump sending an empty byte.
            #However, never tested because errors are extremely rare.
            if response1 != b'':
                break
        current_port = self.response_interpret(response1)
        if current_port[1] == port:
            if self.verbose == True:
                print('Valve: "{}" already in position {}'.format(self.name, port))

        else:
            while True:
                self.write_message(self.message_builder('change', port))
                self.wait_ready()
                while True:
                    self.read_message() #flush output
                    #check current port after change
                    self.write_message(self.message_builder('read'))
                    response = self.read_message()
                    port_val = re.compile(b'0.\\r')
                    if re.match(port_val, response):
                        break        
                current_port = self.response_interpret(response)[1]
                if self.verbose == True: 
                    print('Valve: "{}" moved to port {}'.format(self.name, current_port))
                if current_port == port:
                    break
                    
