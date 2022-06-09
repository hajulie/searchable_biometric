import pyoram, os
from pyoram.oblivious_storage.tree.path_oram import \
    PathORAM
from Crypto.Util.Padding import pad, unpad

#under the condition that oram_block_size is a multiple of _block_size 

_block_count = 10
_block_size = 8
oram_block_size = 8
_storage_name = "heap.bin"

data=[b'', b'\xd0\xcbU\xc9\xa5\xaa\xeeH\x87', b'\r\x00\xe3\xa7\x8b\xeb\xee+', b'\xa5\xf7\xa6\xaa-\xc4\x92/\xc7\x99']

def put_oram(data): #UNFINISHED AND DOES NOT WORK 
    #calculate top level size 
    # size_root = len(pickle.dumps(self.tree.get_node(self.root).data))
    # oram_block_size = 8
    # oram_block_size = size_root + (_block_size - (size_root % _block_size))

    ###HELPER FUNCTIONS#
    #padding
    def oram_padding(item): 
        if len(item) >= _block_size:
            #takes the last block of the existing string, and pads it 
            last_block = len(item)%_block_size
            front, end = item[:-last_block], item[-last_block:]
            if len(end) == _block_size: 
                with_pad = end
            else:
                with_pad = pad(end, _block_size)
            temp = front + with_pad 

        else: 
            temp = pad(item, _block_size)

        #pads the rest of the block meant for oram with 00s
        temp_block = b'\x00' * _block_size
        # if len(temp) < oram_block_size: 
        blocks_to_add = (oram_block_size - len(temp))/_block_size
        assert blocks_to_add - int(blocks_to_add) == 0
        new = temp + (temp_block * int(blocks_to_add))
        # else: 
        #     _mod = len(temp) % oram_block_size
        #     if _mod != 0: 
        #         new = temp + (temp_block * int(_mod/oram_block_size))

        return new
    ###

    if os.path.exists(_storage_name):
        os.remove(_storage_name)

    f = PathORAM.setup(_storage_name, block_size= oram_block_size, block_count=_block_count, storage_type='file')
    f.close()
    
    # with PathORAM(storage_name, f.stash, f.position_map, key=f.key, storage_type='file') as f: 
    #     for i in range(self.root, self.branching_factor**self.depth): #go through nodes 
    #         serial = pickle.dumps(self.tree.get_node(i).data)
    #         num_blocks = len(serial) // oram_block_size
    #         temp_blocks = []
    #         for i in range(num_blocks): 
    #             block, serial = serial[:oram_block_size], serial[oram_block_size:]
    #             temp_blocks.append(block)
    #         padded = oram_padding(serial)
    #         temp_blocks.append(padded)

    #         for i in temp_blocks: 
    #             f.write_block(0, i)
    
    #     print(f.position_map)
    #     print(f.read_block(0))

    map = {val : [] for val in data}
    f = PathORAM(_storage_name, f.stash, f.position_map, key=f.key, storage_type='file')

    # with PathORAM(_storage_name, f.stash, f.position_map, key=f.key, storage_type='file') as f: 
    add_to = 0 
    # print("map:", map)
    for i in data:
        serial = i
        temp_blocks = []
        num_blocks = len(serial) // oram_block_size
        for k in range(num_blocks): 
            block, serial = serial[:oram_block_size], serial[oram_block_size:]
            temp_blocks.append(block)
        padded = oram_padding(serial)
        temp_blocks.append(padded)
        # print("temp_blocks:", temp_blocks)

        for j in range(len(temp_blocks)): 
            # print("added:", temp_blocks[j], " | length:", len(temp_blocks[j]))
            f.write_block(add_to, temp_blocks[j])
            map[i].append(add_to)
            add_to += 1
    
        # pos_map = f.position_map
        # print(pos_map)
        # print("dict map:", map)
        # for i in range(_block_count):
        #     print("i: %i, str: %r"%(i, f.read_block(i)))
        # for i in range(_block_count):
        #     print("i: %i, str: %r"%(i, f.read_block(i)))
    return f, map

def retrieve_data(value, oram, map): #make map and oram into objects! 
    raw_data = []
    if value not in map: 
        print("Value does not exist") #this would be replaced with mask probably? 
    else: 
        in_map = map[value]
        for pos in in_map: 
            raw_data.append(oram.read_block(pos))

        new_split = [] 
        for v in raw_data: 
            v = bytes(v)
            for i in range(0, oram_block_size//_block_size): 
                front, v = v[:_block_size], v[_block_size:]
                if front != b'\x00' * _block_size: 
                    new_split += [front]

        new_split[-1] = unpad(new_split[-1], _block_size)
        orig = b''.join(new_split)

    return orig


f, map = put_oram(data)

for i in data:
    print(retrieve_data(i, f, map))