import sys
from magma import *
from mantle import *
import math
from rom import ROM
from boards.icestick import IceStick

icestick = IceStick()
icestick.Clock.on()
icestick.TX.output().on()
icestick.RTS.on()
# icestick.CTS.output().on()
icestick.DTR.on()
    

main = icestick.main()

class Debugger:
    """
        __mdb_uart() - Defines Magma code for UART which outputs state saved in init
    """
    def __mdb_uart(self):
        if not self.init and len(self.init):
            self.init = [array(*[0, 0, 0, 0, 0, 0, 0, 0])]*8
        valid = 1

        # data to be sent
        printf = Counter(int(math.log(len(init),2)), ce=True) # determines which byte in init to send
        rom = ROM(int(math.log(len(init),2)), init, printf.O) # selects 8-bit arrays from the array of inits
        data = array(1, rom.O[7], rom.O[6], rom.O[5], rom.O[4],
                     rom.O[3], rom.O[2], rom.O[1], rom.O[0], 0) # current byte split into bits

        # baud clock
        clock = CounterModM(103, 8, ce=True) # clock that couts at baudrate
        baud = clock.COUT

        # count bits written in current byte
        count = Counter(5, ce=True, r=True)
        done = Decode(30, 5)(count) # true if byte has finished sending, and some padding 1s have been written

        # run determines if bits are currently being sent
        run = DFF(ce=True)
        run_n = LUT3([0,0,1,0, 1,0,1,0])
        run_n(done, valid, run)
        run(run_n) # run is low when we are loading a new byte
        wire(baud, run.CE) 

        # reset when done with byte
        reset = LUT2(I0&~I1)(done, run)
        count(CE=baud, RESET=reset)

        #printf increments when a whole byte is written
        shift = PISO(10, ce=True)
        load = LUT2(I0&~I1)(valid,run)
        shift(1,data,load)
        wire(baud, shift.CE)
        ready = LUT2(~I0 & I1)(run, baud)
        wire(ready, printf.CE) 
        wire(shift, main.TX) # output to TX

        # Clock should run until reaches firstByte again.  Triggered by RTS
        firstByte = Decode(0,3)(printf)
        EOL = LUT2(I0&I1)(firstByte,done)
        rtsSwitch = DFF()
        rtsSwitch_A = LUT4( (I0|I1) & ~I2 | (I2 & ~I3)) (self.rtsCtrl, rtsSwitch.O, EOL, baud)
        wire(rtsSwitch_A, rtsSwitch.I)
        wire(rtsSwitch.O, clock.CE) 
        

    def mdb_dtrrts_setup(self):
        # RTS SETUP
        rtsCtrl = DFF() # up for one clock cycle after rts upedge
        rtsBefore = DFF() # used to calculate rtsCtrl
        input = LUT3(I0&~I1&~I2)(main.RTS, rtsCtrl.O, rtsBefore) #calculation of rtsCtrl
        wire(rtsBefore.I, main.RTS)
        wire(rtsCtrl.I, input)
        self.rtsCtrl = rtsCtrl

        # DTR SETUP
        dtrCtrl = DFF() # up for one clock cycle after dtr upedge
        dtrBefore = DFF() # used to calculate dtrCtrl
        input = LUT3(I0&~I1&~I2)(main.DTR, dtrCtrl.O, dtrBefore) #calculation of dtrCtrl
        wire(dtrBefore.I, main.DTR)
        wire(dtrCtrl.I, input)
        self.dtrCtrl = dtrCtrl


    def is_power2(num):
        return num != 0 and ((num & (num - 1)) == 0)


    """
        track() - adds circuit components to output tracked bits to UART
    """
    def track(self):
        n = len(self.init)
        if not is_power2(n):
            logn = int(math.floor(math.log(n,2)))
            desiredN = 2**(logn+1)
            for x in range(desiredN):
                init.append(array(*[0, 0, 0, 0, 0, 0, 0, 0]))

        self.mdb_dtrrts_setup()
        self.__mdb_uart()

    """
    writeNames() - dump names of bits to textfile
    """
    def writeNames(self):
        pass

    def __init__(self):
        self.init = []
        self.bits = []
        self.names = []
        self.rtsCtrl = None
        self.dtsCtrl = None

mdb = Debugger()
c = Counter(8,ce=True)
wire(c.CE, dtrCtrl.O)
mdb.init = [c.O];

compile(sys.argv[1], main)