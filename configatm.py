import re
import os
import pandas as pd
from datetime import datetime

def get_conf():
    file_path = r'C:\ProBase\conf\LOG_1\deviceTrace'
    pattern = 'LOG_+\d\d\d+-+\d\d+-+\d\d+_+\d{10}.TRC'

    for filename in os.listdir(file_path):
        if re.findall(pattern, filename):
            filepath = os.path.join(file_path, filename)
            with open(filepath, mode='r', encoding='ANSI') as datacollect:
                data = datacollect.read()

    #########################ALL_PARNUMBER_IN_TRC#####################################
    portnumber = re.findall("0175\d{7}", data)

    #########################EPP_SERIAL_NUM###########################################
    epp = re.findall('[A-Z]{2}----\w{10}', data)
    eppspisok = []
    for i in epp:
        if i not in eppspisok:
            eppspisok.append(i)
    eppf = eppspisok[0]

    ########################CONVERT_ALL_PORTNUMBER_AND_PORTNUMBER_EPP_CARDREAD########
    isklucheniya = {'01750291752'}
    seen = set()
    result_lines = []
    for line in portnumber:
        if line in isklucheniya:
            result_lines.append(line)
        elif line not in seen:
            result_lines.append(line)
            seen.add(line)

    epppart = result_lines[1]

    cardpart = result_lines[0]

    #######################PRINTER_PORTNUMBER########################################
    tp30part = []
    tp30partsn = ('01750302835', '01750302898')
    for i in tp30partsn:
        if i in seen:
            tp30part.append(i)

    #####################HEAD_RM4H-V_SAFE############################################
    hct = re.findall(r'head.transportUnit.VIRTUAL-HEAD_HCT.fru:\w{10,11}', data)
    pc = re.findall(r"PC:\w{10,11}", data)
    motherboard = re.findall(r'Motherboard:\w{10,11}', data)
    fib = re.findall(r'FIB:\w{10,11}', data)
    cib = re.findall(r'CIB:\w{10,11}', data)
    hlt = re.findall(r'head.transportUnit.VIRTUAL-HEAD_HLT.fru:\d{10,11}', data)
    hmt = re.findall(r'head.transportUnit.VIRTUAL-HEAD_HMT.fru:\d{10,11}', data)
    hut = re.findall(r'head.transportUnit.VIRTUAL-HEAD_HUT.fru:\d{10,11}', data)
    dmab = re.findall(r'head.transportUnit.banknoteReader.eeprom.DMAB:\d{10,11}', data)
    masb = re.findall(r'head.transportUnit.banknoteReader.eeprom.MASB:\d{10,11}', data)
    tasb = re.findall(r'head.transportUnit.banknoteReader.eeprom.TASB:\d{10,11}', data)
    head = re.findall(r'head.fru:\d+\w{9,10}', data)
    collector = re.findall(r'head.ioUnit.collectorUnit.fru:\d{10,11}', data)
    inputout = re.findall(r'head.ioUnit.fru:\d{10,11}', data)
    shuter = re.findall(r'head.ioUnit.shutter.eeprom:\d{10,11}', data)
    sch = re.findall(r'safe.cashUnitString.1.VIRTUAL-SAFE_SCH.fru:\d{10,11}', data)
    ds1 = re.findall(r'safe.cashUnitString.2.dispenseStackingUnit_slot.1.fru:\d{10,11}', data)
    ds2 = re.findall(r'safe.cashUnitString.2.dispenseStackingUnit_slot.2.fru:\d{10,11}', data)
    ds3 = re.findall(r'safe.cashUnitString.2.dispenseStackingUnit_slot.3.fru:\d{10,11}', data)
    ds4 = re.findall(r'safe.cashUnitString.2.dispenseStackingUnit_slot.4.fru:\d{10,11}', data)
    hst = re.findall(r'safe.distributionTransport.VIRTUAL-SAFE_HST.fru:\d{10,11}', data)
    sdt = re.findall(r'safe.distributionTransport.VIRTUAL-SAFE_SDT.fru:\d{10,11}', data)
    svt = re.findall(r'safe.distributionTransport.VIRTUAL-SAFE_SVT.fru:\d{10,11}', data)

    #########################RM4V##############################################
    rm4system = re.findall(r'rm4System.fru:\w{10,11}', data)
    rac = re.findall(r'safe.VIRTUAL-RM4V_CHEST_RACK_UNIT.fru:\d{10,11}', data)
    trans = re.findall(r'safe.VIRTUAL-RM4V_CHEST_TRANSPORT_UNIT.fru:\d{10,11}', data)
    loop = re.findall(r'safe.VIRTUAL-RM4V_LOOPBACK_TRANSPORT.fru:\d{10,11}', data)
    lower = re.findall(r'safe.VIRTUAL-RM4V_LOWER_TRANSPORT.fru:\d{10,11}', data)

    #############################PRINTERSN_CARDREADSN_ESCROWSN################
    tp30 = re.findall('\d{2}[A-Z]{3}\d{5}\s', data)
    cardr = re.search('\d\d\D\d\d\d\d\d\d\d', data)

    ############################ESCROW_PORTNUMBER_SERIALNUMBER################
    escrowpartrm4 = '01750291701'
    escrow = re.findall(r'ESCROW.CU_REFERENCE_VALUES_ARE_MISSING\W{3}\w\W\w{2}\W{4}\w\W{6}\d{10}', data)
    esc = str(escrow)
    esrowconvert = re.findall(r'7\d{9}', esc)

    ###########################SERIALNUMBER_ATM###############################
    SN = re.findall('5310\d{6}', data)
    snnumber = SN[0]

    ##########################ALL_MODULES_SNATM###############################
    ALL = hct, hlt, hmt, hut, dmab, masb, tasb, head, collector, inputout, shuter, sch, ds1, ds2, ds3, ds4, rac, trans, rm4system, loop, lower, hst, sdt, svt, pc, fib, cib, tp30part, tp30, cardpart, cardr, escrowpartrm4, esrowconvert, epppart, eppf, snnumber

    #########################ONLY_PORT_SN_NUMBER#############################
    formatin = str(ALL)
    old = re.findall(r"\d+[0-9A-Z]{9,10}", formatin)
    isklucheniya = {'01750291752'}
    seen = set()
    result_lines = []
    for line in old:
        if line in isklucheniya:
            result_lines.append(line)
        elif line not in seen:
            result_lines.append(line)
            seen.add(line)

    #######################PORT_SERIAL_NUMBER_STRUCTURING####################
    result = ''
    for i, line in enumerate(result_lines):
        if i % 2 == 0:
            result += line + '   '
        elif i == SN:
            result += "" + line + ""
        else:
            result += line + '\n\n'

    print(result)

    #######################CREATE_FOLDER_AND_TXT_FILE########################
    folder_name = r'C:\CONFIG_ATM'
    os.makedirs(folder_name, exist_ok=True)
    with open(os.path.join(folder_name, f'{snnumber}.txt'), 'w') as output_file:
        output_file.write(f'{result}\n')

    txt_file_path = f'C:\CONFIG_ATM\{snnumber}.txt'
    output_file_path = f'C:\CONFIG_ATM\{snnumber}.xlsx'

    #########################CONVERT_IN_XML##################################
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]  # CLEAR_EMPTY_STR

    last_line = lines[-1]  # END_STR
    data_lines = lines[:-1]  # ALL_STR_WITHOUT_ENDSTR

    data = [line.split() for line in data_lines]
    df = pd.DataFrame(data)

    df.insert(0, "", last_line)  # EMPTY_TITLE_FOR_ONE

    current_date = datetime.now().strftime('%d-%m-%Y')
    df[len(df.columns)] = current_date  # EMPTY_TITLE_FOR_DATE

    df.to_excel(output_file_path, index=False, header=False)