def hash(s)->int:
    hash_val = 0
    for c in s:
        hash_val ^= ord(c)
    return hash_val

def fun():
    s = input()
    str_list = s.split()
    result = []
    temp = []
    used = set()
    for i in range(len(str_list)):
        if i in used:
            continue
        temp.clear()
        j = i+1
        used.add(i)
        temp.append(str_list[i])
        for j in range(len(str_list)):
            if hash(str_list[i]) == hash(str_list[j]):
                temp.append(str_list[j])
        result.append(temp)
    for row in result:
        print(row)

if __name__ == "__main__":
    fun()


