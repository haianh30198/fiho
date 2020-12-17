from flask import Flask, request, jsonify, url_for, render_template, redirect, flash, send_file
import pandas as pd
import sqlite3
import random
import math
import json
import os
from datetime import datetime
from tabulate import tabulate
from slugify import slugify, Slugify, UniqueSlugify
import pytz
from sklearn.metrics.pairwise import cosine_similarity
from recommend.data_of_user import newData
from recommend.convert_5_properties import priority
from recommend.places_nearby import locationFromAddress
from recommend.data_of_system import createFileData
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Vị trị lưu file upload của thêm file gợi ý
UPLOAD_FOLDER = 'data/rawAddition/'
ALLOWED_EXTENSIONS = {'xlxs', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)

# Giá trị mặc định
# Dữ liệu để gợi ý
dataRaw = pd.read_csv("./data/raw/BDSraw.csv")
# Dữ liệu để tính sim
system = pd.read_csv("./data/vector/BDSvector.csv")
# location
location = pd.read_csv('./data/location/location.csv')

try:
    # Lấy thông tin dữ liệu gợi ý chính
    conn = sqlite3.connect("./database/fiho.db")
    fileRecommendQuery = "SELECT name, vector_name, location FROM file_recommend WHERE ID = (SELECT MAX(ID) FROM file_recommend)"
    fileRecommendCursor = conn.execute(fileRecommendQuery)

    for fileRecommend in fileRecommendCursor:
        # Dữ liệu để gợi ý
        dataRaw = pd.read_csv(fileRecommend[0])
        # Dữ liệu để tính sim
        system = pd.read_csv(fileRecommend[1])
        # location
        location = pd.read_csv(fileRecommend[2])
    conn.close()
except:
    # Dữ liệu để gợi ý
    dataRaw = pd.read_csv("./data/raw/BDSraw.csv")
    # Dữ liệu để tính sim
    system = pd.read_csv("./data/vector/BDSvector.csv")
    # location
    location = pd.read_csv('./data/location/location.csv')

# Định dạng tên file có ngày giờ


def format_file_name(name):
    vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
    datetime_vietnam = datetime.now(vietnam)
    gio = datetime_vietnam.strftime("%H:%M:%S").split(":")
    ngay = str(datetime_vietnam.date()).split('-')
    return (name + "-" + gio[0]+gio[1]+gio[2]+"-"+ngay[2]+ngay[1]+ngay[0])

# Lọc theo quận


def filterDistrict(data, district):
    newData = data[data['District'] == int(district)]
    newData = newData.reset_index()
    del newData['index']
    return newData


def recommend(district, price, priceUp, area, areaUp, bedrooms, bedroomsUp, floors, floorsUp, direction, directionUp, places):
    # Xử lý địa điểm nhập vào của người dùng
    pnbs = places.split(',')
    placesNearBy = []
    for pnb in pnbs:
        placesNearBy.append(pnb.strip())

    # Lọc data theo quận của người dùng
    systemDistrict = filterDistrict(system, district)
    # Sau khi lọc nhân thêm độ ưu tiên của người dùng vào bảng vector
    systemDistrict = priority(price, 'price', priceUp, systemDistrict)
    systemDistrict = priority(area, 'area', areaUp, systemDistrict)
    systemDistrict = priority(bedrooms, 'bedrooms', bedroomsUp, systemDistrict)
    systemDistrict = priority(floors, 'floors', floorsUp, systemDistrict)
    systemDistrict = priority(direction, 'directions',
                              directionUp, systemDistrict)

    # Data người dùng nhập
    user = newData(price, area, bedrooms, floors, direction, placesNearBy)
    # Nhân thêm độ ưu tiên cho các thuộc tính
    user = priority(price, 'price', priceUp, user)
    user = priority(area, 'area', areaUp, user)
    user = priority(bedrooms, 'bedrooms', bedroomsUp, user)
    user = priority(floors, 'floors', floorsUp, user)
    user = priority(direction, 'directions', directionUp, user)

    # print("==============Dữ liệu hệ thống==============\n")
    # print(systemDistrict)
    # print("===========END - Dữ liệu hệ thống===========\n")

    # print("===========Yêu cầu của người dùng===========\n")
    # print(user)
    # print("========END - Yêu cầu của người dùng========\n")

    # Tính độ tương tự
    sim = cosine_similarity(
        systemDistrict.iloc[:, 2:].values.tolist(), user.values.tolist())

    # Sao chép dataframe
    dataResult = filterDistrict(system, district).copy()

    # Thêm cột Similar
    dataResult['Similar'] = sim

    # Nối 2 data theo ID
    dataResult = pd.merge(dataRaw, dataResult, on=['ID'])
    # Lấy ra các thuộc tính cần thiết
    dataResult = dataResult[['ID', 'Title', 'Price', 'Area',
                             'Bedrooms', 'Floors', 'Direction', 'Address', 'District', 'Images', 'Phone', 'Description', 'Similar']]

    # Sắp xếp kết quả theo độ tương tự
    dataResult = dataResult.sort_values(by='Similar', ascending=False)

    # Reset index
    dataResult = dataResult.reset_index()
    del dataResult['index']

    # Loại bỏ phần tử lập
    dataResult = dataResult.drop_duplicates(
        subset=['Title', 'Price', 'Area', 'Phone'], keep='first').reset_index(drop=True)

    return dataResult.head()

