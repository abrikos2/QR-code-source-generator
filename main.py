import numpy as np
import pprint
from PIL import Image
import tables
import time # убрать на релизе
class QRCodegenerator:
    def __init__(self, data:str, error_correction="M"):
        self._data:str = data
        self.error_correction:str = error_correction  
    
        
    @property
    def data(self) -> list:
        fill_data = ['11101100', '00010001']
        result:str = "0100" + ''.join(format(len(self._data.encode('utf-8')), f'0{8 if self.version <=9 else 16}b')) + '0000' + ''.join(format(byte, '08b') for byte in self._data.encode('utf-8'))
        data = []
        i = 0 
        while len(data) < self.version_table[self.version] - len(result):
            position = i % (len(fill_data[0]) + len(fill_data[1]))
            if position < len(fill_data[0]):
                data.append(fill_data[0][position])
            else:
                data.append(fill_data[1][position-len(fill_data[0])])
            i+=1
        result = result + ''.join(data)
        num_blocks = self.amount_blocks
        if num_blocks == 1:
            return [result]
        blocks = []
        start = 0
        for i in range(num_blocks):
            end = start + len(result)//num_blocks + (1 if i<len(result)%num_blocks else 0)
            blocks.append(result[start:end])
            start = end
        blocks.sort(key=lambda x: len(x))    
        return blocks
    @property
    def version_table(self) -> dict:     
        return tables.version_table[self.error_correction]
    @property
    def amount_blocks(self) -> dict:
        return tables.amount_blocks[self.error_correction][self.version]
    @property
    def amount_correction_byte(self) -> dict:
        return tables.correction_bytes[self.error_correction][self.version]
    @property
    def version(self) -> int:
        lenght = len(''.join(format(byte, '08b') for byte in self._data.encode('utf-8')))
        for version, item in self.version_table.items():
            if lenght <= item:
                return version
        return 10
    @property
    def correction_bytes(self) -> list:
        data = self.data
        result = []
        for block in data:
            bytes_list = []
            for i in range(0, len(block), 8):
                byte_str = block[i:i+8].ljust(8, '0')
                bytes_list.append(int(byte_str, 2))
            prepared_array = bytes_list + [0] * (max(len(bytes_list), self.amount_correction_byte) - len(bytes_list))
            ecc_bytes = prepared_array[:self.amount_correction_byte]
            if self.amount_blocks == 1: 
                return ecc_bytes
            result.append(ecc_bytes)
        return result

    #def generate(self) -> str:
        
    
        

    
    

def save_qr_image(qr_matrix, filename):
    img_size = qr_matrix.shape[0]
    img = Image.new('1', (img_size, img_size))
    img.putdata(qr_matrix.flatten())
    img.save(filename)

def main():
    start = time.time() # убрать на релизе
    obj =QRCodegenerator("https://exampleasdsdidfgsdfgsdfgsdfgsdfgjfhossiasjdfhdfgsdfgsdfgsdfgsdfglkjahsdfgid")
    print(obj.version)
    print(obj.version_table[obj.version])
    print(len(obj.data[0]))
    print(obj.amount_blocks)
    print(obj.correction_bytes)
    print(len(obj.correction_bytes[0]))
    print(obj.amount_correction_byte)
    print(f"execute time: {time.time() -start:.2f} секунд")
    #qr_matrix = create_qr_matrix(data)
    #save_qr_image(qr_matrix, "manual_qrcode.png")

if __name__ == "__main__":
    main()