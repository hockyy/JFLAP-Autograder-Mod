/*
Author : Hocky Yudhiono
3/4/2021 10:32:58 AM

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

// 36 six nodes

const int N = 6;
int ubah(int a, int b){
    a %= N; b %= N;
    return a * N + b + 1;
}

vector <int> edge[105];

int main(){
    rep(i,0,N) rep(j,0,N){
        int u = ubah(i, j);
        {
            int v = ubah(i + 1, j);
            edge[u].pb(v);
        }
        {
            int v = ubah(i,j + 1);
            edge[v].pb(u);
        }
    }
    cout << N * N << endl;
    for(int i = 1;i <= N * N;i++){
        trav(cur, edge[i]) cout << i << " " << cur << " " << 1 << endl;
    }
    for(int i = 1;i <= N * N;i++){
        cout << i << " " << i << " " << 0 << endl;
    }
}