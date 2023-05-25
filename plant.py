import csv
from wordcloud import WordCloud
import jieba
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

def reader_file():
    items = []
    with open('film_info.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i in reader:
            items.append(i)
    f.close()
    return items


items = reader_file()
string = ''
for item in items:
    string = string + item[1]
string = ' '.join(jieba.cut(string))
img = Image.open('./static/image/heart.png')
img_array = np.array(img)
wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path='msyh.ttc'
)
wc.generate_from_text(string)
fig = plt.figure(figsize=(3.5,3.0))
plt.imshow(wc)
plt.margins(0, 0)
plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
plt.axis('off')
# plt.show()
plt.savefig('./static/image/heart_cloud.png')

