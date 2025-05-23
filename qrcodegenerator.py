import numpy as np
from PIL import Image
from io import BytesIO
from version import Version
from encoder import Encoder
from errorcorrection import ErrorCorrection

class QRCodeGenerator:
    def __init__(self):
        self.version = Version()
        self.aligment_patern_locations = {
            2:  [18, 6],
            3:  [22, 6],
            4:  [26, 6],
            5:  [30, 6],
            6:  [34, 6],
            7:  [38, 22, 6],
            8:  [42, 24, 6],
            9:  [46, 26, 6],
            10: [50, 28, 6],
            11: [54, 30, 6],
            12: [58, 32, 6],
            13: [62, 34, 6],
            14: [66, 46, 26, 6],
            15: [70, 48, 26, 6],
            16: [74, 50, 26, 6],
            17: [78, 54, 30, 6],
            18: [82, 56, 30, 6],
            19: [86, 58, 30, 6],
            20: [90, 62, 34, 6],
            21: [94, 72, 50, 28, 6],
            22: [98, 74, 50, 26, 6],
            23: [102, 78, 54, 30, 6],
            24: [106, 80, 54, 28, 6],
            25: [110, 84, 58, 32, 6],
            26: [114, 86, 58, 30, 6],
            27: [118, 90, 62, 34, 6],
            28: [122, 98, 74, 50, 26, 6],
            29: [126, 102, 78, 54, 30, 6],
            30: [130, 104, 78, 52, 26, 6],
            31: [134, 108, 82, 56, 30, 6],
            32: [138, 112, 86, 60, 34, 6],
            33: [142, 114, 86, 58, 30, 6],
            34: [146, 118, 90, 62, 34, 6],
            35: [150, 126, 102, 78, 54, 30, 6],
            36: [154, 128, 102, 76, 50, 24, 6],
            37: [158, 132, 106, 80, 54, 28, 6],
            38: [162, 136, 110, 84, 58, 32, 6],
            39: [166, 138, 110, 82, 54, 26, 6],
            40: [170, 142, 114, 86, 58, 30, 6]
        }
    def generate(self, text, output_file):
        print(f'Text: {text}')
        encoder = Encoder()
        error_correction = ErrorCorrection()
        print(f'length: {len(text)}')
        version = self.version.get_version_info(text)
        print(f'Version: {version}')
        message = error_correction.generate_error_correction(text, version)
        qr_size = 21 + (version-1) * 4
        qr_matrix = np.zeros((qr_size, qr_size), dtype=int)
        self.place_finder_patterns(qr_matrix)
        align_pattern_location = self.place_aligment_pattern(qr_matrix, version)
        self.place_timing_pattern(qr_matrix)
        self.place_dark_module(qr_matrix, version)
        self.place_data(qr_matrix, message, version, align_pattern_location)
        masked_matrix, best_mask= self.apply_best_mask(qr_matrix, version, align_pattern_location)
        format_string= self.generate_format_string(best_mask)
        self.place_format_information(masked_matrix, format_string)
        version_info= self.generate_version_information(version)
        self.place_version_information(masked_matrix, version_info)
        final_qr= self.add_quiet_zone(masked_matrix)
        return self.export_to_png(final_qr, output_file)

    def place_timing_pattern(self, qr_matrix: np):
        size = qr_matrix.shape[0]
        for i in range(8, size - 8):
            self.set_bit(qr_matrix, 6, i, i % 2 == 0)
            self.set_bit(qr_matrix, i, 6, i % 2 == 0)

    def place_dark_module(self, qr_matrix, version):
        self.set_bit(qr_matrix, (4*version)+9, 8, 1)

    def set_bit(self, qr_matrix, row, col, value):
        qr_matrix[row, col] = value

    def place_finder_patterns(self, qr_matrix):
        finder_pattern = np.array([
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1 ,0 ,1],
            [1, 0, 1, 1, 1, 0 ,1],
            [1, 0 ,1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1]
        ])
        qr_matrix[0:7, 0:7] = finder_pattern
        qr_matrix[0:7, -7:] = finder_pattern
        qr_matrix[-7:, 0:7] = finder_pattern

    def place_aligment_pattern(self, qr_matrix: np, version):
        align_loc = []
        if version == 1:
            return
        locations = self.aligment_patern_locations[version]
        size = qr_matrix.shape[0]
        for row in locations:
            for col in locations:
                if not self.overlaps_finder_pattern(row, col, size):
                    pos = [row, col]
                    align_loc.append(pos)
                    self.place_single_aligment_pattern(qr_matrix, row, col)
        return align_loc
    
    def overlaps_finder_pattern(self, row, col, size):
        return ((row < 8 and col < 8) or
                (row < 8 and col > size - 9) or
                (row > size - 9 and col < 8))
    
    def place_single_aligment_pattern(self, qr_matrix: np, center_row, center_col):
        for i in range(-2, 3):
            for j in range(-2, 3):
                if abs(i) == 2 or abs(j) == 2 or (i == 0 and j == 0):
                    qr_matrix[center_row + i, center_col + j] = 1
                else:
                    qr_matrix[center_row + i, center_col + j] = 0

    def place_data(self, qr_matrix: np, final_message, version, align_pattern_loc):
        size = qr_matrix.shape[0]
        up = True
        data_index = 0
        
        for right in range(size - 1, 0, -2):
            if right == 7:  
                right -= 1
            
            for vertical in range(size - 1, -1, -1) if up else range(size):
                for left in range(right, right - 2, -1):
                    if left < 0:
                        continue
                    
                    if self.is_data_module(qr_matrix, vertical, left, version, align_pattern_loc):
                        self.set_bit(qr_matrix, vertical, left, final_message[data_index])
                        data_index += 1
                        if data_index >= len(final_message):
                            return
            
            up = not up

    def is_data_module(self, qr_matrix: np, row, col, version, align_pattern_loc):
        size = qr_matrix.shape[0]
        
        if (row < 9 and col < 9) or (row < 9 and col > size - 9) or (row > size - 9 and col < 9):
            return False
        
        if row == 6:
            return False
        
        if col == 6:
            return False


        if size > 21:
            for pos in align_pattern_loc:
                x= pos[0]
                y= pos[1]
                if (x - 2 <= row <= x + 2) and (y - 2 <= col <= y + 2):
                    return False

        
        if row == 4 * version + 9 and col == 8:
            return False
        
        return True

    def get_alignment_pattern_positions(self, version):
        if version == 1:
            return []
        return self.aligment_patern_locations[version]
    
    def apply_best_mask(self, qr_matrix: np, version, align_pattern_loc):
        best_mask = 0
        best_score = float('inf')
        
        for mask in range(8):
            masked_matrix = self.apply_mask(qr_matrix, mask, version, align_pattern_loc)
            score = self.evaluate_mask(masked_matrix)
            if score < best_score:
                best_score = score
                best_mask = mask
        
        return self.apply_mask(qr_matrix, best_mask, version, align_pattern_loc), best_mask
    
    def apply_mask(self, qr_matrix: np, mask_pattern, version, align_pattern_loc):
        size = qr_matrix.shape[0]
        masked_matrix = qr_matrix.copy()
        
        for row in range(size):
            for col in range(size):
                if self.is_data_module(masked_matrix, row, col, version, align_pattern_loc):
                    if self.mask_function(mask_pattern, row, col):
                        masked_matrix[row, col] = 1 - masked_matrix[row, col] 
        
        return masked_matrix

    def mask_function(self, mask_pattern, row, col):
        if mask_pattern == 0:
            return (row + col) % 2 == 0
        elif mask_pattern == 1:
            return row % 2 == 0
        elif mask_pattern == 2:
            return col % 3 == 0
        elif mask_pattern == 3:
            return (row + col) % 3 == 0
        elif mask_pattern == 4:
            return (row // 2 + col // 3) % 2 == 0
        elif mask_pattern == 5:
            return ((row * col) % 2) + ((row * col) % 3) == 0
        elif mask_pattern == 6:
            return (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
        elif mask_pattern == 7:
            return (((row + col) % 2) + ((row * col) % 3)) % 2 == 0

    def evaluate_mask(self, masked_matrix):
        return (self.evaluate_condition_1(masked_matrix) +
                self.evaluate_condition_2(masked_matrix) +
                self.evaluate_condition_3(masked_matrix) +
                self.evaluate_condition_4(masked_matrix))

    def evaluate_condition_1(self, matrix: np):
        penalty = 0
        size = matrix.shape[0]
        for row in range(size):
            count = 1
            for col in range(1, size):
                if matrix[row, col] == matrix[row, col-1]:
                    count += 1
                else:
                    if count >= 5:
                        penalty += 3 + (count - 5)
                    count = 1
            if count >= 5:
                penalty += 3 + (count - 5)
        for col in range(size):
            count = 1
            for row in range(1, size):
                if matrix[row, col] == matrix[row-1, col]:
                    count += 1
                else:
                    if count >= 5:
                        penalty += 3 + (count - 5)
                    count = 1
            if count >= 5:
                penalty += 3 + (count - 5)

        return penalty

    def evaluate_condition_2(self, matrix: np):
        penalty = 0
        size = matrix.shape[0]

        for row in range(size - 1):
            for col in range(size - 1):
                if (matrix[row, col] == matrix[row, col+1] == 
                    matrix[row+1, col] == matrix[row+1, col+1]):
                    penalty += 3

        return penalty

    def evaluate_condition_3(self, matrix: np):
        penalty = 0
        size = matrix.shape[0]
        pattern1 = np.array([1, 0, 1, 1, 1, 0, 1])
        pattern2 = np.array([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0])
        for row in range(size):
            for col in range(size - 6):
                if np.array_equal(matrix[row, col:col+7], pattern1):
                    if col >= 4 and np.all(matrix[row, col-4:col] == 0):
                        penalty += 40
                    elif col + 11 <= size and np.all(matrix[row, col+7:col+11] == 0):
                        penalty += 40
        for col in range(size):
            for row in range(size - 6):
                if np.array_equal(matrix[row:row+7, col], pattern1):
                    if row >= 4 and np.all(matrix[row-4:row, col] == 0):
                        penalty += 40
                    elif row + 11 <= size and np.all(matrix[row+7:row+11, col] == 0):
                        penalty += 40

        return penalty

    def evaluate_condition_4(self, matrix: np):
        total_modules = matrix.size
        dark_modules = np.sum(matrix)
        dark_percentage = (dark_modules / total_modules) * 100

        prev_multiple = (dark_percentage // 5) * 5
        next_multiple = prev_multiple + 5

        prev_deviation = abs(prev_multiple - 50) // 5
        next_deviation = abs(next_multiple - 50) // 5

        return min(prev_deviation, next_deviation) * 10
    
    def generate_format_string(self, mask_pattern):
        ec_indicator = '00'
        mask_indicator = f'{mask_pattern:03b}'
        format_bits = ec_indicator + mask_indicator
        generator_poly = int('10100110111', 2)
        format_poly = int(format_bits + '0' * 10, 2)
        
        for _ in range(5):
            if format_poly.bit_length() >= generator_poly.bit_length():
                format_poly ^= generator_poly << (format_poly.bit_length() - generator_poly.bit_length())
        
        error_correction_bits = f'{format_poly:010b}'
        format_string = format_bits + error_correction_bits
        
        mask = int('101010000010010', 2)
        final_format = int(format_string, 2) ^ mask
        
        return f'{final_format:015b}'
    
    def place_format_information_2(self, qr_matrix: np, size):
        for i in range(9):
            if qr_matrix[8, i] != 1:
                qr_matrix[8, i] = 2 
        for i in range(9):
            if qr_matrix[i, 8] != 1:
                qr_matrix[i, 8]= 2
        for i in range(8):
            if qr_matrix[(size-1)-i, 8] != 1:
                qr_matrix[(size-1)-i, 8]= 2
        for i in range(8):
            if qr_matrix[8, (size-1)-i] != 1:   
                qr_matrix[8, (size-1)-i]= 2
    
    def place_format_information(self, qr_matrix: np, format_string):
        size = qr_matrix.shape[0]
        
        for i in range(6):
            qr_matrix[8, i] = int(format_string[i])
            qr_matrix[i, 8] = int(format_string[14 - i])
        qr_matrix[7, 8] = int(format_string[6])
        qr_matrix[8, 7] = int(format_string[7])
        qr_matrix[8, 8] = int(format_string[8])
        
        for i in range(8):
            qr_matrix[size - 1 - i, 8] = int(format_string[i])
        for i in range(7):
            qr_matrix[8, size - 7 + i] = int(format_string[14 - i])

    def generate_version_information(self, version):
        if version < 7:
            return None
        
        version_indicator = f'{version:06b}'
        version_poly = int(version_indicator + '000000000000', 2)
        generator_poly = int('1111100100101', 2)
        
        for _ in range(6):
            if version_poly.bit_length() >= generator_poly.bit_length():
                version_poly ^= generator_poly << (version_poly.bit_length() - generator_poly.bit_length())
        
        error_correction_bits = f'{version_poly:012b}'
        return version_indicator + error_correction_bits
    
    def place_version_information(self, qr_matrix: np, version_info):
        if version_info is None:
            return
        
        size = qr_matrix.shape[0]
        
        for i in range(6):
            for j in range(3):
                qr_matrix[size - 11 + j, i] = int(version_info[i * 3 + j])

        for i in range(6):
            for j in range(3):
                qr_matrix[i, size - 11 + j] = int(version_info[i * 3 + j])

    def add_quiet_zone(self, qr_matrix: np):
        size = qr_matrix.shape[0]
        new_size = size + 8
        new_matrix = np.zeros((new_size, new_size), dtype=int)
        new_matrix[4:-4, 4:-4] = qr_matrix
        return new_matrix
    
    def export_to_png(self, qr_matrix: np, filename, scale=10, quiet_zone=True):
        if quiet_zone:
            qr_matrix = self.add_quiet_zone(qr_matrix)
        
        height, width = qr_matrix.shape
        image = Image.new('RGB', (width * scale, height * scale), 'white')
        pixels = image.load()

        for y in range(height):
            for x in range(width):
                if qr_matrix[y, x] == 1:
                    for i in range(scale):
                        for j in range(scale):
                            pixels[x * scale + i, y * scale + j] = (0, 0, 0)
        img_byte_array = BytesIO()
        image.save(img_byte_array, format="PNG")
        if __name__ == '__main__':
            image.save(filename)
            print(f"QR code saved as {filename}")
        return img_byte_array.getvalue()
        