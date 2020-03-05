# MXII-valve
MX Series II actuated valve from Rheodyne, now IDEX.

Python module to control the [MX Series II](https://www.idex-hs.com/store/valves/stand-alone-valve-products/mx-series-iitm.html) actuated valve over USB. Software was written susing the MX Series II(TM) Driver Development Package, File-1418039677, downloaded from [here](https://www.idex-hs.com/support/literature-downloads/operation-manuals).

# Get started
- Make sure [pyserial](https://pythonhosted.org/pyserial/) is installed.
- Connec the valve with USB.
- Make sure the valve is in the "remote" operation mode by pressing the button on the front pannel. LED should be on. 
- Import the module: `import MXII_valve`.
- Find the USB address of the valve: `valve_address = MXII_valve.find_address()[0]`
- This will give you an address in the format of `COMX` on Windows or `dev/ttyUSBX` on Linux.
- It will also give you an identifire for the FTDI chip inside the valve. This ID is unique to the valve and can be used to find the port quicker in the future by: `MXII_valve.find_address(identifier = ID)`
- Initiate the valve: valve = `MXII_valve.MX_valve(valve_address, ports=10, name='My_valve', verbose=True)



### Disclaimer
This code was developed and tested on the MXX778-605 10-position, 11-port motorized low pressure valve. The code should work for other models but this is not tested. Please contribute to the project if you optimize the code for other modles. 
