from versions import Versions

class Encoder:
    def __init__(self):
        self.version = Versions()
        self.alphanum= set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./():')
        self.mode_indicator = {
            "NUMERIC": "0001",
            "ALPHANUMERIC": "0010",
            "BYTE": "0100",
            "KANJI": "1000"
        }
        self.alphanumeric_values = {
        "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
        "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17, "I": 18,
        "J": 19, "K": 20, "L": 21, "M": 22, "N": 23, "O": 24, "P": 25, "Q": 26, "R": 27,
        "S": 28, "T": 29, "U": 30, "V": 31, "W": 32, "X": 33, "Y": 34, "Z": 35, " ": 36,
        "$": 37, "%": 38, "*": 39, "+": 40, "-": 41, ".": 42, "/": 43, ":": 44
        }
        #0-й индекс: общее количество кодовых слов
        #1-й индекс: кодовые слова с исправлением ошибок в каждом блоке
        #2-й индекс: количество блоков 1-го типа
        #3-й индекс: количество блоков 2-го типа
        #4-й индекс: кодовые слова данных для блока 1-го типа
        #5-й индекс: кодовые слова данных для блока 2-го типа
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
    def determine_encoding(self, text:str):
        return 'NUMERIC' if text.isnumeric() else 'ALPHANUMERIC' if all(char in self.alphanum for char in text) else "BYTE" if self.is_iso(text) else 'BYTE'
    
    def is_iso(self, text:str):
        try:
            text.encode('latin-1')
            return True
        except UnicodeError:
            return False
        
    def encode(self, text):
        encoding = self.determine_encoding(text)
        mode_indicator = self.mode_indicator[encoding]
        char_count_indicator, version = self.get_char_count_indicator(text)
        encoded_data = mode_indicator + char_count_indicator + self.__get_encoded_data__(encoding, text)

    def get_char_count_indicator(self, text):
        encoding_mode = self.determine_encoding(text)
        version = self.version.smallest_version(text, self.determine_encoding(text))
        bits = None
        if encoding_mode == 'NUMERIC':
            if version <=9:
                bits = 10
            elif 10 <= version <= 26:
                bits = 12
            elif 27 <= version <= 40:
                bits = 14
        elif encoding_mode== "ALPHANUMERIC":
            if version <= 9:
                bits= 9
            elif 10 <= version <= 26:
                bits= 11
            elif 27 <= version <= 40:
                bits= 13
        elif encoding_mode== "BYTE":
            if version <= 9:
                bits= 8
            else:
                bits= 16 
        return format(len(text), f'0{bits}b'), version
    def __get_encoded_data__(self, encoding, text):
        if encoding== "NUMERIC": return self.numeric_encoding(text)
        elif encoding== "ALPHANUMERIC": return self.alphanumeric_encoding(text)
        elif encoding== "BYTE": return self.byte_encoding(text)
    def numeric_encoding(self, text):
        list = []
        result = []
        i = 0
        while i < len(text):
            t = text[i:i+3]
            i += 3
            list.append(t)
        for group in list:
            binary = bin(int(group))[2:]
            result.append(binary)
        return ''.join(result)
    def alphanumeric_encoding(self, text):
        list= []
        i= 0
        result= ""
        while i < (len(text)):
            t= text[i:i+2]
            i+= 2
            list.append(t)
        for group in list:
            if len(group)== 2:
                c1= group[0]
                c2= group[1]
                sum= (self.alphanumeric_values[c1] * 45) + self.alphanumeric_values[c2]
                b= format(sum, '011b')
            else:
                c = group[0]
                sum = self.alphanumeric_values[c]
                b = format(sum, '06b')
            result += b
        return result
    def byte_encoding(self, text):
        try:
            byte_encoded= text.encode('iso-8859-1')
        except UnicodeError:
            byte_encoded= text.encode('utf-8')

        binary_str= ""
        for byte in byte_encoded:
            binary_str += format(byte, '08b')
        return binary_str