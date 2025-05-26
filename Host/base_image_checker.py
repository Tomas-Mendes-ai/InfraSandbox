#!/usr/bin/python3

# Checks if all conditions are present to run the nspawn container

# Error codes:
# -1 : subprocess error
# 0 : OK
# 1 : Lab can't run on system (e.g. insufficient permissions)
# 2 : python handled exception

# Will implement and polish logging after implementing the module that calls this.
# gnupg (gpg) handling of exit-codes and output-streams is a bit of a mess. Must check for better options (or implement a parser?)

import os
from pathlib import Path
import subprocess
import re


K_RING = "./keyring.kbx"
C_SUM = "./SHA256SUM"
C_SUM_SIG = "./SHA256SUM.gpg"
T_IMAGE = "./image.tar.xz"

NSPAWN_FPR = "9E31BD4963FC2D19815FA7180E2A1E4B25A425F6"
NSPAWN_UUID = "Nspawn.org Team (Nspawn.org Signing key for Images and Containers) <team@nspawn.org>"

#Returns a list with any files missing
def missing_files():

    missing = []

    if k_ring_exists_permissions() == 1: missing.append("K_RING")
    if c_cum_exists_permissions() == 1: missing.append("C_SUM") 
    if c_sum_sig_exists_permissions() == 1: missing.append("C_SUM_SIG")
    if t_image_exists_permissions() == 1: missing.append("T_IMAGE")

    return missing

#Failure causes exit with error code
def check_authenticity():

    p_key()
    c_sum_sig()
    c_sum_match()
    t_image()



#Looks for nspawn.org public key and checks against pre-validated hard-coded values
#Makes this script the trust anchor - will probably review later
def p_key():

    write_log("P_KEY - Looking for public key in {K_RING}\n" \
              "Directing gpg --status-fd to stdout".format(K_RING), 1)

    cmd = ["gpg",
           "--no-default-keyring",
           "--keyring", K_RING,
           "--with-fingerprint",
           "--with-colons",
           "--list-keys"
           "--status-fd", "1"]

    try:

        result = subprocess.run(cmd, capture_output=True, text=True)

        if (not result.returncode == 0):
            write_log("P_KEY - Internal error on subprocess <{subprocess}>\n" \
                      "Options: {options}\n" \
                      "stdout stream:\n{stdout}\n"
                      "stderr stream:\n{stderr}\n" \
                      "Exiting with code -1" \
                      .format(cmd.pop[0], cmd, result.stdout, result.stderr) \
                      , 2)
                
            exit(-1)
        
        r_exp = re.Pattern(r"""pub[:-]+([\w:]+\w).*\n #Metadata
                           fpr[:-]+([\w:]+\w).*\n     #Fingerprint
                           uid[:-]+([^\n]+):\n"""     #Owner Unique Identifier
                           , re.X)
        
        keys = re.findall(r_exp, result.stdout)

        log_not_found = "P_KEY - Subprocess <{subprocess}> found no valid public key.\n" \
                        "Options: {options}\n" \
                        "stdout stream:\n{stdout}\n" \
                        "stderr stream:\n{stderr}\n" \
                        "Proceeding...".format(cmd.pop[0], cmd, result.stdout, result.stderr)

        if len(keys) == 0:
            write_log(log_not_found, 2)
            return 1

        for k in keys:
            if k[2] == NSPAWN_FPR and k[3] == NSPAWN_UUID:

                write_log("P_KEY - Found valid public key:\n" \
                "PUB: {pub}\n" \
                "FPR: {fpr}\n" \
                "UID: {uid}\n".format(k[1], k[2], k[3])
                , 1)
                return 0
            
        write_log(log_not_found, 2)
        
        return 1


    except Exception as e:
        write_log("P_KEY - Exception raised looking for public key in {K_RING}:\n{exception}\n" \
        "Exiting with code 2".format(K_RING, e), 2)
        exit(2)

