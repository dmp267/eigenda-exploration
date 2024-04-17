# helper functions for guaranteeing the validity of the data to be dispersed to EigenDA
# converted from go example at https://docs.eigenlayer.xyz/eigenda/rollup-guides/blob-encoding
BYTES_PER_SYMBOL = 32


def convert_by_padding_empty_byte(data):
    """
    Convert data by padding an empty byte at the front of every 31 bytes.
    This ensures every 32 bytes are within the valid range of a field element for bn254 curve.
    """
    parse_size = BYTES_PER_SYMBOL - 1
    data_size = len(data)
    data_len = (data_size + parse_size - 1) // parse_size
    
    valid_data = bytearray(data_len * BYTES_PER_SYMBOL)
    valid_end = len(valid_data)
    
    for i in range(data_len):
        start = i * parse_size
        end = (i + 1) * parse_size
        if end > data_size:
            end = data_size
            valid_end = end - start + 1 + i * BYTES_PER_SYMBOL
        
        # With big endian, setting the first byte to 0 ensures data is within the valid range
        valid_data[i * BYTES_PER_SYMBOL] = 0
        valid_data[i * BYTES_PER_SYMBOL + 1: (i + 1) * BYTES_PER_SYMBOL] = data[start:end]
    
    return bytes(valid_data[:valid_end])


def remove_empty_byte_from_padded_bytes(data):
    """
    Remove the first byte from every 32 bytes, reversing the change made by convert_by_padding_empty_byte.
    """
    parse_size = BYTES_PER_SYMBOL
    data_size = len(data)
    data_len = (data_size + parse_size - 1) // parse_size
    
    put_size = BYTES_PER_SYMBOL - 1
    valid_data = bytearray(data_len * put_size)
    valid_len = len(valid_data)
    
    for i in range(data_len):
        start = i * parse_size + 1
        end = (i + 1) * parse_size
        if end > data_size:
            end = data_size
            valid_len = end - start + i * put_size
        
        valid_data[i * put_size: (i + 1) * put_size] = data[start:end]
    
    return bytes(valid_data[:valid_len])