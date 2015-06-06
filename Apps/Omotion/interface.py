import sys
import os
import time
import subprocess
import struct
import string
import pickle

import serial


class interface:
    def __init__(self, platform = "atmega32u4"):
        # atmega2560, atmega328p
        self.platform = platform
        
        self.variables = {}
        self.ser = None
        self.id_offset = 0

        self.com_ok = True
        self.err_count = 0

        self.var_types = {"boolean": 1, "char": 1, "unsigned char": 1,
                          "byte": 1, "int": 2, "unsigned int": 2, "word": 2,
                          "long": 4, "unsigned long": 4, "short": 2,
                          "float": 4, "double": 4}


    # initializes arduino connection
    def init_serial(self, com):
        try:
            # if just com number is given
            pycom = int(com) - 1
        except:
            # for linux (dev/tty -stuff)
            pycom = com
            
        self.ser = serial.Serial(pycom, 115200, timeout = 0.1)
        # wait bootloader to timeout
        time.sleep(3)
        # clear rx buffer
        self.ser.read(20)

    def disconnect(self):
        self.ser.close()

    def get_status(self):
        if self.ser and self.ser.isOpen():
            return "Open"
        else:
            return "Closed"


    # get all global variables of the arduino sketch
    def get_variables(self, elf_path, forced_relink = False):

        if elf_path.strip() == "":
            f = open("/home/pi/Omotion/variables.db")
            #f = open("variables.db")
            self.variables = pickle.load(f)
            f.close()
            self.ser.read(20)
            return self.create_ret_vars()
        
        # search paths from elf-file
        base_path, file_name, arduino_path = self.get_paths(elf_path)

        map_path = os.path.join(base_path, file_name + ".cpp.map")

        # if there isn't map-file already or relink is forced,
        # the new map-file is created. 
        if not os.path.exists(map_path) or forced_relink:
            map_path = self.relink(base_path, file_name, arduino_path)

        # search global variables from map file    
        self.parse_map(map_path)

        print "1", self.variables

        # search type declarations for variables
        self.parse_source(base_path, file_name)

        print "2", self.variables

        # remove unused variables and add offset to addresses
        self.clean_up_var_list()

        print "3", self.variables

        f = open("variables.db", "wb+")
        pickle.dump(self.variables, f)
        f.close()

        self.ser.read(20)
        
        return self.create_ret_vars()
    

    def create_ret_vars(self):
        ret_vars = {}
        for name in self.variables.keys():
            var_type = self.variables[name][2]
            len_val = self.var_types[var_type]
            ret_vars[name] = self.variables[name][1] / len_val

        return ret_vars


    # get variable value from arduino
    def get_variable(self, name, index):
        ret_var = None
        found, ret_var = self.get_value(name, index)
        #print "get", name, index, ret_var
        return ret_var


    # set variable value to arduino
    def set_variable(self, name, value, index):
        val_type = self.variables[name][2]
        if val_type == "float" or val_type == "double":
            self.set_value(name, float(value), index)
        else:
            self.set_value(name, int(value), index)
        


    ####################################
    # "private"
    ####################################

    def fix_path(self, path):
        splitted = path.split("\"")
        new_path = ""
        for part in splitted:
            new_path += part
        return new_path

    def inc_id_offset(self):
        self.id_offset += 1
        if self.id_offset > 7:
            self.id_offset = 0

    def get_value(self, name, offset):
        if not self.com_ok:
            self.ser.read(20)
            
        # id 1..8        
        id_val = 1 + self.id_offset
        self.inc_id_offset()

        var_type = self.variables[name][2]
        len_val = self.var_types[var_type]
        addr = self.variables[name][0] + offset*len_val

        ret_id = None
        ret_val = None
        ret_len = None

        # send request to arduino
        #self.ser.read(20)
        
        msg = struct.pack("BBH", id_val, len_val, addr)
        self.ser.write(msg)
        ret_msg = self.ser.read(2+len_val)

        # decode reply according to variable type
        if len(ret_msg) == 2+len_val:
            if var_type == "boolean" or var_type == "char":
                ret_id, ret_len, ret_val = struct.unpack("=BBb", ret_msg)
            if var_type == "unsigned char" or var_type == "byte":
                ret_id, ret_len, ret_val = struct.unpack("=BBB", ret_msg)
            if var_type == "int" or var_type == "short":
                ret_id, ret_len, ret_val = struct.unpack("=BBh", ret_msg)
            if var_type == "unsigned int" or var_type == "word":
                ret_id, ret_len, ret_val = struct.unpack("=BBH", ret_msg)
            if var_type == "long":
                ret_id, ret_len, ret_val = struct.unpack("=BBl", ret_msg)
            if var_type == "unsigned long":
                ret_id, ret_len, ret_val = struct.unpack("=BBL", ret_msg)
            if var_type == "float" or var_type == "double":
                ret_id, ret_len, ret_val = struct.unpack("=BBf", ret_msg)

        # lost bytes(s)
        # todo: resynch scema
        if ret_id == id_val and ret_len == len_val:
            #print "com ok"
            return True, ret_val
            
        else:
            com_ok = False
            print "com err"
            self.ser.read(20)
            return False, 0


    def set_value(self, name, value, offset):
        ret_id = None
        ret_val = None
        ret_len = None

        # id 64..71
        id_val = 64 + self.id_offset
        self.inc_id_offset()
        
        var_type = self.variables[name][2]
        len_val = self.var_types[var_type]
        addr = self.variables[name][0] + offset*len_val

        #print "set_val", var_type, len_val, addr, name, value, offset, id_val

        # construct message according to varriable type
        if var_type == "boolean" or var_type == "char":
            msg = struct.pack("BBHb", id_val, len_val, addr, value)
        if var_type == "unsigned char" or var_type == "byte":
            msg = struct.pack("BBHB", id_val, len_val, addr, value)
        if var_type == "int" or var_type == "short":
            msg = struct.pack("BBHh", id_val, len_val, addr, value)
        if var_type == "unsigned int" or var_type == "word":
            msg = struct.pack("BBHH", id_val, len_val, addr, value)
        if var_type == "long":
            msg = struct.pack("BBHl", id_val, len_val, addr, value)
        if var_type == "unsigned long":
            msg = struct.pack("BBHL", id_val, len_val, addr, value)
        if var_type == "float" or var_type == "double":
            msg = struct.pack("BBHf", id_val, len_val, addr, value)

        # send it to arduino
        self.ser.write(msg)
        ret_msg = self.ser.read(2)
        if len(ret_msg) == 2:
            ret_id, ret_len = struct.unpack("=BB", ret_msg)

        #print "set_val_msg", "." + msg + ".", ret_id, ret_len

        # communication ok?
        if ret_id == id_val and ret_len == len_val:
            return True
        else:
            return False
        

    def clean_up_var_list(self):
        for key in self.variables.keys():
            if self.variables[key][0] == 0:
                # delete variables that are dropped by the compiler (address = 0)
                del self.variables[key]
                continue
            
            if self.variables[key][1] > 4 and self.variables[key][2] == "unknown":
                # remove tables that are not defined in the "user" code
                del self.variables[key]
                continue
            
            # address space in arduino is 2 bytes long and start from 0
            # => there is 0x800000 offset compared to map-file
            self.variables[key][0] -= int("800000", 16)


            # guess data types for variables that are not defined in *.cpp
            if self.variables[key][2] == "unknown" and self.variables[key][1] == 4:
                self.variables[key][2] = "long"

            if self.variables[key][2] == "unknown" and self.variables[key][1] == 2:
                self.variables[key][2] = "int"

            if self.variables[key][2] == "unknown" and self.variables[key][1] == 1:
                self.variables[key][2] = "char"

            # 3 bytes long (object)
            if self.variables[key][2] == "unknown":
                del self.variables[key]



    # is there #include "globals.h"
    def globals_h(self, source_path):
        f = open(source_path, "r")
        count = 0
        
        for line in f:
            count += 1
            
            line = line.strip()

            if len(line) == 0:
                continue

            if line.find("#include \"globals.h\"") > -1:
                return True

            if count > 100:
                return False

        return False        


    def parse_source(self, base_path, file_name):

        source_path = os.path.join(base_path, file_name + ".cpp")

        if self.globals_h(source_path):
            h_path = os.path.join(base_path, "globals.h")
            f = open(h_path, "r")
        else:
            f = open(source_path, "r")

        block_count = 0
        count = 0

        for line in f:
            count += 1

            comment = line.find("//")
            if comment > -1:
                line = line[0:comment]
            
            line = line.strip()

            if len(line) == 0:
                continue

            block_count += string.count(line, "{")
            block_count -= string.count(line, "}")

            if block_count > 0:
                continue

            for typ in self.var_types.keys():
                if len(line) <= len(typ):
                    continue

                # remove volatile
                if len(line) > 8 and line[0:8] == "volatile":
                    line = line[9:]

                if line[0:len(typ)] == typ and line[-1] == ";":
                    eq = line.find("=")
                    if eq > -1:
                        def_vars = line[len(typ):eq].split(",")
                    else:
                        def_vars = line[len(typ):-1].split(",")
                        
                    for var in def_vars:
                        var = var.strip()
                        bracket = var.find("[")
                        if bracket > -1:
                            var = var[0:bracket]
                        
                        if self.variables.has_key(var):
                            self.variables[var][2] = typ        
                    break;



    # reads binary file and return its content as single string
    def read_binary_file(self, bin_file):
        f = open(bin_file, "rb")

        byte = f.read(1)
        count = 0
        string = ""

        while byte != "":
            count += 1
            if byte:
                pass
            else:
                break

            string += byte
            byte = f.read(1)
            
        f.close()
        return string


    # all needed paths can be extracted from the elf-file
    # todo: this is a hack. more robust way is needed.
    def get_paths(self, elf_path):
        base_path, elf_file = os.path.split(elf_path)

        #elf = self.read_binary_file(elf_path)

        # "works in our lab"
        #index = elf.find(base_path)
        #index2 = elf.find("hardware\\arduino", index)
        #arduino_path = elf[index+len(base_path)+1:index2]

        file_name = elf_file[0:-8]

        arduino_path = ""

        print "paths", base_path, file_name, arduino_path

        return base_path, file_name, arduino_path


    def find_map(self, base_path, file_name):
        return os.path.exists( os.path.join(base_path, file_name + ".cpp.map") )


    # when arduino sketch is linked, there is no -Wl,-Map option used.
    # To make matters worse, build process doesn't use any make- or config-files,
    # everything is hard coded in processing.app.debug.Compiler :(

    # fortunately we have enough information to relink the code 
    # now we can get our hands to map-file that is basically map of the address space

    # todo: platform sniffing (how?)
    def relink(self, base_path, file_name, arduino_path):
        print "relink_cmd 3  ." + arduino_path + "."
        
        file_wo_suffix = base_path + "\\" + file_name

        print "file  ." + file_wo_suffix + "."
        
        cmd = "C:\\arduino-1.0.1\\hardware\\tools\\avr\\bin\\avr-gcc "

        print "cmd1  ." + cmd + "."
        
        cmd += "-Os "
        cmd += "-Wl,--gc-sections " #,--relax "
        cmd += "-Wl,-Map=" + file_wo_suffix + ".cpp.map "
        cmd += "-mmcu=" + self.platform + " "
        cmd += "-o " + file_wo_suffix + ".cpp.elf " + file_wo_suffix + ".cpp.o "
        cmd += self.get_libs(base_path)
        cmd += base_path + "\\core.a "
        cmd += "-L" + base_path + " "
        cmd += "-lm "

        print "relink_cmd  ." + cmd + "."

        ret_code = subprocess.call(cmd)


        if ret_code > 0:
            print "Error: relinking failed"
            return ""

        map_path = file_wo_suffix + ".cpp.map"

        return map_path


    def get_libs(self, path):
        folders = [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]

        ret_str = ""

        for lib in folders:
            ret_str += path + "\\" + lib + "\\" + lib + ".cpp.o "

        return ret_str


    # parse global variables from the file
    def parse_map(self, map_path):
        self.variables = {}
        
        f = open(map_path, "r")

        data_in_next_line = False
        count = 0

        for line in f:
            line = line.strip()
            count += 1

            if len(line) == 0:
                continue

            line = line.split()

            index1 = line[0].find(".data.")
            index2 = line[0].find(".bss.")

            if index1 == 0 or index2 == 0:
                if line[0][0:5] == ".bss.":
                    name = line[0][5:]
                else:
                    name = line[0][6:]
                    
                if len(line) == 1:
                    data_in_next_line = True
                else:
                    self.variables[name] = [int(line[1],16), int(line[2],16), "unknown"]
            

            elif data_in_next_line:
                data_in_next_line = False
                self.variables[name] = [int(line[0], 16), int(line[1],16), "unknown"]
                
        f.close()
