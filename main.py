import base64
from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
import vtk
from flask import Flask, request, render_template, json, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='templates')
# 解决跨域问题，虽然我也不知道为什么本机调用会有这个报错
CORS(app)


# 定义函数来获取指定粒子的位置信息
def getParticlePositions(filePaths, particleId, xThreshold, yThreshold, zThreshold):
    positions = []
    for filename in filePaths:
        position = getSingleParticlePosition(filename, particleId, xThreshold, yThreshold, zThreshold)
        if position:
            positions.append(position)
    return positions


# 定义函数来获取单个粒子的位置信息
def getSingleParticlePosition(filename, particleId, xThreshold, yThreshold, zThreshold):
    # 创建一个 vtkXMLPolyDataReader 对象
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    # 获取 polydata 和粒子数据
    polydata = reader.GetOutput()
    points = polydata.GetPoints()
    particles = polydata.GetPointData().GetArray("Particle_ID")

    # 检查粒子数组是否为空
    if particles is not None:
        # 遍历所有粒子
        for i in range(polydata.GetNumberOfPoints()):
            if particles.GetValue(i) == particleId:
                position = points.GetPoint(i)
                x, y, z = position
                if xThreshold[0] is not None and yThreshold[0] is not None and zThreshold[0] is not None:
                    # 检查位置是否在阈值范围内
                    if xThreshold[0] <= x <= xThreshold[1] and \
                            yThreshold[0] <= y <= yThreshold[1] and \
                            zThreshold[0] <= z <= zThreshold[1]:
                        return position
                else:
                    return position
        # 如果没有找到匹配的粒子，返回 None
        return None
    else:
        return None


# 画出粒子的轨迹
def plotParticleTrajectory(positions):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = [pos[0] for pos in positions]
    y = [pos[1] for pos in positions]
    z = [pos[2] for pos in positions]

    ax.plot(x, y, z, marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    # 本地展示
    # plt.show()
    # 使用当前时间生成文件名
    currentTime = datetime.now().strftime('%Y%m%d%H%M%S')
    # 本地保存的位置
    fileName = 'image_' + currentTime + '.png'
    filePath = f'F:/vtp/vtp/{fileName}'
    # 保存图像到本地路径以及IO流里面
    plt.savefig(filePath, format='png')
    imgBuf = BytesIO()
    plt.savefig(imgBuf, format='png')
    imgBuf.seek(0)
    plt.close(fig)
    imgBase64 = base64.b64encode(imgBuf.getvalue()).decode('utf-8')
    imgStrings = [fileName, imgBase64]
    return imgStrings


@app.route('/getPositions', methods=['POST'])
def getResult():
    particleId = float(request.form.get('particle_id'))
    xThreshold = json.loads(request.form.get('x_threshold'))
    yThreshold = json.loads(request.form.get('y_threshold'))
    zThreshold = json.loads(request.form.get('z_threshold'))
    filePaths = json.loads(request.form.get('filePaths'))
    # 读取一系列的vtp文件并获取特定粒子的位置信息
    particle_positions = getParticlePositions(filePaths, particleId, xThreshold, yThreshold, zThreshold)
    if particle_positions:
        # 画图
        imgStrings = plotParticleTrajectory(particle_positions)
    return jsonify({'fileName': imgStrings[0], 'imgBase64': imgStrings[1]})


@app.route('/')
def index():
    return render_template('form.html')


# 傻逼Flask自动找favicon不然报错
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(debug=True, port=2887)
