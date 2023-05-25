from flask import Flask, render_template
import csv

app = Flask(__name__)


@app.route('/')
def anc():
    return render_template('index.html', items=items, sum8=sum8, sum9=sum9, county=sk, num=sv,date=date,date_sum=date_sum,county_items=county_items )


# 读取文件
def reader_file():
    items = []
    filename ='E:\\bk\Learning\数据库\豆瓣TOP100爬虫数据可视化与分析\\film_info.csv'
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i in reader:
            items.append(i)
    f.close()
    return items


# 读数据
items = reader_file()
# 统计个评分电影数量
sum9, sum8 = 0, 0
for i in items:
    if float(i[2]) >= 9:
        sum9 += 1
    else:
        sum8 += 1

# 上映日期与电影数量
date_list,date,date_sum = [],[],[]
date_dict = {}
for i in items:
    date_list.append(i[4])
date_list.sort()
for i in date_list:
    date_dict[f'{i}'] = date_list.count(i)
for k,v in date_dict.items():
    date.append(k)
    date_sum.append(v)

# 统计上映地区
count_county, sk, sv = [], [], []
county_items = {}
for i in items:
    i[3] = i[3].split(' ')
    for w in i[3]:
        count_county.append(w)
        county_items[f'{w}'] = count_county.count(w)
for k, v in county_items.items():
    sk.append(k)
    sv.append(v)
print(county_items)

if __name__ == '__main__':
    app.run(debug=True)
