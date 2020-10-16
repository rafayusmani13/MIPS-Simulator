def bin_to_dec(b):
    if(b[0]=="0"):
        return int(b, base=2)
    else:
        flip = ""
        
        for num in b:
            if num == "0":
                flip += "1"
            else:
                flip += "0"
        
        flip = flip[1:]
        return (int(flip, base=2) * -1) - 1

def hex_to_bin(line):
    h = line.replace("\n", "")
    i = int(h, base=16)
    b = bin(i)
    b = b[2:].zfill(32)
    print(f'Instruction {h} in binary is {b}')
    return(b)

def twos(b):
    n = len(b) 
    i = n - 1
    while(i >= 0):
        if (b[i] == '1'):
            break
        i -= 1
    if (i == -1):
        return ('1' + b)
    k = i - 1
    while(k >= 0):
        if (b[k] == '1'):
            b = list(b) 
            b[k] = '0'
            b = ''.join(b) 
        else:
            b = list(b) 
            b[k] = '1'
            b = ''.join(b) 
        k -= 1 
    
    return b

def dec_to_bin(d):
    b = ''
    if d > -1:
        b = bin(d)
        b = b[2:].zfill(32)
    
    else:
        d *= -1
        b = bin(d)[3:]
        twos(b)

    return b

def itosbin(i, n):
    s = ""
    if i >= 0:
        s = bin(i)[2:].zfill(n)
    else:
        s = bin(0-i)[2:].zfill(n)
        s = twos(s)

    return s

# Register list: $0 = [0], $1 = [1], $2 = [2]
# $3 = [3], $4 = [4], $5 = [5], $6 = [6], $7 = [7], $8 = [8], $9 = [9], $10 = [10], $11 = [11], $12 = [12]
# $13 = [13], $14 = [14], $15 = [15], $16 = [16], $17 = [17], $18 = [18], $19 = [19], $20 = [20]
# $21 = [21], $22 = [22], $23 = [23], $24 = [24], $25 = [25], $26 = [26], $27 = [27], $28 = [28]
# $29 = [29], $30 = [30], $31 = [31], $pc = [32], $hi = [33], $lo = [34]

def alg_inst(asm, reg_list):
    #addi, add, sub, mul, mult, mfhi, mflo, slt, lui
    full = asm.split(' ')   #addi $1, $2, 10
    inst = full[0]          #addi
    if inst != 'mflo' and inst != 'mfhi':
        first = int(full[1][1:-1])   # $1,
    if inst != 'mult' and inst != 'mflo' and inst != 'mfhi' and inst != 'lui':
        second = int(full[2][1:-1])  # $2,

    if inst == 'addi':
        const = int(full[3])
        reg_list[first] = reg_list[second] + const
        return reg_list[first]
    elif inst == 'add':
        third = int(full[3][1:])
        reg_list[first] = reg_list[second] + reg_list[third]
        return reg_list[first]
    elif inst == 'sub':
        third = int(full[3][1:])
        reg_list[first] = reg_list[second] - reg_list[third]
        return reg_list[first]
    elif inst == 'slt':
        third = int(full[3][1:])
        if reg_list[second] < reg_list[third]:
            reg_list[first] = 1
        else:
            reg_list[first] = 0
        return reg_list[first]
    elif inst == 'mult':
        second = int(full[2][1:])
        temp = reg_list[first] * reg_list[second]
        val = itosbin(temp, 64)
        reg_list[33] = bin_to_dec(val[:32])  #lo
        if val[32:].__contains__('1'):
            reg_list[34] = bin_to_dec(val[32:])   #hi
    elif inst == 'mul':
        third = int(full[3][1:])
        temp = reg_list[second] * reg_list[third]

        val = itosbin(temp, 64)
        reg_list[33] = bin_to_dec(val[:32])  #lo
        reg_list[first] = bin_to_dec(val[32:])
        if val[32:].__contains__('1'):
            reg_list[34] = bin_to_dec(val[32:])   #hi
        
        return reg_list[first]
    elif inst == 'mflo':
        first = int(full[1][1:])
        reg_list[first] = reg_list[34]
        return reg_list[first]
    elif inst == 'mfhi':
        first = int(full[1][1:])
        reg_list[first] = reg_list[33]
        return reg_list[first]
    elif inst == 'sll':
        const = int(full[3])
        reg_list[first] = reg_list[second] << const
        return reg_list[first]
    elif inst == 'srl':
        const = int(full[3])
        temp = reg_list[second]
        temp = itosbin(temp, 32)
        t = ''
        x = 0
        temp = temp[0:(32 - const)]

        while(x < const):
            temp = '0' + temp
            x += 1
        
        temp = bin_to_dec(temp)
        reg_list[first] = temp
        return reg_list[first]
    elif inst == 'srlv':
        third = int(full[3][1:])
        reg_list[first] = reg_list[second] >> reg_list[third]
        return reg_list[first]
    elif inst == 'lui':
        const = int(full[2])
        reg_list[first] = const << 16
        return reg_list[first]

