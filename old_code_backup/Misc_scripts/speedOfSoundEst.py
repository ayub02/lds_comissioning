from datetime import datetime, timedelta


MKT = datetime(2020, 12, 1, 22, 14, 24, 253000) + timedelta(microseconds=20*302)
BV61 = datetime(2020, 12, 1, 22, 14, 40, 853000) + timedelta(microseconds=20*298)
BV62 = datetime(2020, 12, 1, 22, 14, 42, 93000) + timedelta(microseconds=20*298)
BV63 = datetime(2020, 12, 1, 22, 15, 1, 993000) + timedelta(microseconds=20*292)
BV64 = datetime(2020, 12, 1, 22, 15, 2, 373000) + timedelta(microseconds=20*292)
BV65 = datetime(2020, 12, 1, 22, 15, 44, 573000) + timedelta(microseconds=20*276)
BV66 = datetime(2020, 12, 1, 22, 15, 44, 833000) + timedelta(microseconds=20*276)
KBS = datetime(2020, 12, 1, 22, 16, 38, 453000) + timedelta(microseconds=20*260)

loc_MKT = 0
loc_BV61 = 18.691
loc_BV62 = 20.097
loc_BV63 = 42.458
loc_BV64 = 42.879
loc_BV65 = 90.166
loc_BV66 = 90.447
loc_KBS = 150.5

print('Speed of sound MKT-BV61:     ', round((loc_BV61-loc_MKT)*1000/(BV61-MKT).total_seconds(), 1))
print('Speed of sound BV61-BV62:    ', round((loc_BV62-loc_BV61)*1000/(BV62-BV61).total_seconds(), 1))
print('Speed of sound BV62-BV63:    ', round((loc_BV63-loc_BV62)*1000/(BV63-BV62).total_seconds(), 1))
print('Speed of sound BV63-BV64:    ', round((loc_BV64-loc_BV63)*1000/(BV64-BV63).total_seconds(), 1))
print('Speed of sound BV64-BV65:    ', round((loc_BV65-loc_BV64)*1000/(BV65-BV64).total_seconds(), 1))
print('Speed of sound BV65-BV66:    ', round((loc_BV66-loc_BV65)*1000/(BV66-BV65).total_seconds(), 1))
print('Speed of sound BV66-KBS:     ', round((loc_KBS-loc_BV66)*1000/(KBS-BV66).total_seconds(), 1))



