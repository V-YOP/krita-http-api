# Krita HTTP API

Expose Krita API by a HTTP Server, which relies on python standard module `http.server`. for simplicity, it's a **single-thread** HTTP server, which will read request body and respond a json.

# Usage

1. Download this repo as ZIP and Open Krita, import it via menu 'Tools/Scripts/Import Python Plugin from File'.
2. restart Krita, and you will see a float message "API Server Launched, port: 8080"
3. `curl -X POST -d '{"delay": 200}' http://localhost:1976`

# Documentation

TODO Not implemented

# Call Flow

If you'd like to imporve or modify this, check this sequence diagram explaining the handling process of an HTTP Request.

![](./sequence_diagram.png)