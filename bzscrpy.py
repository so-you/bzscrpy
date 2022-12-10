from lib2to3.pgen2 import driver
import time
from selenium import webdriver
import xlwt
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 创建chrome驱动
driver = webdriver.Chrome(executable_path='/Users/warrior/opt/chromedriver')
WAIT = WebDriverWait(driver, 10)
driver.set_window_size(1400, 900)
# 搜索关键字
key_words = "梅西 阿根廷"

# 点击搜索
def first_search(key_words):
    print('开始搜索' + key_words)
    try:
        # 打开网址
        driver.get('https://www.bilibili.com/')

        # 取得浏览器中的搜索框 并输入查询关键字
        input = WAIT.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='nav-search-content']/input[@class='nav-search-input']")))
        input.send_keys(key_words)
        # 点击查询按钮
        submit = WAIT.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='nav-search-btn']")))
        submit.click()

        # 选中第二个标签页
        all_h = driver.window_handles
        driver.switch_to_window(all_h[1])

        # 读取搜索页面数据
        get_html()

        # 取最大页码
        maxbtn = WAIT.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='vui_pagenation--btns']//button[last()-1]")))
        return int(maxbtn.text)
    except TimeoutException as e:
        print(e)
        return first_search()

# 页面读取
def get_html():
    print('页面读取中......')
    # 等待页面加载完成(判断是否有下一页按钮)
    WAIT.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@class='vui_pagenation--btns']//button[contains(text(), '下一页')]")))

    html = driver.page_source
    print('页面读取完成......')

    # 抓取所需的数据并存到结果集中
    read_to_data(html)


vlist = []

# 抓取数据
def read_to_data(html):
    soup = BeautifulSoup(html, 'lxml')
    vidos = soup.find(class_='video-list').find_all(class_='bili-video-card')

    global vlist

    for item in vidos:
        # 标题
        title = item.find(
            "h3", class_="bili-video-card__info--tit").get('title')
        # 链接
        link = item.find("a", class_="").get('href')
        link = "https://" + link
        # 播放数
        view_num = item.find(
            "span", class_="bili-video-card__stats--item").span.string
        # 弹幕数
        danmu = item.find_all(
            "span", class_="bili-video-card__stats--item")[1].span.string
        # up主
        author = item.find(
            "span", class_="bili-video-card__info--author").string
        # 发布日期
        datee = item.find("span", class_="bili-video-card__info--date").string
        datee = datee.strip()[1:]

        print(title + " " + link + " " + view_num)
        vlist.append([title, link, view_num, danmu, author, datee])

## 下一页
def next_page(page):
    print('点击下一页: ' + str(page))
    try:
        time.sleep(1)
        # 点击下一页
        nextbtn = WAIT.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='vui_pagenation--btns']//button[contains(text(), '下一页')]")))
        nextbtn.click()

        # 读取页面
        get_html()
    except TimeoutException as e:
        print(e)
        driver.refresh()
        return next_page(page)


index = 1

# 保单数据到Excel
def save_to_excel(vlist):
    print('最后保存数据到Excel中......')

    if len(vlist):
        # 创建excle
        wb = xlwt.Workbook(encoding='utf-8', style_compression=0)

        sheet = wb.add_sheet('b站搜索结果', cell_overwrite_ok=True)
        sheet.write(0, 0, '序号')
        sheet.write(0, 1, '名称')
        sheet.write(0, 2, '链接')
        sheet.write(0, 3, '观看次数')
        sheet.write(0, 4, '弹幕数')
        sheet.write(0, 5, '作者')
        sheet.write(0, 6, '发布时间')

        global index

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


## 入口函数
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

    # 保存数据到Excel
    save_to_excel(vlist)