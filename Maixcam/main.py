from maix import image, display, app, time, camera, ext_dev, nn, uart,touchscreen
import cv2
import numpy as np
import math
import sys
# axp=ext_dev.axp2101.AXP2101()	#降压使用，默认3300mv，改为2500mv还算稳定，1800mv偶尔可以。
# axp=ext_dev.axp2101.AXP2101()	#降压使用，默认3300mv，改为2500mv还算稳定，1800mv偶尔可以。
# axp.dcdc1(2500)		

# 初始化显示和摄像头
disp = display.Display()
cam = camera.Camera(640, 480, image.Format.FMT_BGR888)  # 使用BGR格式直接兼容OpenCV 640, 480
device = "/dev/ttyS0"
ports = uart.list_devices() # 列出当前可用的串口
serial = uart.UART(device, 115200)
disp.set_backlight(20)


######################################################################
MODE = -1 #-1 (初始化校准模式)  
          # 0 (低功耗待机模式)   
          # 1 (基础三题)  
          # 2 (平面发挥加仿射重叠)  
          # 3 (仿射变换旋转发挥+指定数字指令)
######################################################################

# 测量参数设置（单位：厘米）
KNOWN_DISTANCE = 100      # 已知距离（校准时的物体距离摄像头距离）
KNOWN_WIDTH = 17.0          # 已知物体宽度（A4纸宽度）
KNOWN_HEIGHT = 25.5         # 已知物体高度（A4纸高度）

# focalLength = None          # 摄像头焦距（将通过校准计算得到）
focalLength = 1372          # 摄像头焦距（将通过校准计算得到）实际测量（640*480）
focalLength2 = 1340          # 摄像头焦距（将通过校准计算得到）实际测量（640*480）
Width_value = 2

#################################透视代码参数###################################
# Inner Rect的实际尺寸（厘米）
INNER_RECT_WIDTH_CM = 25.7  # 长边
INNER_RECT_HEIGHT_CM = 17  # 短边

# 透视变换目标尺寸（竖屏：高度 > 宽度）
TARGET_WIDTH = 993  # 竖屏宽度
TARGET_HEIGHT = 1500  # 竖屏高度（大于宽度）

# 参考距离和像素尺寸（已知值）
REF_DISTANCE_CM = 100.0  # 参考距离（厘米）
REF_LONG_PX = 337.5     # 参考距离时长边的像素长度
REF_SHORT_PX = 222.5    # 参考距离时短边的像素长度


# 距离校准参数：当距离为43cm时，inner rect两长边像素和的1/2为250px
CALIBRATION_DISTANCE = 100.0  # 校准距离（cm）
CALIBRATION_PIXEL = 337.5     # 校准像素长度
DISTANCE_CONSTANT = CALIBRATION_DISTANCE * CALIBRATION_PIXEL  # 比例常数（cm·px）

# 长宽比阈值设置（可根据实际情况调节）
ASPECT_RATIO_LOWER = 1.4  # 长宽比下限
ASPECT_RATIO_UPPER = 2.5  # 长宽比上限
##################################################################################

###############################重叠识别参数#############################################
LENGTH_RANGE = [20, 3000]
ACCPT_ANGLE_ERR = 15
PRECITION = 0
ACCPET_SAME_LENGTH_ERR = 20
ANGLE_THRESHOLD = 20
EPSILON = 0.005

########################################################################################


# 形状检测参数（初始值）
params = {
    'canny_th1': 50,
    'canny_th2': 150,
    'outer_rect_area': 16000,       #矩形框阈值
    'inner_rect_area': 1000,       #内部元素最小阈值
    'aspect_ratio': 10,
    'min_shape_area': 200,      # 内部形状最小面积
    'iou_threshold': 0.8,       # 矩形IoU阈值
    'shape_iou_threshold': 0.5 # 内部形状IoU阈值
}

# 初始化全局变量
var1 = 0  # 左侧控制的变量
var2 = 0  # 右侧控制的变量

# 初始化显示
ts = touchscreen.TouchScreen()

# 按键配置参数
button_width = 150  # 按键宽度
button_height = 150  # 按键高度
button_margin = 160  # 按键之间的垂直间距
screen_margin_x = 160  # 左右边距

# 图像尺寸（与摄像头匹配）
img_width, img_height = 640, 480
img_center_x = img_width // 2  # 图像中心X坐标
img_center_y = img_height // 2  # 图像中心Y坐标

# 左侧按键组（控制var1）- 纵向排列
left_col_x = img_center_x - screen_margin_x - button_width
btn_var1_add = [
    left_col_x,
    10,  # 顶部距离
    button_width,
    button_height
]
btn_var1_sub = [
    left_col_x,
    10 + button_height + button_margin,
    button_width,
    button_height
]

# 右侧按键组（控制var2）- 纵向排列，与左侧对称
right_col_x = img_center_x + screen_margin_x
btn_var2_add = [
    right_col_x,
    10,
    button_width,
    button_height
]
btn_var2_sub = [
    right_col_x,
    10 + button_height + button_margin,
    button_width,
    button_height
]

# 初始化YOLO数字检测模型
print("加载YOLO数字检测模型...")
try:
    digit_detector = nn.YOLOv8(model="/root/models/best_int8.mud", dual_buff=True)
    print("YOLO模型加载成功")
    YOLO_ENABLED = False
except Exception as e:
    print(f"YOLO模型加载失败: {e}")
    print("将跳过数字识别功能")
    digit_detector = None
    YOLO_ENABLED = False

# 🔧 九宫格验证调试开关
GRID_DEBUG = True   # 设为False可简化输出，只保留关键验证信息

# 🔧 YOLO数字识别参数配置 - 全局调参变量
YOLO_CONFIDENCE = 0.3       # 置信度阈值 (建议范围: 0.1-0.8)
YOLO_IOU = 0.45             # IoU阈值 (建议范围: 0.3-0.7)
YOLO_DEBUG = True           # 调试模式，显示详细信息



def set_grid_debug(debug_mode):
    """设置九宫格验证调试模式"""
    global GRID_DEBUG
    GRID_DEBUG = debug_mode
    print(f"九宫格调试模式已设置为: {GRID_DEBUG}")
    if GRID_DEBUG:
        print("  将显示详细的索引对应关系验证信息")
    else:
        print("  将使用简化输出模式")

def set_yolo_confidence(confidence):
    """设置YOLO识别的置信度阈值"""
    global YOLO_CONFIDENCE
    YOLO_CONFIDENCE = confidence
    print(f"YOLO置信度阈值已设置为: {YOLO_CONFIDENCE}")

def set_yolo_iou(iou):
    """设置YOLO识别的IoU阈值"""
    global YOLO_IOU
    YOLO_IOU = iou
    print(f"YOLO IoU阈值已设置为: {YOLO_IOU}")

def set_yolo_debug(debug_mode):
    """设置YOLO调试模式"""
    global YOLO_DEBUG
    YOLO_DEBUG = debug_mode
    print(f"YOLO调试模式已设置为: {YOLO_DEBUG}")

print("YOLO数字识别系统已就绪")
print(f"当前参数: 置信度={YOLO_CONFIDENCE}, IoU={YOLO_IOU}, YOLO调试={YOLO_DEBUG}, 九宫格调试={GRID_DEBUG}")
print("调参命令: set_yolo_confidence(0.1~0.8), set_yolo_debug(True/False), set_grid_debug(True/False)")

def update_params(param, value):
    """更新参数值"""
    params[param] = value

isHeadFirstReceive = False
isHeadSecReceive   = False
isModeSet = False
isNumberSet = False
isfinishedOnce = False
Number = -1

def on_received(serial : uart.UART, data : bytes):
    global isfinishedOnce
    global MODE
    global Number
    print(data)
    if len(data) < 5 or data[0] != 0x00 or data[1] != 0xff or data[-1] != 0xfe:
        return None  # 不符合协议格式
    MODE = data[2]

    
    isfinishedOnce = True

serial.set_received_callback(on_received)

def switchToMode0():
    global MODE
    while MODE != 0 :
        if MODE == 0:
            break


def uart_sendCommand(distance: int, width: int) -> int:
    # 参数类型检查
    if not isinstance(distance, int) or not isinstance(width, int):
        raise ValueError("参数必须是整数")
    # 参数范围检查
    if not (0 <= distance <= 65535) or not (0 <= width <= 65535):
        print(f"错误: 参数越界 (distance:{distance}, width:{width})，必须在0-65535范围内")
        return 0
    try:
        # 构造发送数据包
        sendArray = (
            b'\x00' + b'\xFF' + 
            distance.to_bytes(2, 'big') + 
            width.to_bytes(2, 'big') + 
            b'\xFE'
        )
        
        print("发送数据包:")
        print(sendArray)
        
        # 重复发送3次（根据原逻辑）
        for _ in range(3):
            serial.write(sendArray)
            time.sleep_ms(2)
        return 1
    except Exception as e:
        print(f"发送失败: {str(e)}")
        return 0