def log_inst(asm, reg_list):
    #xor, andi, ori
    full = asm.split(' ')   #addi $1, $2, 10
    inst = full[0]          #addi
    first = int(full[1][1:-1])   # $1,
    second = int(full[2][1:-1])  # $2,

    if inst == 'xor':
        third = int(full[3][1:])
        reg_list[first] = reg_list[second] ^ reg_list[third]
        return reg_list[first]
    elif inst == 'andi':
        const = int(full[3])
        reg_list[first] = reg_list[second] & const
        return reg_list[first]
    elif inst == 'ori':
        const = int(full[3])
        reg_list[first] = reg_list[second] | const
        return reg_list[first]

def store_inst(asm, reg_list, dm_list):
    #lw, sw
    full = asm.split(' ')   #lw $3, 0($2)
    inst = full[0]          #lw
    first = int(full[1][1:-1])   # $3,
    after = full[2]              #0($2)

    first_i = after.find('(')
    second_i = after.find('$')
    shift = int(after[:first_i])
    second = int(after[(second_i + 1):-1])
    index = ((shift + reg_list[second]) - 8192) // 4

    if inst == 'sw':
        dm_list[index] = reg_list[first]
    elif inst == 'lw':
        reg_list[first] = dm_list[index]
        return reg_list[first]

def branch_inst(asm, reg_list, pc, index):
    #j, bne, beq
    full = asm.split(' ')   #bne $25, $13, 2
    inst = full[0]          #j, bne, beq

    if inst != 'j':
        first = int(full[1][1:-1])      #25
        second = int(full[2][1:-1])     #13
        const = int(full[3])            #2
    else:
        const = int(full[1])

    if inst == 'j':
        index = int(const / 4)
        return index
    elif inst == 'beq':
        if reg_list[first] == reg_list[second]:     #$25 != $13
            index += int(const)
            index += 1
            return index
        else:
            index += 1
            return index
    elif inst == 'bne':
        if reg_list[first] != reg_list[second]:
            index += int(const)
            index += 1
            return index
        else:
            index += 1
            return index

def special_inst(asm, reg_list): #width
    full = asm.split(' ')
    inst = full[0]
    first = int(full[1][1:-1])   # $1,
    second = int(full[2][1:-1])  # $2, all that matters here
    m = 0
    l = 0
    w = 0
    
    if(second != 0):
        temp = itosbin(reg_list[second], 32)
        w = 1
    
    ind = 0
    while ind < 32:# or m == ind:
        if (temp[ind] == '1'):
            m = ind
            break
        else:
            ind += 1
    
    ind = len(temp) - 1
    while ind >= 0:# or l == ind:
        if(temp[ind] == '1'):
            l = ind
            break
        else:
            ind -= 1

    if w == 1:
        w += (l - m)

    reg_list[first] = w

    return reg_list[first]

