import sys
from magma import *
from mantle import *
from rom import ROM
from boards.icestick import IceStick

icestick = IceStick()
icestick.Clock.on()
icestick.TX.output().on()
icestick.D1.on()
icestick.D2.on()
icestick.D3.on()
icestick.D4.on()
icestick.D5.on()
icestick.RTS.on()
# icestick.CTS.output().on()
icestick.DTR.on()
    

main = icestick.main()

rtsCtrl = DFF() # up for one clock cycle after rts upedge
rtsBefore = DFF() # used to calculate rtsCtrl
wire(rtsBefore.I, main.RTS)

input = LUT3(I0&~I1&~I2)(main.RTS, rtsCtrl.O, rtsBefore)
wire(rtsCtrl.I, input)

# valid = 1

# init = [array(*int2seq(ord(c), 8)) for c in 'hello, world  \r\n']

# printf = Counter(4, ce=True) # determines which byte in init to send


# rom = ROM(4, init, printf.O) # this is a rom which selects 8-bit arrays

# data = array(rom.O[7], rom.O[6], rom.O[5], rom.O[4],
#              rom.O[3], rom.O[2], rom.O[1], rom.O[0], 0 ) # current byte split into bits

# clock = CounterModM(103, 8, ce=True) # clock that couts at baudrate
# baud = clock.COUT

# count = Counter(4, ce=True, r=True) # counts number of bits written?
# done = Decode(15, 4)(count) # true if on 16th bits

# notDone = Not()
# wire(done, notDone.I0)

# run = DFF(ce=True)
# run_n = LUT3([0,0,1,0, 1,0,1,0])
# run_n(done, valid, run)
# run(run_n) # run is low when we are loading a new byte
# wire(baud, run.CE) 

# reset = LUT2(I0&~I1)(done, run) # reset when done with 16 bits
# count(CE=baud, RESET=reset)

# shift = PISO(9, ce=True)
# load = LUT2(I0&~I1)(valid,run)
# shift(1,data,load)
# wire(baud, shift.CE)

# ready = LUT2(~I0 & I1)(run, baud)
# wire(ready, printf.CE) #printf increments when a whole byte is written

# wire(shift, main.TX)

# wire(main.RTS, main.D1)
# wire(main.DTR, main.D2)
# wire(1, main.D3)

slowClock = Counter(21, ce=True)
testCounter = Counter(4, ce=True)
wire(testCounter.CE, slowClock.COUT)

EOL = testCounter.COUT

EOLbefore = DFF()
wire(EOLbefore.I, EOL)

rtsSwitch = DFF()               # not at EOL, always continue after click
rtsSwitch_D = LUT4( (I0|I1) & ~I2 | (I2 & ~I3)) (rtsCtrl, rtsSwitch.O, EOL, slowClock.COUT)
wire(rtsSwitch_D, rtsSwitch.I)
wire(rtsSwitch.O, slowClock.CE)

wire(testCounter.O[0], main.D1)
wire(testCounter.O[1], main.D2)
wire(testCounter.O[2], main.D3)
wire(testCounter.O[3], main.D4)
wire(EOL, main.D5)


compile(sys.argv[1], main)

