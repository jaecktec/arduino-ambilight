# arduino-ambilight

contents:  
pythonapp: script that computes the colors for the ambilight and sends the values over UDP/protobuf to an arduino  
arduino: FastLED based arduino app that lisetns on UDP port 1234 and waits for UDP/protobuf RGB values that get applied to the led strip  
protobuf: contains a docker image with needed config to compile protobuf files (optional)  

How does the ambilight work:

1) python script takes a screenshot every 10 seconds  
2) resizes the image to 31*21 (amount of LEDs I have behind my screen) 
3) collects the borders and assigns it to an array 
4) sends led values encoded with protobuf to Arduino
5) arduino listens on UDP for protobuf encoded messages, 
6) on message, applies colors to lightstrip


