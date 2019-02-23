import numpy
import matplotlib.pyplot
import cv2


KEYS = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
# 先准备好图片转换后会变成哪些字符,一会儿还会对字符进行排序
charset = ['.', '!', '~', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+']
# orders用于存放排序后字符的顺序
orders = numpy.zeros(len(charset))


# 计算出每个符号再点阵中有多少个点显示
def numsofone_in_charbytes(text):
    # 先获取字符的ascii码值
    offset = ord(text)
    # 然后打开字库文件找到位置
    with open("./ASC16", "rb") as ASC16:
        location = offset*16
        ASC16.seek(location)
        retbytes = ASC16.read(16)
    # 已经获取到该字符的点阵表示字节retbytes,现在要计算这16字节中有多少个1
    count = 0
    for i in range(len(retbytes)):
        # 对于retbytes中的每一个字节
        for j in range(len(KEYS)):
            if KEYS[j] & retbytes[i]:
                count += 1
    return count

for s in range(len(charset)):
    orders[s] = numsofone_in_charbytes(charset[s])
print(orders)

# 依据这个对点进行排序
# numpy.argsort()可以给出排序后各元素在原来数组中的索引
s = numpy.argsort(orders)
print(s)
# 依据上面的索引重新对charset排序
charsetnew = []
for i in range(len(charset)):
    charsetnew.append(charset[s[i]])
print(charsetnew)

# 排序完成后就可以建立图片像素和字符的映射
# 建立映射并不是简单的一个像素对应一个字符，考虑到图片的大小问题
# 有时需要进行缩放,不然做出来的字符画会过大无法显示
# 这里我们将图片中每16*8大小的一个像素块的平均像素值映射成一个字符

# 先写一个函数，将输入图片都裁剪成宽为8的倍数，高为16的倍数，即去掉右边和下面的余值
def trim_pic(img):
    shape = numpy.shape(img)
    # 如果图片本身的长宽不满足要求就直接返回空
    if shape[0] < 16 or shape[1] < 8:
        return None
    height = shape[0]//16
    width = shape[1]//8
    print(height)
    print(width)
    trimed_pic = img[:height*16, :width*8]
    return trimed_pic

# 裁剪完成后，将图片看成16*8大小像素块的组成，然后计算每一个像素块的平均像素值
# 得到平均像素值的矩阵,其实相当于池化操作,这里的图片一律先转成灰度图再输入
def pool16_8(img):
    # shape，第一个元素是矩阵行数，所以是图片的高
    shape = numpy.shape(img)
    row = shape[0] // 16
    cow = shape[1] // 8
    avgpixel = numpy.zeros((row,cow), dtype=float)
    for i in range(row):
        for j in range(cow):
            # 此处计算各个像素块的平均值
            t = 0.0
            for t1 in range(16):
                for t2 in range(8):
                   t += img[t1+i*16, t2+j*8]
            avgpixel[i, j] = t/(16*8)
    return avgpixel

# 上面的函数完成后，再根据映射将元素替换成字符
def cvt2char(avgpixel, charset):
    # avgpixel是计算后的像素平均值，charset是用于制作字符画的字符集
    chars = len(charset)
    race = 255.0/chars
    shape = numpy.shape(avgpixel)
    retcharmatrix = []
    rowchar = []
    for i in range(shape[0]):
        for j in range(shape[1]):
            # 获取像素的等级
            s = avgpixel[i, j] // race
            # 得到对应的字符
            rowchar.append(charset[int(s)])
        retcharmatrix.append(rowchar[:])
        rowchar.clear()
    return retcharmatrix

# stackoverflow上一位大佬写的彩色图片转换成灰度图的代码
def rgb2gray(rgb):
    return numpy.dot(rgb[..., :3], [0.299, 0.587, 0.114])

# 至此，所有的步骤都完成，下面是用图片做实验了



# 读入一张图片
srcimg = matplotlib.pyplot.imread("F:/temp/ppghuahua.jpg")
# 转换成灰度图
grayimg = rgb2gray(srcimg)
# 先裁剪一下
trimedimg = trim_pic(grayimg)
# 再进行池化平均
pooledimg = pool16_8(trimedimg)
# 再得到转换后的字符矩阵
charpic = cvt2char(pooledimg, charsetnew)

# 简单输出看一下

for r in charpic:
    for c in r:
        print(c, end='')
    print()










'''
t = []
rect_list = []
for i in range(16):
    rect_list.append([])



print(rect_list)


text = ""
# 获取text的gb2312编码
gb2312 = text.encode('gb2312')
print(gb2312)
# 将gb2312转换成十六进制的表示，hex_str是bytes类的实例
hex_str = binascii.b2a_hex(gb2312)
print(type(hex_str))
# 按照UTF-8编码转换成字符串
result = str(hex_str, encoding='utf-8')

# eval()函数执行一个字符串表达式，并返回表达式的值
# 前两位对应汉字的第一个字节：区码
area = eval('0x'+result[:2]) - 0xA0
# 后两位对应汉字的第二个字节：位码
index = eval('0x'+result[2:]) - 0xA0

offset = (94*(area-1) + (index-1)) * 32
front_rect = None

# 读取HZK16的汉字库文件
with open("./HZK16", "rb") as f:
    # 找到text字的字模
    f.seek(offset)
    # 读取该字模
    font_rect = f.read(32)


for k in range(len(font_rect) // 2):
    每两个字节一行,一共16行
    row_list = rect_list[k]
    for j in range(2):
        for i in range(8):
            asc = font_rect[k*2+j]
            flag = asc & KEYS[i]
            row_list.append(flag)

for row in rect_list:
    for i in row:
        if i:
            print('0', end=' ')
        else:
            print('.', end=' ')
    print()
'''

