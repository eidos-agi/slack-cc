#!/usr/bin/env bash
# print.sh — Send a PDF to the office printer
#
# Usage:
#   ./tools/print.sh path/to/file.pdf
#   ./tools/print.sh path/to/file.pdf 10.0.231.27    # custom IP
#
# Printer: "Executive" — 25th Floor Copier (Ricoh)
# Protocol: Raw print over TCP port 9100

set -euo pipefail

FILE="${1:?Usage: print.sh <file.pdf> [printer-ip]}"
PRINTER_IP="${2:-10.0.231.27}"
PORT=9100

if [[ ! -f "$FILE" ]]; then
    echo "Error: $FILE not found" >&2
    exit 1
fi

SIZE=$(wc -c < "$FILE")
echo "Printing: $FILE ($SIZE bytes)"
echo "Printer:  $PRINTER_IP:$PORT (Executive — 25th Floor)"

python3 -c "
import socket, sys
with open('$FILE', 'rb') as f:
    data = f.read()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('$PRINTER_IP', $PORT))
s.sendall(data)
s.close()
print(f'Sent {len(data)} bytes — check the printer')
"
