from FileData import FileData
import os
import PySimpleGUI as sg
from PIL import Image
import RSA
import binascii as bina


def main():

    fileLoaded = False

    sg.theme('SystemDefault')

    menu_def = [['File',['Open','---', 'Exit']],
                ['Image',['Display','Meta data','DFT 2D']],
                ['Edit', 'Anonymization'],
                ['RSA', ['Key Generator', 
                         'Encrypt File', ['ECB - encrypt', 'CBC - encrypt', 'PCBC - encrypt'], 
                         'Decrypt File', ['ECB - decrypt', 'CBC - decrypt', 'PCBC - decrypt']]],
                ['RSA2',['ECB2 - encrypt','ECB2 - decrypt']],
                ['Help']]

    filename = None
    fileData = None

    layout = [[sg.Menu(menu_def)],[sg.Image(filename, key='-IMAGE-')]]

    # Create the Window
    window = sg.Window('E-media', layout, size = (500,500), auto_size_text = True, text_justification='center', resizable = True)

    
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:	
            break
        if event == 'Open':
            filename = sg.popup_get_file('Please enter a file name')
            if filename == None:
                continue
            if not os.path.isfile(filename):
                sg.popup_error('File doesn\'t exist!',keep_on_top = True)
            else:
                if filename.find('.bmp') == -1 and filename.find('.BMP') == -1:
                    sg.popup_error('Only bmp extension accepted')
                else:
                    file = open(filename, "rb")
                    
                    fileData = FileData()
                    if not fileData.load(file):
                        
                        sg.popup_error('Something wrong with file')
                    else:
                        Image.open(filename).save('tmp.png')
                        window['-IMAGE-'].update('tmp.png')
                        fileLoaded = True

        if event == 'Display':
            if fileLoaded:
                fileData.display_image()
                print('\tSucces! ')
            else:
                sg.popup_error('File is not loaded!')
            
        if event == 'Meta data':	
            if fileLoaded:
                fileData.display_meta_data()
            else:
                sg.popup_error('File is not loaded!')
            

        if event == 'DFT 2D':	
            if fileLoaded:
                fileData.dft()
            else:
                sg.popup_error('File is not loaded!')
            

        if event == 'Anonymization':
            if fileLoaded:
                file2 = open("./anonym.bmp", "wb")
                try:
                    fileData.anonym()
                    fileData.writeToFile(file2)
                except:
                    sg.popup_error("Error! Anonymizaton failed")
                sg.popup('Succes! File created!')
                file2.close()
            else:
                sg.popup_error('File is not loaded!')
            
        if event == 'Key Generator':
            RSA.key_generator()

#----------------- Encrypting types ---------------------
        if event == 'ECB - encrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'E'
            type = 'ECB'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './encrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot encrypt")

        if event == 'CBC - encrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'E'
            type = 'CBC'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './encrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot encrypt")

        if event == 'PCBC - encrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'E'
            type = 'PCBC'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './encrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot encrypt")
        if event == 'ECB2 - encrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'E'
            type = 'EECB2'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './encrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot encrypt")

#------------------ Decrypting types ----------------------------
        if event == 'ECB - decrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'D'
            type = 'ECB'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './decrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot decrypt")

        if event == 'CBC - decrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'D'
            type = 'CBC'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './decrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot decrypt")

        if event == 'PCBC - decrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'D'
            type = 'PCBC'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './decrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot decrypt")

        if event == 'ECB2 - decrypt':
            if not fileLoaded: 
                sg.popup_error('File is not loaded!')
                continue
            mode = 'D'
            type = 'DECB2'
            try:
                if(crypto(mode, type, fileLoaded, fileData, window)):
                    fileData = load_and_display_file(window, './decrypted_file.bmp')
            except:
                sg.popup_error("Error! Cannot decrypt")

    if fileLoaded:
        file.close()
    if os.path.isfile('tmp.png'):
        os.remove('tmp.png')
    window.close()
# main end --------------------------------------------------------        

def load_and_display_file(window, filename):
    file = open(filename, "rb")
    fileData = FileData()
    fileData.load(file)
    Image.open(filename).save('tmp.png')
    window['-IMAGE-'].update('tmp.png')
    return fileData


def crypto(mode, type, fileLoaded, fileData, window):
    if fileLoaded:
        # check if default key file exist
        if os.path.isfile('./key.txt'):
            answer = sg.popup_yes_no('Key found in file: key.txt. Do you want to use this key?',keep_on_top = True)
        key = None   
        # key loaded not from key.file
        if answer == None or answer == 'No':
            filename = sg.popup_get_file('Please enter a key file name')
            if filename != None:
                if not os.path.isfile(filename):
                    sg.popup_error('File doesn\'t exist!',keep_on_top = True)
                    return
                else:
                    key = RSA.read_key_from_file(filename)
            else:
                return
        # key loaded from key.file
        elif answer == 'Yes':
            key = RSA.read_key_from_file('./key.txt')
        else:
            return False

        if key:   

            file = None
            # encryption mode
            if(mode == 'E'):
                if(type == 'ECB'):
                    fileData.ECB_make_encrypted_file(key)
                if(type == 'CBC'):
                    fileData.CBC_make_encrypted_file(key)
                if(type == 'PCBC'):
                    fileData.PCBC_make_encrypted_file(key)
                if(type == 'EECB2'):
                    fileData.ECB_make_encrypted_file2(key)

             # decryption mode
            if(mode == 'D'):
                if(type == 'ECB'):
                    fileData.ECB_make_decrypted_file(key)
                if(type == 'CBC'):
                    fileData.CBC_make_decrypted_file(key)
                if(type == 'PCBC'):
                    fileData.PCBC_make_decrypted_file(key)
                if(type == 'DECB2'):
                    fileData.ECB_make_decrypted_file2(key)
            return True

        else:
            sg.popup('No keys!')
            return False

    # file not loaded error
    else: 
        sg.popup_error('File is not loaded!')


if __name__ == "__main__":
    main()