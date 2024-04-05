# -*- coding: utf-8 -*-

from odoo import fields, models

import pandas as pd
import random as rd


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def input_data(self, first_date_start):
        """Returns a dict of jobs numbers as Key and weight, processing time (minutes) and due date (days) as values"""
        mo_name = self.get_mo_name()
        mo_weight = self.get_mo_weight()
        mo_release_date = self.get_mo_release_date(first_date_start)
        mo_due_date = self.get_mo_due_date(first_date_start)
        mo_mold = self.get_mo_mold()
        print(mo_mold)
        mo_duration_expected = self.get_mo_duration_expected()
        all_info = {
            'name': mo_name,
            'wj': mo_weight,
            'rj': mo_release_date,
            'dj': mo_due_date,
            'mold': mo_mold,
            'pj': mo_duration_expected
        }
        print(all_info)
        instance_dict = pd.DataFrame(all_info)
        instance_dict = instance_dict.sort_values(by=['dj', 'name'], ascending=True)  # Sort theo 2 biến là dj và name
        # Vì sort theo EDD nên đơn nào tới hạn trước thì xếp lên đầu,
        # Có thêm name vì mỗi lần thu thập dữ liệu không giống nhau, tập dữ liệu đầu vào luôn cố định, ưu tiên sau dj.
        index = pd.Series([i for i in range(1, len(mo_name) + 1)])  # Đánh số thứ tự để phục vụ cho tính solution.
        instance_dict = instance_dict.set_index([index], 'name')
        instance_dict = instance_dict.to_dict('index')
        return instance_dict

    # 1: {'name': 'WH/MO/00029', 'wj': 2.6, 'mold': 'K038', 'rj': 0, 'dj': 25920, 'pj': 1062.93},
    # 2: {'name': 'WH/MO/00028', 'wj': 2.6, 'mold': 'K039-1', 'rj': 0, 'dj': 27360, 'pj': 4676.87},
    # 3: {'name': 'WH/MO/00027', 'wj': 2.6, 'mold': 'K064', 'rj': 0, 'dj': 28800, 'pj': 3758.5},
    # 4: {'name': 'WH/MO/00026', 'wj': 2.6, 'mold': 'K038', 'rj': 0, 'dj': 30240, 'pj': 2125.85},
    # 5: {'name': 'WH/MO/00025', 'wj': 2.6, 'mold': 'K096-1', 'rj': 0, 'dj': 31680, 'pj': 9853.06},
    # 6: {'name': 'WH/MO/00024', 'wj': 2.6, 'mold': 'K033', 'rj': 0, 'dj': 33120, 'pj': 977.89},
    # 7: {'name': 'WH/MO/00023', 'wj': 2.6, 'mold': 'K039-1', 'rj': 0, 'dj': 34560, 'pj': 2125.85},
    # 8: {'name': 'WH/MO/00022', 'wj': 2.6, 'mold': 'K038', 'rj': 0, 'dj': 36000, 'pj': 2125.85}

    def get_tenure(self, instance_dict):
        """Return the length of Tabu List"""
        if len(instance_dict) < 10:
            tenure = 5
        elif len(instance_dict) < 20:
            tenure = 15
        else:
            tenure = 31
        return tenure

    # Từ solution đưa ra tập giá trị bao gồm:
    # {(1,2):{'move_value':0}, (2,3):{'move_value:0}}
    def get_tabu_structure(self, solution):
        """Takes a dict (input data)
            Returns a dict of tabu attributes(pair of jobs that are swapped) as keys and [move_value]"""
        dict_data = {}
        swap = []
        for i in range(0, len(solution)-1):
            swap.append(solution[i])
            swap.append(solution[i+1])
            dict_data[tuple(swap)] = {'move_value': 0}
            swap = []
        return dict_data

    def get_initial_solution(self, instance_dict):
        n_jobs = len(instance_dict)
        initial_solution = list(range(1, n_jobs+1))
        return initial_solution

    def check_mold(self, job, solution, instance_dict):
        index_solution = solution.index(job)
        if index_solution != len(solution) - 1:
            next_job = solution[index_solution + 1]
            if instance_dict[job]['mold'] != instance_dict[next_job]['mold']:  # Kiểm tra khuôn hiện tại có giống khuôn tiếp theo?
                sj = 3 * 60   # 3 hours
            else:
                sj = 0
        else:
            sj = 0
        return sj

    def obj_fun(self, solution, instance_dict):
        """Takes a set of scheduled jobs, dict (input data)
            Return the objective function value of the solution"""
        ts = 0  # Thời gian bắt đầu bằng 0
        objfun_value = 0
        for job in solution:
            sj = self.check_mold(job, solution, instance_dict)   # Kiểm tra có cần thay khuôn không? Nếu có sj,j+1 +3h
            if solution.index(job) == 0:   # Công việc ban đầu
                te_i = instance_dict[job]["rj"] + instance_dict[job]["pj"] + sj
                # Thời gian kết thúc bằng rj + pj
            elif solution.index(job) > 0:  # Đơn hàng tiếp theo
                if ts > instance_dict[job]["rj"]:
                    te_i = ts + instance_dict[job]["pj"] + sj
                elif ts <= instance_dict[job]["rj"]:
                    te_i = instance_dict[job]["rj"] + instance_dict[job]["pj"] + sj

            d_i = instance_dict[job]["dj"]   # Thời gian quá hạn
            # T_i = max(0, te_i - d_i)
            L_i = te_i - d_i          # Độ trễ đại số bằng thời gian kết thúc - thời gian quá hạn
            if L_i > 0:
                u_i = 1.0
            else:
                u_i = 0.0
            W_i = instance_dict[job]["wj"]

            objfun_value += W_i * u_i     # Giá trị hàm mục tiêu
            # objfun_value += W_i * T_i
            ts = te_i   # thời gian bắt đầu sau bằng thời gian kết thúc
        return objfun_value

    def swap_move(self, solution, i, j):
        """Takes a list (solution) returns a new neighbor solution with i, j swapped"""
        solution = solution.copy()
        # job index in the solution:
        i_index = solution.index(i)
        j_index = solution.index(j)
        # Swap
        solution[i_index], solution[j_index] = solution[j_index], solution[i_index]
        return solution

    def update_tabu_list(self, tabu_list, best_move):
        tabu_list.pop()
        tabu_list.insert(0, best_move)
        return tabu_list

    def check_tabu_list(self, tabu_list, best_move):
        if best_move in tabu_list:
            return True
        else:
            return False

    def get_best_move(self, tabu_structure, tabu_list):
        present_best_move = min(tabu_structure, key=lambda x: tabu_structure[x]['move_value']) # Kiểm tra move value nào là nhỏ nhất
        move_value = tabu_structure[present_best_move]['move_value']  # Lấy giá trị move value nhỏ nhất
        list_key = []
        for key in tabu_structure.keys():
            if tabu_structure[key]['move_value'] == move_value:
                list_key.append(list(key))    # Có thể có nhiều điểm có giá trị tốt nhất.

        just_updated = False
        for index in range(0, len(list_key)):
            best_move = list_key[index]
            check_tabu_list = self.check_tabu_list(tabu_list, best_move) # Kiểm tra Tabu list có cặp đó chưa, có rồi thì bỏ qua.
            if not check_tabu_list:
                tabu_list = self.update_tabu_list(tabu_list, best_move)
                just_updated = True
                break

        if not just_updated:
            best_move = None
            tabu_list = tabu_list
            return best_move, tabu_list
        return tuple(best_move), tabu_list    # Xuất ra được Best Move và Tabu List mới nhất.

    def tabu_search(self, instance_dict):
        """The implementation Tabu Search algorithm with short-term memory and pair swap as Tabu attribute"""
        # Parameters:
        tenure = self.get_tenure(instance_dict)    # Chiều dài Tabu List.

        tabu_list = [[0, 0] for x in range(0, tenure)]   # Khai báo Tabu List.
        current_solution = self.get_initial_solution(instance_dict)  # Tạo current solution là lời giải ban đầu.

        best_objvalue = self.obj_fun(current_solution, instance_dict)   # Tính giá trị hàm mục tiêu
        best_solution = current_solution    # Kết quả điều độ tốt nhất với vòng lặp chạy đầu tiên.

        # tabu_list = [[12, 15], [14, 15], [9, 15], [11, 15], [13, 15], [13, 11], [13, 9], [14, 12], [12, 14], [13, 14], [9, 14], [11, 14], [13, 12], [12, 13], [9, 13], [11, 13], [11, 9], [11, 12], [9, 12], [10, 8], [8, 10], [7, 6], [6, 7], [5, 3], [3, 5], [4, 1], [1, 4], [9, 11], [9, 10], [1, 2], [3, 4]]
        # current_solution = [2, 1, 4, 3, 5, 6, 7, 8, 10, 15, 12, 14, 9, 11, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150]
        # best_solution = [2, 1, 4, 3, 5, 6, 7, 8, 10, 15, 12, 14, 9, 11, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150]
        # best_objvalue = self.obj_fun(best_solution)

        # Sau khi ra chiều dài Tabu List, kết quả điều độ sơ khởi
        n_terminate = 50  # Xác định số lần lặp.
        terminate = 0
        while terminate < n_terminate:
            # Searching the whole neighborhood of the current solution
            tabu_structure = self.get_tabu_structure(current_solution)
            # Tạo ra cầu trúc Tabu ứng với từng cặp lân cận sẽ có một giá trị move value (giá trị hàm mục tiêu)
            for move in tabu_structure:
                candidate_solution = self.swap_move(current_solution, move[0], move[1])
                candidate_objvalue = self.obj_fun(candidate_solution, instance_dict)
                tabu_structure[move]['move_value'] = candidate_objvalue
            # Select the move with the lowest ObjValue in the neighborhood (minimization)
            best_move, tabu_list = self.get_best_move(tabu_structure, tabu_list)
            if best_move is not None:
                current_solution = self.swap_move(current_solution, best_move[0], best_move[1])
                current_objvalue = self.obj_fun(current_solution, instance_dict)    # Tính lại hàm mục tiêu của best move lấy ở trên
                # So sánh với giá trị ham mục tiêu của best move ban đầu.
                if current_objvalue < best_objvalue:
                    best_solution = current_solution
                    best_objvalue = current_objvalue
            terminate += 1
        return best_solution

    # Khi đã ra được best solution, đưa công việc về định dạng ban đầu để thực hiện.
    # Ví dụ: best move = 2 1 3 4 5 -> 1 2 3 4 5
    def order_input_data(self, first_date_start):
        instance_dict = self.input_data(first_date_start)  # Lấy dữ liệu đầu vào
        best = self.tabu_search(instance_dict)  # Tìm ra được kết quả của Tabu Search -> Thứ tự
        order_name = []
        order_weight = []
        order_release_date = []
        order_due_date = []
        order_duration_expected = []
        for job in best:  # Chuẩn hoá lại dữ liệu ban đầu theo dữ liệu đã điều độ với số thứ tự từ nhỏ đến lớn.
            order_name.append(instance_dict[job]['name'])
            order_weight.append(instance_dict[job]['wj'])
            order_release_date.append(instance_dict[job]['rj'])
            order_due_date.append(instance_dict[job]['dj'])
            order_duration_expected.append(instance_dict[job]['pj'])
        order_all_info = {
            'name': order_name,
            'wj': order_weight,
            'rj': order_release_date,
            'dj': order_due_date,
            'pj': order_duration_expected
        }
        order_instance_dict = pd.DataFrame(order_all_info, index=[i for i in range(1, len(order_name) + 1)]).to_dict(
            'index')
        return order_instance_dict
