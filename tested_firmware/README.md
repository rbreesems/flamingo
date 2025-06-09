
## For sharing with other Cave Meshers

This directory contains the firmware file be shared with other Cave Meshers.  All other files can be found on the repo at https://github.com/rbreesems/flamingo .

- `rak4631-firmware-hopmod-2-5-06-2025-1.uf2` - the compiled version of the modified firmware for Meshtastic 2.5 version firmware `Stable (Beta)` based on the `may2025` branch in the  Reese github repo at: https://github.com/rbreesems/firmware.  Updated June 2025.

- `rak4631-firmware-2-5-06-2025-slink-19200.uf2` - the compiled version of the modified firmware for Meshtastic 2.5 version firmware `Stable (Beta)` based on the `slink` branch in the Reese github repo at: https://github.com/rbreesems/firmware .  This code has everything the `may2025` branch has plus the RS485 serial link is enabled.  See the discussion below on the RS485 serial link modification. Updated June 2025. Uses 19200 baud.

- `rak4631-firmware-2-5-06-2025-slink-9600.uf2` - Same as other `slink` firmware but uses 9600 baud.



## Firmware Modifications

The firmware repo is in the Reese github repo at: https://github.com/rbreesems/firmware

The may2025 branch (based on Meshtastic 2.5.20) is the latest branch has the following changes.

- Packet header has been changed to support a hop limit up to 255, but firmware has it limited to 31.
See the section on hop limit modification for a discussion of this change. The most important ramification is that radios
with this firmware can only talk to radios with the same firmware.

- LCD splash screen displays HCRU firmware version name.

- Range test has been modified to support non-hopping/hopping range test packets.  Default is non-hopping.

- Range test messages sent to phone now have the RX RSSI/SNR for the received packet. RSSI is a negative number that increases in absolute value with increasing distance between TX/RX nodes.
SNR is a magic number sent by the Gods and you can figure out its relationship to distance.

- Range test should be enabled on all cave nodes. It is not necessary to set sender delay, it is automatically set to 30 seconds, but the sending is soft disabled.  The sending action must be soft-enabled by an
admin command as specified in the next bullet. Range test still needs to be enabled in the settings. Also, if GPS is disabled the range test module is still operational.

- Admin commands are supported on any direct channel message to a node. Admin commands are case insensitive (capitialization shown for empahsis only).  Admin commands are ignored if received on the general channel.
These admin commands are compatible with voice recognition in the messaging app.

  - `ADRT on`  -- turn on range test (default delay is 30 seconds)
  - `ADRT on hop`  -- turn on range test, and enable packet hopping
  - `ADRT off`  -- turn off range test.
  - `ADRT delay <15|30|60>`  -- set delay for between packets. Only 15, 30, or 60 is recognized.


## RS485 Serial link modification

This firmware (based on the `slink` branch in the firmware repo) is meant for a RAK19007 Wisblock base board + RAK4631 module + RAK5802 RS485 module (installed in the IO slot of the Wisblock base board). This firmware modification sends/receives packets out the RS485 port in addition to the LORA link. This is intended to be used to hard link a pair of radios in a cave where wireless between the two radios is impractical.  The 
RAK5802 RS485 module uses the RXD1, TXD1 ports, so do not use this software with a board that has something connected to these ports, like the WisMesh Pocket radio that has a built-in GPS connected to this port. 

Baud rate vs range testing yielded:

  - 115200 can drive 100 ft
  - 57600 can drive 700 ft
  - 19200 can drive 1400 ft
  - 9600 can drive 2000 ft 
 
 Any packet receieved over RS485 RX is echoed over LORA TX; a packet received over RS485 RX is never echoed back over RS485 TX.

## Hop Limit Modification


Because we want to build a long chain of nodes in a cave that can pass along a message, it seems that increasing the hop limit from the current maximum 7 to something larger is needed.  The Meshtastic devs constantly warn that a hop limit > 3 becomes unreliable due to mesh saturation. Howeever, it is unclear that this will happen in a cave if a node in a chain can only reach two neigbors - ahead and behind. It may be that increasing the hop limit is a naive approach and that testing will show that is unworkable, but least it should be tried.

A packet header has two fields: hop_start and hop_limit.  The hop_start is the hop_limit for when the packet is initially
sent, and the initial hop_limit is set to the hop_limit set on the radio. Each time the packet is rebroadcast, the hop_limit
is decremented. The different between hop_limit and hop_start at any point is the number of hops the packet has traveled.
When hop_limit reaches 0, then the packet is no longer broadcast.

