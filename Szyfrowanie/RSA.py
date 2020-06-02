import math
import numpy as np
import Crypto.Util.number as num
import Crypto.Random.random as rand
import PySimpleGUI as sg

padding = 50
possibleKeySize = (256,512,1024,2048,4096)

def generate_key(keySize):
    p = q = n = 0
    tmp = int(keySize / 2)

    while n.bit_length() != keySize :
        p = num.getPrime(tmp)
        q = num.getPrime(tmp)
        while p == q:
            q = num.getPrime(tmp)
        n = p * q

    fi = (p - 1) * (q - 1)
    subsize = 17
    e = 65537
    while NWD(e,fi) != 1:
        e = num.getPrime(subsize)

    d = num.inverse(e,fi)

    check_key((n,e,d))
    return n,e,d, p, q

def check_key(key):
    for i in key:
        if i == None:
            return False
    n = key[0]
    e = key[1]
    d = key[2]
    m = 42
    c = pow(m,e,n)
    m2 = pow(c,d,n)
    if m != m2:
        return False
    return True

def NWD(a,b):
    if b > a:
        a,b = b,a
    while b != 0:    
        c = a % b
        a = b
        b = c
    return a


# ------------------- EBC ----------------------------
def encrypt_ECB(data, publicKey): 
    n = publicKey[0]
    e = publicKey[1]
    keySize = n.bit_length()
    keySizeB = int(keySize / 8) 
    blockSizeB = int(keySizeB - padding)

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
    window = sg.Window('', layout, finalize = True)
    progress_bar = window['progressbar']
    progress_percent = window['progress']
    i = 0
    #--------------------- Progres bar window
    #----------------------------------

    encryptedData = b''
    for block in dataTab:
        m = int.from_bytes(block,'big')
        c = pow(m,e,n)
        encryptedData = encryptedData + c.to_bytes(keySizeB,'big')
        # updating progress bar ----------------------
        prc = int(100 * (i + 1) / len(dataTab))
        progress_percent.update(str(prc) + '%')
        progress_bar.update_bar(i + 1)
        i+=1
        #---------------------------------------------
        
    
    window.close()
    return encryptedData

def decrypt_ECB(encryptedData, privateKey): 
    
    n = privateKey[0]
    keySize = n.bit_length()
    d = privateKey[2]
    keySizeB = int(keySize / 8)
    blockSizeB = int(keySizeB - padding)

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
    window = sg.Window('', layout, finalize = True)
    progress_bar = window['progressbar']
    progress_percent = window['progress']
    i = 0
    #--------------------- Progres bar window
    #----------------------------------

    decryptedData = b''
    for block in encryptedDataTab:
        c = int.from_bytes(block,'big')

        m = pow(c,d,n)
        decryptedData = decryptedData + m.to_bytes(blockSizeB,'big')
        # updating progress bar ----------------------
        prc = int(100 * (i + 1) / len(encryptedDataTab))
        progress_percent.update(str(prc) + '%')
        progress_bar.update_bar(i + 1)
        i+=1
        #---------------------------------------------
    window.close()
    return decryptedData
# ------------------- EBC ----------------------------


# ------------------- CBC ----------------------------
def encrypt_CBC(data,publicKey):
    n = publicKey[0]
    e = publicKey[1]
    keySize = n.bit_length()
    keySizeB = int(keySize / 8) 
    blockSizeB = int(keySizeB - padding)

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
    window = sg.Window('', layout, finalize = True)
    progress_bar = window['progressbar']
    progress_percent = window['progress']
    i = 0
    #--------------------- Progres bar window
    #----------------------------------

    f = open('./e.txt','w')
    iv = rand.getrandbits(blockSizeB * 8)
    encryptedDataTab = []
    encryptedDataTab.append(iv.to_bytes(keySizeB,'big'))
    for block in dataTab:
        m = int.from_bytes(block,'big')
        m = m ^ iv
        f.write(str(m) + '\t')
        c = pow(m,e,n)
        iv = c
        f.write(str(c) + '\n')
        encryptedDataTab.append(c.to_bytes(keySizeB,'big'))
        # updating progress bar ----------------------
        prc = int(100 * (i + 1) / len(dataTab))
        progress_percent.update(str(prc) + '%')
        progress_bar.update_bar(i + 1)
        i+=1
        

    f.close()
    encryptedData = b''
    for block in encryptedDataTab:
        encryptedData = encryptedData + block
    
    window.close()
    return encryptedData

def decrypt_CBC(encryptedData,privateKey):
    n = privateKey[0]
    keySize = n.bit_length()
    d = privateKey[2]
    keySizeB = int(keySize / 8)
    blockSizeB = int(keySizeB - padding)

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
    window = sg.Window('', layout, finalize = True)
    progress_bar = window['progressbar']
    progress_percent = window['progress']
    i = 0
    #--------------------- Progres bar window
    #----------------------------------

    f = open('./d.txt','w')
    iv = int.from_bytes(encryptedDataTab.pop(0),'big')
    decryptedDataTab = []
    for block in encryptedDataTab:
        c = int.from_bytes(block,'big')
        f.write(str(c) + '\t')
        m = pow(c,d,n)
        m = m ^ iv
        iv = c
        f.write(str(m) + '\n')
        decryptedDataTab.append(m.to_bytes(blockSizeB,'big'))
        # updating progress bar ----------------------
        prc = int(100 * (i + 1) / len(encryptedDataTab))
        progress_percent.update(str(prc) + '%')
        progress_bar.update_bar(i + 1)
        i+=1
        #---------------------------------------------
        
    f.close()
    decryptedData = b''
    for block in decryptedDataTab:
         decryptedData = decryptedData + block

    window.close()
    return decryptedData
