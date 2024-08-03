from functools import reduce
from operator import mul
from safety_case.model import aggregation_comm as comm

class AggregationAlgo:
    np = comm.NodeParse()
    lp = comm.LinkParse()
    def calParent(self, node, list_child_node):
        dict_ret_detail = {'dec': 0, 'conf': 0}
        dict_ret_bdu = {}
        nodeInfo = self.np.getDetail(node)
        type = nodeInfo['type']

        if len(list_child_node) > 0:
            list_bdu_w = []
            for cnode in list_child_node:
                dc = self.np.getDecConf(cnode)
                bdu = self.DecConf2BelDisbUncer(dc)
                w = cnode['weight']
                list_bdu_w.append((bdu, w))

            bduA = self.aggregation_List(type, list_bdu_w)
            dcA = self.BelDisbUncer2DecConf(bduA)

            # 保留两位小数
            dict_ret_detail['dec'] = round(dcA.dec, 2)
            dict_ret_detail['conf'] = round(dcA.conf, 2)

            dict_ret_bdu['bel'] = round(bduA.bel, 2)
            dict_ret_bdu['disb'] = round(bduA.disb, 2)
            dict_ret_bdu['uncer'] = round(bduA.uncer, 2)
        else:
            print('结点数量错误')

        node['detail'] = 'type:{},{}'.format(type, self.np.getDetailStr(dict_ret_detail))
        node['reliability'] = ' (%s)' % self.np.getDetailStr(dict_ret_bdu)
        return node


    def DecConf2BelDisbUncer(self, dc):
        bdu = comm.BelDisbUncer()
        bdu.bel = dc.conf * dc.dec
        bdu.disb = dc.conf * (1 - dc.dec)
        bdu.uncer = 1 - bdu.bel - bdu.disb
        return bdu

    def BelDisbUncer2DecConf(self, bdu):
        dc = comm.DecConf()
        dc.conf = bdu.bel + bdu.disb
        if bdu.bel + bdu.disb < 0.0001: # bel+disb==0
            dc.dec = 0
        else:
            dc.dec = bdu.bel / (bdu.bel + bdu.disb)
        return dc

    def aggregation_List(self, type, list_bdu_w):
        # list_bdu_w = [(BelDisbUncer(bel,disb,uncer), weight), (), ...]
        bduA = comm.BelDisbUncer()
        if type == 'PC':
            bduA = self.PC_Arg_List(list_bdu_w)
        elif type == 'PR':
            bduA = self.PR_Arg_List(list_bdu_w)
        elif type == 'WeightedSum':
            bduA = self.Weighted_Sum_List(list_bdu_w)
        elif type == 'ClassicAnd':
            bduA = self.Classic_And_List(list_bdu_w)
        elif type == 'ClassicOr':
            bduA = self.Classic_Or_List(list_bdu_w)
        elif type == 'BucketsEffect':
            bduA = self.Buckets_Effect_List(list_bdu_w)
        else:
            bduA.bel = '计算类型(type)不存在'
        return bduA

    def Buckets_Effect_List(self, list_bdu_w):
        list_bel = [bdu_w[0].bel for bdu_w in list_bdu_w]
        list_disb = [bdu_w[0].disb for bdu_w in list_bdu_w]
        bduA = comm.BelDisbUncer()
        bduA.bel = min(list_bel)
        bduA.disb = max(list_disb)
        bduA.uncer = 1 - bduA.bel - bduA.disb
        return bduA

    def Classic_Or_List(self, list_bdu_w):
        list_bel = [bdu_w[0].bel for bdu_w in list_bdu_w]
        list_disb = [bdu_w[0].disb for bdu_w in list_bdu_w]

        # b1d2d3...dn + b1b2d3...dn + ... + b1b2b3...bn
        list_disb_bel = []
        for j in range(1, len(list_bdu_w)+1):
            tmp_list = []
            for m in range(0, j):
                tmp_list.append(list_bel[m])
            for n in range(j, len(list_bdu_w)):
                tmp_list.append(list_disb[n])
            list_disb_bel.append(tmp_list)

        bduA = comm.BelDisbUncer()
        bduA.bel = 0
        for it in list_disb_bel:
            bduA.bel += self.mulList(it)
        bduA.disb = self.mulList(list_disb)
        bduA.uncer = 1 - bduA.bel - bduA.disb
        return bduA

    def Classic_And_List(self, list_bdu_w):
        list_bel = [bdu_w[0].bel for bdu_w in list_bdu_w]
        list_disb = [bdu_w[0].disb for bdu_w in list_bdu_w]

        # d1b2b3...bn + d1d2b3...bn + ... + d1d2d3...dn
        list_disb_bel = []
        for j in range(1, len(list_bdu_w)+1):
            tmp_list = []
            for m in range(0, j):
                tmp_list.append(list_disb[m])
            for n in range(j, len(list_bdu_w)):
                tmp_list.append(list_bel[n])
            list_disb_bel.append(tmp_list)

        bduA = comm.BelDisbUncer()
        bduA.bel = self.mulList(list_bel)
        bduA.disb = 0
        for it in list_disb_bel:
            bduA.disb += self.mulList(it)
        bduA.uncer = 1 - bduA.bel - bduA.disb
        return bduA

    def Weighted_Sum_List(self, list_bdu_w):
        list_w_bel = [bdu_w[1] * bdu_w[0].bel for bdu_w in list_bdu_w]
        list_w_disb = [bdu_w[1] * bdu_w[0].disb for bdu_w in list_bdu_w]
        list_w = [bdu_w[1] for bdu_w in list_bdu_w]
        bduA = comm.BelDisbUncer()
        bduA.bel = self.addList(list_w_bel) / self.addList(list_w)
        bduA.disb = self.addList(list_w_disb) / self.addList(list_w)
        bduA.uncer = 1 - bduA.bel - bduA.disb
        return bduA

    def PC_Arg_List(self, list_bdu_w):
        list_w = [bdu_w[1] for bdu_w in list_bdu_w]
        list_bel = [bdu_w[0].bel for bdu_w in list_bdu_w]
        list_disb = [bdu_w[0].disb for bdu_w in list_bdu_w]
        list_1_sub_disb = [(1 - bdu_w[0].disb) for bdu_w in list_bdu_w]
        list_bel_mul_w = [bdu_w[0].bel * bdu_w[1] for bdu_w in list_bdu_w]
        list_disb_mul_w = [bdu_w[0].disb * bdu_w[1] for bdu_w in list_bdu_w]
        bduA = comm.BelDisbUncer()
        bduA.bel = self.addList(list_bel_mul_w) + self.mulList(list_bel) * (1 - self.addList(list_w))
        bduA.disb = self.addList(list_disb_mul_w) + (1 - self.mulList(list_1_sub_disb)) * \
                    (1 - self.addList(list_w))
        bduA.uncer = 1 - bduA.bel - bduA.disb
        return bduA

    def PR_Arg_List(self, list_bdu_w):
        list_w = [bdu_w[1] for bdu_w in list_bdu_w]
        list_bel = [bdu_w[0].bel for bdu_w in list_bdu_w]
        list_1_sub_bel = [(1 - bdu_w[0].bel) for bdu_w in list_bdu_w]
        list_disb = [bdu_w[0].disb for bdu_w in list_bdu_w]
        list_bel_mul_w = [bdu_w[0].bel * bdu_w[1] for bdu_w in list_bdu_w]
        list_disb_mul_w = [bdu_w[0].disb * bdu_w[1] for bdu_w in list_bdu_w]
        bduA = comm.BelDisbUncer()
        bduA.bel = self.addList(list_bel_mul_w) + (1 - self.mulList(list_1_sub_bel)) * (
                    1 - self.addList(list_w))
        bduA.disb = self.addList(list_disb_mul_w) + self.mulList(list_disb) * (1 - self.addList(list_w))
        bduA.uncer = 1 - bduA.bel - bduA.disb
        return bduA

    def addList(self, list_num):
        return sum(list_num)

    def mulList(self, list_num):
        return reduce(mul, list_num)
