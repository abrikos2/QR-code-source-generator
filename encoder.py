from version import Version

class Encoder:
    def __init__(self):
        self.version = Version()
        #1: количество слов
        #2: количество блоков 
        #3: количество блоков 1-го типа
        #4: количество блоков 2-го типа
        #5: шаг деления 1-го типа
        #6: шаг деления 2-го типа   
        self.block_info= {
        1: [16, 10, 1, 0, 16, 0], 
        2: [28, 16, 1, 0, 28, 0], 
        3: [44, 26, 1, 0, 44, 0], 
        4: [64, 18, 2, 0, 32, 0], 
        5: [86, 24, 2, 0, 43, 0],
        6: [108, 16, 4, 0, 27, 0], 
        7: [124, 18, 4, 0, 31, 0], 
        8: [154, 22, 2, 2, 38, 39], 
        9: [182, 22, 3, 2, 36, 37], 
        10: [216, 22, 4, 1, 43, 44],
        11: [254, 30, 1, 4, 50, 51], 
        12: [290, 22, 6, 2, 36, 37], 
        13: [334, 22, 8, 1, 37, 38],
        14: [365, 24, 4, 5, 40, 41], 
        15: [415, 24, 5, 5, 41, 42],
        16: [453, 28, 7, 3, 45, 46], 
        17: [507, 28, 10, 1, 46, 47], 
        18: [563, 26, 9, 4, 43, 44], 
        19: [627, 26, 3, 11, 44, 45], 
        20: [669, 26, 3, 13, 41, 42],
        21: [714, 26, 17, 0, 42, 0], 
        22: [782, 28, 17, 0, 46, 0], 
        23: [860, 28, 4, 5, 121, 122], 
        24: [914, 2, 6, 14, 45, 46], 
        25: [1000, 28, 8, 13, 47, 48],
        26: [1062, 28, 19, 4, 46, 47], 
        27: [1128, 28, 22, 3, 45, 46], 
        28: [1193, 28, 3, 23, 45, 46], 
        29: [1267, 28, 21, 7, 45, 46], 
        30: [1373, 28, 19, 10, 47, 48],
        31: [1455, 28, 2, 29, 46, 47], 
        32: [1541, 28, 10, 23, 46, 47], 
        33: [1631, 28, 14, 21, 46, 47], 
        34: [1725, 28, 14, 23, 46, 47], 
        35: [1812, 28, 12, 26, 47, 48],
        36: [1914, 28, 6, 34, 47, 48], 
        37: [1992, 28, 29, 14, 46, 47], 
        38: [2102, 28, 13, 32, 46, 47], 
        39: [2216,  28, 40, 7, 47, 48], 
        40: [2334, 28, 18, 31, 47, 48]
        }
    
    def encode(self, text):
        chat_count_indicator, version = self.get_char_count_indicator(text)
        encoded_data = '0100' + f'{chat_count_indicator}' + self.get_encoded_data(text)
        padding_1 = self.terminator_padding(version, encoded_data)
        padding_2 = self.pad_8(padding_1)
        return self.add_236_17(padding_2, version)

    def get_char_count_indicator(self, text):
        version = self.version.get_version_info(text)
        return format(len(text), f'0{8 if version <= 9 else 16}b'), version
    
    def terminator_padding(self, version, encoded_data):
        remaining_bits = self.block_info[version][0] * 8 - len(encoded_data)
        if remaining_bits >=4:
            encoded_data+= '0000'
        else:
            encoded_data+= '0'* remaining_bits
        return encoded_data
    
    def pad_8(self, encoded_data):
        while len(encoded_data) % 8 != 0:
            encoded_data+= '0'
        return encoded_data

    def add_236_17(self, encoded_data, version):
        total_bits = self.block_info[version][0] * 8
        flag = True
        while len(encoded_data) < total_bits:
            if flag:
                encoded_data += '11101100'
            else:
                encoded_data+= '00010001'
            flag = not flag
        return encoded_data

    def get_encoded_data(self, text: str):
        try:
            encoded = text.encode('iso-8859-1')
        except UnicodeError:
            encoded = text.encode('utf-8')
        binary_str = ''
        for byte in encoded:
            binary_str += format(byte, '08b')
        return binary_str