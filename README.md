# Python抓取B站关于"卡塔尔 世界杯"视频数据
## 分析
### 一、步骤
1. 打开B站，输入搜索关键字，点击查询跳转到搜索结果页面
2. 读取页面信息，并抓取所需数据，然后点击下一页
3. 循环上面过程直至最后一页。

> 数据： 标题、播放量、弹幕数、UP主、发布时间

### 二、技术
Python + selenium + beautifulsoup + xlwt

命令pip list 检查下面包是否已经安装，没有安装可以使用下面命令进行安装，我的是Pip3
``` python
pip3 install selenium==3.8.0 ## 4.0版本之后不支持plantomJs
pip3 install beautifulsoup4
pip3 install lxml
pip3 install xlwt
```

安装chrome驱动，先查看chrome浏览器版本，找到对应的版本号(最接近自己的)，下载，然后解压到任意目录即可。
![[Pasted image 20221210105724.png]]
chrome驱动下载地址：
https://registry.npmmirror.com/binary.html?path=chromedriver/

## 代码示例

### 1、打开B站
``` python
# 创建chrome浏览器驱动
driver = webdriver.Chrome(executable_path = '/Users/warrior/opt/chromedriver')
# 打开网址
driver.get('https://www.bilibili.com/')
```

### 2、点击首页搜索并返回页码
```python
# 取得浏览器中的搜索框 并输入查询关键字
input = WAIT.until(EC.presence_of_element_located((By.XPATH,"//div[@class='nav-search-content']/input[@class='nav-search-input']")))
input.send_keys(key_words)

# 点击查询按钮
submit = WAIT.until(EC.element_to_be_clickable((By.XPATH,"//div[@class='nav-search-btn']")))
submit.click()

# 选中第二个标签页
all_h = driver.window_handles
driver.switch_to_window(all_h[1])

## 取最大页码
maxbtn = WAIT.until(EC.presence_of_element_located((By.XPATH, "//div[@class='vui_pagenation--btns']//button[last()-1]")))
return int(maxbtn.text)
```

### 3、页面加载并读取
```python
# 等待页面加载完成(判断是否有下一页按钮)
WAIT.until(EC.presence_of_element_located((By.XPATH, "//div[@class='vui_pagenation--btns']//button[contains(text(), '下一页')]")))

# 获得页面源代码
html = driver.page_source
```

### 4、bs获取页面中数据
```python
soup = BeautifulSoup(html, 'lxml')
# 得到视频list
vidos = soup.find(class_='video-list').find_all(class_='bili-video-card')
# 全局list变量，用于存储抓取的数据
global vlist

for item in vidos:
	# 取标题
	title = item.find("h3",class_="bili-video-card__info--tit").get('title')
	# 取视频链接
	link = item.find("a", class_="").get('href')
	link = "https://" + link
	# 播放数
	view_num = item.find("span",class_="bili-video-card__stats--item").span.string
	# 弹幕数
	danmu = item.find_all("span",class_="bili-video-card__stats--item")[1].span.string
	# UP主
	author = item.find("span", class_="bili-video-card__info--author").string
	# 日期
	datee = item.find("span",class_="bili-video-card__info--date").string
	datee = datee.strip()[1:]
	print(title + " " + link + " " + view_num)
	# 将数据放入到vlist中
	vlist.append([title, link, view_num, danmu, author, datee])
```

### 5、点击下一页
```python
# 取得下一页按钮
nextbtn = WAIT.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='vui_pagenation--btns']//button[contains(text(), '下一页')]")))
# 点击
nextbtn.click()
```

### 6、保存数据到Excel
``` python
# 创建excel
wb = xlwt.Workbook(encoding='utf-8', style_compression=0)

sheet = wb.add_sheet('b站搜索结果',cell_overwrite_ok=True)
sheet.write(0,0,'序号')
sheet.write(0,1,'名称')
sheet.write(0,2,'链接')
sheet.write(0,3,'观看次数')
sheet.write(0,4,'弹幕数')
sheet.write(0,5,'作者')
sheet.write(0,6,'发布时间')

global index
# 遍历并且填入数据
for m in vlist:
	sheet.write(index, 0, index)
	sheet.write(index, 1, m[0])
	sheet.write(index, 2, m[1])
	sheet.write(index, 3, m[2])
	sheet.write(index, 4, m[3])
	sheet.write(index, 5, m[4])
	sheet.write(index, 6, m[5])
	index = index + 1

# 保存输出Excel 文件
wb.save(key_words + "b站搜索结果.xlsx")

```

### 7、入口函数
``` python
if __name__ == '__main__':
	try:
		# 打开页面并搜索，返回最大页码
		total = first_search(key_words)
		# 循环
		for i in range(2, total+1):
			# 点击下一页
			next_page(i)
	except:
		print("异常")
	finally:
		# 关闭浏览器
		driver.close()
	## 保存数据到Excel
	save_to_excel(vlist)
```


## 结果

### 结果如图
分别搜索了"卡塔尔 世界杯" 和"梅西 阿根廷"，生成了两个Excel文件，可以修改变量 key_words 检索B站任意数据结果
![[Pasted image 20221210193048.png]]
### 问题
1. 主要是XPath取页面元素的问题，取不到页面元素，多检查是否漏(多)括号。
2. 读不到页面元素，可能是网络加载慢导致的，一：可以time.sleep(1) 1秒一下试试；二：重新运行试试。
3. B站有反爬机制，UI有可能升级更新，程序报错找不到对应html元素，这个只能事先说明：2022-12-10日的代码


## 完整代码

Github: https://github.com/BraveChi/bzscrpy.git


# 评论里面分享代码和教程



1. WebDriveWait类
[selenium 之WebDriveWait类的等待机制](https://blog.csdn.net/biggbang/article/details/121511531)

2. 各浏览器驱动下载

| 浏览器  | 驱动下载链接                                                          | 
| ------- | --------------------------------------------------------------------- |
| Chrome  | https://sites.google.com/a/chromium.org/chromedriver/downloads   https://registry.npmmirror.com/binary.html?path=chromedriver/     |
| Edge    | https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ |
| Firefox | https://github.com/mozilla/geckodriver/releases                       |
| Safari  | https://webkit.org/blog/6900/webdriver-support-in-safari-10/          |

