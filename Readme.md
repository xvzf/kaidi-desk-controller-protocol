# Kaidi KDDY041 KD1869A standing desk controller protocoll analysis
> Foundation work for home-assistant integration

It seems to be a simple protocol, with a start byte, a checksum, and an end byte. The checksum is the sum of the bytes between the start and end bytes.
It's no request/response, both controller and base board are firing messages at each other (like, as fast as 9600 baud can go).

## Interface

:warning: both supply logic and communication logic are ~4.5-5V on my unit. It is not safe to connect this to a 3.3V logic level device like an ESP32 and will kill it.
For this analysis, I've used a Raspberry Pi Pico, which can tolerate up to 5V for logic level inputs and has been fine.
Nevertheless, a logic level shifter is recommended for use with 3.3V devices.

Controller and display are connected via an RJ45 cable, where 4 pins are used for power and UART communication. The pinout remains to be determined, I've soldered directly to the controller board for this analysis.
The UART interface has a baudrate of 9600, 8 data bits, no parity, and 1 stop bit.

![Pinout](./img/2.png?raw=true "Controller board pinout")

## Packet Structure

```
0x68 0x01 0x__ 0x__ 0x__ 0x__ 0xdf 0x16
^^^^^ ^^^                 ^^^ ^^^^^^^^^^
start  |                   |   end byte
byte   |                   |
       |                checksum (sum?)
 seemingly static
```


### display -> controller messages

2nd payload byte seems to be the command, 0x01 is up, 0x02 is down, 0x03 is idle.

**Idle**:
```
0x68 0x01 0x03 0x00 0x00 0x04 0x16
```
**Moving up**:
```
0x68 0x01 0x01 0x00 0x00 0x02 0x16
```
**Moving down**:
```
0x68 0x01 0x02 0x00 0x00 0x03 0x16
```

### controller -> display messages

There seems to be just one packet containing the expansion height, and the controller responds with a series of packets, each with a 16bit number, incrementing by one for every 0.1cm.

Logic of a height offset seems to be on the display side, as the controller just sends the extension height.
Same as for the "height savings" feature, the feature is on the display side, as the display sends up/down commands to the controller until the saved height/offset is reached.

```
0x68 0x01 0x00 0x00 0x28 0x29 0x16
               ^^^^^^^^^
             16bit  number
```


## Packet captures display -> controller

### Idle, moving down, idle

```
[['0x68', '0x01', '0x03', '0x00', '0x00', '0x04', '0x16'],
 ['0x68', '0x01', '0x02', '0x00', '0x00', '0x03', '0x16'],
 ['0x68', '0x01', '0x03', '0x00', '0x00', '0x04', '0x16']]
```

### Idle, moving up, idle
```
[['0x68', '0x01', '0x03', '0x00', '0x00', '0x04', '0x16'],
 ['0x68', '0x01', '0x01', '0x00', '0x00', '0x02', '0x16'],
 ['0x68', '0x01', '0x03', '0x00', '0x00', '0x04', '0x16']]
```

## Packet captures controller -> display

### Moving up from 64 to 128 and back down to 68 (cm?)
```
[['0x68', '0x01', '0x00', '0x00', '0x00', '0x01', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x0A', '0x0B', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x14', '0x15', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x1E', '0x1F', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x28', '0x29', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x32', '0x33', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x3C', '0x3D', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x46', '0x47', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x50', '0x51', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x5A', '0x5B', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x64', '0x65', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x6E', '0x6F', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x78', '0x79', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x82', '0x83', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x8C', '0x8D', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x96', '0x97', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xA0', '0xA1', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xAA', '0xAB', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xB4', '0xB5', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xBE', '0xBF', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xC8', '0xC9', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xD2', '0xD3', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xDC', '0xDD', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xE6', '0xE7', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xF0', '0xF1', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xFA', '0xFB', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x04', '0x06', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x0E', '0x10', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x18', '0x1A', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x22', '0x24', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x2C', '0x2E', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x36', '0x38', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x40', '0x42', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x4A', '0x4C', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x54', '0x56', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x5E', '0x60', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x68', '0x6A', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x72', '0x74', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x7C', '0x7E', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x86', '0x88', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x90', '0x92', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x9A', '0x9C', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xA4', '0xA6', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xAE', '0xB0', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xB8', '0xBA', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xC2', '0xC4', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xCC', '0xCE', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xD6', '0xD8', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xCC', '0xCE', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xD6', '0xD8', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xE0', '0xE2', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xEA', '0xEC', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xF4', '0xF6', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xFE', '0x00', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x08', '0x0B', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x12', '0x15', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x1C', '0x1F', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x26', '0x29', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x30', '0x33', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x3A', '0x3D', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x44', '0x47', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x4E', '0x51', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x58', '0x5B', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x62', '0x65', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x6C', '0x6F', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x76', '0x79', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x80', '0x83', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x8A', '0x8D', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x80', '0x83', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x76', '0x79', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x6C', '0x6F', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x62', '0x65', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x58', '0x5B', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x4E', '0x51', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x44', '0x47', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x3A', '0x3D', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x30', '0x33', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x26', '0x29', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x1C', '0x1F', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x12', '0x15', '0x16'],
 ['0x68', '0x01', '0x00', '0x02', '0x08', '0x0B', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xFE', '0x00', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xF4', '0xF6', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xEA', '0xEC', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xE0', '0xE2', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xD6', '0xD8', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xCC', '0xCE', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xC2', '0xC4', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xB8', '0xBA', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xAE', '0xB0', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0xA4', '0xA6', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x9A', '0x9C', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x90', '0x92', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x86', '0x88', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x7C', '0x7E', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x72', '0x74', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x68', '0x6A', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x5E', '0x60', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x54', '0x56', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x4A', '0x4C', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x40', '0x42', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x36', '0x38', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x2C', '0x2E', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x22', '0x24', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x18', '0x1A', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x0E', '0x10', '0x16'],
 ['0x68', '0x01', '0x00', '0x01', '0x04', '0x06', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xFA', '0xFB', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xF0', '0xF1', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xE6', '0xE7', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xDC', '0xDD', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xD2', '0xD3', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xC8', '0xC9', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xBE', '0xBF', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xB4', '0xB5', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xAA', '0xAB', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0xA0', '0xA1', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x96', '0x97', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x8C', '0x8D', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x82', '0x83', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x78', '0x79', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x6E', '0x6F', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x64', '0x65', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x5A', '0x5B', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x50', '0x51', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x46', '0x47', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x3C', '0x3D', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x32', '0x33', '0x16'],
 ['0x68', '0x01', '0x00', '0x00', '0x28', '0x29', '0x16']]
```
