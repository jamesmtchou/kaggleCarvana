from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

class Colors(object):
	class Color(object):
		def __init__(self, value):
			self.value = value

		def __str__(self):
			return "%s : %s" % (self.__class__.__name__, self.value)

	class Red(Color): pass
	class Blue(Color): pass
	class Green(Color): pass
	class Yellow(Color): pass
	class White(Color): pass
	class Gray(Color): pass
	class Black(Color): pass
	class Pink(Color): pass
	class Teal(Color): pass

class ColorWheel(object):
    def __init__(self, rgb):
        r, g, b = rgb

        self.rgb = (Colors.Red(r), Colors.Green(g), Colors.Blue(b), )
	
    def estimate_color(self):
        dominant_colors = self.get_dominant_colors()
        total_colors = len(dominant_colors)
        if total_colors == 1:
            return dominant_colors[0]
        elif total_colors == 2:
            color_classes = [x.__class__ for x in dominant_colors]
            if Colors.Red in color_classes and Colors.Green in color_classes:
                return Colors.Yellow(dominant_colors[0].value)
            elif Colors.Red in color_classes and Colors.Blue in color_classes:
                return Colors.Pink(dominant_colors[0].value)
            elif Colors.Blue in color_classes and Colors.Green in color_classes:
                return Colors.Teal(dominant_colors[0].value)
        elif total_colors == 3:
            if dominant_colors[0].value > 200:
                return Colors.White(dominant_colors[0].value)
            elif dominant_colors[0].value > 100:
                return Colors.Gray(dominant_colors[0].value)
            else:
                return Colors.Black(dominant_colors[0].value)
        else:
            print ("Dominant Colors : %s" % dominant_colors)
	
    def get_dominant_colors(self):
        max_color = max([x.value for x in self.rgb])
        return [x for x in self.rgb if x.value >= max_color * .85]

def img_to_array(img, data_format=None):
    """Converts a PIL Image instance to a Numpy array.
    # Arguments
        img: PIL Image instance.
        data_format: Image data format.
    # Returns
        A 3D Numpy array.
    # Raises
        ValueError: if invalid `img` or `data_format` is passed.
    """
    if data_format is None:
        data_format = 'channels_last'#K.image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format: ', data_format)
    # Numpy array x has format (height, width, channel)
    # or (channel, height, width)
    # but original PIL image has format (width, height, channel)
    x = np.asarray(img, dtype='float32')
    if len(x.shape) == 3:
        print "my shape is 3"
        if data_format == 'channels_first':
            x = x.transpose(2, 0, 1)
    elif len(x.shape) == 2:
        print "my shape is 2"
        if data_format == 'channels_first':
            x = x.reshape((1, x.shape[0], x.shape[1]))
        else:
            x = x.reshape((x.shape[0], x.shape[1], 1))
    else:
        raise ValueError('Unsupported image shape: ', x.shape)
    return x

def process_image(image):
    image_color_quantities = {}
    width, height = image.size
    width_margin = int(width - (width * .65))
    height_margin = int(height - (height * .75))
    for x in range(width_margin, width - width_margin, 4):
        for y in range(height_margin, height - height_margin):
            r, g, b = image.getpixel((x, y))
            key = "%s:%s:%s" % (r, g, b, )
            key = (r, g, b, )
            image_color_quantities[key] = image_color_quantities.get(key, 0) + 1

    total_assessed_pixels = sum([v for k, v in image_color_quantities.items() if v > 10])
    strongest_color_wheels = [(ColorWheel(k), v / float(total_assessed_pixels) * 100, ) for k, v in image_color_quantities.items() if v > 10]

    final_colors = {}
    
    st_color = ''
    strong = 0

    for color_wheel, strength in strongest_color_wheels:
        color = color_wheel.estimate_color()
        final_colors[color.__class__] = final_colors.get(color.__class__, 0) + strength
            
    for color, strength in final_colors.items():
        #print ("%s - %s" % (color.__name__, strength, ))
        if strong<strength:
            strong=strength
            st_color = color.__name__

    #image.show()
    return st_color

if __name__ == '__main__':
    import pandas as pd
    from tqdm import tqdm
    import os
    
    meta = pd.read_csv('../../data/metadata.csv')[:2000]
    uids = meta['id']
    
    test = '../../train/'
    print "meta is: ", type(meta)
    
    colors = []
    i = 0
    for car in tqdm(uids, miniters=10):#path = ''
        if os.path.isfile(test+car+'_05.jpg') :
            path=test         
            image = Image.open(path+car+'_05.jpg')
            x = img_to_array(image)
            print "numpy image is: ", x.shape
            plt.imshow(x)
            #color = process_image(image)
            #colors.append(color)
            i=i+1
            #print "is is ", i
            if i==1:
                break
    #meta['color'] = colors
    print "colors are ", colors
    
    meta.to_csv('metadata2.csv', index=False)