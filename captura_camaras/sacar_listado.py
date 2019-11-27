from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# formato CSV:
# ID_Camera, URL, Video/Still, Long, Lat, Status
# 0001, http://informo.munimadrid.es/cameras/Camara06303.jpg, S, 45.19,41.32, 0
#  0  , 1                                                   , 2, 3    , 4   , 5
# Status:
# 0 -> ok
# 100 ->

input_file = 'CCTV.kml'

tree = ET.parse(input_file)

root = tree.getroot()

output = ''

for pl in root[0].findall('{http://earth.google.com/kml/2.2}Placemark'):
    # print (pl[0].text)
    text = pl[0].text
    soup = BeautifulSoup(text, "html.parser")

    url = soup.img["src"]

    url = url.split('?')[0]
    coordinates = (pl[3][1].text)[:-4]
    id = url[43:-4]

    output += id + ',' + url + ',S,' + coordinates + ',0' + '\n'

print(output)

with open('lista_camaras.csv', 'w') as f:
    f.write(output)
