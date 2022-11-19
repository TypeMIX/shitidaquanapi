from fake_useragent import UserAgent  # 防爬检测
import requests as req  # 主要请求库
from bs4 import BeautifulSoup as bs  # 解析html
import difflib  # 计算字符串相似度
from numpy import array  # 既然涉及计算那就有numpy

uac = UserAgent(path=r"fake_useragents.json")


def uaHeaders():
    return {'User-Agent': uac.random}


def similarity(str1: str, str2: str):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


class QuestionNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.args = args


def fetch(query):
    '''
    Search for the question on Shitidaquan and return the answer

    :param query: question string
    :return: answer string
    '''
    url = "https://shitidaquan.com/search?query=%s" % query  # 试题大全地址代参数
    # 这里怎么处理一下try-catch
    resp4bs = req.get(url, headers=uaHeaders())  # 访问
    soup = bs(resp4bs.text, "html.parser")  # 解析
    # print(soup)

    #body = soup.body
    # print(dir(body))
    answerlist = soup.findAll(attrs={'class': "py-2 border-b"})  # 一针见血一点
    # print(answerlist)
    sim = []
    redirects = []
    questitles = []
    for i in answerlist:
        # print(i.findAll(name="a"))
        ases = i.findAll(name="a", attrs={
                         "class": "text-base"})[0]  # 题目,去掉下面的标签

        # 获取链接
        # print(ases)
        # print(ases["href"])
        redirects.append(ases['href'])

        # 相似度
        similar = similarity(ases.text, query)
        # print(similar)
        sim.append(similar)
        questitles.append(ases.text)
        # for j in ases:
        #    print(j)
        #    print(similarity(j.text, query))
        # print('=-=-=-=-=-=-=-=')
    if not redirects or not sim or not questitles:
        raise QuestionNotFound

    sim = array(sim)
    # print(sim)
    redirects = array(redirects)
    # print(redirects)

    ansred = redirects[sim.argmax()]  # 答案的连接
    question = questitles[sim.argmax()]  # 问题
    # print(ansred)

    resp4ans = req.get(ansred, headers=uaHeaders())
    anssoup = bs(resp4ans.text, 'html.parser')
    # print(anssoup)
    answerorig = anssoup.findAll(
        attrs={'class': 'text-sm text-red-500'})[0]  # 更直接一点
    answer = answerorig.text.replace("参考答案：", '')
    # 这里多走一步,把符号改成数字了
    yes_or_no = {"√": "正确", "×": "错误"}
    if answer in yes_or_no.keys():
        answer = yes_or_no[answer]
    # print(answer)
    return question.replace("\n", ''), answer
