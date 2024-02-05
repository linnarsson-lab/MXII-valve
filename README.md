# MXII-valve
MX Series II actuated valve from Rheodyne, now IDEX.

Python module to control the [MX Series II](https://www.idex-hs.com/store/valves/stand-alone-valve-products/mx-series-iitm.html) actuated valve over USB. Software was written susing the MX Series II(TM) Driver Development Package, File-1418039677, downloaded from [here](https://www.idex-hs.com/docs/default-source/product-manuals/mx-series-ii-operating-manual.pdf?sfvrsn=419402f3_3).

# Get started
- Make sure [pyserial](https://pythonhosted.org/pyserial/) is installed.
- Connect the valve with the provided USB cable.
- Make sure the valve is in the "remote" operation mode. Press the the button on the front pannel if this is not the case. The LED should be on. 
- In a Python interpreter, import the module: `import MXII_valve`.
- Find the USB address of the valve: `valve_address = MXII_valve.find_address()[0]` 
- The find_address() function returns a port object, where the first item contians the address in the format of `COMX` on Windows or `dev/ttyUSBX` on Linux. The address will also be printed. 
- It will also give you an ID nubmer for the FTDI chip inside the valve. This ID is unique to the valve and can be used to find the port quicker in the future by: `MXII_valve.find_address(identifier = <ID>)`
- Initiate the valve: `valve = MXII_valve.MX_valve(valve_address, ports=10, name='My_valve', verbose=True)` Change the number of ports depending on your model. 
- Now the valve is ready for operation

# Troubleshooting
Make sure the [FTDI drivers](https://ftdichip.com/drivers/x) are installed.  
If you get an error that the valve is not properly connected. Please download the [control software](https://www.idex-hs.com/resources/software-drivers#:~:text=MX%20Series%20II%E2%84%A2%20Control%0ASoftware%20Program) from the manufacturer. Connect to the valve with their software and try the Python code again.    

# Functions
The valve has two main functions:
- Get the current port with: `valve.get_port()`
- Change the port to a desired port, for example port 3: `valve.change_port(3)` The program will block untill the valve is ready for the next operation.

# Citation
If this code is usefull for your work, please cite:  
[Borm et. al. (2023) Scalable in situ single-cell profiling by electrophoretic capture of mRNA using EEL FISH. Nature Biotechnology.](https://doi.org/10.1038/s41587-022-01455-3)


# Disclaimer
This code was developed and tested on the MXX778-605 10-position, 11-port motorized low pressure valve. The code should work for other models but this is not tested. Furthermore, not all possible functionalities are implemented yet, refer to the manual to implement them. Please contribute to the project if you test other models or implement more functions.
