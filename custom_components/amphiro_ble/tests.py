datas = [
    "0000080027000027004e752b002c3241000000",
    "0000080026000026004c762b002a3241000000",
    "00000800240000240049762b00293241000000",
    "00000800210000210043792b00253241000000",
    "000008001e00001e003d772b00223241000000",
    "000008001d00001d003a762b00203241000000",
    "000008001b00001b0037762b001f3241000000",
    "000008001400001400287a2b00163241000000",
]


for hex_str in datas:
    print(hex_str)
    val = hex_str

    # Construct v1 containing spaced out representation of the raw data
    v1 = ""
    startCounter = int(val[2:6], 16)
    v1 += str(val)[0:8] + " "

    secs = int(val[6:10], 16)
    v1 += str(val)[8:12] + " "

    v1 += str(val)[12:14] + " "

    a = int(val[12:16], 16)
    v1 += str(val)[14:18] + " "

    pulses = int(val[16:22], 16)
    v1 += str(val)[18:24] + " "

    temp = int(val[22:24], 16)
    v1 += str(val)[24:26] + " "

    kwatts = int(val[24:28], 16) / 100
    v1 += str(val)[26:30] + " "

    # Constant 19?
    v1 += str(val)[30:32] + " "

    v1 += str(val)[32:]

    data = {}
    data["session"] = startCounter
    data["second"] = secs
    data["temp"] = temp
    data["kwatts"] = kwatts
    data["pulses"] = pulses
    data["liters"] = round(pulses / 2560, 2)
    data["liters_rounded"] = round(pulses / 2560)
    data["a"] = a
    print(data)
    print(v1)
