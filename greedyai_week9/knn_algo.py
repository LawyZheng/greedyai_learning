import heapq
import numpy
from sklearn.datasets.samples_generator import make_blobs
import plotly.graph_objects as go

from sklearn.neighbors import KNeighborsClassifier


def create_sample_data():
    centers = [[-2, 2], [2, 2], [0, 4]]
    x, y = make_blobs(n_samples=60, centers=centers, random_state=0, cluster_std=0.6)
    return x, y, centers


def draw_graph_sample(x, y, centers):
    fig = go.Figure()

    trace_data = go.Scatter(x=x[:, 0],
                            y=x[:, 1],
                            name='sample',
                            mode='markers',
                            marker=dict(size=20,
                                        color=y
                                        )
                            )

    trace_center = go.Scatter(x=centers[:, 0],
                              y=centers[:, 1],
                              mode='markers',
                              name='center',
                              marker=dict(size=10,
                                          color='red',
                                          line_width=2
                                          )
                              )

    fig.add_trace(trace_data)
    fig.add_trace(trace_center)
    fig.show()


def draw_graph_distance(x, y, centers, target, nearest_points):
    fig = go.Figure()

    trace_data = go.Scatter(x=x[:, 0],
                            y=x[:, 1],
                            name='sample',
                            mode='markers',
                            marker=dict(size=20,
                                        color=y
                                        )
                            )

    trace_center = go.Scatter(x=centers[:, 0],
                              y=centers[:, 1],
                              mode='markers',
                              name='center',
                              marker=dict(size=10,
                                          color='red',
                                          line_width=2
                                          )
                              )

    fig.add_trace(trace_data)
    fig.add_trace(trace_center)

    for distance, index, species in nearest_points:
        trace = go.Scatter(x=[x[index, 0], target[0]],
                           y=[x[index, 1], target[1]],
                           mode='lines',
                           marker=dict(size=5,
                                       color='green')
                           )
        fig.add_trace(trace)

    trace_target = go.Scatter(x=[target[0]],
                              y=[target[1]],
                              mode='markers',
                              marker=dict(size=10,
                                          color='orange',
                                          line_width=2
                                          )
                              )
    fig.add_trace(trace_target)

    fig.show()


def knn_algorism(target, x, y, n):
    heap = list()

    for i, each_data in enumerate(x):
        # 计算两点间距离
        distance = numpy.sqrt((target[0] - each_data[0]) ** 2 + (target[1] - each_data[1]) ** 2)

        # python默认最小堆，所以要取负号，转化为用最小堆筛选最大值
        if len(heap) < n:
            heapq.heappush(heap, (-distance, i, y[i]))
        elif -distance > heap[0][0]:
            heapq.heapreplace(heap, (-distance, i, y[i]))

    # 取符号，转化为正数，并排序
    heap = [(-distance, i, species) for distance, i, species in heap]
    heap.sort()

    return heap


def main():
    x, y, centers = create_sample_data()
    centers = numpy.array(centers)

    target = [0, 2]

    nearest_points = knn_algorism(target, x, y, 5)
    print(nearest_points)
    # draw_graph_sample(x, y, centers)
    draw_graph_distance(x, y, centers, target, nearest_points)

    target = [[0, 2]]
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(x, y)
    neighbor_points = knn.kneighbors(target, return_distance=False)
    print(neighbor_points[0])


if __name__ == '__main__':
    main()
