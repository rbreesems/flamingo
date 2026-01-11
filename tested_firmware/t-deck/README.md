
## The T-Deck and HCRU firmware changes

This zip archive contains files for programming the T-deck with the HCRU firmware.

This firmware is based on 2.6.11. Currently the firmware only has the packet header changes that allows for a higher hop count, it has no other changes.  As such, a T-deck could serve as a personal device for a rescuer to send/receive messages on the HCRU mesh, but not as a listener node for node placement as it does not have RSSI display/buzzer changes.

The important files in this ZIP archive are:

1. `device-update.bat` - bat script for updating the firmware
2. `firmware-t-deck-2.6.11-update.bin` - firmware file to use with `device-update.bat`

Any other files can be ignored.

These instructions assume that you have a Python environment installed that has the meshtastic and esptool packages installed, and 
that you can open a command window that has these environment available.

### Steps to update a new T-deck:

#### Programming Mode
Anytime that the T-Deck is to be programmed with a new .bin file, either via the Web Flasher or via a BAT script, it must first be
put into programming mode:

1. Turn the T-Deck off.
2. Press the trackball button, turn the device back on, and hold the trackball button for 5 seconds.
3. Upon release of the button the screen should be blank. At this point you can proceed with programming.
4. To further verify if the device is in programming mode, connect a USB cable, open a command window and execute `esptool chip-id` - information about the T-deck CPU should be returned (older versions of the `esptool` package may require `esptool chip_id`).

#### To update T-Deck firmware:

1. If the T-Deck has the old GUI, use the Meshtastic Web Flasher to update it to 2.6.11, and after programming the T-Deck should display the new GUI. Note that to put the T-Deck into programming mode for the Web Flasher, turn it off, press the trackball down, turn it back on, and hold the trackball button for 5 seconds. Upon release the screen should be blank. At this point you can proceed with the Web Flasher.
2. Open a command window  and update the T-Deck with the settings found in the `utils/tdeck-2.6.yml` file (`python config.py tdeck-2-6.yml --set` )
4. Put the T-Deck in programming mode and connect a USB cable.
5. Open a command window, verify that the T-Deck responds to the `esptool chip-id` command.
6. Change to the directory that has the files in the archive, and execute `device-update.bat -f firmware-t-deck-2.6.11-update.bin`.
7. Power-cycle the T-Deck, the welcome screen should display `HCRU xxxxx`  (where XXXXX is the HCRU version).

The radio should now be able to communicate with other HCRU radios that has either 2.5 or 2.6 firmware with the packet header changes.
