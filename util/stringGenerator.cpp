/*
Author : Hocky Yudhiono
2/25/2021 3:01:07 PM

1. You can sort the query if offline!
2. Don't bring the dp remaining state when dfsing on DP on Tree.
3. Try to reverse (Think from the back) if you stuck.
4. Be careful when submitting Div. 2 D-F, dont waste it on stupid WAs.
5. Try to reduce a problem, think of it when you're making subtasks
   like when problemsetting.
6. Matching problems can be solved with DP and vice versa.
   Counting and optimizing problems can be solved with DP.
   Try bitmasking when N is small. When big, consider greedy-ing.

*/

#include <algorithm>
#include <iostream>
#include <numeric>
#include <cstdlib>
#include <cassert>
#include <cstring>
#include <iomanip>
#include <cstdio>
#include <limits>
#include <string>
#include <vector>
#include <cmath>
#include <deque>
#include <queue>
#include <stack>
#include <map>
#include <set>
using namespace std;

typedef long long LL;
typedef long long ll;
typedef long double LD;
typedef vector<int> vi;
typedef pair<LL,LL> PLL;
typedef pair<LL,int> PLI;
typedef pair<int,int> PII;
typedef pair<int,int> pii;
typedef vector<vector<LL>> VVL;

#define rep(i, a, b) for(int i = a; i < (b); ++i)
#define trav(a, x) for(auto& a : x)
#define all(x) begin(x), end(x)
#define sz(x) (int)(x).size()
#define popf pop_front
#define pf push_front
#define popb pop_back
#define mp make_pair
#define pb push_back
#define remove erase
#define fi first
#define se second

// If the time limit is strict, try not to use long double

// Remember to undefine if the problem is interactive
#define endl '\n'
#define DEBUG(X) cout << ">>> DEBUG(" << __LINE__ << ") " << #X << " = " << (X) << endl

const double EPS = 1e-9;
const int INFMEM = 63;
const int INF = 1061109567;
const LL LINF = 4557430888798830399LL;
const double DINF = numeric_limits<double>::infinity();
const LL MOD = 1000000007;
const int dx[8] = {0,0,1,-1,1,-1,1,-1};
const int dy[8] = {1,-1,0,0,1,-1,-1,1};
// Do dir^1 to get reverse direction
const char dch[4] = {'R','L','D','U'};
// const string ds[8] = {"E","W","S","N","SE","NW","SW","NE"};
const double PI = 3.141592653589793;

inline void open(string a){
    freopen((a+".in").c_str(),"r",stdin);
    freopen((a+".out").c_str(),"w",stdout);
}

inline void fasterios(){
    // Do not use if interactive
    ios_base::sync_with_stdio(0);
    cin.tie(0); cout.tie(0);
    // cout << fixed << setprecision(10);
}


vi pi(const string& s) {
    vi p(sz(s));
    rep(i,1,sz(s)) {
        int g = p[i-1];
        while (g && s[i] != s[g]) g = p[g-1];
        p[i] = g + (s[i] == s[g]);
    }
    return p;
}

vi match(const string& s, const string& pat) {
    vi p = pi(pat + '\0' + s), res;
    rep(i,sz(p)-sz(s),sz(p))
        if (p[i] == sz(pat)) res.push_back(i - 2 * sz(pat));
    return res;
}

/*
aaa
aaaa
aaab
baaa
aaaaa
aaaab
aaaba
aaabb
abaaa
baaaa

aaa
aaab
baaa
aaaba
aaabb
abaaa
baaab
bbaaa
aaabaa
aaabab
*/

bool specialValid(const string& s, const string& pat) {
    vi res = match(s, pat), ret;
    rep(i,1,sz(res)) if(res[i-1] + sz(pat) > res[i]) return 0;
    return sz(res) & 1;
}


// Proper order
bool cmp(string a, string b){
    if(sz(a) != sz(b)) return sz(a) < sz(b);
    return a < b;
}

void uniquize(vector<string> &res){
    sort(all(res), cmp);
    res.erase(unique(all(res)),res.end());
}

vector <string> concat(const vector<string> &A, const vector<string> &B){
    vector <string> res;
    trav(a, A) trav(b, B) res.pb(a + b);
    uniquize(res);
    return res;
}

vector <string> concat2(const vector<string> &A, const vector<string> &B){
    vector <string> res;
    trav(a, A) trav(b, B) if(sz(a) == sz(b) && a != b) res.pb(a + b);
    uniquize(res);
    return res;
}

vector <string> power(const vector <string> &A, int expo, bool isStar = 1){
    vector <string> base = {""};
    vector <string> res = {};
    if(isStar) res.pb("");
    res.insert(res.end(), all(base));
    for(int i = 1;i <= expo;i++){
        base = concat(A, base);
        res.insert(res.end(), all(base));
    }
    uniquize(res);
    return res;
}

bool isValid(const string &S){
    return 1;
    // return sz(match(S, "aaa")) == 1;

    map <char, int> cnt;
    trav(cur, S) cnt[cur]++;
    return cnt['a'] / 3 % 2;
    // return cnt['a'] >= cnt['b'];
    // return cnt['a'] && cnt['b'] && 2 * cnt['a'] <= cnt['b'] && cnt['b'] <= 3 * cnt['a'];

    // int cari = S.find("ca");
    // if(cari != sz(S) && cari != -1) return 0;
    // cari = S.find("bb");
    // if(cari != sz(S) && cari != -1) return 0;
    // return 1;
}

vector <string> reverse(const vector <string> &L){
    vector <string> res;
    trav(cur, L){
        string tmp = cur; reverse(all(tmp));
        res.pb(tmp);
    }
    return res;
}

bool eachPrefix(const string &S){
    string curpref = "";
    trav(ch, S){
        curpref += ch;
        if(!isValid(curpref)) return 0;
    }
    return 1;
}

int main(){
    fasterios();
    vector <string> A = {"0","1"};

    vector <string> isi = power(A, 10);
    uniquize(isi);
    // Filter isi here
    int cntout = INF;
    trav(cur, isi){
        if(isValid(cur)){
            cout << cur << endl;
            if(--cntout <= 0) break;
        }
    }
}