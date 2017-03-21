import sys
from magma import *
from mantle import *
import math
from rom import ROM
from boards.icestick import IceStick

def is_power2(num):
    return num != 0 and ((num & (num - 1)) == 0)

class Debugger:
    """
        __mdb_uart() - Defines Magma code for UART which outputs state saved in init
    """
    def __mdb_uart(self):
        if not self.init and len(self.init):
            self.init = [array(*[0, 0, 0, 0, 0, 0, 0, 0])]*8
        valid = 1

        # data to be sent
        numBytes = int(math.log(len(self.init),2))
        printf = Counter(numBytes, ce=True) # determines which byte in init to send
        rom = ROM(numBytes, self.init, printf.O) # selects 8-bit arrays from the array of inits
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
        wire(shift, self.main.TX) # output to TX

        # Clock should run until reaches firstByte again.  Triggered by RTS

        firstByte = Decode(0,numBytes)(printf)
        EOL = LUT2(I0&I1)(firstByte,done)
        rtsSwitch = DFF()
        rtsSwitch_A = LUT4( (I0|I1) & ~I2 | (I2 & ~I3)) (self.rtsCtrl, rtsSwitch.O, EOL, baud)
        wire(rtsSwitch_A, rtsSwitch.I)
        wire(rtsSwitch.O, clock.CE) 
        wire(self.main.D1, self.main.RTS)
        wire(self.main.D2, self.main.DTR)
        

    def __mdb_dtrrts_setup(self):
        # RTS SETUP
        rtsCtrl = DFF() # up for one clock cycle after rts upedge
        rtsBefore = DFF() # used to calculate rtsCtrl
        input = LUT3(I0&~I1&~I2)(self.main.RTS, rtsCtrl.O, rtsBefore) #calculation of rtsCtrl
        wire(rtsBefore.I, self.main.RTS)
        wire(rtsCtrl.I, input)
        self.rtsCtrl = rtsCtrl

        # DTR SETUP
        dtrCtrl = DFF() # up for one clock cycle after dtr upedge
        dtrBefore = DFF() # used to calculate dtrCtrl
        input = LUT3(I0&~I1&~I2)(self.main.DTR, dtrCtrl.O, dtrBefore) #calculation of dtrCtrl
        wire(dtrBefore.I, self.main.DTR)
        wire(dtrCtrl.I, input)
        self.dtrCtrl = dtrCtrl

    """
    writeNames() - dump names of bits to textfile
    """
    def __write_names(self):
        target = open('names.txt', 'w')
        for name in self.names:
            target.write(name)
            target.write('\n')
        pass

    """
    track() - takes either an array of bits, or a single bit as first argument,
              and adds it to the list of bits to be tracked .
    """
    def track(self, toTrack, name):
        #TODO: check name and toTrack type
        if hasattr(toTrack, 'interface'):
            toTrack = toTrack.interface.outputs()
            
        if isinstance(toTrack, Sequence):
            for i in range(len(toTrack[0])): 
                self.bits.append(toTrack[0][i])
                self.names.append(name + "_" + str(i)) 
        else:
            self.bits.append(toTrack)
            self.names.append(name)

    def __pad_init(self):
        n = len(self.init)

        if n == 0:
            for x in range(0):
                self.init.append(array(*[0, 0, 0, 0, 0, 0, 0, 0]))

        elif n == 1:
            for x in range(1):
                self.init.append(array(*[0, 0, 0, 0, 0, 0, 0, 0]))

        elif not is_power2(n):
            logn = int(math.floor(math.log(n,2)))
            desiredN = 2**(logn+1)
            for x in range(desiredN):
                self.init.append(array(*[0, 0, 0, 0, 0, 0, 0, 0]))

    def __populate_init(self):
        print self.bits
        i = 0
        n = len(self.bits)
        currArr = []
        while i < n:
            currArr.insert(0,self.bits[i])
            i += 1
            if len(currArr) == 8:
                self.init.insert(0,array(*currArr))
                currArr = []

        while len(currArr) < 8:
            currArr.insert(0,0)

        self.init.append(array(*currArr))
        print "INIT: ", self.init

    """
        debug() - adds circuit components to output tracked bits to UART
    """
    def debug(self):
        
        self.__populate_init()
        self.__pad_init()
        self.__mdb_dtrrts_setup()
        self.__mdb_uart()
        self.__write_names()
    

    def __init__(self, main):
        self.init = []
        self.bits = []
        self.names = []
        self.rtsCtrl = None
        self.dtrCtrl = None
        self.main = main





