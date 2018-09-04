from flask import Flask, jsonify

import argparse
import mmap
import sys
import os
import psutil

from lru import LRU


def create_line_server(filename, num_blocks, block_size):
    app = Flask(__name__)
    mmap_index = {}
    line_keys = []
    lru = LRU(num_blocks)
    f = open(filename, 'r+b')
    mm = mmap.mmap(f.fileno(), 0)


    def create_indices():
        """
        Scan through the file, make a mapping of line numbers
        to byte position in the file

        This is making the assumption there are not more lines
        than space in memory
        """
        # We are using 1-indexed lines in our file for human usability
        line_num = 1
        pos = 0
        new_pos = pos
        while new_pos != -1:
            block_start = pos
            start_line = line_num
            cont = True
            while (pos - block_start) < block_size and cont:
                new_pos = mm.find('\n'.encode('utf-8'), pos + 1)
                if new_pos == -1:
                    cont = False
                elif (new_pos - block_start) <= block_size:
                    pos = new_pos
                    line_num += 1
                else:
                    cont = False

            mmap_index[(start_line, line_num)] = (block_start, pos)
            pos += 1

        for key in sorted(mmap_index.keys()):
            for i in range(key[0], key[1]):
                line_keys.append(key)

        return


    def warm_lru():
        mmap_keys = sorted(list(mmap_index.keys()))

        if num_blocks > len(mmap_keys):
            num_blocks_to_load = len(mmap_keys)
        else:
            num_blocks_to_load = num_blocks

        for i in range(num_blocks_to_load):
            key = mmap_keys[i]
            update_lru(key)
        return

    def update_lru(key):
        lines = []
        pos = mmap_index[key]
        mm.seek(pos[0])
        while mm.tell() < pos[1]:
            line = mm.readline().decode('utf-8').rstrip('\n')
            lines.append(line)
        lru[key] = lines
        return


    @app.before_first_request
    def preprocess():
        """
        This builds the needed indices and warms up the cache

        This can/will cause the first request to hang while the file
        is preprocessed
        """
        create_indices()
        warm_lru()
        return


    @app.route('/lines/<line_index>')
    def lines(line_index):
        try:
            line_index = int(line_index)
        except ValueError:
            response = jsonify(message='Line index must be an integer')
            response.status_code = 413
            return response

        if line_index < 1 or line_index > len(line_keys):
            response = jsonify(message='Invalid line index')
            response.status_code = 413
            return response

        key = line_keys[line_index - 1]
        if not lru.has_key(key):
            update_lru(key)

        line = lru[key][line_index - key[0]]
        return jsonify(line=line)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    free_mem = psutil.virtual_memory().free
    num_blocks = 64
    block_size = (free_mem * 0.7) // num_blocks
    app = create_line_server(args.filename, num_blocks, block_size)
    app.run(port=5000, debug=False)
