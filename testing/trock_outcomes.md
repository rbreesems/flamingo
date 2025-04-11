
## My Thoughts on TRock 4/4/2025 Test

1. Verified firmware hop extension mod, new firmware worked as expected, got 8 hops with 10 radios.

2. Serial logging at surface node worked ok, but needs improvement.

3. Range test definitely clogged normal message sending. Once RT was disabled, message comms worked much better, even at max hop limit at handprint wall.

### What needs to improve

1. Optimizing radio placement distance takes too long.  Need to have *lots* of radios and put them down within easy LOS of each other and go for placement speed. How many radios do need? Maybe up to 20 radios in-cave (10 per case, two cases). This ia a money issue, not a technical issue.

2. Need better remote control of surface node Range test from in-cave target node. Need to implement some parseable command that can be used to turn range test off on, something as simple as: "adminrt off", "adminrt on" -- if a message starts with 'adminrt', then it is an admin command to turn RT off/on.  This should also not require a radio reboot as this requires serial logging to be turned back on, which may be missed.

3. Serial logging needs to improve to account for Direct messages, as current logging misses surface node outgoing messages if they are in a DM channel.

4. Need to figure out why Range Test is clogging up comms.  My working theory is that too many packets are being kept on the 'recently seen' packet list, and that nodes are spending too much CPU effort looking at the recently seen packet list and dealing with RT packets instead of message comm packets.  Will look more closely at the firmware and do some experimentation.


### What does the next test need to try?

1. Different antennas

2. We could try short/turbo mode instead of long/fast mode.  We are never going to have 'long' range in a cave so might as well blast out the packets as fast as possible.  This could also decrease the channel clogging by RT if packets are sent faster.

3. MORE RADIOS  MORE RADIOS MORE RADIOS - the goal would be to push further into TRock with more radios.

