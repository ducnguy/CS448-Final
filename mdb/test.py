import sys
from magma import *
from mantle import *
import math
from rom import ROM
from boards.icestick import IceStick
from mdb import Debugger

icestick = IceStick()
icestick.Clock.on()
icestick.TX.output().on()
icestick.RTS.on()
icestick.D1.on()
icestick.D2.on()
icestick.DTR.on()
    
main = icestick.main()

mdb = Debugger(main)

c = Counter(8, ce=True)
mdb.track(c, "TestCounter")
mdb.track(c.O[0], "TestBit")
mdb.ce(c.CE, 1)

mdb.debug()
compile(sys.argv[1], main)

