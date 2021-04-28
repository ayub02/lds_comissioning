from sim_new import Pipeline
import pandas as pd
import numpy as np
import paho.mqtt.client as mqtt
import json
from time import sleep
from vcf_calc import VCFOperational_Pressure as VCF
import configparser


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


def create_pressure_values(_locations, _pressures, _flow, _norm_density):
    _dict_PT_tag_loc = dict(zip(PTs['Tag'].tolist(), PTs['Distance'].tolist()))
    _dict_PT_tag_station = dict(zip(PTs['Tag'].tolist(), PTs['Station'].tolist()))
    _dict_PT_tag_value = {}
    for _tag, _loc in _dict_PT_tag_loc.items():
        idx = (np.abs(np.array(_locations) - _loc)).argmin()
        _dict_PT_tag_value[_tag] = pressures[idx]

    return _dict_PT_tag_loc, _dict_PT_tag_station, _dict_PT_tag_value


def write_opc_values(_dict_PT_tag_loc, _dict_PT_tag_station, _dict_PT_tag_value, _flow_up, _flow_down, _prod_temp_MKT,
                     _prod_temp_KBS, _prod_temp_FSD, _prod_temp_MCK, _soil_temp_seg1, _soil_temp_seg2, _soil_temp_seg3,
                     _norm_density, _reinj_flow, _leak_location, _leak_pdrop):
    # Writing PT values
    for _tag, _val in _dict_PT_tag_value.items():
        publislhBuffer(_tag, _val / 1e5, _topic=_dict_PT_tag_station[_tag])

    publislhBuffer('PT3003', dict_PT_tag_value['PT3025'] / 1e5, _topic='KBS')
    publislhBuffer('PT3020', dict_PT_tag_value['PT3025'] / 1e5, _topic='KBS')
    publislhBuffer('PT3004', dict_PT_tag_value['PT3025'] / 1e5, _topic='KBS')
    publislhBuffer('PT4000', dict_PT_tag_value['PT4025'] / 1e5, _topic='FSD')
    publislhBuffer('PT4003', dict_PT_tag_value['PT4025'] / 1e5, _topic='FSD')
    publislhBuffer('PT4027', dict_PT_tag_value['PT4025'] / 1e5, _topic='FSD')
    publislhBuffer('PT4004', dict_PT_tag_value['PT4025'] / 1e5, _topic='FSD')

    # Leak parameters
    print('Writing leak parameters')
    publislhBuffer('exp_leak_loc', _leak_location, _topic='misc')
    publislhBuffer('exp_pdrop', _leak_pdrop, _topic='misc')

    # Temperature values
    print('Writing temperature values')
    TT_dict = {'TT2003': _prod_temp_MKT, 'TT3011': _prod_temp_KBS, 'TT4012': _prod_temp_FSD, 'TT5001': _prod_temp_MCK,
               }
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
    if is_leak is False:
        FT_dict = {'FT2080': _flow_up * _norm_density, 'FT3010': (_flow_up + _reinj_flow) * _norm_density,
                   'FT4012': (_flow_up + _reinj_flow) * _norm_density,
                   'FT4013': (_flow_up + _reinj_flow) * _norm_density,
                   'FT5000': (_flow_up + _reinj_flow) * _norm_density}
    if is_leak is True:
        if leak_location <= 150503.3:
            FT_dict = {'FT2080': _flow_up * _norm_density, 'FT3010': (_flow_down + _reinj_flow) * _norm_density,
                       'FT4012': (_flow_down + _reinj_flow) * _norm_density,
                       'FT4013': (_flow_down + _reinj_flow) * _norm_density,
                       'FT5000': (_flow_down + _reinj_flow) * _norm_density}
        elif leak_location <= 283921.8:
            FT_dict = {'FT2080': _flow_up * _norm_density, 'FT3010': (_flow_up + _reinj_flow) * _norm_density,
                       'FT4012': (_flow_down + _reinj_flow) * _norm_density,
                       'FT4013': (_flow_down + _reinj_flow) * _norm_density,
                       'FT5000': (_flow_down + _reinj_flow) * _norm_density}
        elif leak_location <= 283931.8:
            FT_dict = {'FT2080': _flow_up * _norm_density, 'FT3010': (_flow_up + _reinj_flow) * _norm_density,
                       'FT4012': (_flow_up + _reinj_flow) * _norm_density,
                       'FT4013': (_flow_down + _reinj_flow) * _norm_density,
                       'FT5000': (_flow_down + _reinj_flow) * _norm_density}
        elif leak_location <= 363531.4:
            FT_dict = {'FT2080': _flow_up * _norm_density, 'FT3010': (_flow_up + _reinj_flow) * _norm_density,
                       'FT4012': (_flow_up + _reinj_flow) * _norm_density,
                       'FT4013': (_flow_up + _reinj_flow) * _norm_density,
                       'FT5000': (_flow_down + _reinj_flow) * _norm_density}
        else:
            raise ValueError('Leak outside of pipeline')

    publislhBuffer('FT2080', FT_dict['FT2080'], _topic='MKT')
    publislhBuffer('FT3010', FT_dict['FT3010'], _topic='KBS')
    publislhBuffer('FT_reinj', _reinj_flow, _topic='KBS')
    publislhBuffer('FT4012', FT_dict['FT4012'], _topic='FSD')
    publislhBuffer('FT4013', FT_dict['FT4013'], _topic='FSD')
    publislhBuffer('FT5000', FT_dict['FT5000'], _topic='MCK')

    return dict_PT_tag_value, dict_PT_tag_station


