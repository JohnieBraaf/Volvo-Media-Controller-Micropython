from pyboard.lin import LinInterface
from pyboard.can import CanInterface

# print board info
print('H743 - Volvo Media Controller')

# start LIN bus
lin1 = LinInterface(uart=7, baudrate=9600, tx='E8', rx='E7', en='E9', rst='E10')
lin2 = LinInterface(uart=2, baudrate=9600, tx='A2', rx='A3', en='A1', rst='A0')

# start CAN bus
can1 = CanInterface(1, baudrate=125_000, sample_point=80, extframe=False, params=(0x0, 0x0))
can2 = CanInterface(2, baudrate=125_000, sample_point=80, extframe=False, params=(0x0, 0x0))