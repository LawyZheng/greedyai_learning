'''
基于热搜和问题产生语料库
多个答案可以对应一个问题
加权取平均的方法获取答案

'''
import jieba
from sklearn.metrics.pairwise import cosine_similarity
import numpy
from sqlalchemy import create_engine
import pandas
import time


class Robot(object):
    """docstring for Robot"""
    def __init__(self):
        self.database_engine = create_engine('sqlite:////Users/lawyzheng/Desktop/Code/spider.db')
        jieba.load_userdict('wordsdict.txt')

        self.questions_answer_map = list()
        self.questions_list = self.__get_question_list()
        self.answers_list = self.__get_answer_list()
        self.corpus = self.__get_corpus()
        self.questions_vector_list = self.__get_questions_vector_list()

    def __get_vector(self, splited_question):
        vector = list()
        for each_word in self.corpus:
            vector.append(1 if each_word in splited_question else 0)
        return numpy.array(vector).reshape(1, -1)

    def __get_question_list(self):
        '''
        加载问题集，以及问题所指向答案的index
        '''
        questions_list = list()
        self.questions_answer_map = []

        # 读取用户所记录的问题
        with open('questions.txt', 'r') as f:
            questions_text = f.read()

        for each_question in questions_text.split('\n'):
            answer_map_index = int(each_question.split(' ')[0])
            question = each_question.split(' ')[1].strip()

            self.questions_answer_map.append(answer_map_index)
            questions_list.append(question)

        return questions_list

    def __get_answer_list(self):
        answers_list = list()

        # 由于第一个问题是关于最近发生的事，答案不在问题集中，先加载第一个问题
        weibo_resou_df = pandas.read_sql('tb_weibo_resou', con=self.database_engine, index_col='index')

        # 筛选最近三天最热门的10条热搜
        now = int(time.time())
        weibo_resou_df = weibo_resou_df[weibo_resou_df.end_time >= now - 3 * 24 * 60 * 60]
        weibo_resou_df.sort_values(by=['hot_index'], inplace=True, ascending=False)
        top_10_list = weibo_resou_df.head(10).title.to_numpy()

        first_answer_text = '我想一想哈。最近这几件事情都比较火诶。\n'
        answers_list.append(first_answer_text + '\n'.join(top_10_list))

        # 读取答案集
        with open('answers.txt', 'r') as f:
            answers_text = f.read()

        for each_answer in answers_text.split('\n'):
            answers_list.append(each_answer.split(' ')[1].strip())

        return answers_list

    def __get_corpus(self):
        '''
        载入微博热搜标题和问题集，进行中文切割获得语料库
        '''
        weibo_resou_df = pandas.read_sql('tb_weibo_resou', con=self.database_engine, index_col='index')

        # 将微博热搜转化成词汇
        text = weibo_resou_df.title.to_list()
        corpus = list(jieba.cut(''.join(text)))
        # 将问题集转化成词汇
        corpus += list(jieba.cut(''.join(self.questions_list)))

        return corpus

    def __get_answer_index(self, similarity_list):
        '''
        取指向同一答案的相似度的平均值
        选取平均值大于 0.25 的项目
        '''
        # 初始化变量
        answers_index_list = list()
        pre_answer_index = -1

        # 遍历每个答案的向量，获取所对应的余弦相似度，所指同一个答案的问题添加到一个列表中
        for i, each_similarity in enumerate(similarity_list):
            if self.questions_answer_map[i] != pre_answer_index:
                answers_index_list.append([each_similarity[0][0]])
                pre_answer_index = self.questions_answer_map[i]
            else:
                answers_index_list[self.questions_answer_map[i]].append(each_similarity[0][0])

        # 计算每个答案的平均余弦相似度
        answers_index_list = list(map(numpy.mean, answers_index_list))
        # print(answers_index_list)

        # 返回余弦相似度大于 0.25 的答案
        return [answers_index_list.index(each) for each in answers_index_list if each >= 0.2]

    def __get_questions_vector_list(self):
        splited_questions_list = list()
        questions_vector_list = list()

        # 获得每个问题分词后的结果
        for each_question in self.questions_list:
            splited_questions_list.append(list(jieba.cut(each_question)))

        # 获得每个问题的向量
        for each_splited_question in splited_questions_list:
            questions_vector_list.append(self.__get_vector(each_splited_question))

        return questions_vector_list

    def get_answer(self, target_question):
        similarity_list = list()

        # 获得用户所提问题的向量
        splited_target_question = list(jieba.cut(target_question))
        target_question_vector = self.__get_vector(splited_target_question)

        # 获取目标问题与所有问题的余弦相似度
        for each_question_vector in self.questions_vector_list:
            similarity_list.append(cosine_similarity(each_question_vector, target_question_vector))

        # 获得相对应的答案
        # similarity_list = [
        #     numpy.array([[0.7]]), numpy.array([[0.6]]), numpy.array([[0.7]]), numpy.array([[0.3]]),
        #     numpy.array([[0.1]]), numpy.array([[0.3]]), numpy.array([[0.1]]), numpy.array([[0.1]]),
        #     numpy.array([[0.]]), numpy.array([[0.]]),
        #     numpy.array([[0.]]), numpy.array([[0.]]),
        #     numpy.array([[0.]]), numpy.array([[0.]]),
        #     numpy.array([[0.]])
        # ]
        answers_index_list = self.__get_answer_index(similarity_list)

        # 返回结果
        # 如果没有匹配到合适的答案，返回不知道
        if not len(answers_index_list):
            return '对不起，我不明白您在说什么。'
        # 如果只匹配到一个合适的答案，返回答案
        elif len(answers_index_list) == 1:
            return self.answers_list[answers_index_list[0]]
        # 如果匹配到一个以上合适的答案，推测可能问的问题
        else:
            question_guess_dict = dict()
            # 选取每个答案里相似度最高的那个问题
            for question_index, answer_index in enumerate(self.questions_answer_map):
                # 如果问题所指的答案在返回的列表里
                if answer_index in answers_index_list:
                    cur_max_simi_question_index = question_guess_dict.get(answer_index)
                    # 如果该答案已有所对应的问题在temp_dict中，则比较相似度的大小，进行筛选
                    if cur_max_simi_question_index:
                        max_similarity = max(similarity_list[cur_max_simi_question_index], similarity_list[question_index])
                        question_guess_dict[answer_index] = similarity_list.index(max_similarity)
                    else:
                        question_guess_dict[answer_index] = question_index

            answer_text = '不好意思，我没听清楚您在说啥呀。我猜您可能想说的是...\n'
            for question_index in question_guess_dict.values():
                answer_text += ("%s\n" % self.questions_list[question_index])

            return answer_text

    def add_question_and_answer(self):
        pass


if __name__ == '__main__':
    robot = Robot()
    answer = robot.get_answer('最近有什么热点新闻')
    print(answer)