#Tests checksum signature with nspawn.org public key
def c_sum_sig():

    write_log("C_SUM_SIG - Validating checksum signature {c_sum_sig} with public key\n" \
              "Directing --status-fd to stdout".format(C_SUM_SIG), 1)

    cmd = [
    "gpg",
    "--no-default-keyring",
    "--keyring", K_RING,
    "--status-fd", "1",
    "--verify", C_SUM]

    try:

        result = subprocess.run(cmd, capture_output=True, text=True)

        if (not result.returncode == 0):
            write_log("C_SUM_SIG - Internal error on subprocess <{subprocess}>\n" \
                      "Options: {options}\n" \
                      "stdout stream:\n{stdout}\n"
                      "stderr stream:\n{stderr}\n" \
                      "Couldn't be decrypted?\n"
                      "Exiting with code -1" \
                      .format(cmd.pop[0], cmd, result.stdout, result.stderr) \
                      , 2)
            exit(-1)

        if result.returncode == 0:
            write_log("C_SUM_SIG - Checksum signature {c_sum_sig} valid\n" \
                      "{subprocess} stdout stream:\n{stdout}\n" \
                      "Proceeding...".format(C_SUM_SIG, cmd.pop[0], result.stdout), 1)
    
    except Exception as e:
        write_log("C_SUM_SIG - Exception raised validating {c_sum_sig} signature using public key:\n{exception}\n" \
        "Exiting with code 2".format(C_SUM_SIG, e), 2)
        exit(2)

#Tests checksum against signature  
def c_sum_match():
    
    write_log("C_SUM - Validating checksum {c_sum} againt signature {c_sum_sig}\n" \
              "Directing --status-fd to stdout".format(C_SUM, C_SUM_SIG), 1)

    cmd = [
        "gpg",
        "--no-default-keyring",
        "--keyring", K_RING,
        "--status-fd", "1",
        "--verify", C_SUM, T_IMAGE]
            
    try:
        
        result = subprocess.run(cmd, capture_output=True, text=True)

        if (not result.returncode == 0):
            write_log("C_SUM - Internal error on subprocess <{subprocess}>\n" \
                      "Options: {options}\n" \
                      "stdout stream:\n{stdout}\n"
                      "stderr stream:\n{stderr}\n" \
                      "Checksum doesn't match signature?\n"
                      "Exiting with code -1" \
                      .format(cmd.pop[0], cmd, result.stdout, result.stderr) \
                      , 2)
            exit(-1)

        if result.returncode == 0:
            write_log("C_SUM - Checksum {c_sum} matches signature {c_sum_sig}\n" \
                      "{subprocess} stdout stream:\n{stdout}\n" \
                      "Proceeding...".format(C_SUM, C_SUM_SIG, cmd.pop[0], result.stdout), 1)
              
    except Exception as e:
        write_log("C_SUM - Exception raised validating {c_sum} against signature {c_sum_sig}:\n{exception}\n" \
        "Exiting with code 2".format(C_SUM, C_SUM_SIG, e), 2)
        exit(2)

#tests image checksum against nspawn.org checksum
def t_image():
    
    write_log("", 1)

    cmd = [
        "sha256sum",
        "-c",
        C_SUM]
    try:

        result = subprocess.run(cmd, capture_output=True, text=True)

        if (not result.returncode == 0):
            write_log("T_IMAGE - Internal error on subprocess <{subprocess}>\n" \
                      "Options: {options}\n" \
                      "stdout stream:\n{stdout}\n"
                      "stderr stream:\n{stderr}\n" \
                      "Image doesn't match checksum?\n"
                      "Exiting with code -1" \
                      .format(cmd.pop[0], cmd, result.stdout, result.stderr) \
                      , 2)
            exit(-1)

    except Exception as e:
        write_log("T_IMAGE - Exception raised validating {t_image} against checksum {c_sum}:\n{exception}\n" \
        "Exiting with code 2".format(T_IMAGE, C_SUM, e), 2)
        exit(2)

#Tests if the required files exist with required permissions
def k_ring_exists_permissions():
    return file_exists_permissions(K_RING)

def c_cum_exists_permissions():
    return file_exists_permissions(C_SUM)

def c_sum_sig_exists_permissions():
    return file_exists_permissions(C_SUM_SIG)

def t_image_exists_permissions():
    return file_exists_permissions(T_IMAGE)

def file_exists_permissions(file):

    target = Path(file)

    write_log("{file} - Validating file".format(file), 1)

    try:
        if not target.exists():
            write_log("{file} - File not found, proceeding...".format(file), 1)
            return 1
        
        if not os.access(target, os.R_OK, os.W_OK):
            write_log("{file} - Check read/write permissions and try again.\n" \
                      "Exiting with code 1", 2)
            exit(1)

    except Exception as e:
        write_log("{file} - Exception raised:\n{exception}\n" \
                  "Exiting with code 2".format(file, e), 2)
        exit(2)

    write_log("{file} - Valid". format(file), 1)
    return 0

#method to write logs and output messages.
#Will implement with python's 'logging' module
def write_log(line, stream):
    pass