def preprocess_image(frame):
    """图像预处理增强边缘检测"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)
    blurred = cv2.bilateralFilter(gray_eq, 9, 75, 75)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=1)
    edges = cv2.Canny(thresh, 20, 80)
    return edges, gray_eq

def calculate_shape_features(contour):
    """计算轮廓的几何特征"""
    area = cv2.contourArea(contour)
    if area < 1:
        return 0, 0, 0, 0, 0, 0

    perimeter = cv2.arcLength(contour, True)    # 计算最小外接圆（圆心坐标和半径）
    # 圆形度计算公式：4π×面积 / 周长²（标准圆的圆形度为1）
    circularity = 4 * math.pi * (area / (perimeter**2)) if perimeter > 0 else 0
    # 计算最小外接圆（圆心坐标和半径）
    ((cx, cy), radius) = cv2.minEnclosingCircle(contour)
    circle_area = math.pi * radius**2    # 外接圆面积
    # 圆拟合度：轮廓面积 / 外接圆面积（值越接近1，形状越接近圆）
    circle_fit = area / circle_area if circle_area > 0 else 0
    
    # 凸包分析
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    convexity = area / hull_area if hull_area > 0 else 0
    
    # 椭圆拟合度
    if len(contour) >= 5:
        ellipse = cv2.fitEllipse(contour)
        (center, axes, orientation) = ellipse
        a, b = axes[0]/2, axes[1]/2
        ellipse_area = math.pi * a * b if a > 0 and b > 0 else 0
        ellipse_fit = area / ellipse_area if ellipse_area > 0 else 0
    else:
        ellipse_fit = 0
    
    # 对称性分析
    moments = cv2.moments(contour)
    symmetry = 0
    if moments["m00"] > 0:
        cx, cy = moments["m10"]/moments["m00"], moments["m01"]/moments["m00"]
        distances = [math.hypot(p[0][0]-cx, p[0][1]-cy) for p in contour]
        mean_dist = sum(distances) / len(distances) if distances else 0
        variance = sum((d - mean_dist)**2 for d in distances) / len(distances) if distances else 0
        symmetry = 1 - (variance / (mean_dist**2)) if mean_dist > 0 else 0
    
    
    return circularity, circle_fit, convexity, ellipse_fit, symmetry, area

# 形状识别函数（严格区分矩形和正方形）
def detect_shape(contour):
    area = cv2.contourArea(contour)
    if area < 100:  # 过滤小轮廓
        return "Unknown"
    
    # 计算几何特征
    circularity, circle_fit, convexity, ellipse_fit, symmetry, _ = calculate_shape_features(contour)
    circ_thresh = 0.85   # 圆形度阈值
    conv_thresh = 0.8   # 凸度阈值

    
    # 圆形识别条件：综合圆形度、圆拟合度、椭圆拟合度、对称性和凸度
    is_circle = (
        circularity > circ_thresh and   # 圆形度足够高
        circle_fit > 0.55 and            # 轮廓接近外接圆
        ellipse_fit > 0.8 and           # 轮廓接近椭圆（圆是特殊椭圆）
        symmetry > 0.9 and              # 对称性好
        convexity > conv_thresh         # 凸形（圆是凸形）
    )
    #测量结果
    # circularity 0.8911908382694279
    # circle_fit 0.9353374321604834
    # ellipse_fit 0.9986695941135155
    # symmetry 0.9996902017178512
    # convexity 0.992910808073671
    

    if is_circle:
        #调参用
        # print("---------------------")
        # print("circularity",circularity)
        # print("circle_fit",circle_fit)
        # print("ellipse_fit",ellipse_fit)
        # print("symmetry",symmetry)
        # print("convexity",convexity)
        return "Circle"
    
    # 多边形逼近
    perimeter = cv2.arcLength(contour, True)
    epsilon = 0.02 * perimeter
    approx = cv2.approxPolyDP(contour, epsilon, True)
    sides = len(approx)
    
    # 三角形检测
    if sides == 3:
        angles = []
        for i in range(3):
            p1, p2, p3 = approx[i][0], approx[(i+1)%3][0], approx[(i+2)%3][0]
            v1 = (p1[0]-p2[0], p1[1]-p2[1])
            v2 = (p3[0]-p2[0], p3[1]-p2[1])
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            cross = v1[0]*v2[1] - v1[1]*v2[0]
            angles.append(abs(math.degrees(math.atan2(cross, dot))))
        return "Equilateral Triangle" if all(50 < a < 70 for a in angles) else "Triangle"


    # 正方形/矩形检测（优化判定条件）
    elif sides == 4:
        x, y, w, h = cv2.boundingRect(approx)
        
        # 确保长边比短边，计算比例
        if w > h:
            aspect_ratio = float(w) / h
            long_side, short_side = w, h
        else:
            aspect_ratio = float(h) / w
            long_side, short_side = h, w
        
        # 计算四个角的角度（应接近90度）
        angles = []
        for i in range(4):
            p1, p2, p3 = approx[i][0], approx[(i+1)%4][0], approx[(i+2)%4][0]
            v1 = (p1[0]-p2[0], p1[1]-p2[1])
            v2 = (p3[0]-p2[0], p3[1]-p2[1])
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            cross = v1[0]*v2[1] - v1[1]*v2[0]
            angle = abs(math.degrees(math.atan2(cross, dot)) - 90)  # 与90度的偏差
            angles.append(angle)
        
        # 正方形判定：接近1:1的比例，角度接近90度
        issquare = (
            0.9 <= aspect_ratio <= 1.2 and  # 更严格的正方形比例范围
            all(a < 10 for a in angles) and  # 角度接近90度
            convexity > 0.95
        )
        # print("aspect_ratio:",aspect_ratio)
        # print("convexity:",convexity)
        if issquare:
            print("Square")
            return "Square"
        
        # 矩形判定，特别是符合1.2-1.6比例范围的矩形
        is_rectangle = (
            all(a < 15 for a in angles) and  # 角度接近90度
            convexity > 0.9 and
            (aspect_ratio < 0.83 or aspect_ratio > 1.2)  # 排除接近正方形的形状
        )
        
        if is_rectangle:
            # 特别标记出符合1.2-1.6比例范围的矩形
            if 1.2 <= aspect_ratio <= 1.6:
                return "Rectangle"
            else:
                return "Rectangle"
    
    # 备选圆形检测（边数多的近似圆形）
    elif sides > 6 and circularity > 0.7 and symmetry > 0.8:
        return "Circle"
    
    return "Unknown"
    


def find_min_marker(contours):
    """找到图像中最小的非重叠轮廓，且长边与短边比例在1.2到1.6之间"""
    
    if len(contours) > 0:
        # 过滤面积过小的轮廓
        valid_contours = [c for c in contours if cv2.contourArea(c) > params['outer_rect_area']]
        # print(f"过滤前检测到 {len(valid_contours)} 个有效轮廓")
        
        if valid_contours:
            # 按面积升序排序，优先保留面积小的轮廓
            valid_contours.sort(key=lambda c: cv2.contourArea(c), reverse=False)
            
            # 筛选出长宽比在1.2到1.6之间的轮廓
            ratio_filtered = []
            for contour in valid_contours:
                # 获取最小外接矩形
                rect = cv2.minAreaRect(contour)
                # 矩形的宽和高
                width, height = rect[1]
                
                # 确保宽大于等于高，方便计算比例
                if width < height:
                    width, height = height, width
                
                # 计算长宽比
                aspect_ratio = width / height if height > 0 else 0
                
                # 检查比例是否在1.2到1.6之间
                if 1.3 <= aspect_ratio <= 3.5:
                    ratio_filtered.append(contour)
            
            # print(f"比例筛选后保留 {len(ratio_filtered)} 个轮廓")
            
            if ratio_filtered:
                # 消除重叠轮廓，保留最小的
                non_overlapping = []
                overlap_threshold = 0.5  # 重叠面积阈值，超过此值视为重叠
                
                for contour in ratio_filtered:
                    # 计算当前轮廓的边界框
                    x, y, w, h = cv2.boundingRect(contour)
                    current_area = w * h
                    is_overlapping = False
                    
                    # 与已保留的轮廓比较
                    for kept in non_overlapping:
                        kx, ky, kw, kh = cv2.boundingRect(kept)
                        
                        # 计算交集区域
                        inter_x1 = max(x, kx)
                        inter_y1 = max(y, ky)
                        inter_x2 = min(x + w, kx + kw)
                        inter_y2 = min(y + h, ky + kh)
                        
                        # 计算交并比(IOU)
                        if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                            inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                            union_area = current_area + (kw * kh) - inter_area
                            iou = inter_area / union_area
                            
                            # 如果重叠度超过阈值，则标记为重叠
                            if iou > overlap_threshold:
                                is_overlapping = True
                                break
                    
                    # 如果不重叠，则保留当前轮廓
                    if not is_overlapping:
                        non_overlapping.append(contour)
                
                # print(f"去重后保留 {len(non_overlapping)} 个轮廓")
                
                # 如果有非重叠轮廓，返回最小的那个
                if non_overlapping:
                    # 由于已经按面积升序排序，第一个就是最小的
                    smallest_contour = non_overlapping[0]
                    smallest_rect = cv2.minAreaRect(smallest_contour)
                    # print(f"找到最小轮廓，面积: {cv2.contourArea(smallest_contour)}")
                    return smallest_rect
    
    # 如果没有找到有效轮廓，返回None
    print("未找到有效轮廓")
    return None




def distance_to_camera(knownWidth, focalLength, perWidth):
    """计算到摄像头的距离"""
    return (knownWidth * focalLength) / perWidth

def calculate_focalLength(image):
    """计算焦距"""
    marker = find_min_marker(image)
    if marker:
        return (marker[1][1] * KNOWN_DISTANCE) / KNOWN_WIDTH
    return None
#----------------------------------------------------------------------------------------------------
#以下是透视代码

def get_long_sides_average(sides):
    """获取两条长边的平均长度（和的二分之一）"""
    if len(sides) != 4:
        return 0.0
    # 排序后取后两条作为长边（矩形对边相等，理论上后两条长度相近）
    sorted_sides = sorted(sides)
    long_sides = sorted_sides[2:]  # 取较长的两条边
    return (long_sides[0] + long_sides[1]) / 2  # 和的二分之一


def calculate_side_lengths(approx):
    """计算四边形四条边的像素长度（欧氏距离）"""
    pts = approx.reshape(4, 2).astype(np.float32)
    ordered_pts = order_points(pts)  # 按左上→右上→右下→左下排序
    
    # 四条边：左上-右上，右上-右下，右下-左下，左下-左上
    sides = []
    for i in range(4):
        x1, y1 = ordered_pts[i]
        x2, y2 = ordered_pts[(i+1)%4]
        length = math.hypot(x2 - x1, y2 - y1)  # 欧氏距离
        sides.append(length)
    return sides

def is_square(contour, eps=0.1):
    """判断轮廓是否为正方形：四边形且宽高比接近1"""
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    if len(approx) != 4:  # 必须是四边形
        return False, None  # 不是四边形时返回None
    
    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = float(w) / h
    # 正方形宽高比应接近1（允许±0.1偏差）
    if (1 - eps < aspect_ratio < 1 + eps):
        return True, approx
    return False, approx  # 是四边形但不是正方形

def is_rectangle(contour, eps=0.1):
    """判断轮廓是否为长方形（非正方形）：四边形且宽高比偏离1"""
    is_sq, approx = is_square(contour, eps)
    if approx is None:  # 不是四边形
        return False, None
    if is_sq:  # 排除正方形
        return False, None
    # 是四边形且不是正方形，即为长方形
    return True, approx

# 添加函数：计算原始图像中Inner Rect的长和宽（像素）
def calculate_inner_rect_size(approx):
    """计算原始图像中Inner Rect的长和宽（像素）"""
    # 将点转换为(4, 2)格式
    pts = approx.reshape(4, 2)
    
    # 对点进行排序（左上、右上、右下、左下）
    ordered_pts = order_points(pts)
    
    # 计算四条边的长度
    top_edge = np.linalg.norm(ordered_pts[0] - ordered_pts[1])
    right_edge = np.linalg.norm(ordered_pts[1] - ordered_pts[2])
    bottom_edge = np.linalg.norm(ordered_pts[2] - ordered_pts[3])
    left_edge = np.linalg.norm(ordered_pts[3] - ordered_pts[0])
    
    # 计算宽度（取顶部和底部的平均值）
    width_px = (top_edge + bottom_edge) / 2.0
    
    # 计算高度（取左侧和右侧的平均值）
    height_px = (left_edge + right_edge) / 2.0
    
    return width_px, height_px

def order_points(pts):
    """对四边形顶点按顺时针排序（左上→右上→右下→左下）"""
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # 左上
    rect[2] = pts[np.argmax(s)]  # 右下
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # 右上
    rect[3] = pts[np.argmax(diff)]  # 左下
    
    return rect

def draw_square_info(image, squares, color=(0, 255, 0)):
    """在图像上绘制正方形信息（包括实际尺寸）"""
    for i, sq in enumerate(squares):
        cv2.drawContours(image, [sq["approx"]], -1, color, 2)
        
        # 计算中心点
        M = cv2.moments(sq["approx"])
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            # 绘制序号
            cv2.putText(image, f"{i+1}", (cX-10, cY+10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 绘制实际边长（厘米）
            if "real_side_cm" in sq:
                cv2.putText(image, f"{sq['real_side_cm']:.2f} cm", (cX-30, cY+40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

def calculate_real_size(warped_squares):
    """计算正方形的实际尺寸（厘米）"""
    # 透视变换后Inner Rect的像素面积
    warped_inner_area = TARGET_WIDTH * TARGET_HEIGHT
    
    # Inner Rect的实际面积（平方厘米）
    inner_real_area = INNER_RECT_WIDTH_CM * INNER_RECT_HEIGHT_CM
    
    # 计算面积比例因子（平方厘米/平方像素）
    area_ratio = inner_real_area / warped_inner_area
    
    # 为每个正方形计算实际边长
    for sq in warped_squares:
        # 正方形的像素面积
        pixel_area = sq["area"]
        
        # 计算实际面积（平方厘米）
        real_area = pixel_area * area_ratio
        
        # 计算实际边长（厘米） - 正方形面积 = 边长^2
        real_side = math.sqrt(real_area)
        sq["real_side_cm"] = real_side
        
        # 打印调试信息
        print(f"正方形像素面积: {pixel_area:.2f} px², 实际面积: {real_area:.2f} cm², 边长: {real_side:.2f} cm")

    return warped_squares

def detect_squares_in_warped(warped_img):
    """在透视变换后的图像中检测正方形"""
    # 对变换后的图像重新预处理（关键：基于校正后的图像检测）
    gray_warped = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    blurred_warped = cv2.GaussianBlur(gray_warped, (5, 5), 0)
    
    # 自适应阈值处理 - 更适合光照变化的环境
    thresh_warped = cv2.adaptiveThreshold(
        blurred_warped, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        15, 
        3
    )
    
    # 形态学操作 - 填充小孔洞，连接断裂边缘
    kernel = np.ones((3, 3), np.uint8)
    # 开运算：去除小噪点
    opened = cv2.morphologyEx(thresh_warped, cv2.MORPH_OPEN, kernel, iterations=1)
    # 闭运算：填充边缘缺口
    morphed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)  # 增加迭代次数
    
    # 查找变换后图像中的轮廓
    contours_warped, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    square_candidates = []
    for cnt in contours_warped:
        area = cv2.contourArea(cnt)
        # 基于变换后图像尺寸设置面积阈值
        if not (200 < area < (TARGET_WIDTH * TARGET_HEIGHT) * 0.4):
            continue
        
        # 计算轮廓周长和近似多边形
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        # 必须是四边形
        if len(approx) != 4:
            continue
        
        # 检查凸性
        if not cv2.isContourConvex(approx):
            continue
        
        # 关键优化：使用最小外接矩形（旋转矩形）计算宽高比
        rect = cv2.minAreaRect(approx)  # 获取旋转矩形
        w, h = rect[1]  # 旋转矩形的宽和高（已按大小排序）
        if h == 0:  # 避免除零
            continue
        aspect_ratio = min(w / h, h / w)  # 取宽高比的最小值（确保≤1）
        
        # 放宽宽高比阈值：从0.85-1.15改为0.75-1.25（允许更大变形）
        if not (0.75 < aspect_ratio < 1.25):
            continue
        # 计算轮廓面积与边界矩形面积的比例
        rect_area = w * h
        extent = float(area) / rect_area
        
        # 有效正方形的面积比例应在0.8以上
        if extent > 0.75:
            square_candidates.append({
                "contour": cnt,
                "approx": approx,
                "area": area,
                "rect": (x, y, w, h),
                "keep": True
            })
    
    # 过滤重叠正方形
    m = len(square_candidates)
    for i in range(m):
        sq1 = square_candidates[i]
        if not sq1["keep"]:
            continue
        for j in range(i + 1, m):
            sq2 = square_candidates[j]
            if not sq2["keep"]:
                continue
            if calculate_iou(sq1["rect"], sq2["rect"]) > 0.4:  # 使用更宽松的IOU阈值
                if sq1["area"] > sq2["area"]:
                    sq2["keep"] = False
                else:
                    sq1["keep"] = False
                    break
    
    return [sq for sq in square_candidates if sq["keep"]]

def draw_warped_squares_on_original(original_img, warped_squares, M_inv):
    """在原始图像上绘制透视变换后检测到的正方形"""
    for i, sq in enumerate(warped_squares):
        # 获取正方形的四个角点
        points = sq["approx"].reshape(-1, 2)
        
        # 将这些点映射回原始图像空间
        mapped_points = map_points_to_original(points, M_inv)
        
        # 在原始图像上绘制映射后的正方形
        cv2.polylines(original_img, [mapped_points], True, (255, 0, 0), 3)
        
        # 计算中心点并绘制序号和实际边长
        M = cv2.moments(mapped_points)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            # 绘制序号
            cv2.putText(original_img, f"#{i+1}", (cX-10, cY-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 绘制实际边长（厘米）
            if "real_side_cm" in sq:
                cv2.putText(original_img, f"{sq['real_side_cm']:.2f} cm", (cX-40, cY+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

# 新增函数：将透视变换后的点映射回原始图像
def map_points_to_original(points, M_inv):
    """将透视变换后的点映射回原始图像空间"""
    # 将点转换为适合perspectiveTransform的格式
    points_float = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    
    # 应用逆透视变换
    mapped_points = cv2.perspectiveTransform(points_float, M_inv)
    
    # 转换回整数坐标
    return np.int32(mapped_points)

def calculate_distance(pixel_length):
    """根据像素长度计算实际距离（cm）"""
    if pixel_length <= 0:
        return 0.0
    return DISTANCE_CONSTANT / pixel_length

def draw_contour_info(image, contours, color=(0, 255, 0)):
    """在图像上绘制轮廓信息（正方形显示边长，其他显示面积）"""
    for i, cnt in enumerate(contours):
        # 绘制轮廓
        cv2.drawContours(image, [cnt["approx"]], -1, color, 2)
        
        # 计算中心点
        M = cv2.moments(cnt["approx"])
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            # 绘制序号和形状类型
            cv2.putText(image, f"{i+1}", (cX-10, cY+10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(image, cnt["shape_type"], (cX-30, cY-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            
            # 正方形显示边长，其他显示面积（厘米）
            if cnt["shape_type"] == "Square" and "real_side_cm" in cnt:
                cv2.putText(image, f"Side: {cnt['real_side_cm']:.2f} cm", (cX-40, cY+40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            elif "real_area_cm" in cnt:
                cv2.putText(image, f"Area: {cnt['real_area_cm']:.2f} cm²", (cX-40, cY+40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
def detect_all_contours_in_warped(warped_img):
    """在透视变换后的图像中检测所有轮廓（不限制形状）"""
    # 对变换后的图像重新预处理
    gray_warped = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    blurred_warped = cv2.GaussianBlur(gray_warped, (5, 5), 0)
    
    # 自适应阈值处理
    thresh_warped = cv2.adaptiveThreshold(
        blurred_warped, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        15,  # 增大blockSize，减少局部噪声影响
        3    # 调整C值，控制阈值偏移
    )
    
    # 形态学处理：去噪和填充缺口
    kernel = np.ones((3, 3), np.uint8)
    opened = cv2.morphologyEx(thresh_warped, cv2.MORPH_OPEN, kernel, iterations=1)  # 去噪
    morphed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)  # 填充缺口
    
    # 查找所有外部轮廓
    contours_warped, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contour_candidates = []
    for cnt in contours_warped:
        area = cv2.contourArea(cnt)
        # 过滤过小轮廓（保留有意义的轮廓）
        if not (50 < area < (TARGET_WIDTH * TARGET_HEIGHT) * 0.6):  # 放宽面积范围
            continue
        
        # 轮廓近似（保留形状特征）
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)  # 保留轮廓主要特征
        
        # 获取最小外接矩形
        rect = cv2.minAreaRect(approx)
        w, h = rect[1]
        if h == 0:
            continue
        
        # 判断轮廓形状类型
        shape_type = "Unknown"
        if len(approx) == 4:
            aspect_ratio = min(w / h, h / w)
            if 0.9 < aspect_ratio < 1.1:
                shape_type = "Square"
            else:
                shape_type = "Rectangle"
        elif len(approx) == 3:
            shape_type = "Triangle"
        elif len(approx) > 4:
            # 判断是否为圆形（通过面积与周长比）
            circularity = 4 * math.pi * area / (peri * peri) if peri > 0 else 0
            if circularity > 0.7:
                shape_type = "Circle"
            else:
                shape_type = f"Polygon ({len(approx)})"
        
        contour_candidates.append({
            "contour": cnt,
            "approx": approx,
            "area": area,
            "shape_type": shape_type,
            "rect": (int(rect[0][0]-w/2), int(rect[0][1]-h/2), int(w), int(h)),
            "keep": True
        })
    
    # 过滤重叠轮廓（保留面积较大的）
    m = len(contour_candidates)
    for i in range(m):
        cnt1 = contour_candidates[i]
        if not cnt1["keep"]:
            continue
        for j in range(i + 1, m):
            cnt2 = contour_candidates[j]
            if not cnt2["keep"]:
                continue
            if calculate_iou(cnt1["rect"], cnt2["rect"]) > 0.5:  # 重叠阈值
                if cnt1["area"] > cnt2["area"]:
                    cnt2["keep"] = False
                else:
                    cnt1["keep"] = False
                    break
    
    return [cnt for cnt in contour_candidates if cnt["keep"]]

def calculate_aspect_ratio(approx):
    """计算矩形的长宽比（长边/短边）"""
    width_px, height_px = calculate_inner_rect_size(approx)
    if min(width_px, height_px) == 0:
        return 0.0
    return max(width_px, height_px) / min(width_px, height_px)

def is_aspect_ratio_valid(ratio):
    """检查长宽比是否在设定的阈值范围内"""
    return ASPECT_RATIO_LOWER <= ratio <= ASPECT_RATIO_UPPER

def calculate_real_contour_sizes(warped_contours):
    """计算所有轮廓的实际尺寸（正方形计算边长，其他计算面积）"""
    # 透视变换后Inner Rect的像素面积
    warped_inner_area = TARGET_WIDTH * TARGET_HEIGHT
    
    # Inner Rect的实际面积（平方厘米）
    inner_real_area = INNER_RECT_WIDTH_CM * INNER_RECT_HEIGHT_CM
    
    # 计算面积比例因子（平方厘米/平方像素）
    area_ratio = inner_real_area / warped_inner_area
    
    # 为每个轮廓计算实际尺寸
    for idx, cnt in enumerate(warped_contours):
        # 轮廓的像素面积
        pixel_area = cnt["area"]
        
        # 计算实际面积（平方厘米）
        real_area = pixel_area * area_ratio
        cnt["real_area_cm"] = real_area
        
        # 对于正方形，额外计算边长
        if cnt["shape_type"] == "Square":
            real_side = math.sqrt(real_area)  # 正方形边长 = 面积的平方根
            cnt["real_side_cm"] = real_side
            print(f"{cnt['shape_type']} {idx+1} 像素面积: {pixel_area:.2f} px², 实际边长: {real_side:.2f} cm")
        else:
            print(f"{cnt['shape_type']} {idx+1} 像素面积: {pixel_area:.2f} px², 实际面积: {real_area:.2f} cm²")

    return warped_contours

def draw_warped_contours_on_original(original_img, warped_contours, M_inv):
    """在原始图像上绘制透视变换后检测到的所有轮廓"""
    for i, cnt in enumerate(warped_contours):
        # 获取轮廓的顶点
        points = cnt["approx"].reshape(-1, 2)
        
        # 将这些点映射回原始图像空间
        mapped_points = map_points_to_original(points, M_inv)
        
        # 在原始图像上绘制映射后的轮廓
        cv2.polylines(original_img, [mapped_points], True, (255, 0, 0), 3)
        
        # 计算中心点并绘制信息
        M = cv2.moments(mapped_points)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            # 绘制序号和形状类型
            cv2.putText(original_img, f"#{i+1}", (cX-10, cY-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(original_img, cnt["shape_type"], (cX-30, cY+20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # 正方形显示边长，其他显示面积
            if cnt["shape_type"] == "Square" and "real_side_cm" in cnt:
                cv2.putText(original_img, f"Side: {cnt['real_side_cm']:.2f} cm", (cX-40, cY+45), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            elif "real_area_cm" in cnt:
                cv2.putText(original_img, f"Area: {cnt['real_area_cm']:.2f} cm²", (cX-40, cY+45), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#以上是透视代码
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
#以下是面积法识别半径周长代码
def detect_shapes_in_rect(contours):
    """检测所有轮廓中的各种形状（不限制在特定矩形内）"""
    shapes = {
        'triangles': [],
        'squares': [],
        'circles': []
    }
    
    # 处理所有轮廓
    for cnt in contours:
        cnt_area = cv2.contourArea(cnt)
        # 过滤面积过小的轮廓
        if cnt_area < params['min_shape_area']:
            continue
            
        # 尝试检测三角形
        is_tri, tri_approx, tri_conf = detect_triangle(cnt)
        if is_tri and tri_conf > 50:
            shapes['triangles'].append({
                "contour": cnt,
                "approx": tri_approx,
                "area": cnt_area,
                "confidence": tri_conf,
                "type": "triangle"
            })
            continue
        
        # 尝试检测正方形
        is_sq, sq_approx, sq_conf = detect_square_shape(cnt)
        if is_sq and sq_conf > 50:
            shapes['squares'].append({
                "contour": cnt,
                "approx": sq_approx,
                "area": cnt_area,
                "confidence": sq_conf,
                "type": "square"
            })
            continue
        
        # 尝试检测圆形
        is_circ, circ_data, circ_conf = detect_circle(cnt)
        if is_circ and circ_conf > 50:
            shapes['circles'].append({
                "contour": cnt,
                "circle_data": circ_data,  # (center, radius)
                "area": cnt_area,
                "confidence": circ_conf,
                "type": "circle"
            })
            continue
    
    # 对每种形状进行重叠过滤
    shapes['triangles'] = filter_overlapping_shapes(shapes['triangles'])
    shapes['squares'] = filter_overlapping_shapes(shapes['squares'])
    shapes['circles'] = filter_overlapping_shapes(shapes['circles'])
    
    return shapes

def filter_overlapping_shapes(shape_candidates):
    """过滤重叠的形状候选"""
    if not shape_candidates:
        return []
    
    # 为每个候选添加keep标记
    for shape in shape_candidates:
        shape["keep"] = True
    
    m = len(shape_candidates)
    
    for i in range(m):
        shape1 = shape_candidates[i]
        if not shape1["keep"]:
            continue
        
        # 获取形状1的边界框
        if shape1["type"] == "circle":
            center, radius = shape1["circle_data"]
            rect1 = (center[0] - radius, center[1] - radius, 2*radius, 2*radius)
        else:
            rect1 = cv2.boundingRect(shape1["approx"])
        
        for j in range(i + 1, m):
            shape2 = shape_candidates[j]
            if not shape2["keep"]:
                continue
            
            # 获取形状2的边界框
            if shape2["type"] == "circle":
                center, radius = shape2["circle_data"]
                rect2 = (center[0] - radius, center[1] - radius, 2*radius, 2*radius)
            else:
                rect2 = cv2.boundingRect(shape2["approx"])
            
            # 计算两个形状的IoU
            iou = calculate_iou(rect1, rect2)
            
            # 若重叠度高
            if iou > params['shape_iou_threshold']:
                # 保留置信度更高的形状，如果置信度相近则保留面积更大的
                conf_diff = abs(shape1.get("confidence", 0) - shape2.get("confidence", 0))
                if conf_diff < 10:  # 置信度相近
                    if shape1["area"] > shape2["area"]:
                        shape2["keep"] = False
                    else:
                        shape1["keep"] = False
                        break
                else:  # 保留置信度更高的
                    if shape1.get("confidence", 0) > shape2.get("confidence", 0):
                        shape2["keep"] = False
                    else:
                        shape1["keep"] = False
                        break
    
    return [shape for shape in shape_candidates if shape["keep"]]

#一样
def calculate_iou(rect1, rect2):
    """计算两个矩形/正方形的交并比（IoU）"""
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    
    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1 + w1, x2 + w2)
    inter_y2 = min(y1 + h1, y2 + h2)
    
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area
    
    return inter_area / union_area if union_area > 0 else 0

def detect_triangle(contour):
    """检测等边三角形"""
    area = cv2.contourArea(contour)
    if area < params['min_shape_area']:
        return False, None, 0
    
    # 使用多个epsilon值尝试三角形逼近
    peri = cv2.arcLength(contour, True)
    
    for epsilon_factor in [0.02, 0.025, 0.03, 0.035, 0.04]:
        epsilon = epsilon_factor * peri
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        if len(approx) == 3:
            # 计算三边长度
            def distance(p1, p2):
                return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            
            sides = []
            for i in range(3):
                p1 = approx[i][0]
                p2 = approx[(i+1)%3][0]
                sides.append(distance(p1, p2))
            
            # 检查是否为等边三角形（边长差异小于20%）
            avg_side = sum(sides) / 3
            max_diff = max(abs(side - avg_side) for side in sides)
            
            if max_diff / avg_side < 0.2:  # 20%的误差容忍
                confidence = 100 - (max_diff / avg_side) * 100
                return True, approx, confidence
    
    return False, None, 0

def detect_circle(contour):
    """检测圆形"""
    area = cv2.contourArea(contour)
    if area < params['min_shape_area']:
        return False, None, 0
    
    # 先排除明显的四边形
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    if len(approx) == 4:  # 如果能逼近为四边形，则不是圆形
        return False, None, 0
    
    # 计算圆形度 = 4π * area / perimeter²
    if peri == 0:
        return False, None, 0
    
    circularity = 4 * np.pi * area / (peri * peri)
    
    # 收紧圆形度范围，排除正方形(π/4≈0.785)
    if 0.85 <= circularity <= 1.15:  # 更严格的圆形度要求
        # 使用最小外接圆检查
        (x, y), radius = cv2.minEnclosingCircle(contour)
        circle_area = np.pi * radius * radius
        area_ratio = area / circle_area
        
        # 提高面积比例要求
        if area_ratio > 0.75:  # 更严格的面积比例要求
            # 检查轮廓点数，圆形应该有更多的点
            contour_points = len(contour)
            if contour_points > 8:  # 圆形通常有更多轮廓点
                confidence = min(100, circularity * 70 + area_ratio * 30)
                center = (int(x), int(y))
                return True, (center, int(radius)), confidence
    
    return False, None, 0

def is_contour_inside(contour, rect):
    """判断轮廓是否完全在矩形内部"""
    x, y, w, h = rect
    rect_right = x + w
    rect_bottom = y + h
    
    for point in contour:
        px, py = point[0]
        if not (x < px < rect_right and y < py < rect_bottom):
            return False
    return True

def detect_square_shape(contour):
    """检测正方形形状"""
    area = cv2.contourArea(contour)
    if area < params['min_shape_area']:
        return False, None, 0
    
    peri = cv2.arcLength(contour, True)
    
    # 尝试多个epsilon值以获得更好的四边形逼近
    for epsilon_factor in [0.015, 0.02, 0.025, 0.03]:
        epsilon = epsilon_factor * peri
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # 正方形宽高比应接近1，收紧范围
            if 0.85 <= aspect_ratio <= 1.15:
                # 检查四个角度是否接近90度
                angles = []
                for i in range(4):
                    p1 = approx[i][0]
                    p2 = approx[(i+1)%4][0]
                    p3 = approx[(i+2)%4][0]
                    
                    # 计算向量
                    v1 = (p1[0] - p2[0], p1[1] - p2[1])
                    v2 = (p3[0] - p2[0], p3[1] - p2[1])
                    
                    # 计算角度
                    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
                    mag_v1 = np.sqrt(v1[0]**2 + v1[1]**2)
                    mag_v2 = np.sqrt(v2[0]**2 + v2[1]**2)
                    
                    if mag_v1 > 0 and mag_v2 > 0:
                        cos_angle = dot_product / (mag_v1 * mag_v2)
                        cos_angle = np.clip(cos_angle, -1, 1)
                        angle = np.degrees(np.arccos(cos_angle))
                        angles.append(angle)
                
                # 检查角度是否接近90度
                if len(angles) == 4:
                    angle_deviations = [abs(angle - 90) for angle in angles]
                    avg_deviation = sum(angle_deviations) / 4
                    
                    # 角度偏差小于15度认为是正方形
                    if avg_deviation < 15:
                        # 计算置信度
                        aspect_confidence = 100 - abs(1 - aspect_ratio) * 200
                        angle_confidence = 100 - avg_deviation * 5
                        confidence = (aspect_confidence + angle_confidence) / 2
                        return True, approx, max(0, min(100, confidence))
    
    return False, None, 0

def calculate_shape_size(shape_area, inner_rect_pixel_area, shape_type):
    """计算形状的实际尺寸"""
    # 计算形状像素面积与Inner Rect像素面积的比例
    area_ratio = shape_area / inner_rect_pixel_area
    
    # 计算Inner Rect的实际面积（平方厘米）
    inner_rect_real_area = 25.5 * 17.0 
    
    # 计算形状的实际面积（平方厘米）
    shape_real_area = area_ratio * inner_rect_real_area
    
    if shape_type == "square":
        # 正方形边长
        side_length_cm = math.sqrt(shape_real_area)
        return f"{side_length_cm:.2f}cm"
    elif shape_type == "triangle":
        # 等边三角形边长: area = (√3/4) * side²
        side_length_cm = math.sqrt(4 * shape_real_area / math.sqrt(3))
        return f"{side_length_cm:.2f}cm"
    elif shape_type == "circle":
        # 圆形半径: area = π * r²
        radius_cm = math.sqrt(shape_real_area / math.pi)
        diameter_cm = 2 * radius_cm
        return f"{diameter_cm:.2f}cm"
    
    return "未知"

def draw_results(img, rectangles, inner_rect_info, shapes):
    """绘制检测结果"""
    result_img = img.copy()
    
    
    
    if inner_rect_info:
        inner_approx = inner_rect_info["approx"]
        inner_rect = cv2.boundingRect(inner_approx)
        x, y, w, h = inner_rect
        inner_rect_pixel_area = w * h
        
        # cv2.drawContours(result_img, [inner_approx], -1, (0, 0, 255), 3)
        # 绘制Inner Rect
        box = cv2.boxPoints(rectangles)
        box = np.intp(box)
        cv2.drawContours(result_img, [box], -1, (0, 255, 0), 3)
        
        
        # 绘制内部形状
        shape_counter = 1
        
        # 绘制三角形（蓝色）
        for triangle in shapes['triangles']:
            cv2.drawContours(result_img, [triangle["approx"]], -1, (255, 0, 0), 2)
            
            # 计算实际尺寸
            size_text = calculate_shape_size(triangle["area"], inner_rect_pixel_area, "triangle")
            
            # 在三角形中心标注
            M = cv2.moments(triangle["contour"])
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                cv2.putText(result_img, f"tir{shape_counter}", (cX-15, cY),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(result_img, size_text, (cX-25, cY+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 2)
                shape_counter += 1
        
        # 绘制正方形（绿色）
        for square in shapes['squares']:
            cv2.drawContours(result_img, [square["approx"]], -1, (0, 255, 0), 2)
            
            # 计算实际尺寸
            size_text = calculate_shape_size(square["area"], inner_rect_pixel_area, "square")
            
            # 在正方形中心标注
            M = cv2.moments(square["contour"])
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                cv2.putText(result_img, f"sqare{shape_counter}", (cX-15, cY),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(result_img, size_text, (cX-25, cY+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 2)
                shape_counter += 1
        
        # 绘制圆形（青色）
        for circle in shapes['circles']:
            center, radius = circle["circle_data"]
            cv2.circle(result_img, center, radius, (255, 255, 0), 2)
            
            # 计算实际尺寸
            size_text = calculate_shape_size(circle["area"], inner_rect_pixel_area, "circle")
            
            # 在圆形中心标注
            cv2.putText(result_img, f"circle{shape_counter}", (center[0]-15, center[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(result_img, size_text, (center[0]-25, center[1]+20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 2)
            shape_counter += 1
    
    return result_img

def mode1_result(inner_rect_info, shapes):
    """
    提取并返回所有形状的类型和尺寸信息
    
    参数:
        inner_rect_info: 内部矩形信息（用于尺寸换算）
        shapes: 包含三角形、正方形、圆形的字典，格式为:
                {
                    'triangles': [{'area': ..., ...}, ...],
                    'squares': [{'area': ..., ...}, ...],
                    'circles': [{'area': ..., ...}, ...]
                }
    
    返回:
        list: 形状信息列表，每个元素为字典，包含 'type'（类型）和 'size'（尺寸）
              示例: [
                  {'type': 'triangle', 'size': '边长: 5.2 cm'},
                  {'type': 'square', 'size': '边长: 3.1 cm'},
                  ...
              ]
    """
    # 存储所有形状的类型和尺寸信息
    shape_info_list = []
    
    if inner_rect_info:
        # 获取内部矩形的像素面积（用于尺寸换算）
        inner_approx = inner_rect_info["approx"]
        inner_rect = cv2.boundingRect(inner_approx)
        x, y, w, h = inner_rect
        inner_rect_pixel_area = w * h
        
        # 处理三角形
        for triangle in shapes['triangles']:
            # 计算三角形的实际尺寸（通过辅助函数获取尺寸文本）
            size_text = calculate_shape_size(triangle["area"], inner_rect_pixel_area, "triangle")
            # 添加到结果列表
            shape_info_list.append({
                "type": "triangle",  # 形状类型
                "size": size_text    # 尺寸信息（包含单位）
            })
        
        # 处理正方形
        for square in shapes['squares']:
            size_text = calculate_shape_size(square["area"], inner_rect_pixel_area, "square")
            shape_info_list.append({
                "type": "square",
                "size": size_text
            })
        
        # 处理圆形
        for circle in shapes['circles']:
            size_text = calculate_shape_size(circle["area"], inner_rect_pixel_area, "circle")
            shape_info_list.append({
                "type": "circle",
                "size": size_text
            })
    
    # 如果没有内部矩形信息，返回空列表
    return shape_info_list

def draw_center_cross(img, color=(0, 0, 255), thickness=2, line_length=350):
    """
    在图像中心绘制十字标记
    
    参数:
        img: 输入图像（OpenCV的ndarray格式）
        color: 十字线颜色，默认红色（BGR格式，(0,0,255)为红色）
        thickness: 线宽，默认2
        line_length: 十字线的半长（从中心向四周延伸的长度），默认20
    返回:
        绘制了十字的图像
    """
    # 获取图像的高度和宽度（注意：OpenCV中shape是(height, width, channels)）
    h, w = img.shape[:2]
    
    # 计算图像中心坐标
    center_x = w // 2
    center_y = h // 2
    
    # 绘制水平线（穿过中心点，左右延伸）
    # 起点：(center_x - line_length, center_y)
    # 终点：(center_x + line_length, center_y)
    cv2.line(
        img,
        (center_x - line_length, center_y),
        (center_x + line_length, center_y),
        color,
        thickness
    )
    
    # 绘制垂直线（穿过中心点，上下延伸）
    # 起点：(center_x, center_y - line_length)
    # 终点：(center_x, center_y + line_length)
    cv2.line(
        img,
        (center_x, center_y - line_length),
        (center_x, center_y + line_length),
        color,
        thickness
    )
    
    return img
def draw_vertical_quadrants(img, color=(0, 0, 255), thickness=2):
    """
    在图像上绘制垂直方向的直线，将屏幕沿水平方向四等分
    
    参数:
        img: 输入图像（OpenCV的ndarray格式）
        color: 直线颜色，默认红色（BGR格式，(0,0,255)为红色）
        thickness: 线宽，默认2
    返回:
        绘制了等分线的图像
    """
    # 获取图像的高度和宽度
    h, w = img.shape[:2]
    
    # 计算四等分的垂直直线x坐标
    # 第一条线：1/4宽度处
    x1 = w // 4
    # 第二条线：2/4（即1/2）宽度处（中线）
    x2 = w // 2
    # 第三条线：3/4宽度处
    x3 = (3 * w) // 4
    
    # 绘制三条垂直直线（从顶部到底部贯穿整个图像）
    # 第一条线
    cv2.line(
        img,
        (x1, 0),          # 起点：(x1, 顶部)
        (x1, h),          # 终点：(x1, 底部)
        color,
        thickness
    )
    
    # 第二条线（中线）
    cv2.line(
        img,
        (x2, 0),          # 起点：(x2, 顶部)
        (x2, h),          # 终点：(x2, 底部)
        color,
        thickness
    )
    
    # 第三条线
    cv2.line(
        img,
        (x3, 0),          # 起点：(x3, 顶部)
        (x3, h),          # 终点：(x3, 底部)
        color,
        thickness
    )
    
    return img

#以上是面积法识别半径周长代码
#----------------------------------------------------------------------------------------------------


class DEBUG_IOUDETECT:

    def __init__(self, accptAngleErr = 15,
                        precition = None,          # 如果已知像素对应实际长度的比例 务必设置
                        lengthRange  = [20, 5000], # 如果设置precition将长度距离设置为真实边长的距离 单位需统一
                        accpetSameLengthErr = 20,
                        angle_threshold     = 20,
                        epsilon   = 0.005,
                        testImage = None):
        self.acceptAngleErr       = accptAngleErr
        self.lengthRange          = lengthRange
        self.acceptSameLengthErr  = accpetSameLengthErr
        self.testImage            = testImage
        self.inputImage           = None
        self.epsilon              = epsilon
        self.precition            = precition
        self.rectLimit            = {6, 12} # 6-12cm
        self.coordList            = []
        self.isSetFlag            = None
        self.acceptOppAngle       = angle_threshold
        self.minLength            = 999999999
        self.lengthRange = list(lengthRange)  # 转换为可修改的列表
        if precition:
            self.lengthRange[0] = self.lengthRange[0] / self.precition
            self.lengthRange[1] = self.lengthRange[1] / self.precition
           #  print(self.lengthRange)

    def DEBUG_GetShortestRectLength(self):
        return self.minLength

    def DEBUG_CheckIsInRange(self, distance):
        if (distance >= self.lengthRange[0]) and \
           (distance <= self.lengthRange[1]):
            return True
        else:
            return False

    def DEBUG_CheckIs90Angle(self, angle):
        if abs(angle - 90) <= self.acceptAngleErr:
            return True
        else:
            return False

    def DEBUG_CheckIsSameLine(self, line1, line2):
        if abs(line1 - line2) <= self.acceptSameLengthErr:
            return True
        else:
            return False

    def DEBUG_SortCoords(self, corners):
        # 按 [左上, 右上, 右下, 左下] 排序
        # 1. 按 y 坐标排序（区分上下）
        corners = corners[np.argsort(corners[:, 1])]
        # 2. 对上半部分按 x 排序（左上 < 右上）
        top = corners[:2][np.argsort(corners[:2, 0])]
        # 3. 对下半部分按 x 排序（左下 < 右下）
        bottom = corners[2:][np.argsort(corners[2:, 0])]
        # 合并结果
        sorted_corners = np.vstack([top, bottom[::-1]])  # 调整为 [tl, tr, br, bl]
        return sorted_corners

    def DEBUG_GetFourthPoint(self, p1, p2, p3):
        # 计算第四个点
        P1, P2, P3 = np.array(p1), np.array(p2), np.array(p3)
        P4 = [-P2[0] + P1[0] + P3[0], -P2[1] + P1[1] + P3[1]]
        corners = np.array([P1, P2, P3, P4], dtype=np.int32)
        sorted_corners = self.DEBUG_SortCoords(corners)
        return sorted_corners

    def DEBUG_GetThirdAndFourthPoints(self, P1, P2, P3, P4):
        distance = np.linalg.norm(P2 - P3)
        v1 = np.array(P2) - np.array(P1)
        v2 = np.array(P4) - np.array(P3)
        distanceV1 = np.linalg.norm(v1)
        distanceV2 = np.linalg.norm(v2)

        # 根据正方形尺寸缩放坐标点
        v1 = v1 * (distance / distanceV1)
        v2 = v2 * (distance / distanceV2)

        # 计算两个正方形埋点
        calculatedP3 = [P2[0] - v1[0], P2[1] - v1[1]]
        calculatedP4 = [P3[0] + v2[0], P3[1] + v2[1]]

        corners = np.array([P2, P3, calculatedP3, calculatedP4], dtype=np.int32)
        sorted_corners = self.DEBUG_SortCoords(corners)
        return sorted_corners

    def DEBUG_SetRectFlag(self, points):
        for i in range(len(points)):
            self.isSetFlag[i] = False

    def DEBUG_CheckGuessPointsIsInAlreadyDetectedRects(self, coords = None):
        if not np.any(coords) or not np.any(self.coordList):
            return False
        # print(coords)
        for coord in self.coordList:
            for rectCoord in coords:
                if rectCoord[0] == coord[0][0] and rectCoord[1] == coord[0][1] \
                   or rectCoord[0] == coord[1][0] and rectCoord[1] == coord[1][1]\
                   or rectCoord[0] == coord[2][0] and rectCoord[1] == coord[2][1]\
                   or rectCoord[0] == coord[3][0] and rectCoord[1] == coord[3][1]:
                        return True
                else:
                    continue
        return False

    def DEBUG_GetShortestLengthAndCorners(self):
        if not self.coordList:
            self.minLength = 0  # 无数据时返回0和None
            return

        min_len = float('inf')
        smallest_corners = None  # 存储最小正方形的角点
        
        for corners in self.coordList:
            if len(corners) != 4:
                continue  # 跳过角点数量不正确的项
            
            # 计算相邻边平均长度
            x1, y1 = corners[0]
            x2, y2 = corners[1]
            x3, y3 = corners[2]
            side1 = ((x2 - x1)**2 + (y2 - y1)** 2)**0.5
            side2 = ((x3 - x2)** 2 + (y3 - y2)**2)** 0.5
            avg_side = (side1 + side2) / 2

            # 更新最小边长和对应角点
            if avg_side < min_len:
                min_len = avg_side
                smallest_corners = corners

        # 处理未找到有效正方形的情况
        if min_len == float('inf'):
            self.minLength = 0
        else:
            # for i in range(4):
            #     cv2.line(self.testImage, tuple(smallest_corners[i]), tuple(smallest_corners[(i + 1) % 4]), color=(0, 0, 255), thickness = 30)
            self.minLength = min_len

    def DEBUG_Calculate_Angle(self, v1, v2):
        # 计算两点夹角
        cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-5)
        angle_rad = np.arccos(np.clip(cos_theta, -1, 1))
        angle_deg = np.degrees(angle_rad)
        return angle_deg

    def nms_remove_overlapping_squares(self, square_corners_set, iou_threshold=0.5):
        """
        使用非极大值抑制(NMS)去除重合正方形
        
        参数:
            square_corners_set: 正方形角点集合，每个元素为4个角点坐标列表
            iou_threshold: IOU阈值，超过此值视为重合，默认0.5
        
        返回:
            去重后的正方形角点列表
        """
        if not square_corners_set or len(square_corners_set) == 0:
            return []
        
        # 1. 转换为边界框并计算面积（作为置信度替代）
        bboxes = []
        areas = []
        for sq in square_corners_set:
            # 提取边界框 (xmin, ymin, xmax, ymax)
            xs = [p[0] for p in sq]
            ys = [p[1] for p in sq]
            xmin, ymin = min(xs), min(ys)
            xmax, ymax = max(xs), max(ys)
            bboxes.append((xmin, ymin, xmax, ymax))
            # 用面积作为置信度（面积越大优先级越高）
            areas.append((xmax - xmin) * (ymax - ymin))
        
        # 2. 按置信度（面积）降序排序
        order = sorted(range(len(areas)), key=lambda i: areas[i], reverse=True)
        
        keep = []
        while order:
            # 保留置信度最高的正方形
            i = order.pop(0)
            keep.append(i)
            
            # 计算与剩余正方形的IOU
            for j in order[:]:  # 使用副本遍历
                # 当前正方形边界框
                x1, y1, x2, y2 = bboxes[i]
                # 对比正方形边界框
                x3, y3, x4, y4 = bboxes[j]
                
                # 计算交集
                inter_x1 = max(x1, x3)
                inter_y1 = max(y1, y3)
                inter_x2 = min(x2, x4)
                inter_y2 = min(y2, y4)
                inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
                
                # 计算并集
                area_i = areas[i]
                area_j = areas[j]
                union_area = area_i + area_j - inter_area
                
                # 计算IOU
                iou = inter_area / union_area if union_area > 0 else 0
                
                # 若IOU超过阈值，移除该正方形
                if iou > iou_threshold:
                    order.remove(j)
        
        # 返回保留的正方形
        return [square_corners_set[i] for i in keep]

    def DEBUG_CheckVectorIsOppositeDirection(self, v1, v2):
        # 转换为numpy数组
        v1 = np.array(v1)
        v2 = np.array(v2)
        # 处理零向量情况
        if np.linalg.norm(v1) < 1e-8 or np.linalg.norm(v2) < 1e-8:
            return False  # 零向量不算作反向
        # 向量归一化
        norm_v1 = v1 / np.linalg.norm(v1)
        norm_v2 = v2 / np.linalg.norm(v2)
        # 计算点积
        dot_product = np.dot(norm_v1, norm_v2)
        # 处理浮点精度问题
        dot_product = np.clip(dot_product, -1.0, 1.0)
        # 计算向量间角度（度）
        angle = np.degrees(np.arccos(dot_product))  # 反向平行判定条件：夹角接近180°
        return abs(angle - 180) < self.acceptOppAngle

    def DEBUG_CheckIsRect_TwoLineOneAngle(self, p1, p2, p3):
        # 两点向量计算
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        angle_deg = self.DEBUG_Calculate_Angle(v1, v2)
        # 计算两点间距
        distanceP1_P2 = np.linalg.norm(p1 - p2)
        distanceP2_P3 = np.linalg.norm(p2 - p3)
        if self.DEBUG_CheckIsInRange(distanceP1_P2) and \
           self.DEBUG_CheckIsInRange(distanceP2_P3) and \
           self.DEBUG_CheckIsSameLine(distanceP1_P2, distanceP2_P3) and \
           self.DEBUG_CheckIs90Angle(angle_deg):
            RectCoord = self.DEBUG_GetFourthPoint(p1, p2, p3)
            # if self.testImage is not None:
            #     for i in range(4):
            #         cv2.line(self.testImage, tuple(RectCoord[i]), tuple(RectCoord[(i + 1) % 4]), color=(0, 255, 0), thickness=2)
            return True, RectCoord
        else:
            return False, []

    def DEBUG_CheckIsRect_ThreeLineThreeAngle(self, p1, p2, p3, p4):
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p2)
        v3 = np.array(p4) - np.array(p3)
        distanceP1_P2 = np.linalg.norm(v1)
        distanceP2_P3 = np.linalg.norm(v2)
        distanceP3_P4 = np.linalg.norm(v3)
        angle_deg1 = self.DEBUG_Calculate_Angle(v1, v2)
        angle_deg2 = self.DEBUG_Calculate_Angle(v2, v3)
        if self.DEBUG_CheckIsInRange(distanceP1_P2) and \
           self.DEBUG_CheckIsInRange(distanceP2_P3) and \
           self.DEBUG_CheckIsInRange(distanceP3_P4) and \
           self.DEBUG_CheckIsSameLine(distanceP1_P2, distanceP2_P3) and \
           self.DEBUG_CheckIsSameLine(distanceP2_P3, distanceP3_P4) and \
           self.DEBUG_CheckIs90Angle(angle_deg1) and \
           self.DEBUG_CheckIs90Angle(angle_deg2):
            coord = self.DEBUG_GetFourthPoint(p2, p3, p4)
            # if self.testImage is not None:
            #     for i in range(4):
            #         cv2.line(self.testImage, tuple(coord[i]), tuple(coord[(i + 1) % 4]), color=(0, 255, 0), thickness=2)
            return True, coord
        else:
            return False, []


    def DEBUG_ChecIsRect_OneLineTwoAngle(self, p1, p2, p3, p4):
        global image
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p2)
        v3 = np.array(p4) - np.array(p3)
        angle_deg1 = self.DEBUG_Calculate_Angle(v1, v2)
        angle_deg2 = self.DEBUG_Calculate_Angle(v2, v3)
        distanceP2_P3 = np.linalg.norm(v2)  # 计算的是中间两个点的长度
        # print(angle_deg1, angle_deg2, distanceP2_P3)
        # 检测是否有两角, 并且有一边存在
        if self.DEBUG_CheckIs90Angle(angle_deg1) and \
           self.DEBUG_CheckIs90Angle(angle_deg2) and \
           self.DEBUG_CheckIsInRange(distanceP2_P3) and \
           self.DEBUG_CheckVectorIsOppositeDirection(v1, v3):
            RectCoord = self.DEBUG_GetThirdAndFourthPoints(p1, p2, p3, p4)
            # if self.testImage is not None:
            #     for i in range(4):
            #         cv2.line(self.testImage, tuple(RectCoord[i]), tuple(RectCoord[(i + 1) % 4]), color=(0, 255, 0), thickness=2)
            return True, RectCoord
        else:
            return False, []

    def DEBUG_CheckIsInnerRect(self, p1, p2, p3):
        midPoint = np.array(p1 + p3) / 2
        x = int(round(midPoint[0]))
        y = int(round(midPoint[1]))

        # import random
        # random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # cv2.line(self.testImage, tuple(p1), tuple(p3), color=(0, 0, 255), thickness=2)
        # cv2.circle(self.testImage, p2, radius=3, color=random_color, thickness=2)
        # cv2.circle(self.testImage, (x, y), radius=3, color=random_color, thickness=2)

       # cv2.waitKey(1000)

        if self.inputImage[y][x] == 255:
            return True
        else:
            return False


    def DEBUG_CheckIfRect(self, p1, p2, p3, p4):
        # 当前的角为内90度角
        # print(self.DEBUG_CheckGuessPointsIsInAlreadyDetectedRects())
        if self.DEBUG_CheckIsInnerRect(p1, p2, p3):
            ###############################三边三角情况#####################################
            # isRect, coords = self.DEBUG_CheckIsRect_ThreeLineThreeAngle(p1, p2, p3, p4)
            # #print(coords)
            # if isRect:
            #     print("ThreeLineThreeAngle")
            #     return 2, coords # 2
            ################################两边一角的情况###################################
            # isRect, coords = self.DEBUG_CheckIsRect_TwoLineOneAngle(p1, p2, p3)
            # self.DEBUG_CheckGuessPointsIsInAlreadyDetectedRects(coords)
            # #print(coords)
            # if isRect and not self.DEBUG_CheckGuessPointsIsInAlreadyDetectedRects(coords):
            #     cv2.circle(self.testImage, p1, radius=6, color=(0, 0, 255), thickness=2)
            #     print("TwoLineOneAngle")
            #     return 1, coords  # 后增一步 因为下一个点处在该正方形内部
            ###############################################################################
            isRect, coords = self.DEBUG_ChecIsRect_OneLineTwoAngle(p1, p2, p3, p4)
            # print("num", len(coords))
           # print(coords)
            if isRect and not self.DEBUG_CheckGuessPointsIsInAlreadyDetectedRects(coords):
                cv2.circle(self.testImage, p1, radius=6, color=(0, 0, 255), thickness=2)
                print("OneLineTwoAngle")
                return 2, coords  # 后增两步 因为后两个点肯定在正方形内部
            ###############################################################################
        return 0, []

    '''
        @brief: 检测重叠矩形在DEBUG_FindIOURects之前调用 (外部调用)
        @param: 传入实时更新的像素对应实际距离
    '''
    def DEBUG_UpdateLengthRange(self, precition):
        self.lengthRange[0] = self.lengthRange[0] / precition
        self.lengthRange[1] = self.lengthRange[1] / precition
        print(self.lengthRange)

        
    '''
        @brief: 检测重叠矩形 (外部调用)
        @param: 传入检测到的轮廓数组
        @param: 若传入frame则测试图像开启
        @return: 若有矩形框存在则返回存储矩形框的列表存储格式
    '''
    def DEBUG_FindIOURects(self, contours, input, frame = None):
        self.testImage = frame
        self.inputImage = input
        # self.testImage = cv2.cvtColor(self.testImage, cv2.COLOR_GRAY2BGR)
        # self.inputImage = image
        self.coordList.clear()
        for contour in contours:
            # 多边形逼近轮廓
            epsilon = self.epsilon * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) < 3:
                continue
            points = approx[:, 0, :]
            # self.testImage = draw_coords(self.testImage, points)
            n = len(points)
            i = 0
            while i < n:
                p1 = points[(i - 1) % n]
                p2 = points[i % n]
                p3 = points[(i + 1) % n]
                p4 = points[(i + 2) % n]
                #######找到之后可以STEP增加################
                step, coords = self.DEBUG_CheckIfRect(p1, p2, p3, p4)
                if np.any(coords):
                    self.coordList.append(coords)
                i += step + 1
                ########################################
        if self.coordList:
            self.DEBUG_GetShortestLengthAndCorners()
            self.coordList = self.nms_remove_overlapping_squares(self.coordList)
            for RectCoord in self.coordList:
                for i in range(4):
                    cv2.line(self.testImage, tuple(RectCoord[i]), tuple(RectCoord[(i + 1) % 4]), color=(0, 255, 0), thickness=2)
            return self.coordList
        else:
            return []



detector = DEBUG_IOUDETECT(lengthRange = tuple(LENGTH_RANGE), precition = 0, 
                            accpetSameLengthErr = ACCPET_SAME_LENGTH_ERR,
                            angle_threshold = ANGLE_THRESHOLD,
                            epsilon = EPSILON
                             )

def crop_rectangle_from_points(image, points):
    """
    根据四个顶点从图像中裁切出矩形区域
    
    参数:
        image: 输入图像
        points: 四个顶点坐标，形状为 (4, 2)
    
    返回:
        cropped_image: 裁切后的矩形图像
        crop_rect: 裁切区域的边界框 (x, y, w, h)
    """
    # 获取边界框
    x, y, w, h = cv2.boundingRect(points)
    
    # 确保边界框在图像范围内
    x = max(0, x)
    y = max(0, y)
    w = min(w, image.shape[1] - x)
    h = min(h, image.shape[0] - y)
    
    # 裁切图像
    cropped_image = image[y:y+h, x:x+w]
    
    return cropped_image, (x, y, w, h)

def detect_digit_in_crop(cropped_image, confidence_threshold=0.5, iou_threshold=0.45):
    """
    在裁切的图像中检测数字
    
    参数:
        cropped_image: 裁切后的图像（OpenCV格式）
        confidence_threshold: 置信度阈值（如果为默认值则使用全局变量）
        iou_threshold: IoU阈值（如果为默认值则使用全局变量）
    
    返回:
        detected_digits: 检测到的数字信息列表，每个元素包含 {'digit': 数字, 'score': 置信度, 'bbox': 边界框}
    """
    if not YOLO_ENABLED or digit_detector is None:
        if YOLO_DEBUG:
            print("❌ YOLO未启用或模型未加载")
        return []
    
    # 如果使用默认参数，则采用全局配置
    if confidence_threshold == 0.5:  # 默认值，使用全局配置
        confidence_threshold = YOLO_CONFIDENCE
    if iou_threshold == 0.45:  # 默认值，使用全局配置  
        iou_threshold = YOLO_IOU
    
    if YOLO_DEBUG:
        print(f"🔧 检测参数: 置信度={confidence_threshold}, IoU={iou_threshold}")
        print(f"📐 裁切图像尺寸: {cropped_image.shape}")
    
    try:
        # 将OpenCV图像从BGR转换为RGB格式（YOLO模型需要RGB输入）
        if YOLO_DEBUG:
            print(f"🎨 转换图像格式: BGR → RGB")
        rgb_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        
        # 将RGB图像转换为MaixCAM图像格式
        maix_img = image.cv2image(rgb_image, bgr=False, copy=True)
        
        original_size = (maix_img.width(), maix_img.height())
        
        # 调整图像尺寸到模型输入尺寸
        if maix_img.width() != digit_detector.input_width() or maix_img.height() != digit_detector.input_height():
            maix_img = maix_img.resize(digit_detector.input_width(), digit_detector.input_height())
            if YOLO_DEBUG:
                print(f"📏 图像尺寸调整: {original_size} → ({digit_detector.input_width()}, {digit_detector.input_height()})")
        
        # 进行检测
        if YOLO_DEBUG:
            print(f"🔍 开始YOLO检测...")
        
        objs = digit_detector.detect(maix_img, conf_th=confidence_threshold, iou_th=iou_threshold)
        
        detected_digits = []
        for i, obj in enumerate(objs):
            digit_info = {
                'digit': digit_detector.labels[obj.class_id],  # 检测到的数字
                'score': obj.score,                            # 置信度
                'bbox': (obj.x, obj.y, obj.w, obj.h),         # 相对于裁切图像的边界框
                'class_id': obj.class_id                      # 类别ID
            }
            detected_digits.append(digit_info)
        
        return detected_digits
        
    except Exception as e:
        print(f"数字检测错误: {e}")
        if YOLO_DEBUG:
            import traceback
            traceback.print_exc()
        return []

def draw_digit_results_on_warped(warped_image, rect_coords, digit_results):
    """
    在透视变换后的图像上绘制数字检测结果
    
    参数:
        warped_image: 透视变换后的图像
        rect_coords: 矩形区域的四个顶点列表
        digit_results: 对应的数字检测结果列表
    """
    for rect_idx, (quad_array, digits) in enumerate(zip(rect_coords, digit_results)):
        # 处理四边形坐标
        points = np.squeeze(quad_array)
        
        if len(points.shape) != 2 or points.shape[0] != 4:
            continue
        
        # 绘制矩形边框
        for i in range(4):
            pt1 = tuple(map(int, points[i]))
            pt2 = tuple(map(int, points[(i + 1) % 4]))
            cv2.line(warped_image, pt1, pt2, color=(0, 255, 0), thickness=3)
        
        # 计算矩形中心点
        center_x = int(np.mean(points[:, 0]))
        center_y = int(np.mean(points[:, 1]))
        
        # 显示检测到的数字
        if digits:
            # 如果检测到数字，显示置信度最高的数字
            best_digit = max(digits, key=lambda x: x['score'])
            digit_text = f"{best_digit['digit']}"
            score_text = f"({best_digit['score']:.2f})"
            
            # 绘制数字（大字体，黄色）
            cv2.putText(warped_image, digit_text, (center_x-20, center_y+10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            
            # 绘制置信度（小字体，白色）
            cv2.putText(warped_image, score_text, (center_x-25, center_y+35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else:
            # 没有检测到数字，显示"?"
            cv2.putText(warped_image, "?", (center_x-10, center_y+10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        
        # 绘制矩形编号（左上角）
        bbox = cv2.boundingRect(points.astype(int))
        cv2.putText(warped_image, f"R{rect_idx+1}", (bbox[0], bbox[1]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

def process_digit_recognition(warped_inner, rect_coords):
    all_digit_results = []
    cropped_images_list = []  # 保存所有裁切的图像
    old_quad_array = []
    
    if len(rect_coords) == 0:
        print("无矩形区域需要识别")
        return all_digit_results, cropped_images_list
    
    print(f"开始数字识别 ({len(rect_coords)} 个区域)...")
    if GRID_DEBUG:
        print("🔍 索引对应关系验证：")
    
    successful_detections = 0
    
    for rect_idx, quad_array in enumerate(rect_coords):  # 按原始顺序处理
        old_quad_array.append(quad_array)
        print(quad_array)
        if GRID_DEBUG:
            print(f"  处理矩形 R{rect_idx+1} (索引{rect_idx}) -> ", end="")
        
        points = np.squeeze(quad_array)

        
        if len(points.shape) != 2 or points.shape[0] != 4:
            if GRID_DEBUG:
                print(f"坐标错误，跳过")
            else:
                print(f"R{rect_idx+1}: 坐标错误，跳过")
            all_digit_results.append([])
            cropped_images_list.append((None, rect_idx))
            if GRID_DEBUG:
                print(f"    ↳ all_digit_results[{len(all_digit_results)-1}] = []")
                print(f"    ↳ cropped_images_list[{len(cropped_images_list)-1}] = (None, R{rect_idx+1})")
            continue
        
        # 裁切矩形区域
        cropped_image, crop_rect = crop_rectangle_from_points(warped_inner, points)
        
        if cropped_image.size == 0:
            if GRID_DEBUG:
                print(f"裁切失败，跳过")
            else:
                print(f"R{rect_idx+1}: 裁切失败，跳过")
            all_digit_results.append([])
            cropped_images_list.append((None, rect_idx))
            if GRID_DEBUG:
                print(f"    ↳ all_digit_results[{len(all_digit_results)-1}] = []")
                print(f"    ↳ cropped_images_list[{len(cropped_images_list)-1}] = (None, R{rect_idx+1})")
            continue
        
        # 保存裁切的图像用于显示
        cropped_images_list.append((cropped_image.copy(), rect_idx))
        if GRID_DEBUG:
            print(f"图像{cropped_image.shape[:2]} -> ", end="")
        
        # 检测数字
        digit_results = detect_digit_in_crop(cropped_image)
        all_digit_results.append(digit_results)
        
        # 验证对应关系
        current_idx = len(all_digit_results) - 1
        if digit_results:
            successful_detections += 1
            best_digit = max(digit_results, key=lambda x: x['score'])
            if GRID_DEBUG:
                print(f"数字'{best_digit['digit']}'({best_digit['score']:.2f})")
                print(f"    ↳ all_digit_results[{current_idx}] = [{best_digit['digit']}]")
                print(f"    ↳ cropped_images_list[{current_idx}] = (图像, R{rect_idx+1})")
            else:
                print(f"R{rect_idx+1}: 数字 '{best_digit['digit']}' ({best_digit['score']:.2f})")
        else:
            if GRID_DEBUG:
                print(f"未识别到数字")
                print(f"    ↳ all_digit_results[{current_idx}] = []")
                print(f"    ↳ cropped_images_list[{current_idx}] = (图像, R{rect_idx+1})")
            else:
                print(f"R{rect_idx+1}: 未识别到数字")
    
    return all_digit_results, cropped_images_list, old_quad_array

def draw_rectangles_on_warped(warped_inner, rect_coords):
    """
    在透视变换后的图像上绘制检测到的矩形框
    
    参数:
        warped_inner: 透视变换后的图像
        rect_coords: 矩形区域的四个顶点列表
    """
    if warped_inner is None or len(rect_coords) == 0:
        return
    
    print(f"🎨 在warped_inner上绘制 {len(rect_coords)} 个矩形框")
    
    for coord_idx, quad_array in enumerate(rect_coords):
        # 直接处理不同可能的数组形状，避免squeeze错误
        points = np.squeeze(quad_array)
        
        # 确保是二维数组 (n, 2)
        if len(points.shape) != 2:
            print(f"警告：第 {coord_idx} 个四边形坐标维度错误，形状为 {points.shape}")
            continue
        
        # 验证是否有4个点
        if points.shape[0] == 4:
            # 绘制四边形（连接4个点形成闭合图形）
            for i in range(4):
                pt1 = tuple(points[i])
                pt2 = tuple(points[(i + 1) % 4])  # 最后一个点连接回第一个点
                cv2.line(warped_inner, pt1, pt2, color=(0, 255, 0), thickness=3)
            
            # 在矩形中心添加编号标识
            center_x = int(np.mean(points[:, 0]))
            center_y = int(np.mean(points[:, 1]))
            cv2.putText(warped_inner, f"R{coord_idx+1}", (center_x-15, center_y+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.circle(warped_inner, (center_x, center_y), 5, (255, 255, 0), -1)
        else:
            print(f"警告：第 {coord_idx} 个四边形坐标格式不正确，包含 {points.shape[0]} 个点（预期4个）")
    
    # 在warped图像上添加检测统计信息
    if len(rect_coords) > 0:
        cv2.putText(warped_inner, f"Detected: {len(rect_coords)} Rectangles", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

def resize_keep_aspect_ratio(image, target_size=(80, 80), fill_color=(0, 0, 0), show_size_info=True, rect_id=""):
    """
    保持长宽比地将图像缩放到目标尺寸，不足部分用填充色填充
    
    参数:
        image: 输入图像
        target_size: 目标尺寸 (width, height)
        fill_color: 填充颜色，默认黑色
        show_size_info: 是否显示原始尺寸信息
        rect_id: 矩形标识符
    
    返回:
        resized_image: 保持长宽比的缩放图像
    """
    if image is None or image.size == 0:
        return np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
    
    # 获取原始图像尺寸
    h, w = image.shape[:2]
    target_w, target_h = target_size
    
    # 计算缩放比例，保持长宽比
    scale = min(target_w / w, target_h / h)
    
    # 计算缩放后的尺寸
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # 缩放图像
    if len(image.shape) == 2:  # 灰度图转RGB
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    resized = cv2.resize(image, (new_w, new_h))
    
    # 创建目标尺寸的画布，使用深灰色填充以区分图像和填充区域
    canvas = np.full((target_h, target_w, 3), fill_color, dtype=np.uint8)
    
    # 计算居中放置的位置
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    
    # 将缩放后的图像放置到画布中心
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    # 🆕 添加原始尺寸信息显示
    if show_size_info:
        # 在画布底部显示原始尺寸
        size_text = f"{w}x{h}"
        text_size = cv2.getTextSize(size_text, cv2.FONT_HERSHEY_SIMPLEX, 0.3, 1)[0]
        text_x = (target_w - text_size[0]) // 2
        text_y = target_h - 3
        
        # 添加黑色背景使文字更清晰
        cv2.rectangle(canvas, (text_x-2, text_y-text_size[1]-2), 
                     (text_x+text_size[0]+2, text_y+2), (0, 0, 0), -1)
        cv2.putText(canvas, size_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        # 在左上角显示缩放比例
        scale_text = f"{scale:.2f}x"
        cv2.putText(canvas, scale_text, (2, 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 0), 1)
    
    return canvas

def create_cropped_images_grid(cropped_images_list, grid_size=(90, 90), use_nine_grid=True, digit_results=None):
    """
    将所有裁切的图像拼接成一个网格显示，保持原始长宽比，并显示数字识别结果
    
    参数:
        cropped_images_list: 裁切图像列表，每个元素为 (image, rect_idx)
        grid_size: 每个小图像的显示尺寸
        use_nine_grid: 是否使用3x3九宫格布局
        digit_results: 数字识别结果列表，对应每个图像的识别结果
    
    返回:
        grid_image: 拼接后的网格图像
    """
    # 🔍 验证数据一致性
    if cropped_images_list and digit_results:
        if len(cropped_images_list) != len(digit_results):
            print(f"⚠️  数据不一致：cropped_images_list长度({len(cropped_images_list)}) != digit_results长度({len(digit_results)})")
        elif GRID_DEBUG:
            print(f"✅ 数据一致性检查通过：{len(cropped_images_list)} 个图像对应 {len(digit_results)} 个识别结果")
    
    if use_nine_grid:
        # 🆕 固定使用3x3九宫格布局
        cols, rows = 3, 3
        grid_width = cols * grid_size[0]
        grid_height = rows * grid_size[1]
        # 简化输出
    else:
        # 原有的动态布局（保留作为备选）
        if not cropped_images_list:
            placeholder = np.zeros((grid_size[1], grid_size[0], 3), dtype=np.uint8)
            cv2.putText(placeholder, "No Crops", (5, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            return placeholder
        
        num_images = len(cropped_images_list)
        cols = min(num_images, 4)
        rows = (num_images + cols - 1) // cols
        grid_width = cols * grid_size[0]
        grid_height = rows * grid_size[1]
        print(f"动态网格布局: {rows}行 x {cols}列")
    
    # 创建网格图像，使用深色背景
    grid_image = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)
    
    # 在九宫格中添加位置标记
    if use_nine_grid:
        for i in range(9):
            row = i // 3
            col = i % 3
            x_start = col * grid_size[0]
            y_start = row * grid_size[1]
            
            # 绘制九宫格边框
            cv2.rectangle(grid_image, (x_start, y_start), 
                         (x_start + grid_size[0] - 1, y_start + grid_size[1] - 1), 
                         (64, 64, 64), 1)
            
            # 在空格子中显示位置编号
            center_x = x_start + grid_size[0] // 2
            center_y = y_start + grid_size[1] // 2
            cv2.putText(grid_image, f"{i+1}", (center_x-8, center_y+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
    
    # 填充实际的图像
    digits_displayed = 0
    for idx, (cropped_img, rect_idx) in enumerate(cropped_images_list):
        if cropped_img is None or cropped_img.size == 0:
            continue
        
        # 确保索引与 rectCoords 一致
        if use_nine_grid and idx >= 9:
            print(f"警告：图像超出九宫格显示范围 ({len(cropped_images_list)} > 9)")
            break
        
        # 🔍 验证索引对应关系
        if GRID_DEBUG:
            print(f"📍 九宫格位置{idx+1}: 矩形R{rect_idx+1} -> ", end="")
        
        # 计算当前图像在网格中的位置
        row = idx // cols
        col = idx % cols
        
        # 🆕 保持长宽比地调整图像尺寸
        resized_img = resize_keep_aspect_ratio(cropped_img, grid_size, 
                                             fill_color=(32, 32, 32), 
                                             show_size_info=True, 
                                             rect_id=f"R{rect_idx+1}")
        
        # 在图像上添加矩形编号
        cv2.putText(resized_img, f"R{rect_idx+1}", (2, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # 🆕 添加数字识别结果显示
        if digit_results and idx < len(digit_results) and digit_results[idx]:
            # 获取该图像的识别结果
            digit_result = digit_results[idx]
            if digit_result:  # 如果有识别结果
                best_digit = max(digit_result, key=lambda x: x['score'])
                digit_text = best_digit['digit']
                confidence = best_digit['score']
                
                # 🔍 验证对应关系
                if GRID_DEBUG:
                    print(f"识别到数字'{digit_text}'({confidence:.2f})")
                
                # 在格子右下角显示识别的数字
                # 计算数字文本尺寸
                text_size = cv2.getTextSize(digit_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                
                # 右下角位置计算（留出边距）
                digit_x = grid_size[0] - text_size[0] - 8
                digit_y = grid_size[1] - 15
                
                # 添加数字背景（深色半透明）
                bg_x1 = digit_x - 3
                bg_y1 = digit_y - text_size[1] - 3
                bg_x2 = digit_x + text_size[0] + 3
                bg_y2 = digit_y + 3
                
                # 绘制背景矩形
                cv2.rectangle(resized_img, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
                cv2.rectangle(resized_img, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 255, 0), 1)
                
                # 绘制识别的数字（绿色字体，右下角）
                cv2.putText(resized_img, digit_text, 
                           (digit_x, digit_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                
                # 在数字下方显示置信度（小字体）
                conf_text = f"{confidence:.2f}"
                conf_x = digit_x + (text_size[0] - cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.3, 1)[0][0]) // 2
                cv2.putText(resized_img, conf_text, 
                           (conf_x, digit_y + 12),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
                
                digits_displayed += 1
        else:
            # 🔍 验证无识别结果的情况
            if GRID_DEBUG:
                if digit_results and idx < len(digit_results):
                    print(f"无识别结果")
                else:
                    print(f"索引超出范围或无digit_results")
        
        # 添加边框 - 使用明亮颜色区分有内容的格子
        cv2.rectangle(resized_img, (0, 0), (grid_size[0]-1, grid_size[1]-1), 
                     (255, 255, 255), 2)
        
        # 放置到网格中
        y_start = row * grid_size[1]
        y_end = y_start + grid_size[1]
        x_start = col * grid_size[0]
        x_end = x_start + grid_size[0]
        
        grid_image[y_start:y_end, x_start:x_end] = resized_img
    
    # 输出九宫格简化统计
    if use_nine_grid and len(cropped_images_list) > 0:
        print(f"九宫格: {len(cropped_images_list)} 图像, {digits_displayed} 数字")
    
    # 在九宫格顶部添加标题信息
    if use_nine_grid:
        total_digits = sum(1 for results in (digit_results or []) if results)
        cv2.putText(grid_image, f"Nine Grid: {len(cropped_images_list)}/9 images, {total_digits} digits", 
                   (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return grid_image

def crop_inner_rect(image, inner_rect):
    """
    裁剪图像中 inner_rect 包围的区域
    
    参数:
        image: 原始图像（OpenCV 的 numpy 数组格式，BGR 或灰度图）
        inner_rect: 由 cv2.boundingRect 得到的矩形元组 (x, y, w, h)
                    - x: 矩形左上角 x 坐标
                    - y: 矩形左上角 y 坐标
                    - w: 矩形宽度
                    - h: 矩形高度
    返回:
        cropped_image: 裁剪后的图像区域（numpy 数组）
    """
    # 解析 inner_rect 的坐标和尺寸
    x, y, w, h = inner_rect
    
    # 确保坐标在图像范围内（避免越界）
    # 获取图像的高度和宽度
    img_h, img_w = image.shape[:2]
    # 计算有效裁剪区域（防止 x、y 为负或超出图像范围）
    x_start = max(0, x)
    y_start = max(0, y)
    x_end = min(img_w, x + w)  # 注意：OpenCV 切片是 [y_start:y_end, x_start:x_end]
    y_end = min(img_h, y + h)
    
    # 裁剪图像（numpy 切片，注意 y 在前，x 在后）
    cropped_image = image[y_start:y_end, x_start:x_end]
    
    return cropped_image


def resize_to_multiple_of_two(image):
    """将图像的宽和高调整为 2 的倍数"""
    h, w = image.shape[:2]
    
    # 计算最接近的 2 的倍数（向上取整）
    new_w = (w + 1) // 2 * 2  # 如 641 → 642，643 → 644
    new_h = (h + 1) // 2 * 2
    
    # 缩放图像
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    return resized

def filter_edge_black_regions(binary_image, edge_ratio=0.05, min_edge_width=5):
    """
    滤除二值化图像边缘的黑色部分，只保留非边缘区域的黑色内容
    
    参数:
        binary_image: 二值化图像（单通道，黑色为0，白色为255）
        edge_ratio: 边缘区域占图像最小边的比例（默认0.05，即5%）
        min_edge_width: 边缘区域的最小宽度（像素，默认5）
    
    返回:
        filtered_binary: 过滤后的二值化图像
        mask: 用于过滤的掩码（可用于调试）
    """
    h, w = binary_image.shape[:2]
    
    # 计算边缘宽度（取比例计算值和最小宽度的最大值）
    min_side = min(w, h)
    edge_width = int(min_side * edge_ratio)
    edge_width = max(edge_width, min_edge_width)  # 确保边缘宽度不小于最小值
    
    # 创建掩码：中心区域为白色（255，保留），边缘区域为黑色（0，过滤）
    mask = np.ones((h, w), dtype=np.uint8) * 255
    mask[:edge_width, :] = 0  # 顶部边缘
    mask[-edge_width:, :] = 0  # 底部边缘
    mask[:, :edge_width] = 0  # 左侧边缘
    mask[:, -edge_width:] = 0  # 右侧边缘
    
    # 应用掩码，保留中心区域的黑色部分
    filtered_binary = cv2.bitwise_and(binary_image, binary_image, mask=mask)
    
    return filtered_binary, mask

def get_innermost_contours(binary_image):
    """
    从二值化图像中提取最内层轮廓（无任何子轮廓的轮廓）
    
    参数:
        binary_image: 二值化图像（单通道，0为背景，255为前景）
    
    返回:
        innermost_contours: 最内层轮廓列表
    """
    # 使用RETR_TREE模式获取所有轮廓及完整层级关系
    contours, hierarchy = cv2.findContours(
        binary_image, 
        cv2.RETR_TREE,  # 建立完整层级结构
        cv2.CHAIN_APPROX_SIMPLE  # 简化轮廓点
    )
    
    innermost_contours = []
    if hierarchy is not None:
        # 遍历所有轮廓，筛选没有子轮廓的轮廓（最内层）
        for i, h in enumerate(hierarchy[0]):
            # hierarchy[0][i][2]表示当前轮廓的第一个子轮廓索引，-1表示无子女
            if h[2] == -1:
                innermost_contours.append(contours[i])
    
    return innermost_contours

def repair_white_region(binary_img, white_threshold=200):
    """将白色区域内的深色像素（数字）转为白色"""
    # 找到白色区域的掩码
    _, white_mask = cv2.threshold(binary_img, 127, 255, cv2.THRESH_BINARY)
    
    # 在白色区域内，将低于阈值的深色像素（数字）转为白色
    result = binary_img.copy()
    result[(white_mask == 255) & (result < white_threshold)] = 255
    return result


def map_crop_to_original(crop_coords, inner_rect):
    """
    将裁剪图像中的坐标映射映射回原始图像的坐标
    
    参数:
        crop_coords: 裁剪图像中的坐标，可以是：
                    - 单个点 (x, y)
                    - 点列表 [(x1, y1), (x2, y2), ...]
                    - 轮廓数组（OpenCV的contour格式）
        inner_rect: 裁剪区域的矩形信息，即cv2.boundingRect返回的(x, y, w, h)
                    其中(x, y)是原始图像中裁剪区域的左上角坐标
    
    返回:
        original_coords: 映射到原始图像后的坐标，格式与输入一致
    """
    # 提取裁剪区域在原始图像中的左上角坐标（偏移量）
    crop_x, crop_y = inner_rect[0], inner_rect[1]
    
    # 处理单个点 (x, y)
    if isinstance(crop_coords, tuple) and len(crop_coords) == 2:
        x, y = crop_coords
        return (x + crop_x, y + crop_y)
    
    # 处理点列表 [(x1, y1), (x2, y2), ...]
    elif isinstance(crop_coords, list) and all(isinstance(p, tuple) and len(p) == 2 for p in crop_coords):
        return [(x + crop_x, y + crop_y) for x, y in crop_coords]
    
    # 处理轮廓（OpenCV contour格式，numpy数组）
    elif isinstance(crop_coords, list) and all(isinstance(c, np.ndarray) for c in crop_coords):
        original_contours = []
        for contour in crop_coords:
            # 轮廓格式为 (N, 1, 2)，需要添加偏移后保持格式
            shifted = contour + np.array([[[crop_x, crop_y]]], dtype=np.int32)
            original_contours.append(shifted)
        return original_contours
    
    # 处理单个轮廓（如从findContours得到的单个轮廓）
    elif isinstance(crop_coords, np.ndarray) and len(crop_coords.shape) == 3:
        return crop_coords + np.array([[[crop_x, crop_y]]], dtype=np.int32)
    
    else:
        raise ValueError("不支持的坐标格式，请输入点、点列表或轮廓数组")

def get_only_largest_white_component(img, inner_rect, kernel_size=3):
    """
    仅提取inner_rect范围内面积最大的**单个**白色连通域，排除其他所有区域
    
    参数:
        img: 输入图像（单通道二值图或三通道彩色图）
        inner_rect: 感兴趣区域(x, y, w, h)
        kernel_size: 形态学操作核大小
    
    返回:
        result: 黑底图像，仅包含唯一最大的白色连通域
    """
    # 1. 处理输入图像得到二值图
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        binary = cv2.bitwise_not(binary)  # 白色为目标
    else:
        binary = img.copy()
    
    # 2. 提取ROI并预处理
    x, y, w, h = inner_rect
    x, y = max(0, x), max(0, y)
    w = min(w, img.shape[1] - x)
    h = min(h, img.shape[0] - y)
    roi = binary[y:y+h, x:x+w]
    
    # 去噪（减少小连通域干扰）
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    roi_clean = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel)  # 先开运算去除小噪点
    
    # 3. 检测所有外轮廓
    contours, _ = cv2.findContours(roi_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. 初始化结果（全黑）
    result = np.zeros_like(img)
    
    if contours:
        # 计算所有轮廓的面积
        contour_areas = [cv2.contourArea(cnt) for cnt in contours]
        
        # 找到面积最大的轮廓的索引（确保只取一个）
        max_area_idx = np.argmax(contour_areas)
        largest_contour = contours[max_area_idx]
        
        # 转换为原始图像坐标
        largest_contour = largest_contour + np.array([[[x, y]]], dtype=np.int32)
        
        # 创建掩码并提取唯一最大区域
        mask = np.zeros(img.shape[:2], np.uint8)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        result[mask == 255] = img[mask == 255]
    
    return result

def get_only_largest_white_component_max(img, kernel_size=3):
    """
    仅提取整个图像范围内面积最大的**单个**白色连通域，排除其他所有区域
    
    参数:
        img: 输入图像（单通道二值图或三通道彩色图）
        kernel_size: 形态学操作核大小（用于去噪）
    
    返回:
        result: 黑底图像，仅包含唯一最大的白色连通域（无白色区域则返回全黑）
    """
    # 1. 处理输入图像得到二值图（白色为目标区域）
    if len(img.shape) == 3:
        # 彩色图转灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 大津法自动阈值二值化（分离黑白区域）
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # 反转二值图：确保目标白色区域为255，背景为0
        binary = cv2.bitwise_not(binary)
    else:
        # 单通道图像直接复制（假设已为二值图）
        binary = img.copy()
    
    # 2. 预处理：去噪（去除小面积噪声干扰）
    # 创建形态学操作核
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    # 开运算：先腐蚀后膨胀，去除微小白色噪点
    img_clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # 3. 检测所有外轮廓（只关注最外层轮廓，忽略嵌套轮廓）
    # RETR_EXTERNAL：只提取最外层轮廓
    # CHAIN_APPROX_SIMPLE：简化轮廓，保留关键顶点
    contours, _ = cv2.findContours(img_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. 初始化结果图像（全黑背景）
    result = np.zeros_like(img)
    
    # 5. 筛选面积最大的白色连通域
    if contours:  # 若存在轮廓
        # 计算每个轮廓的面积
        contour_areas = [cv2.contourArea(cnt) for cnt in contours]
        
        # 找到面积最大的轮廓索引
        max_area_idx = np.argmax(contour_areas)
        largest_contour = contours[max_area_idx]
        
        # 创建掩码：用于标记最大连通域
        mask = np.zeros(img.shape[:2], np.uint8)
        # 在掩码上填充最大轮廓区域（白色255）
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        
        # 将原图中最大连通域的像素提取到结果图像
        # 彩色图：保留原始颜色；单通道图：保留灰度值
        result[mask == 255] = img[mask == 255]
    else:
        # 没有找到轮廓时，返回全黑图像
        print("警告：get_only_largest_white_component_max未找到任何轮廓")
    
    return result

def fill_holes_in_white(binary_img):
    """填充白色区域内的所有孔洞（无论大小）"""
    # 找到白色区域的外轮廓
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return binary_img
    
    # 填充外轮廓内的所有孔洞（子轮廓）
    mask = np.zeros_like(binary_img)
    for i, h in enumerate(hierarchy[0]):
        # 外轮廓（没有父轮廓）
        if h[3] == -1:
            # 填充外轮廓及其内部所有孔洞
            cv2.drawContours(mask, contours, i, 255, -1)
    
    return mask

def parse_length_str(length_str):
    """
    将带单位的长度字符串（如'11.60cm'）解析为数值类型
    
    参数:
        length_str: 带单位的长度字符串
    返回:
        float: 解析后的数值
    """
    # 提取字符串中的数字部分（包括小数点）
    numeric_part = ''.join([c for c in length_str if c.isdigit() or c == '.'])
    
    # 转换为浮点数
    try:
        return float(numeric_part)
    except ValueError:
        # 处理转换失败的情况（如字符串格式错误）
        return None

# 计算图像按键到屏幕的映射关系（解决触摸不准问题）
btn_var1_add_disp = image.resize_map_pos(
    img_width, img_height, disp.width(), disp.height(),
    image.Fit.FIT_CONTAIN,
    btn_var1_add[0], btn_var1_add[1], btn_var1_add[2], btn_var1_add[3]
)
btn_var1_sub_disp = image.resize_map_pos(
    img_width, img_height, disp.width(), disp.height(),
    image.Fit.FIT_CONTAIN,
    btn_var1_sub[0], btn_var1_sub[1], btn_var1_sub[2], btn_var1_sub[3]
)
btn_var2_add_disp = image.resize_map_pos(
    img_width, img_height, disp.width(), disp.height(),
    image.Fit.FIT_CONTAIN,
    btn_var2_add[0], btn_var2_add[1], btn_var2_add[2], btn_var2_add[3]
)
btn_var2_sub_disp = image.resize_map_pos(
    img_width, img_height, disp.width(), disp.height(),
    image.Fit.FIT_CONTAIN,
    btn_var2_sub[0], btn_var2_sub[1], btn_var2_sub[2], btn_var2_sub[3]
)

def is_in_button(x, y, btn_disp_pos):
    """检查触摸点是否在屏幕上的按键区域内"""
    return (x > btn_disp_pos[0] and 
            x < btn_disp_pos[0] + btn_disp_pos[2] and 
            y > btn_disp_pos[1] and 
            y < btn_disp_pos[1] + btn_disp_pos[3])

def draw_buttons_opencv(img_cv):
    """在OpenCV图像上绘制按键和变量值"""
    # 绘制左侧var1控制按键
    cv2.rectangle(img_cv, 
                 (btn_var1_add[0], btn_var1_add[1]),
                 (btn_var1_add[0] + btn_var1_add[2], btn_var1_add[1] + btn_var1_add[3]),
                 (0, 255, 0), 3)  # 绿色矩形
    cv2.putText(img_cv, "+1", 
               (btn_var1_add[0] + 35, btn_var1_add[1] + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # 绿色文字
    
    cv2.rectangle(img_cv, 
                 (btn_var1_sub[0], btn_var1_sub[1]),
                 (btn_var1_sub[0] + btn_var1_sub[2], btn_var1_sub[1] + btn_var1_sub[3]),
                 (0, 0, 255), 3)  # 红色矩形
    cv2.putText(img_cv, "-1", 
               (btn_var1_sub[0] + 35, btn_var1_sub[1] + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # 红色文字
    
    # 显示var1值
    cv2.putText(img_cv, f"Var1: {var1}", 
               (btn_var1_add[0], btn_var1_sub[1] + btn_var1_sub[3] + 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # 白色文字
    
    # 绘制右侧var2控制按键
    cv2.rectangle(img_cv, 
                 (btn_var2_add[0], btn_var2_add[1]),
                 (btn_var2_add[0] + btn_var2_add[2], btn_var2_add[1] + btn_var2_add[3]),
                 (0, 255, 0), 3)  # 绿色矩形
    cv2.putText(img_cv, "+1", 
               (btn_var2_add[0] + 35, btn_var2_add[1] + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # 绿色文字
    
    cv2.rectangle(img_cv, 
                 (btn_var2_sub[0], btn_var2_sub[1]),
                 (btn_var2_sub[0] + btn_var2_sub[2], btn_var2_sub[1] + btn_var2_sub[3]),
                 (0, 0, 255), 3)  # 红色矩形
    cv2.putText(img_cv, "-1", 
               (btn_var2_sub[0] + 35, btn_var2_sub[1] + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # 红色文字
    
    # 显示var2值
    cv2.putText(img_cv, f"Var2: {var2}", 
               (btn_var2_add[0], btn_var2_sub[1] + btn_var2_sub[3] + 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # 白色文字
    
    return img_cv

def handle_touch(x, y):
    """处理触摸事件，更新变量值并打印当前值"""
    global var1, var2, focalLength, Width_value
    
    if is_in_button(x, y, btn_var1_add_disp):
        focalLength += 1
        print(f"focalLength 已更新: {focalLength}")
        sys.stdout.flush()
        time.sleep_ms(200)  # 防抖处理
    elif is_in_button(x, y, btn_var1_sub_disp):
        focalLength -= 1
        print(f"focalLength 已更新: {focalLength}")
        sys.stdout.flush()
        time.sleep_ms(200)
    elif is_in_button(x, y, btn_var2_add_disp):
        Width_value += 0.1
        print(f"Width_value 已更新: {Width_value}")
        sys.stdout.flush()
        time.sleep_ms(200)
    elif is_in_button(x, y, btn_var2_sub_disp):
        Width_value -= 0.1
        print(f"Width_value 已更新: {Width_value}")
        sys.stdout.flush()
        time.sleep_ms(200)
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
# 主循环
while not app.need_exit():
    time1 = time.time()

    img = cam.read()
    img = img.rotate(90)
    
    img_cv = image.image2cv(img, ensure_bgr=False, copy=False)

    

    # 克隆原始帧用于显示结果
    display_frame = img_cv.copy()

    #结果图像
    result_img = img_cv.copy()
    ######################################################初始模式手动校准模式###############################################
    if MODE == -1:
        print("校准")
        # 预处理
        edges, gray_eq = preprocess_image(img_cv)

        # 查找所有轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 检测外层矩形（marker）
        marker = find_min_marker(contours)
        distance = None
        marker_long_side_actual = 25.5   # 内矩形较长边的实际长度（单位：cm）
        marker_long_side_pixel = 0      # 内矩形较长边的像素长度

        
        # 过滤marker范围外的轮廓
        marker_bbox = None
        if marker:
            box = cv2.boxPoints(marker)
            box = np.intp(box)  # 替换np.int0为np.intp，避免 deprecated 警告

            # 计算原始标记物的最小/最大坐标
            x_min_orig, y_min_orig = np.min(box, axis=0)
            x_max_orig, y_max_orig = np.max(box, axis=0)
            
            # 计算标记物中心坐标
            center_x = (x_min_orig + x_max_orig) / 2
            center_y = (y_min_orig + y_max_orig) / 2

            # 计算原始宽度和高度
            width_orig = x_max_orig - x_min_orig
            height_orig = y_max_orig - y_min_orig

            # 扩大1.1倍（在中心不变的情况下扩展边界）
            expand_ratio = 1.2                      ##############################
            new_width = width_orig * expand_ratio
            new_height = height_orig * expand_ratio
            
            # 计算扩大后的边界框坐标
            x_min = int(center_x - new_width / 2)
            y_min = int(center_y - new_height / 2)
            x_max = int(center_x + new_width / 2)
            y_max = int(center_y + new_height / 2)
            
            # 确保边界框不超出图像范围
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(img_cv.shape[1], x_max)
            y_max = min(img_cv.shape[0], y_max)

            marker_bbox = (x_min, y_min, x_max, y_max)
            

            # 计算内矩形较长边的像素长度
            marker_width, marker_height = marker[1][0], marker[1][1]
            marker_long_side_pixel = max(marker_width, marker_height)
        
        filtered_contours = []
        for cnt in contours:
            if cv2.contourArea(cnt) < params['inner_rect_area']:
                continue
            
            if not marker_bbox:
                filtered_contours.append(cnt)
                continue
            
            cnt_points = cnt.reshape(-1, 2)
            x_min_cnt, y_min_cnt = np.min(cnt_points, axis=0)
            x_max_cnt, y_max_cnt = np.max(cnt_points, axis=0)
            
            # 判断轮廓是否完全在标记物内部
            is_inside = (
                x_min_cnt >= marker_bbox[0] and  # 轮廓左边界在标记物左边界右侧
                x_max_cnt <= marker_bbox[2] and  # 轮廓右边界在标记物右边界左侧
                y_min_cnt >= marker_bbox[1] and  # 轮廓上边界在标记物上边界下方
                y_max_cnt <= marker_bbox[3]      # 轮廓下边界在标记物下边界上方
            )
            
            if is_inside:
                filtered_contours.append(cnt)
        
        contours = filtered_contours
        
        shapes = {'triangles': [], 'squares': [], 'circles': []}

        # print(f"过滤后轮廓数量: {len(contours)}")

        
            
        if marker:
            distance = distance_to_camera(KNOWN_WIDTH, focalLength, min(marker[1][0], marker[1][1]))
            # print(f"内矩形宽像素: {marker[1][0]}, 高像素: {marker[1][1]}")
            # print(f"内矩形较长边像素: {marker_long_side_pixel}")

            #计算长宽比例
            aspect_ratio = max(marker[1][0], marker[1][1])/min(marker[1][0], marker[1][1])
            # print(f"长宽比例: {max(marker[1][0], marker[1][1])/min(marker[1][0], marker[1][1])}")


            #以下是平视代码
            
            # 将 marker 的边界框转换为轮廓点集（approx 格式）
            box = cv2.boxPoints(marker)  # 获取 marker 的四个顶点
            marker_contour = np.intp(box).reshape(-1, 1, 2)  # 转换为 (n,1,2) 格式的轮廓
            inner_rect = cv2.boundingRect(marker_contour)

            # 构建 inner_rect_info 字典
            inner_rect_info = {
                "approx": marker_contour  # 存储 marker 的轮廓点集
            }



            # #----------------------------------------------------------------------------------------------------
            # #以下是平视面积法测量（目前精准度不高）


            # # 在Inner Rect内检测各种形状
            # shapes = detect_shapes_in_rect(contours)

                
            # # 绘制结果
            # result_img = draw_results(img_cv, marker, inner_rect_info, shapes)

            # #结果
            # shape_results = mode1_result(inner_rect_info, shapes)
            # for i, shape in enumerate(shape_results, 1):
            #     # print(f"第{i}个形状：类型={shape['type']}，尺寸={shape['size']}")

            #     cv2.putText(result_img, f"{shape['size']}", 
            #         (result_img.shape[1]-240, 70),
            #         cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)

            # 显示距离
            cv2.putText(result_img, f"{distance:.2f}", 
                    (result_img.shape[1]-470, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 6)

            cv2.putText(result_img, f"focalLength:{focalLength:.0f}", 
                    (result_img.shape[1]-470, 550),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (250, 0, 0), 6)
            cv2.putText(result_img, f"Width_value:{Width_value:.1f}", 
                    (result_img.shape[1]-470, 600),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (250, 0, 0), 6)
            Width_value


            # 检测内部形状并计算尺寸（支持正方形、等边三角形和圆形）
            if contours and marker_long_side_pixel > 0:
                for cnt in contours:
                    shape = detect_shape(cnt)
                    
                    # 处理正方形
                    if shape == "Square":
                        rect = cv2.minAreaRect(cnt)
                        square_width, square_height = rect[1]
                        square_side_pixel = min(square_width, square_height)
                        
                        square_side_actual = (square_side_pixel / marker_long_side_pixel) * marker_long_side_actual
                        
                        box = cv2.boxPoints(rect)
                        box = np.intp(box)
                        cv2.drawContours(result_img, [box], -1, (255, 0, 0), 2)
                        
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            cv2.putText(result_img, f"Square: {square_side_actual:.2f}cm", 
                                    (cX-50, cY+30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                            cv2.putText(result_img, f"{square_side_actual:.2f}cm", 
                                    (result_img.shape[1]-240, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
                        
                        # print(f"正方形像素边长: {square_side_pixel:.1f}, 实际边长: {square_side_actual:.2f}cm")
                    
                    # 处理等边三角形
                    elif shape in ["Equilateral Triangle", "Triangle"]:
                        perimeter = cv2.arcLength(cnt, True)
                        epsilon = 0.03 * perimeter
                        approx = cv2.approxPolyDP(cnt, epsilon, True)
                        
                        if len(approx) == 3:
                            vertices = [tuple(point[0]) for point in approx]
                            
                            def distance_pixel(p1, p2):
                                return math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                            
                            side1 = distance_pixel(vertices[0], vertices[1])
                            side2 = distance_pixel(vertices[1], vertices[2])
                            side3 = distance_pixel(vertices[2], vertices[0])
                            
                            triangle_side_pixel = (side1 + side2 + side3) / 3
                            triangle_side_actual = (triangle_side_pixel / marker_long_side_pixel) * marker_long_side_actual
                            
                            cv2.drawContours(result_img, [cnt], -1, (0, 165, 255), 2)
                            for (x, y) in vertices:
                                cv2.circle(result_img, (x, y), 5, (0, 0, 255), -1)
                            
                            M = cv2.moments(cnt)
                            if M["m00"] != 0:
                                cX = int(M["m10"] / M["m00"])
                                cY = int(M["m01"] / M["m00"])
                                cv2.putText(result_img, f"Triangle: {triangle_side_actual:.2f}cm", 
                                        (cX-50, cY+30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                                cv2.putText(result_img, f"{triangle_side_actual:.2f}cm", 
                                    (result_img.shape[1]-240, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
                            
                            print(f"三角形像素边长: {triangle_side_pixel:.1f}, 实际边长: {triangle_side_actual:.2f}cm")
                    
                    # 处理圆形（新增：测量直径）
                    elif shape == "Circle":
                        # 使用最小外接圆获取圆心和半径
                        (x, y), radius = cv2.minEnclosingCircle(cnt)
                        center = (int(x), int(y))
                        radius_pixel = int(radius)
                        diameter_pixel = radius_pixel * 2  # 直径 = 半径 * 2
                        
                        # 计算实际直径
                        diameter_actual = (diameter_pixel / marker_long_side_pixel) * marker_long_side_actual
                        
                        # 绘制圆形和直径线
                        cv2.circle(result_img, center, radius_pixel, (0, 255, 0), 2)  # 绘制圆形
                        # 绘制一条水平直径线（便于可视化）
                        cv2.line(result_img, 
                                (center[0] - radius_pixel, center[1]), 
                                (center[0] + radius_pixel, center[1]), 
                                (0, 255, 0), 2)
                        
                        # 显示直径信息
                        cv2.putText(result_img, f"Circle: {diameter_actual:.2f}cm", 
                                (center[0]-50, center[1]+30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                        cv2.putText(result_img, f"{diameter_actual:.2f}cm", 
                                (result_img.shape[1]-240, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
                        
                        print(f"圆形像素直径: {diameter_pixel:.1f}, 实际直径: {diameter_actual:.2f}cm")
                    
                    # 处理其他形状
                    elif shape != "Unknown" and shape != "Rectangle":
                        color = (255, 0, 0)
                        cv2.drawContours(result_img, [cnt], -1, color, 2)
                        
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            cv2.putText(result_img, shape, (cX-20, cY),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                
            
            # 显示参数信息
            param_text = f"Th1:{params['canny_th1']} Th2:{params['canny_th2']}"
            cv2.putText(result_img, param_text, (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            
        
        # 处理触摸事件
        x, y, pressed = ts.read()
        if pressed:  # 只有在触摸按下时才处理
            handle_touch(x, y)
    #######################################################模式0休眠模式#################################################
    elif MODE == 0:
        print("休眠")
    #######################################################模式1基础模式##################################################
    elif MODE == 1:
        # 预处理
        edges, gray_eq = preprocess_image(img_cv)

        # 查找所有轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 检测外层矩形（marker）
        marker = find_min_marker(contours)
        distance = None
        marker_long_side_actual = 25.5   # 内矩形较长边的实际长度（单位：cm）
        marker_long_side_pixel = 0      # 内矩形较长边的像素长度

        
        # 过滤marker范围外的轮廓
        marker_bbox = None
        if marker:
            box = cv2.boxPoints(marker)
            box = np.intp(box)  # 替换np.int0为np.intp，避免 deprecated 警告

            # 计算原始标记物的最小/最大坐标
            x_min_orig, y_min_orig = np.min(box, axis=0)
            x_max_orig, y_max_orig = np.max(box, axis=0)
            
            # 计算标记物中心坐标
            center_x = (x_min_orig + x_max_orig) / 2
            center_y = (y_min_orig + y_max_orig) / 2

            # 计算原始宽度和高度
            width_orig = x_max_orig - x_min_orig
            height_orig = y_max_orig - y_min_orig

            # 扩大1.1倍（在中心不变的情况下扩展边界）
            expand_ratio = 1.2                      ##############################
            new_width = width_orig * expand_ratio
            new_height = height_orig * expand_ratio
            
            # 计算扩大后的边界框坐标
            x_min = int(center_x - new_width / 2)
            y_min = int(center_y - new_height / 2)
            x_max = int(center_x + new_width / 2)
            y_max = int(center_y + new_height / 2)
            
            # 确保边界框不超出图像范围
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(img_cv.shape[1], x_max)
            y_max = min(img_cv.shape[0], y_max)

            marker_bbox = (x_min, y_min, x_max, y_max)
            

            # 计算内矩形较长边的像素长度
            marker_width, marker_height = marker[1][0], marker[1][1]
            marker_long_side_pixel = max(marker_width, marker_height)
        
        filtered_contours = []
        for cnt in contours:
            if cv2.contourArea(cnt) < params['inner_rect_area']:
                continue
            
            if not marker_bbox:
                filtered_contours.append(cnt)
                continue
            
            cnt_points = cnt.reshape(-1, 2)
            x_min_cnt, y_min_cnt = np.min(cnt_points, axis=0)
            x_max_cnt, y_max_cnt = np.max(cnt_points, axis=0)
            
            # 判断轮廓是否完全在标记物内部
            is_inside = (
                x_min_cnt >= marker_bbox[0] and  # 轮廓左边界在标记物左边界右侧
                x_max_cnt <= marker_bbox[2] and  # 轮廓右边界在标记物右边界左侧
                y_min_cnt >= marker_bbox[1] and  # 轮廓上边界在标记物上边界下方
                y_max_cnt <= marker_bbox[3]      # 轮廓下边界在标记物下边界上方
            )
            
            if is_inside:
                filtered_contours.append(cnt)
        
        contours = filtered_contours
        
        shapes = {'triangles': [], 'squares': [], 'circles': []}

        # print(f"过滤后轮廓数量: {len(contours)}")

        
            
        if marker:
            distance = distance_to_camera(KNOWN_HEIGHT, focalLength, max(marker[1][0], marker[1][1]))
            print(f"内矩形宽像素: {marker[1][0]}, 高像素: {marker[1][1]}")
            # print(f"内矩形较长边像素: {marker_long_side_pixel}")

            #计算长宽比例
            aspect_ratio = max(marker[1][0], marker[1][1])/min(marker[1][0], marker[1][1])
            print(f"长宽比例: {max(marker[1][0], marker[1][1])/min(marker[1][0], marker[1][1])}")


            #以下是平视代码
            
            # 将 marker 的边界框转换为轮廓点集（approx 格式）
            box = cv2.boxPoints(marker)  # 获取 marker 的四个顶点
            marker_contour = np.intp(box).reshape(-1, 1, 2)  # 转换为 (n,1,2) 格式的轮廓
            inner_rect = cv2.boundingRect(marker_contour)

            # 构建 inner_rect_info 字典
            inner_rect_info = {
                "approx": marker_contour  # 存储 marker 的轮廓点集
            }



            # #----------------------------------------------------------------------------------------------------
            # #以下是平视面积法测量（目前精准度不高）


            # # 在Inner Rect内检测各种形状
            # shapes = detect_shapes_in_rect(contours)

            # # 统计形状数量
            # total_shapes = len(shapes['triangles']) + len(shapes['squares']) + len(shapes['circles'])
            
            # # print(f"   └─ 三角形: {len(shapes['triangles'])}个, 正方形: {len(shapes['squares'])}个, 圆形: {len(shapes['circles'])}个")

            # if total_shapes > 0:
            #     print()
                
            # # 绘制结果
            # result_img = draw_results(img_cv, marker, inner_rect_info, shapes)

            # #结果
            # shape_results = mode1_result(inner_rect_info, shapes)
            # for i, shape in enumerate(shape_results, 1):
            #     print(f"第{i}个形状：类型={shape['type']}，尺寸={shape['size']}")

            # # 显示距离
            # cv2.putText(result_img, f"{distance:.2f}cm", 
            #         (result_img.shape[1]-150, 30),
            #         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            # 检测内部形状并计算尺寸（支持正方形、等边三角形和圆形）
            shape_results11 = 0
            if contours and marker_long_side_pixel > 0:
                for cnt in contours:
                    shape = detect_shape(cnt)
                    
                    # 处理正方形
                    if shape == "Square":
                        rect = cv2.minAreaRect(cnt)
                        square_width, square_height = rect[1]
                        square_side_pixel = min(square_width, square_height)
                        
                        square_side_actual = (square_side_pixel / marker_long_side_pixel) * marker_long_side_actual
                        
                        box = cv2.boxPoints(rect)
                        box = np.intp(box)
                        cv2.drawContours(result_img, [box], -1, (255, 0, 0), 2)
                        
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            cv2.putText(result_img, f"Square: {square_side_actual:.2f}cm", 
                                    (cX-50, cY+30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                            cv2.putText(result_img, f"{square_side_actual:.2f}cm", 
                                    (result_img.shape[1]-240, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
                        
                        print(f"正方形像素边长: {square_side_pixel:.1f}, 实际边长: {square_side_actual:.2f}cm")
                        shape_results11 = square_side_actual
                    
                    # 处理等边三角形
                    elif shape in ["Equilateral Triangle", "Triangle"]:
                        perimeter = cv2.arcLength(cnt, True)
                        epsilon = 0.03 * perimeter
                        approx = cv2.approxPolyDP(cnt, epsilon, True)
                        
                        if len(approx) == 3:
                            vertices = [tuple(point[0]) for point in approx]
                            
                            def distance_pixel(p1, p2):
                                return math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                            
                            side1 = distance_pixel(vertices[0], vertices[1])
                            side2 = distance_pixel(vertices[1], vertices[2])
                            side3 = distance_pixel(vertices[2], vertices[0])
                            
                            triangle_side_pixel = (side1 + side2 + side3) / 3
                            triangle_side_actual = (triangle_side_pixel / marker_long_side_pixel) * marker_long_side_actual
                            
                            cv2.drawContours(result_img, [cnt], -1, (0, 165, 255), 2)
                            for (x, y) in vertices:
                                cv2.circle(result_img, (x, y), 5, (0, 0, 255), -1)
                            
                            M = cv2.moments(cnt)
                            if M["m00"] != 0:
                                cX = int(M["m10"] / M["m00"])
                                cY = int(M["m01"] / M["m00"])
                                cv2.putText(result_img, f"Triangle: {triangle_side_actual:.2f}cm", 
                                        (cX-50, cY+30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                                cv2.putText(result_img, f"{triangle_side_actual:.2f}cm", 
                                    (result_img.shape[1]-240, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
                            
                            print(f"三角形像素边长: {triangle_side_pixel:.1f}, 实际边长: {triangle_side_actual:.2f}cm")
                            shape_results11 = triangle_side_actual + 0.5
                    
                    # 处理圆形（新增：测量直径）
                    elif shape == "Circle":
                        # 使用最小外接圆获取圆心和半径
                        (x, y), radius = cv2.minEnclosingCircle(cnt)
                        center = (int(x), int(y))
                        radius_pixel = int(radius)
                        diameter_pixel = radius_pixel * 2  # 直径 = 半径 * 2
                        
                        # 计算实际直径
                        diameter_actual = (diameter_pixel / marker_long_side_pixel) * marker_long_side_actual
                        
                        # 绘制圆形和直径线
                        cv2.circle(result_img, center, radius_pixel, (0, 255, 0), 2)  # 绘制圆形
                        # 绘制一条水平直径线（便于可视化）
                        cv2.line(result_img, 
                                (center[0] - radius_pixel, center[1]), 
                                (center[0] + radius_pixel, center[1]), 
                                (0, 255, 0), 2)
                        
                        # 显示直径信息
                        cv2.putText(result_img, f"Circle: {diameter_actual:.2f}cm", 
                                (center[0]-50, center[1]+30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                        cv2.putText(result_img, f"{diameter_actual:.2f}cm", 
                                (result_img.shape[1]-240, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
                        
                        print(f"圆形像素直径: {diameter_pixel:.1f}, 实际直径: {diameter_actual:.2f}cm")
                        shape_results11 = diameter_actual
                    
                    # 处理其他形状
                    elif shape != "Unknown" and shape != "Rectangle":
                        color = (255, 0, 0)
                        cv2.drawContours(result_img, [cnt], -1, color, 2)
                        
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            cv2.putText(result_img, shape, (cX-20, cY),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            ###############################串口发送实际数据指令############################################
            # print(shape_results11)
            # print(11111111111111111111111111111111111111)

            if shape_results11:
                shapeWidth = shape_results11*10 + Width_value
                print(int(distance), int(shapeWidth))
                uart_sendCommand(int(distance) * 10, int(shapeWidth))
                switchToMode0() 
            ####################################阻塞等待回模式0###########################################


    #############################################模式2发挥题###########################################
    elif MODE == 2 or MODE == 4:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, params['canny_th1'], params['canny_th2'])

        # 查找所有轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rectangle_count = 0
        valid_rectangles_info = []
        # 第一轮：收集可能的矩形轮廓（用于确定Inner Rect）
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 5000:  # 过滤过小轮廓
                continue
            
            is_rect, approx_rect = is_rectangle(contour)
            is_sq, approx_sq = is_square(contour)
            
            if is_rect or is_sq:
                approx = approx_rect if is_rect else approx_sq
                aspect_ratio = calculate_aspect_ratio(approx)
                ratio_valid = is_aspect_ratio_valid(aspect_ratio)
                
                valid_rectangles_info.append({
                    "contour": contour,
                    "is_rectangle": is_rect,
                    "approx": approx,
                    "area": area,
                    "keep": True,
                    "aspect_ratio": aspect_ratio,
                    "ratio_valid": ratio_valid
                })

        # 第二轮：过滤重叠矩形（确定Inner Rect）
        n = len(valid_rectangles_info)
        for i in range(n):
            info1 = valid_rectangles_info[i]
            if not info1["keep"]:
                continue
            rect1 = cv2.boundingRect(info1["approx"])
            area1 = info1["area"]
            rect1_area = rect1[2] * rect1[3]
            rect1_metric = area1 / rect1_area if rect1_area > 0 else 0
            
            for j in range(i + 1, n):
                info2 = valid_rectangles_info[j]
                if not info2["keep"]:
                    continue
                rect2 = cv2.boundingRect(info2["approx"])
                area2 = info2["area"]
                rect2_area = rect2[2] * rect2[3]
                rect2_metric = area2 / rect2_area if rect2_area > 0 else 0
                
                if calculate_iou(rect1, rect2) > 0.8:
                    if (area1 > area2 * 1.2) or (rect1_metric > rect2_metric + 0.1):
                        info2["keep"] = False
                    else:
                        info1["keep"] = False
                        break

        filtered_rectangles = [info for info in valid_rectangles_info if info["keep"]]

        # 打印所有检测到的矩形的长宽比及有效性
        print("\n===== 检测到的矩形信息 =====")
        print(f"长宽比阈值范围: {ASPECT_RATIO_LOWER} - {ASPECT_RATIO_UPPER}")
        for i, info in enumerate(filtered_rectangles):
            rect_type = "长方形" if info["is_rectangle"] else "正方形"
            validity = "有效" if info["ratio_valid"] else "无效"
            print(f"矩形 {i+1}: 类型={rect_type}, 面积={info['area']:.2f} px², 长宽比={info['aspect_ratio']:.4f}, {validity}")

        # 透视变换及内部轮廓检测（所有类型）
        warped_inner = None
        transform_matrix = None
        M_inv = None
        warped_contours = []  # 存储变换后图像中检测到的所有轮廓
        distance_text = ""

        # 判断轮廓是否在指定矩形内部的辅助函数
        def is_contour_inside_rect(contour, rect):
            x, y, w, h = rect
            # 获取轮廓的所有点
            points = contour.reshape(-1, 2)
            # 检查所有点是否在矩形内部
            for (px, py) in points:
                if not (x <= px <= x + w and y <= py <= y + h):
                    return False
            return True

        # 确定Inner Rect并执行透视变换
        rect_only = [info for info in filtered_rectangles if info["is_rectangle"] and info["ratio_valid"]]
        if rect_only:
            inner_rect_info = min(rect_only, key=lambda x: x["area"])
            inner_approx = inner_rect_info["approx"]
            inner_rect = cv2.boundingRect(inner_approx)
            x_inner, y_inner, w_inner, h_inner = inner_rect
            
            # 过滤只保留inner rect内部的轮廓
            filtered_rectangles = [
                info for info in filtered_rectangles
                if is_contour_inside_rect(info["contour"], (x_inner, y_inner, w_inner, h_inner))
            ]

            # 计算Inner Rect尺寸和距离
            width_px, height_px = calculate_inner_rect_size(inner_approx)


            # 计算Inner Rect的长边像素长度及实际距离
            sides = calculate_side_lengths(inner_approx)  # 四条边的像素长度
            avg_long_px = get_long_sides_average(sides)   # 两长边和的二分之一
            distance_cm = distance_to_camera(KNOWN_HEIGHT, focalLength2, avg_long_px) # 计算实际距离
            
            
            # 打印Inner Rect信息
            print("\n===== Inner Rect 信息 =====")
            print(f"Inner Rect尺寸: 宽度={width_px:.2f}像素, 高度={height_px:.2f}像素")
            print(f"Inner Rect长宽比: {inner_rect_info['aspect_ratio']:.4f} (在阈值范围内)")
            
            # 在图像上显示Inner Rect信息
            cv2.putText(display_frame, f"Distance: {distance_cm:.1f} cm", 
                    (x_inner, y_inner + h_inner + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 绘制Inner Rect
            cv2.drawContours(display_frame, [inner_approx], -1, (0, 0, 255), 3)
            cv2.putText(display_frame, "Inner Rect", (x_inner, y_inner - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 执行透视变换
            inner_pts = inner_approx.reshape(4, 2).astype("float32")
            src_pts = order_points(inner_pts)
            dst_pts = np.array([
                [0, 0],
                [TARGET_WIDTH - 1, 0],
                [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
                [0, TARGET_HEIGHT - 1]], dtype="float32")
            
            transform_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
            warped_inner = cv2.warpPerspective(img_cv, transform_matrix, (TARGET_WIDTH, TARGET_HEIGHT))
            M_inv = cv2.getPerspectiveTransform(dst_pts, src_pts)
            
            # 在原始图像上绘制所有变换后的轮廓
            if M_inv is not None and warped_contours:
                draw_warped_contours_on_original(display_frame, warped_contours, M_inv)
        else:
            # 没有符合要求的Inner Rect
            print("\n未检测到符合长宽比要求的Inner Rect")
            cv2.putText(display_frame, f"No valid Inner Rect (AR: {ASPECT_RATIO_LOWER}-{ASPECT_RATIO_UPPER})", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # 绘制原始图像中的矩形，用不同颜色标记有效性
        for info in filtered_rectangles:
            rectangle_count += 1
            color = (0, 255, 0) if info["ratio_valid"] else (0, 165, 255)
            cv2.drawContours(display_frame, [info["approx"]], -1, color, 2)
            x, y, _, _ = cv2.boundingRect(info["approx"])
            cv2.putText(display_frame, f"AR: {info['aspect_ratio']:.2f}", 
                    (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            validity_text = "Valid" if info["ratio_valid"] else "Invalid"
            cv2.putText(display_frame, validity_text, 
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        # 显示原始图像信息
        cv2.putText(display_frame, f"Rectangles: {rectangle_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        #以下是重叠代码
        #----------------------------------------------------------------------------------------------------
        # 安全检查：确保warped_inner存在且有效
        if warped_inner is not None and warped_inner.size > 0:
            print(f"🔍 开始处理透视变换后的图像，尺寸: {warped_inner.shape}")
            cropImage = warped_inner
            # print(cropImage.shape)
            showImage = warped_inner
            
            gray = cv2.cvtColor(warped_inner, cv2.COLOR_BGR2GRAY)
            threshold, binary_image = cv2.threshold(
                gray, 
                0,                  # 初始阈值（无意义，大津法会覆盖）
                255,                # 最大值（超过阈值的像素设为255）
                cv2.THRESH_BINARY + cv2.THRESH_OTSU  # 大津法+二值化
            )
            binary = cv2.bitwise_not(binary_image)
            # 安全检查：确保newImage不是None
            if binary is not None:
                newImage = fill_holes_in_white(binary)
                contour = get_innermost_contours(newImage)
                rectCoords = detector.DEBUG_FindIOURects(contour, newImage, frame = warped_inner)
            else:
                print("错误：get_only_largest_white_component_max返回None，跳过后续处理")
                rectCoords = []
                
            # remapCoords = map_crop_to_original(rectCoords, inner_rect)
            showImage = detector.testImage
            print(f"🔍 在透视变换图像中检测到 {len(rectCoords)} 个矩形")
            
            for coord_idx, quad_array in enumerate(rectCoords):
                # 直接处理不同可能的数组形状，避免squeeze错误
                # 去除所有大小为1的维度
                points = np.squeeze(quad_array)
                
                # 确保是二维数组 (n, 2)
                if len(points.shape) != 2:
                    print(f"警告：第 {coord_idx} 个四边形坐标维度错误，形状为 {points.shape}")
                    continue
                
                # 验证是否有4个点
                if points.shape[0] == 4:
                    # 绘制四边形（连接4个点形成闭合图形）
                    for i in range(4):
                        pt1 = tuple(points[i])
                        pt2 = tuple(points[(i + 1) % 4])  # 最后一个点连接回第一个点
                        cv2.line(warped_inner, pt1, pt2, color=(0, 255, 0), thickness=3)
                    
                    # 在矩形中心添加编号标识
                    center_x = int(np.mean(points[:, 0]))
                    center_y = int(np.mean(points[:, 1]))
                    cv2.putText(warped_inner, f"R{coord_idx+1}", (center_x-15, center_y+5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    cv2.circle(warped_inner, (center_x, center_y), 5, (255, 255, 0), -1)
                else:
                    print(f"警告：第 {coord_idx} 个四边形坐标格式不正确，包含 {points.shape[0]} 个点（预期4个）")
            
            # 在warped图像上添加检测统计信息
            if len(rectCoords) > 0:
                cv2.putText(warped_inner, f"Detected: {len(rectCoords)} Rectangles", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # 添加安全检查：确保newImage不是None
            if newImage is not None:
                resize = resize_to_multiple_of_two(newImage)
            else:
                print("警告：newImage为None，跳过resize处理")
        else:
            print("⚠️  警告：warped_inner为None或空图像，跳过透视变换图像处理")
            print("   这通常是因为没有检测到符合长宽比要求的Inner Rect")
            rectCoords = []
        
        # MaixCAM智能显示选择
        if warped_inner is not None and warped_inner.size > 0:
            # 如果有透视变换图像，创建拼接显示
            warped_resized = cv2.resize(warped_inner, (320, 480))
            display_resized = cv2.resize(display_frame, (320, 480))
            
            # 水平拼接原始图像和透视变换图像
            result_img = np.hstack((display_resized, warped_resized))
            
            # 在拼接图像上添加标题
            cv2.putText(result_img, "Original", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(result_img, "Warped+Rects", (330, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 在拼接图像上显示检测结果
            cv2.putText(result_img, f"Rects: {len(rectCoords)}", 
                    (330, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            draw_vertical_quadrants(result_img)
            
        else:
            # 如果没有透视变换图像，只显示原始图像
            result_img = display_frame
            cv2.putText(result_img, "No Inner Rect Found", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        #############################################串口发送指令信息###############################################
        minAreaLength = detector.DEBUG_GetShortestRectLength()
        if minAreaLength != 0 and minAreaLength < 65535:
            detector.minLength = 0 # 重新清空在类内的存储变量
            realLength = minAreaLength / TARGET_HEIGHT *  KNOWN_HEIGHT * 10
            print("len:", realLength, "cm", minAreaLength)
            distance   = distance_cm * 10
            uart_sendCommand(int(distance), int(realLength))
            switchToMode0()
        ############################################################################################################
    #################################模式4作弊模式#######################################################
    elif MODE == 98:
    #######代表已经接收到了数据并且接收到了命令##################################################################
        if Number != -1:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blur, params['canny_th1'], params['canny_th2'])

            # 查找所有轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            rectangle_count = 0
            valid_rectangles_info = []
            # 第一轮：收集可能的矩形轮廓（用于确定Inner Rect）
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 5000:  # 过滤过小轮廓
                    continue
                
                is_rect, approx_rect = is_rectangle(contour)
                is_sq, approx_sq = is_square(contour)
                
                if is_rect or is_sq:
                    approx = approx_rect if is_rect else approx_sq
                    aspect_ratio = calculate_aspect_ratio(approx)
                    ratio_valid = is_aspect_ratio_valid(aspect_ratio)
                    
                    valid_rectangles_info.append({
                        "contour": contour,
                        "is_rectangle": is_rect,
                        "approx": approx,
                        "area": area,
                        "keep": True,
                        "aspect_ratio": aspect_ratio,
                        "ratio_valid": ratio_valid
                    })

            # 第二轮：过滤重叠矩形（确定Inner Rect）
            n = len(valid_rectangles_info)
            for i in range(n):
                info1 = valid_rectangles_info[i]
                if not info1["keep"]:
                    continue
                rect1 = cv2.boundingRect(info1["approx"])
                area1 = info1["area"]
                rect1_area = rect1[2] * rect1[3]
                rect1_metric = area1 / rect1_area if rect1_area > 0 else 0
                
                for j in range(i + 1, n):
                    info2 = valid_rectangles_info[j]
                    if not info2["keep"]:
                        continue
                    rect2 = cv2.boundingRect(info2["approx"])
                    area2 = info2["area"]
                    rect2_area = rect2[2] * rect2[3]
                    rect2_metric = area2 / rect2_area if rect2_area > 0 else 0
                    
                    if calculate_iou(rect1, rect2) > 0.8:
                        if (area1 > area2 * 1.2) or (rect1_metric > rect2_metric + 0.1):
                            info2["keep"] = False
                        else:
                            info1["keep"] = False
                            break

            filtered_rectangles = [info for info in valid_rectangles_info if info["keep"]]

            # 打印所有检测到的矩形的长宽比及有效性
            print("\n===== 检测到的矩形信息 =====")
            print(f"长宽比阈值范围: {ASPECT_RATIO_LOWER} - {ASPECT_RATIO_UPPER}")
            for i, info in enumerate(filtered_rectangles):
                rect_type = "长方形" if info["is_rectangle"] else "正方形"
                validity = "有效" if info["ratio_valid"] else "无效"
                print(f"矩形 {i+1}: 类型={rect_type}, 面积={info['area']:.2f} px², 长宽比={info['aspect_ratio']:.4f}, {validity}")

            # 透视变换及内部轮廓检测（所有类型）
            warped_inner = None
            transform_matrix = None
            M_inv = None
            warped_contours = []  # 存储变换后图像中检测到的所有轮廓
            distance_text = ""

            # 判断轮廓是否在指定矩形内部的辅助函数
            def is_contour_inside_rect(contour, rect):
                x, y, w, h = rect
                points = contour.reshape(-1, 2)
                for (px, py) in points:
                    if not (x <= px <= x + w and y <= py <= y + h):
                        return False
                return True

            # 确定Inner Rect并执行透视变换
            rect_only = [info for info in filtered_rectangles if info["is_rectangle"] and info["ratio_valid"]]
            if rect_only:
                inner_rect_info = min(rect_only, key=lambda x: x["area"])
                inner_approx = inner_rect_info["approx"]
                inner_rect = cv2.boundingRect(inner_approx)
                x_inner, y_inner, w_inner, h_inner = inner_rect
                
                # 过滤只保留inner rect内部的轮廓
                filtered_rectangles = [
                    info for info in filtered_rectangles
                    if is_contour_inside_rect(info["contour"], (x_inner, y_inner, w_inner, h_inner))
                ]

                # 计算Inner Rect尺寸和距离
                width_px, height_px = calculate_inner_rect_size(inner_approx)

                # 计算Inner Rect的长边像素长度及实际距离
                sides = calculate_side_lengths(inner_approx)
                avg_long_px = get_long_sides_average(sides)
                distance_cm = calculate_distance(avg_long_px)
                
                # 打印Inner Rect信息
                print("\n===== Inner Rect 信息 =====")
                print(f"Inner Rect尺寸: 宽度={width_px:.2f}像素, 高度={height_px:.2f}像素")
                print(f"Inner Rect长宽比: {inner_rect_info['aspect_ratio']:.4f} (在阈值范围内)")
                
                # 在图像上显示Inner Rect信息
                cv2.putText(display_frame, f"Distance: {distance_cm:.1f} cm", 
                        (x_inner, y_inner + h_inner + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 绘制Inner Rect
                cv2.drawContours(display_frame, [inner_approx], -1, (0, 0, 255), 3)
                cv2.putText(display_frame, "Inner Rect", (x_inner, y_inner - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # 执行透视变换
                inner_pts = inner_approx.reshape(4, 2).astype("float32")
                src_pts = order_points(inner_pts)
                dst_pts = np.array([
                    [0, 0],
                    [TARGET_WIDTH - 1, 0],
                    [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
                    [0, TARGET_HEIGHT - 1]], dtype="float32")
                
                transform_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                warped_inner = cv2.warpPerspective(img_cv, transform_matrix, (TARGET_WIDTH, TARGET_HEIGHT))
                M_inv = cv2.getPerspectiveTransform(dst_pts, src_pts)
                
                # 在原始图像上绘制所有变换后的轮廓
                if M_inv is not None and warped_contours:
                    draw_warped_contours_on_original(display_frame, warped_contours, M_inv)
            else:
                # 没有符合要求的Inner Rect
                print("\n未检测到符合长宽比要求的Inner Rect")
                cv2.putText(display_frame, f"No valid Inner Rect (AR: {ASPECT_RATIO_LOWER}-{ASPECT_RATIO_UPPER})", 
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # 绘制原始图像中的矩形，用不同颜色标记有效性
            for info in filtered_rectangles:
                rectangle_count += 1
                color = (0, 255, 0) if info["ratio_valid"] else (0, 165, 255)
                cv2.drawContours(display_frame, [info["approx"]], -1, color, 2)
                x, y, _, _ = cv2.boundingRect(info["approx"])
                cv2.putText(display_frame, f"AR: {info['aspect_ratio']:.2f}", 
                        (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                validity_text = "Valid" if info["ratio_valid"] else "Invalid"
                cv2.putText(display_frame, validity_text, 
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # 显示原始图像信息
            cv2.putText(display_frame, f"Rectangles: {rectangle_count}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # 以下是重叠代码
            # ----------------------------------------------------------------------------------------------------
            # 安全检查：确保warped_inner存在且有效
            if warped_inner is not None and warped_inner.size > 0:
                print(f"🔍 开始处理透视变换后的图像，尺寸: {warped_inner.shape}")
                cropImage = warped_inner
                showImage = warped_inner
                
                gray = cv2.cvtColor(warped_inner, cv2.COLOR_BGR2GRAY)
                threshold, binary_image = cv2.threshold(
                    gray, 
                    0,                  # 初始阈值（无意义，大津法会覆盖）
                    255,                # 最大值（超过阈值的像素设为255）
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU  # 大津法+二值化
                )
                binary = cv2.bitwise_not(binary_image)
                # 安全检查：确保newImage不是None
                if binary is not None:
                    newImage = fill_holes_in_white(binary)
                    contour = get_innermost_contours(newImage)
                    rectCoords = detector.DEBUG_FindIOURects(contour, newImage, frame = warped_inner)
                else:
                    print("错误：get_only_largest_white_component_max返回None，跳过后续处理")
                    rectCoords = []
                    
                showImage = detector.testImage
                print(f"🔍 在透视变换图像中检测到 {len(rectCoords)} 个矩形")

                # mode3 复用 mode2 的检测链路，但返回最大矩形的长度
                if len(rectCoords) > 0:
                    def get_rect_size(quad_array):
                        points = np.squeeze(quad_array)
                        if len(points.shape) != 2 or points.shape[0] != 4:
                            return 0
                        x, y, w, h = cv2.boundingRect(points.astype(np.int32))
                        return w * h

                    def get_rect_edge_length(quad_array):
                        points = np.squeeze(quad_array)
                        if len(points.shape) != 2 or points.shape[0] != 4:
                            return 0

                        side_lengths = []
                        for i in range(4):
                            p1 = points[i]
                            p2 = points[(i + 1) % 4]
                            side_lengths.append(np.linalg.norm(p1 - p2))

                        if not side_lengths:
                            return 0
                        return max(side_lengths)

                    largest_rect = max(rectCoords, key=get_rect_size)
                    maxAreaLength = get_rect_edge_length(largest_rect)

                    if maxAreaLength != 0 and maxAreaLength < 65535:
                        real = maxAreaLength / TARGET_HEIGHT * KNOWN_HEIGHT * 10
                        distance = distance_cm * 10
                        print("max len:", real, "mm", maxAreaLength)
                        uart_sendCommand(int(distance), int(real))
                        Number = -1
                        switchToMode0()
                    
                    #uart_sendCommand[]
                        # MaixCAM智能显示选择
                if warped_inner is not None and warped_inner.size > 0:
                    # 如果有透视变换图像，创建拼接显示
                    warped_resized = cv2.resize(warped_inner, (320, 480))
                    display_resized = cv2.resize(display_frame, (320, 480))
                    
                    # 水平拼接原始图像和透视变换图像
                    result_img = np.hstack((display_resized, warped_resized))
                    
                    # 在拼接图像上添加标题
                    cv2.putText(result_img, "Original", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(result_img, "Warped+Rects", (330, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # 在拼接图像上显示检测结果
                    cv2.putText(result_img, f"Rects: {len(rectCoords)}", 
                            (330, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    draw_vertical_quadrants(result_img)

         
    ##################################模式5作弊模式######################################################
    elif MODE == 99:
        print()

    elif MODE == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, params['canny_th1'], params['canny_th2'])

        # 查找所有轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rectangle_count = 0
        valid_rectangles_info = []
        # 第一轮：收集可能的矩形轮廓（用于确定Inner Rect）
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 5000:  # 过滤过小轮廓
                continue
            
            is_rect, approx_rect = is_rectangle(contour)
            is_sq, approx_sq = is_square(contour)
            
            if is_rect or is_sq:
                approx = approx_rect if is_rect else approx_sq
                aspect_ratio = calculate_aspect_ratio(approx)
                ratio_valid = is_aspect_ratio_valid(aspect_ratio)
                
                valid_rectangles_info.append({
                    "contour": contour,
                    "is_rectangle": is_rect,
                    "approx": approx,
                    "area": area,
                    "keep": True,
                    "aspect_ratio": aspect_ratio,
                    "ratio_valid": ratio_valid
                })
        
        # 第二轮：过滤重叠矩形（确定Inner Rect）
        n = len(valid_rectangles_info)
        for i in range(n):
            info1 = valid_rectangles_info[i]
            if not info1["keep"]:
                continue
            rect1 = cv2.boundingRect(info1["approx"])
            area1 = info1["area"]
            rect1_area = rect1[2] * rect1[3]
            rect1_metric = area1 / rect1_area if rect1_area > 0 else 0
            
            for j in range(i + 1, n):
                info2 = valid_rectangles_info[j]
                if not info2["keep"]:
                    continue
                rect2 = cv2.boundingRect(info2["approx"])
                area2 = info2["area"]
                rect2_area = rect2[2] * rect2[3]
                rect2_metric = area2 / rect2_area if rect2_area > 0 else 0
                
                if calculate_iou(rect1, rect2) > 0.8:
                    if (area1 > area2 * 1.2) or (rect1_metric > rect2_metric + 0.1):
                        info2["keep"] = False
                    else:
                        info1["keep"] = False
                        break
        
        filtered_rectangles = [info for info in valid_rectangles_info if info["keep"]]
        
        # 打印所有检测到的矩形的长宽比及有效性
        print("\n===== 检测到的矩形信息 =====")
        print(f"长宽比阈值范围: {ASPECT_RATIO_LOWER} - {ASPECT_RATIO_UPPER}")
        for i, info in enumerate(filtered_rectangles):
            rect_type = "长方形" if info["is_rectangle"] else "正方形"
            validity = "有效" if info["ratio_valid"] else "无效"
            print(f"矩形 {i+1}: 类型={rect_type}, 面积={info['area']:.2f} px², 长宽比={info['aspect_ratio']:.4f}, {validity}")
        
        # 绘制原始图像中的矩形，用不同颜色标记有效性
        for info in filtered_rectangles:
            rectangle_count += 1
            color = (0, 255, 0) if info["ratio_valid"] else (0, 165, 255)
            cv2.drawContours(display_frame, [info["approx"]], -1, color, 2)
            x, y, _, _ = cv2.boundingRect(info["approx"])
            cv2.putText(display_frame, f"AR: {info['aspect_ratio']:.2f}", 
                    (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            validity_text = "Valid" if info["ratio_valid"] else "Invalid"
            cv2.putText(display_frame, validity_text, 
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # 透视变换及内部轮廓检测（所有类型）
        warped_inner = None
        transform_matrix = None
        M_inv = None
        warped_contours = []  # 存储变换后图像中检测到的所有轮廓
        distance_text = ""
        
        # 确定Inner Rect并执行透视变换
        rect_only = [info for info in filtered_rectangles if info["is_rectangle"] and info["ratio_valid"]]
        if rect_only:
            inner_rect_info = min(rect_only, key=lambda x: x["area"])
            inner_approx = inner_rect_info["approx"]
            inner_rect = cv2.boundingRect(inner_approx)
            x, y, w, h = inner_rect
            
            # 计算Inner Rect尺寸和距离
            width_px, height_px = calculate_inner_rect_size(inner_approx)


            # 计算Inner Rect的长边像素长度及实际距离
            sides = calculate_side_lengths(inner_approx)  # 四条边的像素长度
            avg_long_px = get_long_sides_average(sides)   # 两长边和的二分之一
            distance_cm = calculate_distance(avg_long_px) # 计算实际距离
            
            # 打印Inner Rect信息
            print("\n===== Inner Rect 信息 =====")
            print(f"Inner Rect尺寸: 宽度={width_px:.2f}像素, 高度={height_px:.2f}像素")
            print(f"Inner Rect长宽比: {inner_rect_info['aspect_ratio']:.4f} (在阈值范围内)")
            
            # 在图像上显示Inner Rect信息
            # cv2.putText(display_frame, f"Inner Rect: {width_px:.1f}x{height_px:.1f}px", 
            #         (x, y - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            # cv2.putText(display_frame, f"AR: {inner_rect_info['aspect_ratio']:.2f} (Valid)", 
            #         (x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            # cv2.putText(display_frame, f"Threshold: {ASPECT_RATIO_LOWER}-{ASPECT_RATIO_UPPER}", 
            #         (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(display_frame, f"Distance: {distance_cm:.1f} cm", 
                    (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 绘制Inner Rect
            cv2.drawContours(display_frame, [inner_approx], -1, (0, 0, 255), 3)
            cv2.putText(display_frame, "Inner Rect", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 执行透视变换
            inner_pts = inner_approx.reshape(4, 2).astype("float32")
            src_pts = order_points(inner_pts)
            dst_pts = np.array([
                [0, 0],
                [TARGET_WIDTH - 1, 0],
                [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
                [0, TARGET_HEIGHT - 1]], dtype="float32")
            
            transform_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
            warped_inner = cv2.warpPerspective(img_cv, transform_matrix, (TARGET_WIDTH, TARGET_HEIGHT))
            M_inv = cv2.getPerspectiveTransform(dst_pts, src_pts)
            



            
            # 在原始图像上绘制所有变换后的轮廓
            if M_inv is not None and warped_contours:
                draw_warped_contours_on_original(display_frame, warped_contours, M_inv)
        else:
            # 没有符合要求的Inner Rect
            print("\n未检测到符合长宽比要求的Inner Rect")
            cv2.putText(display_frame, f"No valid Inner Rect (AR: {ASPECT_RATIO_LOWER}-{ASPECT_RATIO_UPPER})", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # 显示原始图像信息
        cv2.putText(display_frame, f"Rectangles: {rectangle_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        
        # if rect_only:
        #     cv2.putText(display_frame, f"Contours detected: {len(warped_contours)}", 
        #             (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        #     cv2.putText(display_frame, f"Inner Rect Size: {INNER_RECT_WIDTH_CM}x{INNER_RECT_HEIGHT_CM} cm", 
        #             (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 0), 2)
            
        #     # 显示平均距离
        #     cv2.putText(display_frame, f"Avg Distance: {distance_text}", 
        #             (display_frame.shape[1] - 300, 30), 
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        

        #以下是重叠代码
        #----------------------------------------------------------------------------------------------------
        # 安全检查：确保warped_inner存在且有效
        if warped_inner is not None and warped_inner.size > 0:
            print(f"🔍 开始处理透视变换后的图像，尺寸: {warped_inner.shape}")
            cropImage = warped_inner
            # print(cropImage.shape)
            showImage = warped_inner
            
            gray = cv2.cvtColor(warped_inner, cv2.COLOR_BGR2GRAY)
            threshold, binary_image = cv2.threshold(
                gray, 
                0,                  # 初始阈值（无意义，大津法会覆盖）
                255,                # 最大值（超过阈值的像素设为255）
                cv2.THRESH_BINARY + cv2.THRESH_OTSU  # 大津法+二值化
            )
            binary = cv2.bitwise_not(binary_image)
            # 沿用mode2的处理流程：不做get_only_largest_white_component_max，保留所有连通域
            if binary is not None:
                newImage = fill_holes_in_white(binary)
                contour = get_innermost_contours(newImage)
                rectCoords = detector.DEBUG_FindIOURects(contour, newImage, frame = warped_inner)
            else:
                print("错误：二值化失败，跳过后续处理")
                rectCoords = []
                
            # remapCoords = map_crop_to_original(rectCoords, inner_rect)
            showImage = detector.testImage
            print(f"🔍 在透视变换图像中检测到 {len(rectCoords)} 个矩形")
            
            # 🔢 数字识别功能集成
            if YOLO_ENABLED and len(rectCoords) > 0:
                print("\n===== 🔢 开始YOLO数字识别 =====")
                
                # 对所有矩形区域进行数字识别，同时获取裁切图像
                digit_results, cropped_images_list = process_digit_recognition(warped_inner, rectCoords)
                
                # 创建裁切图像的网格显示
                crops_grid = create_cropped_images_grid(cropped_images_list, grid_size=(90, 90), use_nine_grid=True)
                print(f"🖼️  创建裁切图像网格，尺寸: {crops_grid.shape}")
                
                # 在warped_inner上绘制数字检测结果
                draw_digit_results_on_warped(warped_inner, rectCoords, digit_results)
                
                # 统计和显示检测结果
                total_detected = sum(1 for results in digit_results if results)
                print(f"\n📊 数字识别统计：{total_detected}/{len(rectCoords)} 个矩形检测到数字")
                
                # 在图像上添加统计信息
                cv2.putText(warped_inner, f"Digits: {total_detected}/{len(rectCoords)}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                
            else:
                # 如果YOLO未启用，使用原有的绘制方式
                print("⚠️  YOLO未启用，使用基础矩形绘制")
                cropped_images_list = []  # 空列表
                crops_grid = create_cropped_images_grid([], grid_size=(90, 90), use_nine_grid=True)  # 创建空九宫格
                
                for coord_idx, quad_array in enumerate(rectCoords):
                    # 直接处理不同可能的数组形状，避免squeeze错误
                    points = np.squeeze(quad_array)
                    
                    # 确保是二维数组 (n, 2)
                    if len(points.shape) != 2:
                        print(f"警告：第 {coord_idx} 个四边形坐标维度错误，形状为 {points.shape}")
                        continue
                    
                    # 验证是否有4个点
                    if points.shape[0] == 4:
                        # 绘制四边形（连接4个点形成闭合图形）
                        for i in range(4):
                            pt1 = tuple(points[i])
                            pt2 = tuple(points[(i + 1) % 4])  # 最后一个点连接回第一个点
                            cv2.line(warped_inner, pt1, pt2, color=(0, 255, 0), thickness=3)
                        
                        # 在矩形中心添加编号标识
                        center_x = int(np.mean(points[:, 0]))
                        center_y = int(np.mean(points[:, 1]))
                        cv2.putText(warped_inner, f"R{coord_idx+1}", (center_x-15, center_y+5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        cv2.circle(warped_inner, (center_x, center_y), 5, (255, 255, 0), -1)
                    else:
                        print(f"警告：第 {coord_idx} 个四边形坐标格式不正确，包含 {points.shape[0]} 个点（预期4个）")
            
            # 在warped图像上添加检测统计信息
            if len(rectCoords) > 0:
                cv2.putText(warped_inner, f"Detected: {len(rectCoords)} Rectangles",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            # 添加安全检查：确保newImage不是None
            if newImage is not None:
                resize = resize_to_multiple_of_two(newImage)
            else:
                print("警告：newImage为None，跳过resize处理")
        else:
            print("⚠️  警告：warped_inner为None或空图像，跳过透视变换图像处理")
            print("   这通常是因为没有检测到符合长宽比要求的Inner Rect")
            rectCoords = []
            crops_grid = create_cropped_images_grid([], grid_size=(90, 90), use_nine_grid=True)  # 创建空九宫格

        #############################################串口发送指令信息（MODE3：取最大矩形）###############################################
        # 沿用mode2原理：从rectCoords中选目标，但取最大而非最小
        if len(rectCoords) > 0:
            # 计算每个矩形的边长
            def get_rect_avg_side(quad_array):
                points = np.squeeze(quad_array)
                if len(points.shape) != 2 or points.shape[0] != 4:
                    return 0
                side_lengths = []
                for i in range(4):
                    p1 = points[i]
                    p2 = points[(i + 1) % 4]
                    side_lengths.append(np.linalg.norm(p1 - p2))
                side_lengths.sort()
                # 取较短两边的平均值作为正方形边长（与mode2的minLength逻辑一致）
                return (side_lengths[0] + side_lengths[1]) / 2

            # 找最大矩形（按平均边长排序，取最大）
            max_side = 0
            for quad in rectCoords:
                avg_side = get_rect_avg_side(quad)
                if avg_side > max_side:
                    max_side = avg_side

            if max_side > 0 and max_side < 65535:
                realLength = max_side / TARGET_HEIGHT * KNOWN_HEIGHT * 10
                distance = distance_cm * 10
                print("MODE3 max len:", realLength, "mm", max_side)
                uart_sendCommand(int(distance), int(realLength))
                switchToMode0()
        ############################################################################################################

        # MaixCAM智能显示选择
        if warped_inner is not None and warped_inner.size > 0:
            # 如果有透视变换图像，创建三列拼接显示
            # 🆕 优化布局适应九宫格：原始图像(300) | 透视变换(300) | 九宫格(270)
            warped_resized = cv2.resize(warped_inner, (300, 480))
            display_resized = cv2.resize(display_frame, (300, 480))
            
            # 🆕 九宫格是正方形，调整尺寸以更好地适应显示
            # 九宫格尺寸：3x3 * 90 = 270x270，居中显示
            crops_resized = cv2.resize(crops_grid, (270, 270))
            
            # 创建九宫格显示区域（270宽，480高，居中显示九宫格）
            crops_display = np.zeros((480, 270, 3), dtype=np.uint8)
            y_offset = (480 - 270) // 2  # 居中放置九宫格
            crops_display[y_offset:y_offset+270, :] = crops_resized
            
            # 三列水平拼接：原始图像 | 透视变换图像 | 九宫格显示区域
            result_img = np.hstack((display_resized, warped_resized, crops_display))
            
            # 在拼接图像上添加标题
            cv2.putText(result_img, "Original", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            warped_title = "Warped+Digits" if YOLO_ENABLED else "Warped+Rects"
            cv2.putText(result_img, warped_title, (310, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(result_img, "Nine Grid", (610, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 在拼接图像上显示检测结果
            cv2.putText(result_img, f"Rects: {len(rectCoords)}", 
                    (310, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 在九宫格区域显示统计信息
            total_crops = len([img for img, idx in cropped_images_list if img is not None]) if 'cropped_images_list' in locals() else 0
            cv2.putText(result_img, f"Crops: {total_crops}/9", 
                    (610, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # 显示九宫格信息
            cv2.putText(result_img, f"90x90px Grid", 
                    (610, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(result_img, "Keep Aspect", 
                    (610, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            draw_vertical_quadrants(result_img)
            
        else:
            # 如果没有透视变换图像，显示原始图像和九宫格
            display_resized = cv2.resize(display_frame, (410, 480))
            
            # 九宫格居中显示
            crops_resized = cv2.resize(crops_grid, (270, 270))
            crops_display = np.zeros((480, 270, 3), dtype=np.uint8)
            y_offset = (480 - 270) // 2
            crops_display[y_offset:y_offset+270, :] = crops_resized
            
            # 两列拼接显示
            result_img = np.hstack((display_resized, crops_display))
            
            cv2.putText(result_img, "Original", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(result_img, "No Inner Rect Found", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(result_img, "Nine Grid", (420, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

     
    



    # 显示参数信息
    param_text = f"Th1:{params['canny_th1']} Th2:{params['canny_th2']}"
    cv2.putText(result_img, param_text, (10, 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # 显示结果
    draw_center_cross(result_img)

    img_show = image.cv2image(result_img, bgr=True, copy=False)
    # img_show = image.cv2image(edges, bgr=True, copy=False)
    disp.show(img_show)
    # print(time.time()-time1)
    # print()
    # print(MODE)
