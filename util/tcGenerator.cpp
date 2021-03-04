#include <iostream>
typedef long long LL;
using namespace std;

#define rep(i, a, b) for(int i = a; i < (b); ++i)
#define trav(a, x) for(auto& a : x)
#define all(x) begin(x), end(x)
#define sz(x) (int)(x).size()
#define popb pop_back
#define pb push_back
#define remove erase
#define fi first
#define se second
#define endl '\n'

#include <random>
#include <chrono>
mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count()); //For LL

LL getRange(LL a, LL b){
    LL ran = b-a+1;
    return (rng()%ran)+a;
}

void fill(vector<char> &V, char lo, char hi){
    V.clear();
    for(;lo <= hi;lo++) V.pb(lo);
}

const int N = 100;

int main(){
    ios_base::sync_with_stdio(0);
    cin.tie(0); cout.tie(0);
    vector <char> isi;
    fill(isi, '0', '1');
    // fill(isi, 'a', 'b');
    trav(cur, isi) cout << cur; cout << endl;
    for(int i = 1; i <= N;i++){
        int len = getRange(20, 50);
        for(int j = 0;j < len;j++) cout << isi[rng()%sz(isi)];
        cout << endl;
    }
}