
## Pre-built firmware for rak4631

All firmware is built from the `may2025` branch in firmware repo.

Version display: `HCRU 07/25.0`

1. rak4631-firmware-2-5-07-2025-0.u2 - has hop modifications, remote commands

2. rak4631-firmware-2-5-07-2025-0-slink - #1 + serial RS485 link - set the baud rate via the CLI

3. rak4631-firmware-2-5-07-2025-0-active-buzzer-io3-range-test-rssi.uf2 - #1 + buzzer, built for Wismesh Pocket

Version display: `HCRU 07/25.1`
Added Alert Bell emoji receive as toggle for ADRT on/off - allows remote range test to be toggled on/off via emoji. Same rak4631 versions as above except filename has 07-2025-1.

Version display: `HCRU 07/25.2`
Fixed logging of long messages (problem discovered durng August 3/2025 mock scenario). Only have firmware for base nodes, serial link and buzzer nodes do not need this fix.

## Pre-built firmware for T-deck

The ZIP archive with `t-deck` in the filename has firmware for the T-deck. Download, unzip, and read the `README` in that directory for more instructions. Currently, the T-deck support is limited to only the packet header changes so that a T-deck can send/receive messages on the HCRU mesh.
















