BITMAP_FILEHEADER_SIZE = 14
BC_SIZE = 4
BC_WIDTH = 2
BC_HIGHT = 2
BC_PLANES = 2
BC_BCTCOUNT = 2


class BitmapCoreHeader:

    Size = bytes(BC_SIZE)
    Width = bytes(BC_WIDTH)
    Hight = bytes(BC_HIGHT)
    Planes = bytes(BC_PLANES)
    BitCount = bytes(BC_BCTCOUNT)


    def init(self,file):
        file.seek(BITMAP_FILEHEADER_SIZE)
        self.Size = file.read(BC_SIZE)
        self.Width = file.read(BC_WIDTH)
        self.Hight = file.read(BC_HIGHT)
        self.Planes = file.read(BC_PLANES)
        self.BitCount = file.read(BC_BCTCOUNT)
        

    def disp(self):
        print("BCTMAP INFO HEADER:")
        print("\tDIB Header Size:" , int.from_bytes(self.Size,"little"))
        print("\tImage Width: ", int.from_bytes(self.Width,"little"))
        print("\tImage Hight: ", int.from_bytes(self.Hight,"little"))
        print("\tPlanes: ", int.from_bytes(self.Planes,"little"))
        print("\tBitCount: ", int.from_bytes(self.BitCount,"little"))
       
        
    def anonim(self):
        #self.Size 
        #self.Width
        #self.Hight
        self.Planes = bytes(BC_PLANES)
        #self.BitCount  

    def writeToFile(self,file):
        file.write(self.Size+
                   self.Width+
                   self.Hight+
                   self.Planes+
                   self.BitCount)


    def return_as_text(self):

        text = ( "DIB Header Size:" + str(int.from_bytes(self.Size,"little"))+'\n' +
        "Image Width: " + str(int.from_bytes(self.Width,"little"))+'\n' +
        "Image Hight: " + str(int.from_bytes(self.Hight,"little"))+'\n' +
        "Planes: " + str(int.from_bytes(self.Planes,"little"))+'\n' +
        "BitCount: " + str(int.from_bytes(self.BitCount,"little")))
        return text

