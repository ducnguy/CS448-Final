#MagDebug
Team Members: Duc Nguyen

#Goal: 
The goal of the project is to build a debugging framework on top of Magma.  The API will provide functions which "wrap" existing Magma hardware designs with circuits that will count clock cycles and store hardware states at certain points of execution (i.e. specific clock cycles).  A UART will be utilized for relaying debug info to the host machine.

#Motivation: 
As we have seen with the example of the Toastboard [Hartmann et al.], ubiquitous examination of a system with immediate visualization allows users to diagnose problems based on a wealth of data instead of having to form a single hypothesis and plan before taking a measurement.  With the MagDebug system, users should be able to test a hypotheses without making major changes to their code or writing test prototypes.  For users (like myself) that are new to hardware/FPGA design, this will speed up the learning process, and help make the task of writing simple designs as easy and unintimidating as it should be.  For more experienced users, MagDebug will hopefully accomplish some use cases similar to the ones software debugging tools like GDB accomplish (being able to step through and examine execution by clock cycle, examining hardware state after N number of clock cycles).

#Previous Work: 
This article http://www.newelectronics.co.uk/electronics-technology/debugging-methods-for-fpgas/18546/ provides a good summary of existing FPGA debugging methods.  Some notable points from the article are:
  - Hardware debugging using the ispLever EPIC design editor: "EPIC is a design editor that displays the exact implementation of the design in hardware and which also can be used interactively to make smaller modifications to the design after synthesis. Typical modifications include changing selected I/O Standards, adding debugging probes or inverting signals."
  - Hardware debugging using Lattice Reveal tool: "Lattice has implemented a tool called Reveal which is included in the ispLEVER software environment. With Reveal no external logic analyser or free pins on the fpga are required. The software in the system logic analyser captures signal activity and stores the information in internal RAM Blocks. The storedinformation is passed via the JTAG interface to the software analyser running on the PC. The trigger conditions can be changed on the fly without changing the design.
    
Though these are reasonable debugging tools, they require developing under the ispLever development environment, which is currenlty only provided on Windows machines.  Furthermore, this approach would not allow the same metaprogramming capabilites that Magma affords.

#Resources:
- UART with configurable baud rate: http://www.ijritcc.org/download/IJRITCC_1352.pdf
- Existing debugging methods: http://www.newelectronics.co.uk/electronics-technology/debugging-methods-for-fpgas/18546/
- Toastboard for design ideas: https://bid.berkeley.edu/files/papers/toastboard.pdf

#Tasks:
- **week 1**
  - design Magma API for hooking up wires to be saved by registers at certain points in time
  - design Magma API for wrapping design for single step examination
  - implement UART
- **week 2-3**
  - implement Magma process for hooking up wires to be saved by registers at certain points in time
  - connect registers in previous point to be sent by UART to PC
- **week 3-4**
  - implement Magma API for wrapping design for single step examination
  - allow PC input to control single stepping
