from flask import Flask, request, jsonify, url_for, render_template, redirect, flash, send_file
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
import pytz
from sklearn.metrics.pairwise import cosine_similarity
from recommend.data_of_user import newData
from recommend.convert_5_properties import priority
from recommend.places_nearby import locationFromAddress
from recommend.data_of_system import createFileData
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)

# Dữ liệu để gợi ý
dataRaw = pd.read_csv("./data/raw/BDSraw.csv")
# Dữ liệu để tính sim
system = pd.read_csv("./data/vector/BDSvector.csv")
# location
location = pd.read_csv('./data/location/location.csv')
# Lọc dữ liệu theo quận

# Định dạng tên file


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
    systemDistrict = priority(price, 'price', priceUp, systemDistrict)
    systemDistrict = priority(area, 'area', areaUp, systemDistrict)
    systemDistrict = priority(bedrooms, 'bedrooms', bedroomsUp, systemDistrict)
    systemDistrict = priority(floors, 'floors', floorsUp, systemDistrict)
    systemDistrict = priority(direction, 'directions',
                              directionUp, systemDistrict)

    # Data người dùng nhập
    user = newData(price, area, bedrooms, floors, direction, placesNearBy)
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

    dataResult = pd.merge(dataRaw, dataResult, on=['ID'])
    dataResult = dataResult[['ID', 'Title', 'Price', 'Area',
                             'Bedrooms', 'Floors', 'Direction', 'Address', 'District', 'Images', 'Phone', 'Description', 'Similar']]

    # Sắp xếp kết quả theo độ tương tự
    dataResult = dataResult.sort_values(by='Similar', ascending=False)

    # Reset index
    dataResult = dataResult.reset_index()
    del dataResult['index']

    return dataResult.head()


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route("/", methods=['GET', 'POST'])
def index():
    result = "map"
    data = "empty"
    lenData = 0
    warning = "p hidden"
    titleMap = ""
    district = 1
    price = 0
    priceUp = 1
    floors = 0
    floorsUp = 1
    area = 0
    areaUp = 1
    bedrooms = 0
    bedroomsUp = 1
    direction = 0
    directionUp = 1
    placesNearby = "Nhà hàng, quán cà phê, công viên"
    locationAll = []

    for i in range(0, len(location.index)):
        locationAll.append([location.iloc[i][0], location.iloc[i][1]])

    lengthLocation = len(locationAll)

    if(request.method == 'POST'):
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

        print(placesNearby)
        from tabulate import tabulate
        try:
            rs = recommend(int(district), int(price), int(priceUp), float(area), int(areaUp), int(bedrooms), int(
                bedroomsUp), int(floors), int(floorsUp), int(direction), int(directionUp), placesNearby)
            print("===========================================================================TOP 5 GỢI Ý TỐT NHẤT===========================================================================\n")
            print(tabulate(rs[['Title', 'Price', 'Area', 'Bedrooms', 'Floors', 'Direction', 'Similar']], headers=[
                '#', 'Tiêu đề bán nhà', 'Giá', 'Diện tích', 'Phòng ngủ', 'Tầng', 'Hướng', 'ĐTT'], tablefmt="grid"))
            print("\n========================================================================END - TOP 5 GỢI Ý TỐT NHẤT========================================================================\n")
            data = rs.values.tolist()

            lenData = len(data)

            result = "empty"
            titleMap = "title-map"
        except:
            warning = "script"

    # Lưu giá trị khi submit
    districtSelected = ""

    if(district == '1'):
        districtSelected = 0
    if(district == '2'):
        districtSelected = 1
    if(district == '3'):
        districtSelected = 2
    if(district == '4'):
        districtSelected = 3
    if(district == '5'):
        districtSelected = 4
    if(district == '6'):
        districtSelected = 5
    if(district == '7'):
        districtSelected = 6
    if(district == '8'):
        districtSelected = 7
    if(district == '9'):
        districtSelected = 8

    areaSelected = ""

    if(area == '0'):
        areaSelected = 0
    if(area == '25'):
        areaSelected = 1
    if(area == '40'):
        areaSelected = 2
    if(area == '60'):
        areaSelected = 3
    if(area == '85'):
        areaSelected = 4
    if(area == '125'):
        areaSelected = 5
    if(area == '175'):
        areaSelected = 6
    if(area == '250'):
        areaSelected = 7
    if(area == '350'):
        areaSelected = 8
    if(area == '750'):
        areaSelected = 9
    if(area == '1200'):
        areaSelected = 10

    priceSelected = ""

    if(price == '0'):
        priceSelected = 0
    if(price == '250000000'):
        priceSelected = 1
    if(price == '650000000'):
        priceSelected = 2
    if(price == '900000000'):
        priceSelected = 3
    if(price == '2000000000'):
        priceSelected = 4
    if(price == '4000000000'):
        priceSelected = 5
    if(price == '6000000000'):
        priceSelected = 6
    if(price == '8500000000'):
        priceSelected = 7
    if(price == '15000000000'):
        priceSelected = 8
    if(price == '25000000000'):
        priceSelected = 9
    if(price == '50000000000'):
        priceSelected = 10

    floorsSelected = ""

    if(floors == '0'):
        floorsSelected = 0
    if(floors == '1'):
        floorsSelected = 1
    if(floors == '2'):
        floorsSelected = 2
    if(floors == '3'):
        floorsSelected = 3
    if(floors == '4'):
        floorsSelected = 4
    if(floors == '5'):
        floorsSelected = 5
    if(floors == '6'):
        floorsSelected = 6
    if(floors == '7'):
        floorsSelected = 7
    if(floors == '8'):
        floorsSelected = 8
    if(floors == '9'):
        floorsSelected = 9
    if(floors == '10'):
        floorsSelected = 10

    bedroomsSelected = ""

    if(bedrooms == '0'):
        bedroomsSelected = 0
    if(bedrooms == '1'):
        bedroomsSelected = 1
    if(bedrooms == '2'):
        bedroomsSelected = 2
    if(bedrooms == '3'):
        bedroomsSelected = 3
    if(bedrooms == '4'):
        bedroomsSelected = 4
    if(bedrooms == '5'):
        bedroomsSelected = 5
    if(bedrooms == '6'):
        bedroomsSelected = 6
    if(bedrooms == '7'):
        bedroomsSelected = 7
    if(bedrooms == '8'):
        bedroomsSelected = 8
    if(bedrooms == '9'):
        bedroomsSelected = 9
    if(bedrooms == '10'):
        bedroomsSelected = 10

    directionSelected = ""

    if(direction == '0'):
        directionSelected = 0
    if(direction == '1'):
        directionSelected = 1
    if(direction == '2'):
        directionSelected = 2
    if(direction == '3'):
        directionSelected = 3
    if(direction == '4'):
        directionSelected = 4
    if(direction == '5'):
        directionSelected = 5
    if(direction == '6'):
        directionSelected = 6
    if(direction == '7'):
        directionSelected = 7
    if(direction == '8'):
        directionSelected = 8

    # END - Lưu giá trị khi submit

    return render_template('index2.html', result=result, locationAll=locationAll, lengthLocation=lengthLocation, data=data, lenData=lenData, warning=warning, district=int(district), price=int(price), dataRaw=dataRaw.values.tolist(), districtSelected=districtSelected, areaSelected=areaSelected, priceSelected=priceSelected, floorsSelected=floorsSelected, bedroomsSelected=bedroomsSelected, directionSelected=directionSelected, priceUp=priceUp, areaUp=areaUp, floorsUp=floorsUp, bedroomsUp=bedroomsUp, directionUp=directionUp, placesNearby=placesNearby, titleMap=titleMap)


