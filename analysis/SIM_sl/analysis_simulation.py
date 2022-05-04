import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import spatial


def get_s1_u1(data, dt=0.001, scale=1):
    u0 = data.u0
    s0 = data.s0
    alpha = data.alpha
    beta = data.beta
    gamma = data.gamma

    u1 = u0 + (alpha - beta*u0)*dt
    s1 = s0 + (beta*u0 - gamma*s0)*dt
    data['u1_true'] = u1
    data['s1_true'] = s1
    return data

def get_s1_u1_scVelo(data, dt=0.001, scale=1):
    u0 = data.dynamic_u0
    s0 = data.dynamic_s0
    alpha = data.alpha
    beta = data.beta
    gamma = data.gamma

    u1 = u0 + (alpha - beta*u0)*dt
    s1 = s0 + (beta*u0 - gamma*s0)*dt
    data['u1_true'] = u1
    data['s1_true'] = s1
    return data

def subtract(list1, list2):
    difference = []
    zip_object = zip(list1, list2)
    for list1_i, list2_i in zip_object:
        difference.append(list1_i-list2_i)
    return np.array(difference)

def cosine_similarity(u0, s0, u1_t, s1_t, u1, s1):
    """Cost function
    Return:
        list of cosine distance and a list of the index of the next cell
    """
    # Velocity from (u0, s0) to (u1, s1)
    # u0, s0, u1_t, s1_t, u1, s1 =multiple_path['u0'], multiple_path['s0'], multiple_path['u1'], multiple_path['s1'], multiple_path_back_ground_true2['u1_true'], multiple_path_back_ground_true2['s1_true']

        
    uv = subtract(u1.to_list(), u0.to_list())
    sv = subtract(s1.to_list(), s0.to_list())
    uv_t = subtract(u1_t.to_list(), u0.to_list())
    sv_t = subtract(s1_t.to_list(), s0.to_list())
    cos = []
    for i in range(len(u0)):
        cos.append(1 - spatial.distance.cosine([uv[i], sv[i]], [uv_t[i], sv_t[i]]))
    return cos


def cosine_similarity_scVelo(u0, s0, u1_t, s1_t, u1, s1):
    """Cost function
    Return:
        list of cosine distance and a list of the index of the next cell
    """
    # Velocity from (u0, s0) to (u1, s1)
    # u0, s0, u1_t, s1_t, u1, s1 =predict.dynamic_u0, predict.dynamic_s0, observe.u1_true, observe.s1_true, predict.dynamic_u1, predict.dynamic_s1

        
    uv = u1.to_list()
    sv = s1.to_list()
    uv_t = subtract(u1_t.to_list(), u0.to_list())
    sv_t = subtract(s1_t.to_list(), s0.to_list())
    cos = []
    for i in range(len(u0)):
        cos.append(1 - spatial.distance.cosine([uv[i], sv[i]], [uv_t[i], sv_t[i]]))
    return cos

def caluculate_cosin(predic, observe):
    observe = get_s1_u1(observe)
    cos = cosine_similarity(predic.u0, predic.s0, predic.u1, predic.s1, observe.u1_true, observe.s1_true)
    return cos

def caluculate_cosin_scVelo(predict, observe):
    # predict, observe=simulation100_scVelo, simulation100_simulate
    observe = get_s1_u1(observe)
    cos_dynamic = cosine_similarity_scVelo(predict.dynamic_u0, predict.dynamic_s0, observe.u1_true, observe.s1_true, predict.dynamic_u1, predict.dynamic_s1)
    cos_static = cosine_similarity_scVelo(predict.static_u0, predict.static_s0, observe.u1_true, observe.s1_true, predict.static_u1, predict.static_s1)
    return cos_dynamic, cos_static


