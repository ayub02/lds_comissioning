import scipy.interpolate as interpolate
from sim_functions import leak_noleak_pressures_flows, flow_from_dp, calc_ultimate_ds_pressure
import pandas as pd
import numpy as np
import paho.mqtt.client as mqtt
import json
from time import sleep
from vcf_calc import VCFOperational_Pressure as VCF
from FT_pdrop import ft_pressure_drop
import configparser


def PCV_pressure(_flow, _norm_density, _open):
    open_lst = np.arange(0, 110, 10)
    kv_lst = [0, 312, 625, 1250, 2500, 5000, 10000, 20000, 40000, 80000, 160000]
    f_cubic = interpolate.interp1d(open_lst, kv_lst, kind='linear')
    kv = f_cubic(_open)
    # print('PCV P drop', '\t', round(_norm_density/1000/(kv/_flow)**2, 2))
    return _norm_density/1000/(kv/_flow)**2*1e5


def pump_pressure(_flow, _norm_density):
    _flow = _flow / 1000
    J0, J1, J2, J3, J4, J5, J6 = 2.81E+02, -7.17E+01, 1.55E+02, -1.09E+02, 0, 0, 0
    head = J6 * _flow ** 6 + J5 * _flow ** 5 + J4 * _flow ** 4 + J3 * _flow ** 3 + J2 * _flow ** 2 + J1 * _flow + J0
    _density = _norm_density
    _p = _density * head * 9.81
    for ii in range(10):
        _p = _density * head * 9.81
        _density = op_density(_norm_density, _p / 1e5, 20)
    return _p


def publislhBuffer(key, val, _topic=None):
    print(_topic, '\t', key, '\t', round(val, 2))
    buff = json.dumps({key: val})
    mqttclient = mqtt.Client('c1', False)
    mqttclient.connect(host=mqttHost, port=mqttPort)  # connect to broker
    ret = mqttclient.publish(_topic, payload=buff, qos=1)
    sleep(0.1)
    mqttclient.disconnect()


def op_density(_norm_density, pressure, temp):
    op_density_list = np.linspace(_norm_density - 20, _norm_density + 20, 50, endpoint=True)
    norm_density_list = []
    for val in op_density_list:
        norm_density_list.append(val / VCF(val, pressure, temp))
    return np.interp(_norm_density, norm_density_list, op_density_list)


def create_pressure_values(_locations, _pressures):
    # Creating PT values
    PTs = pd.read_excel('../data/instrumentation.xlsx', sheet_name='PT')
    dict_PT_tag_loc = dict(zip(PTs['Tag'].tolist(), PTs['Distance'].tolist()))
    dict_PT_tag_station = dict(zip(PTs['Tag'].tolist(), PTs['Station'].tolist()))
    dict_PT_tag_value = {}
    for _tag, _loc in dict_PT_tag_loc.items():
        idx = (np.abs(np.array(_locations) - _loc)).argmin()
        dict_PT_tag_value[_tag] = _pressures[idx]
        # print(_tag, '\t', _loc, '\t', round(dict_PT_tag_value[_tag] / 1e5, 2))
    return dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value


