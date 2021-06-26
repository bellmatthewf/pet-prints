#!/usr/bin/env python3

# Author: Matthew Bell - 2018

"""Create a socket then perform an action, then close it. Can send/receive tcp,
receive udp, or broadcast udp"""

import socket


class Sockets:
    def __init__(
        self, src_host, src_port, dest_host=None, dest_port=None, broadcast_host=None
    ):
        self.src_host = src_host
        self.src_port = src_port
        self.dest_host = dest_host
        self.dest_port = dest_port
        self.broadcast_host = broadcast_host

    def create_socket(
        self, tcp=None, udp=None, tcp_timeout=None, udp_timeout=None, tcp_listen=None
    ):
        if tcp:
            self.s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if tcp_timeout:
                self.s_tcp.settimeout(tcp_timeout)
            self.s_tcp.bind((self.src_host, self.src_port))
            if tcp_listen:
                self.s_tcp.listen(40)

        if udp:
            self.s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            if udp_timeout:
                self.s_udp.settimeout(udp_timeout)
            self.s_udp.bind((self.src_host, self.src_port))

    def close_socket(self, tcp=None, udp=None):
        if tcp:
            self.s_tcp.close()

        if udp:
            self.s_udp.close()

    def accept_tcp_conn(self):
        conn, addr = self.s_tcp.accept()
        ip = addr[0]
        pi_id = ip.split(".")[3]
        return conn, ip, pi_id

    def send_tcp_data(self, encoded_data, byte_size, connect=None):
        if connect:
            self.s_tcp.connect((self.dest_host, self.dest_port))
        self.s_tcp.sendall(encoded_data, byte_size)
        self.s_tcp.shutdown(socket.SHUT_WR)

    def recv_tcp_data(self, conn, byte_size, close_conn=False, file_location=None):
        chunks = []
        while True:
            data = conn.recv(byte_size)
            if not data:
                break
            chunks.append(data)
        result = b"".join(chunks)
        if file_location:
            f = open(file_location, "wb")
            f.write(result)
            if close_conn:
                conn.close()
            return
        elif close_conn:
            conn.close()
        return result

    def send_udp_data(self, encoded_data):
        self.s_udp.sendto(encoded_data, (self.dest_host, self.dest_port))

    def send_udp_broadcast(self, encoded_data):
        self.s_udp.sendto(encoded_data, (self.broadcast_host, self.dest_port))

    def recv_udp_data(self, byte_size):
        data = self.s_udp.recvfrom(byte_size)
        return data[0]
