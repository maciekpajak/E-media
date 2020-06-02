from BitmapFileHeader import BitmapFileHeader
from BitmapInfoHeader import BitmapInfoHeader
from ColorProfile import ColorProfile
from RGBA import RGBA
import RSA
import rsa


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

        self.GAP1 = b''
        self.GAP2 = b''
        self.colorTable = []
        self.imageData = []
        self.fullImageData = 0

        self.key = ()
    
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

        bfh_layout = [[sg.Multiline(self.bfh.return_as_text(),disabled=True,size = (100,100))]]
        dib_layout = [[sg.Multiline(self.dib.return_as_text(),disabled=True,size = (100,100))]]

        #color table
        if self.colorTable != []:
            col = 'Color Table' + ' #RGBA ' + '\n'
            i = 1
            for color in self.colorTable:
                col += "Color " + str(i).center(3) + ' #' + color.color_to_string_RGBA().upper().center(8) + '\n'
                i+=1

            col_layout = [[sg.Multiline(col,disabled=True, size = (100,100))]]
        else:
            col_layout = [[sg.T("No color profile")]]

       
        #gap 1
        if self.GAP1 != []:
            gap1_layout = [[sg.Multiline(str(self.GAP1),disabled=True,size = (100,100))]]
        else:
            gap1_layout = [[sg.T("Gap 1 is empty")]]

        #gap2
        if self.GAP2 != []:
            gap2_layout = [[sg.Multiline(str(self.GAP2),disabled=True,size = (100,100))]]
        else:
            gap2_layout = [[sg.T("Gap 2 is empty")]]


        layout = [[sg.TabGroup([[sg.Tab('Bitmap File Header', bfh_layout), 
                                 sg.Tab('Bitmap Info Header', dib_layout),
                                 sg.Tab('Color Table', col_layout),
                                 sg.Tab('Gap 1', gap1_layout),
                                 sg.Tab('Gap 2', gap2_layout)]])],]

        window = sg.Window('Meta data', layout, size = (600, 300),keep_on_top = True,finalize = True,auto_size_text=True)
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
            tmp = bytes(color.color_to_string_RGBA(),'ascii')
            tmp = color.color_to_bytes_RGBA()
            file.write(color.color_to_bytes_RGBA())

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

        #--------------------- Progres bar window
        #----------------------------------
        # layout the window
        layout = [[sg.ProgressBar(self.imageHight, orientation='h', size=(20, 20),key='progressbar',bar_color=('blue', 'white'))],
                    [sg.Text('  0%',key = 'progress')]]
        # create the window
        window = sg.Window('', layout,keep_on_top = True, finalize = True)
        progress_bar = window['progressbar']
        progress_percent = window['progress']
        #--------------------- Progres bar window
        #----------------------------------

        if self.compression == 0:
            file.seek(self.imageOffset,0)
  
            if self.bitsPerPixel == 1:
                for i in range(self.imageHight):
                    # updating progress bar ----------------------
                    prc = int(100 * (i + 1) / self.imageHight)
                    progress_percent.update(str(prc) + '%')
                    progress_bar.update_bar(i + 1)
                    #---------------------------------------------
                    self.imageData.append([]) #new row in image data
                    row = BitArray(file.read(rowSize))
                    for j in range(self.imageWidth):
                        self.imageData[i].append(self.colorTable[1 if row[j] == 1 else 0])

            elif self.bitsPerPixel == 4:
                for i in range(self.imageHight):
                    # updating progress bar ----------------------
                    prc = int(100 * (i + 1) / self.imageHight)
                    progress_percent.update(str(prc) + '%')
                    progress_bar.update_bar(i + 1)
                    #---------------------------------------------
                    self.imageData.append([]) #new row in image data
                    row = BitArray(file.read(rowSize))
                    pixels = list(row.cut(4))
                    for j in range(self.imageWidth):
                        self.imageData[i].append(self.colorTable[pixels[j].int])

            elif self.bitsPerPixel == 8:
               for i in range(self.imageHight):
                   # updating progress bar ----------------------
                    prc = int(100 * (i + 1) / self.imageHight)
                    progress_percent.update(str(prc) + '%')
                    progress_bar.update_bar(i + 1)
                    #---------------------------------------------
                    self.imageData.append([]) #new row in image data
                    row = list(file.read(rowSize))
                    for j in range(self.imageWidth):
                        self.imageData[i].append(self.colorTable[row[j]])

            elif self.bitsPerPixel == 16:
                pass

            elif self.bitsPerPixel == 24:
                for i in range(self.imageHight):
                    # updating progress bar ----------------------
                    prc = int(100 * (i + 1) / self.imageHight)
                    progress_percent.update(str(prc) + '%')
                    progress_bar.update_bar(i + 1)
                    #---------------------------------------------
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
        window.close()

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
        self.bfh.anonim(BITMAP_FILEHEADER_SIZE + self.dibSize + self.colorTableSize * 4) #dodane +self.colorTableSize
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
        imgFmag = plt.imshow(20 * np.log10(1 + F_mag),cmap=cm.Greys_r)
        plt.title("|F(k)|")

        plt.subplot(133)
        imgFphase = plt.imshow(F_phase,cmap=cm.Greys_r)
        plt.title("phase of F(k)")
        plt.show(block=False)

    def ECB_make_encrypted_file(self, key):
        
        encryptedData = RSA.encrypt_ECB(self.fullImageData,key)
        file2 = open("./encrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(encryptedData)
        file2.close()

    def ECB_make_decrypted_file(self, key):
        decryptedData = RSA.decrypt_ECB(self.fullImageData + self.GAP2,key)
        file2 = open("./decrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(decryptedData)
        file2.close()

    def CBC_make_encrypted_file(self, key):
        encryptedData = RSA.encrypt_CBC(self.fullImageData,key)
        file2 = open("./encrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(encryptedData)
        file2.close()

    def CBC_make_decrypted_file(self, key):
        decryptedData = RSA.decrypt_CBC(self.fullImageData + self.GAP2,key)
        file2 = open("./decrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(decryptedData)
        file2.close()

    def PCBC_make_encrypted_file(self, key):
        encryptedData = RSA.encrypt_PCBC(self.fullImageData,key)
        file2 = open("./encrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(encryptedData)
        file2.close()

    def PCBC_make_decrypted_file(self, key):
        data = self.fullImageData + self.GAP2
        decryptedData = RSA.decrypt_PCBC(data,key)
        file2 = open("./decrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(decryptedData)
        file2.close()




    def ECB_make_encrypted_file2(self, key):

        data = self.fullImageData + self.GAP2
        keySize = key[0].bit_length()
        pubkey = rsa.PublicKey(key[0],key[1])

        keySizeB = int(keySize / 8) 
        blockSizeB = int(keySizeB - 20)

        pad = int(len(data) % blockSizeB)

        for i in range(blockSizeB - pad):
            data = data + b'\x00'

        dataTab = []
        for i in range(int(len(data) / blockSizeB)):
            start = i * blockSizeB
            end = (i + 1) * blockSizeB
            dataTab.append(data[start:end])

        #--------------------- Progres bar window
        #----------------------------------
        # layout the window
        layout = [[sg.ProgressBar(len(dataTab), orientation='h', size=(20, 20),key='progressbar',bar_color=('blue', 'white'))],
                    [sg.Text('  0%',key = 'progress')]]
        # create the window
        window = sg.Window('', layout,keep_on_top = True, finalize = True)
        progress_bar = window['progressbar']
        progress_percent = window['progress']
        i = 0
        #--------------------- Progres bar window
        #----------------------------------

        encryptedData = b''
        for block in dataTab:
            encryptedData = encryptedData + rsa.encrypt(block,pubkey)
            # updating progress bar ----------------------
            prc = int(100 * (i + 1) / len(dataTab))
            progress_percent.update(str(prc) + '%')
            progress_bar.update_bar(i + 1)
            i+=1
            #---------------------------------------------

        file2 = open("./encrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(encryptedData)
        file2.close()
        window.close()

    def ECB_make_decrypted_file2(self, key):


        encryptedData = self.fullImageData + self.GAP2
        keySize = key[0].bit_length()
        privkey = rsa.PrivateKey(key[0],key[1],key[2],key[3],key[4])

        keySizeB = int(keySize / 8)
        blockSizeB = int(keySizeB - 20)

        encryptedDataTab = []
        for i in range(int(len(encryptedData) / keySizeB)):
            start = i * keySizeB
            end = (i + 1) * keySizeB
            encryptedDataTab.append(encryptedData[start:end])

        #--------------------- Progres bar window
        #----------------------------------
        # layout the window
        layout = [[sg.ProgressBar(len(encryptedDataTab), orientation='h', size=(20, 20),key='progressbar',bar_color=('blue', 'white'))],
                    [sg.Text('  0%',key = 'progress')]]
        # create the window
        window = sg.Window('', layout,keep_on_top = True, finalize = True)
        progress_bar = window['progressbar']
        progress_percent = window['progress']
        i = 0
        #--------------------- Progres bar window
        #----------------------------------

        decryptedData = b''
        for block in encryptedDataTab:
            decryptedData = decryptedData + rsa.decrypt(block,privkey)
            # updating progress bar ----------------------
            prc = int(100 * (i + 1) / len(encryptedDataTab))
            progress_percent.update(str(prc) + '%')
            progress_bar.update_bar(i + 1)
            i+=1
            #---------------------------------------------


        file2 = open("./decrypted_file.bmp", "wb")
        self.bfh.writeToFile(file2)
        self.dib.writeToFile(file2)  
        self.write_to_file_color_profile(file2)
        file2.write(decryptedData)
        file2.close()
        window.close()