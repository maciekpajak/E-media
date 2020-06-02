class RGBA:
    red = 0
    green = 0
    blue = 0
    alpha = 0

    def __init__(self,red,green,blue,alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def color_to_string_RGBA(self):
        return str(self.red.to_bytes(1,'big').hex() + 
                   self.green.to_bytes(1,'big').hex() + 
                   self.blue.to_bytes(1,'big').hex() + 
                   self.alpha.to_bytes(1,'big').hex())

    def color_to_bytes_RGBA(self):
        return self.red.to_bytes(1,'big') + self.green.to_bytes(1,'big') + self.blue.to_bytes(1,'big') + self.alpha.to_bytes(1,'big')

    def color_to_bit(self):
        if self.red > 127 and self.green > 127 and self.blue > 127:
            return 'x'
        else:
            return ' '
                 