# Xử lý các route ko tồn tại trả về trang 404


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

# Trang chủ khi mới tải trang


@app.route("/", methods=['GET', 'POST'])
def index():
    # Hiển thị các địa điểm đang được rao bán trên bản đồ theo dữ liệu location
    locationAll = []

    for i in range(0, len(location.index)):
        locationAll.append([location.iloc[i][0], location.iloc[i][1]])

    lengthLocation = len(locationAll)

    return render_template('index2.html', locationAll=locationAll, lengthLocation=lengthLocation, dataRaw=dataRaw.values.tolist())

# Trang nhận kết quả và dùng ajax hiển thị thay cho bản đồ các địa điểm đang rao bán


@app.route('/result', methods=['GET', 'POST'])
def result():
    data = 0
    lenData = 0
    warning = "hide-warning"
    resultWarning = ""
    district = request.form.get('district')
    price = request.form.get('price')
    priceUp = request.form.get('priceUp')
    area = request.form.get('area')
    areaUp = request.form.get('areaUp')
    floors = request.form.get('floors')
    floorsUp = request.form.get('floorsUp')
    bedrooms = request.form.get('bedrooms')
    bedroomsUp = request.form.get('bedroomsUp')
    direction = request.form.get('direction')
    directionUp = request.form.get('directionUp')
    placesNearby = request.form.get('placesNearby')

    # print(placesNearby)
    try:
        # Nhận các yêu cầu và xử lý đưa ra gợi ý
        rs = recommend(int(district), int(price), int(priceUp), float(area), int(areaUp), int(bedrooms), int(
            bedroomsUp), int(floors), int(floorsUp), int(direction), int(directionUp), placesNearby)
        print("===========================================================================TOP 5 GỢI Ý TỐT NHẤT===========================================================================\n")
        print(tabulate(rs[['Title', 'Price', 'Area', 'Bedrooms', 'Floors', 'Direction', 'Similar']], headers=[
            '#', 'Tiêu đề bán nhà', 'Giá', 'Diện tích', 'Phòng ngủ', 'Tầng', 'Hướng', 'ĐTT'], tablefmt="grid"))
        print("\n========================================================================END - TOP 5 GỢI Ý TỐT NHẤT========================================================================\n")

        # Chuyển dataframe thành dạng list để hiện thị ra giao diện
        data = rs.values.tolist()

        lenData = len(data)
        # print(lenData)

    except:
        warning = ""
        resultWarning = "hide-warning"

    return render_template('result.html', warning=warning, resultWarning=resultWarning, lenData=lenData, data=data)

# Theo dõi lượt click theo session


@app.route('/rating', methods=['GET', 'POST'])
def rating():
    clicked = None
    clicked = request.json

    top = clicked['top']
    sessionTop = clicked['sessionTop']

    conn = sqlite3.connect("./database/fiho.db")

    # Kiểm tra tồn tại session trong csdl chưa
    checkSession = conn.execute(
        "SELECT * FROM rating WHERE session = '"+sessionTop+"'")

    existSesion = ""
    for s in checkSession:
        existSesion = s

    # Nếu tồn tại thì update
    if existSesion:
        if(top == "1"):
            conn.execute(
                "UPDATE rating SET top1 = 1 WHERE session = '"+sessionTop+"'")
        if(top == "2"):
            conn.execute(
                "UPDATE rating SET top2 = 1 WHERE session = '"+sessionTop+"'")
        if(top == "3"):
            conn.execute(
                "UPDATE rating SET top3 = 1 WHERE session = '"+sessionTop+"'")
        if(top == "4"):
            conn.execute(
                "UPDATE rating SET top4 = 1 WHERE session = '"+sessionTop+"'")
        if(top == "5"):
            conn.execute(
                "UPDATE rating SET top5 = 1 WHERE session = '"+sessionTop+"'")

        conn.commit()
    # Ngược lại thì tạo mới
    else:
        paramsSession = (str(sessionTop), str(1))

        if(top == "1"):
            conn.execute(
                "INSERT INTO rating (session, top1) VALUES (?,?)", paramsSession)
        if(top == "2"):
            conn.execute(
                "INSERT INTO rating (session, top2) VALUES (?,?)", paramsSession)
        if(top == "3"):
            conn.execute(
                "INSERT INTO rating (session, top3) VALUES (?,?)", paramsSession)
        if(top == "4"):
            conn.execute(
                "INSERT INTO rating (session, top4) VALUES (?,?)", paramsSession)
        if(top == "5"):
            conn.execute(
                "INSERT INTO rating (session, top5) VALUES (?,?)", paramsSession)

        conn.commit()
    conn.close()
    return clicked

# Trang chi tiết nhà