def write_opc_values(dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value, _flow_up, _flow_down, _prod_temp_MKT,
                     _prod_temp_KBS, _prod_temp_FSD, _prod_temp_MCK, _soil_temp_seg1, _soil_temp_seg2, _soil_temp_seg3,
                     _norm_density, _reinj_flow, dp_KBS_FT, dp_KBS_pumps, dp_FSD_pumps, dp_KBS_PCV,
                     dP_FSD_PCV_upstream, P_FSD_PCV_downstream, dp_FSDI_FT, dp_FSDO_FT):
    # Writing PT values
    for _tag, _val in dict_PT_tag_value.items():
        publislhBuffer(_tag, _val / 1e5, _topic=dict_PT_tag_station[_tag])

    publislhBuffer('PT3003', (dict_PT_tag_value['PT3025'] + dp_KBS_FT) / 1e5, _topic='KBS')
    publislhBuffer('PT3020', (dict_PT_tag_value['PT3025'] + dp_KBS_FT + dp_KBS_pumps) / 1e5, _topic='KBS')
    publislhBuffer('PT3004', (dict_PT_tag_value['PT3025'] + dp_KBS_FT + dp_KBS_pumps + dp_KBS_PCV) / 1e5, _topic='KBS')
    publislhBuffer('PT4000', (dict_PT_tag_value['PT4025'] + dP_FSD_PCV_upstream + dp_FSDI_FT) / 1e5, _topic='FSD')
    publislhBuffer('PT4003', (dict_PT_tag_value['PT4025'] + dP_FSD_PCV_upstream + dp_FSDI_FT) / 1e5, _topic='FSD')
    publislhBuffer('PT4027', (dict_PT_tag_value['PT4025'] + dP_FSD_PCV_upstream + dp_FSD_pumps +
                              dp_FSDI_FT) / 1e5, _topic='FSD')
    publislhBuffer('PT4004', (dict_PT_tag_value['PT4025'] + dP_FSD_PCV_upstream + dp_FSD_pumps +
                              P_FSD_PCV_downstream + dp_FSDI_FT) / 1e5, _topic='FSD')


    # Temperature values
    print('Writing temperature values')
    TT_dict = {'TT2003': _prod_temp_MKT, 'TT3011': _prod_temp_KBS, 'TT4012': _prod_temp_FSD, 'TT5001': _prod_temp_MCK}
    publislhBuffer('TT2003', TT_dict['TT2003'], _topic='MKT')
    publislhBuffer('TT3011', TT_dict['TT3011'], _topic='KBS')
    publislhBuffer('TT4012', TT_dict['TT4012'], _topic='FSD')
    publislhBuffer('TT5001', TT_dict['TT5001'], _topic='MCK')
    publislhBuffer('ST', _soil_temp_seg1, _topic='BV65')
    publislhBuffer('ST', _soil_temp_seg2, _topic='BV71')
    publislhBuffer('ST', _soil_temp_seg3, _topic='BV75')

    # Density values
    print('Writing density values')
    DT_dict = {'DT2080': op_density(_norm_density, dict_PT_tag_value['PT2003'] / 1e5, TT_dict['TT2003']),
               'DT3010': op_density(_norm_density, dict_PT_tag_value['PT3025'] / 1e5, TT_dict['TT3011']),
               'DT4012': op_density(_norm_density, dict_PT_tag_value['PT4025'] / 1e5, TT_dict['TT4012']),
               'DT4013': op_density(_norm_density, dict_PT_tag_value['PT4026'] / 1e5, TT_dict['TT4012']),
               'DT5000': op_density(_norm_density, dict_PT_tag_value['PT5000A'] / 1e5, TT_dict['TT5001'])}

    publislhBuffer('DT2080', DT_dict['DT2080'], _topic='MKT')
    publislhBuffer('DT3010', DT_dict['DT3010'], _topic='KBS')
    publislhBuffer('DT4012', DT_dict['DT4012'], _topic='FSD')
    publislhBuffer('DT4013', DT_dict['DT4013'], _topic='FSD')
    publislhBuffer('DT5000', DT_dict['DT5000'], _topic='MCK')

    # Flow values
    print('Writing flow values')
    FT_dict = {'FT2080': _flow_up * _norm_density, 'FT3010': _flow_up * _norm_density,
               'FT4012': _flow_up * _norm_density, 'FT4013': _flow_up * _norm_density,
               'FT5000': _flow_up * _norm_density}

    publislhBuffer('FT2080', FT_dict['FT2080'], _topic='MKT')
    publislhBuffer('FT3010', FT_dict['FT3010'], _topic='KBS')
    publislhBuffer('FT_reinj', _reinj_flow, _topic='KBS')
    publislhBuffer('FT4012', FT_dict['FT4012'], _topic='FSD')
    publislhBuffer('FT4013', FT_dict['FT4013'], _topic='FSD')
    publislhBuffer('FT5000', FT_dict['FT5000'], _topic='MCK')

    return dict_PT_tag_value, dict_PT_tag_station


