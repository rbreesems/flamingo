#!/usr/bin/env bash
set -euo pipefail

# If you get rak4630s with the other variety of bootloader, this will update that, and the soft device. 
# When it completes, you still need to update the firmware. 
# 
# The utilities you need are found by following this link : 
# Follow directions at https://docs.rakwireless.com/product-categories/wisblock/rak4631-r/dfu/#converting-rak4631-r-to-rak4631
# 
# Windows-focused Bash script (Git Bash / MSYS2) to:
# 1) Find the COM port whose device name contains "nRF52"
# 2) Flash bootloader via ./nrfutil.exe on that port
# 3) Detect the newly appeared COM port
# 4) Flash softdevice via adafruit-nrfutil on the new COM port
#
# Optional: send an AT command before DFU (disabled by default).
# Enable with:
#   SEND_AT_BOOT=1 bash ./rak4631_factory_dfu.sh [START_PORT] [SOFTDEVICE_PORT]
# Tuning knobs:
#   AT_PORT=COM62          (defaults to START_PORT)
#   AT_BAUD=9600           (defaults to 9600)
#   AT_CMD=AT+BOOT         (defaults to AT+BOOT)
#   AT_METHOD=auto|powershell|python   (defaults to auto)
#
# If the device replies with "AT_COMMAND_NOT_FOUND", the script will fail.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

NRFUTIL_EXE="./nrfutil.exe"
BOOTLOADER_PKG="rak4631_factory_bootloader.zip"
SOFTDEVICE_PKG="rak4631_factory_softdevice.zip"
AT_BAUD_DEFAULT="9600"
AT_CMD_DEFAULT="AT+BOOT"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

require_file() {
  local p="$1"
  [[ -f "$p" ]] || die "Missing file: $p"
}

require_cmd() {
  local c="$1"
  command -v "$c" >/dev/null 2>&1 || die "Missing command in PATH: $c"
}

# Output lines: COM7|Some Device Name (COM7)
list_com_ports() {
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "\
    \$ErrorActionPreference='Stop'; \
    Get-CimInstance Win32_PnPEntity | \
      Where-Object { \$_.Name -match '\(COM\d+\)' } | \
      ForEach-Object { \
        \$name = \$_.Name; \
        if (\$name -match '\((COM\d+)\)') { \
          \$port = \$matches[1]; \
          Write-Output (\"\$port|\$name\"); \
        } \
      }"
}

find_nrf52_port() {
  local ports
  ports="$(list_com_ports || true)"
  [[ -n "${ports//[[:space:]]/}" ]] || die "No COM ports found."

  local match
  match="$(echo "$ports" | grep -i 'nrf52' | head -n 1 || true)"
  [[ -n "$match" ]] || {
    echo "Available COM ports:" >&2
    echo "$ports" >&2
    die "Could not find a COM port whose name contains 'nRF52'."
  }

  echo "$match" | cut -d'|' -f1
}

can_python_serial() {
  command -v python >/dev/null 2>&1 || return 1
  python -c "import serial" >/dev/null 2>&1
}

send_at_powershell() {
  local port="$1"
  local baud="$2"
  local cmd="$3"

  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "\
    \$ErrorActionPreference='Stop'; \
    \$port='${port}'; \
    \$baud=${baud}; \
    \$cmd='${cmd}'; \
    \$sp = New-Object System.IO.Ports.SerialPort -ArgumentList @(\$port,\$baud,'None',8,'One'); \
    \$sp.Encoding = [System.Text.Encoding]::ASCII; \
    \$sp.Handshake = [System.IO.Ports.Handshake]::None; \
    \$sp.ReadTimeout = 200; \
    \$sp.WriteTimeout = 500; \
    \$sp.DtrEnable = \$true; \
    \$sp.RtsEnable = \$true; \
    \$resp = ''; \
    try { \
      \$sp.Open(); \
      Start-Sleep -Milliseconds 100; \
      \$sp.DiscardInBuffer(); \
      \$sp.DiscardOutBuffer(); \
      # Explicit CRLF EOL. \
      \$sp.Write(\$cmd + [char]13 + [char]10); \
      \$sp.BaseStream.Flush(); \
      # Read any response for ~1.2s (device might reply quickly or reboot). \
      \$deadline = (Get-Date).AddMilliseconds(1200); \
      while ((Get-Date) -lt \$deadline) { \
        try { \$resp += \$sp.ReadExisting() } catch { } \
        Start-Sleep -Milliseconds 50; \
      } \
    } finally { \
      if (\$sp -and \$sp.IsOpen) { \$sp.Close() } \
      if (\$sp) { \$sp.Dispose() } \
    } \
    if (\$resp -match 'AT_COMMAND_NOT_FOUND') { \
      Write-Output \$resp; \
      exit 3; \
    } \
    Write-Output \$resp"
}

send_at_python() {
  local port="$1"
  local baud="$2"
  local cmd="$3"

  python - "$port" "$baud" "$cmd" <<'PY'
import sys, time
try:
    import serial  # pyserial
except Exception as e:
    print(f"pyserial not available: {e}", file=sys.stderr)
    sys.exit(2)

port = sys.argv[1]
baud = int(sys.argv[2])
cmd = sys.argv[3]

resp = b""
try:
    with serial.Serial(port=port, baudrate=baud, bytesize=8, parity="N", stopbits=1, timeout=0.2, write_timeout=0.5) as s:
        try:
            s.reset_input_buffer()
            s.reset_output_buffer()
        except Exception:
            pass
        s.write((cmd + "\r\n").encode("ascii", errors="ignore"))
        s.flush()
        deadline = time.time() + 1.2
        while time.time() < deadline:
            chunk = s.read(4096)
            if chunk:
                resp += chunk
            time.sleep(0.05)
except Exception as e:
    # On Windows, if the device reboots/disconnects immediately after receiving AT+BOOT,
    # pyserial may throw a noisy "ClearCommError failed (... The device does not recognize the command.)".
    # This is typically harmless for our use-case; treat it as "no response" and continue.
    msg = str(e)
    if "ClearCommError failed" in msg or "The device does not recognize the command" in msg:
        pass
    else:
        print(f"serial error: {e}", file=sys.stderr)
        sys.exit(1)

text = resp.decode("ascii", errors="ignore")
if "AT_COMMAND_NOT_FOUND" in text:
    print(text)
    sys.exit(3)
print(text)
PY
}

