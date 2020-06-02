from FileData import FileData
import os
import PySimpleGUI as sg
from PIL import Image


def main():

    fileLoaded = False

    sg.theme('DarkAmber')

    menu_def = [['File', 'Load'],
                ['Image',['Display','Meta data','DFT 2D']],
                ['Edit', 'Anonymization'],
                ['Help'],
                ['About','Quit']
                 ]

    filename = None

    layout = [[sg.Menu(menu_def)],[sg.Image(filename, key = '-IMAGE-')]]

    # Create the Window
    window = sg.Window('E-media', layout, size = (500,500), auto_size_text = True, text_justification='center', resizable = True)

    
    while True:
        event, values = window.read()
        if event in (None, 'Quit'):	
            break
        if event in ('Load'):
            print('Load file :')
            filename = sg.popup_get_file('Please enter a file name')
            
            if filename  == None:
                continue
            print(filename)
            
            if not os.path.isfile(filename):
                print('Error! File doesn\'t exist')
                
                sg.popup_error('File doesn\'t exist!',keep_on_top = True)
            else:
                if filename.find('.bmp') == -1 and filename.find('.BMP') == -1:
                    print('Error! Only bmp extension accepted')
                    
                    sg.popup_error('Only bmp extension accepted')
                else:
                    file = open(filename, "rb")
                    print('Loading file... Please wait ')
                    
                    fileData = FileData()
                    if not fileData.load(file):
                        print('Error! Something wrong with file ')
                        
                        sg.popup_error('Something wrong with file')
                    else:
                        print('Succes! File loaded ')
                        
                        Image.open(filename).save('tmp.png')
                        window['-IMAGE-'].update('tmp.png')
                        fileLoaded = True
                        sg.popup('Succes!',keep_on_top = True,)
        if event in ('Display'):
            print('Display image: ')
            if fileLoaded:
                fileData.display_image()
                print('\tSucces! ')
            else:
                print('\tError! File not loaded ')
                sg.popup_error('File is not loaded!')
            

        if event in ('Meta data'):	
            print('Display meta data: ')
            if fileLoaded:
                fileData.display_meta_data()
                print('\tSucces! ')
            else:
                print('\tError! File not loaded ')
                sg.popup_error('File is not loaded!')
            

        if event in ('DFT 2D'):	
            print('Display DFT 2D: ')
            if fileLoaded:
                fileData.dft()
                print('\tSucces! ')
            else:
                print('\tError! File not loaded ')
                sg.popup_error('File is not loaded!')
            

        if event in ( 'Anonymization'):
            print('Anonymization: ')
            if fileLoaded:
                filename2 = "./anonym.bmp"
                file2 = open(filename2, "wb")
                fileData.anonym()
                fileData.writeToFile(file2)
                print('\tSucces! ')
                sg.popup('Succes! File created!')
                file2.close()
            else:
                print('\tError! File not loaded ')
                sg.popup_error('File is not loaded!')
            

    if fileLoaded:
        file.close()
    os.remove('tmp.png')

    window.close()
        
 
        
if __name__ == "__main__":
    # execute only if run as a script
    main()