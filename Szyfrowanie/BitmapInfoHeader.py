import PySimpleGUI as sg

BITMAP_FILEHEADER_SIZE = 14
BI_SIZE = 4
BI_WIDTH = 4
BI_HIGHT = 4
BI_PLANES = 2
BI_BITCOUNT = 2
BI_COMPRESSION = 4
BI_SIZEIMAGE = 4
BI_XPELSPERMETER = 4
BI_YPELSPERMETER = 4
BI_CLRUSED = 4
BI_CLRIMPORTANT = 1
BI_CLRROTATION = 1
BI_RESERVED = 2


class BitmapInfoHeader:

    Size = bytes(BI_SIZE)
    Width = bytes(BI_WIDTH)
    Hight = bytes(BI_HIGHT)
    Planes = bytes(BI_PLANES)
    BitCount = bytes(BI_BITCOUNT)
    Compression= bytes(BI_COMPRESSION)
    SizeImage= bytes(BI_SIZEIMAGE)
    XPelsPerMeter= bytes(BI_XPELSPERMETER)
    YPelsPerMeter= bytes(BI_YPELSPERMETER)
    ClrUsed= bytes(BI_CLRUSED)
    ClrImportant = bytes(BI_CLRIMPORTANT)
    ClrRotation = bytes(BI_CLRROTATION)
    Reserved = bytes(BI_RESERVED)

    def load(self,file):
        file.seek(BITMAP_FILEHEADER_SIZE)
        self.Size = file.read(BI_SIZE)
        self.Width = file.read(BI_WIDTH)
        self.Hight = file.read(BI_HIGHT)
        self.Planes = file.read(BI_PLANES)
        self.BitCount = file.read(BI_BITCOUNT)
        self.Compression= file.read(BI_COMPRESSION)
        self.SizeImage= file.read(BI_SIZEIMAGE)
        self.XPelsPerMeter= file.read(BI_XPELSPERMETER)
        self.YPelsPerMeter= file.read(BI_YPELSPERMETER)
        self.ClrUsed= file.read(BI_CLRUSED)
        self.ClrImportant = file.read(BI_CLRIMPORTANT)
        self.ClrRotation = file.read(BI_CLRROTATION)
        self.Reserved = file.read(BI_RESERVED)

    def disp(self):
        print("BITMAP INFO HEADER:")
        print("\tDIB Header Size:" , int.from_bytes(self.Size,"little"))
        print("\tImage Width: ", int.from_bytes(self.Width,"little"))
        print("\tImage Hight: ", int.from_bytes(self.Hight,"little"))
        print("\tPlanes: ", int.from_bytes(self.Planes,"little"))
        print("\tBitCount: ", int.from_bytes(self.BitCount,"little"))
        print("\tCompression:" , int.from_bytes(self.Compression,"little"))
        print("\tImage Size: ", int.from_bytes(self.SizeImage,"little"))
        print("\tHorizontal Resolution (pixels per meter): ", int.from_bytes(self.XPelsPerMeter,"little"))
        print("\tVertical Resolution (pixels per meter): ", int.from_bytes(self.YPelsPerMeter,"little"))
        print("\tNumber of used colors: ", int.from_bytes(self.ClrUsed,"little"))
        print("\tNumber of important colors:" , int.from_bytes(self.ClrImportant,"little"))
        print("\tColor rotation: ", int.from_bytes(self.ClrRotation,"little"))
        print("\tReserved: ", int.from_bytes(self.Reserved,"little"))
        
    def anonim(self):
        #self.Size 
        #self.Width
        #self.Hight
        self.Planes = bytes(BI_PLANES)
        #self.BitCount
        self.Compression= bytes(BI_COMPRESSION)
        self.SizeImage= bytes(BI_SIZEIMAGE)
        self.XPelsPerMeter= bytes(BI_XPELSPERMETER)
        self.YPelsPerMeter= bytes(BI_YPELSPERMETER)
        self.ClrUsed= bytes(BI_CLRUSED)
        self.ClrImportant = bytes(BI_CLRIMPORTANT)
        self.ClrRotation = bytes(BI_CLRROTATION)
        self.Reserved = bytes(BI_RESERVED)  

    def writeToFile(self,file):
        file.write(self.Size+
                   self.Width+
                   self.Hight+
                   self.Planes+
                   self.BitCount+
                   self.Compression+
                   self.SizeImage+
                   self.XPelsPerMeter+
                   self.YPelsPerMeter+
                   self.ClrUsed+
                   self.ClrImportant+
                   self.ClrRotation+
                   self.Reserved)

    def return_as_text(self):

        text = ( "DIB Header Size:" + str(int.from_bytes(self.Size,"little"))+'\n' +
        "Image Width: " + str(int.from_bytes(self.Width,"little"))+'\n' +
        "Image Hight: " + str(int.from_bytes(self.Hight,"little"))+'\n' +
        "Planes: " + str(int.from_bytes(self.Planes,"little"))+'\n' +
        "BitCount: " + str(int.from_bytes(self.BitCount,"little"))+'\n' +
        "Compression:" + str(int.from_bytes(self.Compression,"little"))+'\n' +
        "Image Size: " + str(int.from_bytes(self.SizeImage,"little"))+'\n' +
        "Horizontal Resolution (pixels per meter): " + str(int.from_bytes(self.XPelsPerMeter,"little"))+'\n' +
        "Vertical Resolution (pixels per meter): " + str(int.from_bytes(self.YPelsPerMeter,"little"))+'\n' +
        "Number of used colors: " + str(int.from_bytes(self.ClrUsed,"little"))+'\n' +
        "Number of important colors:" + str(int.from_bytes(self.ClrImportant,"little"))+'\n' +
        "Color rotation: " + str(int.from_bytes(self.ClrRotation,"little"))+'\n' +
        "Reserved: " + str(int.from_bytes(self.Reserved,"little")))
        return text