# Reading configurations
config = configparser.ConfigParser()
config.read('../config/Complete_pump_PCV_FT.ini')

# Kepware
mqttHost = config['Kepware']['mqttHost']
mqttPort = int(config['Kepware']['mqttPort'])

# Fluid properties
eta = float(config['Fluid properties']['eta'])                                  # m
norm_density = float(config['Fluid properties']['norm_density'])                # kg/m3
kin_viscosity = float(config['Fluid properties']['kin_viscosity'])              # m2/s

# Process conditions
noLeakFlow = float(config['Process conditions']['noLeakFlow'])  # m3/hr
upstream_pressure = float(config['Process conditions']['upstream_pressure'])    # Pa
prod_temp_MKT = float(config['Process conditions']['prod_temp_MKT'])            # C
prod_temp_KBS = float(config['Process conditions']['prod_temp_KBS'])            # C
prod_temp_FSD = float(config['Process conditions']['prod_temp_FSD'])            # C
prod_temp_MCK = float(config['Process conditions']['prod_temp_MCK'])            # C
soil_temp_seg1 = float(config['Process conditions']['soil_temp_seg1'])          # C
soil_temp_seg2 = float(config['Process conditions']['soil_temp_seg2'])          # C
soil_temp_seg3 = float(config['Process conditions']['soil_temp_seg3'])          # C

# Scenarios
reinj_flow = float(config['Scenarios']['reinj_flow'])                           # m3/hr
KSB_num_pumps = int(config['Scenarios']['KSB_num_pumps'])                       # integer
FSD_num_pumps = int(config['Scenarios']['FSD_num_pumps'])                       # integer
KBS_PCV = float(config['Scenarios']['KBS_PCV'])                                 # 0-100
FSD_PCV_upstream = float(config['Scenarios']['FSD_PCV_upstream'])               # 0-100
FSD_PCV_downstream = float(config['Scenarios']['FSD_PCV_downstream'])           # 0-100

# Chainage
chainage = pd.read_excel('../data/MKT_MCK_data_points_400m_new.xlsx', sheet_name=0)
node_dist = chainage['dist_node1'].tolist() + [chainage['dist_node2'].tolist()[-1]]
node_height = chainage['node1_height'].tolist() + [chainage['node2_height'].tolist()[-1]]
node_dia = chainage['inner_dia'].tolist()

locations, pressures, flow_up, flow_down = leak_noleak_pressures_flows(upstream_pressure, noLeakFlow,
                                                                       norm_density, kin_viscosity, eta, node_dist,
                                                                       node_height, node_dia, is_leak=False,
                                                                       leak_loc=None, leak_dp=None, shut_in=False)

# Break points
break_points = [[0.0, 150513.292],
                [150513.292, 283931.832],
                [283931.832, 363531.429]]
bpidx = []
for lst in break_points:
    idx0 = np.argmin([abs(val - lst[0]) for val in node_dist])
    idx1 = np.argmin([abs(val - lst[1]) for val in node_dist])
    bpidx.append([idx0, idx1])

_, f_cubic1 = flow_from_dp(upstream_pressure, noLeakFlow, norm_density, kin_viscosity, eta,
                           node_dist[bpidx[0][0]:bpidx[0][1] + 1],
                           node_height[bpidx[0][0]:bpidx[0][1] + 1],
                           node_dia[bpidx[0][0]:bpidx[0][1]], shut_in=False)

# KBS_FSD
_, f_cubic2 = flow_from_dp(upstream_pressure, noLeakFlow, norm_density, kin_viscosity, eta,
                           node_dist[bpidx[1][0]:bpidx[1][1] + 1],
                           node_height[bpidx[1][0]:bpidx[1][1] + 1],
                           node_dia[bpidx[1][0]:bpidx[1][1]], shut_in=False)
