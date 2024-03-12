from pprint import pprint


def parse_packets(lines, direction='>'):
    packets = []  # To hold all the parsed packets

    prev_char = None

    # Define start marker for a new packet
    start_markers = ['0x68', '0x01']

    # Iterate over each line
    current_packet = []  # To hold the current packet being constructed
    for line in lines:
        if not line.startswith(direction):
            continue
        data = line[1:].strip()

        if data == start_markers[1] and prev_char and prev_char == start_markers[0] and len(current_packet) == 0:
            current_packet = start_markers.copy()
        elif len(current_packet) > 0:
            current_packet.append(data)

        prev_char = data

        if len(current_packet) > 0 and current_packet[-1] == '0x16':
            packets.append(current_packet.copy())
            current_packet = []

    return packets

def dedup(inarray):
    outarray = []
    prev = None
    for pkt in inarray:
        if pkt != prev:
            outarray.append(pkt)
            prev = pkt
    return outarray

if __name__ == "__main__":
    with open('bidi_dump_final_down_70', 'r') as file:
        lines = file.readlines()

    pkts_in = parse_packets(lines, direction='<')
    pkts_out = parse_packets(lines, direction='>')

    print("Packets in: ", len(pkts_in))
    pprint(dedup(pkts_in))

    print("Packets out: ", len(pkts_out))
    pprint(dedup(pkts_out))