@app.route("/detail/<id>")
def detail(id):
    # Lọc dữ liệu theo id để đưa ra dòng dữ liệu tương ứng với ngôi nhà
    for i in range(len(dataRaw.index)):
        if(dataRaw.iloc[i][0] == id):
            detail = dataRaw.iloc[i]

    # Lấy kinh vĩ độ từ địa chỉ
    latA, longA = locationFromAddress(detail.values[7])

    detail = detail.copy()

    detail['longitude'] = longA  # Kinh độ
    detail['latitude'] = latA  # Vĩ độ
    # print(type(detail[4]))

    # Lấy ngẫu nhiên 3 nhà khác
    detail1 = ""
    detail2 = ""
    detail3 = ""

    random1 = random.choice(dataRaw['ID'])
    random2 = random.choice(dataRaw['ID'])
    random3 = random.choice(dataRaw['ID'])

    for i in range(len(dataRaw.index)):
        if(dataRaw.iloc[i][0] == random1):
            detail1 = dataRaw.iloc[i]
        if(dataRaw.iloc[i][0] == random2):
            detail2 = dataRaw.iloc[i]
        if(dataRaw.iloc[i][0] == random3):
            detail3 = dataRaw.iloc[i]

    return render_template('detail.html', detail=detail, detail1=detail1, detail2=detail2, detail3=detail3)


# Xây dưng trang admin


@app.route("/admin")
def admin():
    conn = sqlite3.connect("./database/fiho.db")
    userQuery = "SELECT COUNT(*) FROM users"
    userCursor = conn.execute(userQuery)
    for user in userCursor:
        userResult = user[0]

    # Thống kế số lượng quận trong tất cả bản tin hiện tại
    districtList = ['Ninh Kiều', 'Cái Răng', 'Bình Thủy', 'Ô Môn',
                    'Thốt Nốt', 'Vĩnh Thạnh', 'Thới Lai', 'Cờ Đỏ', 'Phong Điền']

    colorList = ["#00876c", "#57a18b", "#8cbcac", "#bed6ce",
                 "#f1f1f1", "#f1c6c6", "#ec9c9d", "#e27076", "#d43d51"]

    rowData = len(dataRaw.index)

    addressData = dataRaw['Address']

    addresses = []  # Mảng chứa tất cả các quận đã tách
    for i in range(rowData):
        addresses.append("Không rõ")

    for addInData in range(0, rowData):
        for dis in districtList:
            if(slugify(addressData[addInData], to_lower=True).find(slugify(dis, to_lower=True)) != -1):
                addresses[addInData] = dis

    dataDis = dataRaw.copy()
    dataDis['District'] = addresses

    # Đếm quận
    def countDistrict(district):
        return sum(dataDis['District'].str.count(district))

    dataCountDistrict = []

    for dis in districtList:
        dataCountDistrict.append(countDistrict(dis))

    # Thống kế lượt click trên kết quả hiển thị
    clickQuery = "SELECT COUNT(session), sum(top1), sum(top2), sum(top3), sum(top4), sum(top5) FROM rating"
    clickCursor = conn.execute(clickQuery)
    for click in clickCursor:
        clickResult = click

    topClick = []
    for i in range(1, 6):
        topClick.append(str(math.ceil(clickResult[i]/clickResult[0]*100)))

    conn.close()
    return render_template('admin/index.html', userResult=userResult, dataRaw=dataRaw, recommendAmount=len(dataRaw.index), dataCountDistrict=dataCountDistrict, districtList=districtList, colorList=colorList, topClick=topClick, clickResult=clickResult)


@app.route("/admin/users")  # Hiển thị thành viên
def show_user():
    conn = sqlite3.connect("./database/fiho.db")
    query = "SELECT * FROM users"
    cursor = conn.execute(query)
    users = []
    for row in cursor:
        users.append(list(row))
    conn.close()
    return render_template('admin/users.html', users=users, lenUsers=len(users))


@app.route("/admin/users/add", methods=['GET', 'POST'])  # Thêm thành viên
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        conn = sqlite3.connect("./database/fiho.db")
        c = conn.cursor()

        # Kiểm tra tài khoản tồn tại
        checkUsername = "root"
        cursorUsername = c.execute(
            "SELECT username FROM users WHERE username='"+username+"'")
        for i in cursorUsername:
            checkUsername = i
        checkUsername = checkUsername[0]

        if(username == checkUsername):
            flash('Tài khoản đã tồn tại !')
            return redirect(url_for('add_user'))
        if(password != password2):
            flash('Nhập lại mật khẩu không khớp !')
            return redirect(url_for('add_user'))
        else:
            params = (str(username), str(password),
                      str(name), str(phone), str(address), str(1))
            cursor = c.execute(
                "INSERT INTO users (username, password, name, phone, address, status) VALUES (?,?,?,?,?,?)", params)
            conn.commit()
            conn.close()

            flash('Thêm nhân viên thành công !')
            return redirect(url_for('show_user'))

    return render_template('admin/add-user.html')


@app.route("/admin/users/edit", methods=['GET', 'POST'])  # Cập nhật thành viên
def update_user():
    return render_template('admin/add-user.html')


@app.route("/admin/users/delete/<id>")  # Xóa thành viên
def delete_user(id):
    conn = sqlite3.connect("./database/fiho.db")
    query = "DELETE FROM users WHERE ID =" + str(id)
    cursor = conn.execute(query)
    conn.commit()
    conn.close()
    flash('Xóa nhân viên thành công !')
    return redirect(url_for('show_user'))

# Quản lý file
# File hệ thống


@app.route("/admin/files/system")  # Hiện thị file
def file_system():
    conn = sqlite3.connect("./database/fiho.db")
    query = "SELECT * FROM file_system"
    cursor = conn.execute(query)
    files = []
    for row in cursor:
        files.append(list(row))
    conn.close()
    return render_template('admin/file-system.html', files=files, lenFiles=len(files))


