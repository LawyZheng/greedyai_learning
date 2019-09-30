from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier


# 获取数据
def get_flower_data():
    iris = load_iris()
    iris_data = iris.data
    iris_type = iris.target
    return iris_data, iris_type


def get_knn_accuracy(iris_data, iris_type, n):
    score = 0
    for i in range(n):
        # 筛选训练集
        x_train, x_test, y_train, y_test = train_test_split(iris_data, iris_type, test_size=0.25)
        # 标准化数据
        std = StandardScaler()
        x_train = std.fit_transform(x_train)
        x_test = std.transform(x_test)

        # knn算法，拟合模型
        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(x_train, y_train)

        # 获取预测结果
        # y_predict = knn.predict(x_test)
        # print(y_predict)
        # print(y_test)
        # 计算当前准确率
        print(knn.score(x_test, y_test))
        score += knn.score(x_test, y_test)

    return score / n


def main():
    iris_data, iris_type = get_flower_data()
    print(get_knn_accuracy(iris_data, iris_type, 10))


if __name__ == '__main__':
    main()
