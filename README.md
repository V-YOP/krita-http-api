# Krita HTTP API

Expose Krita API by a HTTP Server, which relies on python standard module `http.server`. it's a multi-threaded BIO HTTP server, which will read request body and respond a json.

# Usage

1. Download this repo as ZIP and Open Krita, import it via menu 'Tools/Scripts/Import Python Plugin from File' and make sure plugin 'HTTP API' is enabled.
2. restart Krita, **open a document**
3. execute `curl -d '{"code": "floating-message", "param": {"message": "Hello, World!"} }' localhost:1976`

If you need add more API, just add more "controller"s in `./controllers`. both sync style and async style(like express.js) API is provided.

# limitation

1. Sometimes it will timeout rather than throws exception when route code not found.
2. Server will reject further connections when there's already several (8 i guess) connections, it's responsible for the client to limit max connections.
3. 

# Documentation

TODO API Documentation

# Call Flow

If you'd like to imporve or modify this, check this sequence diagram explaining the handling process of an HTTP Request.

![](./sequence_diagram.png)
