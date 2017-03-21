import sys
from magma import *
from mantle import *
from rom import ROM
from boards.icestick import IceStick
from mdb import Debugger

def main():
    icestick = IceStick()
    icestick.Clock.on()
    icestick.TX.output().on()
    icestick.RTS.on()
    icestick.D1.on()
    icestick.D2.on()
    icestick.DTR.on()

    main = icestick.main()
    mdb = Debugger(main)

    valid = 1

    init = [array(*int2seq(ord(c), 8)) for c in 'hello, world  \r\n']

    printf = Counter(4, ce=True)
    rom = ROM(4, init, printf.O)

    data = array(rom.O[7], rom.O[6], rom.O[5], rom.O[4],
                 rom.O[3], rom.O[2], rom.O[1], rom.O[0], 0 )

    clock = CounterModM(103, 8, ce=True)

    mdb.ce(clock.CE, 1)
    baud = clock.COUT

    count = Counter(4, ce=True, r=True)
    done = Decode(15, 4)(count)

    run = DFF(ce=True)
    run_n = LUT3([0,0,1,0, 1,0,1,0])
    run_n(done, valid, run)
    run(run_n)
    mdb.ce(run.CE, baud) # wire(baud, run.CE)

    reset = LUT2(I0&~I1)(done, run)
    mdb.ce(count.CE, baud)
    wire(count.RESET, reset)

    shift = PISO(9, ce=True)
    load = LUT2(I0&~I1)(valid,run)
    shift(1,data,load)
    mdb.ce(shift.CE, baud) # wire(baud, shift.CE)

    ready = LUT2(~I0 & I1)(run, baud)
    mdb.ce(printf.CE, ready) # wire(ready, printf.CE)

    test = Counter(17, ce=True)
    mdb.ce(test.CE, 1)

    mdb.track(baud, "Baud")
    mdb.track(run.O, "Run")
    mdb.track(clock, "BaudClock")
    mdb.track(ready, "Ready")
    mdb.track(count, "Count")
    mdb.track(done, "Done")
    mdb.track(printf, "Printf")
    # mdb.track(test, "test")

    # wire(main.CLKIN, main.J3[0])
    # wire(baud,       main.J3[1])
    # wire(run,        main.J3[2])
    # wire(done,       main.J3[3])
    # wire(shift,      main.J3[4])
    #wire(ready,      main.J3[5])
    #wire(valid,      main.J3[6])
    #wire(count,      main.J3[4:8])
    mdb.debug()
    compile(sys.argv[1], main)

if __name__ == "__main__":
    main()