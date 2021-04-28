import numpy as np
import scipy.interpolate as interpolate
from matplotlib import pyplot as plt


def leak_noleak_pressures_flows(p_up, flow, rho, kin_visc, eta, st_dist, st_height, st_dia,
                                is_leak=False, leak_loc=None, leak_dp=None, shut_in=False):
    # p_up in Pascal
    # flow in m3/hr
    # leak_lock in m
    # leak_dp in Pascal
    if is_leak is False:
        pressures, _ = calc_ultimate_ds_pressure(p_up, flow, rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in)
        flow = flow_from_dp(p_up - pressures[-1], flow, rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in)
        return st_dist, pressures, flow, flow


def flow_from_dp(dP, flow_guess, rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in):
    if flow_guess <= 0:
        return 0
    Q = np.arange(1, 2001, 10, dtype=float)
    P = np.zeros(len(Q))
    for i, _ in enumerate(P):
        _, p_down = calc_ultimate_ds_pressure(dP, Q[i], rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in)
        P[i] = dP - p_down
        # print(P[i], '\t', Q[i])
    f_cubic = interpolate.interp1d(P, Q, kind='cubic')
    q_target = f_cubic(dP)

    return q_target, f_cubic


def calc_ultimate_ds_pressure(p_up, flow, rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in):
    P = np.ones(len(st_dist)) * p_up
    for i in range(len(P) - 1):
        P[i + 1] = calc_downstream_pressure(P[i], st_dia[i], st_height[i], st_height[i + 1],
                                            flow, st_dist[i + 1] - st_dist[i], rho, kin_visc, eta, shut_in)
    return P, P[-1]


def calc_downstream_pressure(p_up, pipe_id, h_up, h_down, flow, L, rho, kin_visc, eta, shut_in):
    area_avg = 3.14 * pipe_id ** 2 / 4
    vel = flow / area_avg / 3600
    if flow != 0:
        if shut_in is False:
            fd = darcy(pipe_id, eta, vel, kin_visc)
        if shut_in is True:
            fd = 0
    else:
        fd = 0
    p_down = p_up + rho * 9.81 * (h_up - h_down) - fd * rho * vel ** 2 * L / 2 / pipe_id
    return p_down


def reynold_num(dia, vel, kin_visc):
    return vel * dia / kin_visc


def darcy(_dia, _eta, _vel, _kin_visc):
    Re = reynold_num(_dia, _vel, _kin_visc)
    fd = 0.011
    for i in range(10):
        a = 2 * np.log10(_eta / 3.7 / _dia + 2.51 / Re / np.sqrt(fd))
        fd = (1 / a) ** 2
    return fd

