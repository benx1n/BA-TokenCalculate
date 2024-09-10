import csv
from pathlib import Path

from pulp import PULP_CBC_CMD, LpMinimize, LpProblem, LpVariable, lpSum, value

dir_path = Path(__file__).parent

# 导出CSV标题
header = [
    "袜子加成",
    "糖果加成",
    "礼物盒加成",
    "Q9",
    "Q10",
    "Q11",
    "Q12",
    "共需耗体",
]
# 各加成组合
A_bonus = [0.3, 0.5, 0.6, 0.7, 0.8, 1]
B_bonus = [0.6, 0.8, 1]
C_bonus = [0.4, 0.6, 0.8, 1]

# 代币期望值
expected_tokens = {"A": 3518, "B": 7116, "C": 9445}

# 代币加成
user_bonus = {"A": 0.3, "B": 0.6, "C": 0.8}

# 关卡掉落数量
drops = {
    1: {"A": 8, "B": 8, "C": 28},
    2: {"A": 28, "C": 16},
    3: {"B": 28, "C": 16},
    4: {"C": 40},
}

# 关卡体力消耗
energy_cost = [20, 20, 20, 20]


def calculate(expected_tokens, user_bonus, drops):
    prob = LpProblem("代币求解", LpMinimize)
    levels = [LpVariable(f"关卡_{i}", lowBound=0, cat="Integer") for i in range(1, 5)]
    prob += lpSum(level * cost for level, cost in zip(levels, energy_cost))

    for token in expected_tokens:
        prob += (
            lpSum(
                (
                    levels[i - 1]
                    * int((drops[i].get(token, 0) * (1 + user_bonus[token]) + 0.999))
                )
                for i in range(1, 5)
            )
            >= expected_tokens[token],
            f"需求_{token}",
        )

    solver = PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    list = []
    for v in levels:
        print(f"{v.name} = {value(v)}")
        list.append(value(v))
    print(f"总体力消耗 = {value(prob.objective)}")
    list.append(value(prob.objective))
    return list


csv_list = []
for A_each in A_bonus:
    for B_each in B_bonus:
        for C_each in C_bonus:
            user_bonus["A"] = A_each
            user_bonus["B"] = B_each
            user_bonus["C"] = C_each
            print(A_each, B_each, C_each)
            result = calculate(expected_tokens, user_bonus, drops)
            print("\n")
            csv_list.append(
                [
                    A_each,
                    B_each,
                    C_each,
                    result[0],
                    result[1],
                    result[2],
                    result[3],
                    result[4],
                ]
            )

with open(dir_path / "calculate.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for row in csv_list:
        writer.writerow(row + [""] * (len(header) - len(row)))