def get_esitimate(one_test_true, one_test):
    one_test_true_possitive = one_test_true[one_test_true['alpha']==one_test_true.loc[0,'alpha']]
    idx = one_test_true_possitive.index
    alpha_possitive = one_test_true.loc[0,'alpha']
    beta_possitive = one_test_true.loc[0,'beta']
    gamma_possitive = one_test_true.loc[0,'gamma']
    test_possitive = one_test.iloc[idx]
    alpha_possitive_predict = test_possitive['alpha'].mean()
    beta_possitive_predict = test_possitive['beta'].mean()
    gamma_possitive_predict = test_possitive['gamma'].mean()
    possitive = [alpha_possitive/beta_possitive, beta_possitive/beta_possitive, gamma_possitive/beta_possitive]
    possitive_predict = [alpha_possitive_predict/beta_possitive_predict, beta_possitive_predict/beta_possitive_predict, gamma_possitive_predict/beta_possitive_predict]

    one_test_true_zero = one_test_true[one_test_true['alpha']==one_test_true.loc[1100,'alpha']]
    idx = one_test_true_zero.index
    alpha_zero = one_test_true.loc[1100,'alpha']
    beta_zero = one_test_true.loc[1100,'beta']
    gamma_zero = one_test_true.loc[1100,'gamma']
    test_zero = one_test.iloc[idx]
    alpha_zero_predict = test_zero['alpha'].mean()
    beta_zero_predict = test_zero['beta'].mean()
    gamma_zero_predict = test_zero['gamma'].mean()
    zero = [alpha_zero/beta_zero, beta_zero/beta_zero, gamma_zero/beta_zero]
    zero_predict = [alpha_zero_predict/beta_zero_predict, beta_zero_predict/beta_zero_predict, gamma_zero_predict/beta_zero_predict]
    return(possitive, possitive_predict, zero, zero_predict)


def get_similarity_cellDancer(fold):
    """
    esitimate cellDancer
    """
    multiple_path = pd.read_csv('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/simulation/simulation_results/multiple_path/celldacer/multi_path_'+str(fold)+'/detail_e200.csv')
    multiple_path_back_ground_true = pd.read_pickle('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/simulation/data/multi_path/multi_path_'+str(fold)+'.pkl')
    cos_all = []
    for i in range(1000):
        simulation100_cellDancer = multiple_path[multiple_path['gene_name']=='simulation'+str(i).zfill(3)]
        simulation100_simulate = multiple_path_back_ground_true[multiple_path_back_ground_true['gene_list']=='simulation'+str(i).zfill(3)]
        cos = caluculate_cosin(simulation100_cellDancer, simulation100_simulate)
        cos_all.append(np.mean(cos))

        # plt.hist(d)
        # plt.show()
        # plt.hist(s)
        # plt.show()

    cellDancer = pd.DataFrame({'similarity':cos_all, 'method': 'cellDancer', 'fold':fold})
    return(cellDancer)


def get_similarity_scVelo(fold):
    """
    esitimate scVelo
    """
    # fold = i
    multiple_path_scVelo = pd.read_csv('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/simulation/simulation_results/scVelo/s0_u0_s1_u1_dynamic_and_steady_df_'+str(fold)+'.csv')
    multiple_path_back_ground_true = pd.read_pickle('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/simulation/data/multi_path/multi_path_'+str(fold)+'.pkl')
    dynamic = []
    static = []
    for i in range(1000):
        simulation100_scVelo = multiple_path_scVelo[multiple_path_scVelo['gene_list']=='simulation'+str(i).zfill(3)]
        simulation100_simulate = multiple_path_back_ground_true[multiple_path_back_ground_true['gene_list']=='simulation'+str(i).zfill(3)]
        d, s = caluculate_cosin_scVelo(simulation100_scVelo, simulation100_simulate)
        dynamic.append(np.median(d))
        static.append(np.median(s))

        # plt.hist(d)
        # plt.show()
        # plt.hist(s)
        # plt.show()

    scVelo1 = pd.DataFrame({'similarity':dynamic, 'method': 'dynamic', 'fold':fold})
    scVelo2 = pd.DataFrame({'similarity':static, 'method': 'static', 'fold': fold})
    scVelo = pd.concat([scVelo1, scVelo2])
    return(scVelo)


########## analysis cellDancer


multiple_path = pd.read_csv('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/simulation/simulation_results/multiple_path/celldacer/multi_path_0/detail_e200.csv',index_col=0 )
multiple_path_back_ground_true = pd.read_pickle('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/simulation/data/multi_path/multi_path_0.pkl')
multiple_path = multiple_path.sort_values(by = ['gene_name'])


cellDancer_all=pd.DataFrame()
for i in range(10):
    print(i)
    cellDancer = get_similarity_cellDancer(i)
    cellDancer_all = pd.concat([cellDancer_all, cellDancer])


sns.boxplot(x="fold", y="similarity", hue='method', data=cellDancer_all)


all = pd.concat([scVelo_all, cellDancer_all])
sns.boxplot(x="fold", y="similarity", hue='method', data=all)




scVelo_all=pd.DataFrame()
for i in range(10):
    print(i)
    scVelo = get_similarity(i)
    scVelo_all = pd.concat([scVelo_all, scVelo])

scVelo_all.to_csv('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/simulation/data/multi_path/similarity.csv')




