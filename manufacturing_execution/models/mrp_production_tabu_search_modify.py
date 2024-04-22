from odoo import fields, models
import os
import pandas as pd

import random


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @staticmethod
    def write_to_excel(workcenter, terminate_list, obj_val_list):
        write_data = {
            'workcenter': workcenter,
            'terminate_list': terminate_list,
            'obj_val_list': obj_val_list,
        }
        pf = pd.DataFrame(write_data)
        export_path = r'D:\\Odoo_14\\capstone_project\\tabu_search_modify.xlsx'
        if os.path.exists(export_path):
            df_existing = pd.read_excel(export_path)
            df_final = pd.concat([df_existing, pf])
        else:
            df_final = pf
        # Write back to Excel
        df_final.to_excel(export_path, index=False)

    @staticmethod
    def get_neighbor_solutions(current_solution):
        neighbors = []
        for i in range(len(current_solution) - 1):
            neighbor = current_solution.copy()
            neighbor[i], neighbor[i + 1] = current_solution[i + 1], current_solution[i]
            neighbors.append(neighbor)
        return neighbors

    def tabu_search_modify(self, dict_per_workcenter, first_date_start):
        tenure = self.get_tenure(dict_per_workcenter)
        if tenure == 0:
            dict_per_workcenter[1]['date_start'] = self.first_date_planned_start(first_date_start)
            return self.get_initial_solution(dict_per_workcenter)

        tabu_list = []
        current_solution = self.get_initial_solution(dict_per_workcenter)
        best_solution = current_solution
        best_object_value = float('inf')
        best_neighbor_solution = None
        loop_idx = 0
        iterations = 100
        # excel data
        terminate_list = []
        obj_val_list = []
        while loop_idx < iterations:
            neighbor_solutions = self.get_neighbor_solutions(current_solution)

            for neighbor_solution in neighbor_solutions:
                if neighbor_solution not in tabu_list:
                    neighbor_object_val = self.obj_fun(neighbor_solution, dict_per_workcenter, first_date_start)
                    if neighbor_object_val < best_object_value:
                        best_neighbor_solution = neighbor_solution
                        best_object_value = neighbor_object_val

            current_solution = best_neighbor_solution
            tabu_list.append(best_neighbor_solution)
            # prepare data for excel
            terminate_list.append(loop_idx)
            obj_val_list.append(best_object_value)

            if len(tabu_list) > tenure:
                tabu_list.pop(0)

            if self.obj_fun(current_solution, dict_per_workcenter, first_date_start) < self.obj_fun(best_solution, dict_per_workcenter, first_date_start):
                best_solution = current_solution

            loop_idx += 1
        self.write_to_excel(dict_per_workcenter[1]['workcenter'], terminate_list, obj_val_list)
        return best_solution

    def scheduling_planning_orders(self, first_date_start):
        df_groupby_workcenter = self.get_data_groupby_workcenter()  # Lấy dữ liệu đầu vào
        dicts_by_workcenter = []
        solutions_by_workcenter = []
        for name, group in df_groupby_workcenter:
            index = pd.Series([i for i in range(1, len(group['name']) + 1)])
            instance_dict = group.set_index([index]).to_dict('index')
            best_solution = self.tabu_search_modify(instance_dict, first_date_start)
            print(f"Best solution for workcenter {name}: {best_solution}")
            solutions_by_workcenter.append(best_solution)
            dicts_by_workcenter.append(instance_dict)

        order_instance_dicts = []
        idx_of_workcenter = 0
        for solution in solutions_by_workcenter:
            # print(solution)
            # print("workcenter no.", idx_of_workcenter)
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
            for job in solution:  # Chuẩn hoá lại dữ liệu ban đầu theo dữ liệu đã điều độ với số thứ tự từ nhỏ đến lớn.
                order_no.append(dicts_by_workcenter[idx_of_workcenter][job]['no'])
                order_name.append(dicts_by_workcenter[idx_of_workcenter][job]['name'])
                order_weight.append(dicts_by_workcenter[idx_of_workcenter][job]['weight'])
                order_bom.append(dicts_by_workcenter[idx_of_workcenter][job]['bom'])
                order_workcenter.append(dicts_by_workcenter[idx_of_workcenter][job]['workcenter'])
                order_mold.append(dicts_by_workcenter[idx_of_workcenter][job]['mold'])
                order_release_date.append(dicts_by_workcenter[idx_of_workcenter][job]['release_date'])
                order_date_planned_start.append(dicts_by_workcenter[idx_of_workcenter][job]['date_start'])
                order_date_planned_finish.append(dicts_by_workcenter[idx_of_workcenter][job]['date_finish'])
                order_deadline_manufacturing.append(dicts_by_workcenter[idx_of_workcenter][job]['deadline_manufacturing'])
                order_duration_expected.append(dicts_by_workcenter[idx_of_workcenter][job]['duration_expected'])
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
            df = (pd.DataFrame(order_all_info, index=[i for i in range(1, len(order_name) + 1)])
                  .sort_values(by='date_start')
                  .reset_index(drop=True))
            df.index = range(1, len(df) + 1)
            order_instance_dict = df.to_dict('index')
            order_instance_dicts.append(order_instance_dict)
            idx_of_workcenter += 1
            # self.dictionary_display(order_instance_dict)
        return order_instance_dicts
