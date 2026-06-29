"""
轻量贝叶斯知识追踪 · Lightweight Bayesian Knowledge Tracing (BKT)
================================================================
BKT 用学生的答题序列，估计他对某个知识点的"掌握概率"。
这是一个无外部依赖的轻量实现，约 40 行，保证秒跑。

BKT estimates a student's "mastery probability" of a concept from their
sequence of answers. This is a lightweight, dependency-free implementation
(~40 lines) that runs instantly.

四个标准参数 · Four standard parameters:
  P_L0 : 初始掌握概率 · prior probability the skill is already known
  P_T  : 学习概率（不会→会）· probability of transitioning from unlearned to learned
  P_S  : 失误概率（会但答错）· slip: probability of answering wrong despite knowing
  P_G  : 猜对概率（不会但答对）· guess: probability of answering right without knowing

TODO（将来升级）· TODO (future upgrade):
  换成 pyBKT 库可以按数据自动拟合这四个参数，更准确。
  Switch to the pyBKT library to fit these four parameters from data automatically.
    from pyBKT.models import Model
    model = Model(); model.fit(data=df)
  当前用固定参数，足够 demo 和起步。
  Current version uses fixed parameters—sufficient for demo and getting started.
"""


class BKT:
    def __init__(self, p_l0=0.3, p_t=0.15, p_s=0.1, p_g=0.2):
        self.p_l0 = p_l0  # 初始掌握 · prior
        self.p_t = p_t    # 学习 · learn rate
        self.p_s = p_s    # 失误 · slip
        self.p_g = p_g    # 猜对 · guess

    def estimate(self, correct_sequence: list[bool]) -> float:
        """
        给一串对错（按时间顺序），返回最终掌握概率。
        Given a sequence of correct/incorrect (in time order), return final mastery prob.

        没有作答记录时返回初始概率。· Returns prior when there are no attempts.
        """
        p_known = self.p_l0
        for is_correct in correct_sequence:
            # 第一步：根据这次作答更新"当前已掌握"的后验概率
            # Step 1: posterior update of "currently known" given this observation
            if is_correct:
                numerator = p_known * (1 - self.p_s)
                denominator = p_known * (1 - self.p_s) + (1 - p_known) * self.p_g
            else:
                numerator = p_known * self.p_s
                denominator = p_known * self.p_s + (1 - p_known) * (1 - self.p_g)

            p_known_posterior = numerator / denominator if denominator > 0 else p_known

            # 第二步：加上"这次作答后可能学会了"的学习概率
            # Step 2: add the learning opportunity after this attempt
            p_known = p_known_posterior + (1 - p_known_posterior) * self.p_t

        return round(p_known, 4)

    def mastery_state(self, probability: float) -> str:
        """
        把概率映射成三状态（申报书要求的"未掌握/部分掌握/已掌握"）。
        Map probability to three states (proposal's "unlearned/partial/mastered").
        """
        if probability >= 0.7:
            return "mastered"        # 已掌握
        elif probability >= 0.4:
            return "partial"         # 部分掌握
        else:
            return "unlearned"       # 未掌握
