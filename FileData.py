from BitmapFileHeader import BitmapFileHeader
from BitmapInfoHeader import BitmapInfoHeader
from ColorProfile import ColorProfile
from RGBA import RGBA
import math
from bitstring import BitArray
import PySimpleGUI as sg

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from PIL import Image

BITMAP_FILEHEADER_SIZE = 14


class FileData:
    """description of class"""
    
    def __init__(self):
        self.gap1_flag = False
        self.clrProfile_flag = False
        self.gap2_flag = False
        self.bfh = BitmapFileHeader()

        self.dibSize = 0
    
        #image info
        self.compression = 0
        self.bitsPerPixel = 0
        self.imageWidth = 0
        self.imageHight = 0
        self.colorTableOffset = 0
        self.colorTableSize = 0
        self.gap1Offset = 0
        self.gap1Size = 0
        self.imageOffset = 0
        self.imageSize = 0
        self.gap2Offset = 0
        self.gap1Size = 0
        self.pixelArraySize = 0

        self.GAP1 = []
        self.GAP2 = []
        self.colorTable = []
        self.imageData = []
        self.fullImageData = 0
    
    def load(self, file):
        self.sourceFile = file
        #bitmap file header
        if not self.load_bitmap_file_header(file): return False
        #saving bitmap info header size
        file.seek(BITMAP_FILEHEADER_SIZE)
        self.dibSize = int.from_bytes(file.read(4),"little")
        #bitmap info header
        self.load_bitmap_info_header(file)
        # color profile
        self.load_color_profile(file)
        # gap1
        if self.load_gap1(file): self.gap1_flag = True
        # image
        self.load_image_data(file)
        # gap2
        if self.load_gap2(file): self.gap2_flag = True
        return True

    def display_meta_data(self):

        bfh_layout =  [[sg.Multiline(self.bfh.return_as_text(),disabled=True,size = (100,100))]]
        dib_layout =  [[sg.Multiline(self.dib.return_as_text(),disabled=True,size = (100,100))]]

        #color table
        if self.colorTable != []:
            col = 'Color Table' + ' #RGBA '+ '\n'
            i=1
            for color in self.colorTable:
                col += "Color " + str(i).center(3) + ' #' + color.color_to_string_RGBA().upper().center(8) +'\n'
                i+=1

            col_layout = [[sg.Multiline(col,disabled=True, size = (100,100))]]
        else:
            col_layout = [[sg.T("No color profile")]]

       
        #gap 1
        if self.GAP1 != []:
            gap1_layout =  [[sg.Multiline(str(self.GAP1,'utf-8'),disabled=True,size = (100,100))]]
        else:
            gap1_layout =  [[sg.T("Gap 1 is empty")]]

        #gap2 
        if self.GAP2 != []:
            gap2_layout =  [[sg.Multiline(str(self.GAP2,'utf-8'),disabled=True,size = (100,100))]]
        else:
            gap2_layout =  [[sg.T("Gap 2 is empty")]]


        layout = [[sg.TabGroup([[
                                sg.Tab('Bitmap File Header', bfh_layout), 
                                 sg.Tab('Bitmap Info Header', dib_layout),
                                 sg.Tab('Color Table', col_layout),
                                 sg.Tab('Gap 1', gap1_layout),
                                 sg.Tab('Gap 2', gap2_layout)
                                 ]])],]

        window = sg.Window('Meta data', layout, size = (600, 300),finalize = True,auto_size_text=True)
        return window

    def display_image(self):
        im = Image.open(self.sourceFile)
        im.show() 

    # meta data methods
    def load_bitmap_file_header(self,file):
        if not self.bfh.load(file): return False
        #getting useful data from bitmap file header
        self.imageOffset = int.from_bytes(self.bfh.bfOffBits,"little")
        return True
        
    def load_bitmap_info_header(self,file):
        if self.dibSize == 40:
            self.dib = BitmapInfoHeader() 
            self.dib.load(file)

            self.compression = int.from_bytes(self.dib.Compression,"little")
        elif self.dibSize == 12:
            self.dib = BitmapCoreHeader() 
            self.dib.load(file)

            #saving useful data from bitmap info header
        self.bitsPerPixel = int.from_bytes(self.dib.BitCount,"little")
        self.imageWidth = int.from_bytes(self.dib.Width,"little")
        self.imageHight = int.from_bytes(self.dib.Hight,"little")

    # color profile methods
    def load_color_profile(self,file):

        if self.bitsPerPixel == 1 or self.bitsPerPixel == 4 or self.bitsPerPixel == 8 :
            self.colorTableSize = (2 ** self.bitsPerPixel)
            self.colorTableOffset = BITMAP_FILEHEADER_SIZE + self.dibSize
            file.seek(self.colorTableOffset,0)
            for i in range(int(self.colorTableSize)):
                red = int.from_bytes(file.read(1),"big")
                green = int.from_bytes(file.read(1),'big')
                blue = int.from_bytes(file.read(1),'big')
                alpha = int.from_bytes(file.read(1),'big')
                self.colorTable.append(RGBA(red,green,blue,alpha))
                #file.read(1)
            return True

        return False

    def write_to_file_color_profile(self,file):
        for color in self.colorTable:
            file.write(color.color_to_string_RGBA())

    # gap 1 methods
    def load_gap1(self,file):
        self.gap1Offset = self.colorTableOffset + self.colorTableSize * 4 + self.dibSize + BITMAP_FILEHEADER_SIZE
        self.gap1Size = self.imageOffset - self.gap1Offset

        if self.gap1Size > 0: 
            file.seek(self.gap1Offset,0)
            self.GAP1 = file.read(self.gap1Size)
            return True

        return False

    # image methods
    def load_image_data(self,file):
        if (self.imageOffset == 0) and (self.bitsPerPixel == 24):
            self.imageOffset = BITMAP_FILEHEADER_SIZE + self.dib.biSize
            
        rowSize = math.ceil(self.imageWidth * self.bitsPerPixel / 32) * 4 # data pixels + pending data
        self.pixelArraySize = rowSize * abs(self.imageHight)

        file.seek(self.imageOffset,0)
        self.fullImageData = file.read(self.pixelArraySize)

        if self.compression == 0:

            file.seek(self.imageOffset,0)
  
            if self.bitsPerPixel == 1:
                for i in range(self.imageHight):
                    self.imageData.append([]) #new row in image data
                    row = BitArray(file.read(rowSize))
                    for j in range(self.imageWidth):
                        self.imageData[i].append(self.colorTable[1 if row[j] == 1 else 0])

            elif self.bitsPerPixel == 4:
                for i in range(self.imageHight):
                    self.imageData.append([]) #new row in image data
                    row = BitArray(file.read(rowSize))
                    pixels = list(row.cut(4))
                    for j in range(self.imageWidth):
                        self.imageData[i].append(self.colorTable[pixels[j].int])

            elif self.bitsPerPixel == 8:
               for i in range(self.imageHight):
                    self.imageData.append([]) #new row in image data
                    row = list(file.read(rowSize))
                    for j in range(self.imageWidth):
                        self.imageData[i].append(self.colorTable[row[j]])

            elif self.bitsPerPixel == 16:
                pass

            elif self.bitsPerPixel == 24:
                for i in range(self.imageHight):
                    self.imageData.append([]) #new row in image data
                    row = list(file.read(rowSize))
                    for j in range(self.imageWidth):
                        blue = row[3 * j + 0]
                        green = row[3 * j + 1]
                        red = row[3 * j + 2]
                        self.imageData[i].append(RGBA(red,green,blue,0))
                    

            elif self.bitsPerPixel == 32:
                pass

        if self.imageHight > 0: self.imageData = list(reversed(self.imageData))

    # gap 2 methods
    def load_gap2(self,file):
        self.gap2Offset = self.imageOffset + self.pixelArraySize
        pos1 = file.seek(0,2) 
        pos2 = file.seek(self.gap2Offset,0)
        if pos1 > pos2: 
            self.GAP2 = file.read()
            return True

        return False

    # anonymization
    def anonym(self):
        self.bfh.anonim(BITMAP_FILEHEADER_SIZE + self.dibSize)
        self.dib.anonim()

    def writeToFile(self,file):
        self.bfh.writeToFile(file)
        self.dib.writeToFile(file)  
        self.write_to_file_color_profile(file)
        file.write(self.fullImageData)

    # Fourier Transformation 2D
    def dft(self):
        f = []
        i = 0
        for row in self.imageData:      
            f.append([])
            for pixel in row:
                f[i].append((pixel.red + pixel.green + pixel.blue) / 3)
            i += 1
            
        F = np.fft.fft2(f)
        #print(F.shape)

        F_mag = np.abs(np.fft.fftshift(F))
        F_phase = np.angle(np.fft.fftshift(F))

        plt.rc("font", size=10)

        plt.subplot(131)
        imgf = plt.imshow(f, cmap=cm.Greys_r)
        plt.title("original image")

        plt.subplot(132)
        imgFmag = plt.imshow(20*np.log10(1+F_mag),cmap=cm.Greys_r)
        plt.title("|F(k)|")

        plt.subplot(133)
        imgFphase = plt.imshow(F_phase,cmap=cm.Greys_r)
        plt.title("phase of F(k)")
        plt.show(block=False)