@app.route("/admin/files/system/detail/<id>")  # Chi tiết file
def detail_file(id):
    # conn = sqlite3.connect("./database/fiho.db")
    # query = "SELECT * FROM file_system WHERE=" + str(id)
    # cursor = conn.execute(query)
    # for row in cursor:
    #     fileResult = row[0]
    # conn.close()
    print(id)
    return render_template('admin/detail-file.html', dataRaw=dataRaw)

# Thu thập dữ liệu


@app.route("/admin/files/system/crawl", methods=['GET', 'POST'])
def system_crawl():
    if request.method == "POST":
        if request.form['crawl-data'] == "BDS":
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import NoSuchElementException
            import pandas as pd
            import uuid

            PATH = "./driver/chromedriver.exe"

            driver = webdriver.Chrome(PATH)

            # chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--no-sandbox')
            # chrome_options.add_argument('--disable-dev-shm-usage')
            # driver = webdriver.Chrome(PATH, chrome_options=chrome_options)

            # PATH = "./driver/phantomjs.exe"
            # driver = webdriver.PhantomJS(PATH)

            # driver.get("https://batdongsan.com.vn/ban-nha-dat-can-tho")

            titles = []  # Mảng lưu các tiêu đề để click link chuyển vào trang đó
            array = []  # Mảng lưu kết quả thông tin cào được 1 trang trước khi append vào object properties

            properties = {
                'ID': [],
                'Title': [],
                'Area': [],
                'Price': [],
                'Floors': [],
                'Bedrooms': [],
                'Direction': [],
                'Address': [],
                'Images': [],
                'Phone': [],
                'Description': []
            }

            MIN_PAGE = 1
            MAX_PAGE = 17

            try:
                for page in range(MIN_PAGE, MAX_PAGE + 1):
                    URL = "https://batdongsan.com.vn/ban-nha-dat-can-tho/p" + \
                        str(page)

                    driver.get(URL)

                    wait = WebDriverWait(driver, 10)

                    # Lấy cha của các items
                    lists = wait.until(
                        EC.presence_of_element_located(
                            (By.ID, "product-lists-web")
                        )
                    )

                    # # Chạy qua các item lấy title của các item
                    # items = lists.find_elements_by_class_name('product-item')
                    # for item in items:
                    #     # title = item.find_element_by_class_name('wrap-plink')
                    #     # titles.append(title.text)
                    #     titles.append(item.get_attribute('prid'))

                    # Chạy qua các item lấy link của các item
                    items = lists.find_elements_by_css_selector(
                        '.product-item .wrap-plink')
                    for item in items:
                        # title = item.find_element_by_class_name('wrap-plink')
                        # titles.append(title.text)
                        titles.append(item.get_attribute('href'))

                    count = 1
                    # Chạy qua các title và click vào trang tương ứng
                    for title in titles:
                        # element = wait.until(
                        #     EC.presence_of_element_located(
                        #         (By.XPATH, "//div[@prid='"+title+"']"))
                        # )

                        # element.click()
                        print(title)

                        driver.get(title)

                        # Tạo ID
                        id = uuid.uuid4()
                        array.append("ID:")
                        array.append(id)
                        # End Tạo ID

                        try:
                            # Lấy hình
                            linkImages = []

                            imageHouse = wait.until(
                                EC.presence_of_element_located(
                                    (By.CLASS_NAME, "swiper-wrapper"))
                            )

                            images = imageHouse.find_elements_by_tag_name(
                                'div')
                            for image in images:
                                link = image.find_element_by_css_selector(
                                    'div img')
                                links = link.get_attribute('src')
                                linkImages.append(links)

                            array.append("Hình:")
                            array.append(linkImages)
                            # End lấy hình
                        except:
                            # Lấy hình
                            linkImages = []

                            linkImages.append(
                                "https://staticfile.batdongsan.com.vn/images/no-image.png")

                            array.append("Hình:")
                            array.append(linkImages)
                            pass

                        # Lấy tiêu đề nhà
                        titleHouse = wait.until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'tile-product'))
                        )
                        array.append('Tiêu đề:')
                        array.append(titleHouse.text)
                        # End lấy điều đề nhà

                        # Lấy thông tin phần trên mô tả
                        header = wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".short-detail-wrap ul"))
                        )

                        items = header.find_elements_by_tag_name('li')
                        for item in items:
                            r1 = item.find_element_by_class_name('sp1')
                            r2 = item.find_element_by_class_name('sp2')
                            array.append(r1.text)
                            array.append(r2.text)
                        # END - Lấy thông tin phần trên mô tả

                        # Lấy thông tin phần ĐẶC ĐIỂM BÂT ĐỘNG SẢN
                        header2 = wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".box-round-grey3"))
                        )

                        items2 = header2.find_elements_by_tag_name('div')
                        for item2 in items2:
                            r3 = item2.find_element_by_class_name('r1')
                            r4 = item2.find_element_by_class_name('r2')
                            array.append(r3.text)
                            array.append(r4.text)
                        # END - Lấy thông tin phần ĐẶC ĐIỂM BÂT ĐỘNG SẢN

                        # Lấy số điện thoại
                        userWrapper = wait.until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'user'))
                        )

                        phone = userWrapper.find_element_by_css_selector(
                            '.phone .phoneEvent')

                        array.append('Điện thoại:')
                        array.append(phone.get_attribute('raw'))
                        # END - Lấy số điện thoại

                        # Lấy mô tả
                        desWrapper = wait.until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'des-product'))
                        )
                        array.append('Mô tả:')
                        array.append(desWrapper.text)
                        # END - Lấy mô tả

                        # Lưu thông tin vào mảng
                        for i in range(len(array)):
                            if(array[i] == 'ID:'):
                                properties['ID'].append(array[i+1])
                            if(array[i] == 'Tiêu đề:'):
                                properties['Title'].append(array[i+1])
                            if(array[i] == 'Mức giá:'):
                                properties['Price'].append(array[i+1])
                            if(array[i] == 'Diện tích:'):
                                properties['Area'].append(array[i+1])
                            if(array[i] == 'Số phòng ngủ:'):
                                properties['Bedrooms'].append(array[i+1])
                            if(array[i] == 'Số tầng:'):
                                properties['Floors'].append(array[i+1])
                            if(array[i] == 'Hướng nhà:'):
                                properties['Direction'].append(array[i+1])
                            if(array[i] == 'Địa chỉ:'):
                                properties['Address'].append(array[i+1])
                            if(array[i] == 'Hình:'):
                                properties['Images'].append(array[i+1])
                            if(array[i] == 'Điện thoại:'):
                                properties['Phone'].append(array[i+1])
                            if(array[i] == 'Mô tả:'):
                                properties['Description'].append(array[i+1])
                        # End - Lưu thông tin vào mảng

                        # Xử lý trường hợp nếu thuộc tính bị thiếu
                        if('Tiêu đề:') not in array:
                            properties['Title'].append('NaN')
                        if('Mức giá:') not in array:
                            properties['Price'].append('NaN')
                        if('Diện tích:') not in array:
                            properties['Area'].append('NaN')
                        if('Số phòng ngủ:') not in array:
                            properties['Bedrooms'].append('NaN')
                        if('Số tầng:') not in array:
                            properties['Floors'].append('NaN')
                        if('Hướng nhà:') not in array:
                            properties['Direction'].append('NaN')
                        if('Địa chỉ:') not in array:
                            properties['Address'].append('NaN')
                        if('Hình:') not in array:
                            properties['Images'].append('NaN')
                        if('Điện thoại:') not in array:
                            properties['Phone'].append('NaN')
                        if('Mô tả:') not in array:
                            properties['Description'].append('NaN')
                        # End - Xử lý trường hợp nếu thuộc tính bị thiếu

                        array.clear()
                        driver.back()

                        print('Xong trang: ', page, '- Quảng cáo thứ: ', count)
                        count += 1
                    count = 1

                    titles.clear()

            finally:
                driver.quit()
                print('ID', len(properties['ID']))
                print('Title', len(properties['Title']))
                print('Area', len(properties['Area']))
                print('Floors', len(properties['Floors']))
                print('Bedrooms', len(properties['Bedrooms']))
                print('Price', len(properties['Price']))
                print('Direction', len(properties['Direction']))
                print('Address', len(properties['Address']))
                print('Images', len(properties['Images']))
                print('Phone', len(properties['Phone']))
                print('Description', len(properties['Description']))

                df = pd.DataFrame(properties, columns=[
                    'ID', 'Title', 'Price', 'Area', 'Bedrooms', 'Floors', 'Direction', 'Address', 'Images', 'Phone', 'Description'])

                nameFileBDS = './data/rawSystem/' + \
                    format_file_name('BatDongSan')+'.csv'

                df.to_csv(nameFileBDS, index=False,
                          header=True, encoding='utf-8-sig')

                vector_nameFileBDS = './data/vectorSystem/' + \
                    format_file_name('vectorBatDongSan')+'.csv'

                createFileData(nameFileBDS, vector_nameFileBDS)

                print(df)

                vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
                timeA = datetime.now(vietnam).strftime("%H:%M:%S")
                timeB = datetime.now(vietnam).date()
                atCreate = str(timeB) + " " + str(timeA)

                conn = sqlite3.connect("./database/fiho.db")

                # Chuyển các tập tin cũ thành hết hạn trước khi thêm vào thêm mới
                conn.execute(
                    "UPDATE file_system SET status = 0 WHERE name LIKE '%BatDongSan-%'")
                conn.commit()

                paramsSys = (str(nameFileBDS), str(
                    vector_nameFileBDS), str(atCreate), str(1))

                cursor = conn.execute(
                    "INSERT INTO file_system (name, vector_name, atCreate, status) VALUES (?, ?, ?, ?)", paramsSys)
                conn.commit()
                conn.close()

        if request.form['crawl-data'] == "BDSVN":
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import NoSuchElementException
            import pandas as pd
            import uuid

            PATH = "./driver/chromedriver.exe"
            driver = webdriver.Chrome(PATH)

            driver.maximize_window()

            # chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--no-sandbox')
            # chrome_options.add_argument('--disable-dev-shm-usage')
            # driver = webdriver.Chrome(PATH, chrome_options=chrome_options)

            # PATH = "./driver/phantomjs.exe"
            # driver = webdriver.PhantomJS(PATH)

            # driver.get("https://batdongsan.com.vn/ban-nha-dat-can-tho")

            titles = []  # Mảng lưu các tiêu đề để click link chuyển vào trang đó
            array = []  # Mảng lưu kết quả thông tin cào được 1 trang trước khi append vào object properties

            properties = {
                'ID': [],
                'Title': [],
                'Area': [],
                'Price': [],
                'Floors': [],
                'Bedrooms': [],
                'Direction': [],
                'Address': [],
                'Images': [],
                'Phone': [],
                'Description': []
            }

            MIN_PAGE = 1
            MAX_PAGE = 3

            URL = "http://www.batdongsan.vn/default.aspx?removedos=true"

            driver.get(URL)

            try:
                for page in range(MIN_PAGE, MAX_PAGE + 1):
                    URL = "http://www.batdongsan.vn/giao-dich/ban-nha-dat-tai-can-tho/pageindex-" + \
                        str(page) + ".html"

                    driver.get(URL)

                    wait = WebDriverWait(driver, 30)

                    # Lấy cha của các items
                    lists = wait.until(
                        EC.presence_of_element_located(
                            (By.ID, "cat_0")
                        )
                    )

                    count = 1
                    # Chạy qua các item lấy title của các item
                    items = lists.find_elements_by_css_selector(' .content1')
                    for item in items:
                        title = item.find_element_by_class_name('P_Title')
                        titles.append(title.text)

                    for title in titles:
                        try:
                            element = wait.until(
                                EC.presence_of_element_located(
                                    (By.LINK_TEXT, title))
                            )
                        except:
                            break

                        # element.click()
                        driver.execute_script("arguments[0].click();", element)

                        # Tạo ID
                        id = uuid.uuid4()
                        array.append("ID:")
                        array.append(id)
                        # End Tạo ID

                        try:
                            # Lấy hình
                            linkImages = []

                            imageHouse = wait.until(
                                EC.presence_of_element_located(
                                    (By.CLASS_NAME, "warp_images"))
                            )

                            images = imageHouse.find_elements_by_css_selector(
                                '.slider-avatar .slider .owl-stage-outer .owl-stage')

                            for image in images:
                                link = image.find_element_by_css_selector(
                                    '.owl-item .box-banner-img .changemedia')
                                links = link.get_attribute('href')
                                linkImages.append(links)

                            array.append("Hình:")
                            array.append(linkImages)
                            # End lấy hình
                        except:
                            array.append("Hình:")
                            array.append(
                                "https://staticfile.batdongsan.com.vn/images/no-image.png")
                            pass

                        try:
                            wrapTitle = WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "#Home1_ctl33_viewdetailproduct .PD_Product .Product_List .wrap"))
                            )
                            titleHome = wrapTitle.find_element_by_css_selector(
                                '.P_Title1 h1')
                            array.append('Tiêu đề:')
                            array.append(titleHome.text)
                        except:
                            array.append('Tiêu đề:')
                            array.append('Cần bán nhà (Tiêu đề lỗi)')

                        header = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "PD_Thongso"))
                        )

                        items = header.find_elements_by_class_name(
                            'details-warp-item')
                        for item in items:
                            r1 = item.find_element_by_tag_name('label')
                            r2 = item.find_element_by_tag_name('span')
                            array.append(r1.text)
                            array.append(r2.text)

                        # Lấy thông tin phần ĐẶC ĐIỂM BÂT ĐỘNG SẢN
                        header2 = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "details-warp-item-attribute"))
                        )

                        items2 = header2.find_elements_by_tag_name('li')
                        for item2 in items2:
                            r3 = item2.find_element_by_class_name(
                                'attributename')
                            r4 = item2.find_element_by_class_name(
                                'attributevalue')
                            array.append(r3.text)
                            array.append(r4.text)
                        # END - Lấy thông tin phần ĐẶC ĐIỂM BÂT ĐỘNG SẢN

                        # Lấy số điện thoại
                        userWrapper = wait.until(
                            EC.presence_of_element_located(
                                (By.ID, 'Home1_ctl27_viewdetailproduct'))
                        )

                        phone = userWrapper.find_element_by_class_name('phone')

                        array.append('Điện thoại:')
                        array.append(phone.text)
                        # END - Lấy số điện thoại

                        # Lấy mô tả
                        desWrapper = wait.until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'PD_Gioithieu'))
                        )
                        array.append('Mô tả:')
                        array.append(desWrapper.text)
                        # END - Lấy mô tả

                        for i in range(len(array)):
                            if(array[i] == 'ID:'):
                                properties['ID'].append(array[i+1])
                            if(array[i] == 'Tiêu đề:'):
                                properties['Title'].append(array[i+1])
                            if(array[i] == 'Giá cả:'):
                                properties['Price'].append(array[i+1])
                            if(array[i] == 'Diện tích:'):
                                properties['Area'].append(array[i+1])
                            if(array[i] == 'Số phòng ngủ'):
                                properties['Bedrooms'].append(
                                    array[i+1] + " (phòng)")
                            if(array[i] == 'Số tầng'):
                                properties['Floors'].append(
                                    array[i+1] + " (tầng)")
                            if(array[i] == 'Hướng nhà'):
                                properties['Direction'].append(array[i+1])
                            if(array[i] == 'Địa chỉ:'):
                                properties['Address'].append(array[i+1])
                            if(array[i] == 'Hình:'):
                                properties['Images'].append(array[i+1])
                            if(array[i] == 'Điện thoại:'):
                                properties['Phone'].append(array[i+1])
                            if(array[i] == 'Mô tả:'):
                                properties['Description'].append(array[i+1])

                        if('Tiêu đề:') not in array:
                            properties['Title'].append('NaN')
                        if('Giá cả:') not in array:
                            properties['Price'].append('NaN')
                        if('Diện tích:') not in array:
                            properties['Area'].append('NaN')
                        if('Số phòng ngủ') not in array:
                            properties['Bedrooms'].append('NaN')
                        if('Số tầng') not in array:
                            properties['Floors'].append('NaN')
                        if('Hướng nhà') not in array:
                            properties['Direction'].append('NaN')
                        if('Địa chỉ:') not in array:
                            properties['Address'].append('NaN')
                        if('Hình:') not in array:
                            properties['Images'].append('NaN')
                        if('Điện thoại:') not in array:
                            properties['Phone'].append('NaN')
                        if('Mô tả:') not in array:
                            properties['Description'].append('NaN')

                        array.clear()
                        driver.back()

                        print('Xong trang: ', page, '- Quảng cáo thứ: ', count)
                        count += 1
                    count = 1

                    titles.clear()

            finally:
                driver.quit()
                print('ID', len(properties['ID']))
                print('Title', len(properties['Title']))
                print('Area', len(properties['Area']))
                print('Floors', len(properties['Floors']))
                print('Bedrooms', len(properties['Bedrooms']))
                print('Price', len(properties['Price']))
                print('Direction', len(properties['Direction']))
                print('Address', len(properties['Address']))
                print('Images', len(properties['Images']))
                print('Phone', len(properties['Phone']))
                print('Description', len(properties['Description']))

                df = pd.DataFrame(properties, columns=[
                    'ID', 'Title', 'Price', 'Area', 'Bedrooms', 'Floors', 'Direction', 'Address', 'Images', 'Phone', 'Description'])

                nameFileBDSVN = './data/rawSystem/' + \
                    format_file_name('BatDongSanVN')+'.csv'

                df.to_csv(nameFileBDSVN, index=False,
                          header=True, encoding='utf-8-sig')

                vector_nameFileBDSVN = './data/vectorSystem/' + \
                    format_file_name('vectorBatDongSanVN')+'.csv'

                createFileData(nameFileBDSVN, vector_nameFileBDSVN)

                print(df)

                vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
                timeA = datetime.now(vietnam).strftime("%H:%M:%S")
                timeB = datetime.now(vietnam).date()
                atCreate = str(timeB) + " " + str(timeA)

                conn = sqlite3.connect("./database/fiho.db")

                # Chuyển các tập tin cũ thành hết hạn trước khi thêm vào thêm mới
                conn.execute(
                    "UPDATE file_system SET status = 0 WHERE name LIKE '%BatDongSanVN-%'")
                conn.commit()

                paramsSys = (str(nameFileBDSVN),
                             str(vector_nameFileBDSVN), str(atCreate), str(1))

                cursor = conn.execute(
                    "INSERT INTO file_system (name, vector_name, atCreate, status) VALUES (?, ?, ?, ?)", paramsSys)
                conn.commit()
                conn.close()

        flash('Đã thu thập dữ liệu xong !')
        return redirect(url_for('file_system'))

    return render_template('admin/system-crawl.html')

