# Hardware variants 

## HCRU 

### Cavenode

### Slink 

### Gen2 

### Hybrid


---
## NSWCRS

We use custom boards, all off the RAK4630 at this point.
We also use a combination of commercial ones for testing, and other purposes.
- Seeed T1000E
- Seeed nrfkit
- Heltec T114
- Heltec 3


| Type     | Processor | BMS | GPS | UI  LED | buzzer | log (SD) | RS485 | IP rating |
| -        |  -        | -   |  -  | -       | -      | -        | -     | -         |
| Basic    | RAK4630   | Y   | opt | Y       | N      | N        |  N    |  IP68     |
| RS485    | RAK4630   | Y   | N   | Y       | N      | opt      |  Y    | IP67      |
| Logger   | RAK4630   | Y   | opt | Y       | N      | Y        |  opt  | IP67      |
| Surface  | Rpi zero  | Y   | opt | N       | N      | Y        |  N    | -         |
| ParaNode | RAK4630   | Y   | Y   | N       | N      | N        |  N    | IP67      |

*ParaNode coming soon, cost down, and integrated GPS for paragliding*

### Basic units

Custom designed circuit board using a RAK4630, 
Board is 65x20 mm
Features:
- Inbuilt battery protection
- Reed switch / regular switch to isolate the battery when in the case (exposed to magnetic field)
- 2x RGB leds(RT and message controlled), and 2x single colour LEDS (HB, and packet rx)
- Optional GPS
- Optional I2C
- Optional magnetic USB connector
- 5v Solar compatible
- Directly compatible with 18650 (approx 1 week) or other LiPo

### RS485 / Logger  

Custom designed circuit board using a RAK4630, 
Board is 90x30 mm
Features:
- Inbuilt battery protection
- Reed switch / regular switch to isolate the battery when in the case (exposed to magnetic field)
- 2x RGB leds(RT and message controlled), and 2x single colour LEDS (HB, and packet rx)
- Optional GPS 
- Optional I2C
- Optional magnetic USB connector
- 5v Solar compatible
- Directly compatible with 18650 (approx 1 week) or other LiPo
- Footprint for an openLog SD card logger 
- RS485 interface

### Surface 

RPi zero, with a hat (currently using a wifi enabled heltec 3, not the hat)

Features: 
- Runs web UI on local network to allow monitoring of last heard, and battery voltages, and track them over time 
- Can autoreply / emote to all messages. 
- Logs all traffic 
- Hopefully eventually be able to monitor Neighbours
