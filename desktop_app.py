import cv2
import math
import numpy as np
import tkinter as tk, os
from tkinter import filedialog
from PIL import ImageTk, Image
from pprint import pprint
from skimage import color

pressed_x = pressed_y = 0
def pressed(event):
  global pressed_x, pressed_y
  pressed_x = event.x
  pressed_y = event.y

def dragged(event):
  global pressed_x, pressed_y
  delta_x = event.x - pressed_x
  delta_y = event.y - pressed_y
  item_id = target_image.find_closest(event.x, event.y)
  x, y = target_image.coords(item_id)
  target_image.coords(item_id, x+delta_x, y+delta_y)
  pressed_x = event.x
  pressed_y = event.y

def image_up():
  global img
  fTyp = [("","*")]
  iDir = os.path.abspath(os.path.dirname(__file__))
  file = filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
  img = Image.open(file)      
  target_image.image = ImageTk.PhotoImage(img)
  target_image.create_image(0,0,image = target_image.image,anchor = tk.NW, tags="img")
  target_image.create_rectangle(185, 185, 215, 215, outline = 'green')
  target_image.grid(row=2, column=0, columnspan=5)
  # クリックされたとき
  target_image.tag_bind("img", "<ButtonPress-1>", pressed)
  # ドラッグされたとき
  target_image.tag_bind("img", "<B1-Motion>", dragged)

  raw_title = tk.Label(text='生データ', relief=tk.RIDGE)
  med_rgb_title = tk.Label(text='代表色(rgb)', relief=tk.RIDGE)
  med_lab_title = tk.Label(text='代表色(lab)', relief=tk.RIDGE)
  raw_title.grid(row=3, column=1, padx=5, pady=5)
  med_rgb_title.grid(row=3, column=2, padx=5, pady=5)
  med_lab_title.grid(row=3, column=3, padx=5, pady=5)


def base_image_crop():
  global base_image_representative_rgb
  title = tk.Label(text='基準画像', relief=tk.RIDGE)
  x, y = target_image.coords((1,))
  cropped = img.crop((185 - x, 185 - y, 215 - x, 215 - y))
  base_image.image = ImageTk.PhotoImage(cropped)
  base_image.create_image(0,0,image = base_image.image,anchor = tk.NW, tags="base_img")
  converted2opcv = pillow2opencv(cropped)
  representative_color = get_representative_color(converted2opcv)
  rgb_img = np.zeros((30, 30, 3), dtype=np.uint8)
  base_image_representative_rgb = np.around(representative_color[0])
  cv2.rectangle(rgb_img, (0, 0), (30, 30), tuple(map(lambda rgb:int(rgb), base_image_representative_rgb)), thickness=-1)
  rgb_image_canvas = tk.Canvas(width = 30, height = 30)
  rgb_image_canvas.image = ImageTk.PhotoImage(opencv2pillow(rgb_img))
  rgb_image_canvas.create_image(0,0,image = rgb_image_canvas.image, anchor = tk.NW)

  title.grid(row=4, column=0, padx=5, pady=5)
  base_image.grid(row=4, column=1, padx=5, pady=5)
  rgb_image_canvas.grid(row=4, column=2, padx=5, pady=5)

def compare_image_crop():
  global compare_image_representative_rgb
  title = tk.Label(text='比較画像', relief=tk.RIDGE)
  x, y = target_image.coords((1,))
  cropped = img.crop((185 - x, 185 - y, 215 - x, 215 - y))
  compare_image.image = ImageTk.PhotoImage(cropped)
  compare_image.create_image(0,0,image = compare_image.image,anchor = tk.NW, tags="base_img")
  converted2opcv = pillow2opencv(cropped)
  representative_color = get_representative_color(converted2opcv)
  compare_image_representative_rgb = np.around(representative_color[0])
  rgb_img = np.zeros((30, 30, 3), dtype=np.uint8)
  cv2.rectangle(rgb_img, (0, 0), (30, 30), tuple(map(lambda rgb:int(rgb), compare_image_representative_rgb)), thickness=-1)
  rgb_image_canvas = tk.Canvas(width = 30, height = 30)
  rgb_image_canvas.image = ImageTk.PhotoImage(opencv2pillow(rgb_img))
  rgb_image_canvas.create_image(0,0,image = rgb_image_canvas.image, anchor = tk.NW)
  
  title.grid(row=5, column=0, padx=5, pady=5)
  compare_image.grid(row=5, column=1, padx=5, pady=5)
  rgb_image_canvas.grid(row=5, column=2, padx=5, pady=5)