# Xóa file


@app.route("/admin/files/system/delete/<id>")  # Hiện thị file thêm từ QTV
def system_detele(id):
    conn = sqlite3.connect("./database/fiho.db")
    query = "SELECT name FROM file_system WHERE ID =" + str(id)
    cursor = conn.execute(
        """SELECT name FROM file_system WHERE ID = (?)""", str(id))
    conn.commit()
    conn.close()
    # conn = sqlite3.connect("./database/fiho.db")

    # queryCheck = "SELECT (name, vector_name) FROM file_system WHERE ID =" + \
    #     str(id)
    # cursorCheck = conn.execute(queryCheck)
    # for filePath in cursorCheck:
    #     if(filePath):
    #         os.remove(filePath)

    # query = "DELETE FROM file_system WHERE ID =" + str(id)
    # cursor = conn.execute(query)
    # conn.commit()
    # conn.close()
    flash('Xóa tệp hệ thống thành công !')
    return redirect(url_for('file_system'))


@app.route("/admin/files/system/download/<filename>", methods=['GET'])
def download_file(filename):
    path = "data/rawSystem/"+filename
    return send_file(path, as_attachment=True)

# Kích hoạt tạo file gợi ý mới bằng cách thủ công


@app.route("/admin/files/system/active")
def system_active():
    # try:
    # Mảng chứa các đường link file dữ liệu
    rawfileAll = []
    vetorFileAll = []

    # Kết nôi CSDL
    conn = sqlite3.connect("./database/fiho.db")
    # Select file hệ thống
    querySystem = "SELECT name, vector_name FROM file_system WHERE status = 1"
    cursorSystem = conn.execute(querySystem)
    # Select file admin thêm vào
    queryAdmin = "SELECT name, vector_name FROM file_addition WHERE status = 1"
    cursorAdmin = conn.execute(queryAdmin)

    for filesNameSystem in cursorSystem:
        rawfileAll.append(pd.read_csv(filesNameSystem[0]))  # file gốc
        vetorFileAll.append(pd.read_csv(filesNameSystem[1]))  # file gốc

    for filesNameAdmin in cursorAdmin:
        rawfileAll.append(pd.read_csv(filesNameAdmin[0]))  # file gốc
        vetorFileAll.append(pd.read_csv(filesNameAdmin[1]))  # file gốc

    # Nối tất cả các file trong mảng lại
    mergeRawFiles = pd.concat(rawfileAll, sort=False, ignore_index=True)
    mergeVectorFiles = pd.concat(
        vetorFileAll, sort=False, ignore_index=True)

    # Lấy vĩ độ kinh độ từ địa chỉ nhà tạo ra map
    createMap = []
    for add in mergeRawFiles['Address']:
        latitude, longitude = locationFromAddress(add)
        createMap.append([longitude, latitude])

    # Chuyển thành dataframe
    dfCreateMap = pd.DataFrame(createMap, columns=['kinhdo', 'vido'])

    # Tạo tên cho tập gợi mới
    nameRecommend = './data/raw/' + \
        format_file_name('recommned')+'.csv'
    nameVectorRecommend = './data/vector/' + \
        format_file_name('recommned')+'.csv'
    mapRecommend = './data/location/' + \
        format_file_name('location')+'.csv'

    # Lưu thành file csv cho thập dữ liệu
    mergeRawFiles.to_csv(nameRecommend, index=False,
                         header=True, encoding='utf-8-sig')
    mergeVectorFiles.to_csv(nameVectorRecommend, index=False,
                            header=True, encoding='utf-8-sig')
    dfCreateMap.to_csv(mapRecommend, index=False,
                       header=True, encoding='utf-8-sig')

    # Định dạng ngày giờ để lưu
    vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
    timeA = datetime.now(vietnam).strftime("%H:%M:%S")
    timeB = datetime.now(vietnam).date()
    atCreate = str(timeB) + " " + str(timeA)

    # Chuyển các tập tin cũ thành hết hạn trước khi thêm vào thêm mới
    conn.execute("UPDATE file_recommend SET status = 0")
    conn.commit()

    paramsSys = (str(nameRecommend),
                 str(nameVectorRecommend), str(mapRecommend), str(atCreate), str(1))

    cursor = conn.execute(
        "INSERT INTO file_recommend (name, vector_name, location, atCreate, status) VALUES (?, ?, ?, ?, ?)", paramsSys)
    conn.commit()
    conn.close()

    flash('Đã khởi tạo lại tập dữ liệu gợi ý cho hệ thống!')
    return redirect(url_for('admin'))
    # except:
    #     flash('Chưa có file nào được sử dụng!')
    #     return redirect(url_for('file_addition'))