# Reading instruments
PTs = pd.read_excel('../data/instrumentation.xlsx', sheet_name='PT')

# Reading configurations
config = configparser.ConfigParser()
config.read('../config/Complete_leak_shutin.ini')

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
shut_in = eval(config['Scenarios']['shut_in'])                                  # True/False
is_leak = eval(config['Scenarios']['is_leak'])                                  # True/False
reinj_flow = float(config['Scenarios']['reinj_flow'])                           # m3/hr
leak_location = float(config['Scenarios']['leak_location'])                     # m
leak_pdrop = float(config['Scenarios']['leak_pdrop'])                           # Pa
steps = int(config['Scenarios']['steps'])                                       # integer
pdrop_PTs = config['Scenarios']['pdrop_PTs'].split(',')                         # list of strings

chainage = pd.read_excel('../data/MKT_MCK_data_points_400m_new.xlsx', sheet_name=0)
mfm = Pipeline(node1_dist=chainage['dist_node1'].tolist(),
               node2_dist=chainage['dist_node2'].tolist(),
               node1_height=chainage['node1_height'].tolist(),
               node2_height=chainage['node2_height'].tolist(),
               length=chainage['length'].tolist(),
               inner_dia=chainage['inner_dia'].tolist(),
               eta=eta,
               norm_density=norm_density,
               kin_viscosity=kin_viscosity)

leak_pdrop_array = np.linspace(0, leak_pdrop, num=steps, endpoint=True)
if shut_in is False:
    if is_leak is False:
        locations, pressures, flow_up, flow_down = mfm.leak_noleak_pressures_flows(upstream_pressure, noLeakFlow,
                                                                                   is_leak=False, leak_loc=None,
                                                                                   leak_dp=None, shut_in=False)

        dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value = create_pressure_values(locations, pressures,
                                                                                         flow_up, norm_density)

        write_opc_values(dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value, flow_up, flow_down, prod_temp_MKT,
                         prod_temp_KBS, prod_temp_FSD, prod_temp_MCK, soil_temp_seg1, soil_temp_seg2, soil_temp_seg3,
                         norm_density, reinj_flow, 0, 0)

    if is_leak is True:
        for val in leak_pdrop_array:
            sleep(2)
            locations, pressures, flow_up, flow_down = mfm.leak_noleak_pressures_flows(upstream_pressure, noLeakFlow,
                                                                                       is_leak=True,
                                                                                       leak_loc=leak_location,
                                                                                       leak_dp=val, shut_in=False)

            dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value = create_pressure_values(locations, pressures,
                                                                                             flow_up, norm_density)

            write_opc_values(dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value, flow_up, flow_down, prod_temp_MKT,
                             prod_temp_KBS, prod_temp_FSD, prod_temp_MCK, soil_temp_seg1, soil_temp_seg2,
                             soil_temp_seg3,
                             norm_density, reinj_flow, leak_location, val)
elif shut_in is True:
    if is_leak is False:
        locations, pressures, flow_up, flow_down = mfm.leak_noleak_pressures_flows(upstream_pressure, noLeakFlow,
                                                                                   is_leak=False, leak_loc=None,
                                                                                   leak_dp=None, shut_in=True)
        dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value = create_pressure_values(locations, pressures,
                                                                                         flow_up, norm_density)
        write_opc_values(dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value, flow_up, flow_down, prod_temp_MKT,
                         prod_temp_KBS, prod_temp_FSD, prod_temp_MCK, soil_temp_seg1, soil_temp_seg2, soil_temp_seg3,
                         norm_density, reinj_flow, 0, 0)

    if is_leak is True:
        locations, pressures, flow_up, flow_down = mfm.leak_noleak_pressures_flows(upstream_pressure, noLeakFlow,
                                                                                   is_leak=False, leak_loc=None,
                                                                                   leak_dp=None, shut_in=True)
        dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value = create_pressure_values(locations, pressures,
                                                                                         flow_up, norm_density)
        PT_tag_value, PT_tag_station = write_opc_values(dict_PT_tag_loc, dict_PT_tag_station, dict_PT_tag_value,
                                                        flow_up, flow_down, prod_temp_MKT,
                                                        prod_temp_KBS, prod_temp_FSD, prod_temp_MCK, soil_temp_seg1,
                                                        soil_temp_seg2, soil_temp_seg3, norm_density,
                                                        reinj_flow, 0, 0)

        for val in leak_pdrop_array:
            print(val)
            for tag in pdrop_PTs:
                publislhBuffer(tag, (PT_tag_value[tag] - val) / 1e5, _topic=PT_tag_station[tag])
            sleep(1)
