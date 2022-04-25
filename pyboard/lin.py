from machine import Pin
from pyb import UART

class LinInterface:
    def __init__(self, uart, baudrate, tx, rx, en, rst=None):
        self.tx  = Pin(tx, Pin.OUT) # RX on Lin board
        self.rx  = Pin(rx, Pin.IN)  # TX on Lin board
        self.en  = Pin(en, Pin.OUT)
        self.rst = Pin(rst, Pin.IN) if rst else None

        self.en.value(1) # enter normal mode
        self.tx.value(1) # enable tranciever

        #self._recv_caller = self._recvcb

        self.lin = UART(uart, baudrate)
        #print(dir(self.rx))
        #self.lin.irq(trigger=Pin.IRQ_RISING, handler=self.receive)


    #def _recvcb(self, reason):
    #    while self._buf.any():
    #        msg = self._buf.get()
    #        self._print('RX', msg[0], msg[3])

    @micropython.native
    def receive(self, bus, reason):
        print('hallo')

    def sleep(self):
        # re-init TX as output pin
        self.tx  = Pin(self.tx.name(), Pin.OUT)

        # create a falling edge on en-pin with tx low to enter sleep mode
        #self.tx.value(1)
        self.en.value(1)
        time.sleep_ms(1)
        self.tx.value(0)
        self.en.value(0)