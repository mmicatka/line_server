import argparse
import hashlib

def generate_file(num_lines):
    file_name = str(num_lines) + '.sha256.txt'

    with open(file_name, 'w') as f:
        for seed in range(1, num_lines + 1):
            line = hashlib.sha256(str(seed).encode('utf-8')).hexdigest()
            f.write(line + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_lines', type=int, help='the number of lines in the file')
    args = parser.parse_args()
    generate_file(args.num_lines)
