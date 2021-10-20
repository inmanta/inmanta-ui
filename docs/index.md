# Inmanta Web Console

The Inmanta Web Console is a web GUI for the Inmanta Service Orchestrator.

## Browser support

For using the web console, the last 2 versions of the Chrome, Firefox, Edge and Safari browsers are supported.  
For security reasons it's always recommended to use the latest version of these browsers.

## Proxy

When configuring a proxy for the web-console, the url should always end in `/console`.  
The web-console uses the `/console` part as an `anchor`.  
The application page urls will be stitched onto the right side of the anchor.  
Whatever is to the left of the anchor is considered to be the proxy.  
So from an application perspective, the url is constructed as:  
(`proxy`) + (`anchor`) + (`application defined urls`)

### Examples

Given the input url, the application will use the following `proxy` + `anchor`.

| Scenario              | input url                   | `proxy` + `anchor` |
| --------------------- | --------------------------- | ------------------ |
| Empty proxy respected | /console/resources?env=abcd | /console           |
| Proxy respected       | /someproxy/console          | /someproxy/console |
| Faulty url ignored    | /someproxy                  | /console           |