def process(b):
    b_op = b[0:6]
    b_rs = b[6:11]
    b_rt = b[11:16]
    b_imm = b[16:]
    b_func = b[26:]
    b_rd = b[16:21]
    b_sa = b[21:26]
    target = b[6:]
    op = True
    print(f'-> {b_op} | {b_rs} | {b_rt} | {b_imm}')
    asm = ""
    if b_op == '000000':  #r-type
        if b_func == "100000":  #add
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            imm = bin_to_dec(b_imm)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            imm = str(imm)
            asm = "add " + rd + ", " + rs + ", " + rt
            print(f'in asm: {asm}')
        elif b_func == "101010":  #slt
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            imm = bin_to_dec(b_imm)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            imm = str(imm)
            asm = "slt " + rd + ", " + rs + ", " + rt
            print(f'in asm: {asm}')
        elif b_func == "100010":  #sub
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            imm = bin_to_dec(b_imm)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            imm = str(imm)
            asm = "sub " + rd + ", " + rs + ", " + rt
            print(f'in asm: {asm}')
        elif b_func == "100110":  #xor
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            imm = bin_to_dec(b_imm)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            imm = str(imm)
            asm = "xor " + rd + ", " + rs + ", " + rt
            print(f'in asm: {asm}')
        elif b_func == "011000":  #mult
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            imm = bin_to_dec(b_imm)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            imm = str(imm)
            asm = "mult " + rs + ", " + rt
            print(f'in asm: {asm}')
        elif b_func == "010010":  #mflo
            rd = int(b_rd, base=2)
            op = False
            rd = "$" + str(rd)
            asm = "mflo " + rd
            print(f'in asm: {asm}')
        elif b_func == "000010":  #srl
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            sa = bin_to_dec(b_sa)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            sa = str(sa)
            asm = "srl " + rd + ", " + rt + ", " + sa
            print(f'in asm: {asm}')
        elif b_func == "000000":  #sll
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            sa = bin_to_dec(b_sa)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            sa = str(sa)
            asm = "srl " + rd + ", " + rt + ", " + sa
            print(f'in asm: {asm}')
        elif b_func == "000110":  #srlv
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            sa = bin_to_dec(b_sa)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            sa = str(sa)
            asm = "srlv " + rd + ", " + rt + ", " + rs
            print(f'in asm: {asm}')
        elif b_func == "000000":  #sll
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            sa = bin_to_dec(b_sa)
            op = False
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            sa = str(sa)
            asm = "sll " + rd + ", " + rt + ", " + sa
            print(f'in asm: {asm}')
        elif b_func == "010000":  #mfhi
            rd = int(b_rd, base=2)
            op = False
            rd = "$" + str(rd)
            asm = "mfhi " + rd
            print(f'in asm: {asm}')

    elif b_op == "001000":  #addi
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "addi " + rt + ", " + rs + ", " + imm
        print(f'in asm: {asm}')
    elif b_op == "011100": #mul
            rs = int(b_rs, base=2)
            rt = int(b_rt, base=2)
            rd = int(b_rd, base=2)
            imm = bin_to_dec(b_imm)
            op = True
            rs = "$" + str(rs)
            rt = "$" + str(rt)
            rd = "$" + str(rd)
            imm = str(imm)
            asm = "mul " + rd + ", " + rs + ", " + rt
            print(f'in asm: {asm}')
    elif b_op == "001100":  #andi
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "andi " + rt + ", " + rs + ", " + imm
        print(f'in asm: {asm}')
    elif b_op == "001101":  #ori
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "ori " + rt + ", " + rs + ", " + imm
        print(f'in asm: {asm}')
    elif b_op == "111111":  #special
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "w " + rt + ", " + rs + ", " + imm
        print(f'in asm: {asm}')
    elif b_op == "100011":  #lw
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "lw " + rt + ", " + imm + "(" + rs + ")"
        print(f'in asm: {asm}')
    elif b_op == "101011":  #sw
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "sw " + rt + ", " + imm + "(" + rs + ")"
        print(f'in asm: {asm}')
    elif b_op == "001111":  #lui
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "lui " + rt + ", " + imm
        print(f'in asm: {asm}')
    elif b_op == "000100":  #beq
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "beq " + rs + ", " + rt + ", " + imm
        print(f'in asm: {asm}')
    elif b_op == "000101":  #bne
        rs = int(b_rs, base=2)
        rt = int(b_rt, base=2)
        imm = bin_to_dec(b_imm)
        op = True
        rs = "$" + str(rs)
        rt = "$" + str(rt)
        imm = str(imm)
        asm = "bne " + rs + ", " + rt + ", " + imm
        print(f'in asm: {asm}')
    elif b_op == "000010":  #jump
        tar = int(target, base=2)
        op = True
        tar = tar * 4
        tar = str(tar)
        asm = "j " + tar
        print(f'in asm: {asm}')
    else:
        if op:
            print(f'NO idea about op = {b_op}')
        else:
            print(f'NO idea about func = {b_func}')
    return (asm)

