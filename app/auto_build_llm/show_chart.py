import json, os, math
from copy import deepcopy
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
import numpy as np

try:
    os.chdir('./app')
except:
    pass

def Show_Similarity_Chart(plt, src_path='app/auto_build_llm/compare_data.json', title='不同领域的相似度比较', field='similarity'):
    dict_domain_simi = make_data(src_path, field)

    # 只提取出混合数据-画线箱图
    dict_domain_hybridSimi = calc_hybrid(dict_domain_simi)
    draw_boxplot_chart(plt, dict_domain_hybridSimi, title)

    # 画平均值柱状图
    # dict_domain_avgSimi = calc_agv(dict_domain_simi)
    # draw_bar_chart(plt, dict_domain_avgSimi, title)
    return 0

def calc_hybrid(dict_domain_simi):
    dict_domain_hybridSimi = deepcopy(dict_domain_simi)
    for domain, dict_llm in dict_domain_hybridSimi.items():
        dict_domain_hybridSimi[domain] = dict_llm['hybrid']

    with open('sim_hybrid.json', 'w', encoding='utf-8') as f:
        json.dump(dict_domain_hybridSimi, f, indent=4)
    return dict_domain_hybridSimi


def calc_agv(dict_domain_simi):
    dict_domain_avgSimi = deepcopy(dict_domain_simi)
    # 算平均值
    for domain, dict_llm in dict_domain_avgSimi.items():
        for llm_name, list_simi in dict_llm.items():
            # list_simi = [s for s in list_simi if s > 0]
            dict_llm[llm_name] = sum(list_simi) // len(list_simi)

    # {'CubeSat': {'person': 86.214285714285714, 'gpt-3.5': 37.0}, 'AGV': {'person': 55, 'gpt-3.5': 67}}
    # 根据上面数据，请用python，画一个柱状图组，横坐标是 CubeSat，AGV等，代表领域；纵坐标是 person、gpt-3.5 对应的数值，代表准确率。标清person、gpt-3.5的图例
    return dict_domain_avgSimi