# FSD_MCK
_, f_cubic3 = flow_from_dp(upstream_pressure, noLeakFlow, norm_density, kin_viscosity, eta,
                           node_dist[bpidx[2][0]:bpidx[2][1] + 1],
                           node_height[bpidx[2][0]:bpidx[2][1] + 1],
                           node_dia[bpidx[2][0]:bpidx[2][1]], shut_in=False)

# MKT_KBS
_, pdown = calc_ultimate_ds_pressure(upstream_pressure, 0, norm_density, kin_viscosity, eta,
                                     node_dist[bpidx[0][0]:bpidx[0][1] + 1],
                                     node_height[bpidx[0][0]:bpidx[0][1] + 1],
                                     node_dia[bpidx[0][0]:bpidx[0][1]], shut_in=False)
dP_noFlow1 = upstream_pressure - pdown

# KBS_FSD
_, pdown = calc_ultimate_ds_pressure(upstream_pressure, 0, norm_density, kin_viscosity, eta,
                                     node_dist[bpidx[1][0]:bpidx[1][1] + 1],
                                     node_height[bpidx[1][0]:bpidx[1][1] + 1],
                                     node_dia[bpidx[1][0]:bpidx[1][1]], shut_in=False)
dP_noFlow2 = upstream_pressure - pdown

# FSD_MCK
_, pdown = calc_ultimate_ds_pressure(upstream_pressure, 0, norm_density, kin_viscosity, eta,
                                     node_dist[bpidx[2][0]:bpidx[2][1] + 1],
                                     node_height[bpidx[2][0]:bpidx[2][1] + 1],
                                     node_dia[bpidx[2][0]:bpidx[2][1]], shut_in=False)
dP_noFlow3 = upstream_pressure - pdown

print('No flow dPs', round(dP_noFlow1 / 1e5, 2), '\t', round(dP_noFlow2 / 1e5, 2), '\t', round(dP_noFlow3 / 1e5, 2),
      '\t')
P1 = upstream_pressure
P4 = pressures[-1]

for kw in range(3):
    dp_KBS_FT = - ft_pressure_drop(kin_viscosity, norm_density, noLeakFlow)
    dp_FSDI_FT = - ft_pressure_drop(kin_viscosity, norm_density, noLeakFlow)
    dp_FSDO_FT = - ft_pressure_drop(kin_viscosity, norm_density, noLeakFlow)
    print('FT pressure drop', dp_KBS_FT)
    dp_KBS_pumps = pump_pressure(noLeakFlow, norm_density)*KSB_num_pumps
    dp_FSD_pumps = pump_pressure(noLeakFlow, norm_density)*FSD_num_pumps
    dp_KBS_PCV = - PCV_pressure(noLeakFlow, norm_density, KBS_PCV)
    dP_FSD_PCV_upstream = - PCV_pressure(noLeakFlow, norm_density, FSD_PCV_upstream)
    dP_FSD_PCV_downstream = - PCV_pressure(noLeakFlow, norm_density, FSD_PCV_downstream)

    P2inc = dp_KBS_pumps + dp_KBS_PCV + dp_KBS_FT
    P3inc = dp_FSD_pumps + dP_FSD_PCV_upstream + dP_FSD_PCV_downstream + dp_FSDI_FT + dp_FSDO_FT

    P2_lst = np.linspace(8e5, 65e5, 100, endpoint=True)
    P3_lst = np.linspace(8e5, 65e5, 100, endpoint=True)

    x_3D = []
    y_3D = []
    z_3D = []
    for P2 in P2_lst:
        for P3 in P3_lst:
            dP1 = P1 - P2
            dP2 = P2 + P2inc - P3
            dP3 = P3 + P3inc - P4

            if dP1 > dP_noFlow1 and dP2 > dP_noFlow2 and dP3 > dP_noFlow3:
                flow1 = f_cubic1(dP1)
                flow2 = f_cubic2(dP2)
                flow3 = f_cubic3(dP3)
                x_3D.append(P2)
                y_3D.append(P3)
                z_3D.append(abs(flow1 - flow2) + abs(flow2 - flow3))
    idx_min = np.argmin(z_3D)

    P2_lst = np.linspace(x_3D[idx_min] - 2e5, x_3D[idx_min] + 2e5, 300, endpoint=True)
    P3_lst = np.linspace(y_3D[idx_min] - 2e5, y_3D[idx_min] + 2e5, 300, endpoint=True)

    x_3D = []
    y_3D = []
    z_3D = []
    for P2 in P2_lst:
        for P3 in P3_lst:
            dP1 = P1 - P2
            dP2 = P2 + P2inc - P3
            dP3 = P3 + P3inc - P4

            if dP1 > dP_noFlow1 and dP2 > dP_noFlow2 and dP3 > dP_noFlow3:
                flow1 = f_cubic1(dP1)
                flow2 = f_cubic2(dP2)
                flow3 = f_cubic3(dP3)
                x_3D.append(P2)
                y_3D.append(P3)
                z_3D.append(abs(flow1 - flow2) + abs(flow2 - flow3))
    idx_min = np.argmin(z_3D)
    # print('P2', '\t', x_3D[idx_min], '\t', 'P3', '\t', y_3D[idx_min], 'diff', '\t', z_3D[idx_min])

    P2 = x_3D[idx_min]
    P3 = y_3D[idx_min]
    dP1 = P1 - P2
    noLeakFlow = f_cubic1(dP1)
    print('noleakflow', noLeakFlow)

