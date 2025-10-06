# flamingo
Repo for sharing utilities for in-cave communication project using Meshtastic-based radios.  This is an extension of (but not affiliated with) the work done by the [Vangelis](https://github.com/semper-ad-fundum/vangelis) project.

With tongue-in-cheek, if flamingo must stand for something, then:

`FLAMINGO` - Forward Link And Mesh Interconnect Network Ground Operations !!!!! 


AKA -> Using Meshtastic radios for underground (cave) communication

# Background

We are members of the Huntsville Cave Rescue Unit [HCRU](https://www.hcru.org/) and one of our members (J. Moon) saw the Vangelis work and thought this could be useful in a cave rescue situation.  We use wired comms for cave rescues, but the problem is that the decades-old field phones that are used have no readily-available replacements, so a more modern approach is needed.

After looking at the Vangelis work, J. Moon recruited some tech-minded folks from the unit, and we started working.  The [Vangelis](https://github.com/semper-ad-fundum/vangelis) site gives a good summary of their attempt at using Meshtastic radios in a cave, and we used their tips on how to configure radios and what to expect when radios are placed in a cave.

A cave environment is much different from open air, with radios needing to be placed within near LOS of each other to form a linear chain (not a mesh) that forwards packets to/from the surface.   One of the challenges is the max hop limit of 7 that is in the current Meshtastic firmware - this limit is because two 3-bit fields (`hop_limit` and `hop_start`) are used in the packet header to track hops. The `hop_limit` is set to the max hop limit configuration setting.  The `hop_start` field is the max hop limit that the packet started with, and is decremented each time the packet is forwarded. The difference between `hop_limit` and `hop_start` is the number of hops the packet has traveled.  When `hop_start` reaches 0, the packet is no longer forwarded.

Meshtastic guidance is that 3 is typically a sufficient value for maximum hops for most mesh mesh configurations to avoid packet congestion. However, our configuration is a linear chain, so mesh congestion is not an issue. We require more hops than 7, with the max feasible limit something to be discovered through testing.

# Firmware Modifications

This [repo](https://github.com/rbreesems/firmware) is our fork of the meshtastic repo.   We have been using RAK4630-based radios, both built-from-scratch with 3D printed enclosures and off-the-shelf 
[WisMeshPocket V2](https://store.rokland.com/products/wismesh-pocket).

The branches `may2025` (firmware 2.5) `hopmod_2_6_11` (firmware 2.6) contains our modifications (other branches should not be used).  The following summarizes our changes:

- Packet header has been changed to support a hop limit up to 255, but firmware has it limited to 31.
See the section on hop limit modification for a discussion of this change. The most important ramification is that radios with this firmware can only talk to radios with the same firmware.

- LCD splash screen displays HCRU firmware version name.

- Range test has been modified to support non-hopping/hopping range test packets.  Default is non-hopping.  It has also been modified to be enabled even when GPS code is excluded. Also, range test data is never saved to storage.

- Range test messages sent to phone now have the RX RSSI/SNR for the received packet. RSSI is a negative number that increases in absolute value with increasing distance between TX/RX nodes.
SNR is a magic number sent by the Gods and you can figure out its relationship to distance.

- Range test should be enabled on all cave nodes as any cave node may have to send/receive range test packets. Range test must enabled and the sender delay must be set in order for the remote range test admin commands to work (set this via the CLI or app). Even if sender delay is non-zero, the sending action must be soft-enabled by an admin command as specified in the next bullet.

- Admin commands are supported for direct channel messages to a node. Admin commands are case insensitive (capitalization shown for emphasis only).  Admin commands are ignored if received on the general channel.
These admin commands are compatible with voice recognition in the messaging app. The first word of an admin
command was chosen to not be part of a normal status message.

  - `ADRT on`  -- turn on range test (default delay is 30 seconds)
  - `ADRT on hop`  -- turn on range test, and enable packet hopping
  - `ADRT off`  -- turn off range test.
  - `ADRT delay <15|30|60>`  -- set delay for between packets. Only 15, 30, or 60 is recognized.

- Logging messages to the serial port have been modified for easier parsing. Logging of all communication at Incident Command (IC) during a rescue is of critical importance. Our assumption is that the relay chain extends all the way to IC, with a laptop hooked to the surface node so that serial logging can be done.  The messages output to the serial port during operation were slightly modified so that they could be easily parsed afterwards, and incoming/outgoing messages with timestamps easily summarized. We use Microsoft Code + Serial Monitor plugin for serial monitoring. We used this methodology during testing and it worked well. There is a fix for logging of long messages in `HCRU 07/25.2` - a problem was discovered during the mock scenario held on August 3/2025 that messages longer than about 50 characters got truncated in the log. Fortunately, most of the messages during the mock were short, but it was still annoying to have lost some message content.

- Support for serial link via the RAK5802 RS485 module - see the detailed section below.

- Support for a buzzer haptic for RSSI - see the detailed section below.

- Support for a heartbeat LED (blinks every two seconds) - useful for locating nodes that have been placed in the cave. NOT SUPPORTED ON BRIDGE NODES (nodes with the RS485 interface).

The `firmware/variants/rak4631/platformio.ini` file (2.6 or less) contains different targets for these various capabilities. All targets contain the hop limit and admin command modifications.

1. `env:rak4631` - just contains hop limit/admin modifications
2. `env:rak4631_slink` - `env:rak4631` + enables serial link modifications
3. `env:rak4631_buzzer` - `env:rak4631` + enables buzzer modifications
4. `env:rak4631_cavenode` - `env:rak4631` + enables buzzer modifications + blinky heartbeat led
5. `env:rak4631_slink_hb` - `env:rak4631` + enables serial link modifications + blinky heartbeat led (DO NOT USE - SEE BELOW)

The above targets are based on the `may2025` (2.5 firmware) and `hopmod_2.6.11` (2.6 firmware) branches.

The `firmware/variants/rak4631/platformio.ini` file in the `hopmod_2.7.9` branch (2.7 firmware) has the following targets (in this branch, all Flamingo code changes are protected by a `#ifdef FLAMINGO`/`#endif` section).

1. `env:rak4631` - this target compiles to standard Meshtastic firmware
2. `env:rak4631_flamingo` - has `-D FLAMINGO` compile flag, just contains hop limit/admin modifications, suitable for a generic rak4631 device like a WisMesh Pocket
3. `env:rak4631_slink` - `env:rak4631_flamingo` + enables serial link modifications
4. `env:rak4631_buzzer` - `env:rak4631_flamingo` + enables buzzer modifications - assumes active buzzer.
5. `env:rak4631_cavegen2` - `env:rak4631_flamingo` + enables buzzer modifications + blinky heartbeat led, intended for our 2nd gen cave node


For targets that support the buzzer and heartbeat LED the pin usage can be changed via compile time defines.

The `tested_firmware` directory for pre-built firmware, in sub-directories labeled as `fw2_5`, `fw2_6`, and `fw2_7`.  Going forward, new features will be added to 2.7 firmware builds and will not be backported to 2.5/2.6.

On the Bridge Nodes, aka serial link nodes (RAK19007 Wisblock base board + RAK4631 module + RAK5802 RS485 module) we have discovered that IO1 and IO2 appear to be shorted to each other on the RAK5802 RS485 board.  According to the RAK5802 documentation, IO1 is a low-true signal used to disable the RS485 interface, so our code always keeps it in the high state (we never disable the RS485 interface). We tried using IO2 for the blink LED, but found that RS485 operation became erratic with blink enabled. We then discovered that IO2 was always high, the same state as IO1, and it is suspicious that IO1 and IO2 are directly across from each other on the RAK19007 I/O connector. The conclusion is that IO1 and IO2 are shorted, and that blinking IO2 periodically enables/disables the RS485 interface, causing erratic operation. Unfortunately, there is no other easily accessible general purpose IO pin for use as the blinky LED using the RAK19007 base board. So on our bridge node builds, we just tie the blink LED to IO2 and accept that it will always be on when power is applied (does not appear to affect power usage that much, only a 7% overnight drop on an 18650 battery). So, our serial link firmware builds do not include the blink module for this reason.

## Buzzer Haptic for RSSI

The buzzer modifications use an active buzzer to indicate different RSSI ranges when a range test packet is received. The ranges are:

1. One beep: RSSI greater than or equal to -90
2. Two beeps:  RSSI less than -90  greater than or equal to -110
3. Three beeps  RSSI less than -110.

The 2.7+ firmware builds have extended this to also use a running SNR (signal-to-noise ratio) average based on the last three packets - if the average SNR falls below 1.0, then three beeps is used regardless of RSSI. We have found SNR to be a good predictor packet loss. SNR tends to bounce around when moving so once beeps are sounded based on SNR, need to pause and wait for SNR to steady out to determine if SNR is unacceptable or not.

This buzzer is used during relay placement so that you don't have to keep your eyes on the screen to see RSSI values for range test packets. This does not use the RAK PWM buzzer settings in the phone app.  The buzzer is only installed on the radio that you want to use as a relay placement listener.

The buzzer we used was purchased from Amazon (search for Active Buzzer Module, 5V Piezoelectric Alarm, DIYables store) - it is a small 3-pin (Vcc/Gnd/IO) breadboard.  We have stuffed it successfully into a WisMesh Pocket radio, it just barely fits. It runs fine on 3.3V.  This particular active buzzer is an active low enable.

These modifications could easily be modified to support a passive buzzer.


## RS485 Serial link modification

The `slink` targets in the `platformio.ini` enable the serial link code. This code is meant for a RAK19007 Wisblock base board + RAK4631 module + RAK5802 RS485 module (installed in the IO slot of the Wisblock base board). This firmware modification sends/receives packets out the RS485 port in addition to the LORA link. This is intended to be used to hard link a pair of radios in a cave where wireless between the two radios is impractical.  The 
RAK5802 RS485 module uses the RXD1, TXD1 ports, so do not use this software with a board that has something connected to these ports, like the WisMesh Pocket radio that has a built-in GPS connected to this port. 

Our terminology for radio that has the RS485 interface is `bridge node`, as it allows bridging between the wireless/wired worlds.

Baud rate vs range testing yielded:

  - 115200 can drive 100 ft
  - 57600 can drive 700 ft
  - 19200 can drive 1400 ft
  - 9600 can drive 2400 ft 
  - 4800 can drive 4700 ft (1.4 km) 
  - 2400 can drive 5500 ft (1.6 km, do not know max distance,  suspect it is approximately 3 km - 9800 ft )

Any packet received over RS485 RX is echoed over LORA TX; a packet received over RS485 RX is never echoed back over RS485 TX. Any packet received over LORA RX that is rebroadcast by the router is also sent over RS485 TX.  Packet flow on the RS485 serial link is bidirectional.

Our procedure for testing if the hard link works between a pair of radios is as follows. This test assumes that the 
only two radios in range are the two hard linked radios that are being tested.
Connect two radios via the hard link, then bluetooth connect to each radio with the phone app, and in the Lora Config section, turn off 'Transmit enabled'.  Then send a direct message to whatever radio is not connected to via phone; if an ack is returned then the message went through the hard link to the destination.  Then, disconnect one of the wires in the hard link, and try sending again - this time the message send will fail with a max retry limit reached as the hard link is not connected.  Connect to each radio again via the phone app, and turn RF transmit back on.  Try sending the direct message again and this time it will succeed even with the hard link broken, as the message will go over RF.

To test RF RX (radio 1)> RS485 TX (radio 1) > RS485 RX (radio 2) > RF TX (radio 2) > RF RX (radio 3), just turn on a third radio in the room, connect your phone to the bridge node that has LORA TX disabled (radio 1), and target radio 3 with a direct message.  The packet will be sent by radio 1 over the wire to the bridge node with LORA TX enabled (radio 2), and which will then send the packet to radio 3 via RF -  you should receive an ACK back from this direct message.

The image below: ![Alt text](./img/bridge_nodes_1km.jpg?raw=true "Bridge nodes driving 1 km of wire") shows three bridge nodes @4800 baud and 1 km of wire (spools of 800/800/800/900 ft = 3300 ft). Two bridge nodes are the ends, and a third bridge nodes is spliced in the middle (like a field phone).  You could also place two more bridge nodes in this system, one each spool connection. The bridge nodes have their LORA TX disabled during testing, this forces packets over the wire.  This shows the power of the RS485 link - you can have as little or as much wire in the system vs wireless as you want.  These bridge nodes are packaged in temporary housing until our 3D printed enclosures are ready.  While this may look like a 'multi-hop wire' connection it is not - this just a multi-driver RS485 topology (which RS485 supports). Any packet sent by a bridge node over the wire arrives at all connected bridge nodes and counts as one hop. Just think of the wire as being 'air' if that helps.  There will be packet collision on the wire, just like there is packet collision over the air - there is no arbitration mechanism for who is allowed access to the wire. RS485 supports driver contention without damage to the drivers, the packets just get garbled and retries/random backoff are necessary to get packets through (just like via air TX).  It is assumed that cave rescuers will have individual radios with them, and if a rescuer is in range of a bridge node, packets from the rescuer will jump on the wire, and packets arriving at the bridge node will be sent over the air and arrive at the rescuer radio.

## RS485 Connection

RS485 is a two-wire differential bidirectional signaling protocol that can support multiple drivers, with driver contention (collision)
causing no damage to the drivers. For the RAK5802 RS485 module, if we call the two wires A and B, then A must be connected
to A and B must be connected to B.  This is because of how the RAK5802 is designed; it does not support cross-connected wires.  Traditional comm wire using field phones is connection agnostic, but that is not the
case with this system - reversing the connection A > B and B > A will cause a comm failure.  Because of this, we have marked the
ends of our comm wire with Red/Blue tape, and the connectors on the radio are Red/Black - so Red is connected to the Red terminal, and whatever color is not Red is connected to the black terminal. 

One strength of the traditional comm wire + field phones deployment is that the comm wire can be tapped into at any
point with a field phone.  That can still work with this system, but the problem is that typical comm wire uses black
for both wires, so there is no distinguishing A from B when tapping in.  The solution is to tap in using one polarity and send a direct message - if an ack is received, then the message succeeded and the polarity is correct. If no ack is received, reverse the direction and try again - it should succeed.  Having a reversed direction will cause no damage to
the RAK5802 RS485 module.

## RS485 Collision

Just like over-the-air packets, there can be a packet collision if both ends of the hard link attempt to send a packet
at the same time. RS485 supports multiple-driver connection, and driver contention causes no physical damage.
However, the packet will be garbled on reception - the firmware uses a 16-bit header and a 32-bit CRC wrapper around each Meshtastic packet
sent over the RS485 link, so a garbled packet is detected and discarded.  If we assume an average text message is about 50 chars or less (so packet size is about 100 bytes with header bytes), it will take about 0.05 seconds to transmit at 19200 bits/second.  This gives 20 TX slots in one second for a packet.  If we assume a packet every 15 seconds, this is 300 TX slots, giving a collision probability of less than 1%.  IF there is a collision, the packet is lost, but that is why there is
retransmit logic in the Meshtastic stack.

## Hop Limit Extension

The packet header was modified to provide 8-bit fields for both `hop_limit` and `hop_start`.  This means an upper limit of 255 hops, but our firmware has set the maxium limit to 31 hops as probably this is the maxinum number of radios any sane individual would want to bring into a cave (however, this is easily changed to a higher number up to 255 if desired)

The packet header was extended by four bytes (must be aligned on a four-byte boundary) with one byte each for `hop_limit` and `hop_start` and the other two bytes for a 16-bit magic number used to identify our packets. 

Modifying the packet header structure has the following ramifications:

1. Our radios can only talk with each other, they cannot talk to any radios using normal Meshtastic firmware.
2. A normal Meshtatic packet arriving at one of our radios is rejected upon receipt after header parsing because of a magic number mismatch. There is a 1/66536 chance (~ 0.002%) that the magic number will be correct, but the packet will be rejected after further parsing due to structure mismatch.
3. Our packet header is constructed such that the original `hop_limit` and `hop_start` fields will have values of 1 and 0, respectively, so this packet will not be forwarded after the header is parsed.  Unpacking this packet will fail due to fields mismatch and so will be rejected.

There were enough extra bytes in the original Meshtastic packet structure that the 200-byte payload limit was not affected by the packet header modification.

Setting the hop-limit greater than 7 must be done via the CLI as the phone apps all assume the max hop limit is 7.



## Using Range Test to set Cave Relay nodes

In the master Meshtastic firmware, range test packets have their packet hop_limit forced to zero when sent so that when they arrive at another node, they are not forwarded.
Our modifications allow range test packets to either be hopping or non-hopping (default).

There are two methodologies that can be used when setting out relay nodes in a cave, using hopping or non-hopping packets:

Using hopping packets (NOT PREFERRED, tends to clog the mesh): 

1. In this scenario, the surface node sends out all range test packets and uses hopping packets.

2. To place a relay node,  move away from the previous relay node (or surface node if this is the first relay) until range test packet arrival becomes unreliable, 
then move back into reliable range, place a new relay node, and move on. 

3. Arrival of a range test packet at the last relay node verifies end-to-end connectivity.

4. In our test of this, it seemed like the range test packets congested the network, and interfered with sending normal messages back to the surface node.

Using non-hopping packets (this has become our preferred method):

1. Use a direct admin message `ADRT on`  to the previous relay node (or surface node if this is the first relay) to enable range test sending.

2. Move away from the range test sending node until range test packet arrival become unreliable, 
then move back into reliable range, and place a new relay node. 

3. Use a direct admin message `ADRT off` to the sending node to turn off range test sending.

4. Send a message to the surface node and get an ack back to verify end-to-end connectivity.

5. Go back to step #1 where the current relay node becomes the previous relay node.


## A Note on V2.5 vs V2.6 firmware

We have ported our changes to Version 2.6 firmware even though it does not seem to have anything really needed for our cave radios, just to stay semi-current with Meshtastic (even though this is a fast moving target).  If you update a V2.5 radio to V2.6 firmware, be aware that this wipes settings, and things like longName/shortName and all other have to be reprogrammed.


## Router Algorithm/Network Congestion/Reliability

Here is my simple interpretation of the router algorithm -- for the case we are interested in, general broadcast packets, a node forwards packets that it has not seen before.  Each packet has a randomized packet number, and it keeps track of 'recently seen' packets.  If a packet arrives that the node has recently seen, then that packet is discarded.

In our linear chain case, each node will see two neighbors (behind/ahead). For a packet traveling from start to end, a node gets a packet from the `behind` neighbor. The node rebroadcasts it.  The `ahead` neighbor receives the packet, and rebroadcasts it. The `behind` neighbor receives this rebroadcast packet, but because it has been recently seen, the packet is discarded.  The hop limit value in our linear chain case has no effect on network congestion.  If packets only enter from either the start or end of the chain, then network congestion is only affected by how fast new packets are introduced into the chain.

End-to-end reliability will drop as the chain gets longer. It serves us best to be conservative in relay node placement - one or two weak links in the chain can kill end-to-end reliability. With 99% node reliability, a chain of 10 gives us 90% end-to-end reliability. We should be able to achieve 99% reliability with conservative node placement and given that nodes will retransmit if an acknowledgement is not received for a packet (MAX_RETRANSMIT is 5)

# Utility Software

The `utils` subdirectory has the following python scripts:

1. The `config.py` is a script for writing settings to a radio using the `meshtastic` CLI. It reads a YML file that contains the settings (see `cave_node.yml` for an example). It is critical that all radios be configured in the same way and this script streamlines the process. During script operation, the settings are read back from the radio after programming to verify that all settings were transferred correctly, and loops up to three times to complete the programming. We have noticed that a radio does not always get all of the setting on the first try (for unknown reasons) so the verification loop is necessary.  This script also writes an information file to the `infofiles` subdirectory so that a record of each radio that is programmed is saved.

2. The `gen_csv.py` is a utility that parses all of the files in the `infofiles` subdirectory and writes out a summary CSV file. The format of the CSV file is specified by a YML file, see the `node_csvspec.yml` file for an example. This gives you a handy summary of all the radios that have been programmed.

3. The `log_parse.py` file is a utility for parsing the radio serial log files to produce a summary of incoming/outgoing messages + timestamps.


# Testing

The following presentation [Huntsville Grotto Presentation/July 7, 2005/Jamie Moon](./doc/25-07-02_HSV_Grotto_Program_FLAMINGO_Cave_Radios.pdf) contains a lot more details on the two Tumbling Rock tests and Guffey Cave test that are described below.

## Tumbling Rock Cave Preserve / Alabama /US   April 4, 2025

First deployment of radios with our firmware that had the modified packet header to support higher hop limits.  Deployed approximately 10 wireless radios in the cave and verified that we had a hop count greater than 7.   Reached the `handprint` wall'. 

## Tumbling Rock Cave Preserve / Alabama /US   June 6, 2025

Goals:

- Repeat previous test that reached the handprint wall using only wireless radios and use the new range test tool that prints out RSSI values to check node placement, RSSI values – `Accomplished`.

- Replace stub antennas with new longer, higher gain antennas, record RSSI values. `Accomplished`, new antennas are better, by about 5-10% in some cases.

- Test different radio modes to determine if giving up some distance for faster signaling is worth it. `Accomplished`, it is worth it, less latency, did not affect the chain reliability. We are now using Medium/Slow as our default radio setting.

- Deploy one more or more hard-linked RS485 paired radios (bridge nodes) to test a mixed wired/wireless system and push deeper into the cave. `Accomplished`, deployed one hard linked radio pair using a comm spool (about 700 ft), then deployed the last wireless radio after that and reached past totem gallery. Total radio hops at this point were 11, there were 12 radios deployed.

After deploying the last radio, we still had two comm spools and a pair of bridge nodes, and could have pushed deeper, but it was about 20:30 at that point and everyone was burnt, so Jamie called it. Exited the cave at 21:30. The testing of the antennas and the radio modes took a long time as each radio had to be visited/handled to accomplish the task.

[Unedited Youtube Video](https://www.youtube.com/watch?v=4BVUCpGBc3U&ab_channel=Chris%27Corner) of the Tumbling Rock test.

## Guffey Cave / Alabama /US   June 27, 2025

Guffey Cave is the site of the all-day cave rescue scenario that is the capstone of Huntsville Cave Rescue Unit's four-day cave rescue class that is held each year in late July/early August.  We wanted to test deployment of the mesh in preparation for using it as an instructor channel during the scenario this year.

The goal was to reach `The Big Fall Room` which is about 1 km into the cave, and which generally students are able to reach with wired comms during the scenario.  We also wanted to test our new listener node that had an active buzzer installed that beeped based on RSSI value, useful during wireless node placement.

We exceeded the goal, we reached about 200m past the `The Big Fall Room` and to the crawl that leads to `Little India`. The total distance into the cave was about 1200m. 

 - Two wired segments were deployed (900 ft/275m from entrance to just before the pump room) and another wired segment (240m ft) that went through the breakdown leading to `Grand Central`.   There were wireless relay nodes between the two wired segments and after the second wired segment.  The wired segments were using 4800 baud as we thought that might have to connect all four spools together (1 km) but that proved unnecessary.  We could have used as high as 19200 baud since each bridge node was only driving one spool (~900 ft/275m).

 The team still had two comm spools (each 800 ft/240m) and a pair of bridge nodes when they reached the crawl to `Little India` but we were about out of time and had accomplished our goals.  The remaining time was spent replacing some of wired connection #2 with wireless nodes for experimentation purposes.

 Total deployed radios were 4 bridge (RS485/wireless) nodes, and about 12 wireless nodes.

 ## HCRU Cave Rescue Class Scenario/ Guffey Cave / Alabama /US   August 3, 2025 

For the Cave Rescue class scenario, we replicated the previous deployment. We also distributed radios (WisMesh Pockets) to several instructors that were in the cave. The total radio deployment was 20 - seven for instructors (and the IC radio) and the rest for the mesh (this includes the bridge nodes on the wired segments). One instructor had their own T-deck that was programmed with our firmware. The mesh performed flawlessly during the day-long exercise.  A total of 453 text messages was logged by IC (primary channel and DMs to IC) - this did not include DMs between instructors in the cave. The maximum hops logged was 11 - this was at the location of the two patients that were the most remote point of the scenario.

Since the two wired segments were relatively short, one about 300 feet and the other about 700 feet, the bridge nodes used 19200 baud.  LORA mode was Medium Slow for all radios.

The mesh proved its worth almost immediately when a mistake was made in the placement of two patients - this was discovered and fixed via text messages.  Throughout the day, dynamic adjustments were made to HCRU unit member placement in the cave via text message coordination over the mesh.

HCRU leadership was thrilled with the mesh performance and want to have more mesh usage in future events.

## HCRU/Chattanooga Cave Rescue/Jackson County Rescue Mock/ Tumbling Rock Cave / Alabama /US   Sept 27, 2025

HCRU hosted a joint mock scenario with Chattanooga Cave Rescue/TN, Jackson County Rescue, and two members from Blacksburg Va Rescue Squad on Sept 27/2025 at Tumbling Rock cave preserve. About 50 cavers were in attendance.  The initial teams entered at about 9:00 am and the patient exited at 5:00 pm.  The scenario had two patients (one ambulatory and one requiring a litter) who were located in a vertical section about one kilometer into the cave. A mesh was established in the cave, using approximately 23 cave radios, three different wired segments (900 ft/800 ft/ 800 ft) using six bridge nodes, and 10 other mesh radios for rescuers. 

The Good:

- Comms was established to the patient location (which was 100 ft above the floor in a vertical section)
- Wired bridges worked very well
- The blinky LED added to the 2nd Gen cave node worked well for finding placed nodes during retrieval

The Bad:

- I was not conservative enough in inital placement of the wireless nodes, leading to comms failure to IC once we were about 5 or 6 wireless nodes past the first wired link.  Our two Blacksburg members (Philip B and Jerin M) went back to identify weak spots, and then eventually called for more mesh nodes which we sent back with a third member (after we had laid the second wired link). See the discussion below for the root cause of this problem.

- The comms shared channel was chaotic - we need to use a different shared channel for comms status/link status back to IC with the shared channel for general rescuers.

- Rescuer radios need to be placed on client mute while the mesh is being deployed/debugged as if you are trying to debug a weak link then other Client radios can mess up your debugging (Philip B suggested this initially and I ignored him, and regretted it later). Once the mesh is established with solid comms then rescuers could change to CLIENT mode.

- Need to give radios meaningful names (change the long name) as they are being handed out to rescuers in ordered to avoid questions like "Who is HA28" on the comms channel during rescue. This is a protocol change, easy to implement.

Overall, leadership of the squads agreed that the mesh radio usage was a success. A backup plan was in-place to use wired+field phones if the mesh failed to perform, but fortunately was not needed.

Below is a photo of all of the radios used in the mock -
the orange capped nodes are the 2nd gen cave mesh nodes, the nodes to the far left are the 2nd gen bridge nodes, the clunky squarish nodes in the middle are the prototype bridge nodes and pile in the middle are rescuer radios (WisMesh pockets and a Tdeck). We used 6 of the 8 available bridge nodes and still had two bridge nodes and a 750 ft wire spool when we reached the patient. FYI, Chris Cargal and Becky Williams designed/made the 3D-printed enclosures for the 2nd gen bridge nodes, while Jamie Moon designed/made the 3D-printed enclosuers for the 2nd gen cave nodes.

![All mesh radios](./doc/all_radios_in_trock_mock_sep25.jpg)

This  [map of node locations/Chris Cargal](./doc/TR_mock_Nodes_20250927.pdf) was made by Chris Cargal.  Node locations were recorded by Chris as we picked up radios as the patient was being carried out. Blue lines are the wired segments, red dots are wireless nodes. One of the red nodes after the end of last wired segement is a rescuer radio 100 ft up from the cave floor at patient location. The lengths of the wired spools used for the wired segments were (WB02-WB01/900 ft, WB01-WB02/800 ft, WB10-WB07/800ft).  Wired bridges used a 9600 baudrate; this was chosen conservatively in case we wanted to connect two spools together.

Photos of the 2nd Gen cave node and bridge node are below.

![Cave node/2nd Gen](./doc/cavenode_2ndgen.jpg)

![Bridge node/2nd Gen](./doc/bridgenode_2ndgen.jpg)

### So why did the mesh used in the Tumbling Rock Mock have initial reliablity problems?

The reason that the cave node placement in the Tumbling Rock mesh looks somewhat haphazard, is because after initial
node placement, there was unreliable comms back to IC, which had to be fixed by going back and patching up weak links
by placing more nodes.

Some extensive testing after the mock revealed the root cause. In our past tests in Tumbling Rock, the 1st gen cave nodes (external antenna) and WisMesh Pockets (external antenna) had similar range, and we used a Pocket as the listener node for placing the cave nodes.

For the mock, we just did the same thing - used a Pocket as a listener node to check the RSSi value of the range test packets being used to place the 2nd gen cave nodes (internal antenna).  However, extensive testing after the mock has revealed that the 2nd Gen cave nodes have about 20% less range than the pockets, due to the internal antenna config.  Thus, cave nodes were being placed out of their reliable range (essentially we were using an apple to place oranges).  The 2nd gen cave nodes were ready just-in-time for the mock, and basic functionaly testing was done on them but not a lot of range testing.  It was just assumed that the 2nd gen cave node range would be the same as the 1st gen.

Anyway, lesson learned - always use the same type of radio to listen for range test packets as the radios being used to build the mesh!

Automated packet testing after the mock also showed the effect of SNR on packet loss - once SNR goes negative, it all over with - packet loss becomes unacceptable (RSSi can still be in the 'ok' range even if SNR is negative).  Currently the buzzer code only watches RSSi value but it is going to be modified to also be sensitive to SNR.


