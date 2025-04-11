## Building Meshtastic Firmware

Follow this guide: https://meshtastic.org/docs/development/firmware/build/  

This uses VS Code + Platform IO plugin to build the firmware.

I built it using my Windows 11 box.

When you build the firmware, you have to select a target.  For my WisMesh Pocket V2 radio
which has internals of RAK4630 WisDuo module + RAK19026 WisMesh Baseboard there seemed to
be two solutions that matched (both use the wiscore_rak4631 board)

- rak4631 - this is the one that I used and should work for our Wiscore boards.
- rak4631_eth_gw -  this seems some sort of special purpose build that excludes a lot of stuff

After the build is completed, the uf2 file will be: firmware/.pio/build/rak4631/firmware.uf2

I did test this and it worked on my devices.  One curious thing is that the firmware file
built this way is about 80% of the size of the firmware file downloaded using the Web flasher.
I am not sure what the difference is.  Both of the firmware files (home built and web flasher)
had the same starting address of 0x26000 but home built only had 2521 blocks while the web flasher 
version had 3015 blocks.

WARNING: If you are on a Windows box, and your home directory has space in it, ie. `C:\Users\Bob Reese\`,
then the firmware build will fail at the 'Generating UF2 file' step for the rak4631 platforms, which is the very last step.
To fix this, edit the file `firmware/bin/platformio-customio.py` and change the line:

```
env.VerboseAction(f"{sys.executable} ./bin/uf2conv.py $BUILD_DIR/firmware.hex -c -f 0xADA52840 -o $BUILD_DIR/firmware.uf2",
                                        "Generating UF2 file"))
```

to be (notice the escaped double quotes around the `{sys.executable}`):
```
env.VerboseAction(f"\"{sys.executable}\" ./bin/uf2conv.py $BUILD_DIR/firmware.hex -c -f 0xADA52840 -o $BUILD_DIR/firmware.uf2",
                                        "Generating UF2 file"))
```



# Building the custom cave node firmware

The Githup repo with the custom firmware is here: https://github.com/rbreesems/firmware

Use branch hopmod_2.5 for a build based on firmware 2.5.20.  You can download a ZIP archive of the this code, when you unzip it the directory will be named `firmware-hopmod-2.5`.  By default, the build files will placed in the `.pio` directory under this directory. If you want the build files, somewhere else, say `C:\platformio` then set the environment variable `PLATFORMIO_WORKSPACE_DIR` to this directory.

## Flashing Meshtastic Firmware

### With the Web Flasher
I used the web flasher: https://flasher.meshtastic.org/

I picked device : RAK WisBlock 4631

I downloaded the lastest beta firmware UF2 file.

When you plug in your device via USB, a serial port should show up, can be viewed in Windows Device Manager.
On Windows, will show up under Ports (Com & LPT) > US Serial Device (COMxx)

This serial port needs to be active in order for the Web Flasher to work.

On the flash portion of the Web Flasher, have two symbols:

- Flash button - this will flash just the firmware

- Trashcan button (Erase flash) - some web wisdom says to do this first before flashing the firmware on a new device.

Both methods use the DFU mode, which makes your device look like a mounted file folder.
In DFU mode, a file folder window will open, and then you drag the .uf2 firmware file to the folder and drop it.

IMPORTANT - once you drag and drop - WAIT - a little progress bar may or may not appear indicating
flashing progress, but once finished, the folder window will close. Wait for it to close before 
doing anything else.

The Erase Flash  method has you download a `nf2_erase2.uf2` file that you drag and drop to 
erase the flash.  It also has an extra step over the normal flash that says to open the serial 
port to complete the erase process.

### With the CLI

Assuming you have installed the `meshtastic` program for the CLI, you can do `meshtastic --enter-dfu` and this will open an explorer window like the Web Flasher does, and you can drag over the `uf2` file.