# File được thêm bởi QTV


@app.route("/admin/files/addition")  # Hiện thị file thêm từ QTV
def file_addition():
    conn = sqlite3.connect("./database/fiho.db")
    query = "SELECT * FROM file_addition"
    cursor = conn.execute(query)
    files = []
    for row in cursor:
        files.append(list(row))
    conn.close()
    return render_template('admin/file-addition.html', files=files, lenFiles=len(files))

# Upload file


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/admin/files/addition/add", methods=['GET', 'POST'])
def add_file_addition():
    if request.method == 'POST':
        # Lấy trạng thái file khi upload
        active = request.form.get('active')

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Đã có lỗi xảy ra! Thử lại sau !')
            return redirect(url_for('add_file_addition'))
        file = request.files['file']
        if allowed_file(file.filename) != True:
            flash('Tệp sai định dạng!')
            return redirect(url_for('add_file_addition'))
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Không có tệp nào được chọn!')
            return redirect(url_for('add_file_addition'))
        if file and allowed_file(file.filename):

            nameFile = format_file_name('admin-file-upload')+'.csv'
            nameFileADMIN = './data/rawAddition/' + nameFile

            filename = nameFile
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # lưu thông tin file vừa up lên cơ sở dữ liệu
            vector_nameFileADMIN = './data/vectorAddition/' + \
                format_file_name('admin-vector-file-upload')+'.csv'

            # Tạo file vector data từ file raw data đã up
            createFileData(nameFileADMIN, vector_nameFileADMIN)

            vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
            timeA = datetime.now(vietnam).strftime("%H:%M:%S")
            timeB = datetime.now(vietnam).date()
            atCreate = str(timeB) + " " + str(timeA)

            conn = sqlite3.connect("./database/fiho.db")

            if(active == "1"):
                paramsSys = (str(nameFileADMIN),
                             str(vector_nameFileADMIN), str(atCreate), str(1))
            else:
                paramsSys = (str(nameFileADMIN),
                             str(vector_nameFileADMIN), str(atCreate), str(0))

            cursor = conn.execute(
                "INSERT INTO file_addition (name, vector_name, atCreate, status) VALUES (?, ?, ?, ?)", paramsSys)
            conn.commit()
            conn.close()

            flash('Đã tải lên thành công!')
            return redirect(url_for('add_file_addition'))

    return render_template('admin/add-file-addition.html')


@app.route("/admin/rating", methods=['GET', 'POST'])
def admin_rating():
    conn = sqlite3.connect("./database/fiho.db")
    query = "SELECT * FROM rating"
    cursor = conn.execute(query)
    rating = []
    for row in cursor:
        rating.append(list(row))
    conn.close()
    return render_template('admin/rating.html', rating=rating, lenRating=len(rating))


if __name__ == "__main__":
    app.run(debug=True)
