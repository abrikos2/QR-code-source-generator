from encoder import Encoder
from version import Version
from bitarray import bitarray

class ErrorCorrection:
    def __init__(self):
        self.encoder = Encoder()
        self.version = Version
        self.gf_exp= [0] * 512 
        self.gf_log= [0] * 256
        self.init_galois_field()
        self.requred_bits= {
        1: 0, 2: 7, 3: 7, 4: 7, 5: 7,
        6: 7, 7: 0, 8: 0, 9: 0, 10: 0,
        11: 0, 12: 0, 13: 0, 14: 3, 15: 3,
        16: 3, 17: 3, 18: 3, 19: 3, 20: 3,
        21: 4, 22: 4, 23: 4, 24: 4, 25: 4,
        26: 4, 27: 4, 28: 3, 29: 3, 30: 3,
        31: 3, 32: 3, 33: 3, 34: 3, 35: 0,
        36: 0, 37: 0, 38: 0, 39: 0, 40: 0
        }

    def init_galois_field(self):
        primitve_polynomial= 0x11d 
        x= 1
        for i in range(0, 255):
            self.gf_exp[i]= x
            self.gf_log[x]= i
            x <<= 1
            if(x & 0x100):
                x ^= primitve_polynomial
        for i in range(255, 512):
            self.gf_exp[i]= self.gf_exp[i-255]
    
    def generate_poly(self, version):
        num_condewords = self.encoder.block_info[version][1]
        x = [1]
        for i in range(num_condewords):
            x = self.multiply_poly(x, [1, self.gf_exp[i]])
        return x
    
    def gf_multiply(self, x,y):
        if x== 0 or y== 0: return 0
        return self.gf_exp[self.gf_log[x] + self.gf_log[y] % 255]

    def multiply_poly(self, x, y):
        result = [0] * (len(x) + len(y) -1)
        for i in range(len(x)):
            for j in range(len(y)):
                result[i+j] ^= self.gf_multiply(x[i], y[j])
        return result
    
    def message_poly(self, text):
        encoded = self.encoder.encode(text)
        i = 0
        list = []
        while i < len(encoded):
            x = encoded[i:i+8]
            i+=8
            list.append(int(x,2))
        return list
    
    def split_into_blocks(self, message, version):
        block_info = self.encoder.block_info[version]
        num_blocks1 = block_info[2]
        num_blocks2 = block_info[3]
        data_codewords1 = block_info[4]
        data_codewords2 = block_info[5]
        blocks = []
        start = 0
        for i in range(num_blocks1):
            end = start + data_codewords1
            blocks.append(message[start:end])
            start = end
        for i in range(num_blocks2):
            end = start + data_codewords2
            blocks.append(message[start:end])
            start = end
        return blocks

    def div(self, message_poly, generator_poly):
        remainder = message_poly + [0] * (len(generator_poly) - 1) 
        for i in range(len(message_poly)):
            if remainder[i] != 0:
                factor = self.gf_log[remainder[i]]
                for j in range(1, len(generator_poly)):
                    if generator_poly[j] != 0:
                        remainder[i + j] ^= self.gf_exp[(factor + self.gf_log[generator_poly[j]]) % 255]
        return remainder[-(len(generator_poly) - 1):]

    def interleave_blocks(self, data_blocks, ec_blocks):
        interleaved = []
        max_length = max(len(block) for block in data_blocks)
        for i in range(max_length):
            for block in data_blocks:
                if i < len(block):
                    interleaved.append(block[i])
        max_ec_length = len(ec_blocks[0])
        for i in range(max_ec_length):
            for block in ec_blocks:
                interleaved.append(block[i])    
        return interleaved
    
    def get_final_message(self, message, version):
        str= ""
        for num in message:
            str += format(num, '08b')
        remainder_bits_to_add= self.requred_bits[version]
        for i in range(0, remainder_bits_to_add):
            str += '0'
        return bitarray(str)

    def generate_error_correction(self, text, version):
        generate_poly = self.generate_poly(version)
        message_poly = self.message_poly(text)
        message_blocks = self.split_into_blocks(message_poly, version)
        errorcorrection_blocks = []
        for block in message_blocks:
            errorcorrection_block = self.div(block, generate_poly)
            errorcorrection_blocks.append(errorcorrection_block) 
        message = self.interleave_blocks(message_blocks, errorcorrection_blocks)
        return self.get_final_message(message, version)