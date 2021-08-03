#!/usr/bin/python3
# -*- python -*-
# # # -*- coding: utf-8 -*-

'''
Push a list of commands on a list of equipments
'''

import argparse
import pexpect
import os.path
import re
import startStop
import login
from pexpect import pxssh

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", dest="rancid_dir", required=True)
parser.add_argument("-v", "--verbose", action="store_true", required=False)
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


def connect(device, model, proto, optiontype, optionvalue, user, password):
    if proto == "telnet":
        # Spawn telnet connection to the device
        session = pexpect.spawnu('telnet', [device])
        session.delaybeforesend = 0.5  # sleep before every send().
        if model == "brocade":
            session = login.brocade(session, user, password)
        elif model == "redback":
            session = login.redback(session, user, password)
        elif model == "cisco":
            session = login.cisco(session, user, password)
        return session
    elif proto == "ssh":
        # Spanw ssh connection to the device
        try:
            session = pxssh.pxssh(
                                 options={optiontype: optionvalue},
                                 encoding="utf-8")
            session.login(device, user, password, auto_prompt_reset=False)
            session.PROMPT = "#$"
            session.prompt()
            # print(session.before)
            return session
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)


def getCommands(model):
    command_file_fd = open("library/"+model+"command", "r")
    commands = command_file_fd.read().split('\n')
    return commands


def sendCommands(session, commands, model, proto):
    # Recursively send commands
    if proto == "telnet":
        for command in commands:
            session.send(command + ret_char)
            session.expect('#$')
        return session
    if proto == "ssh":
        for command in commands:
            session.sendline(command)
            session.prompt()
        return session


def findStartStop(model):
    if model == "brocade":
        start, stop = startStop.brocade()
    elif model == "redback":
        start, stop = startStop.redback()
    elif model == "arista":
        start, stop = startStop.arista()
    elif model == "juniper":
        start, stop = startStop.juniper()
    elif model == "cisco":
        start, stop = startStop.cisco()
    elif model == "fs":
        start, stop = startStop.fs()
    return start, stop


def cleanFile(src, dst, start, stop, model):
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
        d = device[0]  # device name
        m = device[1]  # device model
        proto = device[2]  # protocol to connect to the device telnet or ssh
        if device[3] in device:
            # ssh option typ HostkeyAlgorithms,KexAlgorithms ...
            optiontype = device[3]
        else:
            optiontype = " "
        if device[4] in device:
            # ssh option value +ssh-dss, +diffie-hellman-group1-sha1 ...
            optionvalue = device[4]
        else:
            optionvalue = " "
        ftemp = rancid_dir+d+".new"
        fname = rancid_dir+d
        if os.path.isfile(ftemp):
            f = open(ftemp, "w")
        else:
            f = open(ftemp, "x")
        # Choose credential in those provided
        credentials = chooseCredentials(d, loadCredentials)
        if args.verbose:
            print(">>> DEBUG CONNECT TO "+d)  # debug
        # Connect to the device
        session = connect(d, m, proto, optiontype,
                          optionvalue, credentials[0], credentials[1])
        if args.verbose:
            print(">>> DEBUG OPEN LOGING FILE")  # debug
        # Start loging session in file f
        session.logfile_read = f
        # session.logfile_read = sys.stdout
        if args.verbose:
            print(">>> DEBUG SELECT COMMAND")  # debug
        # Select commands for a model of device
        commands = getCommands(m)
        if args.verbose:
            print(">>> DEBUG SEND COMMAND")  # debug
        # Send command to the device
        session = sendCommands(session, commands, m, proto)
        if args.verbose:
            print(">>> DEBUG CLOSE SESSION")  # debug
        disconnect(session)
        f.close()
        if args.verbose:
            print(">>> DEBUG CLOSE FILE")  # debug

        if args.verbose:
            print(">>> DEBUG GET START STOP TAG")  # debug
        start, stop = findStartStop(m)
        if args.verbose:
            print(">>> DEBUG OPEN FILES")  # debug
        src = open(ftemp, "r")
        dst = open(fname, "w")
        if args.verbose:
            print(">>> DEBUG CLEAN FILE")  # debug
        cleanFile(src, dst, start, stop, m)
        if args.verbose:
            print(">>> DEBUG CLOSE FILES")  # debug
        src.close()
        dst.close()
        if args.verbose:
            print(">>> DEBUG REMOVE .NEW FILE")  # debug
        os.remove(fname+".new")


if __name__ == '__main__':
    main()


