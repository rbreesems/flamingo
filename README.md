# flamingo
Repo for sharing utilities for in-cave communication project using Meshtastic-based radios.  This is an extension of (but not affilated with) the work done by the [Vangelis](https://github.com/semper-ad-fundum/vangelis) project.

With tongue-in-cheek, if flamingo has to stand for something, then:

`FLAMINGO` - Forward Link And Mesh Interconnect Network Ground Operations !!!!! 


AKA -> Using Meshtastic radios for underground (cave) communication

# Background

We are members of the Huntsville Cave Rescue Unit [HCRU](https://www.hcru.org/) and one of our members (J. Moon) saw the Vangelis work and thought this could be useful in a cave rescue situation.  We use wired comms for cave rescues, but the problem is that the decades-old field phones that are used have no readily-available replacements, so a more modern approach is needed.

After looking at the Vangelis work, J. Moon recruited some tech-minded folks from the unit, and we started working.  The [Vangelis](https://github.com/semper-ad-fundum/vangelis) site gives a good summary of their attempt at using Meshtastic radios in a cave, and we used their tips on how to configure radios and what to expect when radios are placed in a cave.

A cave environment is much different from open air, with radios needing to be placed within near LOS of each other to form a linear chain (not a mesh) that forwards packets to/from the surface.   One of the challenges is the max hop limit of 7 that is in the current Meshtastic firmware - this limit is because two 3-bit fields (`hop_limit` and `hop_start`) are used in the packet header to track hops. The `hop_limit` is set to the max hop limit configuration setting.  The `hop_start` field is the max hop limit that the packet started with, and is decremented each time the packet is forwared. The difference between `hop_limit` and `hop_start` is the number of hops the packet has traveled.  When `hop_start` reaches 0, the packet is no longer forwarded.

Meshtastic guidance is that 3 is typically a sufficient value for maximum hops for most mesh configuations to avoid packet congestion. However, our configuration is a linear chain, so mesh congestion is not an issue. We require more hops than 7, with the max feasible limit something to be discovered through testing.

# Firmware Modifications

This [repo](https://github.com/meshtastic/firmware) is our fork of the meshtastic repo.   We have been using RAK4630-based radios, both built-from-scratch with 3D printed enclosures and off-the-shelf 
[WisMeshPocket V2](https://store.rokland.com/products/wismesh-pocket).

The following summarizes our firmware modifications.

## Hop Limit Extension

The packet header was modified to provide 8-bit fields for both `hop_limit` and `hop_start`.  This means an upper limit of 255 hops, but our firmware has set the maxium limit to 31 hops as probably this is the maxinum number of radios any sane individual would want to bring into a cave (however, this is easily changed to a higher number up to 255 if desired)

The packet header was extended by four bytes (must be aligned on a four-byte boundary) with one byte each for `hop_limit` and `hop_start` and the other two bytes for a 16-bit magic number used to identify our packets. 

Modifying the packet header structure has the following ramifications:

1. Our radios can only talk with each other, they cannot talk to any radios using normal Meshtastic firmware.
2. A normal Meshtatic packet arriving at one of our radios is rejected upon reciept after header parsing because of a magic number mismatch. There is a 1/66536 chance (~ 0.002%) that the magic number will be correct, but the packet will be rejected after further parsing due to structure mismatch.
3. Our packet header is constructed such that the original `hop_limit` and `hop_start` fields will have values of 1 and 0, respectively, so this packet will not be forwarded after the header is parsed.  Unpacking this packet will fail due to fields mismatch and so will be rejected.

There was enough extra bytes in the original Meshtastic packet structure that the 200-byte payload limit was not affected by the packet header modification.

Setting the hop-limit greater than 7 has to be done via the CLI as the phone apps all assume the max hop limit is 7.

## Range Test Packet hopping

Our desired methodology for placing radios in the cave is as follows:

1. The surface node is configured to send out range test packets.
2. The comms team leader with the radios has one radio that is being monitored for range test packet reception. The leader advances into the cave until no longer reliably receiving range test packets (so at max range), backs up a bit, then puts down a relay node.
3. The comms team leader then advances with the relay node forwarding range test packets.  This procedure is repeated until the linear chain is completed.

We quickly discovered in above ground tests that the unmodified Meshtastic firmware sets range test packets to have a `hop_start` value of 0 so that they are not forwarded after arrival.  This invalidates the above methodology, and would require each relay node to be configured as a range test packet sender when placing the next relay node.  This would slow down radio placement and require extra actions by the comms team leader.

The solution was simply to set the `hop_start` field in range test packets to the normal value of the maxium hop limit so that range test packets hop between relay nodes.   This was done in our firmware and it worked during in-cave testing.

## Other changes

1. Logging of all communication at Incident Command (IC) during a rescue is of critical importance. Our assumption is that the relay chain extends all the way to IC, with a laptop hooked to the surface node so that serial logging can be done.  The messages output to the serial port during operation were slightly modified so that they could be easily parsed afterwards, and incoming/outgoing messages with timestamps easily summarized. We use Microsoft Code + Serial Monitor plugin for serial monitoring. We used this methodology during testing and it worked well.

2. Easy Remote Admin of Range Test - since range test is integral to radio placement, we need easy/simple control of range test packets. The current method of changing range test by writing settings has a problem in that it is cumbersome to setup remote admin just for this capability, and writing settings to the sending (surface node) causes the device to reboot, which halts serial logging.  The person monitoring the surface node may or may not re-enable serial logging, and critical log information could be lost. 

To address these issues, the range test module has been changed to add a dynamic enable/disable capability for the sender. Configure the sending node as before, but in order for range test packet sending to be enabled, it must receive a 'RT on' message on any channel (direct or general).  To turn RT sending off, just send an 'RT off' message. These simple messages were chosen to be compatible with voice-to-text translation.

3. TODO: More range test modifications to reduce channel clogging.

4. TODO: Realtime RSSI visualization.


# Utility Software

The `utils` subdirectory has the following python scripts:

1. The `config.py` is a script for writing settings to a radio using the `meshtastic` CLI. It reads a YML file that contains the settings (see `cave_node.yml` for an example). It is critical that all radios be configured in the same way and this script streamlines the process. During script operation, the settings are read back from the radio after programming to verify that all settings were transferred correctly, and loops up to three times to complete the programming. We have noticed that a radio does not not always get all of the setting on the first try (for unknown reasons) so the verification loop is necessary.  This script also writes an information file to the `infofiles` subdirectory so that a record of each radio that is programmed is saved.

2. The `gen_csv.py` is a utility that parses all of the files in the `infofiles` subdirectory and writes out a summary CSV file. The format of the CSV file is specified by a YML file, see the `node_csvspec.yml` file for an example. This gives you a handy summary of all of the radios that have been programmed.

3. The `log_parse.py` file is a utility for parsing the radio serial log files to produce a summary of incoming/outgoing messages + timestamps.


# Testing

Will let J. Moon fill this out.




