
def ft_pressure_drop(kin_viscosity, rho_KBS , vol_flow_KBS):

    dyn_visc_KBS = kin_viscosity*1e6*rho_KBS/1000      # cP
    vol_flow_KBS = vol_flow_KBS/1000
    # 0.5 cp
    p00 = 0.1561
    p10 = -0.000202
    p01 = -0.6237
    p20 = -4.289e-09
    p11 = 0.0008857
    p02 = 0.4653
    pdrop_0p5cp = p00 + p10*rho_KBS + p01*vol_flow_KBS + p20*rho_KBS*rho_KBS + p11*rho_KBS*vol_flow_KBS + p02*vol_flow_KBS*vol_flow_KBS;

    # 2 cp
    p00 = 0.1425
    p10 = -0.000186
    p01 = -0.6016
    p20 = -1.79e-08
    p11 = 0.0009583
    p02 = 0.5006
    pdrop_2cp = p00 + p10*rho_KBS + p01*vol_flow_KBS + p20*rho_KBS*rho_KBS + p11*rho_KBS*vol_flow_KBS + p02*vol_flow_KBS*vol_flow_KBS;

    # 3.5 cp
    p00 = 0.1507
    p10 = -0.0002122
    p01 = -0.6027
    p20 = -5.443e-09
    p11 = 0.00101
    p02 = 0.527
    pdrop_3p5cp = p00 + p10*rho_KBS + p01*vol_flow_KBS + p20*rho_KBS*rho_KBS + p11*rho_KBS*vol_flow_KBS + p02*vol_flow_KBS*vol_flow_KBS;

    # 4.5 cp
    p00 = 0.1394
    p10 = -0.0001857
    p01 = -0.6054
    p20 = -2.43e-08
    p11 = 0.001037
    p02 = 0.5416
    pdrop_4p5cp = p00 + p10*rho_KBS + p01*vol_flow_KBS + p20*rho_KBS*rho_KBS + p11*rho_KBS*vol_flow_KBS + p02*vol_flow_KBS*vol_flow_KBS;

    # 5.5 cp
    p00 = 0.1494
    p10 = -0.0002111
    p01 = -0.6103
    p20 = -1.111e-08
    p11 = 0.001064
    p02 = 0.5545
    pdrop_5p5cp = p00 + p10*rho_KBS + p01*vol_flow_KBS + p20*rho_KBS*rho_KBS + p11*rho_KBS*vol_flow_KBS + p02*vol_flow_KBS*vol_flow_KBS;

    if dyn_visc_KBS>=0.5 and dyn_visc_KBS<2:
        slope = (pdrop_0p5cp - pdrop_2cp)/(0.5-2)
        FT_pdrop = slope*(dyn_visc_KBS - 2) + pdrop_2cp

    elif dyn_visc_KBS>=2 and dyn_visc_KBS<3.5:
        slope = (pdrop_2cp - pdrop_3p5cp)/(2-3.5)
        FT_pdrop = slope*(dyn_visc_KBS - 3.5) + pdrop_3p5cp

    elif dyn_visc_KBS>=3.5 and dyn_visc_KBS<4.5:
        slope = (pdrop_3p5cp - pdrop_4p5cp)/(3.5-4.5)
        FT_pdrop = slope*(dyn_visc_KBS - 4.5) + pdrop_4p5cp

    elif dyn_visc_KBS>=4.5 and dyn_visc_KBS<5.5:
        slope = (pdrop_4p5cp - pdrop_5p5cp)/(4.5-5.5)
        FT_pdrop = slope*(dyn_visc_KBS - 5.5) + pdrop_5p5cp
    else:
        print('Dynamic viscosity', dyn_visc_KBS)
        raise ValueError('Viscosity value outside limits')

    return FT_pdrop*1e5
