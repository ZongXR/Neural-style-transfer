# %% 导入包
from nst_utils import *
from tensorflow import reduce_sum, square, matmul, reshape, transpose, global_variables_initializer
from tqdm import tqdm


# %% 定义一个函数，计算内容损失
def compute_content_loss(content_pictures, generate_pictures):
    # 获取矩阵大小
    m, n_h, n_w, n_c = generate_pictures.shape.as_list()
    assert m == 1, "维数不对，请检查"
    return (1 / (4 * n_h * n_w * n_c)) * reduce_sum(square(content_pictures - generate_pictures))


# %% 定义一个函数，计算格拉姆矩阵
def gram_matrix(my_matrix):
    return matmul(my_matrix, my_matrix, transpose_b=True)


# %% 定义一个函数，计算一层的风格损失
def compute_one_layer_style_loss(style_pictures, generate_pictures):
    m, n_h, n_w, n_c = generate_pictures.shape.as_list()
    assert m == 1, "维数不对，请检查"
    # 把输入矩阵reshape一下
    style_pictures = transpose(reshape(style_pictures, shape=(n_h * n_w, n_c)))
    generate_pictures = transpose(reshape(generate_pictures, shape=(n_h * n_w, n_c)))
    # 计算输入矩阵的格拉姆矩阵
    gram_style = gram_matrix(style_pictures)
    gram_generate = gram_matrix(generate_pictures)
    return (1 / (2 * n_h * n_w * n_c) ** 2) * reduce_sum(square(gram_style - gram_generate))


# %% 定义一个函数，计算多层style的加权和
def compute_layers_style_loss(model, layers_style_weights, sess):
    result = 0
    for layer_name, weight in layers_style_weights:
        layer = model[layer_name]
        generate_pictures = layer
        style_pictures = sess.run(layer)
        result = result + weight * compute_one_layer_style_loss(style_pictures, generate_pictures)
    return result


# %% 定义一个函数，计算总的损失
def compute_total_cost(content_loss, style_loss, alpha=10, beta=40):
    return alpha * content_loss + beta * style_loss


# %% 定义一个函数，将之前的函数链接起来
def generate_style_pictures(sess, input_picture, model, total_cost, n_iter=200):
    assert n_iter >= 1, "应指定正确的迭代次数"
    # 定义最优化函数
    optimizer = tf.train.AdamOptimizer(2.0)
    train_step = optimizer.minimize(total_cost)
    # 初始化
    sess.run(global_variables_initializer())
    sess.run(model["input"].assign(input_picture))
    # 不断迭代，减小损失函数
    for i in tqdm(range(n_iter)):
        sess.run(train_step)
        generate_picture = sess.run(model["input"])
        if i % 20 == 0:
            show_image(generate_picture)
            save_image("pictures/generated_pictures/其他/iteration_after_%s.jpg" % i, generate_picture)
    # 保存最终结果
    save_image("pictures/梵高/generate.jpg", generate_picture)
    return generate_picture


# %% 测试函数
if __name__ == "__main__":
    # %% 测试 compute_content_loss
    tf.reset_default_graph()
    with tf.Session() as test:
        tf.set_random_seed(1)
        a_C = tf.random_normal([1, 4, 4, 3], mean=1, stddev=4)
        a_G = tf.random_normal([1, 4, 4, 3], mean=1, stddev=4)
        J_content = compute_content_loss(a_C, a_G)
        print("J_content = " + str(J_content.eval()))

    # %% 测试gram_matrix
    tf.reset_default_graph()
    with tf.Session() as test:
        tf.set_random_seed(1)
        A = tf.random_normal([3, 2 * 1], mean=1, stddev=4)
        GA = gram_matrix(A)
        print("GA = \n" + str(GA.eval()))

    # %% 测试compute_one_layer_style_loss
    tf.reset_default_graph()
    with tf.Session() as test:
        tf.set_random_seed(1)
        a_S = tf.random_normal([1, 4, 4, 3], mean=1, stddev=4)
        a_G = tf.random_normal([1, 4, 4, 3], mean=1, stddev=4)
        J_style_layer = compute_one_layer_style_loss(a_S, a_G)
        print("J_style_layer = " + str(J_style_layer.eval()))

    # %% 测试compute_total_cost
    tf.reset_default_graph()
    with tf.Session() as test:
        np.random.seed(3)
        J_content = np.random.randn()
        J_style = np.random.randn()
        J = compute_total_cost(J_content, J_style)
        print("J = " + str(J))