def make_data(src_path, field='similarity'):
    # 获取json
    with open(src_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 收集similarity数据
    dict_domain_avgSimi = {}
    for goal, info in data.items():
        if info['domain'] not in dict_domain_avgSimi:
            dict_domain_avgSimi[info['domain']] = {}
        for llm_name, cut_info in info['subgoal'].items():
            if llm_name not in dict_domain_avgSimi[info['domain']]:
                dict_domain_avgSimi[info['domain']][llm_name] = []
            for create_obj in cut_info:
                if llm_name == 'person':
                    similarity = create_obj['similarity']
                else:
                    score = max(create_obj[field], create_obj[field+'_ss'], create_obj[field+'_so'], create_obj[field+'_sosu'])
                    similarity = math.ceil(score * 100) # baidu 0~1
                dict_domain_avgSimi[info['domain']][llm_name].append(similarity)
    
    # 计算混合相似度
    for domain, dict_llm in dict_domain_avgSimi.items():
        # 取每个模型的最大值
        list_hybrid = []
        arr_sim = list(dict_llm.values())
        for sim_gpt35, sim_gpt4, sim_palm in zip(arr_sim[1], arr_sim[2], arr_sim[3]):
            hybrid = max(sim_gpt35, sim_gpt4, sim_palm)
            list_hybrid.append(hybrid)
        dict_llm['hybrid'] = list_hybrid

    with open('sim.json', 'w', encoding='utf-8') as f:
        json.dump(dict_domain_avgSimi, f, indent=4)

    return dict_domain_avgSimi # 没算平均

def draw_boxplot_chart(plt, dict_domain_hybridSimi, title):
    # 数据
    '''data = {
        "UAV": [35, 24, 32, 45, 41],
        "AutoRobot": [48, 60, 11, 33, 53],
        "CubeSat": [51, 8, 33, 32, 20],
        "CyberSecurity": [32, 79, 86, 62, 29, 30, 40, 25, 43, 47, 38, 32, 53],
        "Automobile": [15, 15, 37, 26, 7, 38, 41, 35, 21, 36, 40, 52, 48],
        "Pacemaker": [13, 47, 56, 32, 56, 42, 42, 36, 44, 47],
        "Aircraft": [41, 51, 52, 45, 31, 33]
    }'''
    data = dict_domain_hybridSimi

    # 生成箱线图
    plt.figure(figsize=(8, 9))
    plt.boxplot(data.values(), labels=data.keys())
    plt.title("Similarity Between Human-Created and LLM-Created Assurance Cases") # Box Plot of Different Categories
    plt.xlabel('Domain', fontweight='bold', fontsize=14)
    plt.ylabel('Similarity to human creation (%)', fontweight='bold', fontsize=14)
    plt.tick_params(axis='y', labelsize=14)  # 调整y轴刻度字体大小
    # # 显示图表
    plt.show()

def draw_bar_chart(plt, all_data, title):  
    # 输入的数据
    # data = {
    #     'CubeSat': {'person': 86.21, 'gpt-3.5': 37.0, 'gpt-4': 77.0},
    #     'AGV': {'person': 55, 'gpt-3.5': 67, 'gpt-4': 99},
    #     'defance': {'person': 55, 'gpt-3.5': 90, 'gpt-4': 99}
    # }

    data = {}
    for domain, dict_avg in all_data.items():
        del dict_avg['person']
        data[domain] = dict_avg

    # 过滤显示失败的数据
    # set_domain = {'person'}
    # set_domain.add('gpt-3.5')
    # set_domain.add('gpt-4')
    # set_domain.add('PaLM 2')
    
    # data = {}
    # for domain, dict_model in all_data.items():
    #     if set(dict_model.keys()) == set_domain:
    #         data[domain] = dict_model

    # 提取数据
    fields = list(data.keys())
    labels = list(next(iter(data.values())).keys())

    # 初始化列表以存储值
    values = {label: [] for label in labels}

    for field in fields:
        for label in labels:
            values[label].append(data[field].get(label, 0))

    # 创建柱状图
    num_fields = len(fields)
    num_labels = len(labels)
    barWidth = 0.8 / num_labels
    r = np.arange(len(fields))

    

    colors = ['b', 'r', 'g', 'y', 'c', 'm', 'k']  # 预定义颜色列表，如有需要可添加更多颜色

    for i, label in enumerate(labels):
        plt.bar(r + i * barWidth, values[label], color=colors[i], width=barWidth, edgecolor='grey', label=label)
        # plt.plot(r + i * barWidth, values[label], color=colors[i], label=label)
        # 在柱状图上添加数值标签
        for x, val in zip(r + i * barWidth, values[label]):
            plt.text(x, val + 1, str(val), ha='center')

    # 添加标签等
    plt.xlabel('Domain', fontweight='bold', fontsize=14)
    plt.xticks([r + barWidth * (num_labels / 2 - 0.5) for r in range(len(fields))], fields)
    plt.ylabel('Similarity to human creation (%)', fontsize=14)
    plt.title(title)
    # plt.set_xlabel('领域', fontweight='bold')
    # plt.set_xticks([r + barWidth * (num_labels / 2 - 0.5) for r in range(len(fields))], fields)
    # plt.set_ylabel('准确率')
    # plt.set_title('不同领域的准确率比较')

    plt.legend()

    # # 显示图表
    # plt.show()

if __name__ == '__main__':
    # Show_Similarity_Chart(plt, src_path='auto_build_llm/compare_data.json')
    # plt.figure(1, figsize=(12, 6))
    # Show_Similarity_Chart(plt, src_path='app/auto_build_llm/compare_data_temp-0.json', title="不同领域的相似度比较(temp=0)")
    # plt.figure(2, figsize=(12, 6))
    plt.figure(figsize=(14.5, 6))

    english_title = "Comparative Analysis of Similarity Between Human-Created and Language Model-Created Assurance Cases Across Different Domains"

    filepath = 'auto_build_llm/history_data/compare_data_temp-0.8.json'
    field = 'similarity_baidu'
    Show_Similarity_Chart(plt, src_path=filepath, title=english_title, field=field)