@app.route("/detail/<id>")
def detail(id):
    for i in range(len(dataRaw.index)):
        if(dataRaw.iloc[i][0] == id):
            detail = dataRaw.iloc[i]

    latA, longA = locationFromAddress(
        detail.values[7])  # Lấy kinh vĩ độ từ địa chỉ

    detail = detail.copy()

    detail['longitude'] = longA
    detail['latitude'] = latA
    # print(type(detail[4]))
    return render_template('detail.html', detail=detail)


# Xây dưng trang admin


@app.route("/admin")
def admin():
    conn = sqlite3.connect("./database/fiho.db")
    userQuery = "SELECT COUNT(*) FROM users"
    userCursor = conn.execute(userQuery)
    for user in userCursor:
        userResult = user[0]
    conn.close()
    return render_template('admin/index.html', userResult=userResult, dataRaw=dataRaw, recommendAmount=len(dataRaw.index))


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

# Thu thập dữ liệu BDSVN


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
            MAX_PAGE = 1

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

                    # Chạy qua các item lấy title của các item
                    items = lists.find_elements_by_class_name('product-item')
                    for item in items:
                        # title = item.find_element_by_class_name('wrap-plink')
                        # titles.append(title.text)
                        titles.append(item.get_attribute('prid'))

                    count = 1
                    # Chạy qua các title và click vào trang tương ứng
                    for title in titles:
                        element = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//div[@prid='"+title+"']"))
                        )

                        element.click()

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
                atCreate = str(timeA) + " " + str(timeB)

                conn = sqlite3.connect("./database/fiho.db")

                # Chuyển các tập tin cũ thành hết hạn trước khi thêm vào thêm mới
                conn.execute(
                    "UPDATE file_system SET status = 0 WHERE name LIKE '%BatDongSan-%'")
                conn.commit()

                paramsSys = (str(nameFileBDS),
                             str(vector_nameFileBDS), str(atCreate), str(1))

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
            MAX_PAGE = 1

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
                atCreate = str(timeA) + " " + str(timeB)

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


