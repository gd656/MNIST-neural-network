import numpy as np
import scipy.special
import os


class NeuralNetwork:

    def __init__(self, input_nodes, hidden_nodes, output_nodes, learning_rate):
        self.inodes = input_nodes
        self.hnodes = hidden_nodes
        self.onodes = output_nodes
        self.lr = learning_rate

        self.wih = np.zeros((self.hnodes, self.inodes))
        self.who = np.zeros((self.onodes, self.hnodes))

        self.activation_function = lambda x: scipy.special.expit(x)

    def load_weights(self, model_path):
        data = np.load(model_path)

        self.wih = data["wih"]
        self.who = data["who"]

    def query(self, inputs_list):

        inputs = np.array(inputs_list, ndmin=2).T

        # input -> hidden
        hidden_inputs = np.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)

        # hidden -> output
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)

        return final_outputs


# 创建神经网络
input_nodes = 784
hidden_nodes = 200
output_nodes = 10
learning_rate = 0.1

network = NeuralNetwork(
    input_nodes,
    hidden_nodes,
    output_nodes,
    learning_rate
)


# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 模型位于项目根目录
MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "mnist_model.npz"
)

# 加载训练好的模型
network.load_weights(MODEL_PATH)

print("MNIST 模型加载成功")