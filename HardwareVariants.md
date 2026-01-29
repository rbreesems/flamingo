# Hardware variants 

## Huntsville Cave Rescue Unit (HCRU)/US

Our base hardware:
 - [RAK 19007 (WisBlock Base Board 2nd Gen)](https://docs.rakwireless.com/Product-Categories/WisBlock/RAK19007/Datasheet)
 - [RAK 4631 WisBlock Core module](https://docs.rakwireless.com/product-categories/wisblock/rak4631/datasheet).


This is available as the [RAKwireless WisBlock Meshtastic Starter Kit](https://store.rokland.com/products/rak-wireless-wisblock-meshtastic-starter-kit) from [store.rokland.com](store.rokland.com).

For the nodes that support the RS485 interface, we add the [RAK5801, RS485 Module](https://store.rakwireless.com/products/rak5802-rs485-interface?index=55).  This plugs into the RAK 19007 baseboard.

The principle variants listed in the `variants/nrf52840/rak4631/platform.ini` file are:

- `rak4631_flamingo` - base rak4631 build with Flamingo changes, compatible with off-the-shelf rak4631 radios like the [WisMesh Pocket V2](https://store.rokland.com/products/wismesh-pocket?srsltid=AfmBOooeGzU1v4pVKmmec-tGHulBCdLEFPMxsXNFNIvhLJSC50dYbHwc)

- `rak4631_slink` - adds support for the RS485 interface, we use this in our latest hybrid nodes that support wireless + wired

- `rak4631_cavegen2`  - our 2nd generation wireless only radios, has a blinky IO pin and a buzzer IO pin. Our packaging includes both the blinky LED and a buzzer.  See the build flags for pin assignments.



---
## New South Wales Cave Resce Squad (NSWCRS)/Australia

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
![Basic Node](./img/CaveNode_basic.jpg)

Custom designed circuit board using a RAK4630, 
Board is 72.8x18.7 mm
$23.15 USD board cost @20 (JLCPCB)
Features:
- Inbuilt battery protection
- Reed switch / regular switch to isolate the battery when in the case (exposed to magnetic field)
- 3x RGB leds(Meshtastic heartbeat / packet Rx, RangeTest and message controlled)
- Optional GPS
- Optional I2C
- Optional magnetic USB connector
- 5v Solar compatible
- Directly compatible with 18650 (approx 1 week) or other LiPo
- Case is IP67 - ABS with dual TPU gaskets around print in place thread


### RS485 / Logger  
![RS485 Node](./img/RS485_Node.jpg)
![RS485 Board](./img/RS485_Board.jpg)

Custom designed circuit board using a RAK4630, 
Board is 79.4x26.7 mm
$39 USD board cost @5 (JLCPCB)
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
- Case is IP67 - ABS with dual TPU gaskets around print in place thread

### Surface 

RPi zero, with a hat (currently using a wifi enabled heltec 3, not the hat)
Runs [MeshMonitor](https://github.com/DaneEvans/meshMonitor)

Features: 
- Runs web UI on local network to allow monitoring of last heard, and battery voltages, and track them over time 
- Can autoreply / emote to all messages. 
- Logs all traffic 
- Hopefully eventually be able to monitor Neighbours