In the unaltered Meshtastic code, the hop_limit, hop_start each was packed into 3-bit field in a single 'flags' byte in the
16-byte  header (the other two bits in the flags byte was used for two other flags).

In the modified Meshtastic code, four bytes were added to the header, a byte for hop_limit, a byte for hop_start, and a two
byte 'magicnumber' field that is used to detect headers from received packets that are from unmodified radios.  The header
had to be increased by four bytes because it has to align to a four byte boundary. However, there is plenty of space in
the 256 bytes of the packet such that the 200-byte limit that is on messages sent from a phone is not affected. The original
flags byte was kept, with old hop_limit set to 0, hop_start field set to 1 (this combination will ensure our packets do not get forwarded if one arrives at a stock firmware radio).

Even though the hop_limit could now be set as high as 255, the code limits it to 32 as that would be a practical upper
bound on the number of devices a sane person would want to drag into a cave.  A hop_limit > 7 must be set via the Pyton CLI
as the phone apps limit this setting to a maximum of 7.

If we call a radio that has the new firmware a 'cave radio', and one with unaltered firmware a 'normal radio', then:

- Cave radio to cave radio comms work as expected.
- A normal radio packet arriving at a cave radio will be immediately discarded upon detecting a magic number mismatch.
There is a 1 in 65536 chance that a normal packet may have the correct magic number in its packet bytes, but it will still 
get discarded later by the router when it cannot decode the packet.
- A cave radio packet arriving at a normal radio will have a hop_limit of 0/  hop start of 1 in the original flag byte, so it will not be forwarded.

## Using Range Test to set Cave Relay nodes

In the master Meshtastic firmware, range test packets have their packet hop_limit forced to zero when sent so that when they arrive at another node, they are not forwarded.
Our modifications allow range test packets to either be hopping or non-hopping (default).

There are two methodologies that can be used when setting out relay nodes in a cave, using hopping or non-hopping packets:

Using hopping packets: 

1. In this scenario, the surface node sends out all range test packets and uses hopping packets.

2. To place a relay node,  move away from the previous relay node (or surface node if this is the first relay) until range test packet arrival become unreliable, 
then move back into reliable range, place a new relay node, and move on. 

3. Arrival of a range test packet at the last relay node verifies end-to-end connectivity.

4. In our test of this, it seemed like the range test packets congested the network, and intefered with sending normal messages back to the surface node.

Using non-hopping packets:

1. Use a direct admin message `ADRT on`  to the previous relay node (or surface node if this is the first relay) to enable range test sending.

2. Move away from the range test sending node until range test packet arrival become unreliable, 
then move back into reliable range, and place a new relay node. 

3. Use a direct admin message `ADRT off` to the sending node to turn off range test sending.

4. Send a message to the surface node and get an ack back to verify end-to-end connectivity.

5. Go back to step #1 where the current relay node becomes the previous relay node.



## A Note on V2.5 vs V2.6 firmware

Version 2.6 firmware does not seem to have anything really needed for our cave radios, but if personal radios are being switched back and forth between stock firmware and our firmware, our cave radios all needed to be on Version 2.6.  This is because moving between V2.5 and V2.6 wipes settings, and things like longName/shortName have to be reprogrammed.

## Router Algorithm/Network Congestion/Reliability

Here is my simple interpretation of the router algorithm -- for the case we are interested in, general broadcast packets, a node forwards packets that it has not seen before.  Each packet has a randomized packet number, and it keeps track of 'recently seen' packets.  If a packet arrives that the node has recently seen, that packet is discarded.

In our linear chain case, each node will see two neighbors (behind/ahead). For a packet traveling from start to end, a node gets a packet from the `behind` neighbor. The node rebroadcasts it.  The `ahead` neighbor receives the packet, and rebroadcasts it. The `behind` neighbor receives this rebroadcast packet, but because it has been recently seen, the packet is discarded.  The hop limit value in our linear chain case has no effect on network congestion.  If packets only enter from either the start or end of the chain, then network congestion is only affected by how fast new packets are introduced into the chain.

End-to-end reliability will drop as the chain gets longer. It serves us best to be conservative in relay node placement - one or two weak links in the chain can kill end-to-end reliability. With 99% node reliability, a chain of 10 gives us 90% end-to-end reliabilty. We should be able to achieve 99% reliability with conservative node placement and given that nodes will retransmit if an acknowledgement is not received for a packet (MAX_RETRANSMIT is 5)



