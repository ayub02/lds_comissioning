
# pressure in bar
# temp in celcius

def VCFOperational_Pressure(density, pressure, temp):
    ready = True
    counter = 0
    prec = 0.0000001
    vcf = 1

    density15 = density
    while ready:
        Tex = tex(density15)
        Cmp = cmp(density15, temp)
        vcf = VCF(pressure, temp, Tex, Cmp)
        density15_new = density/vcf

        if abs(density15-density15_new) > prec and counter < 20:
            counter += 1
        else:
            ready = False
        if counter > 40:
            ready = False
        density15 = density15_new
    return vcf

def tex(density):
    if density < 610.5:
        tex = 0.00164
    elif density < 653:
        tex = 613.9723/(density*density)
    elif density < 770.5:
        tex = 346.4228/(density*density) + 0.4388/density
    elif density < 788:
        tex = 2680.3206/(density*density) - 0.00336312
    elif density < 839:
        tex = 594.5418/(density*density)
    elif density < 1075.5:
        tex = 186.9696/(density*density) + 0.4862/density
    else:
        tex = 0.000614
    return tex


def cmp(density, Temp):
    e = -1.6208 + (0.00021592*Temp) + (0.87096/(density*density*0.000001)) + ((0.0042092*Temp)/(density*density*0.000001))
    return 2.718281828459045**e/10000


def VCF(Pressure, Temp, tex, cmp):
    return (2.718281828459045**(-tex*(Temp-15)*(1+0.8*tex*(Temp-15))))/(1-cmp*Pressure)



