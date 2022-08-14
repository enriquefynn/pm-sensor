#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import sqlite3
import time
import json
import urllib


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        parsed_path = urllib.parse.urlparse(self.path)
        params = parsed_path.query.split('&')
        output = json.dumps(
            list(
                map(
                    lambda i: {
                        'timestamp': int(i[0]),
                        'pm10': int(i[1]),
                        'pm2_5': int(i[2]),
                    },
                    get_pm_values(),
                )
            )
        )
        self.wfile.write(output.encode())

    def do_POST(self):
        content_length = int(
            self.headers['Content-Length']
        )  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info(
            "POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            str(self.path),
            str(self.headers),
            post_data.decode('utf-8'),
        )
        post_data = json.loads(post_data)
        insert_pm_values(post_data['pm10'], post_data['pm2_5'])

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def create_tables(cur):
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS pm_sensor (
                timestamp                   INTEGER PRIMARY KEY,
                pm10						INTEGER,
                pm2_5						INTEGER
        	)'''
    )


def insert_pm_values(pm10, pm2_5):
    timestamp = int(time.time())
    cur.execute(
        '''INSERT INTO pm_sensor(timestamp, pm10, pm2_5) VALUES (?, ?, ?)''',
        [timestamp, pm10, pm2_5],
    )
    con.commit()


def get_pm_values():
    return cur.execute('''SELECT timestamp, pm10, pm2_5 from pm_sensor''')


con = sqlite3.connect('./pm_sensor.db')
cur = con.cursor()


def run(server_class=HTTPServer, handler_class=S, port=8080):
    create_tables(cur)

    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