@app.route("/admin/files/system/active")
def system_active():
    try:
        # Mảng chứa các đường link file dữ liệu
        fileAll = []

        # Kết nôi CSDL
        conn = sqlite3.connect("./database/fiho.db")
        query = "SELECT name FROM file_system WHERE status = 1"
        cursor = conn.execute(query)
        for filesName in cursor:
            fileAll.append(filesName)  # file gốc
        conn.commit()
        conn.close()

        # Mảng chứa các dataframe sau khi đọc
        rawFiles = []

        for files in fileAll:
            rawFiles.append(pd.read_csv(files[0]))

        # Nối tất cả các file trong mảng lại
        mergeRawFiles = pd.concat(rawFiles, sort=False, ignore_index=True)

        # Loại bỏ các nhà trùng nhau
        mergeRawFiles = mergeRawFiles.drop_duplicates(
            subset=['Title', 'Price', 'Area', 'Phone'], keep='first').reset_index(drop=True)

        # Tạo tên cho tập gợi mới
        nameRecommend = './data/raw/' + \
            format_file_name('recommned')+'.csv'
        nameVectorRecommend = './data/vector/' + \
            format_file_name('recommned')+'.csv'

        # Lưu thành file csv cho thập dữ liệu
        mergeRawFiles.to_csv(nameRecommend, index=False,
                             header=True, encoding='utf-8-sig')

        # Tạo file vector
        createFileData(nameRecommend, nameVectorRecommend)

        flash('Đã khởi tạo lại tập dữ liệu gợi ý cho hệ thống!')
        return redirect(url_for('admin'))
    except:
        flash('Chưa có file nào được sử dụng!')
        return redirect(url_for('file_system'))

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


@app.route("/admin/files/addition/add")  # Hiện thị file
def add_file_addition():
    return render_template('admin/add-file-addition.html')

# Đánh giá hệ Thống


@app.route("/rating")
def rating():
    return render_template('rating.html')


if __name__ == "__main__":
    app.run(debug=True)