def color_distance():
  diff_bl = 255 - base_image_representative_rgb[0]
  diff_g = 255 - base_image_representative_rgb[1]
  diff_r = 255 - base_image_representative_rgb[2]

  def skimage_rgb2lab(rgb):
    return color.rgb2lab(rgb.reshape(1,1,3))

  euclid_distance = math.sqrt(
    ((base_image_representative_rgb[0] - compare_image_representative_rgb[0]) ** 2) +
    ((base_image_representative_rgb[1] - compare_image_representative_rgb[1]) ** 2) +
    ((base_image_representative_rgb[2] - compare_image_representative_rgb[2]) ** 2)
  )

  de2000 = color.deltaE_ciede2000(skimage_rgb2lab(base_image_representative_rgb), skimage_rgb2lab(compare_image_representative_rgb))[0][0]
  

  # rgb_img = np.zeros((30, 30, 3), dtype=np.uint8)
  # cv2.rectangle(rgb_img, (0, 0), (30, 30), collected_rgb, thickness=-1)
  # rgb_image_canvas = tk.Canvas(width = 30, height = 30)
  # rgb_image_canvas.image = ImageTk.PhotoImage(opencv2pillow(rgb_img))
  # rgb_image_canvas.create_image(0,0,image = rgb_image_canvas.image, anchor = tk.NW)

  # collected_lab = [
  #   np.uint8(compare_image_representative_lab[0] + diff_l),
  #   np.uint8(compare_image_representative_lab[1] + diff_a),
  #   np.uint8(compare_image_representative_lab[2] + diff_b)
  # ]

  # lab_img = np.full((30, 30, 3), collected_lab)
  # rgb_from_lab = lab2rgb(lab_img)[0][0]
  # cv2.rectangle(lab_img, (0, 0), (30, 30), (int(rgb_from_lab[0]), int(rgb_from_lab[1]), int(rgb_from_lab[2])), thickness=-1)
  # lab_image_canvas = tk.Canvas(width = 30, height = 30)
  # lab_image_canvas.image = ImageTk.PhotoImage(opencv2pillow(lab_img))
  # lab_image_canvas.create_image(0,0,image = lab_image_canvas.image, anchor = tk.NW)
  
  
  title = tk.Label(text='色の距離', relief=tk.RIDGE)
  title.grid(row=6, column=0, padx=5, pady=5)
  euclid = tk.Label(text='ユークリッド距離: ' + str(euclid_distance), relief=tk.RIDGE)
  euclid.grid(row=6, column=2, padx=5, pady=5)
  de2000 = tk.Label(text='DE2000: ' + str(de2000), relief=tk.RIDGE)
  de2000.grid(row=6, column=3, padx=5, pady=5)

def near_color():
  print('a')

  
def get_representative_color(img):
  colors = img.reshape(-1, 3)
  criteria = cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 10, 1.0
  colors = colors.astype(np.float32)
  ret, label, center = cv2.kmeans(
    colors, 1, None, criteria, attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS
  )
  return center


def pillow2opencv(pillow_image):
  img = np.array(pillow_image, dtype=np.uint8)
  return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def rgb2lab(opencv_image):
  return cv2.cvtColor(opencv_image, cv2.COLOR_BGR2Lab)

def lab2rgb(opencv_image):
  return cv2.cvtColor(opencv_image, cv2.COLOR_Lab2BGR)

def opencv2pillow(opencv_image):
  img = opencv_image.copy()
  colors = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  return Image.fromarray(colors)

def run():
  # グローバル変数を使用するための記述
  global target_image, base_image, compare_image
  global img
  
  # メインウィンドウを作成
  root = tk.Tk()
  # ウィンドウのタイトルを設定
  root.title('色差確認')
  
  # キャンバスの作成
  target_image = tk.Canvas(width = 400,height = 400)
  base_image = tk.Canvas(width = 30, height = 30)
  compare_image = tk.Canvas(width = 30, height = 30)
                      
  # ボタンの作成
  image_up_button = tk.Button(text='画像上げる',command=image_up)
  image_up_button.grid(row=1, column=0, padx=5, pady=5)
  base_image_crop_button = tk.Button(text='基準画像切り抜き',command=base_image_crop)
  base_image_crop_button.grid(row=1, column=1, padx=5, pady=5)
  compare_image_crop_button = tk.Button(text='比較画像切り抜き',command=compare_image_crop)
  compare_image_crop_button.grid(row=1, column=2, padx=5, pady=5)
  compare_image_crop_button = tk.Button(text='色の距離求める',command=color_distance)
  compare_image_crop_button.grid(row=1, column=3, padx=5, pady=5)
  compare_image_crop_button = tk.Button(text='一番近い色？',command=near_color)
  compare_image_crop_button.grid(row=1, column=4, padx=5, pady=5)
  
  def fix():
    a = root.winfo_geometry().split('+')[0]
    b = a.split('x')
    w = int(b[0])
    h = int(b[1])
    root.geometry('%dx%d' % (w+1,h+1))
  root.update()
  root.after(0, fix)
  
  # メインループ
  root.mainloop()

if __name__  == '__main__':
  run()