def exec(asmline, reg, dm, pc, index):
    alg = ["addi", "add", "sub", "slt", "srl", "sll", "srlv", "mult", "mul", "mflo", "mfhi", "lui"]
    log = ["xor", "andi", "ori"]
    mem = ["sw", "lw"]
    branch = ["j", "beq", "bne"]
    special = ["w"]

    if (alg.__contains__(asmline[:4])) or (alg.__contains__(asmline[:3])):
        alg_inst(asmline, reg)
    if (log.__contains__(asmline[:4])) or (log.__contains__(asmline[:3])):
        log_inst(asmline, reg)
    if(mem.__contains__(asmline[:2]) or mem.__contains__(asmline[:3])):
        store_inst(asmline, reg, dm)
    if(special.__contains__(asmline[:1])):
        special_inst(asmline, reg)
    if(branch.__contains__(asmline[:1])) or (branch.__contains__(asmline[:3])):
        return branch_inst(asmline, reg, pc, index)
    
    output_data = ''
    for r in reg:
        output_data += str(r) + ' '
    output_file.write(output_data + '\n')
     

# here begins main

input_file = open("proj1_inst.txt", "r")
output_file = open("sim_output.txt","w")
line_count = 0
pc = []
reg = [0] * 35 #creating a list of registers, size 35
dm = [0] * 1024 #creating a list to simulate Data Memory, from DM[2000] to DM[3000] 0x2000 = 8192 = index[1]
pc_index = 0
inst_mem = []

alu = ["add", "sub", "mult", "xor", "mflo", "mfhi", "slt", "sll", "srl", "srlv", "addi", "andi", "ori", "lui", "mul"]
aluCount = 0
b = ["beq", "bne"]
bCount = 0
j = ["j"]
jCount = 0
mem = ["sw", "lw"]
memCount = 0
special = ["w"]
sCount = 0

for line in input_file:
    line_count += 1
    print(f'\n Line {line_count}: ', end = '')
    bin_str = hex_to_bin(line)
    asmline = process(bin_str)
    pc.append(asmline)
    inst_mem.append(asmline)
    reg[32] = len(pc) * 4
    output_file.write("PC: " + str((len(pc) - 1) * 4) + "| " + asmline + '\n')

inst_count = 0
counter = 0
output_file.write("\n\n\n\n\n\n\n\n\n\n")

while pc_index < (len(pc)):
    if(pc[pc_index][:1] == 'j'): #breakpoint
        pc_index = exec(inst_mem[pc_index], reg, dm, pc, pc_index)
        jCount += 1
    elif(pc[pc_index][:3] == 'beq' or pc[pc_index][:3] == 'bne'):
        pc_index = exec(inst_mem[pc_index], reg, dm, pc, pc_index)
        bCount += 1
    else:
        exec(inst_mem[pc_index], reg, dm, pc, pc_index)
        if alu.__contains__(pc[pc_index][:3]) or alu.__contains__(pc[pc_index][:4]):
            aluCount += 1
        elif mem.__contains__(pc[pc_index][:2]):
            memCount += 1
        elif special.__contains__(pc[pc_index][:1]):
            sCount += 1
        pc_index += 1

    inst_count += 1

print(f'________                _____')
print(f'\nRegister                Value')
print(f'________                _____')
ind = 0
while ind < len(reg):
    if ind < 10:
        print(f'{ind}                        {reg[ind]}')
    else:
        print(f'{ind}                       {reg[ind]}')
    ind += 1

print(f'\n\nFinal PC: {len(pc) * 4}')
print(f'Inst count: {inst_count}')
print(f'Inst stats: ALU: {aluCount} | Branch: {bCount} | Jump: {jCount} | Memory: {memCount} | Special: {sCount}')

print(f'\nDM:\n{dm}')

input_file.close()
output_file.close()
