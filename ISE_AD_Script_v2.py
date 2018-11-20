#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a script to automatically reset the ISE application when it fails to authenticate.

The script monitors the success of authentication to a monitoring probe which uses ISEs for AAA services.
In case 3 authentication attempts fail due to unresponsiveness, the ISE application is stopped and then restarted.
An email notification is also sent to the specified recipient list.

Update the below section with the relevant information.

"""


import paramiko
import time
import datetime
import socket
import sys
import smtplib
import getpass
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText




##### Update the following information ######
#############################################
ISE_address =
ISE_username =
ISE_password =

Probe_address =
Probe_username =
Probe_password =

Sender_email =
# Recipient_email is a list of comma-separated email addresses:
Recipient_email =  

smtp_server = "smtp.gmail.com"
smtp_server_port = 587

#############################################
#############################################


def restart_ise(ise_address, ise_username, ise_password, ise_port):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(str(datetime.datetime.now()) + ": Trying to connect to ISE...")
        ssh.connect(ise_address, port=ise_port, username=ise_username, password=ise_password, look_for_keys=False, allow_agent=False)
    except socket.error:
        print(str(datetime.datetime.now()) + ": ISE is unreachable. "
                                                     "Please verify IP connectivity to ISE and rerun the script.")
        sys.exit()
    except paramiko.ssh_exception.AuthenticationException:
        print(str(datetime.datetime.now()) + ": Unable to login to ISE. Please verify ISE is reachable, "
                                             "verify proper username/password is set and rerun the script.")
        sys.exit()
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(str(datetime.datetime.now()) + ": ISE is unreachable. Please "
                                             "verify IP connectivity to ISE and then rerun the script.")
        sys.exit()
    except paramiko.ssh_exception.SSHException:
        print(str(datetime.datetime.now()) + ": Unable to login to ISE. Please verify ISE is reachable, "
                                             "verify proper username/password is set and rerun the script.")
        sys.exit()
    print(str(datetime.datetime.now()) + ": Connected to ISE...")
    remote_conn = ssh.invoke_shell()
    remote_conn.send("\n")
    time.sleep(2)
    remote_conn.send("\n")
    time.sleep(2)
    print(str(datetime.datetime.now()) + ": Stopping ISE application...")
    remote_conn.send("application stop ise\n")
    time.sleep(300)
    print(str(datetime.datetime.now()) + ": ISE application has been stopped...")
    # output = remote_conn.recv(65535)
    remote_conn.send("application start ise\n")
    print(str(datetime.datetime.now()) + ": ISE application is being restarted; Please wait...")
    time.sleep(300)
    print(str(datetime.datetime.now()) + ": ISE application is being restarted; Please wait...")
    time.sleep(300)
    # output = remote_conn.recv(65535)
    print(str(datetime.datetime.now()) + ": ISE application has been restarted...")
    ssh.close()


def send_email(from_email, from_email_password, to_email, smtp_email_server_address, smtp_email_server_port):
    email_server = smtplib.SMTP(smtp_email_server_address, smtp_email_server_port)
    email_server.ehlo()
    email_server.starttls()
    email_server.ehlo()
    email_server.login(from_email, from_email_password)
    from_address = from_email
    to_address = to_email
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = ', '.join(to_address)
    msg['Subject'] = "Attention: ISE application was restarted!"
    body = "ISE application was stopped/started at " + str(datetime.datetime.now())
    msg.attach(MIMEText(body, 'plain'))
    email_text = msg.as_string()
    email_server.sendmail(from_address, to_address, email_text)
    print(str(datetime.datetime.now()) + ": A notification email was sent to " + ", ".join(str(i) for i in to_email))


def main():
    """
    ISE_address = raw_input("Please enter your ISE IP address: ")
    ISE_username = raw_input("Please enter your username: ")
    ISE_password = getpass.getpass(prompt="Please enter your password: ")
    Probe_address = raw_input("Please enter your monitor probe IP address: ")
    Probe_username = raw_input("Please enter your probe username: ")
    Probe_password = getpass.getpass(prompt="Please enter your probe password: ")
    Sender_email = raw_input("Please enter the sender email address: ")
    Recipient_email = raw_input("Please enter the recipient email: ")
    """
    Email_password = getpass.getpass(prompt="Please enter the sender email password: ")
    while True:
        print(str(datetime.datetime.now()) + ": Starting the ISE monitoring script using probe "
                                             "to " + Probe_address + ".")
        failure_count = 0
        while failure_count < 3:
            try:
                probe = paramiko.SSHClient()
                probe.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                probe.connect(Probe_address, port=22, username=Probe_username, password=Probe_password)
                time.sleep(30)
                probe.close()
                print(str(datetime.datetime.now()) + ": Monitoring probe is reachable. No actions needed.")
                failure_count = 0
            except socket.error:
                print(str(datetime.datetime.now()) + ": Monitor probe is unreachable. "
                                                     "Please verify IP connectivity to the probe and rerun the script.")
                sys.exit()
            except paramiko.ssh_exception.AuthenticationException:
                failure_count += 1
                print(str(datetime.datetime.now()) + ": Authentication failed " + str(failure_count) + " time(s).")
                time.sleep(60)
            except paramiko.ssh_exception.NoValidConnectionsError:
                print(str(datetime.datetime.now()) + ": Monitor probe is unreachable. Please "
                                                     "verify IP connectivity to the probe and then rerun the script.")
                sys.exit()
            except paramiko.ssh_exception.SSHException:
                print(str(datetime.datetime.now()) + ": Invalid credentials for the probe. Please "
                                                     "set proper username/password and rerun the script.")
                sys.exit()
        print(str(datetime.datetime.now()) + ": Authentication to probe "
                                             "unavailable. We will proceed with the ISE restart to recover.")
        restart_ise(ISE_address, ISE_username, ISE_password, 22)
        send_email(Sender_email, Email_password, Recipient_email, smtp_server, smtp_server_port)
        time.sleep(600)


if __name__ == '__main__':
    main()