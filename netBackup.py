#!/usr/bin/python
# -*- python -*-
# # # -*- coding: utf-8 -*-

'''
Push a list of commands on a list of equipments
'''

import sys
import argparse
import pexpect
import os.path
import re
import startStop
import login
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", dest="rancid_dir", required=True)
args = parser.parse_args()

# Set variables
if args.rancid_dir:
    rancid_dir = args.rancid_dir
else:
    rancid_dir = "/opt/rancid"
ret_char = '\r'


def getDevices(device_file):
    # Get the list of devices to connect to
    devices = []
    device_file_fd = open(device_file, "r")
    temp = device_file_fd.read().splitlines()
    for d in temp:
        devices.append(d.split(':'))
    return devices


def getCredentials(credential_file):
    # Get the list of credential to connect with
    credentials = []
    credential_file_fd = open(credential_file, "r")
    temp = credential_file_fd.read().splitlines()
    for c in temp:
        credentials.append(c.split(':'))
    # Return list of all credentials give in the credential file
    return credentials


def chooseCredentials(device, credentials):
    # Choose credential according to credential file.
    # If no special credential use the one with *
    for c in credentials:
        if device == c[0]:
            cred = [c[1], c[2]]
            break
        elif c[0] == '*':
            cred = [c[1], c[2]]
            break
    return cred


def connect(device, model, user, password):
    # Spawn connection to the device
    print("Connecting to "+device)
    session = pexpect.spawnu('telnet', [device])
    session.delaybeforesend = 0.5  # sleep before every send().
    if model == "brocade":
        session = login.brocade(session, user, password)
    elif model == "redback":
        session = login.redback(session, user, password)
    elif model == "mikrotik":
        session = login.mikrotik(session, user+"+c", password)
    return session

def getCommands(model):
    if model == "brocade":
        command_file_fd = open("library/bcommand", "r")
        commands = command_file_fd.read().split('\n')
    elif model == "redback":
        command_file_fd = open("library/rcommand", "r")
        commands = command_file_fd.read().split('\n')
    elif model == "mikrotik":
        command_file_fd = open("library/mkcommand", "r")
        commands = command_file_fd.read().split('\n')
    return commands


def sendCommands(session, commands, model):
    # Recursively send commands
    print("Backuping configuration")
    if model == "brocade":
        for command in commands:
            session.send(command + ret_char)
            session.expect('#$')
    if model == "redback":
        for command in commands:
            session.send(command + ret_char)
            session.expect('#$')
    elif model == "mikrotik":
        for command in commands:
            session.send(command + ret_char)
            session.expect('> $')
    return session


def findStartStop(model):
    if model == "brocade":
        start, stop = startStop.brocade()
    elif model == "redback":
        start, stop = startStop.redback()
    elif model == "mikrotik":
        start, stop = startStop.mikrotik()
    return start, stop


def cleanFile(src, dst, start, stop, model):
    if model == "mikrotik":
        for line in src:
            match = re.match(start, line)
            if match:
                dst.write(line)
                break
        for line in src:
            match = re.match(stop, line)
            if match:
                break
            else:
                dst.write(line)
    else :
        for line in src:
            match = re.match(start, line)
            if match:
                dst.write(line)
                break
        for line in src:
            match = re.match(stop, line)
            if match:
                dst.write(line)
                break
            else:
                dst.write(line)

def disconnect(session):
    # Terminate the telnet session, the hard way.
    session.terminate()


def main():
    # Get data from files
    device_file = "devices"
    devices = getDevices(device_file)
    credential_file = "credentials"
    loadCredentials = getCredentials(credential_file)

    # Main loop
    for device in [d for d in devices if d]:  # Filter out empty lines
        d = device[0]
        m = device[1]
        ftemp = rancid_dir+d+".new"
        fname = rancid_dir+d
        if os.path.isfile(ftemp):
            f = open(ftemp, "w")
        else:
            f = open(ftemp, "x")
        # Choose credential in those provided
        credentials = chooseCredentials(d, loadCredentials)
        #print("1")
        # Connect to the device
        session = connect(d, m, credentials[0], credentials[1])
        #print("2")
        # Start logiing session in file f
        session.logfile_read = f
        #print("3")
        # Select commands for a model of device
        commands = getCommands(m)
        #print("4")
        # Send command to the device
        session = sendCommands(session, commands, m)
        #print("5")
        disconnect(session)
        f.close()
        #print("6")

        start, stop = findStartStop(m)
        src = open(ftemp, "r")
        dst = open(fname, "w")
        cleanFile(src, dst, start, stop, m)
        src.close()
        dst.close()
        os.remove(fname+".new")

if __name__ == '__main__':
    main()

