import cv2
import os
import numpy as np
from draw import drawButton
# 导入YOLOv4-tiny网络模型结构
net = cv2.dnn.readNet('dnn_model\yolov4-tiny.cfg', 'dnn_model\yolov4-tiny.weights')
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1 / 255)# 设置模型的输入
# 获取分类文本的信息
classes = []
with open('dnn_model\classes.txt') as file_obj:
    for class_name in file_obj.readlines():
        class_name = class_name.strip()
        classes.append(class_name)
images_folder = 'D:/data/valid/images'# 读取图片的位置
# 获取文件夹中所有以 '.jpg' 结尾的图像文件，并按文件名进行排序
image_files = sorted([f for f in os.listdir(images_folder) if f.endswith('.jpg')])
# 初始化按钮类和按钮索引
button_class = False  # button_class 表示按钮的类别，这里初始化为 False
button_index = None   # button_index 表示按钮的索引，这里初始化为 None
def click_button(event, x, y, flags, params):
    # 定义全局变量，表示按钮的类别和索引
    global button_class
    global button_index
    if event == cv2.EVENT_LBUTTONDOWN:# 鼠标左键按下事件
        for index, pt in enumerate(np.array(buttonList)):# 遍历按钮列表中的每一个按钮
            # 判断点击位置是否在当前按钮的多边形内
            is_inside = cv2.pointPolygonTest(pt, (x, y), False)
            if is_inside > 0:# 如果在多边形内
                print(f'点击在第 {index + 1} 号按钮位置', (x, y))
                # 如果之前没有选中按钮，则选中当前按钮
                if button_class == False:
                    button_class = True
                    button_index = index
                else:
                    # 如果点击的是 "all" 按钮，则不显示特定类别的框
                    if usenames[index] == 'all':
                        button_index = None
                    else:
                        # 否则，选中当前按钮
                        button_index = index
            else:
                # 如果点击位置不在任何按钮内，则取消按钮选中状态
                button_class = False
cv2.namedWindow('Image')# 创建窗口并命名为 'Image'
cv2.setMouseCallback('Image', click_button)# 设置鼠标回调函数为 click_button，用于处理鼠标事件
usenames = ['all', 'person', 'car']# 创建按钮列表
button = drawButton(usenames)  # 调用绘制按钮的函数 drawButton()
colorline = (0, 255, 0)# 定义绘制检测框的线条颜色
angerline = 13  # 定义绘制线条的宽度
def draw_bounding_box(img, x, y, w, h, pred_name, score):
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 1)# 绘制矩形框
    # 绘制矩形框四条边的线
    cv2.line(img, (x, y), (x + angerline, y), colorline, 2)
    cv2.line(img, (x, y), (x, y + angerline), colorline, 2)
    cv2.line(img, (x + w, y), (x + w, y + angerline), colorline, 2)
    cv2.line(img, (x + w, y), (x + w - angerline, y), colorline, 2)
    cv2.line(img, (x, y + h), (x, y + h - angerline), colorline, 2)
    cv2.line(img, (x, y + h), (x + angerline, y + h), colorline, 2)
    cv2.line(img, (x + w, y + h), (x + w, y + h - angerline), colorline, 2)
    cv2.line(img, (x + w, y + h), (x + w - angerline, y + h), colorline, 2)
    # 在矩形框下方绘制预测类别名称
    cv2.putText(img, pred_name, (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    # 在矩形框上方绘制置信度分数
    cv2.putText(img, str(int(score * 100)) + '%', (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
# 输出图片保存路径
output_folder = 'D:/image/valid/person'
os.makedirs(output_folder, exist_ok=True)
frame_count = 0# 初始化帧计
while frame_count < len(image_files):# 循环遍历图像文件列表
    class_counters = {class_name: 0 for class_name in usenames}# 重新初始化计数器字典
    # 读取图像并调整大小
    frame = cv2.imread(os.path.join(images_folder, image_files[frame_count]))
    frame = cv2.resize(frame, (1280, 720))
    class_ids, scores, bboxes = model.detect(frame, 0.5, 0.3)# 使用目标检测模型获取检测结果
    # 绘制按钮
    button.drawRec_many(frame)
    buttonList = button.recList
    for class_id, score, bbox in zip(class_ids, scores, bboxes):# 遍历检测结果并根据按钮选择绘制边框
        x, y, w, h = bbox
        class_name = classes[class_id]
        # 根据用户选择的按钮绘制边框
        if button_index is None or usenames[button_index] == 'all' or usenames[button_index] == class_name:
            draw_bounding_box(frame, x, y, w, h, class_name, score)
            if class_name in class_counters:# 计数逻辑
                class_counters[class_name] += 1
            class_counters['all'] += 1# 更新 "all" 计数信息
    # 在图像上显示每个类别的计数信息
    count_info = ', '.join([f'{class_name}: {count}' for class_name, count in class_counters.items()])
    cv2.putText(frame, count_info, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow('Image', frame)# 显示图像
    cv2.waitKey(100)#设置帧数，控制图像的显示时长
    frame_filename = f'frame_{frame_count:04d}.jpg'# 保存处理后的照片
    frame_path = os.path.join(output_folder, frame_filename)
    cv2.imwrite(frame_path, frame)
    if cv2.waitKey(30) & 0xFF == 27:# 等待键盘输入，按下 ESC 键退出循环
        break
    frame_count += 1# 帧计数器自增
cv2.destroyAllWindows()#关闭所有窗口