#
# ------------------- CBC ----------------------------


# ------------------- PCBC ---------------------------
#
def encrypt_PCBC(data,publicKey):
    n = publicKey[0]
    e = publicKey[1]
    keySize = n.bit_length()
    keySizeB = int(keySize / 8) 
    blockSizeB = int(keySizeB - padding)

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
    window = sg.Window('', layout, finalize = True)
    progress_bar = window['progressbar']
    progress_percent = window['progress']
    i = 0
    #--------------------- Progres bar window
    #----------------------------------

    f = open('./e.txt','w')
    iv = rand.getrandbits(blockSizeB * 8)
    encryptedDataTab = []
    encryptedDataTab.append(iv.to_bytes(keySizeB,'big'))
    for block in dataTab:
        m = int.from_bytes(block,'big')
        m_copy = m
        m = m ^ iv
        f.write(str(m) + '\t')
        c = pow(m,e,n)
        iv = c ^ m_copy
        f.write(str(c) + '\n')
        encryptedDataTab.append(c.to_bytes(keySizeB,'big'))
        # updating progress bar ----------------------
        prc = int(100 * (i + 1) / len(dataTab))
        progress_percent.update(str(prc) + '%')
        progress_bar.update_bar(i + 1)
        i+=1
        #---------------------------------------------
        

    f.close()
    encryptedData = b''
    for block in encryptedDataTab:
        encryptedData = encryptedData + block
    
    window.close()
    return encryptedData

def decrypt_PCBC(encryptedData,privateKey):
    n = privateKey[0]
    keySize = n.bit_length()
    d = privateKey[2]
    keySizeB = int(keySize / 8)
    blockSizeB = int(keySizeB - padding)

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
    window = sg.Window('', layout, finalize = True)
    progress_bar = window['progressbar']
    progress_percent = window['progress']
    i = 0
    #--------------------- Progres bar window
    #----------------------------------

    f = open('./d.txt','w')
    iv = int.from_bytes(encryptedDataTab.pop(0),'big')
    decryptedDataTab = []
    for block in encryptedDataTab:
        c = int.from_bytes(block,'big')
        f.write(str(c) + '\t')
        m = pow(c,d,n)
        m = m ^ iv
        iv = c ^ m
        f.write(str(m) + '\n')
        decryptedDataTab.append(m.to_bytes(blockSizeB,'big'))
        # updating progress bar ----------------------
        prc = int(100 * (i + 1) / len(encryptedDataTab))
        progress_percent.update(str(prc) + '%')
        progress_bar.update_bar(i + 1)
        i+=1
        #---------------------------------------------
        
    f.close()
    decryptedData = b''
    for block in decryptedDataTab:
         decryptedData = decryptedData + block

    window.close()
    return decryptedData
#
# ------------------- PCBC ---------------------------



def save_key_as_file(n,e,d,p,q):
    keySize = n.bit_length()
    file = open('./key.txt','w')
    file.write('RSA KEY ( ' + str(keySize) + ' bit)')
    file.write('\n---BEGIN MODULE---\n')
    file.write(format(n,'x'))
    file.write('\n---END MODULE---\n')
    file.write('---BEGIN PUBLIC KEY---\n')
    file.write(format(e,'x'))
    file.write('\n---END PUBLIC KEY---\n')
    file.write('---BEGIN PRIVATE KEY---\n')
    file.write(format(d,'x'))
    file.write('\n---END PRIVATE KEY---\n')
    file.write('---BEGIN P---\n')
    file.write(format(p,'x'))
    file.write('\n---END P---\n')
    file.write('---BEGIN Q---\n')
    file.write(format(q,'x'))
    file.write('\n---END Q---\n')
    file.close()


def read_key_from_file(filename):
    
        f = open(filename,'r')
        fileData = f.read()
        f.close()
        if fileData.find('RSA KEY') == -1:
            return False
        fileData = fileData.split('\n')

        n = int(fileData[2],16)
        e = int(fileData[5],16)
        d = int(fileData[8],16)
        r = int(fileData[11],16)
        q = int(fileData[14],16)

        if n.bit_length() not in possibleKeySize:
               return False
        
        if not check_key((n,e,d)):
            return False
        return (n,e,d, r, q)


################################################################
# KEY GENERATOR WINDOW
def key_generator():

    layout = [[sg.Button('Generate Keys')],
              [sg.Combo(possibleKeySize,default_value='1024',readonly=True, key = '-KEY SIZE-')],
              [sg.Multiline(size = (60,7),disabled = True,tooltip = 'Module', key = '-MODULE-')],
              [sg.Multiline(size = (60,7),disabled = True,tooltip = 'Public key',key = '-PUBLIC KEY-')],
              [sg.Multiline(size = (60,7),disabled = True,tooltip = 'Private key',key = '-PRIVATE KEY-')],
              [sg.Button('Save as file')]]

    window = sg.Window('Key Generator', layout, size = (500,500), auto_size_text = True, text_justification='center', resizable = True)

    keyGenerated = False
    
    while True:
        event, values = window.read()
        if event in (None, 'Quit'):	
            break
        if event in ('Generate Keys'):
            keySize = values['-KEY SIZE-']
            (n,e,d,p,q) = generate_key(keySize)
            window['-MODULE-'].update(format(n,'x'))
            window['-PUBLIC KEY-'].update(format(e,'x'))
            window['-PRIVATE KEY-'].update(format(d,'x'))
            keyGenerated = True

        if event in ('Save as file'):
            if not keyGenerated:
                sg.popup('Key in not generated')
            else:
                save_key_as_file(n,e,d,p,q)
                sg.popup('File saved as key.txt')


    window.close()

# KEY GENERATOR WINDOW
################################################################