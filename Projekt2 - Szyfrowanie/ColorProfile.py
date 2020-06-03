

class ColorProfile:
    """description of class"""
    data = []

    def load(self,file,offset,colorTableSize):
        if colorTableSize == 0:
            return False
        else:
            file.seek(offset,0)
            for i in range(int(colorTableSize)):
                self.data.append(file.read(4))
                #file.read(1)
            return True


    def disp(self):
        print("COLOR PROFILE:")
        if len(data) == 0:
            print("\tNo color profile")
        else:
            i = 1
            print('\t#| R | G | B | aplha')
            for word in self.data:
                print("\tColor " + str(i) + " = ", str(word.hex()) )
                i = i + 1

    def writeToFile(self,file):
          for word in self.data:
              file.write(word)