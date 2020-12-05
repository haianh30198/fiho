import pandas as pd
import numpy as np
from slugify import slugify, Slugify, UniqueSlugify
from alive_progress import alive_bar
from recommend.convert_5_properties import *
from recommend.places_nearby import donePlaces, convertNumber


def createFileData(data_path, vector_data_path):
    # Dữ liệu thô ban đầu lúc mới craw
    dataRaw = pd.read_csv(data_path)

    # Xử lý trùng lập (duplicates)
    dataDup = dataRaw.drop_duplicates(
        subset=['Title', 'Price', 'Area', 'Phone'], keep='first').reset_index(drop=True)

    # lấy ra các thuộc tính cần dùng
    data = dataDup[['ID', 'Price', 'Area',
                    'Bedrooms', 'Floors', 'Direction', 'Address']]

    # Sao chép data để xử lý
    dataProcess = data.copy()

    # Lấy quận ra từ địa chỉ
    # B1 - phân tách địa chỉ theo ','
    rowData = len(dataProcess.index)

    districtList = ['Ninh Kiều', 'Cái Răng', 'Bình Thủy', 'Ô Môn',
                    'Thốt Nốt', 'Vĩnh Thạnh', 'Thới Lai', 'Cờ Đỏ', 'Phong Điền']

    addressData = dataProcess['Address']

    addresses = []  # Mảng chứa tất cả các quận đã tách
    for i in range(rowData):
        addresses.append("Không rõ")

    for addInData in range(0, rowData):
        for dis in districtList:
            if(slugify(addressData[addInData], to_lower=True).find(slugify(dis, to_lower=True)) != -1):
                addresses[addInData] = dis

            # B2 - thêm cột và lưu giá trị các quận tương ứng
    dataProcess['District'] = addresses

    # B3 - đổi các quận thành số để dễ sử dụng
    dataProcess['District'] = dataProcess['District'].str.replace('Ninh Kiều', '1').str.replace(
        'Cái Răng', '2').str.replace('Bình Thủy', '3').str.replace('Ô Môn', '4').str.replace('Thốt Nốt', '5').str.replace('Vĩnh Thạnh', '6').str.replace('Thới Lai', '7').str.replace('Cờ Đỏ', '8').str.replace('Phong Điền', '9').str.replace('Không rõ', '10')

    # Ép kiểu cho số của quận
    for i in range(len(data.index)):
        dataProcess['District'].values[i] = int(
            dataProcess['District'].values[i])

    # Thay đổi các thuộc tính về dạng số
    dataProcess = changeProperties(dataProcess)

    # Chuẩn hóa giá
    priceTemp = []
    for i in dataProcess['Price']:
        priceTemp.append(i)
    priceDF = convertPrice(changePrice(priceTemp))

    # Chuẩn hóa diện tích
    areaTemp = []
    for i in dataProcess['Area']:
        areaTemp.append(i)
    areaDF = convertArea(areaTemp)

    # Chuẩn hóa số phòng ngủ
    bedroomsTemp = []
    for i in dataProcess['Bedrooms']:
        bedroomsTemp.append(i)
    bedroomsDF = convertBedrooms(bedroomsTemp)

    # Chuẩn hóa số tầng
    floorsTemp = []
    for i in dataProcess['Floors']:
        floorsTemp.append(i)
    floorsDF = convertFloors(floorsTemp)

    # Chuẩn hóa hướng nhà
    directionsTemp = []
    for i in dataProcess['Floors']:
        directionsTemp.append(i)
    directionsDF = convertDirections(directionsTemp)

    # Nối 5 thuộc tính lại
    propertiesDF = pd.concat(
        [priceDF, areaDF, bedroomsDF, floorsDF, directionsDF], axis=1)

    # Lấy địa điểm và chuẩn hóa về dạng số
    placesTemp = []
    with alive_bar(len(dataProcess['Address'].index)) as bar:  # Show process
        for i in dataProcess['Address']:
            placesTemp.append(donePlaces(i))
            bar()  # Show process
    placesDF = convertNumber(placesTemp)

    # Lấy ID và quận của các items
    idAndDistrict = dataProcess[['ID', 'District']].copy()

    # Nối địa điểm lân cận với 5 thuộc tính
    df = pd.concat(
        [idAndDistrict, propertiesDF, placesDF], axis=1)

    # Lưu thành file csv
    df.to_csv(vector_data_path, index=False,
              header=True, encoding='utf-8-sig')
    print('Đã xử lý và tạo file dữ liệu gợi ý thành công...')
