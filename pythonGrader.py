verdict = ["reject", "accept"]

def solve(s):
    if(s.endswith("0101")): return 0
    if(s.endswith("100")): return 0
    return 1

def main():
    try:
        while 1:
            s = input()
            print(f'{s} {verdict[solve(s)]}')
    except EOFError:
        pass

if __name__ == '__main__':
    main()