send_at() {
  local port="$1"
  local baud="$2"
  local cmd="$3"
  local method="${AT_METHOD:-auto}"

  if [[ "$method" == "powershell" ]]; then
    send_at_powershell "$port" "$baud" "$cmd"
    return 0
  fi

  if [[ "$method" == "python" ]]; then
    can_python_serial || die "AT_METHOD=python requested, but pyserial is not available."
    send_at_python "$port" "$baud" "$cmd"
    return 0
  fi

  # auto: try PowerShell first, then python if available
  local out=""
  if out="$(send_at_powershell "$port" "$baud" "$cmd" 2>/dev/null)"; then
    echo "$out"
    return 0
  fi

  if can_python_serial; then
    send_at_python "$port" "$baud" "$cmd"
    return 0
  fi

  die "Failed to send AT command (PowerShell failed; pyserial not available for fallback)."
}

ports_only_sorted_unique() {
  list_com_ports | cut -d'|' -f1 | sort -u
}

pick_new_port_by_diff() {
  local old_ports_sorted_unique="$1"
  local new_ports_sorted_unique="$2"

  # Return ports in new that were not in old.
  local out=()
  while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    if ! echo "$old_ports_sorted_unique" | grep -qx "$p"; then
      out+=("$p")
    fi
  done <<<"$new_ports_sorted_unique"

  if [[ "${#out[@]}" -eq 1 ]]; then
    echo "${out[0]}"
    return 0
  fi

  if [[ "${#out[@]}" -gt 1 ]]; then
    # Heuristic: prefer a port whose description looks DFU/bootloader-ish.
    local all_now
    all_now="$(list_com_ports)"
    local p
    for p in "${out[@]}"; do
      # Match the exact port at line-start, then look for DFU-ish descriptors.
      if echo "$all_now" | grep -iE "^${p}\\|" | grep -iE '(dfu|boot|bootloader|adafruit|nrf)' >/dev/null 2>&1; then
        echo "$p"
        return 0
      fi
    done
    # Otherwise pick the first and continue.
    echo "${out[0]}"
    return 0
  fi

  # No diff detected.
  echo ""
}

main() {
  require_cmd powershell.exe
  require_file "$NRFUTIL_EXE"
  require_file "$BOOTLOADER_PKG"
  require_file "$SOFTDEVICE_PKG"
  require_cmd adafruit-nrfutil

  echo "Enumerating COM ports (baseline)..."
  local baseline_ports
  baseline_ports="$(ports_only_sorted_unique || true)"
  echo "$baseline_ports" | sed '/^$/d' | awk '{print "  - " $0}'

  echo "Finding nRF52 COM port..."
  local nrf_port
  if [[ "${1:-}" =~ ^COM[0-9]+$ ]]; then
    nrf_port="$1"
  else
    nrf_port="$(find_nrf52_port)"
  fi
  echo "Using nRF52 port: $nrf_port"

  if [[ "${SEND_AT_BOOT:-0}" == "1" ]]; then
    local at_port at_baud at_cmd at_resp
    at_port="${AT_PORT:-$nrf_port}"
    at_baud="${AT_BAUD:-$AT_BAUD_DEFAULT}"
    at_cmd="${AT_CMD:-$AT_CMD_DEFAULT}"
    echo "Sending AT command on $at_port @ ${at_baud}: $at_cmd"
    at_resp="$(send_at "$at_port" "$at_baud" "$at_cmd" || true)"
    if [[ -n "${at_resp//[[:space:]]/}" ]]; then
      echo "AT response:"
      echo "$at_resp" | sed 's/^/  /'
    else
      echo "AT response: (none)"
    fi
    echo "Waiting 5 seconds..."
    sleep 5
  fi

  echo "Flashing bootloader with nrfutil on $nrf_port..."
  "$NRFUTIL_EXE" dfu serial -pkg "$BOOTLOADER_PKG" -p "$nrf_port"
  echo "Waiting 5 seconds..."
  sleep 5

  echo "Enumerating COM ports (after bootloader DFU)..."
  local after_ports
  after_ports="$(ports_only_sorted_unique || true)"
  echo "$after_ports" | sed '/^$/d' | awk '{print "  - " $0}'

  echo "Detecting new COM port..."
  local new_port
  if [[ "${2:-}" =~ ^COM[0-9]+$ ]]; then
    new_port="$2"
  else
    new_port="$(pick_new_port_by_diff "$baseline_ports" "$after_ports")"
  fi

  if [[ -z "$new_port" ]]; then
    echo "No newly appeared COM port detected; falling back to 'any port that is not $nrf_port'." >&2
    new_port="$(echo "$after_ports" | grep -v -x "$nrf_port" | head -n 1 || true)"
  fi
  [[ -n "$new_port" ]] || die "Could not determine the new COM port for softdevice DFU."

  echo "Using softdevice DFU port: $new_port"
  echo "Flashing softdevice with adafruit-nrfutil on $new_port..."
  adafruit-nrfutil --verbose dfu serial --package "$SOFTDEVICE_PKG" -p "$new_port"

  echo "Done."
}

main "$@"

