#!/usr/bin/env bash
# capturar-mac.sh — Captura Y DESCIFRA el protocolo AC/AV (wss://:9010) en un comando.
#
# La clave del descifrado: el handshake TLS TIENE que quedar dentro de la captura.
# Por eso este script CAPTURA PRIMERO y recién después abre el navegador — así la
# conexión nueva (con su handshake) queda grabada y el keylog la puede descifrar.
#
# Uso:  tools/capturar-mac.sh            (banca en https://localhost/)
#       tools/capturar-mac.sh https://alpespay-lab.com/
set -e
URL="${1:-https://localhost/}"
KEYLOG="$HOME/alpes_keys.log"
PCAP="/tmp/alpes_captura.pcap"
PROFILE="/tmp/alpes-chrome"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TSHARK="$(command -v tshark || echo /Applications/Wireshark.app/Contents/MacOS/tshark)"

: > "$KEYLOG"; rm -f "$PCAP"

# Configurar Wireshark para descifrar automáticamente (por si abres la GUI en vivo)
WS_PREFS="$HOME/.config/wireshark/preferences"; mkdir -p "$(dirname "$WS_PREFS")"
python3 - "$WS_PREFS" "$KEYLOG" <<'PY'
import sys
prefs, keylog = sys.argv[1], sys.argv[2]
try: lines = open(prefs).read().splitlines()
except FileNotFoundError: lines = []
lines = [l for l in lines if not l.strip().startswith("tls.keylog_file:")]
lines.append(f"tls.keylog_file: {keylog}")
open(prefs, "w").write("\n".join(lines) + "\n")
PY

echo "──────────────────────────────────────────────────────────────"
echo " 1) Capturando el puerto 9010 en lo0  →  $PCAP"
echo " 2) Se abrirá Chrome (perfil desechable, cert aceptado, claves TLS)"
echo " 3) USA LA BANCA (login, saldo, enviar…). Cuando termines: Ctrl+C aquí."
echo " 4) Se abrirá la captura YA DESCIFRADA en Wireshark (filtro websocket)."
echo "──────────────────────────────────────────────────────────────"

# 1) Capturar PRIMERO (el handshake queda dentro)
"$TSHARK" -i lo0 -f "tcp port 9010" -w "$PCAP" -q >/dev/null 2>&1 &
TS=$!
sleep 2

# 2) Abrir el navegador (conexión NUEVA -> handshake capturado)
if [ -x "$CHROME" ]; then
  SSLKEYLOGFILE="$KEYLOG" "$CHROME" --user-data-dir="$PROFILE" \
    --ignore-certificate-errors --test-type --new-window "$URL" >/dev/null 2>&1 &
else
  echo " (No encontré Chrome; abre tu navegador con SSLKEYLOGFILE=$KEYLOG y ve a $URL)"
fi

# 3) Esperar hasta Ctrl+C
trap 'kill $TS 2>/dev/null' INT
wait $TS 2>/dev/null || true

# 4) Abrir descifrado en Wireshark
echo; echo "Abriendo la captura descifrada en Wireshark…"
open -a Wireshark "$PCAP"