locations1, pressures1, flow_up, flow_down = leak_noleak_pressures_flows(upstream_pressure, noLeakFlow,
                                                                         norm_density, kin_viscosity, eta,
                                                                         node_dist[bpidx[0][0]:bpidx[0][1] + 1],
                                                                         node_height[bpidx[0][0]:bpidx[0][1] + 1],
                                                                         node_dia[bpidx[0][0]:bpidx[0][1]],
                                                                         is_leak=False,
                                                                         leak_loc=None, leak_dp=None, shut_in=False)

locations2, pressures2, flow_up, flow_down = leak_noleak_pressures_flows(P2+P2inc, noLeakFlow,
                                                                         norm_density, kin_viscosity, eta,
                                                                         node_dist[bpidx[1][0]:bpidx[1][1] + 1],
                                                                         node_height[bpidx[1][0]:bpidx[1][1] + 1],
                                                                         node_dia[bpidx[1][0]:bpidx[1][1]],
                                                                         is_leak=False,
                                                                         leak_loc=None, leak_dp=None, shut_in=False)

locations3, pressures3, flow_up, flow_down = leak_noleak_pressures_flows(P3+P3inc, noLeakFlow,
                                                                         norm_density, kin_viscosity, eta,
                                                                         node_dist[bpidx[2][0]:bpidx[2][1] + 1],
                                                                         node_height[bpidx[2][0]:bpidx[2][1] + 1],
                                                                         node_dia[bpidx[2][0]:bpidx[2][1]],
                                                                         is_leak=False,
                                                                         leak_loc=None, leak_dp=None, shut_in=False)

locations = locations1[:-1] + locations2[:-1] + locations3
pressures = list(pressures1)[:-1] + list(pressures2)[:-1] + list(pressures3)

dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value = create_pressure_values(locations, pressures)

write_opc_values(dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value, noLeakFlow, noLeakFlow, prod_temp_MKT,
                 prod_temp_KBS, prod_temp_FSD, prod_temp_MCK, soil_temp_seg1, soil_temp_seg2, soil_temp_seg3,
                 norm_density, reinj_flow, dp_KBS_FT, dp_KBS_pumps, dp_FSD_pumps, dp_KBS_PCV, dP_FSD_PCV_upstream,
                 dP_FSD_PCV_downstream, dp_FSDI_FT, dp_FSDO_FT)
