# %% 导入包
from toolbox import *
from nst_utils import *
from matplotlib.pyplot import imread
import tensorflow as tf


# %% 读取图片
content_picture = imread("pictures/其他/content_reshape.jpg")
style_picture = imread("pictures/其他/style_reshape.jpg")
content_picture = reshape_and_normalize_image(content_picture)
style_picture = reshape_and_normalize_image(style_picture)

# %% 初始化generate_picture
initial_generate = generate_noise_image(content_picture)

# %% 生成模型
tf.reset_default_graph()
sess = tf.InteractiveSession()

# %% 加载模型并显示
model = load_vgg_model("model/imagenet-vgg-verydeep-19.mat")
for key, value in model.items():
    print("\t%s\t%s" % (key, value))


# %% 计算content损失函数
sess.run(model["input"].assign(content_picture))
out = model["conv4_2"]
a_C = sess.run(out)
a_G = out
J_content = compute_content_loss(a_C, a_G)

# %% 计算style损失函数
sess.run(model["input"].assign(style_picture))
layers_style_weight = [
    ("conv1_1", 0.1),
    ("conv2_1", 0.1),
    ("conv3_1", 0.2),
    ("conv4_1", 0.3),
    ("conv5_1", 0.3)
]
J_style = compute_layers_style_loss(model, layers_style_weight, sess)

# %% 计算总的损失函数
J = compute_total_cost(J_content, J_style)

# %% 开始迭代
generate_style_pictures(sess, initial_generate, model, J, n_iter=1600)

