# -*- coding: utf-8 -*-
import socket		# For socket connection
import re			# For regex parsing
import platform		# For getting the operating system name
import subprocess	# For executing a shell command

def send_msg(my_socket, msg, host, agent_port = 9002):
	my_socket.settimeout(20)
	my_socket.sendto(msg, (host, agent_port))
	print ('\nMessage sent, waiting response ...')

	while True:
		try:
			rxbuf = my_socket.recv(2000)
			print ('[Success]Message Received!\n')
			show_response_msg(rxbuf)
		except socket.timeout:
			print ('Timeout!!')
			exit()
		S = rxbuf[0]
		break

def show_response_msg(result):
	response_msg = ""
	pattern = re.compile('(?=)"(.*)"')
	pattern_05_00 = re.compile('(?=)(\\x05\\x00)')

	if pattern_05_00.findall(result) :
		print ("Response Ends with x05x00, No message!")
	elif ( pattern.findall(result) == [] ) or (pattern.findall(result) == ""):
		print ("[Error]Empty message/OID unreachable\n")
	else:
		response_msg = pattern.findall(result)
		print (response_msg)

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    A host may not respond to a ping (ICMP) request even if the hostname is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0

# MAIN #
if __name__ == '__main__':
	can_ping = False
	while can_ping!=True :
		agent_IP = raw_input('Agent target IP: ')
		print("\n\t[Testing connection with agent]\n\n")
		can_ping = ping(agent_IP)
	print("\n\t[Stable connection]\n")
	agent_port = int(raw_input('\nTarget Port (161 ou 9002[android]): '))

	again = 'y'

	Comm = raw_input('Community (default = public): ')
	if not Comm:
		Comm = 'public'
	lenComm = len(Comm)

	#makes the socket ready and connects the interface
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	while again == 'y':
		OID = raw_input('OID: ')
		OID = OID.replace(".", "")
		OID = OID[2:]
		oid = chr(0x2b)
		for i in OID:
			if i !=' ':
				oid = oid + chr(int(i))
			else:
				oif = oid + i
		lenOID = len(oid)

		#Mounts SNMP message starting from the end
		#Value Field
		SVal = chr(0x05) + chr(0x00)

		#Objeto Field
		TypeOid = chr(0x06)
		SOid = TypeOid + chr(lenOID) + oid

		#Sequence / Varbind Type Field
		TypeVarbind = chr(0x30) # tipo varbind
		SVarbind = TypeVarbind + chr(lenOID + 2 + 2) + SOid + SVal

		#Sequence / Varbind List Field
		TypeVarbindList = chr(0x30) # tipo varbind list
		SVarbindList = TypeVarbindList + chr(len(SVarbind)) + SVarbind

		#Request ID, Error, ErrorIndex fields
		RqID = chr(2) + chr(1) + chr(1)
		Err = chr(2) + chr(1) + chr(0)
		ErrIndex = chr(2) + chr(1) + chr(0)

		SPDU = chr(0xa0) + chr(3 + 3 + 3 + len(SVarbindList)) + RqID + Err + ErrIndex + SVarbindList

		#Community
		SComm = chr(4) + chr(lenComm) + Comm
		#Version
		SVersao = chr(2) + chr(1) + chr(0)

		#SNMP MESSAGE
		MsgType = chr(0x30)
		SSnmp = MsgType + chr(3 + 2 + lenComm + len(SPDU)) + SVersao + SComm + SPDU
		#Send the message via socket
		send_msg(my_socket, SSnmp, agent_IP, agent_port)

		again = raw_input('\nSend again? (y/n): ')

	my_socket.close()

	print ('End of operation. Socket closed.\n ----- END ----- \n')

'''
# http://www.net-snmp.org/docs/mibs/
# http://oid-info.com/get/1.3.6.1.2.1.2.2.1.1

OIDs:

interface
.1.3.6.1.2.1.2.1.0 = INTEGER: 3
.1.3.6.1.2.1.2.2.1.1.1 = INTEGER: 1
.1.3.6.1.2.1.2.2.1.1.2 = INTEGER: 2
.1.3.6.1.2.1.2.2.1.1.3 = INTEGER: 3
.1.3.6.1.2.1.2.2.1.2.1 = STRING: lo
.1.3.6.1.2.1.2.2.1.2.2 = STRING: Realtek Semiconductor Co., Ltd. RTL8101/2/6E PCI Express Fast/Gigabit Ethernet controller
.1.3.6.1.2.1.2.2.1.2.3 = STRING: Qualcomm Atheros QCA9565 / AR9565 Wireless Network Adapter
.1.3.6.1.2.1.2.2.1.3.1 = INTEGER: softwareLoopback(24)
.1.3.6.1.2.1.2.2.1.3.2 = INTEGER: ethernetCsmacd(6)
.1.3.6.1.2.1.2.2.1.3.3 = INTEGER: ethernetCsmacd(6)
.1.3.6.1.2.1.2.2.1.4.1 = INTEGER: 65536
.1.3.6.1.2.1.2.2.1.4.2 = INTEGER: 1500
.1.3.6.1.2.1.2.2.1.4.3 = INTEGER: 1500
.1.3.6.1.2.1.2.2.1.5.1 = Gauge32: 10000000
.1.3.6.1.2.1.2.2.1.5.2 = Gauge32: 10000000
'''
'''
system
.1.3.6.1.2.1.1.1.0 = STRING: Linux edison-Inspiron-3442 4.4.0-47-generic #68-Ubuntu SMP Wed Oct 26 19:39:52 UTC 2016 x86_64
.1.3.6.1.2.1.1.2.0 = OID: .1.3.6.1.4.1.8072.3.2.10
.1.3.6.1.2.1.1.3.0 = Timeticks: (701525) 1:56:55.25
.1.3.6.1.2.1.1.4.0 = STRING: Me <me@example.org>
.1.3.6.1.2.1.1.5.0 = STRING: edison@edison-Aspire-5741
.1.3.6.1.2.1.1.6.0 = STRING: Sitting on the Dock of the Bay
'''
