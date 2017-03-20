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

valid = 1

init = [array(*[0, 0, 0, 0, 0, 0, 0, 0]), array(*[0, 0, 0, 0, 0, 0, 0, 1]),array(*[0, 0, 0, 0, 0, 0, 1, 0]), array(*[0, 0, 0, 0, 0, 0, 1, 1]), array(*[0, 0, 0, 0, 0, 1, 0, 0]), array(*[0, 0, 0, 0, 0, 1, 0, 1]), array(*[0, 0, 0, 0, 0, 1, 1, 0]), array(*[1, 0, 0, 0, 0, 0, 0, 1])];

printf = Counter(3, ce=True) # determines which byte in init to send
printf_b = Sub(3)
wire(printf, printf_b.I0)
wire(array(*[0, 1, 1]), printf_b.I1)

rom = ROM(3, init, printf.O) # this is a rom which selects 8-bit arrays from the array of inits

data = array(1, rom.O[7], rom.O[6], rom.O[5], rom.O[4],
             rom.O[3], rom.O[2], rom.O[1], rom.O[0], 0) # current byte split into bits


clock = CounterModM(103, 8, ce=True) # clock that couts at baudrate
baud = clock.COUT


count = Counter(5, ce=True, r=True) # counts number of bits written
done = Decode(30, 5)(count) # true if on 16th bit

run = DFF(ce=True)
run_n = LUT3([0,0,1,0, 1,0,1,0])
run_n(done, valid, run)
run(run_n) # run is low when we are loading a new byte
wire(baud, run.CE) 

reset = LUT2(I0&~I1)(done, run) # reset when done with 16 bits
count(CE=baud, RESET=reset)

shift = PISO(10, ce=True)
load = LUT2(I0&~I1)(valid,run)
shift(1,data,load)
wire(baud, shift.CE)

ready = LUT2(~I0 & I1)(run, baud)
wire(ready, printf.CE) #printf increments when a whole byte is written

EOL = Decode(7,3)(printf)
rtsSwitch = DFF()
rtsSwitch_A = LUT4( (I0|I1) & ~I2 | (I2 & ~I3)) (rtsCtrl, rtsSwitch.O, EOL, baud)

wire(rtsSwitch_A, rtsSwitch.I)
wire(rtsSwitch.O, clock.CE) # CLOCK SHOULD RUN UNTIL PRINTF REACHES EOL

not_ = Not()
wire(not_.I0, rtsSwitch.O)
wire(not_.O, main.D5)

wire(shift, main.TX)

wire(main.RTS, main.D1)
wire(main.DTR, main.D2)
wire(1, main.D3)

# testCounter = Counter(27, ce=True)

# EOL = testCounter.COUT

# EOLbefore = DFF()
# wire(EOLbefore.I, EOL)

# rtsSwitch = DFF()               # not at EOL, always continue after click
# rtsSwitch_D = LUT3( ((I1 & ~I2) | I0)) (rtsCtrl, rtsSwitch.O, EOL)
# wire(rtsSwitch_D, rtsSwitch.I)
# wire(rtsSwitch.O, testCounter.CE)

# wire(testCounter.O[23], main.D1)
# wire(testCounter.O[24], main.D2)
# wire(testCounter.O[25], main.D3)
# wire(testCounter.O[26], main.D4)
# wire(EOL, main.D5)


compile(sys.argv[1], main)

