# -*- coding: utf-8 -*-

from odoo import fields, models
import datetime
import pandas as pd
import random as rd


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_data_dictionary(self):
        """
        Lấy dữ liệu của tất cả các MO cần lên lịch
        """
        mo_no = []
        mo_name = []
        mo_weight = []
        mo_bom = []
        mo_workcenter = []
        mo_mold = []
        mo_release_date = []
        mo_date_planned_start = []
        mo_date_planned_finish = []
        mo_deadline_manufacturing = []
        mo_duration_expected = []
        for rec in self:
            mo_no.append(rec.no_priority_mo)
            mo_name.append(rec.name)
            mo_weight.append(rec.weight_so)
            mo_bom.append(rec.bom_id.code)

            routing = rec.env['mrp.routing.workcenter'].search([('bom_id.code', '=', rec.bom_id.code)])
            mo_workcenter.append(routing.workcenter_id.name)

            product = rec.env['product.template'].search([('name', '=', rec.product_id.name)])
            mold = rec.env['resource.network.connection'].search([('from_resource_id', '=', product.name),
                                                                  ('connection_type', '=', 'product_mold')])
            mo_mold.append(mold)

            mo_release_date.append(self.get_date(rec.release_date))
            mo_date_planned_start.append(self.get_date(rec.date_planned_start))
            mo_date_planned_finish.append(self.get_date(rec.date_planned_finished))
            mo_deadline_manufacturing.append(self.get_date(rec.date_deadline_manufacturing))
            mo_duration_expected.append(rec.production_duration_expected)

        all_info = {'no': mo_no,
                    'name': mo_name,
                    'weight': mo_weight,
                    'bom': mo_bom,
                    'workcenter': mo_workcenter,
                    'mold': mo_mold,
                    'release_date': mo_release_date,
                    'date_start': mo_date_planned_start,
                    'date_finish': mo_date_planned_finish,
                    'deadline_manufacturing': mo_deadline_manufacturing,
                    'duration_expected': mo_duration_expected}

        instance_dict = pd.DataFrame(all_info)
        instance_dict = instance_dict.sort_values(by='no', ascending=False)
        index = pd.Series([i for i in range(1, len(mo_name) + 1)])
        instance_dict = instance_dict.set_index([index], 'name')
        instance_dict = instance_dict.to_dict('index')
        self.dictionary_display(instance_dict)
        return instance_dict

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

    def obj_fun(self, solution, instance_dict, first_date_start):
        """Takes a set of scheduled jobs, dict (input data)
            Return the objective function value of the solution"""
        objfun_value = 0
        for job in solution:
            date_planned_start = self.find_date_planned_start(instance_dict=instance_dict,
                                                              job=job,
                                                              first_date_start=first_date_start)

            instance_dict[job]['date_start'] = date_planned_start
            instance_dict[job]['date_finish'] = date_planned_start + datetime.timedelta(minutes=instance_dict[job]["duration_expected"])

            ts = self.get_time_range(date_planned_start, first_date_start)
            te_i = ts + instance_dict[job]["duration_expected"]
            d_i = self.get_time_range(instance_dict[job]["deadline_manufacturing"], first_date_start)  # Thời gian quá hạn
            L_i = te_i - d_i          # Độ trễ đại số bằng thời gian kết thúc - thời gian quá hạn
            if L_i > 0:
                u_i = 1.0
            else:
                u_i = 0.0
            W_i = instance_dict[job]["weight"]

            objfun_value += W_i * u_i     # Giá trị hàm mục tiêu
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

    def tabu_search(self, instance_dict, first_date_start):
        """The implementation Tabu Search algorithm with short-term memory and pair swap as Tabu attribute"""
        # Parameters:
        tenure = self.get_tenure(instance_dict)    # Chiều dài Tabu List.

        tabu_list = [[0, 0] for x in range(0, tenure)]   # Khai báo Tabu List.
        current_solution = self.get_initial_solution(instance_dict)  # Tạo current solution là lời giải ban đầu.

        best_objvalue = self.obj_fun(current_solution, instance_dict, first_date_start)   # Tính giá trị hàm mục tiêu
        best_solution = current_solution    # Kết quả điều độ tốt nhất với vòng lặp chạy đầu tiên.

        # Sau khi ra chiều dài Tabu List, kết quả điều độ sơ khởi
        n_terminate = 50  # Xác định số lần lặp.
        terminate = 0
        obj_val = 0
        terminate_list = []
        obj_val_list = []
        while terminate < n_terminate:
            terminate_list.append(terminate)
            # Searching the whole neighborhood of the current solution
            tabu_structure = self.get_tabu_structure(current_solution)
            # Tạo ra cầu trúc Tabu ứng với từng cặp lân cận sẽ có một giá trị move value (giá trị hàm mục tiêu)
            for move in tabu_structure:
                candidate_solution = self.swap_move(current_solution, move[0], move[1])
                candidate_objvalue = self.obj_fun(candidate_solution, instance_dict, first_date_start)
                tabu_structure[move]['move_value'] = candidate_objvalue
            # Select the move with the lowest ObjValue in the neighborhood (minimization)
            best_move, tabu_list = self.get_best_move(tabu_structure, tabu_list)
            if best_move is not None:
                current_solution = self.swap_move(current_solution, best_move[0], best_move[1])
                current_objvalue = self.obj_fun(current_solution, instance_dict, first_date_start)    # Tính lại hàm mục tiêu của best move lấy ở trên
                obj_val = current_objvalue
                # So sánh với giá trị ham mục tiêu của best move ban đầu.
                if current_objvalue < best_objvalue:
                    best_solution = current_solution
                    best_objvalue = current_objvalue
                obj_val_list.append(obj_val)
            else:
                obj_val_list.append(obj_val_list[len(obj_val_list)-1])
            terminate += 1
        write_data = {
            'terminate_list': terminate_list,
            'obj_val_list': obj_val_list
        }
        pf = pd.DataFrame(write_data)
        export_path = r'D:\\Odoo_14\\capstone_project\\tabu_search.xlsx'
        pf.to_excel(export_path, index=False)
        return best_solution

    # Khi đã ra được best solution, đưa công việc về định dạng ban đầu để thực hiện.
    # Ví dụ: best move = 2 1 3 4 5 -> 1 2 3 4 5
    def order_input_data(self, first_date_start):
        instance_dict = self.get_data_dictionary()  # Lấy dữ liệu đầu vào
        best = self.tabu_search(instance_dict, first_date_start)  # Tìm ra được kết quả của Tabu Search -> Thứ tự
        order_no = []
        order_name = []
        order_weight = []
        order_bom = []
        order_workcenter = []
        order_mold = []
        order_release_date = []
        order_date_planned_start = []
        order_date_planned_finish = []
        order_deadline_manufacturing = []
        order_duration_expected = []
        for job in best:  # Chuẩn hoá lại dữ liệu ban đầu theo dữ liệu đã điều độ với số thứ tự từ nhỏ đến lớn.
            order_no.append(instance_dict[job]['no'])
            order_name.append(instance_dict[job]['name'])
            order_weight.append(instance_dict[job]['weight'])
            order_bom.append(instance_dict[job]['bom'])
            order_workcenter.append(instance_dict[job]['workcenter'])
            order_mold.append(instance_dict[job]['mold'])
            order_release_date.append(instance_dict[job]['release_date'])
            order_date_planned_start.append(instance_dict[job]['date_start'])
            order_date_planned_finish.append(instance_dict[job]['date_finish'])
            order_deadline_manufacturing.append(instance_dict[job]['deadline_manufacturing'])
            order_duration_expected.append(instance_dict[job]['duration_expected'])
        order_all_info = {
            'no': order_no,
            'name': order_name,
            'weight': order_weight,
            'bom': order_bom,
            'workcenter': order_workcenter,
            'mold': order_mold,
            'release_date': order_release_date,
            'date_start': order_date_planned_start,
            'date_finish': order_date_planned_finish,
            'deadline_manufacturing': order_deadline_manufacturing,
            'duration_expected': order_duration_expected,
        }
        order_instance_dict = pd.DataFrame(order_all_info, index=[i for i in range(1, len(order_name) + 1)]).to_dict(
            'index')
        return order_instance_dict
