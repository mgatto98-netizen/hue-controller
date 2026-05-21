from beautifulhue.api import Bridge
from colormath.color_objects import RGBColor
from time import sleep

    while True:
    from pprint import pprint
    color_set = colors_from_cam()
    pprint(color_set)

    for item in color_set:
        print "Getting the color"
        pprint(item)
        time_length = item[0] # prominence
        red, green, blue = item[1] # colors
        #Set a lights attributes based on RGB colors.
        rgb_color = RGBColor(red,green,blue)
        xyz_color = rgb_color.convert_to('xyz', target_rgb='cie_rgb')
        xyz_x = xyz_color.xyz_x
        xyz_y = xyz_color.xyz_y
        xyz_z = xyz_color.xyz_z
        resource = {
            'which':3,
            'data':{
            'state':{'on':True,
                     'xy':[xyz_x, xyz_y],
                         'transitiontime': 1,
                     'bri': 255}
            }
        }
        bridge.light.update(resource)
        print "sleeping"
        sleep(1)
    sleep(2)
    print "taking another picture."

