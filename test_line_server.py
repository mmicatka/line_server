# test_line_server.py
import pytest
from flask import url_for
import hashlib
from datetime import datetime


class TestApp:
    def test_lines(self, client):
        line_index = 8
        res = client.get(url_for('lines', line_index=line_index))
        line = hashlib.sha256(str(line_index).encode('utf-8')).hexdigest()
        assert res.json == {'line': line}

    def test_lines_bad_indices(self, client):
        line_indices = [-10, 99999999999999999999]
        for line_index in line_indices:
            res = client.get(url_for('lines', line_index=line_index))
            assert res.status_code == 413
            assert res.json == {'message': 'Invalid line index'}

    def test_lines_bad_index_type(self, client):
        res = client.get(url_for('lines', line_index='this is not an integer'))
        assert res.status_code == 413
        assert res.json == {'message': 'Line index must be an integer'}
