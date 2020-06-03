import math
import binascii
import PySimpleGUI as sg

BF_TYPE = 2
BF_SIZE = 4
BF_RESERVED_1 = 2
BF_RESERVED_2 = 2
BF_OFFBITS = 4

POSSIBLE_BITMAP_SIGNATURE = (b'BM',b'BA',b'CI',b'CP',b'IC',b'PT')

class BitmapFileHeader:

    bfType = bytes(BF_TYPE)
    bfSize = bytes(BF_SIZE)
    bfReserved1 = bytes(BF_RESERVED_1)
    bfReserved2 = bytes(BF_RESERVED_2)
    bfOffBits = bytes(BF_OFFBITS)
       

    def load(self,file):
        file.seek(0)
        self.bfType = file.read(BF_TYPE)
        if self.bfType not in POSSIBLE_BITMAP_SIGNATURE: return False
        self.bfSize = file.read(BF_SIZE)
        self.bfReserved1 = file.read(BF_RESERVED_1)
        self.bfReserved2 = file.read(BF_RESERVED_2)
        self.bfOffBits = file.read(BF_OFFBITS)
        return True
       
    def disp(self):
        print("BITMAP FILE HEADER:")
        print("\tType:" , int.from_bytes(self.bfType,"little"))
        print("\tFile size: ", int.from_bytes(self.bfSize,"little"), "B (" , math.ceil(int.from_bytes(self.bfSize,"little") / 1024), "KB )")
        print("\tReserved1: ", int.from_bytes(self.bfReserved1,"little"))
        print("\tReserved2: ", int.from_bytes(self.bfReserved2,"little"))
        print("\tOffset: ", int.from_bytes(self.bfOffBits,"little"))

    def anonim(self, headersSize):
        #self.bfType
        self.bfSize = bytes(BF_SIZE) 
        self.bfReserved1 = bytes(BF_RESERVED_1)
        self.bfReserved2 = bytes(BF_RESERVED_2)
        self.bfOffBits = headersSize.to_bytes(BF_OFFBITS,'little')

    def writeToFile(self,file):
        file.write(self.bfType + self.bfSize + self.bfReserved1 + self.bfReserved2 + self.bfOffBits)

    def return_as_text(self):

        text = "Type:" + str(self.bfType,'utf-8') +'\n' +  "File size: " + str(int.from_bytes(self.bfSize,"little"))  +  " B (" + str(math.ceil(int.from_bytes(self.bfSize,"little") / 1024))+ " KB)" +'\n' + "Reserved1: "+ str(int.from_bytes(self.bfReserved1,"little")) +'\n' + "Reserved2: " + str(int.from_bytes(self.bfReserved2,"little")) +'\n' +  "Offset: " + str(int.from_bytes(self.bfOffBits,"little"))
        return text
                    