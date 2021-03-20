# SimplePound v1.0

This is a simple tool which can be used to stress-test your server, or any other
task where you need to run a lot of simultaneous instances of the same script, 
this can be done like so:
 
./SimplePound.py "wget http://192.0.2.1 -O /dev/null" --thread 64

![screenshot of SimplePound in action](https://github.com/Mikjaer/SimplePound/blob/master/screenshot.png)

Once the tool is running you can in- and decrease the number of workers with the 
[+] and [-] keys, you can pause and resume with [P] and [R] and finally you kan 
zero the min and max counters with [Z]

The verb pound means to hit or beat repeatedly with a lot of force, or to crush 
something by hitting it repeatedly which is exactly what this tool was designed 
to do.

Commercial support available from https://www.mikjaer-consulting.dk/

Copyright 2021 Mikkel Mikjaer Christensen, released under GNU GPL v2.0

