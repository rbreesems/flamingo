
## Pre-built firmware for rak4631

All 2.5 firmware is built from the `may2025` branch, 2.6 firmware from the `hopmod_2.6.11` branch, in firmware repo.

Version display: `HCRU 07/25.1` in `fw2_5`, `fw2_6` directories. 

1. rak4631-firmware-2-5-07-2025-1.u2 - has hop modifications, remote commands
2. rak4631-firmware-2-5-07-2025-1-slink - #1 + serial RS485 link - set the baud rate via the CLI
3. rak4631-firmware-2-5-07-2025-1-active-buzzer-io3-range-test-rssi.uf2 - #1 + buzzer, built for Wismesh Pocket


Version display: `HCRU 07/25.2`
Fixed logging of long messages (problem discovered during August 3/2025 mock scenario). Only have firmware for base nodes, serial link and buzzer nodes do not need this fix.

Version display: `HCRU 09/25.1` -- all changes ported to 2.6.11 Meshtastic, found in `fw_6` directory. Base filename is `rak4631-firmware-2-6-09-2025-1`, `slink`, `active-buzzer` variations are provided. Note that when updating your 2.5 firmware to 2.6, all settings are lost and have to be reprogrammed (this is because of the 2.6 version update, not our changes)

Version display: `FLAMINGO 11.25`, firmware based on 2.7.9 Meshtastic, in `fw2_7` directory

This software has the updated SNR moving average display for range test packets.

1. `rak4631-firmware-wismesh-pocket.uf2`  - has hop modifications, remote commands
2. `rak4631-firmware-wismesh-pocket-active-buzzer-io3.uf2`  - #1 + buzzer, built for Wismesh Pocket
3. `rak4631-firmware-bridgenode.uf2` - #1 + serial RS485 link - set the baud rate via the CLI
4. `rak4631-firmware-cavegen2-active-buzzer-io2-blink-led-io1.uf2` - has buzzer, blink module - built for our 2nd generation cave nodes.
5. `rak4631-firmware-wismeshtag.uf2` - has hop modifications, remote commands (WisMesh tag device)


## Pre-built firmware for T-deck (fw2_6 directory)

The ZIP archive with `t-deck` in the filename has firmware for the T-deck. Download, unzip, and read the `README` in that directory for more instructions. Currently, the T-deck support is limited to only the packet header changes so that a T-deck can send/receive messages on the HCRU mesh.
















