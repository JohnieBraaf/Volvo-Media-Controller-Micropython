import micropython, math
import ubinascii, uhashlib
from pyb import CAN
from pyboard.buf import FrameBuffer

class CanInterface:
    def __init__(self, itf, baudrate=1_000_000, sample_point=80, \
                            extframe=False, auto_restart=True, \
                            params=None, debug_rx=False, debug_tx=False):
        self.itf = itf
        self.baudrate= baudrate
        self.sample_point = sample_point
        self.extframe = extframe
        self.auto_restart = auto_restart
        self.params = params
        self.debug_rx = debug_rx
        self.debug_tx = debug_tx

        self.init()

    def init(self):
        self._buf = FrameBuffer(64)
        self._send_caller = self._sendcb
        self._recv_caller = self._recvcb

        self._can = CAN(self.itf, CAN.NORMAL, \
                           baudrate=self.baudrate, sample_point=self.sample_point, \
                           extframe=self.extframe, auto_restart=self.auto_restart)
        try:
            # fdcan interface
            mode = CAN.RANGE
            params = self.params or (0x0, 0x0) # default no filter
            self._can.setfilter(bank=self.itf-1, mode=mode, fifo=self.itf-1, params=params)
        except Exception as ex:
            # classic can interface
            if self.extframe: # extended id
                mode = CAN.MASK32
                params = self.params or (0x0, 0x0) # default no filter
            else: # classic id
                mode = CAN.MASK16
                params = self.params or (0x0, 0x0, 0x0, 0x0) # default no filter
            self._can.setfilter(bank=self.itf-1, mode=mode, fifo=self.itf-1, params=params)

        self._can.rxcallback(self.itf-1, self.receive)
        print ("CAN " + str(self.itf) + " initialized")

    def deinit(self):
        self._can.rxcallback(self.itf-1, None)
        self._can.deinit()

    def send(self, message, *args):
        # send the message in callback
        if len(args) == 1: # bytes and address
            micropython.schedule(self._send_caller, (message, args[0]))
        else: # micropython can msg format
            micropython.schedule(self._send_caller, message)

    def _sendcb(self, message):
        try:
            if isinstance(message, tuple): # bytes and address
                count = math.ceil(len(message[0]) / 8)
                for i in range(count):
                    msg_bytes = message[0][i * 8: (i * 8) + 8]
                    if i == count: # last message
                        msg_bytes = message[0][(i-1) * 8:]
                    self._can.send(msg_bytes, message[1])
                    self._print('TX', message[1], msg_bytes)
            else: # micropython can msg format
                self._can.send(message[3], message[0])
                self._print('TX', message[0], message[3])
        except Exception as ex:
            if ex.errno == 110: # ETIMEDOUT
                print('cannot send packet on CAN' + str(self.itf) + ', TX queue is full')
            else:
                print('cannot send packet on CAN' + str(self.itf) + ', '+ str(ex))

    @micropython.native
    def receive(self, bus, reason):
        if 0 <= reason < 3:
            while self._can.any(self.itf-1):
                self._can.recv(self.itf-1, self._buf.put())
            if reason == 2:
                print('lost packet on CAN' + str(self.itf) + ', RX queue overflow')
            if self.debug_rx: # print all incoming packets
                micropython.schedule(self._recv_caller, reason)

    def _recvcb(self, reason):
        while self._buf.any():
            msg = self._buf.get()
            self._print('RX', msg[0], msg[3])

    def _print(self, direction, address, message):
        try:
            if (self.debug_rx and direction == 'RX') or (self.debug_tx and direction == 'TX'):
                print(direction + ' | ', address, \
                      '|', '{0: <40}'.format(str(ubinascii.unhexlify(ubinascii.hexlify(message)))), \
                      '|', ubinascii.hexlify(message, ' '))
        except:
            print('could not print frame')

    def print_frame(self, direction, frame):
        try:
            print(direction + ' | ', frame[0], \
                  '|', '{0: <40}'.format(str(ubinascii.unhexlify(ubinascii.hexlify(frame[3])))), \
                  '|', ubinascii.hexlify(frame[3], ' '))
        except:
            print('could not print frame')