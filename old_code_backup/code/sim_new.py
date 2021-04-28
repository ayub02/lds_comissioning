import numpy as np

class Pipeline:
    """
    This class lets user set class properties. Pressure values for leak (pt_val_leak) and no leak conditions
    (pt_val_no_leak) are optional
    """
    def __init__(self,
                 node1_dist=None,
                 node2_dist=None,
                 node1_height=None,
                 node2_height=None,
                 length=None,
                 inner_dia=None,
                 eta=15e-5,
                 norm_density=830,
                 kin_viscosity=2e-6):

        self.node1_dist = node1_dist            # m
        self.node2_dist = node2_dist            # m
        self.node1_height = node1_height        # m
        self.node2_height = node2_height        # m
        self.length = length                    # m
        self.inner_dia = inner_dia              # m
        self._eta = eta                         # m
        self._norm_density = norm_density       # kg/m3
        self._kin_viscosity = kin_viscosity     # m2/s

    def leak_noleak_pressures_flows(self, p_up, flow, is_leak=False, leak_loc=None, leak_dp=None, shut_in=False):
        # p_up in Pascal
        # flow in m3/hr
        # leak_lock in m
        # leak_dp in Pascal

        rho = self._norm_density
        kin_visc = self._kin_viscosity
        eta = self._eta
        new_node_dist = self.node1_dist[:]
        new_node_dist.extend([self.node2_dist[-1]])
        new_node_height = self.node1_height[:]
        new_node_height.extend([self.node2_height[-1]])
        new_inner_dia = self.inner_dia[:]

        if shut_in is True:
            pressures, _ = self.calc_ultimate_ds_pressure(p_up, flow, rho, kin_visc, eta,
                                                          new_node_dist,
                                                          new_node_height,
                                                          new_inner_dia, shut_in)
            return new_node_dist, pressures, 0, 0
        elif shut_in is False:

            if is_leak is False:
                pressures, _ = self.calc_ultimate_ds_pressure(p_up, flow, rho, kin_visc, eta,
                                                              new_node_dist,
                                                              new_node_height,
                                                              new_inner_dia, shut_in)
                flow = self.flow_from_dp(p_up, pressures[-1], flow, rho, kin_visc, eta, new_node_dist,
                                         new_node_height, new_inner_dia, shut_in)
                return new_node_dist, pressures, flow, flow

            elif is_leak is True:
                if leak_loc is not None or leak_dp is not None:
                    if leak_loc < new_node_dist[0] or leak_loc > new_node_dist[-1]:
                        raise ValueError(f'Leak location must be between {new_node_dist[0]}m and {new_node_dist[-1]}m')
                else:
                    raise ValueError('leak_loc and leak_dp need to be specified')

                for i, d in enumerate(new_node_dist):
                    if d > leak_loc:
                        break
                dist_ratio = (leak_loc-new_node_dist[i-1])/(new_node_dist[i]-new_node_dist[i-1])
                height_interpolate = dist_ratio*(new_node_height[i]-new_node_height[i-1])+new_node_height[i-1]

                new_node_dist.insert(i, leak_loc)
                new_node_height.insert(i, height_interpolate)
                new_inner_dia.insert(i, self.inner_dia[i-1])

                pressures, _ = self.calc_ultimate_ds_pressure(p_up, flow, rho, kin_visc, eta, new_node_dist,
                                                              new_node_height, new_inner_dia, shut_in)

                flow_up = self.flow_from_dp(p_up, pressures[i]-leak_dp, flow, rho, kin_visc, eta, new_node_dist[:i+1],
                                            new_node_height[:i+1], new_inner_dia[:i], shut_in)
                flow_down = self.flow_from_dp(pressures[i] - leak_dp, pressures[-1], flow, rho, kin_visc, eta,
                                              new_node_dist[i:], new_node_height[i:], new_inner_dia[i:], shut_in)

                leak_pressure_up, _ = self.calc_ultimate_ds_pressure(p_up, flow_up, rho, kin_visc, eta, new_node_dist[:i+1],
                                                                     new_node_height[:i+1], new_inner_dia[:i+1], shut_in)
                leak_pressure_down, _ = self.calc_ultimate_ds_pressure(pressures[i]-leak_dp, flow_down, rho, kin_visc,
                                                                       eta, new_node_dist[i:], new_node_height[i:],
                                                                       new_inner_dia[i:], shut_in)
                leak_pressure = np.append(leak_pressure_up, leak_pressure_down[1:])

                leak_pressure = np.delete(leak_pressure, i)
                new_node_dist = np.delete(new_node_dist, i)

                return new_node_dist, leak_pressure, flow_up, flow_down
            else:
                raise ValueError('is_leak should be either True or False')
        else:
            raise ValueError('shut_in should be either True or False')

    def flow_from_dp(self, p_up, p_down, flow_guess, rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in):
        if flow_guess <= 0:
            return 0
        elif flow_guess<60:
            Q = np.arange(0.1, flow_guess, 0.1, dtype=float)
        else:
            Q = np.arange(flow_guess - 50, flow_guess + 50, 1, dtype=float)
        P = np.zeros(len(Q))
        for i, _ in enumerate(P):
            _, P[i] = self.calc_ultimate_ds_pressure(p_up, Q[i], rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in)
        a, b, c = np.polyfit(P, Q, 2)
        q_target = a*p_down**2 + b*p_down + c
        return q_target

    def calc_ultimate_ds_pressure(self, p_up, flow, rho, kin_visc, eta, st_dist, st_height, st_dia, shut_in):
        P = np.ones(len(st_dist)) * p_up
        for i in range(len(P) - 1):
            P[i + 1] = self.calc_downstream_pressure(P[i],  st_dia[i], st_height[i], st_height[i + 1],
                                                     flow, st_dist[i + 1] - st_dist[i], rho, kin_visc, eta, shut_in)
        return P, P[-1]

    def calc_downstream_pressure(self, p_up, pipe_id, h_up, h_down, flow, L, rho, kin_visc, eta, shut_in):
        area_avg = 3.14 * pipe_id ** 2 / 4
        vel = flow / area_avg / 3600
        if shut_in is False:
            fd = self.darcy(pipe_id, eta, vel, kin_visc)
        if shut_in is True:
            fd = 0
        p_down = p_up + rho * 9.81 * (h_up - h_down) - fd * rho * vel ** 2 * L / 2 / pipe_id
        return p_down

    @staticmethod
    def reynold_num(dia, vel, kin_visc):
        return vel * dia / kin_visc

    # def darcy_old(self, dia, vel, kin_visc, eta):
    #     re = self.reynold_num(dia, vel, kin_visc)
    #     fd = (1 / (-1.8 * np.log10((eta / dia / 3.7) ** 1.11 + 6.9 / re))) ** 2
    #     # return 0.01795
    #     return fd

    def darcy(self, _dia, _eta, _vel, _kin_visc):

        Re = self.reynold_num(_dia, _vel, _kin_visc)
        fd = 0.011
        for i in range(10):
            a = 2 * np.log10(_eta / 3.7 / _dia + 2.51 / Re / np.sqrt(fd))
            fd = (1 / a) ** 2
        return fd#*(1-0.2739)

    @staticmethod
    def validate_str(value=None):
        if value:
            if type(value) is list:
                if any(not isinstance(s, str) or not s.strip() for s in value):
                    raise ValueError('List entries must be a string')
                return value
            else:
                raise ValueError('Input must be a list')
        else:
            raise ValueError('Input cannot be empty')

    @staticmethod
    def validate_num(value=None, minimum=None):
        if value is None:
            raise ValueError('Input cannot be empty')

        if minimum is not None and not isinstance(minimum, (int, float)):
            raise ValueError('Input must be a real number')

        if type(value) is list:
            if not value:
                raise ValueError('List cannot be empty')
            if any(not isinstance(s, (int, float)) for s in value):
                raise ValueError('Input must be a real number')
            if minimum is not None and any(s < minimum for s in value):
                raise ValueError(f'Input must be greater than {minimum}')
            return value

        if isinstance(value, (int, float)):
            if minimum is not None and value < minimum:
                raise ValueError(f'Input must be a greater than {minimum}')
            return value
        else:
            raise ValueError('Data type not recognized')
